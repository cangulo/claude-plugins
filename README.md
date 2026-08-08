# claude-plugins

Personal [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) marketplace by [@cangulo](https://github.com/cangulo).

It hosts two plugins, each exposing its operations as auto-invocable **skills**:

| Plugin | Skills | Purpose |
| ------ | ------ | ------- |
| `wiki` | `init`, `update`, `validate` | Initialize, update, and validate a repository wiki |
| `adrs` | `init`, `validate`, `implement`, `update` | Spec-driven Architecture Decision Record workflow |

> **Status:** the marketplace and plugin manifests are in place. The `wiki` and
> `adrs` skills are delivered in follow-up phases — installing today registers
> the plugins but the skills are added incrementally.

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
│   └── marketplace.json          # lists both plugins
├── plugins/
│   ├── wiki/
│   │   └── .claude-plugin/plugin.json
│   └── adrs/
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
