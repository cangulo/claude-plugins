# 🗂️ Follow-ups — workflow plugin: auto-invocation, CLAUDE.md link format, detached worktrees

> ADR **20261012-workflow-04-auto-invoke-links** · this is the **follow-ups** list.
> Related: [summary](20261012-workflow-04-auto-invoke-links-0-summary.md) · [plan](20261012-workflow-04-auto-invoke-links-1-plan.md).
>
> Action items **outside** the essential implementation. `adrs:implement` does
> not build these.

## 📊 Overview

| Group | ID | Title | Source | Status |
| ----- | -- | ----- | ------ | ------ |
| Improvements | I1 | CLAUDE.md: close-out first line `ISSUE#<N> closed:` | human | accepted |
| Improvements | I2 | CLAUDE.md: mention auto-invocation in the Implementator rules | agent | accepted |
| Nice-to-have | N1 | Stale-skill check | human | out-of-the-scope |

## 🐛 Bugs

## 🕳️ Gaps

## 📈 Improvements

### I1 — CLAUDE.md: close-out first line `ISSUE#<N> closed:`

**Description:** The Implementator rules in `~/.claude/CLAUDE.md` spell the
closing comment's first line as `#<NUMBER> closed: <title>`; 0.4.0 posts
`ISSUE#<NUMBER> closed: <title>`. Update the line in the 📜Personal CLAUDE.md
chat.
**Source:** human
**Status:** accepted

### I2 — CLAUDE.md: mention auto-invocation in the Implementator rules

**Description:** The rules say "run `/workflow:recap`" and "run
`/workflow:close-out`"; they could say Claude runs them on its own after a PR
(CI green) and after the issue closes. Out of scope for #21; goes through the
📜Personal CLAUDE.md chat.
**Source:** agent
**Status:** accepted

## 🌟 Nice-to-have

### N1 — Stale-skill check

**Description:** Print the loaded plugin version and warn when a newer one is
installed; close-out would refuse to finalize on a stale version.
**Source:** human
**Status:** out-of-the-scope
**Status reason:** Dropped by Carlos in the #21 chat: single consumer,
plugins are reinstalled and chats reloaded by hand.
