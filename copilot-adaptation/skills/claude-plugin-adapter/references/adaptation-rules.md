# Adaptation rules (Claude Code -> Copilot CLI)

Derived from the working port at `~/.copilot/installed-plugins/_direct/superpowers-copilot-cli/UPSTREAM.md`.

| Claude Code | Copilot CLI |
|---|---|
| "use the `Skill` tool to invoke X" | "reference the X skill" (surfaced by its description); in a session the `skill` tool loads it |
| `TodoWrite`, `TaskCreate/Update/List` | session `sql` tool with `todos` / `todo_deps` tables |
| `EnterPlanMode` / `ExitPlanMode` | write the plan to a file, pause, ask the user to approve (`ask_user`) |
| `AskUserQuestion` | `ask_user` (structured form) |
| `subagent_type=Explore/Plan/general-purpose` | `task` tool: `agent_type` explore / general-purpose / task / code-review / rubber-duck |
| Agent `tools: Read, Edit, Bash, Grep, Glob, WebFetch` | `view`, `edit`/`create`, `bash`, `grep`, `glob`, `web_fetch` |
| Agent `model: sonnet/opus/haiku/inherit` | remove, or choose an available model |
| `${CLAUDE_PLUGIN_ROOT}` | `${PLUGIN_ROOT}` (verify expansion); `CLAUDE_PLUGIN_DATA` is an accepted alias |
| `~/.claude/`, `.claude/` | `~/.copilot/`, `.github/` |
| `CLAUDE.md` | `AGENTS.md` or `.github/copilot-instructions.md` (CLAUDE.md is also read) |
| `.claude/settings.json` hooks | plugin `hooks/hooks.json` (check runtime support) |
| `.mcp.json` | `copilot mcp add` / Agent Plugins `mcp.json` with `$schema`; `${PLUGIN_ROOT}` expands only for stdio servers |
| slash `commands/*.md` | usually load as-is for legacy plugins; otherwise convert to a skill |
| "Claude Code" / "Claude" as the runtime | "Copilot CLI" / "Copilot" |
