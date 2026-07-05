"""Legacy — `legacy setup` and `legacy hook`.

setup: installs Legacy into the user's AI tools globally (Claude Code skill),
       so every new session in every project can reach memory. Paths are
       rendered for THIS machine's clone location — no hardcoded homes.
hook:  run inside any project to wire that project's Cursor rules + AGENTS.md.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = str(REPO_ROOT / "legacy")

# tokens used in the repo's integration templates
_TOKENS = ("/Users/sarveshwaran/hangover/legacy", "~/hangover/legacy")


def _render(template_path: Path) -> str:
    text = template_path.read_text()
    for t in _TOKENS:
        text = text.replace(t, CLI)
    return text


def setup_claude_skill() -> str:
    src = REPO_ROOT / "integrations" / "claude-code" / "SKILL.md"
    dst = Path.home() / ".claude" / "skills" / "legacy" / "SKILL.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(_render(src))
    return str(dst)


def hook_project(project: Path | None = None) -> list[str]:
    """Wire the CURRENT project so Cursor + any AGENTS.md-reading agent
    knows about Legacy."""
    project = (project or Path.cwd()).resolve()
    installed = []

    # Cursor project rule
    rule_src = REPO_ROOT / "integrations" / "cursor" / "legacy.mdc"
    rule_dst = project / ".cursor" / "rules" / "legacy.mdc"
    rule_dst.parent.mkdir(parents=True, exist_ok=True)
    rule_dst.write_text(_render(rule_src))
    installed.append(str(rule_dst))

    # AGENTS.md — append the Legacy section if it isn't there yet
    agents_src = REPO_ROOT / "integrations" / "any-agent" / "AGENTS.md"
    agents_dst = project / "AGENTS.md"
    section = _render(agents_src)
    if agents_dst.exists():
        existing = agents_dst.read_text()
        if "Legacy memory agent" not in existing:
            agents_dst.write_text(existing.rstrip() + "\n\n" + section)
            installed.append(str(agents_dst) + " (appended)")
        else:
            installed.append(str(agents_dst) + " (already wired)")
    else:
        agents_dst.write_text(section)
        installed.append(str(agents_dst))
    return installed


import sys as _sys

if _sys.platform == "win32":
    PYTHON = str(REPO_ROOT / ".venv" / "Scripts" / "python.exe")
else:
    PYTHON = str(REPO_ROOT / ".venv" / "bin" / "python")
BACKEND = str(REPO_ROOT / "backend")


def mcp_configs() -> dict:
    """Registration commands/configs for this machine's clone location."""
    claude_cmd = (f"claude mcp add -s user legacy -e PYTHONPATH={BACKEND} "
                  f"-- {PYTHON} -m app.mcp_server")
    cursor_json = {
        "mcpServers": {
            "legacy": {
                "command": PYTHON,
                "args": ["-m", "app.mcp_server"],
                "env": {"PYTHONPATH": BACKEND},
            }
        }
    }
    return {"claude": claude_cmd, "cursor": cursor_json}


def setup_mcp() -> tuple[bool, str]:
    """Try to register the MCP server with Claude Code; return (ok, command)."""
    import shutil
    import subprocess
    display = mcp_configs()["claude"]
    claude = (shutil.which("claude") or shutil.which("claude.cmd")
              or next((str(c) for c in (
                  Path.home() / ".claude" / "local" / "claude",
                  Path("/usr/local/bin/claude"),
                  Path("/opt/homebrew/bin/claude"),
              ) if c.exists()), None))
    if not claude:
        return False, display
    argv = [claude, "mcp", "add", "-s", "user", "legacy",
            "-e", f"PYTHONPATH={BACKEND}", "--", PYTHON, "-m", "app.mcp_server"]
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=30,
                             shell=False)
        ok = out.returncode == 0 or "already exists" in (out.stdout + out.stderr)
        return ok, display
    except Exception:
        return False, display


# ------------------------------------------------------------- autocapture
FLAG = Path.home() / ".legacy" / "autocapture"
HOOK_CMD = f'"{PYTHON}" "{REPO_ROOT / "scripts" / "legacy_session_end.py"}"'
_OLD_HOOK_CMD = str(REPO_ROOT / "scripts" / "legacy_session_end.sh")
SETTINGS = Path.home() / ".claude" / "settings.json"


def _hook_installed(settings: dict) -> bool:
    for entry in settings.get("hooks", {}).get("SessionEnd", []):
        for h in entry.get("hooks", []):
            if h.get("command") == HOOK_CMD:
                return True
    return False


def _remove_old_hook(settings: dict) -> None:
    """Drop the legacy zsh hook entry if present (pre-Windows-support installs)."""
    for entry in settings.get("hooks", {}).get("SessionEnd", []):
        entry["hooks"] = [h for h in entry.get("hooks", [])
                          if h.get("command") != _OLD_HOOK_CMD]
    if "hooks" in settings and "SessionEnd" in settings["hooks"]:
        settings["hooks"]["SessionEnd"] = [
            e for e in settings["hooks"]["SessionEnd"] if e.get("hooks")]


def install_autocapture_hook() -> bool:
    """Merge our SessionEnd hook into ~/.claude/settings.json (backup first).
    Returns True if newly installed, False if it was already there."""
    import json
    settings = {}
    if SETTINGS.exists():
        settings = json.loads(SETTINGS.read_text() or "{}")
        SETTINGS.with_suffix(".json.legacy-bak").write_text(json.dumps(settings, indent=2))
    _remove_old_hook(settings)
    if _hook_installed(settings):
        return False
    settings.setdefault("hooks", {}).setdefault("SessionEnd", []).append(
        {"hooks": [{"type": "command", "command": HOOK_CMD}]}
    )
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(settings, indent=2))
    return True


def autocapture(state: str | None = None) -> dict:
    """on: install hook (once) + set flag. off: clear flag (hook stays, no-ops).
    None: report status."""
    import json
    if state == "on":
        newly = install_autocapture_hook()
        FLAG.parent.mkdir(exist_ok=True)
        FLAG.touch()
        return {"enabled": True, "hook_newly_installed": newly}
    if state == "off":
        FLAG.unlink(missing_ok=True)
        return {"enabled": False}
    settings = {}
    if SETTINGS.exists():
        settings = json.loads(SETTINGS.read_text() or "{}")
    return {"enabled": FLAG.exists(), "hook_present": _hook_installed(settings)}
