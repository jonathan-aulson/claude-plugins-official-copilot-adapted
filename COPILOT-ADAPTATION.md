# Copilot CLI adaptation of claude-plugins-official

This fork of `anthropics/claude-plugins-official` is adapted so GitHub Copilot CLI can register it as a marketplace.

```bash
copilot plugin marketplace add jonathan-aulson/claude-plugins-official-copilot-adapted
copilot plugin marketplace browse claude-plugins-official
```

## What was wrong

Copilot CLI validates the whole `.claude-plugin/marketplace.json` and rejects it if any entry is invalid:
`Invalid marketplace.json: plugins.302.source: Invalid input`. Entry 302 (`xcode`, Apple) uses
`"source": {"source": "command", ...}`, a source type Copilot does not support. The other 316 entries
(`./` paths, `url`, `git-subdir`) load fine.

## What changed

- `.claude-plugin/marketplace.json`: unsupported-source entries removed (no other edits).
- `copilot-adaptation/excluded.json`: the removed entries, kept for reference. `xcode` is macOS-only.
- `copilot-adaptation/adapt_marketplace.py`: idempotent script that re-applies the filter. After merging upstream, run `python3 copilot-adaptation/adapt_marketplace.py` and commit. `--check` fails if unsupported entries exist.

## Plugin-level adaptation

Marketplace entries load, but some plugins use Claude-only features (tool names, hooks, paths). In Copilot,
install them with the `claude-plugin-adapter` skill (user skill at `~/.copilot/skills/claude-plugin-adapter`), which
installs, audits, patches the installed copy and records the patch.
