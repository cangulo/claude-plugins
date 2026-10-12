# 🧩 claude-plugins

Personal [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) marketplace by [@cangulo](https://github.com/cangulo).

It hosts three plugins, each exposing its operations as auto-invocable **skills**:

| Plugin | Skills | Purpose | Status |
| ------ | ------ | ------- | ------ |
| `adrs` | `init`, `validate`, `implement`, `update` | Spec-driven Architecture Decision Record workflow | ✅ available |
| `wiki` | `init`, `update`, `validate` | Initialize, update, and validate a repository wiki | 🚧 coming next |
| `workflow` | `recap`, `close-out` | Wrap up Governor/Implementator chats on GitHub issues | ✅ available |

## 📐 `adrs` — spec-driven ADR workflow

A four-skill workflow that treats an Architecture Decision Record as the
contract for a change. **One ADR is a trio of files** sharing a stem under
`docs/adr/` — `YYYYMMDD-title`, or the grouped `YYYYMMDD-<group>-<NN>-<title>`
when several ADRs share an iteration:

| File | Role |
| ---- | ---- |
| `<stem>-0-summary.md` | The **decision** — context, options, outcome, and Status. |
| `<stem>-1-plan.md` | The **plan** — the essential implementation (approach and steps). |
| `<stem>-2-followups.md` | The **follow-ups** — action items *outside* the essential implementation. |

The `shared/` folder is the single source of truth: `adr-summary-template.md`,
`adr-plan-template.md`, `adr-followups-template.md` (what `init` scaffolds from)
and `adr-schema.md` (what `validate` checks against).

| Skill | What it does |
| ----- | ------------ |
| `/adrs:init` | Scaffold a new ADR trio, Status `Proposed`. **Spec only — writes no implementation code.** |
| `/adrs:validate <path>` | Deterministically check the whole trio against the schema via `scripts/validate-adr.py`. Pass any trio file or the stem. CI-gate friendly. |
| `/adrs:implement <path>` | The agentic step: build the plan (the essential implementation) for an accepted ADR. Follow-ups are tracked, not built. |
| `/adrs:update <path>` | Transition Status, supersede, revise the plan, or triage follow-up items, keeping the trio schema-valid. |

The **summary** carries the ADR Status (`Proposed`, `Accepted`, `Rejected`,
`Deprecated`, `Superseded`) plus front matter including `tags`,
`continuation_of`, and `group`. The validator resolves `continuation_of` and
`Superseded by [...]` links to make sure the referenced ADRs exist.

The **follow-ups** file tracks action items *outside* the essential
implementation (which the plan covers) — bugs, gaps, improvements, and
nice-to-haves that `implement` records but does not build. It opens with an
`Overview` table — `Group | ID | Title | Source | Status` — then a section per
group (`Bugs`, `Gaps`, `Improvements`, `Nice-to-have`) where each item is a
`### <ID> — <Title>` entry with `**Description:**`, `**Source:**`, `**Status:**`,
and an optional `**Status reason:**`. IDs are per-group (`B1`, `G2`, `I1`, `N1`);
`Source` is `human` / `review` / `agent`; item `Status` is `accepted` /
`out-of-the-scope`. Every Overview row has a matching detail entry, and their
Source/Status agree.

Files are length-capped to stay reviewable: **summary ≤ 350**, **follow-ups ≤ 350**,
**plan ≤ 600** lines (the plan captures the approach and where changes land, not
a full code preview). Run the validator directly to gate CI:

```text
python plugins/adrs/skills/validate/scripts/validate-adr.py docs/adr/20260808-use-postgres-0-summary.md
```

## 🧾 `workflow` — Governor/Implementator chat wrap-up

Skills for the Governor/Implementator chat workflow, where each Implementator
chat works on one GitHub issue and reports to a Governor chat (`🏷️<topic>: …`).
They work in local (desktop app) and cloud (claude.ai/code) chats.

`shared/wrap-up.md` is the single source of truth for the wrap-up every skill
runs: identify the issue (argument → branch `<N>-<type>-<slug>` → chat title),
work done, PRs, merged-only cleanup of this issue's branches/worktrees, open
questions and pending actions, finding the Governor, and the output rules.

| Skill | What it does |
| ----- | ------------ |
| `/workflow:recap [ISSUE]` | Wrap-up of this chat's work. Read-only apart from the cleanup and, on new progress, an issue comment plus a `SendMessage` to the Governor (local) or a "say sync" hint (cloud). Never edits the issue body. Runs only when typed. |
| `/workflow:close-out [ISSUE]` | Same wrap-up; if anything is pending it stops and lists it. Otherwise it posts `#<N> closed: <title>`, makes sure the issue is closed, sets its Project Status to Done, notifies the Governor, archives the chat (local) and removes its worktree last. Runs only when typed. |

Recap detects new progress through a hidden `<!-- workflow:recap … -->` marker
line in its last issue comment; close-out's closing comment carries it too. The
design is in
[docs/adr/20261012-workflow-01-shared-wrap-up](./docs/adr/20261012-workflow-01-shared-wrap-up-0-summary.md)
and [docs/adr/20261012-workflow-02-close-out](./docs/adr/20261012-workflow-02-close-out-0-summary.md).

## 📦 Install

```text
/plugin marketplace add cangulo/claude-plugins
/plugin install wiki@cangulo-plugins
/plugin install adrs@cangulo-plugins        # add --scope project to share via .claude/settings.json
/plugin install workflow@cangulo-plugins
```

Works in both Claude Desktop and the Claude Code CLI.

> The marketplace is named `cangulo-plugins` (Claude's validator reserves
> `claude-*` names), so installs use the `@cangulo-plugins` suffix. The repo is
> still `cangulo/claude-plugins`.

## ▶️ Usage

Once a plugin is installed, invoke a skill explicitly with `/<plugin>:<skill>`,
or just describe your task and let Claude auto-invoke the matching skill:

```text
/wiki:init
/adrs:validate docs/adr/20260808-use-postgres-0-summary.md
/adrs:implement docs/adr/20260808-use-postgres
/workflow:recap 8
/workflow:close-out 9
```

## 🗂️ Layout

```text
claude-plugins/
├── .github/workflows/validate.yml    # CI: validates marketplace, plugins and ADRs
├── .claude-plugin/
│   └── marketplace.json              # lists the plugins
├── plugins/
│   ├── adrs/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── shared/
│   │   │   ├── adr-summary-template.md   # decision skeleton init scaffolds from
│   │   │   ├── adr-plan-template.md      # implementation-plan skeleton
│   │   │   ├── adr-followups-template.md # follow-up action-items skeleton
│   │   │   └── adr-schema.md             # trio contract: sections, Status, follow-up vocab
│   │   └── skills/
│   │       ├── init/SKILL.md
│   │       ├── validate/
│   │       │   ├── SKILL.md
│   │       │   └── scripts/validate-adr.py
│   │       ├── implement/SKILL.md
│   │       └── update/SKILL.md
│   ├── wiki/                          # coming in the next phase
│   │   └── .claude-plugin/plugin.json
│   └── workflow/
│       ├── .claude-plugin/plugin.json
│       ├── shared/wrap-up.md          # shared wrap-up procedure
│       └── skills/
│           ├── recap/SKILL.md
│           └── close-out/SKILL.md
├── docs/adr/                          # ADRs for this repo
├── README.md
└── LICENSE
```

## 🛠️ Development

While iterating on a plugin, run Claude Code with the local plugin dir so
`SKILL.md` edits take effect live, without reinstalling from the marketplace:

```text
claude --plugin-dir .
```

Validate a plugin manifest before committing:

```text
claude plugin validate ./plugins/adrs
```

### ✅ CI

[`.github/workflows/validate.yml`](./.github/workflows/validate.yml) runs on
every PR to `main` and every push to `main`. It fails the check when any of
these is invalid:

- the marketplace: `claude plugin validate --strict .`
- each plugin under `plugins/*/`: `claude plugin validate --strict ./plugins/<name>`
- each ADR trio under `docs/adr/`: `validate-adr.py <stem>-0-summary.md`

`claude plugin validate` runs offline, so the workflow needs no secrets.

## 📄 License

[MIT](./LICENSE)
