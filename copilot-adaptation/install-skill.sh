#!/usr/bin/env bash
# Install the claude-plugin-adapter skill into ~/.copilot/skills (re-run to update).
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/claude-plugin-adapter"
DEST="$HOME/.copilot/skills/claude-plugin-adapter"
mkdir -p "$HOME/.copilot/skills"
rm -rf "$DEST"; cp -r "$SRC" "$DEST"; chmod +x "$DEST"/scripts/*
echo "Installed to $DEST. Restart Copilot CLI (or /skills reload) to pick it up."
