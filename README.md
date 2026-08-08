# claude-plugins

Personal [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) marketplace by [@cangulo](https://github.com/cangulo).

It hosts two plugins, each exposing its operations as auto-invocable **skills**:

| Plugin | Skills | Purpose |
| ------ | ------ | ------- |
| `wiki` | `init`, `update`, `validate` | Initialize, update, and validate a repository wiki |
| `adrs` | `init`, `validate`, `implement`, `update` | Spec-driven Architecture Decision Record workflow |

## `wiki` — repository wiki, GitHub-wiki standard

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

## Install

```text
/plugin marketplace add cangulo/claude-plugins
/plugin install wiki@cangulo-plugins
/plugin install adrs@cangulo-plugins        # add --scope project to share via .claude/settings.json
```

Works in both Claude Desktop and the Claude Code CLI.

> The marketplace is named `cangulo-plugins` (Claude's validator reserves
> `claude-*` names), so installs use the `@cangulo-plugins` suffix. The repo is
> still `cangulo/claude-plugins`.

## Usage

Once a plugin is installed, invoke a skill explicitly with `/<plugin>:<skill>`,
or just describe your task and let Claude auto-invoke the matching skill:

```text
/wiki:init
/adrs:validate docs/adr/0007-x.md
/adrs:implement docs/adr/0007-x.md
```

## Layout

```text
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json              # lists both plugins
├── plugins/
│   ├── wiki/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── shared/
│   │   │   ├── wiki-conventions.md    # rules all 3 skills follow
│   │   │   └── publish-wiki.yml       # reference workflow: wiki/ -> .wiki.git
│   │   └── skills/
│   │       ├── init/SKILL.md
│   │       ├── update/SKILL.md
│   │       └── validate/
│   │           ├── SKILL.md
│   │           └── scripts/validate-wiki.py
│   └── adrs/                          # delivered in its own PR
│       └── .claude-plugin/plugin.json
├── README.md
└── LICENSE
```

## Development

While iterating on a plugin, run Claude Code with the local plugin dir so
`SKILL.md` edits take effect live, without reinstalling from the marketplace:

```text
claude --plugin-dir .
```

Validate a plugin manifest before committing:

```text
claude plugin validate ./plugins/adrs
```

## License

[MIT](./LICENSE)
