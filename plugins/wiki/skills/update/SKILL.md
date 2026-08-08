---
name: update
description: Add or edit a wiki page. Use when the user wants to add, write, update, edit, rename, or remove a page in the repository wiki, or refresh wiki content. Keeps the sidebar navigation and internal links in sync with the wiki conventions.
---

# wiki:update — add or edit a wiki page

Create or modify pages in the `wiki/` directory while keeping the wiki valid
against `${CLAUDE_PLUGIN_ROOT}/shared/wiki-conventions.md`.

## Steps

1. **Read the conventions.** Load `${CLAUDE_PLUGIN_ROOT}/shared/wiki-conventions.md`
   for naming, links, and sidebar rules. If `wiki/` does not exist yet, run
   `wiki:init` first.

2. **Make the change:**
   - **Add a page** — create `wiki/Page-Title.md` (hyphenated filename, flat in
     `wiki/`, no subdirectory). Start with one `# Page Title` H1. Link related
     pages with `[[Other Page]]` wiki links.
   - **Edit a page** — update its content, preserving the single H1 and valid
     internal links.
   - **Rename a page** — rename the file to the new `Hyphenated-Title.md` and
     update every `[[...]]` / relative link that pointed at the old name.
   - **Remove a page** — delete the file and remove its entry from
     `_Sidebar.md` and any links to it.

3. **Keep the sidebar in sync.** Ensure `wiki/_Sidebar.md` links to every
   content page (all `wiki/*.md` except `Home.md`, `_Sidebar.md`, `_Footer.md`).
   Add new pages; remove deleted ones.

4. **Keep links valid.** Every internal link must resolve to a page that exists
   under `wiki/`. Use `[[Page Title]]` (preferred) or a relative `[text](Page-Title)`
   link with no `.md` extension.

5. **Validate.** Run `wiki:validate` (or
   `python "${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-wiki.py" wiki`)
   and fix any reported errors.

6. **Report.** Summarize the pages added/edited/removed and any sidebar changes.
