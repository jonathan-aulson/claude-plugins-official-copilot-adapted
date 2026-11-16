---
name: claude-plugin-adapter
description: Installs a plugin from the adapted claude-plugins-official marketplace (or any Claude Code plugin) into Copilot CLI and automatically develops whatever adaptation it needs - audits for Claude-only tools, paths, hooks, agent tool names and MCP/LSP layout, patches the installed copy, records the patch for re-apply after updates, and verifies it loads. Use whenever the user asks to install, add, enable or update a plugin from claude-plugins-official, or a Claude Code plugin/skill that may not run natively in Copilot CLI.
---

# Claude plugin adapter

Goal: when the user says "install X" (from `claude-plugins-official` or any Claude Code plugin), end with X working in Copilot CLI, without the user asking for each fix.

## Process

1. **Install + audit** (do not skip the audit):
   `bash ~/.copilot/skills/claude-plugin-adapter/scripts/install_and_audit.sh <plugin>@claude-plugins-official`
   The installed copy lives under `~/.copilot/installed-plugins/`. If install fails because the plugin is in the fork's `copilot-adaptation/excluded.json`, tell the user why (unsupported source type) and stop.
2. **Read the findings** (`BLOCKER`, `ADAPT`, `CHECK`, `INFO`). Also skim the plugin's README and every SKILL.md, agent and command; the audit is pattern-based and will miss semantic issues.
3. **Develop the adaptation** in the installed copy, using `references/adaptation-rules.md`. Rules of thumb:
   - Keep behaviour-shaping text verbatim; only translate tool and path references.
   - Where a Claude capability has no Copilot equivalent (e.g. hooks that do not fire, `allowed-tools`, plan mode), degrade gracefully and add an `<!-- adaptation-notes: ... -->` comment at the top of the file.
   - Never weaken a safety instruction or permission guard to make something "work".
   - MCP servers: surface the server definition and have the user confirm before registering (`copilot mcp add`); it can run code and read data. Never put secrets in files.
4. **Record the patch** so it survives `copilot plugin update`:
   `mkdir -p ~/.copilot/plugin-adaptations/<plugin> && diff -ruN <pristine> <adapted> > ~/.copilot/plugin-adaptations/<plugin>/adapt.patch` (take the pristine copy from a fresh clone or `git stash`-style backup made BEFORE editing: copy the installed dir to `~/.copilot/plugin-adaptations/<plugin>/pristine/` first). Add `NOTES.md` with what changed and what could not be adapted.
5. **Verify**: re-run `audit_plugin.py` (no BLOCKER, remaining ADAPT items explained), then tell the user to `/restart` and check `/env` (skills, agents, MCP, hooks listed). If you can, invoke one adapted skill once as a smoke test.
6. **Report** in under 120 words: what was installed, what was adapted, what could not be, and anything needing the user's decision.

After `copilot plugin update <plugin>`, re-apply `adapt.patch` (`patch -p0 < ...` from the plugin dir) and fix rejects.

## Known limits (be honest with the user)
- There is no install-time hook in Copilot CLI. The automation is this skill, triggered when installing through Copilot. A bare `copilot plugin install` in a terminal is not adapted; run `install_and_audit.sh` instead.
- Hooks: Copilot CLI v1.0.55 notes say plugin hooks may not execute at runtime. Verify before promising behaviour.
- Plugins whose source type is `command` (e.g. Xcode) are excluded from the marketplace.
