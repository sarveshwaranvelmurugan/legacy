#!/bin/zsh
# Legacy auto-capture — Claude Code SessionEnd hook.
# Claude Code invokes this when a session ends, passing session JSON on stdin.
# Consent gate first: no flag file, no action, ~1ms.
[ -f "$HOME/.legacy/autocapture" ] || exit 0
CWD=$(/usr/bin/python3 -c "import sys,json;print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null)
[ -n "$CWD" ] && [ -d "$CWD" ] || exit 0
LEGACY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$CWD" 2>/dev/null || exit 0
"$LEGACY_ROOT/legacy" observe >/dev/null 2>&1 || true
exit 0
