"""Legacy — deep project learning (`legacy learn`).

Explicitly invoked in a project directory, it reads METADATA ONLY — README,
manifests, directory tree, commit messages; never source file bodies — and
distills it into PROJECT knowledge nodes: purpose, stack, architecture,
features, patterns. This is what lets a future session ask "build a new app
following the patterns of app A and app B" and get a real answer.
"""
from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

import anthropic

from . import cognee_client, config

_claude = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

MANIFESTS = [
    "package.json", "requirements.txt", "pyproject.toml", "go.mod",
    "Cargo.toml", "composer.json", "pom.xml", "build.gradle", "Gemfile",
    "docker-compose.yml", "Dockerfile",
]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build",
             "__pycache__", ".next", "target", ".idea", ".vscode"}


def _tree(root: Path, depth: int = 2) -> str:
    lines: list[str] = []

    def walk(d: Path, level: int) -> None:
        if level > depth:
            return
        try:
            children = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name))
        except PermissionError:
            return
        for c in children:
            if c.name.startswith(".") or c.name in SKIP_DIRS:
                continue
            lines.append("  " * level + c.name + ("/" if c.is_dir() else ""))
            if c.is_dir():
                walk(c, level + 1)

    walk(root, 0)
    return "\n".join(lines[:120])


def gather(path: Path) -> dict:
    """Collect project metadata. No source code bodies leave the machine."""
    readme = ""
    for name in ("README.md", "README.rst", "README.txt", "readme.md"):
        f = path / name
        if f.exists():
            readme = f.read_text(errors="ignore")[:4000]
            break
    manifests = {}
    for name in MANIFESTS:
        f = path / name
        if f.exists():
            manifests[name] = f.read_text(errors="ignore")[:2000]
    try:
        log = subprocess.run(
            ["git", "log", "--oneline", "-30"], cwd=path,
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except Exception:
        log = ""
    return {
        "name": path.resolve().name,
        "readme": readme,
        "manifests": manifests,
        "tree": _tree(path),
        "commits": log,
    }


def learn(path: Path | None = None) -> dict:
    """Distill a project's metadata into PROJECT knowledge nodes and remember."""
    path = path or Path.cwd()
    meta = gather(path)

    prompt = (
        f"Project directory name: {meta['name']}\n\n"
        f"README (truncated):\n{meta['readme'] or '(none)'}\n\n"
        f"Manifests:\n{json.dumps(meta['manifests'], indent=1)[:3000]}\n\n"
        f"Directory tree:\n{meta['tree']}\n\n"
        f"Recent commits:\n{meta['commits'] or '(none)'}"
    )
    response = _claude.messages.create(
        model=config.CME_MODEL,
        max_tokens=1800,
        system=(
            "You are the project-knowledge distiller for Legacy, a memory agent. "
            "From the metadata, produce dense factual knowledge about this project "
            "so a future coding agent could imitate its patterns. Never invent — "
            "if something is not evident from the metadata, omit it."
        ),
        output_config={"format": {"type": "json_schema", "schema": {
            "type": "object",
            "properties": {
                "purpose": {"type": "string"},
                "stack": {"type": "string"},
                "architecture": {"type": "string"},
                "features": {"type": "string"},
                "patterns": {"type": "string"},
            },
            "required": ["purpose", "stack", "architecture", "features", "patterns"],
            "additionalProperties": False,
        }}},
        messages=[{"role": "user", "content": prompt}],
    )
    text = next((b.text for b in response.content if b.type == "text"), "")
    if not text or response.stop_reason == "max_tokens":
        raise RuntimeError("model output empty or truncated — try again")
    k = json.loads(text)

    today = date.today().isoformat()
    name = meta["name"]
    strings = [
        f"[PROJECT] user shanks built project '{name}': {k['purpose']} date {today}. source legacy-learn. verified true.",
        f"[PROJECT] project '{name}' tech stack: {k['stack']}. date {today}.",
        f"[PROJECT] project '{name}' architecture: {k['architecture']}. date {today}.",
        f"[PROJECT] project '{name}' key features: {k['features']}. date {today}.",
        f"[PROJECT] project '{name}' notable patterns and conventions: {k['patterns']}. date {today}.",
    ]
    cognee_client.remember(strings)
    return {"name": name, "knowledge": k, "nodes": len(strings)}
