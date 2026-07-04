#!/bin/zsh
# Legacy auto-capture — Claude Code SessionEnd hook.
# Consent gate first: no flag file, no action, ~1ms. When on: observes the
# workspace git state AND distills the session transcript into workflow
# memory (commands, rituals, conventions — never code or secrets).
[ -f "$HOME/.legacy/autocapture" ] || exit 0
LEGACY_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$LEGACY_ROOT/backend"
"$LEGACY_ROOT/.venv/bin/python" -m app.session_end >/dev/null 2>&1 || true
exit 0
