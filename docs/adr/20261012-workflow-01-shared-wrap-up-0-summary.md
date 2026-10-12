---
status: "Accepted"
date: 2026-10-12
deciders: [Carlos]
consulted: []
informed: [plugins Governor chat]
tags: [plugins, workflow, skills]
continuation_of: []
group: "workflow"
---

# 📝 workflow plugin: shared wrap-up procedure and /workflow:recap

> ADR **20261012-workflow-01-shared-wrap-up** · this is the **summary** (the decision).
> Related: [plan](20261012-workflow-01-shared-wrap-up-1-plan.md) · [follow-ups](20261012-workflow-01-shared-wrap-up-2-followups.md).
> Issue: [claude-plugins#8](https://github.com/cangulo/claude-plugins/issues/8) · Epic: [claude-plugins#7](https://github.com/cangulo/claude-plugins/issues/7).

## 🚦 Status

Accepted

## 🧭 Context and Problem Statement

Carlos runs Governor/Implementator chats on GitHub issues. Each chat needs a
wrap-up that summarizes its work without rewriting the issue body, and that
works in local and cloud chats. The `workflow` plugin provides two skills,
`/workflow:recap` (#8) and `/workflow:close-out` (#9). Both run the same
wrap-up, so the question is how to share it, how recap knows there is new progress to report, and how
the skills behave in local and cloud chats.

## 📋 Requirements

* R1 — One shared wrap-up procedure used by both skills, so they don't drift.
* R2 — Never rewrite the issue body; summaries go in issue comments.
* R3 — Recap never commits, pushes, closes the issue or archives the chat.
* R4 — Cleanup only deletes this issue's merged local branches/worktrees, never
  the chat's own worktree/branch. `git worktree remove` never uses `--force`.
  `git branch -D` only when the PR is merged and the local tip equals its
  `headRefOid` (squash merges; follow-up I1).
* R5 — Notify the Governor only on new progress; always via an issue comment,
  plus `SendMessage` in local chats, or a "say sync" instruction in cloud chats.
* R6 — Works in local (desktop app) and cloud (claude.ai/code) chats; GitHub
  permission failures are reported and don't stop the run.
* R7 — Output uses emoji section headings, per-section codes (`[wd#]`, `[cl#]`,
  `[oq#]`, `[pa#]`) and `repo#N` links.

## ⚖️ Considered Options

* Shared procedure: (A) one `shared/wrap-up.md` referenced via
  `${CLAUDE_PLUGIN_ROOT}` · (B) duplicate the steps in each `SKILL.md` ·
  (C) close-out invokes the recap skill.
* New-progress detection: (D) hidden marker in the update comment carrying a
  state line · (E) conversation memory only.
* Invocation: (F) explicit only (`disable-model-invocation: true`) ·
  (G) auto-invocable.
* Local vs cloud: (H) detect by tool availability (session/messaging tools) ·
  (I) ask Carlos every run.

## ✅ Decision Outcome

Chosen: **A + D + F + H**.

* **A** — `plugins/workflow/shared/wrap-up.md` holds the wrap-up steps
  (identify issue, work done, PRs, cleanup, open questions, pending), the
  output rules, the local/cloud detection, the Governor lookup and the
  "deliver an update" channels. Skills read it and add only their own steps.
  Same pattern as `adrs/shared/`.
* **D** — every update comment ends with a hidden marker
  `<!-- workflow:recap head=<sha> prs=<N>:<state>,… -->`. Recap compares the
  current state and work done against the latest marked comment on the issue.
  It survives new chats and context compaction and works in cloud chats.
* **F** — recap deletes branches and posts comments, so it only runs when
  Carlos types `/workflow:recap`.
* **Cleanup after squash merges** (follow-up I1, approved by Carlos) —
  `git branch -d` first; `-D` only when the PR is `MERGED` on GitHub and the
  local tip equals the PR's `headRefOid`; otherwise flag.
* **H** — local when the session tools (`list_sessions` / `SendMessage`) are
  available; otherwise cloud.

### Pros and Cons of the Options

#### A — shared file

* Good, because one edit updates both skills (R1) and matches `adrs/shared/`.
* Bad, because the skill must read a second file each run.

#### B — duplicate in each skill

* Good, because each skill is self-contained.
* Bad, because the two copies drift (violates R1).

#### C — close-out invokes recap

* Good, because no extra file.
* Bad, because recap's notify step would fire inside close-out, and skill
  chaining is less predictable than reading a file.

#### D — marker comment

* Good, because state lives on GitHub, visible to every chat (R5, R6).
* Bad, because the marker format becomes a small contract to keep stable.

#### E — conversation memory

* Good, because nothing to store.
* Bad, because a new chat or compaction re-sends the same update.

## 📌 Consequences

* Good, because close-out (#9) only adds its decide/finalize steps on top of
  `shared/wrap-up.md`.
* Good, because the Governor and any later chat can see the last reported
  state on the issue.
* Bad, because skills are markdown instructions, so behaviour is verified by a
  manual run, not automated tests.
