# 🛠️ Implementation plan — workflow plugin: /workflow:close-out

> ADR **20261012-workflow-02-close-out** · this is the **plan** — the **essential
> implementation** to satisfy the decision. `adrs:implement` builds this.
> Related: [summary](20261012-workflow-02-close-out-0-summary.md) · [follow-ups](20261012-workflow-02-close-out-2-followups.md).

## 🧩 Approach

Markdown-only change in one PR (closes #9):

```text
plugins/workflow/
├── .claude-plugin/plugin.json   # version 0.2.0, description mentions close-out
├── shared/wrap-up.md            # B1 fix; mention close-out; main-checkout helper
├── skills/recap/SKILL.md        # unchanged
└── skills/close-out/SKILL.md    # new: wrap-up + decide + finalize
```

`skills/close-out/SKILL.md`:

* Front matter: `name: close-out`, `argument-hint: "[ISSUE]"`,
  `disable-model-invocation: true` (it closes issues and archives chats).
* Guarantees: never edits the issue body, never forces, stops on pending.
* Steps:
  1. Read `${CLAUDE_PLUGIN_ROOT}/shared/wrap-up.md`; run its steps 1–6.
  2. **Decide.** Open questions or pending actions → print the wrap-up plus
     `## 🚧 Before closing` (what must happen) and stop.
  3. **Finalize** (no confirmation):
     1. 💬 Comment: first line `#<NUMBER> closed: <title>`, then summary,
        merged PR links, follow-ups added (ADR follow-ups file or "none"),
        then the shared marker. Posted via shared step 7 "deliver an update"
        part 1 only (the issue comment).
     2. 🔒 `gh issue view --json state`; if `OPEN`,
        `gh issue close <NUMBER> --reason completed`.
     3. 📋 GraphQL `issue.projectItems` with each project's `Status` field and
        options, then `gh project item-edit` to the `Done` option. No Project →
        `no Project`.
     4. 📣 Governor: shared step 7 "find the Governor"; local + found →
        `SendMessage` with the comment text without the marker; cloud → tell
        Carlos to say `sync`; Governor chat → `n/a`.
     5. 🗄️ Archive: local → print the step-6 fallback commands first, then
        `get_session` → `archive_session`. Cloud → tell Carlos to archive it.
     6. 🧹 Own worktree, local only: main checkout = first `worktree` entry of
        `git worktree list --porcelain`. Skip worktree removal when this chat
        runs in the main checkout. Else, if the path still exists,
        `git -C <main> worktree remove <path>`; if gone, `removed by archive`.
        Then the branch per shared step 5.3 with `git -C <main>`, then
        `git -C <main> worktree prune`. Any failure → print the command.
  4. Print the wrap-up sections (as recap) plus `## 🎉 Closed out` with one
     line per finalize step.

`shared/wrap-up.md`:

* Intro: name `/workflow:close-out` as a user of the file.
* Step 8: B1, `test("(?m)^<!-- workflow:recap head=")`; note that close-out's
  closing comment also carries the marker.
* Step 5: the branch rule is reused by close-out's own-worktree step (no copy).

## 📋 Steps

1. Fix B1 and the intro in `plugins/workflow/shared/wrap-up.md`.
2. Write `plugins/workflow/skills/close-out/SKILL.md`.
3. Bump `plugins/workflow/.claude-plugin/plugin.json` to `0.2.0`; update its
   description (and the marketplace entry description).
4. Update `README.md`: workflow section, close-out usage, layout.
5. Mark B1 done in ADR 01 follow-ups (status reason only).
6. Verification:
   * `claude plugin validate ./plugins/workflow` and `claude plugin validate .`.
   * `validate-adr.py` on both trios.
   * B1: the new jq filter matches 0 comments on #8 (old one matched 2).
   * Real runs with `claude --plugin-dir plugins/workflow` (needs
     `claude /login`): `/workflow:recap 9`, `/workflow:close-out 9` (stop path).
   * After merge: `/workflow:close-out` in this chat (finalize path), results
     in the closing issue comment.

## ⚠️ Risks and Mitigations

* Risk — closing an issue with work left. Mitigation — any pending action or
  open question stops the run; pending is computed after cleanup.
* Risk — archive ends the session before worktree removal. Mitigation — print
  the removal commands before archiving.
* Risk — Project field names differ (`Status`/`Done`). Mitigation — on no
  match, report and continue (GitHub failures don't stop the run).
