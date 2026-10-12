# 🧾 Shared wrap-up procedure

The single source of truth for wrapping up a chat in the Governor/Implementator
workflow. `/workflow:recap` and `/workflow:close-out` read this file, run the
steps below, then add their own steps on top. Change the shared behaviour
here, never in a skill.

## 🛡️ Ground rules

* **Never rewrite the issue body.** The Governor owns goals and acceptance
  criteria. Summaries go in issue comments.
* **GitHub failures don't stop the run.** If a `gh` call fails (missing
  permissions are common in cloud chats), note it in the output and continue.
* **Never guess the issue.** If it is unclear, ask and stop.

## 1. 🧭 Context

Work out once, reuse in every step:

* **Repo** — `gh repo view --json name,nameWithOwner,url,defaultBranchRef`.
  `<repo>` is the name without the owner; `<default>` is the default branch.
* **Where the chat runs** — **local** when the desktop-app session tools are
  available (`mcp__ccd_session_mgmt__list_sessions`, `SendMessage`; load them
  with `ToolSearch` if they are deferred). **Cloud** when they aren't, or when
  the `CLAUDE_CODE_REMOTE` environment variable is `true`.
* **Chat title** — local: `mcp__ccd_session_mgmt__get_session` for this
  session. Cloud: usually unknown; leave it empty.
* **Role and topic** — a title starting with `🏷️` means this chat **is** a
  Governor. Otherwise the topic is the text before `: #<NUMBER>` in the title
  (`<topic>: #<NUMBER> <title>`). No title → no topic.
* **This checkout** — current branch (`git branch --show-current`) and
  worktree path (`git rev-parse --show-toplevel`). These are never cleaned up.

## 2. 🔎 Identify the issue

Take the first that applies:

1. The skill argument, if it is an issue number (`8` or `#8`).
2. The branch name `<NUMBER>-<type>-<slug>` (e.g. `8-feat-workflow-recap`).
3. The chat title `<topic>: #<NUMBER> <title>`.

If none gives a number, or they disagree, **ask and stop**. Then read it:
`gh issue view <NUMBER> --json number,title,state,url,body,comments`.

## 3. ✅ Work done

Summarize what this chat accomplished, grouped by area. Sources:

* the conversation (decisions, answers, non-code work such as issue comments);
* `git log --oneline origin/<default>..HEAD`;
* `git diff --stat origin/<default>...HEAD`.

Specific but brief: one line per item.

## 4. 🔀 PRs

The issue's PRs are the union of:

* PRs created, pushed to or reviewed in this chat;
* `gh pr list --state all --limit 100 --json number,title,state,url,headRefName,headRefOid,isDraft,body`
  filtered to head branch `<NUMBER>-*` or a body mentioning `#<NUMBER>` as a
  whole word (`Closes #<NUMBER>`, `Part of #<NUMBER>`; regex `#<NUMBER>\b`, so
  `#8` doesn't match `#80`).

For each: link, title, state (`open`, `draft`, `merged`, `closed`). For open
PRs also show CI (`gh pr checks <PR>`) and review state
(`gh pr view <PR> --json reviewDecision,comments`).

## 5. 🧹 Cleanup

Scope: **only this issue's merged PRs**, local branches and worktrees. Never a
repo-wide sweep. For each merged PR, with `<branch>` = its head branch:

1. **Skip** if `<branch>` is this chat's branch, or its worktree is this chat's
   worktree. Report it as kept: `in use by this chat`.
2. **Worktree** — if `git worktree list --porcelain` shows a worktree on
   `refs/heads/<branch>`, run `git worktree remove <path>` (**never**
   `--force`).
3. **Branch** — if `refs/heads/<branch>` exists locally, run
   `git branch -d <branch>`. If it refuses because the branch isn't merged
   (squash merges), use `git branch -D <branch>` **only when** the PR's `gh`
   state is `MERGED` **and** `git rev-parse refs/heads/<branch>` equals the
   PR's `headRefOid` (nothing unpushed is lost). Otherwise don't delete.
4. Run `git worktree prune` once at the end.

If a command refuses (dirty worktree, local commits not in the PR), **don't
force it**. Flag it with the reason and the command Carlos can run by hand.
`git worktree remove --force` is never used. Remote branches are not touched.
Nothing to do → `nothing to clean`. `/workflow:close-out` reuses rule 3 when
it removes this chat's own worktree and branch at the very end.

## 6. ❓ Open questions and ⏳ pending actions

Computed **after** cleanup.

* **Open questions** — anything waiting for an answer from Carlos or another
  chat.
* **Pending actions** — each of these counts:
  * an open or draft PR;
  * failing or running CI, requested changes, unresolved review comments;
  * blocked items (e.g. the issue's "blocked by" list still open);
  * an acceptance criterion the merged PRs clearly don't satisfy, named
    explicitly. Unchecked boxes alone are **not** pending: nobody ticks them.
  * cleanup items flagged in step 5.

An empty list prints `none`. "Nothing pending" means both lists are empty.

## 7. 📣 Governor

### Find the Governor

* This chat is a Governor (`🏷️`) → skip: `n/a — this is the Governor`.
* Cloud chat → skip the lookup (no `SendMessage` back to local chats).
* Local chat → `mcp__ccd_session_mgmt__list_sessions` (or `ListAgents`), keep
  **running** sessions only, match titles starting with `🏷️<topic>:`.
  Running = `isArchived: false`. `isRunning: false` only means the chat is
  idle between turns; it still receives messages.
  * One match → that chat.
  * Several → ask Carlos which one.
  * None, or no topic → say so; the issue comment is the only channel.

### Deliver an update

1. **Issue comment, always.** Write the body to a temp file and run
   `gh issue comment <NUMBER> --body-file <file>`.
2. **Local** with a Governor found → `SendMessage` to its session id with the
   same text, without the hidden marker.
3. **Cloud** → tell Carlos: say `sync` in the `🏷️<topic>: …` Governor chat.

## 8. 🏷️ Update marker

Every update comment posted by a workflow skill (recap's update and
close-out's closing comment) ends with one hidden line:

```text
<!-- workflow:recap head=<short-sha> prs=<PR>:<STATE>,<PR>:<STATE> -->
```

* `head` — `git rev-parse --short HEAD` of this chat's branch.
* `prs` — the issue's PRs from step 4, sorted by number, with the `gh` state
  (`OPEN`, `MERGED`, `CLOSED`; `DRAFT` for draft PRs). Empty when none: `prs=`.

Latest marker comment (anchored to a line that starts with the marker, so
comments that only mention it don't match):
`gh issue view <NUMBER> --json comments --jq '[.comments[] | select(.body | test("(?m)^<!-- workflow:recap head="))] | last'`.

## 9. 🖨️ Output rules

* Markdown sections with emoji `##` headings, in the order the skill lists.
* List items are numbered per section, from 1, regenerated each run:
  `[wd#]` work done, `[cl#]` cleanup, `[oq#]` open questions,
  `[pa#]` pending actions, e.g. `- [pa1] …`.
* In the PRs section the PR link itself is the item id (no code).
* Every PR or issue is a link whose text is `<repo>#<N>` **without the owner**,
  using the URL from `gh`, e.g.
  `[semver#12](https://github.com/cangulo-actions/semver/issues/12)`.
  Never a bare `#N` in the chat output.
* Single-line sections (e.g. Governor) are not indexed.
