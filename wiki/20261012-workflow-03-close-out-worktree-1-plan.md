# 🛠️ Implementation plan — workflow plugin: close-out removes its worktree, three chat contexts

> ADR **20261012-workflow-03-close-out-worktree** · this is the **plan** — the **essential
> implementation** to satisfy the decision. `adrs:implement` builds this.
> Related: [summary](20261012-workflow-03-close-out-worktree-0-summary.md) · [follow-ups](20261012-workflow-03-close-out-worktree-2-followups.md).

## 🧩 Approach

Markdown-only change in one PR (closes #16):

```text
plugins/workflow/
├── .claude-plugin/plugin.json   # version 0.3.0
├── shared/wrap-up.md            # step 1: three contexts; step 5: own-worktree removal; step 7 per context
├── skills/recap/SKILL.md        # notes per context (no archive/removal anyway)
└── skills/close-out/SKILL.md    # new finalize order; archive last
```

`shared/wrap-up.md`:

* Step 1 **Where the chat runs**, checked in order, once:
  1. `CLAUDE_CODE_REMOTE` is `true` → **cloud**.
  2. `mcp__ccd_session_mgmt__get_session` with `"self"` returns this session
     (load it with `ToolSearch` if deferred) → **desktop app**; keep the
     result for the title.
  3. Otherwise → **local CLI** (terminal or headless).
  `ListAgents` / `SendMessage` answering doesn't decide the context.
* Step 1 **Main checkout**: `<main>` = first `worktree` entry of
  `git worktree list --porcelain`.
* New section **Remove this chat's worktree** (used by close-out, after all
  `gh` calls): skip when the chat runs in `<main>`; else
  `git -C <main> worktree remove <path>` (never `--force`); verify with
  `git -C <main> worktree list --porcelain`; if unregistered but the folder
  remains (Windows lock), start the detached `Remove-Item` loop (no
  `-Recurse`) from `<main>`; branch per step 5 rule 3 with `git -C <main>`;
  `git -C <main> worktree prune`; verify the branch with `rev-parse --verify`.
  Still registered → flag with the exact commands.
* Step 7 per context: desktop app → `SendMessage`; local CLI → note "no
  `SendMessage` from a CLI chat", issue comment only; cloud → "say sync".

`skills/close-out/SKILL.md`:

* Guarantees: order comment → closed → Project → notify → worktree → report →
  archive; archive is last and only in the desktop app.
* Finalize sub-steps reordered; the worktree step references the shared
  section; the report is printed **before** archive; archive: desktop app →
  `archive_session` `"self"`; local CLI → "archive skipped: CLI chat";
  cloud → tell Carlos.
* Remove the "removed by archive" path.

## 📋 Steps

1. Edit `plugins/workflow/shared/wrap-up.md` (step 1, worktree section, step 7).
2. Edit `plugins/workflow/skills/close-out/SKILL.md` (order, archive last).
3. Edit `plugins/workflow/skills/recap/SKILL.md` (context wording).
4. Bump `plugins/workflow/.claude-plugin/plugin.json` to `0.3.0`; README if it
   mentions the order or contexts.
5. ADR 02 follow-ups: G1 status reason → done in #16.
6. Verification: `claude plugin validate`, `validate-adr.py` on ADR 02 and 03,
   CI `validate` green; after merge, this chat's own `/workflow:close-out`
   with 0.3.0 (worktree, branch and folder gone, archived last).

## ⚠️ Risks and Mitigations

* Risk — a step needs the repo after removal. Mitigation — all `gh` calls and
  reads happen before; `gh` calls after removal would need `-R <owner/repo>`.
* Risk — the detached loop deletes something else. Mitigation — fixed
  `-LiteralPath`, no `-Recurse`, bounded to 10 min.
* Risk — archive is refused (e.g. the session is pinned or open). Mitigation —
  report it; the worktree is already gone.
