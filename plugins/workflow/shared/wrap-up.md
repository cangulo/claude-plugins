# 🧾 Shared wrap-up procedure

The single source of truth for wrapping up a chat in the Governor/Implementator
workflow. `/workflow:recap` and `/workflow:close-out` read this file, run the
steps below, then add their own steps on top. Change the shared behaviour
here, never in a skill. Both skills run when Carlos types them or when Claude
invokes them on its own (triggers in each skill's `description`).

## 🛡️ Ground rules

* **Never rewrite the issue body.** The Governor owns goals and acceptance
  criteria. Summaries go in issue comments.
* **GitHub failures don't stop the run.** If a `gh` call fails (missing
  permissions are common in cloud chats), note it in the output and continue.
* **Never guess the issue.** If it is unclear, ask and stop.

## 1. 🧭 Context

Work out once, reuse in every step:

* **Repo** — `gh repo view --json name,owner,url,defaultBranchRef`.
  `<owner>` is the owner login, `<repo>` the name without the owner (the
  chat's **own repo** for the link rule, step 9); `<default>` is the default
  branch.
* **Invocation** — `typed` when Carlos typed the skill (`/workflow:<skill>`),
  `auto` when Claude invoked it on its own. Both run the same steps; only
  recap's new-progress rule differs.
* **Where the chat runs** — check in this order, once, and reuse the answer
  (recap and close-out must agree):
  1. **Cloud** — the `CLAUDE_CODE_REMOTE` environment variable is `true`.
  2. **Desktop app** — `mcp__ccd_session_mgmt__get_session` with
     `session_id: "self"` returns this session (load it with `ToolSearch` if
     it is deferred). Keep the result for the title.
  3. **Local CLI** — anything else (a terminal or headless `claude`).

  Only these probes decide. `ListAgents` or `SendMessage` answering doesn't
  make a chat a desktop-app chat; CLI chats have them too. What each context
  may do:

  | Context | `SendMessage` | Remove own worktree | Archive |
  | ------- | ------------- | ------------------- | ------- |
  | Desktop app | yes | yes | yes |
  | Local CLI | no | yes | no |
  | Cloud | no | no | no |

  "Local" below means desktop app or local CLI.
* **Chat title** — desktop app: from `get_session`. Local CLI and cloud:
  usually unknown; leave it empty.
* **Role and topic** — a title starting with `🏷️` means this chat **is** a
  Governor. Otherwise the topic is the text before `: #<NUMBER>` in the title
  (`<topic>: #<NUMBER> <title>`). No title → no topic.
* **This checkout** — current branch (`git branch --show-current`) and
  worktree path (`git rev-parse --show-toplevel`). Step 5 never cleans them
  up; only close-out removes them, last (step 10).
* **Main checkout** — `<main>` = the first `worktree` entry of
  `git worktree list --porcelain`.

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
4. **Detached worktrees** — left by close-outs before 0.3.0, which archived
   the chat first. For each `git worktree list --porcelain` entry with a
   `detached` line, other than this chat's worktree and `<main>`:
   * its `HEAD` equals the full `headRefOid` of one of this issue's merged
     PRs **and** `git -C <path> status --porcelain` prints nothing → run
     `git worktree remove <path>` (**never** `--force`);
   * same `HEAD` but dirty, or the remove refuses → flag it with the reason
     and the command;
   * any other `HEAD` → not this issue's; leave it and don't list it.
5. Run `git worktree prune` once at the end.

If a command refuses (dirty worktree, local commits not in the PR), **don't
force it**. Flag it with the reason and the command Carlos can run by hand.
`git worktree remove --force` is never used. Remote branches are not touched.
Nothing to do → `nothing to clean`. `/workflow:close-out` reuses rule 3 when
it removes this chat's own worktree and branch (step 10).

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
* Cloud or local CLI chat → skip the lookup (no `SendMessage` from these
  chats).
* Desktop-app chat → `mcp__ccd_session_mgmt__list_sessions` (or `ListAgents`), keep
  **running** sessions only, match titles starting with `🏷️<topic>:`.
  Running = `isArchived: false`. `isRunning: false` only means the chat is
  idle between turns; it still receives messages.
  * One match → that chat.
  * Several → ask Carlos which one.
  * None, or no topic → say so; the issue comment is the only channel.

### Deliver an update

1. **Issue comment, always.** Write the body to a temp file and run
   `gh issue comment <NUMBER> --body-file <file>`.
2. **Desktop app** with a Governor found → `SendMessage` to its session id
   with the same text, without the hidden marker.
3. **Local CLI or cloud** → `no SendMessage from a <CLI|cloud> chat`; tell
   Carlos: say `sync` in the `🏷️<topic>: …` Governor chat.

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
* Single-line sections (e.g. Governor) are not indexed.

### 🔗 Link rule

Applies to the chat output **and** every comment a workflow skill posts.

* Every PR or issue is a link to its URL from `gh`. The link text names the
  object type:
  * pull request → `PR#<N>`;
  * issue of GitHub issue type `Epic` → `EPIC#<N>`;
  * any other issue → `ISSUE#<N>`.
* Own repo (step 1) → no prefix, e.g.
  `[ISSUE#8](https://github.com/cangulo/claude-plugins/issues/8)`. Other
  repos → `<repo>/` without the owner, e.g.
  `[semver/PR#12](https://github.com/cangulo-actions/semver/pull/12)`.
* Issue type — once per issue per run:

  ```text
  gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){issueType{name}}}}' -F o=<owner> -F r=<repo> -F n=<N>
  ```

  `null` (personal repos have no issue types) or an error → `ISSUE#<N>`.
* Never a bare `#N`. Native `#N` stays only where GitHub needs it: closing
  keywords (`Closes #N`, `Part of #N`), commit messages, PR titles and
  branch names. The hidden update marker (step 8) keeps its own format.

## 10. 🧹 Remove this chat's worktree

Used by `/workflow:close-out` only, in local chats (desktop app or local CLI),
**after every `gh` call and file read**: once the worktree's `.git` file is
gone, `gh` can't resolve the repo from this folder. `<path>` and `<branch>` are
this chat's worktree and branch, `<main>` the main checkout (step 1).

1. **Main checkout** — the chat runs in `<main>` → don't remove it or its
   branch: `n/a — chat runs in the main checkout`. Stop here.
2. **Worktree** — `git -C <main> worktree remove <path>` (**never**
   `--force`). Judge the result by state, not by exit code:
   * `git -C <main> worktree list --porcelain` has no `worktree <path>` entry
     → unregistered.
   * Still registered → it refused (dirty files, locked). Flag it with the
     reason and the commands; skip the branch.
3. **Locked folder (Windows)** — while this chat runs, its cwd locks
   `<path>`: git deletes the files and unregisters the worktree, but exits
   with `Permission denied` and leaves an empty folder. If `<path>` still
   exists and is empty, start a hidden process from `<main>` that deletes it
   after the session exits:

   ```powershell
   Start-Process pwsh -WorkingDirectory '<main>' -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"`$p='<path>'; for(`$i=0; `$i -lt 120 -and (Test-Path -LiteralPath `$p); `$i++){ Start-Sleep 5; Remove-Item -LiteralPath `$p -ErrorAction SilentlyContinue }"
   ```

   `Remove-Item` has no `-Recurse`, so it can only delete an empty folder;
   the loop gives up after 10 minutes. Report
   `removed (empty folder deleted after the session exits)`. Not empty →
   don't start it; flag the folder.
4. **Branch** — step 5 rule 3 with `git -C <main>` and this issue's merged PR
   for `<branch>`. No merged PR for it → keep it and flag it. Verify:
   `git -C <main> rev-parse --verify --quiet refs/heads/<branch>` prints
   nothing.
5. `git -C <main> worktree prune`.

Report only what was verified: `worktree removed`, `branch deleted`, or the
flagged item with the exact commands Carlos can run by hand.
