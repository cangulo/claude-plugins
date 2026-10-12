---
status: "Accepted"
date: 2026-10-12
deciders: [Carlos]
consulted: []
informed: [plugins Governor chat]
tags: [plugins, workflow, skills]
continuation_of: [20261012-workflow-01-shared-wrap-up]
group: "workflow"
---

# 📝 workflow plugin: /workflow:close-out

> ADR **20261012-workflow-02-close-out** · this is the **summary** (the decision).
> Related: [plan](20261012-workflow-02-close-out-1-plan.md) · [follow-ups](20261012-workflow-02-close-out-2-followups.md).
> Continues: [20261012-workflow-01-shared-wrap-up](20261012-workflow-01-shared-wrap-up-0-summary.md).
> Issue: [claude-plugins#9](https://github.com/cangulo/claude-plugins/issues/9) · Epic: [claude-plugins#7](https://github.com/cangulo/claude-plugins/issues/7).

## 🚦 Status

Accepted

## 🧭 Context and Problem Statement

ADR 01 added `shared/wrap-up.md` and `/workflow:recap`. An Implementator chat
also needs to end cleanly: once its issue is done, post the closing comment,
make sure the issue and its Project item are closed, tell the Governor, archive
the chat and remove its worktree. #9 adds this on top of the shared wrap-up.
The questions are how close-out reuses the wrap-up, how it decides "nothing
pending", and how it removes the worktree the chat itself runs in.

## 📋 Requirements

* R1 — Reuse `shared/wrap-up.md`; no duplicated procedure.
* R2 — Anything pending → stop after the wrap-up; no comment, close, Project
  change, notify or archive.
* R3 — Nothing pending → finalize without confirmation, in order: comment →
  issue closed → Project Done → notify → archive → worktree removal.
* R4 — The closing comment's first line is exactly `#<NUMBER> closed: <title>`.
* R5 — Never edit the issue body. Never `--force` on worktrees; `git branch -D`
  only when the PR is merged and the local tip equals its `headRefOid`.
* R6 — Cloud chats: no `SendMessage`, no archive, no worktree removal; Carlos
  is told what to do by hand.
* R7 — B1 from ADR 01: the update-marker lookup matches only a real marker
  line, not comments that merely mention it.
* R8 — Verified by real skill runs of both `/workflow:recap` and
  `/workflow:close-out`, not only commands run by hand.

## ⚖️ Considered Options

* Reuse: (A) close-out reads `shared/wrap-up.md` like recap · (B) close-out
  invokes `/workflow:recap` first.
* Closing comment marker: (C) end it with the shared update marker · (D) no
  marker.
* Own worktree removal: (E) from the main checkout via `git -C`, after archive,
  best-effort · (F) before archive.
* Worktree already gone after archive (the desktop app may clean it up):
  (G) report it and still delete the branch under the safe rule · (H) stop.
* Real runs: (I) CLI `--plugin-dir` before merge (recap + close-out stop path)
  plus a post-merge finalize run in this chat · (J) CLI only.

## ✅ Decision Outcome

Chosen: **A + C + E + G + I** (Carlos, 2026-10-12, in the #9 chat).

* **A** — same pattern as recap (ADR 01 option A). Close-out adds only the
  decide and finalize steps.
* **C** — the closing comment ends with the shared marker, so a later recap on
  the same issue reports `nothing new`.
* **E** — the order in #9 is kept. A worktree can't remove itself, so the
  commands run with `git -C <main-checkout>`, where the main checkout is the
  first entry of `git worktree list --porcelain`. Failure (e.g. the path is
  still in use on Windows) prints the exact commands to run by hand. The
  commands are printed before archiving, in case archiving ends the session.
* **G** — if the worktree is gone after archive, report `removed by archive`,
  then delete the branch (`-d`, or `-D` under the merged + `headRefOid` rule)
  and prune.
* **I** — before merge, `claude --plugin-dir plugins/workflow` runs
  `/workflow:recap 9` and `/workflow:close-out 9` (stops: the PR is open).
  After merge, Carlos updates the plugin in the desktop app and this chat runs
  `/workflow:close-out` for real to close #9.
* **B1** — the marker lookup uses
  `select(.body | test("(?m)^<!-- workflow:recap head="))`.

### Pros and Cons of the Options

#### A — read the shared file

* Good, because recap and close-out share one procedure (R1).
* Bad, because close-out must read a second file each run (as recap does).

#### B — invoke recap

* Good, because no extra reference.
* Bad, because recap's notify step would post a recap comment right before
  the closing comment (ADR 01 option C).

#### C — marker on the closing comment

* Good, because recap and close-out agree on what was last reported.
* Bad, because the marker is named `workflow:recap` although close-out posts
  it; renaming would break existing markers.

#### E — remove after archive, from the main checkout

* Good, because it keeps the agreed order and the chat's files exist until the
  very end.
* Bad, because archiving may end the session first; mitigated by printing the
  commands before archiving.

#### F — remove before archive

* Good, because the session surely still runs.
* Bad, because it breaks the agreed order (#9 acceptance criteria).

## 📌 Consequences

* Good, because closing an issue is one command that leaves the Governor, the
  issue and the local checkout consistent.
* Good, because B1 stops false "last update" matches for both skills.
* Bad, because the finalize path can only be fully exercised once, on a real
  issue after merge.
