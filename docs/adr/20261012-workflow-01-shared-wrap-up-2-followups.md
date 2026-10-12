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
| Improvements | I1 | Cleanup after squash merges | agent | accepted |

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

### I1 — Cleanup after squash merges

**Description:** This repo squash-merges PRs, so a merged PR's head commit is
not reachable from `main` and `git branch -d` refuses to delete the branch. The
wrap-up then only flags it with a manual command. A safe alternative: delete
with `-D` only when the PR is merged on GitHub **and** the local tip equals the
PR's `headRefOid` (nothing unpushed is lost). This changes the agreed
"merged-only `git branch -d`" rule, so Carlos must decide. It also affects the
final worktree removal in `/workflow:close-out` (#9).

**Source:** agent

**Status:** accepted

**Status reason:** accepted as an improvement: without it, cleanup mostly ends in manual commands.

## 🌟 Nice-to-have
