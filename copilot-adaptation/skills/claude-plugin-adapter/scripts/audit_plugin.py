#!/usr/bin/env python3
"""Audit a Claude Code plugin directory for Copilot CLI compatibility.

Usage: audit_plugin.py <plugin-dir> [--json]
Exit code 0 = no BLOCKER findings, 1 = at least one BLOCKER.
"""
import json
import pathlib
import re
import sys

TEXT_SUFFIXES = {".md", ".json", ".sh", ".py", ".js", ".ts", ".yaml", ".yml", ".txt"}
SKIP_DIRS = {".git", "node_modules"}

# Mirrors the superpowers-copilot-cli UPSTREAM.md adaptation table.
PATTERNS = [
    (r"\bSkill tool\b|via the Skill tool", "ADAPT", "Claude `Skill` tool reference",
     "Replace with 'reference the X skill - Copilot surfaces it from its description'."),
    (r"\bTodoWrite\b|\bTaskCreate\b|\bTaskUpdate\b|\bTaskList\b", "ADAPT", "Claude todo tool names",
     "Use Copilot's session `sql` todos tables (todos / todo_deps)."),
    (r"\bEnterPlanMode\b|\bExitPlanMode\b", "ADAPT", "Claude plan-mode tools",
     "Write the plan to a file and pause for user approval."),
    (r"\bAskUserQuestion\b", "ADAPT", "Claude AskUserQuestion tool", "Use Copilot's `ask_user` tool."),
    (r"subagent_type\s*[=:]", "ADAPT", "Claude subagent_type usage",
     "Map to Copilot `task` agent_type (explore, task, general-purpose, code-review, ...)."),
    (r"\$\{?CLAUDE_PLUGIN_ROOT\}?", "CHECK", "CLAUDE_PLUGIN_ROOT variable",
     "Copilot documents PLUGIN_ROOT (with CLAUDE_/COPILOT_PLUGIN_DATA aliases); verify ROOT expansion or switch to ${PLUGIN_ROOT}."),
    (r"~/\.claude/|\.claude/(settings|rules|commands|agents)", "ADAPT", "~/.claude paths",
     "Use ~/.copilot/ or .github/ equivalents."),
    (r"\bCLAUDE\.md\b", "ADAPT", "CLAUDE.md reference",
     "Copilot also reads CLAUDE.md, but prefer AGENTS.md or .github/copilot-instructions.md."),
    (r"allowed-tools\s*:", "CHECK", "Claude `allowed-tools` frontmatter",
     "Tool names differ in Copilot (view/edit/create/bash/grep/glob); translate or drop."),
]
CLAUDE_TOOL_NAMES = {"Read", "Write", "Edit", "MultiEdit", "Bash", "Grep", "Glob", "WebFetch", "WebSearch", "Task", "NotebookEdit"}
HOOK_EVENTS_CLAUDE = {"PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart", "SessionEnd", "Stop", "SubagentStop", "PreCompact", "Notification"}


def read(path):
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    return match.group(1) if match else ""


def audit(root):
    findings = []

    def add(sev, where, msg, fix):
        findings.append({"severity": sev, "where": str(where.relative_to(root)) if where != root else ".", "finding": msg, "adaptation": fix})

    manifests = [root / ".claude-plugin" / "plugin.json", root / "plugin.json", root / ".plugin" / "plugin.json"]
    manifest = next((m for m in manifests if m.exists()), None)
    if manifest is None:
        add("BLOCKER", root, "No plugin.json (.claude-plugin/plugin.json, plugin.json or .plugin/plugin.json)",
            "Create a minimal manifest with name, version, description.")
    else:
        try:
            data = json.loads(read(manifest))
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", data.get("name", "")):
                add("BLOCKER", manifest, "Plugin name is not kebab-case", "Rename to lowercase letters, digits and hyphens.")
        except json.JSONDecodeError as exc:
            add("BLOCKER", manifest, f"Invalid JSON: {exc}", "Fix the manifest syntax.")

    for sub in ("commands", "agents", "hooks", "skills"):
        if (root / sub).is_dir():
            add("INFO", root / sub, f"Has {sub}/ component", "Verify it loads with `/env` after install.")
    if (root / ".mcp.json").exists() and not (root / "mcp.json").exists():
        add("CHECK", root / ".mcp.json", "MCP config is `.mcp.json`", "If servers do not appear in `/mcp`, register with `copilot mcp add` or mirror as mcp.json.")
    if (root / ".lsp.json").exists():
        add("CHECK", root / ".lsp.json", "LSP config present", "Check with `copilot lsp`; may need com.github.copilot/lsp.json layout.")

    for hooks_file in list(root.glob("hooks/*.json")) + list(root.glob("hooks.json")):
        used = [e for e in HOOK_EVENTS_CLAUDE if f'"{e}"' in read(hooks_file)]
        if used:
            add("CHECK", hooks_file, f"Claude hook event names: {', '.join(sorted(used))}",
                "Confirm Copilot's event names and that hooks execute at runtime (noted as not firing in v1.0.55).")

    for agent in root.glob("agents/*.md"):
        fm = frontmatter(read(agent))
        match = re.search(r"^tools\s*:\s*(.+)$", fm, re.M)
        if match:
            names = {t.strip().strip("[]\"'") for t in match.group(1).split(",")}
            claude = sorted(names & CLAUDE_TOOL_NAMES)
            if claude:
                add("ADAPT", agent, f"Agent tools use Claude names: {', '.join(claude)}", "Map to Copilot tool names (view, edit, create, bash, grep, glob, web_fetch).")
        if re.search(r"^model\s*:\s*(sonnet|opus|haiku|inherit)\b", fm, re.M):
            add("ADAPT", agent, "Agent pins a Claude model alias", "Remove or map to an available Copilot model.")

    for skill in root.glob("skills/*/SKILL.md"):
        fm = frontmatter(read(skill))
        if "name:" not in fm or "description:" not in fm:
            add("BLOCKER", skill, "SKILL.md missing name/description frontmatter", "Add both fields.")

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES or SKIP_DIRS & set(path.parts):
            continue
        text = read(path)
        for regex, sev, msg, fix in PATTERNS:
            if re.search(regex, text):
                add(sev, path, msg, fix)
    return findings


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    root = pathlib.Path(args[0]).expanduser().resolve()
    findings = audit(root)
    if "--json" in sys.argv:
        print(json.dumps(findings, indent=2))
    else:
        order = {"BLOCKER": 0, "ADAPT": 1, "CHECK": 2, "INFO": 3}
        for f in sorted(findings, key=lambda f: order[f["severity"]]):
            print(f"[{f['severity']}] {f['where']}: {f['finding']}\n    -> {f['adaptation']}")
        print(f"\n{len(findings)} findings in {root}")
    sys.exit(1 if any(f["severity"] == "BLOCKER" for f in findings) else 0)


if __name__ == "__main__":
    main()
