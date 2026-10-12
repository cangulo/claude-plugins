# 🗂️ Follow-ups — workflow plugin: shared wrap-up and /workflow:recap

> ADR **20261012-workflow-01-shared-wrap-up** · this is the **follow-ups** list.
> Related: [summary](20261012-workflow-01-shared-wrap-up-0-summary.md) · [plan](20261012-workflow-01-shared-wrap-up-1-plan.md).
>
> Action items **outside** the essential implementation. `adrs:implement` does
> not build these.

## 📊 Overview

| Group | ID | Title | Source | Status |
| ----- | -- | ----- | ------ | ------ |
| Gaps | G1 | No CI in the repo | agent | accepted |

## 🐛 Bugs

## 🕳️ Gaps

### G1 — No CI in the repo

**Description:** The repo has no GitHub Actions workflows, so PRs have no
checks. A workflow could run `claude plugin validate` on each plugin and
`validate-adr.py` on `docs/adr/*-0-summary.md`.

**Source:** agent

**Status:** accepted

**Status reason:** accepted as a gap: PRs currently rely on manual validation.

## 📈 Improvements

## 🌟 Nice-to-have
