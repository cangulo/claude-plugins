---
name: implement
description: Implement an accepted Architecture Decision Record (ADR) by editing the repository to satisfy it. Use when the user asks to implement, apply, execute, or carry out an ADR / architecture decision. This is the agentic step that changes code — it reads the ADR trio (summary, plan, backlog) as the contract.
---

# 🔨 adrs:implement — build the repo changes an ADR specifies

Take an accepted ADR and make the repository changes it calls for, treating the
trio as the contract: the **summary** is the decision, the **plan** is the
approach, and the **backlog** is the list of work items. This is the one ADR
skill that edits application code.

## 📋 Steps

1. **Resolve the ADR.** Use the path/stem the user provided. If none, list
   `docs/adr/` and ask which ADR to implement.

2. **Validate first.** Run `adrs:validate` on the ADR (or the script at
   `${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-adr.py`). If the trio
   is not schema-valid, stop and ask the user to fix it (via `adrs:update`)
   before implementing.

3. **Check the Status** in `<stem>-summary.md`.
   - `Accepted`: proceed.
   - `Proposed`: not yet agreed. Do **not** implement silently — confirm the ADR
     is approved and offer to move it to `Accepted` via `adrs:update` first.
   - `Rejected`, `Deprecated`, or `Superseded`: stop and tell the user this ADR
     should not be implemented (point to the superseding ADR if any).

4. **Read the trio as the contract.**
   - From the **summary**: the Decision Outcome and the Requirements
     (constraints to honor).
   - From the **plan**: the Approach and Steps to follow.
   - From the **backlog**: the concrete work items. Use the `Overview` table to
     see every item, then read each item's detail entry. Implement items whose
     `Status` is `accepted`; **skip** items marked `out-of-the-scope`.

5. **Implement.** Make the changes across the repository — code, config, docs,
   and tests — following the plan's Steps and the existing codebase
   conventions. Keep changes scoped to the ADR. If you find the ADR is ambiguous
   or conflicts with reality, pause and raise it rather than guessing (an
   `adrs:update` may be needed).

   > For heavy, multi-file implementations you may delegate the edits to a
   > subagent — promote this step to a dedicated `agents/implementer.md`
   > (optionally `isolation: "worktree"`) only if implement runs routinely grow
   > large.

6. **Verify.** Run the repo's build/tests/linters where available and confirm
   the change satisfies the summary's Requirements and the plan's
   verification step.

7. **Update the backlog.** If implementation surfaces new `bugs`, `gaps`,
   `improvements`, or `nice-to-have` items, add them (Overview row + matching
   `### <ID> …` detail) with `Source: agent` and an appropriate `Status` — via
   `adrs:update`.

8. **Report.** Summarize the changes made, how they satisfy the ADR, and any
   backlog items left as `out-of-the-scope` or newly added. If the summary's
   Status should change, suggest running `adrs:update`.
