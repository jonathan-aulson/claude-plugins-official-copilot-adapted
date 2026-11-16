#!/usr/bin/env bash
# Install a plugin, then audit it for Copilot CLI compatibility.
# Usage: install_and_audit.sh <plugin>@<marketplace>   (or any `copilot plugin install` spec)
set -uo pipefail
SPEC="${1:?usage: install_and_audit.sh <plugin>@<marketplace>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
copilot plugin install "$SPEC" || exit $?
NAME="${SPEC%%@*}"; NAME="${NAME##*/}"; NAME="${NAME%%:*}"
DIR="$(find "$HOME/.copilot/installed-plugins" -maxdepth 3 -type d -name "$NAME" | head -1)"
if [ -z "$DIR" ]; then echo "Installed, but could not locate $NAME under ~/.copilot/installed-plugins"; exit 0; fi
echo "Auditing $DIR"
python3 "$HERE/audit_plugin.py" "$DIR"
echo "Next: have Copilot apply the ADAPT/CHECK items (claude-plugin-adapter skill), then run /restart."
