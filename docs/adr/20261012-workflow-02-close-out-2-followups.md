# 🗂️ Follow-ups — workflow plugin: /workflow:close-out

> ADR **20261012-workflow-02-close-out** · this is the **follow-ups** list.
> Related: [summary](20261012-workflow-02-close-out-0-summary.md) · [plan](20261012-workflow-02-close-out-1-plan.md).
>
> Action items **outside** the essential implementation. `adrs:implement` does
> not build these.

## 📊 Overview

| Group | ID | Title | Source | Status |
| ----- | -- | ----- | ------ | ------ |
| Gaps | G1 | Terminal CLI chats are treated as cloud | agent | accepted |

## 🐛 Bugs

## 🕳️ Gaps

### G1 — Terminal CLI chats are treated as cloud

**Description:** Shared step 1 detects a local chat by the desktop-app session
tools. A plain terminal `claude` session (e.g. `claude --plugin-dir …`) has no
such tools, so it is treated as cloud: no `SendMessage`, no archive, no
worktree removal, and Carlos gets "say sync" hints. Safe, but a terminal chat
could still remove its worktree. Consider a third context, "local CLI".

**Source:** agent

**Status:** accepted

## 📈 Improvements

## 🌟 Nice-to-have
