---
name: recap
description: Summarize this chat's work on a GitHub issue (work done, PRs, cleanup, open questions, pending actions) and notify the Governor chat of new progress. Read-only apart from merged-only cleanup and the update comment.
argument-hint: "[ISSUE]"
disable-model-invocation: true
---

# 🧾 workflow:recap — wrap up this chat's work

Produce a short wrap-up of the work done in **this chat** on its GitHub issue.

## 🛡️ Guarantees

Recap is **read-only** except for two actions:

1. the merged-only cleanup of this issue's branches/worktrees;
2. notifying the Governor of new progress (an issue comment, plus
   `SendMessage` in local chats).

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
     or when `head` or any PR state differs from the marker, or when the work
     done has items the last update comment doesn't mention (e.g. decisions,
     answered questions).
   * Otherwise → `nothing new to report`; skip step 4.
4. **Notify.** Deliver the update per shared step 7. The comment body:

   ```markdown
   **Recap** · <YYYY-MM-DD> · <chat title, or "cloud chat">

   **Work done**
   - <items, new ones first>

   **PRs**
   - #<PR> <title> — <state>

   **Pending**
   - <pending actions and open questions, or "Nothing pending.">

   <!-- workflow:recap head=<short-sha> prs=<PR>:<STATE>,… -->
   ```

   In the comment, GitHub auto-links `#N`, so plain `#N` is fine there.
5. **Print the report** under these headings, in order:
   * `## ✅ Work done` — `[wd#]` items.
   * `## 🔀 PRs` — one line per PR, the `<repo>#<N>` link first.
   * `## 🧹 Cleanup` — `[cl#]` items (removed, kept, flagged), or
     `nothing to clean`.
   * `## ❓ Open questions` — `[oq#]` items.
   * `## ⏳ Pending actions` — `[pa#]` items.
   * `## 📣 Governor` — one line: what was sent and where (issue comment link,
     Governor chat name, or the "say sync" instruction for cloud),
     `nothing new to report`, or `n/a — this is the Governor`.

   An empty list section prints `none`.
