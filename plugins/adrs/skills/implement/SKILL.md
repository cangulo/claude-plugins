---
name: implement
description: Implement an accepted Architecture Decision Record (ADR) by editing the repository to satisfy it. Use when the user asks to implement, apply, execute, or carry out an ADR / architecture decision. This is the agentic step that changes code — it builds the plan (the essential implementation).
---

# 🔨 adrs:implement — build the repo changes an ADR specifies

Take an accepted ADR and make the repository changes it calls for. The
**plan** is the deliverable — the essential implementation — guided by the
**summary** (the decision). The **follow-ups** file is *not* built here; it is a
tracker for work outside the essential implementation. This is the one ADR skill
that edits application code.

## 📋 Steps

1. **Resolve the ADR.** Use the path/stem the user provided. If none, list
   `docs/adr/` and ask which ADR to implement.

2. **Validate first.** Run `adrs:validate` on the ADR (or the script at
   `${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-adr.py`). If the trio
   is not schema-valid, stop and ask the user to fix it (via `adrs:update`)
   before implementing.

3. **Check the Status** in `<stem>-0-summary.md`.
   - `Accepted`: proceed.
   - `Proposed`: not yet agreed. Do **not** implement silently — confirm the ADR
     is approved and offer to move it to `Accepted` via `adrs:update` first.
   - `Rejected`, `Deprecated`, or `Superseded`: stop and tell the user this ADR
     should not be implemented (point to the superseding ADR if any).

4. **Read the ADR as the contract.**
   - From the **summary**: the Decision Outcome and the Requirements
     (constraints to honor).
   - From the **plan**: the Approach and Steps to follow — this is what you
     build.
   - The **follow-ups** file is context only. **Do not implement its items** —
     they are tracked for later, outside the essential implementation. Read them
     so you don't re-file the same follow-ups, and so you know what is
     deliberately deferred (`out-of-the-scope`).

5. **Implement the plan.** Make the changes across the repository — code,
   config, docs, and tests — following the plan's Steps and the existing
   codebase conventions. Keep changes scoped to the plan. If you find the ADR is
   ambiguous or conflicts with reality, pause and raise it rather than guessing
   (an `adrs:update` may be needed).

   > For heavy, multi-file implementations you may delegate the edits to a
   > subagent — promote this step to a dedicated `agents/implementer.md`
   > (optionally `isolation: "worktree"`) only if implement runs routinely grow
   > large.

6. **Verify.** Run the repo's build/tests/linters where available and confirm
   the change satisfies the summary's Requirements and the plan's
   verification step.

7. **Record follow-ups.** If implementation surfaces new work *outside* the
   essential implementation — `bugs`, `gaps`, `improvements`, or `nice-to-have`
   — add it to the follow-ups file (Overview row + matching `### <ID> …` detail)
   with `Source: agent` and an appropriate `Status`, via `adrs:update`. Do not
   build these now.

8. **Report.** Summarize the changes made and how they satisfy the ADR, plus any
   follow-ups you recorded. If the summary's Status should change, suggest
   running `adrs:update`.
