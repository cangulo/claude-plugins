---
name: validate
description: Validate an Architecture Decision Record (ADR) against the ADR schema. Use when the user asks to validate, check, lint, or verify an ADR under docs/adr, or wants to confirm an ADR's summary, plan, and backlog files have the required structure, a valid Status, and well-formed backlog items.
---

# 🔍 adrs:validate — check an ADR trio against the schema

Validate one ADR — its `summary`, `plan`, and `backlog` files — against
`${CLAUDE_PLUGIN_ROOT}/shared/adr-schema.md`. Validation is deterministic via
the bundled script so it can also gate CI. The three files are one unit, so this
always validates the whole trio.

## 📋 Steps

1. **Resolve the target ADR.** Use the path the user provided — it may be any
   one of the trio files (e.g. `docs/adr/20260808-use-postgres-plan.md`) or the
   bare stem (`docs/adr/20260808-use-postgres`). The script derives the stem and
   checks all three files. If no ADR is given, ask which one to validate.

2. **Run the validator:**

   ```
   python "${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-adr.py" <path>
   ```

   Use `python3` if `python` is not on PATH. The script exits `0` and prints
   `VALID: <stem>` when the whole trio conforms; it exits non-zero and prints
   `INVALID: <stem>` followed by one `- ERROR: …` line per problem (missing trio
   file, bad name/date, missing or empty section, invalid summary Status, or a
   backlog problem: an Overview row with a bad Group/ID/Source/Status, an item ID
   whose prefix doesn't match its group, an Overview row and detail entry that
   don't correspond, a detail entry missing its Description/Source/Status or
   disagreeing with the Overview), a metadata problem (a `continuation_of` or
   `Superseded by` link that doesn't resolve, or a non-array `tags`), or a file
   over its line limit (summary/backlog ≤ 350, plan ≤ 600).

3. **Report the result.**
   - If valid: tell the user the ADR passes.
   - If invalid: list each reported problem and point to the schema rule it
     violates. Offer to fix it via `adrs:update` — but do not change files
     unless asked.

The script is the source of truth for pass/fail. For questions about *why* a
rule exists, consult `${CLAUDE_PLUGIN_ROOT}/shared/adr-schema.md`.
