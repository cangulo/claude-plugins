---
name: init
description: Create a new Architecture Decision Record (ADR) as a spec. Use when the user wants to start, draft, scaffold, or open a new ADR / architecture decision, or asks to record a decision under docs/adr. Scaffolds the ADR trio (summary + plan + follow-ups) with Status "Proposed" — it never writes implementation code.
---

# 🚀 adrs:init — scaffold a new ADR trio

Create the three files that make up one ADR under `docs/adr/`, from the shared
templates. This skill writes **only the ADR spec** — it must not modify
application code, run builds, or implement the decision. Implementation is the
separate `adrs:implement` step.

An ADR is a trio sharing the stem `YYYYMMDD-title`:
`YYYYMMDD-title-0-summary.md`, `YYYYMMDD-title-1-plan.md`,
`YYYYMMDD-title-2-followups.md`.

## 📋 Steps

1. **Confirm the topic.** Determine the decision the ADR captures. If it is
   unclear in one sentence, ask before proceeding. Read
   `${CLAUDE_PLUGIN_ROOT}/shared/adr-schema.md` for the naming and structure
   rules.

2. **Build the stem.** `YYYYMMDD` is today's date; `title` is a short
   `kebab-case` slug of the decision. The stem is `YYYYMMDD-title`, e.g.
   `20260808-use-postgres`. If this ADR is part of an iteration/group with other
   ADRs (or several are created the same day), use the grouped stem
   `YYYYMMDD-<group>-<NN>-<title>` (e.g. `20260808-auth-01-use-oauth`) and set
   the summary's `group` front-matter to `<group>`. Ensure `docs/adr/` exists;
   create it if not.

3. **Scaffold the three files** from the templates, filling each in from what
   you know and replacing every `YYYYMMDD-title` placeholder (including the
   cross-links) with the real stem:
   - `docs/adr/<stem>-0-summary.md` from `${CLAUDE_PLUGIN_ROOT}/shared/adr-summary-template.md`.
     Keep **Status `Proposed`** (both front-matter and the `## Status` section).
     Fill the front matter: `date`, `deciders`, and `tags`; set `group` if this
     is a grouped ADR, and `continuation_of` if it continues an earlier ADR.
     Draft Context, Requirements, Considered Options, the proposed Decision
     Outcome, and Consequences. Remove the template's HTML guidance comments.
   - `docs/adr/<stem>-1-plan.md` from `${CLAUDE_PLUGIN_ROOT}/shared/adr-plan-template.md`.
     Draft the Approach and Steps for the **essential implementation** of the
     decision.
   - `docs/adr/<stem>-2-followups.md` from `${CLAUDE_PLUGIN_ROOT}/shared/adr-followups-template.md`.
     This tracks follow-up items **outside** the essential implementation (the
     plan) — leave it mostly empty at init unless you already know of some. Keep
     the `Overview` table and the four groups (Bugs, Gaps, Improvements,
     Nice-to-have). For each known follow-up: add an `Overview` row
     (`Group | ID | Title | Source | Status`) **and** a matching
     `### <ID> — <Title>` detail entry under its group with `**Description:**`,
     `**Source:**`, `**Status:**`, and an optional `**Status reason:**`. The
     entry's Source/Status must match its Overview row. IDs are per-group and
     sequential — `B1`, `B2` (Bugs), `G1` (Gaps), `I1` (Improvements), `N1`
     (Nice-to-have). `Source` is `human`/`review`/`agent`; `Status` is
     `accepted`/`out-of-the-scope`. Leave a group empty (heading only) when it
     has no items.

   Use clearly-marked `TODO` placeholders for anything genuinely unknown rather
   than inventing facts. Keep each file within its line limit: summary ≤ 350,
   follow-ups ≤ 350, plan ≤ 600 — the plan captures the approach and where
   changes land, not a full preview of the code.

4. **Validate.** Run `adrs:validate` on the new ADR (or
   `python "${CLAUDE_PLUGIN_ROOT}/skills/validate/scripts/validate-adr.py" docs/adr/<stem>-0-summary.md`)
   and fix any reported problems so the whole trio is schema-valid.

5. **Report.** Tell the user the three file paths, that the Status is
   `Proposed`, and that they can review the trio and then run `adrs:implement`
   once they accept it.
