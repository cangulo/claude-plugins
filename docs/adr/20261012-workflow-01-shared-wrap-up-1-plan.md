# 🛠️ Implementation plan — workflow plugin: shared wrap-up and /workflow:recap

> ADR **20261012-workflow-01-shared-wrap-up** · this is the **plan** — the **essential
> implementation** to satisfy the decision. `adrs:implement` builds this.
> Related: [summary](20261012-workflow-01-shared-wrap-up-0-summary.md) · [follow-ups](20261012-workflow-01-shared-wrap-up-2-followups.md).

## 🧩 Approach

Markdown-only change in one PR (closes #8), following the `adrs` plugin layout:

```text
plugins/workflow/
├── .claude-plugin/plugin.json   # name workflow, version 0.1.0
├── shared/wrap-up.md            # the shared procedure (R1)
└── skills/recap/SKILL.md        # thin skill: wrap-up + notify on new progress
```

`shared/wrap-up.md` sections:

1. **Context** — local vs cloud (tool availability), chat title
   (`get_session` locally; unknown in cloud), topic and role (🏷️ = Governor).
2. **Identify the issue** — argument → branch `<N>-<type>-<slug>` → chat title
   `<topic>: #<N> <title>`; ask if unclear. Read it with `gh issue view`.
3. **Work done** — conversation + `git log origin/<default>..HEAD` + diff stat.
4. **PRs** — PRs touched in the chat plus `gh pr list --state all` filtered by
   head branch `<N>-*` or `#<N>` as a whole word (regex `#<N>\b`) in the body; state, CI and review for open ones.
5. **Cleanup** — merged PRs of this issue only: skip the current branch and
   worktree; `git worktree remove` (no `--force`), `git branch -d` (or `-D`
   only when the PR is merged and the local tip equals its `headRefOid`),
   `git worktree prune`; flag anything that fails.
6. **Open questions / pending** — computed after cleanup.
7. **Find the Governor** and **deliver an update** (issue comment always;
   `SendMessage` locally; "say sync" in cloud; skip if this chat is a Governor).
8. **Output rules** — headings, codes, `repo#N` links, GitHub failures are
   reported and don't stop the run, never edit the issue body.
9. **Update marker** — `<!-- workflow:recap head=<sha> prs=<N>:<state>,… -->`.

`skills/recap/SKILL.md`: front matter with `disable-model-invocation: true` and
`argument-hint: "[ISSUE]"`; states the read-only guarantees (R2, R3); runs
wrap-up steps; decides new progress by comparing with the latest marker
comment; delivers the update; prints the six sections.

## 📋 Steps

1. Create `plugins/workflow/.claude-plugin/plugin.json` (version `0.1.0`).
2. Write `plugins/workflow/shared/wrap-up.md`.
3. Write `plugins/workflow/skills/recap/SKILL.md`.
4. Add `workflow` to `.claude-plugin/marketplace.json` and update its description.
5. Update `README.md`: plugins table, a `workflow` section, install line, layout.
6. Verification:
   * `claude plugin validate ./plugins/workflow` and `claude plugin validate .`.
   * `grep -ri jira plugins/workflow` returns nothing.
   * Manual run of `/workflow:recap 8` with `claude --plugin-dir plugins/workflow`
     in this worktree (local path), checking sections, codes and the marker.

## ⚠️ Risks and Mitigations

* Risk — cleanup deletes the wrong branch. Mitigation — merged-only commands,
  scope by issue number, explicit skip of the current branch/worktree.
* Risk — repeated notifications. Mitigation — marker comparison; "nothing new
  to report" when unchanged.
* Risk — cloud chats lack `gh` permissions. Mitigation — report and continue.
