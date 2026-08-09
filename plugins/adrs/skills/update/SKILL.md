---
name: update
description: Update an existing Architecture Decision Record (ADR) — change its Status, supersede it, revise the plan, or triage follow-up items. Use when the user asks to accept, reject, deprecate, supersede, amend, or edit an existing ADR under docs/adr, or to add/triage items in its follow-ups, while keeping the trio schema-valid.
---

# ✏️ adrs:update — revise an existing ADR

Amend an existing ADR's trio (`summary`, `plan`, `follow-ups`), touching
whichever file(s) a change affects and always leaving the trio valid against
`${CLAUDE_PLUGIN_ROOT}/shared/adr-schema.md`.

## 📋 Steps

1. **Resolve the ADR.** Use the path/stem the user provided. If none, list
   `docs/adr/` and ask which ADR to update.

2. **Identify the change** and edit the right file:

   - **Status transition** (in `<stem>-summary.md`) — e.g. `Proposed → Accepted`,
     `Accepted → Deprecated`. Update the `## Status` section and the front-matter
     `status` to an allowed value.
   - **Supersede** (in `<stem>-summary.md`) — set Status to
     `Superseded by [YYYYMMDD-title](YYYYMMDD-title-summary.md)` pointing at the
     replacement. If the replacement ADR does not exist yet, offer to create it
     with `adrs:init` first, then cross-reference both.
   - **Revise the decision** (`summary`) or **the approach/steps** (`plan`) —
     amend the relevant sections. Preserve decision history; do not silently
     rewrite an accepted decision — note material changes.
   - **Metadata** (in `<stem>-summary.md` front matter) — update `tags`,
     `continuation_of`, or `group` as needed.
   - **Follow-up triage** (in `<stem>-followups.md`) — record work *outside* the
     essential implementation. To **add** an item: pick the right group (`Bugs`,
     `Gaps`, `Improvements`, `Nice-to-have`), assign the next sequential ID for
     that group's prefix (`B`/`G`/`I`/`N`), add an `Overview` row
     (`Group | ID | Title | Source | Status`) **and** a matching
     `### <ID> — <Title>` detail entry with `**Description:**`, `**Source:**`,
     `**Status:**`, and an optional `**Status reason:**`. To **re-triage** an
     item, change its `Status` (`accepted` / `out-of-the-scope`) in **both** the
     Overview row and the detail entry — they must agree. Keep the Overview and
     detail in sync — every ID must appear in both.

3. **Keep the trio schema-valid.** Do not drop any required section or leave one
   empty. Use only allowed ADR Status values, and follow-up `Source`
   (`human`/`review`/`agent`) and item `Status` (`accepted`/`out-of-the-scope`)
   values.

4. **Validate.** Run `adrs:validate` on the ADR (or the script at
   `${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-adr.py`) and fix any
   reported problems.

5. **Report.** Summarize what changed (old → new Status, superseding link,
   revised sections, or follow-up edits). If the ADR was just moved to
   `Accepted`, mention that `adrs:implement` can now build the plan.
