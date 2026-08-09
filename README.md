# 🧩 claude-plugins

Personal [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) marketplace by [@cangulo](https://github.com/cangulo).

It hosts two plugins, each exposing its operations as auto-invocable **skills**:

| Plugin | Skills | Purpose | Status |
| ------ | ------ | ------- | ------ |
| `adrs` | `init`, `validate`, `implement`, `update` | Spec-driven Architecture Decision Record workflow | ✅ available |
| `wiki` | `init`, `update`, `validate` | Initialize, update, and validate a repository wiki | ✅ available |

## 📐 `adrs` — spec-driven ADR workflow

A four-skill workflow that treats an Architecture Decision Record as the
contract for a change. **One ADR is a trio of files** sharing a stem under
`docs/adr/` — `YYYYMMDD-title`, or the grouped `YYYYMMDD-<group>-<NN>-<title>`
when several ADRs share an iteration:

| File | Role |
| ---- | ---- |
| `<stem>-summary.md` | The **decision** — context, options, outcome, and Status. |
| `<stem>-plan.md` | The **plan** — the essential implementation (approach and steps). |
| `<stem>-followups.md` | The **follow-ups** — action items *outside* the essential implementation. |

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
python plugins/adrs/skills/validate/scripts/validate-adr.py docs/adr/20260808-use-postgres-summary.md
```

## 📖 `wiki` — repository wiki, GitHub-wiki standard

A three-skill workflow for authoring a repository wiki in a top-level `wiki/`
directory that renders natively as the repo's **GitHub wiki**. The `shared/`
folder is the single source of truth: `wiki-conventions.md` (the rules all three
skills follow) and `publish-wiki.yml` (a reference workflow that syncs `wiki/`
to `https://github.com/<owner>/<repo>.wiki.git`).

| Skill | What it does |
| ----- | ------------ |
| `/wiki:init` | Scaffold a `wiki/` directory (`Home.md` + `_Sidebar.md`) and optionally add the publish workflow. |
| `/wiki:update` | Add, edit, rename, or remove a page, keeping `_Sidebar.md` and internal links in sync. |
| `/wiki:validate` | Deterministically check the whole `wiki/` directory against the conventions via `scripts/validate-wiki.py`. CI-gate friendly. |

Conventions: a **flat** `wiki/` directory, hyphenated page filenames
(`Getting-Started.md` → "Getting Started"), one `# H1` per page, required
`Home.md` + `_Sidebar.md`, and `[[Page Title]]` wiki links. Run the validator
directly to gate CI:

```text
python plugins/wiki/skills/validate/scripts/validate-wiki.py wiki
```

## 📦 Install

```text
/plugin marketplace add cangulo/claude-plugins
/plugin install wiki@cangulo-plugins
/plugin install adrs@cangulo-plugins        # add --scope project to share via .claude/settings.json
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
/adrs:validate docs/adr/20260808-use-postgres-summary.md
/adrs:implement docs/adr/20260808-use-postgres
```

## 🗂️ Layout

```text
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json              # lists both plugins
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
│   └── wiki/
│       ├── .claude-plugin/plugin.json
│       ├── shared/
│       │   ├── wiki-conventions.md    # rules all 3 skills follow
│       │   └── publish-wiki.yml       # reference workflow: wiki/ -> .wiki.git
│       └── skills/
│           ├── init/SKILL.md
│           ├── update/SKILL.md
│           └── validate/
│               ├── SKILL.md
│               └── scripts/validate-wiki.py
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

## 📄 License

[MIT](./LICENSE)
