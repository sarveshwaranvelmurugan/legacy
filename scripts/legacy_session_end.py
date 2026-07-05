#!/usr/bin/env python3
"""Legacy auto-capture — Claude Code SessionEnd hook (cross-platform).
Consent gate first: no flag file, no action. Reads the hook JSON from stdin,
observes the session's workspace, and distills the transcript into workflow
memory. Works on macOS, Linux, and Windows."""
import sys
from pathlib import Path

FLAG = Path.home() / ".legacy" / "autocapture"
if not FLAG.exists():
    sys.exit(0)

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

try:
    from app import session_end
    session_end.main()
except Exception:
    pass  # a hook must never break the host session
sys.exit(0)
