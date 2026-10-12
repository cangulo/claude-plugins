---
name: close-out
description: Wrap up this chat's work on a GitHub issue and, if nothing is pending, post the closing comment, close the issue, set its Project to Done, notify the Governor, archive the chat and remove its worktree.
argument-hint: "[ISSUE]"
disable-model-invocation: true
---

# 🏁 workflow:close-out — finish this chat's issue

Run the same wrap-up as `/workflow:recap`, then close the issue out if nothing
is pending.

## 🛡️ Guarantees

* **Anything pending → stop.** No comment, close, Project change, notify or
  archive. The only side effect is the shared merged-only cleanup.
* **Nothing pending → finalize** without asking for confirmation, in this
  order: comment → issue closed → Project Done → notify → archive → worktree.
* It **never** edits the issue body, never uses `--force` on worktrees, and
  uses `git branch -D` only under the shared cleanup rule (PR `MERGED` and
  local tip equals the PR's `headRefOid`).
* Cloud chats never `SendMessage`, archive or remove worktrees; Carlos is told
  what to do by hand.

## 📋 Steps

1. **Read the shared procedure** at `${CLAUDE_PLUGIN_ROOT}/shared/wrap-up.md`
   and follow its ground rules and output rules throughout.
2. **Wrap-up.** Run its steps 1–6 (context, identify the issue from
   `$ARGUMENTS`, work done, PRs, cleanup, open questions and pending actions).
3. **Decide.**
   * Any open question or pending action → print the report (step 5) with a
     `## 🚧 Before closing` section instead of `## 🎉 Closed out`, stating
     plainly what must happen before the issue can be closed. **Stop.**
   * Both lists empty → finalize (step 4).
4. **Finalize.** Run every sub-step; a failure is reported in its line of the
   `🎉 Closed out` section and doesn't stop the next one, except where noted.
   1. **💬 Comment.** Write the body to a temp file and run
      `gh issue comment <NUMBER> --body-file <file>`:

      ```markdown
      #<NUMBER> closed: <issue title>

      **Summary**
      - <work done items>

      **Merged PRs:** #<PR>, #<PR>

      **Follow-ups**
      - <items added to the ADR follow-ups file or the issue summary, or "none">

      <!-- workflow:recap head=<short-sha> prs=<PR>:<STATE>,… -->
      ```

      The first line is exactly `#<NUMBER> closed: <title>`, using the title
      from `gh`. The last line is the shared update marker (step 8). If the
      comment fails, stop here: the issue isn't closed without its summary.
   2. **🔒 Issue closed.** `gh issue view <NUMBER> --json state`. Usually
      already `CLOSED` by the final PR's `Closes #<NUMBER>` → `already closed`.
      If `OPEN` → `gh issue close <NUMBER> --reason completed`.
   3. **📋 Project.** List the issue's Project items with their `Status`
      field and its options:

      ```text
      gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){projectItems(first:20){nodes{id project{id title field(name:"Status"){... on ProjectV2SingleSelectField{id options{id name}}}}}}}}}' -F o=<owner> -F r=<repo> -F n=<NUMBER>
      ```

      No items → `no Project`. For each item, take the option named `Done`
      and run
      `gh project item-edit --id <item-id> --project-id <project-id> --field-id <field-id> --single-select-option-id <done-option-id>`.
      No `Status` field or `Done` option → report it and continue.
   4. **📣 Notify the Governor** per shared step 7 "Find the Governor":
      * this chat is a Governor → `n/a — this is the Governor`;
      * local, Governor found → `SendMessage` to its session id with the
        comment text, without the marker line;
      * local, none found → say so; the issue comment is the channel;
      * cloud → tell Carlos: say `sync` in the `🏷️<topic>: …` Governor chat.
   5. **🗄️ Archive this chat.**
      * Cloud → tell Carlos to archive the chat by hand.
      * Local → first work out the step-6 commands and print them as a
        fallback (archiving may end this session). Then
        `mcp__ccd_session_mgmt__get_session` for this session and
        `mcp__ccd_session_mgmt__archive_session` with its id.
   6. **🧹 Remove this chat's worktree, last.** Local only; cloud → `n/a`.
      Best-effort: any failure prints the exact command to run by hand.
      * `<main>` = the first `worktree` entry of
        `git worktree list --porcelain` (the main checkout). `<path>` and
        `<branch>` = this chat's worktree and branch from shared step 1.
      * The chat runs in `<main>` → don't remove it or its branch:
        `n/a — chat runs in the main checkout`.
      * `<path>` still exists → `git -C <main> worktree remove <path>`
        (never `--force`). Already gone → `removed by archive`.
      * Branch: apply shared step 5, rule 3 with `git -C <main>` and this
        issue's merged PR for `<branch>`. No merged PR for it → keep it and
        flag it.
      * `git -C <main> worktree prune`.
5. **Print the report** under these headings, in order:
   * `## ✅ Work done` — `[wd#]` items.
   * `## 🔀 PRs` — one line per PR, the `<repo>#<N>` link first.
   * `## 🧹 Cleanup` — `[cl#]` items, or `nothing to clean`.
   * `## ❓ Open questions` — `[oq#]` items.
   * `## ⏳ Pending actions` — `[pa#]` items.
   * Then either `## 🚧 Before closing` (stopped) or `## 🎉 Closed out`
     (finalized), with one line per finalize step: 💬 comment link,
     🔒 issue state, 📋 Project, 📣 Governor, 🗄️ archive, 🧹 worktree/branch
     (or the manual command).

   An empty list section prints `none`.
