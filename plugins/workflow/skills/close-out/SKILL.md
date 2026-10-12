---
name: close-out
description: Wrap up this chat's work on a GitHub issue and, if nothing is pending, post the closing comment, close the issue, set its Project to Done, notify the Governor, remove its worktree and archive the chat last. Use it once the issue's final PR (the one with `Closes #N`) has merged and the issue is closed, when the Governor or Carlos asks to close out, or whenever finishing the issue fits the conversation. Stops and lists what is left if anything is pending.
argument-hint: "[ISSUE]"
---

# 🏁 workflow:close-out — finish this chat's issue

Run the same wrap-up as `/workflow:recap`, then close the issue out if nothing
is pending.

## 🛡️ Guarantees

* **Same run, typed or automatic.** When Claude invokes it on its own, it
  keeps the pending guard and, when nothing is pending, does the full
  finalize, archive included, exactly as when Carlos types it.
* **Anything pending → stop.** No comment, close, Project change, notify or
  archive. The only side effect is the shared merged-only cleanup.
* **Nothing pending → finalize** without asking for confirmation, in this
  order: comment → issue closed → Project Done → notify → worktree and
  branch → report → archive. **Archive is always the last action**: it ends
  the conversation, so nothing after it would run.
* It **never** edits the issue body, never uses `--force` on worktrees, and
  uses `git branch -D` only under the shared cleanup rule (PR `MERGED` and
  local tip equals the PR's `headRefOid`).
* It reports only verified results. A worktree or branch it couldn't remove
  is flagged, with the commands, before archiving.
* Per context (shared step 1): desktop-app chats do everything; local CLI
  chats remove their worktree but skip `SendMessage` and archive; cloud chats
  do neither. Each skip is a clear line in the report.

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
      ISSUE#<NUMBER> closed: <issue title>

      **Summary**
      - <work done items>

      **Merged PRs:** [PR#<N>](<url>), [PR#<N>](<url>)

      **Follow-ups**
      - <items added to the ADR follow-ups file or the issue summary, or "none">

      <!-- workflow:recap head=<short-sha> prs=<PR>:<STATE>,… -->
      ```

      The first line is exactly `ISSUE#<NUMBER> closed: <title>` (plain text,
      no link, so the Governor can match it; `EPIC#` if the issue's type is
      `Epic`), using the title from `gh`.
      Every other PR or issue follows the shared link rule (step 9). The last line is the shared update marker (step 8). If the
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
      * desktop app, Governor found → `SendMessage` to its session id with
        the comment text, without the marker line;
      * desktop app, none found → say so; the issue comment is the channel;
      * local CLI or cloud → `no SendMessage from a <CLI|cloud> chat`; tell
        Carlos: say `sync` in the `🏷️<topic>: …` Governor chat.
   5. **🧹 Remove this chat's worktree and branch.** Every `gh` call is done
      by now. Desktop app or local CLI → shared step 10. Cloud → `n/a — cloud
      chat`.
   6. **🖨️ Print the report** (step 5), including the verified worktree and
      branch result and the archive line below. Print it **before** archiving.
   7. **🗄️ Archive this chat, last.** Nothing runs after this sub-step.
      * Desktop app → `mcp__ccd_session_mgmt__archive_session` with
        `session_id: "self"`. If it is refused (e.g. pinned or open on
        screen), say so in one line.
      * Local CLI → `archive skipped: CLI chat (no session tools)`.
      * Cloud → tell Carlos to archive the chat by hand.
5. **Print the report** under these headings, in order:
   * `## ✅ Work done` — `[wd#]` items.
   * `## 🔀 PRs` — one line per PR, the `PR#<N>` link first (shared link
     rule).
   * `## 🧹 Cleanup` — `[cl#]` items, or `nothing to clean`.
   * `## ❓ Open questions` — `[oq#]` items.
   * `## ⏳ Pending actions` — `[pa#]` items.
   * Then either `## 🚧 Before closing` (stopped) or `## 🎉 Closed out`
     (finalized), with one line per finalize step: 💬 comment link,
     🔒 issue state, 📋 Project, 📣 Governor, 🧹 worktree/branch (verified
     result, or the manual commands), 🗄️ archive (`archiving now` in the
     desktop app, or why it is skipped).

   An empty list section prints `none`.
