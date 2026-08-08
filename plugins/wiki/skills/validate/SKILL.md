---
name: validate
description: Validate a repository wiki against the wiki conventions. Use when the user asks to validate, check, lint, or verify the wiki, or wants to confirm the wiki/ directory has Home and _Sidebar, valid page headings, no broken internal links, and GitHub-wiki-standard structure.
---

# wiki:validate — check the wiki against the conventions

Validate the whole `wiki/` directory against
`${CLAUDE_PLUGIN_ROOT}/shared/wiki-conventions.md`. A wiki is a linked set of
pages, so validation runs over the entire directory, not a single file.
Validation is deterministic via the bundled script so it can also gate CI.

## Steps

1. **Resolve the wiki directory.** Default to `wiki/`. If the user names another
   path, use it.

2. **Run the validator:**

   ```
   python "${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-wiki.py" wiki
   ```

   Use `python3` if `python` is not on PATH. The script prints `WARNING:` and
   `ERROR:` lines, then a final `VALID:`/`INVALID:` summary. It exits `0` when
   there are no errors (warnings are allowed) and non-zero when any error is
   found.

   - **ERROR** (fails): missing `wiki/`, missing `Home.md` or `_Sidebar.md`, a
     page in a subdirectory, a content page with no `# H1`, or a broken internal
     link.
   - **WARNING** (does not fail): a page missing from `_Sidebar.md`, or a page
     with more than one `# H1`.

3. **Report the result.**
   - If valid: tell the user the wiki passes, and surface any warnings.
   - If invalid: list each error and point to the convention it violates. Offer
     to fix them via `wiki:update`.

The script is the source of truth for pass/fail. For the reasoning behind a
rule, consult `${CLAUDE_PLUGIN_ROOT}/shared/wiki-conventions.md`.
