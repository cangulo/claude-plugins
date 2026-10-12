# 🛠️ Implementation plan — workflow plugin: auto-invocation, CLAUDE.md link format, detached worktrees

> ADR **20261012-workflow-04-auto-invoke-links** · this is the **plan** — the **essential
> implementation** to satisfy the decision. `adrs:implement` builds this.
> Related: [summary](20261012-workflow-04-auto-invoke-links-0-summary.md) · [follow-ups](20261012-workflow-04-auto-invoke-links-2-followups.md).

## 🧩 Approach

Markdown-only change in one PR (closes #21):

```text
plugins/workflow/
├── .claude-plugin/plugin.json   # version 0.4.0
├── shared/wrap-up.md            # link rule, issue types, detached cleanup, invocation note
├── skills/recap/SKILL.md        # auto-invocable, triggers, comment template, automatic-run rule
└── skills/close-out/SKILL.md    # auto-invocable, triggers, comment template
README.md                        # auto-invocation, links, loaded version note
```

`shared/wrap-up.md`:

* Step 1 **Repo**: also keep `<owner>` (for GraphQL).
* Step 4 **PRs**: no change to the query.
* Step 5 **Cleanup**, new rule after the branch rule: for each
  `git worktree list --porcelain` entry with a `detached` line, skip this
  chat's worktree and `<main>`; if its `HEAD` equals the full `headRefOid` of
  one of this issue's merged PRs and `git -C <path> status --porcelain` is
  empty → `git worktree remove <path>` (never `--force`). Matching sha but
  dirty, or a refused remove → flag with the command. Detached worktrees whose
  `HEAD` matches no merged PR of this issue are out of scope (not listed).
* Step 9 **Output rules** → new **Link rule**, used for chat output and every
  comment a skill posts:
  * PR → `PR#<N>`; issue → `EPIC#<N>` if its type is `Epic`, else `ISSUE#<N>`.
  * Own repo (step 1) → no prefix; other repos → `<repo>/` (no owner),
    e.g. `[semver/PR#12](…)`.
  * Link target is the URL from `gh`.
  * Type lookup: `gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){issueType{name}}}}' -F o=… -F r=… -F n=…`;
    `null` or error → `ISSUE#N`. Look up each issue once per run.
  * Native `#N` stays in closing keywords, commit messages, PR titles, branch
    names.
* New short section **Invocation**: skills run when typed or when Claude
  invokes them; a run states which (`typed` / `auto`) in the report header
  line, and the recap rule for automatic runs (decision E) lives in recap.

`skills/recap/SKILL.md`:

* Front matter: remove `disable-model-invocation`; description names the
  triggers (after a PR push once CI is green; Governor asks "recap"; otherwise
  when it fits).
* Step 3: automatic run → new progress only when `head` or a PR state differs
  from the marker (or no marker and work done).
* Step 4 template: `[PR#N](url) <title> — <state>`; drop the "plain #N is
  fine" line.

`skills/close-out/SKILL.md`:

* Front matter: remove `disable-model-invocation`; description names the
  triggers (final PR with `Closes #N` merged and issue closed; Governor asks
  "close out"; otherwise when it fits) and says it stops when anything is
  pending.
* Guarantees: same behaviour typed or automatic; full finalize, archive last.
* Comment template: first line `ISSUE#<N> closed: <title>` (plain text, as
  the Governor matches on it), merged PRs as `[PR#N](url)`.

## 📋 Steps

1. Edit `plugins/workflow/shared/wrap-up.md` (owner, detached cleanup, link
   rule, invocation).
2. Edit `plugins/workflow/skills/recap/SKILL.md`.
3. Edit `plugins/workflow/skills/close-out/SKILL.md`.
4. Bump `plugins/workflow/.claude-plugin/plugin.json` to `0.4.0`.
5. README: drop "Runs only when typed", describe triggers and links, link
   ADR 03 and 04, note that running chats keep the version they loaded.
6. Verification: `claude plugin validate --strict` on the marketplace and
   `plugins/workflow`, `validate-adr.py` on ADR 04, CI `validate` green;
   headless `claude -p --plugin-dir ./plugins/workflow` runs where Claude
   invokes recap and close-out (pending path) with no slash command typed;
   a throwaway detached worktree to exercise the cleanup rule. After merge:
   Carlos reloads this chat with 0.4.0 and Claude invokes close-out on its
   own (full finalize).

## ⚠️ Risks and Mitigations

* Risk — Claude auto-invokes close-out too early. Mitigation — the pending
  guard: open PRs or an open issue blocker stop it with no side effects.
* Risk — automatic recaps spam the issue. Mitigation — decision E.
* Risk — a detached worktree holds work. Mitigation — clean status and exact
  merged-PR sha required; never `--force`.
