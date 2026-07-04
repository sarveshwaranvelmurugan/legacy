"""Legacy — session workflow distillation.

The commands you teach your coding agent are tribal knowledge nobody writes
down: "run make lint from repo root", "copy config/ into the service folder
before go test". This module distills them into permanent [WORKFLOW] memory.

Three entry points, one distiller:
  - Claude Code SessionEnd hook  -> distill_claude_transcript(transcript_path)
  - MCP tool legacy_store_session -> distill_text()  (Cursor, Copilot, any client)
  - CLI `legacy distill`          -> distill_text()  (any agent with a terminal)

Privacy: distillation, not transcription. Only workflow facts (commands,
sequences, conventions) are extracted; code, file contents, and secrets never
enter the graph. Transcripts are read once, locally, and discarded.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import anthropic

from . import cognee_client, config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "facts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "knowledge": {"type": "string"},
                    },
                    "required": ["project", "knowledge"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["facts"],
        "additionalProperties": False,
    },
}

_SYSTEM = """You extract durable WORKFLOW knowledge from a coding-session excerpt: the
commands, sequences, and conventions worth remembering for months.

Extract ONLY reusable how-to facts, e.g.:
- how to lint/test/build/deploy in a repo ("lint = 'make lint' from repo root")
- required rituals ("go tests in a service folder need config/ copied from repo root first")
- project conventions ("commits use conventional format", "never push to main")

Each fact: project = repo/project name if evident else "", knowledge = one dense
self-contained sentence with the exact command(s) quoted.

NEVER extract: source code, file contents, API keys/tokens/secrets, one-off
debugging commands, or anything not reusable. 0-6 facts; an uneventful session
yields zero."""


def distill_text(session_text: str, source: str = "session", project_hint: str = "") -> list[str]:
    """Distill workflow knowledge from session text into memory. Returns the
    stored memory strings."""
    if not session_text.strip():
        return []
    prompt = (f"Project context: {project_hint or 'unknown'}\n\n"
              f"Session excerpt:\n{session_text[:14000]}")
    response = _client.messages.create(
        model=config.CME_MODEL,
        max_tokens=900,
        system=_SYSTEM,
        output_config={"format": _SCHEMA},
        messages=[{"role": "user", "content": prompt}],
    )
    facts = json.loads(next(b.text for b in response.content if b.type == "text"))["facts"]
    today = date.today().isoformat()
    strings = []
    for f in facts:
        proj = f["project"] or project_hint
        strings.append(
            f"[WORKFLOW] {f['knowledge']}"
            + (f" project: {proj}." if proj else "")
            + f" date {today}. source {source}. durable workflow knowledge."
        )
    if strings:
        cognee_client.remember(strings)
    return strings


def _extract_from_transcript(path: Path) -> str:
    """Pull user instructions + executed commands from a Claude Code
    transcript (JSONL). Defensive: unknown shapes are skipped."""
    lines = path.read_text(errors="ignore").splitlines()
    picked: list[str] = []
    for line in lines[-600:]:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message") or {}
        role, content = msg.get("role"), msg.get("content")
        if role == "user" and isinstance(content, str):
            picked.append(f"USER: {content[:500]}")
        elif isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if role == "user" and block.get("type") == "text":
                    text = block.get("text", "")
                    if text and not text.startswith("<"):  # skip system-reminders
                        picked.append(f"USER: {text[:500]}")
                elif block.get("type") == "tool_use" and block.get("name") == "Bash":
                    cmd = (block.get("input") or {}).get("command", "")
                    if cmd:
                        picked.append(f"RAN: {cmd[:300]}")
    return "\n".join(picked[-200:])


def distill_claude_transcript(transcript_path: str, cwd: str = "") -> list[str]:
    path = Path(transcript_path)
    if not path.exists():
        return []
    text = _extract_from_transcript(path)
    project = Path(cwd).name if cwd else ""
    return distill_text(text, source="claude-code-session", project_hint=project)
