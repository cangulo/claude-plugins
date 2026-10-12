---
status: "Accepted"
date: 2026-10-12
deciders: [Carlos]
consulted: []
informed: [plugins Governor chat]
tags: [plugins, workflow, skills]
continuation_of: [20261012-workflow-03-close-out-worktree]
group: "workflow"
---

# 📝 workflow plugin: auto-invocation, CLAUDE.md link format, detached worktrees

> ADR **20261012-workflow-04-auto-invoke-links** · this is the **summary** (the decision).
> Related: [plan](20261012-workflow-04-auto-invoke-links-1-plan.md) · [follow-ups](20261012-workflow-04-auto-invoke-links-2-followups.md).
> Continues: [20261012-workflow-03-close-out-worktree](20261012-workflow-03-close-out-worktree-0-summary.md).
> Issue: [ISSUE#21](https://github.com/cangulo/claude-plugins/issues/21).

## 🚦 Status

Accepted

## 🧭 Context and Problem Statement

`workflow` 0.3.0 has two gaps against Carlos' current `~/.claude/CLAUDE.md`:

* **Links.** The skills render `<repo>#<N>` links. CLAUDE.md now wants the
  object type in the link text: `PR#N`, `EPIC#N` (issue type `Epic`) or
  `ISSUE#N`, with no repo name for the chat's own repo and a `repo/` prefix
  (no org) for other repos, in chat output **and** in comments Claude writes.
* **Explicit only.** Both skills set `disable-model-invocation: true`, so
  Carlos has to type them after every PR and at the end of every issue, even
  though CLAUDE.md already says when they run (after each PR; when the issue
  is closed).

Close-outs before 0.3.0 archived the chat first. The desktop app then keeps
the worktree with **no branch checked out** (detached `HEAD`), and the 0.3.0
cleanup only matches worktrees by `refs/heads/<branch>`, so it never sees
them.

The issue also asked for a stale-skill check (a running chat keeps the plugin
version it loaded). Carlos dropped it in the #21 chat: he is the only user
and reinstalls and reloads by hand.

## 📋 Requirements

* R1 — Every PR or issue reference in chat output and in posted comments is a
  link `PR#N` / `ISSUE#N` / `EPIC#N`; own repo without prefix, others with
  `<repo>/`. Closing keywords, commit messages, PR titles and branch names
  keep `#N`.
* R2 — `EPIC#N` only when the issue's GitHub issue type is `Epic`; repos
  without issue types render `ISSUE#N`.
* R3 — Claude can invoke both skills on its own; the descriptions name the
  triggers: recap after a PR push once CI is green; close-out after the final
  PR (`Closes #N`) merges and the issue is closed; either one when the
  Governor asks; otherwise when it fits the conversation.
* R4 — Close-out keeps its guard (anything pending → stop, only the shared
  cleanup) and, when nothing is pending, does the full finalize with archive
  last, whether typed or invoked by Claude.
* R5 — Repeated automatic recaps post nothing when nothing changed.
* R6 — Cleanup also removes a clean detached worktree whose `HEAD` is the
  `headRefOid` of one of this issue's merged PRs; never `--force`; anything
  else is flagged with the command.
* R7 — Shared logic stays in `shared/wrap-up.md`; `workflow` `0.4.0`; the
  README says running chats keep the version they loaded.

## ⚖️ Considered Options

* Issue type for `EPIC#N`: (A) GraphQL `issue { issueType { name } }` per
  referenced issue · (B) treat issues with sub-issues as epics.
* Close-out's first comment line: (C) `ISSUE#<N> closed: <title>` · (D) keep
  `#<N> closed: <title>`.
* New progress for recap: (E) keep 0.3.0's marker rule, but the "work done
  not mentioned yet" clause counts only for typed runs · (F) keep it for
  every run.
* Stale skills: (G) no check, README note only · (H) compare the loaded
  `plugin.json` with the installed one.

## ✅ Decision Outcome

Chosen: **A + C + E + G** (Carlos, 2026-10-12, in the #21 chat; E
proposed by the Implementator and accepted).

* **A** — the type is GitHub's own field; personal repos return `null` →
  `ISSUE#N` (R2). One GraphQL call per issue referenced.
* **C** — the whole comment follows the link rule. The Implementator rule in
  `~/.claude/CLAUDE.md` spells `#<NUMBER> closed:`; that line is updated via
  the 📜Personal CLAUDE.md chat (follow-up I1).
* **E** — automatic runs post only when `head` or a PR state changed against
  the last marker (R5). A fuzzy "new decisions" judgement could repost on
  every automatic run; when typed, Carlos asked for it, so it still applies.
* **G** — Carlos' call: one consumer, manual reinstall. The README explains
  that a running chat keeps the version it loaded.
* Auto-invocation: drop `disable-model-invocation`; the triggers go in the
  `description` (what Claude reads to decide). The skill bodies don't branch
  on who invoked them, except E.
* Detached worktrees: shared step 5 gets a second pass over
  `git worktree list --porcelain` entries with `detached`, matched by full
  `HEAD` sha against this issue's merged PRs' `headRefOid`, removed only when
  `git -C <path> status --porcelain` is empty.

### Pros and Cons of the Options

#### A — GraphQL issue type

* Good, because it is exact and matches what CLAUDE.md means by "type Epic".
* Bad, because one extra call per issue; cheap for a handful of references.

#### B — sub-issues imply epic

* Bad, because a task can have sub-issues; it guesses.

#### C — `ISSUE#N closed:`

* Good, because one link rule everywhere, no exception to remember.
* Bad, because CLAUDE.md must change in step.

#### D — keep `#N closed:`

* Good, because no CLAUDE.md change.
* Bad, because the one line that breaks the rule is the most visible one.

#### E — automatic runs post only on head/PR change

* Good, because repeated automatic recaps are silent (R5).
* Bad, because a decision with no commit isn't reported until a typed recap
  or the next push.

#### F — same rule for every run

* Bad, because the fuzzy clause can fire on each automatic run.

#### G — no stale check

* Good, because nothing to maintain; Carlos reloads after updates.
* Bad, because an old chat runs old logic silently.

#### H — version check

* Good, because a stale chat says so.
* Bad, because more steps for a single-user setup.

## 📌 Consequences

* Good, because Carlos no longer types recap and close-out in each chat.
* Good, because links read the same in chat, comments and CLAUDE.md.
* Good, because worktrees left by 0.2.0 close-outs are cleaned on the next run
  of the same issue.
* Bad, because auto-invocation depends on Claude matching the description; a
  missed trigger is fixed by typing the skill.
* Bad, because a full automatic close-out archives the chat without a prompt;
  the pending guard is the only brake.
