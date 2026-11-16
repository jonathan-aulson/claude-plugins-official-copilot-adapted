# Claude plugins for GitHub Copilot CLI (Allata adaptation)

This is a fork of [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) made usable from **GitHub Copilot CLI**. It gives you two things:

1. **A Copilot-loadable marketplace** - the upstream `marketplace.json` with the one entry Copilot rejects removed (316 of 317 plugins).
2. **The `claude-plugin-adapter` skill** - installs a Claude Code plugin into Copilot, audits it for Claude-only features, patches the installed copy and records the patch.

The upstream README follows the divider at the bottom. Nothing under `plugins/` or `external_plugins/` is modified.

## Quick start

```bash
# 1. Register the marketplace
copilot plugin marketplace add jonathan-aulson/claude-plugins-official-copilot-adapted
copilot plugin marketplace browse claude-plugins-official

# 2. Get the adapter skill (clone, then install it as a user skill)
git clone https://github.com/jonathan-aulson/claude-plugins-official-copilot-adapted.git
./claude-plugins-official-copilot-adapted/copilot-adaptation/install-skill.sh

# 3. In Copilot CLI, just ask:
#    "install the feature-dev plugin from claude-plugins-official"
```

Plugins install as `<plugin>@claude-plugins-official`. Restart Copilot CLI after installing and check `/env`.

## Why the fork exists

Copilot CLI validates the whole `.claude-plugin/marketplace.json` and rejects it if any entry is invalid:
`Invalid marketplace.json: plugins.302.source: Invalid input`. Entry 302, `xcode` (Apple, macOS-only), uses a
`"source": {"source": "command", ...}` source that Copilot does not support. All other entries (`./` paths, `url`,
`git-subdir`) load fine.

## Repository layout (additions)

| Path | Purpose |
|---|---|
| `.claude-plugin/marketplace.json` | Upstream marketplace, minus unsupported-source entries |
| `copilot-adaptation/adapt_marketplace.py` | Idempotent filter that re-applies the exclusion; `--check` fails if unsupported entries exist |
| `copilot-adaptation/excluded.json` | Entries removed by the filter (currently `xcode`) |
| `copilot-adaptation/skills/claude-plugin-adapter/` | The skill: `SKILL.md`, `references/adaptation-rules.md`, `scripts/audit_plugin.py`, `scripts/install_and_audit.sh` |
| `copilot-adaptation/install-skill.sh` | Copies the skill to `~/.copilot/skills/` |

## How the adapter skill works

When you ask Copilot to install a plugin from this marketplace (or any Claude Code plugin):

1. **Install + audit** - `copilot plugin install`, then `audit_plugin.py` scans the installed copy and reports `BLOCKER`, `ADAPT`, `CHECK` and `INFO` findings.
2. **Adapt** - Copilot patches the installed copy using `references/adaptation-rules.md` (e.g. `AskUserQuestion` -> `ask_user`, `TodoWrite` -> `sql` todos, `~/.claude` -> `~/.copilot`, Claude tool names in agents -> Copilot tool names).
3. **Record** - the pristine copy, patch and notes go to `~/.copilot/plugin-adaptations/<plugin>/` so it can be re-applied after `copilot plugin update`.
4. **Verify** - re-audit, restart, check `/env`, smoke-test one skill.

You can run the audit by hand: `python3 ~/.copilot/skills/claude-plugin-adapter/scripts/audit_plugin.py <plugin-dir>`.

### Limits

- Copilot CLI has **no install-time hook**. Adaptation happens when you install *through a Copilot session*. A bare `copilot plugin install` in a terminal is not adapted; use `scripts/install_and_audit.sh <plugin>@claude-plugins-official` (installs and audits) and then ask Copilot to apply the fixes.
- The audit is pattern-based; the skill also has Copilot read the plugin's content for semantic issues.
- Hooks may not execute at runtime in some Copilot CLI versions (observed in v1.0.55). Verify before relying on them.
- MCP servers bundled in plugins can run code: review them before registering.
- Plugins with unsupported source types (`xcode`) are excluded.
- The adaptation rules are derived from the superpowers Copilot port and are best-effort, not a guarantee that every plugin works.

## Keeping up with upstream

```bash
git remote add upstream https://github.com/anthropics/claude-plugins-official.git   # once
git fetch upstream && git merge upstream/main
python3 copilot-adaptation/adapt_marketplace.py     # re-apply the filter
python3 copilot-adaptation/adapt_marketplace.py --check
git commit -am "Sync upstream and re-adapt" && git push
```

Expect a merge conflict in `marketplace.json` and the top of this README; resolve by taking upstream's file and re-running the script (README: keep this section on top).

## Contributing

Improve the audit patterns or adaptation rules in `copilot-adaptation/skills/claude-plugin-adapter/`, then re-run `install-skill.sh`. Report plugins that still fail after adaptation as issues on this fork.

---

# Upstream README (anthropics/claude-plugins-official)


Anthropic's own plugins for Claude, and the `claude-plugins-official` marketplace for Claude Code.

> **Submitting a plugin?** Submit it at **[claude.ai/directory/manage](https://claude.ai/directory/manage)**. Plugins accepted there are served across Claude products. Pull requests to this repository are not monitored.

## What is changing

- **All plugins are now submitted at [claude.ai/directory/manage](https://claude.ai/directory/manage)**, and are served across Claude products from there.
- **`.claude-plugin/marketplace.json` is being phased out for third-party plugins.** It will be reduced over time to Anthropic's own plugins.
- **This repository is the home of Anthropic's own plugins.** Its checks cover the plugin folders here, not the plugins hosted in other repositories.

> **⚠️ Important:** Make sure you trust a plugin before installing, updating, or using it. Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended or that they won't change. See each plugin's homepage for more information.

## Structure

- **`/plugins`** - Internal plugins developed and maintained by Anthropic
- **`/external_plugins`** - Third-party plugins added before submissions moved to [claude.ai/directory/manage](https://claude.ai/directory/manage), and Anthropic's channel plugins (Discord, fakechat, iMessage and Telegram)

## Installation

Plugins can be installed directly from this marketplace via Claude Code's plugin system.

To install, run `/plugin install {plugin-name}@claude-plugins-official`

or browse for the plugin in `/plugin > Discover`

## Contributing

### Third-party plugins

Submit and manage your plugin at [claude.ai/directory/manage](https://claude.ai/directory/manage). Do not open a pull request here: pull requests are not monitored, and `marketplace.json` is being reduced to Anthropic's own plugins.

### Anthropic plugins

Plugins in `/plugins` are developed by Anthropic team members. See `/plugins/example-plugin` for a reference implementation. Every folder there is checked on each pull request, whether or not `marketplace.json` lists it.

## Plugin Structure

Each plugin follows a standard structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── commands/            # Slash commands (optional)
├── agents/              # Agent definitions (optional)
├── skills/              # Skill definitions (optional)
└── README.md            # Documentation
```

## Plugin names are immutable

The `name` field in a marketplace entry is an **immutable slug**. Once a plugin has been published, its `name` must not change — users have it installed under that slug, and renaming it breaks their install with a `plugin-not-found` error.

- To change how a plugin is labeled in the UI, set or update `displayName` instead.
- If a rename is genuinely unavoidable, add an entry to the top-level `renames` map in `.claude-plugin/marketplace.json` so existing installs auto-migrate:

```json
"renames": {
  "old-name": "new-name"
}
```

The Claude Code plugin loader reads this map and transparently rewrites the old slug to the new one on the user's next sync.

## Skill-bundle plugins

When a plugin's source repository ships skills (`SKILL.md` files) without a `.claude-plugin/plugin.json` manifest, the marketplace entry can declare the skills directly using `strict: false` and an explicit `skills` array.

```json
{
  "name": "example-bundle",
  "description": "Brief description of the bundled skills.",
  "author": { "name": "Author Name" },
  "category": "development",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/example-org/sdk.git",
    "path": "packages/agent-skills",
    "ref": "main",
    "sha": "<commit sha>"
  },
  "strict": false,
  "skills": [
    "./skill-a",
    "./skill-b",
    "./skill-c"
  ],
  "homepage": "https://github.com/example-org/sdk"
}
```

Each path in `skills` is relative to `source.path` and points at a directory containing a `SKILL.md`. Paths can reach deeper than a single level — for example, `["./libA/skill-1", "./libB/skill-2"]` exposes a curated subset across multiple library subdirectories. Each skill is registered as `<plugin-name>:<skill-name>` in Claude Code.

For the underlying schema, see [Strict mode](https://code.claude.com/docs/en/plugin-marketplaces) in the marketplace documentation.

## License

Please see each linked plugin for the relevant LICENSE file.

## Documentation

For more information on developing Claude Code plugins, see the [official documentation](https://code.claude.com/docs/en/plugins).
