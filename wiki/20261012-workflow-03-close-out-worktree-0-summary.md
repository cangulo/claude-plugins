---
status: "Accepted"
date: 2026-10-12
deciders: [Carlos]
consulted: []
informed: [plugins Governor chat]
tags: [plugins, workflow, skills]
continuation_of: [20261012-workflow-02-close-out]
group: "workflow"
---

# 📝 workflow plugin: close-out removes its worktree, three chat contexts

> ADR **20261012-workflow-03-close-out-worktree** · this is the **summary** (the decision).
> Related: [plan](20261012-workflow-03-close-out-worktree-1-plan.md) · [follow-ups](20261012-workflow-03-close-out-worktree-2-followups.md).
> Continues: [20261012-workflow-02-close-out](20261012-workflow-02-close-out-0-summary.md) (corrects its options E and G, closes its follow-up G1).
> Issue: [claude-plugins#16](https://github.com/cangulo/claude-plugins/issues/16).

## 🚦 Status

Accepted

## 🧭 Context and Problem Statement

`workflow` 0.2.0 close-out ran archive → remove worktree (ADR 02, E + G). In
real use (#9, #11) the chat ended its turn right after `archive_session`, so
the worktree removal never ran. Archiving in the desktop app doesn't delete
the worktree either: it keeps it with no branch checked out, so "removed by
archive" (G) never happens. Carlos removed both worktrees by hand.

Separately, shared step 1 marks a chat as cloud when the desktop-app session
tools are missing. Terminal and headless CLI chats were treated as cloud, and
not always: in #9, recap said local while close-out said cloud (ADR 02 G1).

Experiment on Windows (throwaway worktree, a process with its cwd inside):
`git -C <main> worktree remove <path>` exits 255 (`Permission denied`), but it
has already deleted every file and unregistered the worktree. Only an empty
folder is left, locked until the process exits. `git branch -d` then works.
A hidden process started from `<main>` with a `Remove-Item` loop (no
`-Recurse`) deletes the folder once the holder exits.

## 📋 Requirements

* R1 — After a successful local close-out the chat's worktree and merged
  branch are gone with no manual step, and the chat is archived.
* R2 — Archive is the **very last** action; the report states the verified
  worktree/branch result before it.
* R3 — Removal stays safe: never `--force`; branch rule unchanged (`-d`, or
  `-D` only when the PR is `MERGED` and the local tip equals `headRefOid`).
* R4 — Removal that can't be completed is reported before archiving, with the
  exact commands. No unverified success.
* R5 — One context rule for recap and close-out with three contexts: desktop
  app, local CLI (terminal or headless), cloud.
* R6 — Local CLI chats remove their worktree from the main checkout and skip
  archive and `SendMessage` with a clear note.
* R7 — Shared logic stays in `shared/wrap-up.md`; `workflow` version `0.3.0`.

## ⚖️ Considered Options

* Order: (A) remove worktree + branch, then report, then archive · (B) keep
  archive → remove (ADR 02 E).
* Empty locked folder on Windows: (C) a detached process deletes it after the
  session exits · (D) report it and print the command only.
* Context detection: (E) `CLAUDE_CODE_REMOTE` → cloud; else
  `get_session "self"` works → desktop app; else local CLI · (F) keep
  "session tools available" only.
* Kept worktree after archive: (G) `discard_kept_worktree` · (H) not used.

## ✅ Decision Outcome

Chosen: **A + C + E + H** (Carlos, 2026-10-12, in the #16 chat).

* **A** — finalize order: comment → issue closed → Project Done → notify →
  remove worktree + branch → print report → archive. Every `gh` call runs
  before removal, because `gh` can't resolve the repo once the worktree's
  `.git` file is gone.
* **Verification** — success is read from `git -C <main> worktree list
  --porcelain` and `git -C <main> rev-parse --verify refs/heads/<branch>`, not
  from exit codes (Windows returns 255 though the worktree is unregistered).
* **C** — if only an empty folder is left, start a hidden `pwsh` from
  `<main>` that retries `Remove-Item -LiteralPath <path>` (no `-Recurse`, so
  it can only delete an empty folder) every 5 s for up to 10 min. Report:
  `removed (empty folder deleted after the session exits)`.
* **E** — the same rule in shared step 1, used by both skills. The deciding
  probe is `get_session "self"`, not `ListAgents` or `SendMessage`, which also
  answer in CLI chats and caused the #9 mismatch.
* **H** — `discard_kept_worktree` only works on a session that is already
  archived, so a chat can't use it on itself; it would also discard changes.

### Pros and Cons of the Options

#### A — remove, report, then archive

* Good, because nothing runs after archive, which ends the conversation.
* Good, because the report can state the verified result (R2, R4).
* Bad, because the last steps run with the worktree's files already gone;
  mitigated by running every `gh` and file read first.

#### B — archive then remove

* Bad, because archive ends the turn; the removal never ran in #9 and #11.

#### C — detached cleanup of the empty folder

* Good, because no manual step remains (R1).
* Bad, because a background process outlives the chat; bounded to 10 min and
  only able to delete an empty folder.

#### D — report only

* Good, because simpler.
* Bad, because every Windows close-out would leave a manual step.

#### E — three contexts, probe `get_session`

* Good, because one deterministic rule; CLI chats can still clean up (R5, R6).
* Bad, because a CLI chat relies on the issue comment to reach the Governor.

#### F — session tools only

* Bad, because CLI chats look like cloud and the probe tool varied (#9).

## 📌 Consequences

* Good, because closing an issue leaves no worktree, branch or folder behind.
* Good, because recap and close-out agree on the context.
* Bad, because the finalize path is fully tested only by a real close-out
  after merge (this chat's own close-out with 0.3.0).
