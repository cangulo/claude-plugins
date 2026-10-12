# 📁 ADR folder resolution

Every `adrs:*` skill reads and writes ADRs in one folder, called `<adr-folder>`
in the other docs. It is not fixed: resolve it at the start of every run, in
this order. The first source that gives a folder wins.

1. **Explicit argument.** A path the user passed (a folder, a trio file or a
   stem) always wins. Its folder is `<adr-folder>`.
2. **Repo CLAUDE.md.** `./CLAUDE.md`, then `./.claude/CLAUDE.md`. Look for a
   rule naming where ADRs live, e.g. `ADRs live in wiki/*.md` or
   `ADR folder: wiki/`.
3. **User CLAUDE.md.** `~/.claude/CLAUDE.md`, same kind of rule. A repo rule
   (step 2) overrides it.
4. **Ask the user.** If no source defines it, ask which folder to use,
   proposing:
   - `docs/adr/` — the classic location;
   - `wiki/` (flat `wiki/*.md`) — useful with the cangulo `wiki` plugin
     installed, which syncs `wiki/` with the repo's GitHub wiki.

   Then **offer** to add a one-line rule to the repo's CLAUDE.md (e.g.
   `- ADRs live in wiki/*.md (adrs plugin folder).`) so later runs don't ask.
   Write it only if the user agrees; create `./CLAUDE.md` if none exists.

The folder is **flat**: the trio sits directly in it, e.g.
`wiki/<stem>-0-summary.md`, `wiki/<stem>-1-plan.md`, `wiki/<stem>-2-followups.md`.

**Always print it** before doing anything else, with its source:

```
📁 ADR folder: wiki/ (from repo CLAUDE.md)
```

Sources: `argument`, `repo CLAUDE.md`, `user CLAUDE.md`, `user answer`.
