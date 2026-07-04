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
    import subprocess
    cmd = mcp_configs()["claude"]
    try:
        out = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        return out.returncode == 0, cmd
    except Exception:
        return False, cmd
