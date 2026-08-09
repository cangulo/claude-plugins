# 📖 Wiki conventions

The canonical rules every wiki page in this repo must follow. All three `wiki`
skills (`init`, `update`, `validate`) treat this file as the single source of
truth, and `scripts/validate-wiki.py` enforces the deterministic subset.

These conventions target the **GitHub wiki**: the `wiki/` folder is authored in
the main repository and a CI workflow publishes it to the repo's wiki git repo
(`https://github.com/<owner>/<repo>.wiki.git`). Everything below keeps the files
renderable natively by GitHub's wiki so the publish step is a straight copy.

## 📁 Location and layout

* Wiki pages live in a top-level **`wiki/`** directory in the repository.
* The directory is **flat** — a GitHub wiki git repo has no folders, so every
  page is a `.md` file directly under `wiki/`. Do not create subdirectories of
  pages. (Binary assets like images may sit alongside the pages.)

## 📄 Page files

* One markdown file per page: **`Title-In-Hyphen-Case.md`**. GitHub derives the
  page title and URL from the filename, replacing hyphens with spaces
  (`Getting-Started.md` → page "Getting Started" at `/wiki/Getting-Started`).
* Use hyphens, not spaces, in filenames. Avoid characters GitHub reserves in
  wiki paths: `\ / : * ? " < > | # %`.
* Every page begins with exactly one level-1 heading (`# Title`) as its first
  heading — the human-readable page title.

## ⭐ Special pages

| File          | Role | Required |
| ------------- | ---- | -------- |
| `Home.md`     | Landing page GitHub shows at `/wiki`. | **Yes** |
| `_Sidebar.md` | Navigation rendered on every page. Must link to every content page. | **Yes** |
| `_Footer.md`  | Footer rendered on every page. | Optional |

Files whose name starts with `_` are treated as GitHub wiki chrome, not content
pages, and are excluded from sidebar-coverage checks.

## 🔗 Links between pages

* Prefer GitHub **wiki links**: `[[Page Title]]`, or `[[Link text|Page-Title]]`
  to use custom text. GitHub resolves the target by matching the page title
  (spaces and hyphens are interchangeable).
* Plain relative markdown links also work: `[text](Page-Title)` (no `.md`
  extension, no leading `./`). An optional `#anchor` may follow.
* Every internal link must resolve to a page file that exists under `wiki/`.
* External links use full `https://…` URLs.

## 📑 Sidebar

* `_Sidebar.md` must contain a link to every content page (every `wiki/*.md`
  that is not `Home.md`, `_Sidebar.md`, or `_Footer.md`). Home may be linked too
  but is not required.
* Keep the sidebar a simple nested bullet list so it renders cleanly in GitHub's
  narrow sidebar column.

## ✔️ Validation severity

`scripts/validate-wiki.py` distinguishes:

* **ERROR** (fails the check, non-zero exit): missing `wiki/` dir, missing
  `Home.md` or `_Sidebar.md`, a page in a subdirectory, a page with no level-1
  heading, or a broken internal link.
* **WARNING** (printed, does not fail): a content page missing from `_Sidebar.md`,
  or a page with more than one level-1 heading.
