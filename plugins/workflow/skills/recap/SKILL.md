---
name: recap
description: Summarize this chat's work on a GitHub issue (work done, PRs, cleanup, open questions, pending actions) and notify the Governor chat of new progress. Use it after pushing to a PR once its CI is green, when the Governor or Carlos asks for a recap or status, or whenever a wrap-up of the issue's progress fits the conversation. Read-only apart from merged-only cleanup and the update comment; posts nothing when nothing changed.
argument-hint: "[ISSUE]"
---

# 🧾 workflow:recap — wrap up this chat's work

Produce a short wrap-up of the work done in **this chat** on its GitHub issue.

## 🛡️ Guarantees

Recap is **read-only** except for two actions:

1. the merged-only cleanup of this issue's branches/worktrees;
2. notifying the Governor of new progress (an issue comment, plus
   `SendMessage` in desktop-app chats; contexts per shared step 1).

It **never** edits the issue body, commits, pushes, closes the issue, archives
the chat, or touches the worktree/branch this chat runs in.

## 📋 Steps

1. **Read the shared procedure** at `${CLAUDE_PLUGIN_ROOT}/shared/wrap-up.md`
   and follow its ground rules and output rules throughout.
2. **Wrap-up.** Run its steps 1–6 (context, identify the issue from
   `$ARGUMENTS`, work done, PRs, cleanup, open questions and pending actions).
3. **Decide whether there is new progress.**
   * This chat is a Governor → skip to step 5 (`n/a — this is the Governor`).
   * Find the latest update marker on the issue (shared step 8).
   * **New progress** when there is no marker yet and the chat has work done,
     or when `head` or any PR state differs from the marker.
   * `typed` runs (shared step 1) also count work done that the last update
     comment doesn't mention (e.g. decisions, answered questions). `auto` runs
     don't, so repeated automatic recaps stay silent until a push or a PR
     state change.
   * Otherwise → `nothing new to report`; skip step 4.
4. **Notify.** Deliver the update per shared step 7. The comment body:

   ```markdown
   **Recap** · <YYYY-MM-DD> · <chat title, or "CLI chat" / "cloud chat">

   **Work done**
   - <items, new ones first>

   **PRs**
   - [PR#<N>](<url>) <title> — <state>

   **Pending**
   - <pending actions and open questions, or "Nothing pending.">

   <!-- workflow:recap head=<short-sha> prs=<PR>:<STATE>,… -->
   ```

   Every PR or issue in the comment follows the shared link rule (step 9).
5. **Print the report** under these headings, in order:
   * `## ✅ Work done` — `[wd#]` items.
   * `## 🔀 PRs` — one line per PR, the `PR#<N>` link first (shared link
     rule).
   * `## 🧹 Cleanup` — `[cl#]` items (removed, kept, flagged), or
     `nothing to clean`.
   * `## ❓ Open questions` — `[oq#]` items.
   * `## ⏳ Pending actions` — `[pa#]` items.
   * `## 📣 Governor` — one line: what was sent and where (issue comment link,
     Governor chat name, or the "say sync" instruction for local CLI and cloud chats),
     `nothing new to report`, or `n/a — this is the Governor`.

   An empty list section prints `none`.
