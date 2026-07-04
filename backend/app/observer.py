"""Legacy — ambient workspace observer.

The agent's passive sense: when you open Legacy in a terminal, it looks at
where you are — git repo, branch, recent commits, uncommitted work — and
remembers it WITHOUT being told. Git history is verified evidence: nobody
accidentally fabricates a commit log.

Deduped via a small state file so revisiting the same repo doesn't spam the
graph: a workspace is re-observed only when HEAD moved or a day has passed.
"""
from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

from . import cme, cognee_client

_STATE = Path.home() / ".legacy" / "observer_state.json"


def _git(args: list[str], cwd: Path) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def _load_state() -> dict:
    if _STATE.exists():
        return json.loads(_STATE.read_text())
    return {}


def _save_state(state: dict) -> None:
    _STATE.parent.mkdir(exist_ok=True)
    _STATE.write_text(json.dumps(state, indent=2))


def look(cwd: Path | None = None) -> dict | None:
    """Observe the current workspace. Returns what was seen, or None if
    there is nothing new worth remembering."""
    cwd = cwd or Path.cwd()
    root = _git(["rev-parse", "--show-toplevel"], cwd)
    if not root:
        return None  # not a repo — nothing ambient to observe

    repo = Path(root).name
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    head = _git(["rev-parse", "--short", "HEAD"], cwd)
    commits_24h = _git(["log", "--since=24 hours ago", "--oneline"], cwd)
    dirty = _git(["status", "--porcelain"], cwd)
    today = date.today().isoformat()

    state = _load_state()
    prev = state.get(root, {})
    if prev.get("head") == head and prev.get("date") == today:
        return {"repo": repo, "branch": branch, "new": False,
                "summary": f"{repo} ({branch}) — already observed today, nothing new."}

    commit_lines = commits_24h.splitlines()
    observation = (
        f"Observed from the terminal on {today}: user shanks is actively working "
        f"in the git repository '{repo}' on branch '{branch}'."
    )
    if commit_lines:
        msgs = "; ".join(line.split(" ", 1)[1] for line in commit_lines[:5])
        observation += (
            f" {len(commit_lines)} commit(s) in the last 24 hours: {msgs}. "
            "This is verified evidence from git history."
        )
    if dirty:
        observation += f" {len(dirty.splitlines())} file(s) currently modified and uncommitted."

    nodes = cme.extract_nodes(observation, today)
    strings = [cme.format_node_for_cognee(n) for n in nodes]
    if strings:
        cognee_client.remember(strings)

    state[root] = {"head": head, "date": today}
    _save_state(state)
    return {
        "repo": repo,
        "branch": branch,
        "new": True,
        "nodes": nodes,
        "summary": f"{repo} ({branch}) — {len(commit_lines)} commit(s) today, "
                   f"{len(dirty.splitlines()) if dirty else 0} file(s) in progress "
                   f"→ {len(strings)} node(s) remembered.",
    }
