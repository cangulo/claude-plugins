# 📐 ADR schema

The canonical contract every ADR in this repo must satisfy. Both `adrs:validate`
(via `scripts/validate-adr.py`) and the other skills treat this file as the
single source of truth. The three `adr-*-template.md` files are conforming
instances of this schema.

## 🗃️ An ADR is a trio of files

One ADR is composed of **three files** that share the same stem
`YYYYMMDD-title` and live together under `docs/adr/`:

| File                          | Role |
| ----------------------------- | ---- |
| `YYYYMMDD-title-summary.md`   | The **decision** — context, options, outcome, and the ADR **Status**. |
| `YYYYMMDD-title-plan.md`      | The **plan** — the essential implementation to satisfy the decision. |
| `YYYYMMDD-title-followups.md` | The **follow-ups** — action items *outside* the essential implementation. |

The skills always act on the trio as a unit: `init` scaffolds all three,
`validate` checks all three, `implement` reads all three, and `update` edits
whichever file(s) a change touches.

## 🏷️ Naming

The stem is `YYYYMMDD-title`, or the optional **grouped** form
`YYYYMMDD-group-NN-title` when several ADRs belong to the same iteration or day.

* `YYYYMMDD` — the creation date (e.g. `20260808`). Must be a real calendar date.
* `group` — *(grouped form only)* a short `kebab-case` iteration slug, matching
  the `group` front-matter property.
* `NN` — *(grouped form only)* a zero-padded index ordering ADRs within the
  group (`01`, `02`, …).
* `title` — a short `kebab-case` slug (lowercase letters, digits, hyphens).
* Suffix — exactly one of `-summary`, `-plan`, `-followups`, then `.md`.
* Simple example trio: `docs/adr/20260808-use-postgres-summary.md`,
  `…-use-postgres-plan.md`, `…-use-postgres-followups.md`.
* Grouped example: `docs/adr/20260808-auth-01-use-oauth-summary.md`
  (group `auth`, index `01`, title `use-oauth`).

## 🧾 Summary front matter

The summary file starts with a YAML front-matter block. Alongside
`status`, `date`, `deciders`, `consulted`, and `informed`, it may carry:

* `tags` — an array of topic strings, e.g. `[database, infra]`.
* `continuation_of` — optional array of ADR **stem(s)** (or links) this one
  continues, e.g. `[20260801-caching]`.
* `group` — optional iteration slug shared by related ADRs; when set it matches
  the `group` segment of the grouped filename.

The validator checks metadata **when it can**: `tags` must be a YAML array, and
every `continuation_of` reference (and any `Superseded by [...]` link in the
Status) must resolve to a summary file that exists under `docs/adr/`. Other
front-matter fields are free-form.

## 🚦 Status (in the summary)

The summary's `## Status` section MUST begin with exactly one of these values
(case-insensitive) on its first non-empty line:

* `Proposed`  — decision drafted, not yet agreed. `adrs:init` always starts here.
* `Accepted`  — agreed; may now be implemented.
* `Rejected`  — considered and declined; kept for the record.
* `Deprecated`— once accepted, no longer applicable.
* `Superseded`— replaced by a later ADR. SHOULD be written as
  `Superseded by [YYYYMMDD-title](YYYYMMDD-title-summary.md)`.

## 📏 File length limits

Each file has a maximum physical line count, keeping every doc focused and
reviewable:

* **summary** — at most **350** lines.
* **follow-ups** — at most **350** lines.
* **plan** — at most **600** lines. The plan gets more room because it captures
  the *process, steps, technical approach, and where changes land* — not a full
  preview of the code to be written. If a plan is pushing the limit, it is
  probably pasting code that belongs in the implementation, not the spec.

## 🏗️ Required structure per file

Each file MUST have a level-1 `# ...` title as its first heading, plus these
level-2 (`##`) sections, each present and non-empty:

* **summary** — `Status`, `Context and Problem Statement`, `Requirements`,
  `Considered Options`, `Decision Outcome`, `Consequences`.
* **plan** — `Approach`, `Steps`.
* **follow-ups** — `Overview`, `Bugs`, `Gaps`, `Improvements`, `Nice-to-have`.

Additional sections (e.g. `### Pros and Cons of the Options`, `Risks and
Mitigations`, front-matter) are allowed and ignored by validation.

## 🗂️ Follow-up item format

The follow-ups file has an **Overview** table followed by one section per group. Every
item appears once in the Overview and once as a detail subsection.

**Overview** — a five-column table listing every action item:

```
| Group | ID | Title | Source | Status |
| ----- | -- | ----- | ------ | ------ |
| Bugs  | B1 | Connection pool leaks | review | accepted |
| Gaps  | G1 | No migration tooling  | agent  | out-of-the-scope |
```

**Group sections** — `Bugs`, `Gaps`, `Improvements`, `Nice-to-have`. Each item
is a level-3 subsection whose heading starts with the item ID and which carries
labelled fields:

```
### B1 — Connection pool leaks

**Description:** Under sustained load the pool is never drained… (repro, links,
code refs — as many lines as needed).

**Source:** review

**Status:** accepted

**Status reason:** accepted as a bug because it exhausts connections in prod.
```

Entry fields:

* **Description** — required, free-form (may be multiline).
* **Source** — required: `human`, `review`, or `agent`.
* **Status** — required: `accepted` or `out-of-the-scope`.
* **Status reason** — optional prose, e.g. "out-of-the-scope because …" or
  "accepted as a gap because …".

An entry's `Source` and `Status` must **match its Overview row**.

Field vocabulary:

* **ID** — per-group prefix + number: **B**ugs → `B1`, `B2`; **G**aps → `G1`;
  **I**mprovements → `I1`; **N**ice-to-have → `N1`. Unique across the follow-ups file.
* **Source** — where the item came from: `human`, `review`, or `agent`.
* **Status** — its triage state: `accepted` or `out-of-the-scope`.

A group with no items keeps just its heading (no rows, no subsections). Every
Overview ID must have a matching `### <ID> …` detail entry in the group its
prefix names, and vice versa.

## ✔️ Validation rules (enforced by `validate-adr.py`)

Given any one path of a trio (any of the three files, or the shared
`YYYYMMDD-title` stem), the validator resolves the whole trio and reports an
ERROR when any of the following fail:

1. All three files (`-summary`, `-plan`, `-followups`) exist for the stem.
2. Each filename matches `YYYYMMDD-<kebab-stem>-{summary,plan,followups}.md` with a
   real `YYYYMMDD` date (covers both the simple and grouped forms).
3. Each file has a level-1 `# ...` title as its first heading.
4. Every required `##` section for that file is present and non-empty.
5. The summary's `## Status` first content line starts with an allowed value.
6. In the follow-ups file: every Overview row has a valid `Group`, an `ID` whose prefix
   matches that group, an allowed `Source`, and an allowed `Status`; every
   Overview ID has a matching `### <ID> …` detail entry in the right group (and
   vice versa); and IDs are unique.
7. Each follow-up detail entry has a non-empty `Description`, an allowed `Source`,
   and an allowed `Status`, and its `Source`/`Status` match its Overview row.
8. Metadata (when present): `tags` is a YAML array, and every `continuation_of`
   reference and `Superseded by [...]` link resolves to an existing summary file.
9. No file exceeds its line limit: 350 (summary), 350 (followups), 600 (plan).

The script exits `0` when the whole trio is valid and non-zero when any error is
found, printing each problem on its own line so it can gate CI.
