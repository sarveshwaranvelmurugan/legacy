"""Legacy — Compact Memory Engine (CME).

Distills raw user reflections into 0-6 typed, confidence-scored nodes
before anything touches Cognee. Cognee never sees noise.

Runs on Claude Haiku 4.5 to keep per-call cost around a quarter of a cent.
"""
from __future__ import annotations

from datetime import date as _date

import anthropic

from . import config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

CME_SYSTEM_PROMPT = """You are the Compact Memory Engine for Legacy, a life-trajectory agent.
You distill a user's raw daily reflection into 0-6 typed memory nodes. Extract only signal; ignore filler, vague musings, and pleasantries.

Node types and when to use them:
- GOAL: user commits to a concrete objective ("I want to learn system design by August").
- ACTION: something the user actually did ("solved 2 LeetCode mediums today"). confidence 0.7-0.9.
- CLAIM: a self-assessment with no evidence attached ("I'm consistent with DSA"). confidence starts 0.3.
- EVIDENCE: verifiable output (commit, certificate, submission, publication). confidence 0.9 if external, 0.5 if self-reported.
- CONTRADICTION: user admits a gap between what they said and what they did ("I said daily DSA but haven't opened it in 3 weeks"). severity low|medium|high.
- PREFERENCE: a durable like/dislike/choice ("my favourite bike is the Hunter 350", "I hate Java", "I prefer dark UIs"). confidence 0.8.
- FACT: a durable personal fact or context ("I live in Chennai", "my campus placements start in September", "I ride to college daily"). confidence 0.8.

Rules:
- Remember the PERSON, not just the goals: preferences, interests, and personal facts are first-class memory.
- Pure filler with nothing durable (greetings, weather small-talk, "lol ok") produces ZERO nodes.
- Never invent details. linked_goal is the user's goal the node relates to, or "" if none is clear.
- text must be a single dense sentence in third person about "user shanks".
- Use the reflection date provided for the date field."""

NODES_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "nodes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["GOAL", "ACTION", "CLAIM", "EVIDENCE", "CONTRADICTION", "PREFERENCE", "FACT"],
                        },
                        "text": {"type": "string"},
                        "linked_goal": {"type": "string"},
                        "domain": {"type": "string"},
                        "confidence": {"type": "number"},
                        "severity": {"type": "string", "enum": ["", "low", "medium", "high"]},
                        "source": {"type": "string"},
                    },
                    "required": ["type", "text", "linked_goal", "domain", "confidence", "severity", "source"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["nodes"],
        "additionalProperties": False,
    },
}


def extract_nodes(reflection: str, reflection_date: str | None = None) -> list[dict]:
    """Run the CME on one raw reflection. Returns a list of typed node dicts."""
    reflection_date = reflection_date or _date.today().isoformat()
    response = _client.messages.create(
        model=config.CME_MODEL,
        max_tokens=1024,
        system=[{"type": "text", "text": CME_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        output_config={"format": NODES_SCHEMA},
        messages=[
            {
                "role": "user",
                "content": f"Reflection date: {reflection_date}\n\nReflection:\n{reflection}",
            }
        ],
    )
    import json

    text = next(b.text for b in response.content if b.type == "text")
    nodes = json.loads(text)["nodes"]
    for n in nodes:
        n["date"] = reflection_date
    return nodes


def format_node_for_cognee(node: dict) -> str:
    """Convert a CME node into a dense, graph-friendly memory string."""
    t = node["type"]
    base = f"[{t}] {node['text']}"
    parts = [base, f"date {node['date']}."]
    if node.get("linked_goal"):
        parts.append(f"linked goal: {node['linked_goal']}.")
    if node.get("domain"):
        parts.append(f"domain: {node['domain']}.")
    parts.append(f"confidence {node['confidence']}.")
    if t == "CONTRADICTION" and node.get("severity"):
        parts.append(f"severity {node['severity']}.")
    if t == "EVIDENCE":
        src = node.get("source") or "manual"
        verified = "true" if src not in ("", "manual", "self-reported") else "false"
        parts.append(f"source {src}. verified {verified}.")
    if t == "CLAIM":
        parts.append("verified false. no supporting evidence linked yet.")
    if t == "GOAL":
        parts.append("status OPEN.")
    if t in ("PREFERENCE", "FACT"):
        parts.append("durable personal memory.")
    return " ".join(parts)
