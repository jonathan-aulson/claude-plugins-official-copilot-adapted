#!/usr/bin/env python3
"""Make the upstream Claude marketplace.json loadable by GitHub Copilot CLI.

Idempotent: safe to re-run after merging upstream (anthropics/claude-plugins-official).
Copilot CLI rejects the whole file if one entry has an unsupported `source`
(e.g. {"source": "command", ...}), so those entries are moved to
copilot-adaptation/excluded.json instead.

Usage: python3 copilot-adaptation/adapt_marketplace.py [--check]
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
EXCLUDED = ROOT / "copilot-adaptation" / "excluded.json"
SUPPORTED_SOURCE_TYPES = {"url", "git-subdir", "github", "git"}


def supported(source):
    if isinstance(source, str):
        return source.startswith("./")
    return isinstance(source, dict) and source.get("source") in SUPPORTED_SOURCE_TYPES


def main():
    check = "--check" in sys.argv
    data = json.loads(MARKETPLACE.read_text())
    kept, dropped = [], []
    for plugin in data["plugins"]:
        (kept if supported(plugin.get("source")) else dropped).append(plugin)

    if check:
        if dropped:
            print("Unsupported entries:", ", ".join(p["name"] for p in dropped))
            sys.exit(1)
        print(f"OK: {len(kept)} plugins, none unsupported")
        return

    data["plugins"] = kept
    MARKETPLACE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    previous = json.loads(EXCLUDED.read_text()) if EXCLUDED.exists() else []
    merged = {p["name"]: p for p in previous}
    merged.update({p["name"]: p for p in dropped})
    EXCLUDED.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False) + "\n")
    print(f"kept {len(kept)}, newly excluded {len(dropped)}: {[p['name'] for p in dropped]}")


if __name__ == "__main__":
    main()
