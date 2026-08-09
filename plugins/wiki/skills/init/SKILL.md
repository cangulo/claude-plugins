---
name: init
description: Initialize a repository wiki. Use when the user wants to create, scaffold, set up, or start a wiki for the repo. Creates a GitHub-wiki-standard wiki/ directory (Home + _Sidebar) and can add the workflow that publishes it to the repo's GitHub wiki.
---

# 🚀 wiki:init — scaffold a GitHub-wiki-standard wiki

Create a `wiki/` directory that follows
`${CLAUDE_PLUGIN_ROOT}/shared/wiki-conventions.md` so it renders natively as the
repository's GitHub wiki and can be published by a CI workflow.

## 📋 Steps

1. **Read the conventions.** Load `${CLAUDE_PLUGIN_ROOT}/shared/wiki-conventions.md`
   — it is the single source of truth for layout, page naming, special pages,
   and links.

2. **Check for an existing wiki.** If `wiki/` already exists, do not overwrite
   it — switch to `wiki:update` behavior for adding/editing pages, and only fill
   in any missing required pages (`Home.md`, `_Sidebar.md`).

3. **Create the required pages** at the top level of `wiki/` (flat — no
   subdirectories of pages):
   - `wiki/Home.md` — the landing page. Start with a single `# <Repo> Wiki`
     heading and a short intro. Draw the repo name/purpose from `README.md` if
     present.
   - `wiki/_Sidebar.md` — navigation. A simple bullet list linking to `Home`
     and every content page, using `[[Page Title]]` wiki links.

4. **Seed content pages (optional).** If the repo has obvious topics (from the
   README, `docs/`, or the user's request), scaffold a page per topic as
   `wiki/Topic-Name.md` (hyphenated filename, one `# Title` H1, brief stub).
   Add each to `_Sidebar.md`. Do not invent content — leave `TODO` stubs.

5. **Offer the publish workflow.** Ask whether to add the sync workflow. If yes,
   copy `${CLAUDE_PLUGIN_ROOT}/shared/publish-wiki.yml` to
   `.github/workflows/publish-wiki.yml`. Tell the user the one-time prerequisite:
   the GitHub wiki must be initialized once (create any page via the repo's Wiki
   tab) before the workflow can push to it.

6. **Validate.** Run `wiki:validate` (or
   `python "${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-wiki.py" wiki`)
   and fix any reported errors so the wiki is convention-valid.

7. **Report.** List the pages created, whether the workflow was added, and how
   to add more pages (`wiki:update`).
