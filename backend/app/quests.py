"""Legacy — Quests: improvement as a game you can't cheat.

Three micro-challenges a day, generated from YOUR graph (weakest area,
active project, a real interest). No checkboxes: completion is PROVEN —
verified against synced evidence and conversation memory. A completed quest
becomes a verified ACTION node, so playing the game literally moves your
real consistency scores. The referee is your own memory.

Levels are deterministic arithmetic over the ledger: actions are XP,
externally verified evidence is worth more. No streaks. No mercy. No cheats.
"""
from __future__ import annotations

import json
import math
import uuid
from datetime import date
from pathlib import Path

import anthropic

from . import cme, cognee_client, config, ledger, observer, sources

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
_STORE = Path(__file__).resolve().parents[1] / "quests.json"


# ------------------------------------------------------------ character sheet
def domain_levels() -> list[dict]:
    """Deterministic RPG stats from the ledger. Verified evidence > claims."""
    entries = [e for e in ledger.load() if e["type"] in ("ACTION", "EVIDENCE")]
    out = []
    for area in ledger.GOAL_AREAS:
        matched = [e for e in entries if ledger.classify(e["text"]) == area]
        xp = sum(25 if e["type"] == "EVIDENCE" else 10 for e in matched)
        level = int(math.isqrt(xp // 10)) if xp else 0
        next_xp = ((level + 1) ** 2) * 10
        out.append({
            "domain": area, "level": level, "xp": xp,
            "next_level_xp": next_xp,
            "progress": min(1.0, xp / next_xp) if next_xp else 1.0,
        })
    return sorted(out, key=lambda d: -d["xp"])


# ----------------------------------------------------------------- generation
_QUEST_SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "quests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "why": {"type": "string"},
                        "domain": {"type": "string"},
                        "verify": {"type": "string", "enum": ["github", "leetcode", "chat"]},
                        "xp": {"type": "integer"},
                    },
                    "required": ["title", "why", "domain", "verify", "xp"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["quests"],
        "additionalProperties": False,
    },
}


def _generate() -> list[dict]:
    entries = ledger.load()
    interests = [e["text"] for e in entries if e["type"] in ("PREFERENCE", "FACT")][-8:]
    recent = [e["text"] for e in entries if e["type"] in ("ACTION", "EVIDENCE")][-10:]
    prompt = (
        f"Today is {date.today().isoformat()}. Consistency per goal area:\n"
        f"{ledger.consistency_report()}\n\n"
        f"Recent activity:\n" + "\n".join(recent) +
        "\n\nInterests and facts about the user:\n" + "\n".join(interests) +
        "\n\nGenerate exactly 3 quests for today: (1) one attacking the WEAKEST "
        "area, (2) one advancing their current active project, (3) one that makes "
        "an interest productive. Each must be completable within ~30 minutes today "
        "and provable with a SIMPLE, GENERIC receipt: verify=github (title must be "
        "'Push at least one commit to <repo>' — never reference specific files or "
        "counts), verify=leetcode (title 'Solve one <difficulty> problem'), or "
        "verify=chat (explain a named concept to Legacy in conversation). "
        "xp between 20 and 60, weakest area highest. 'why' is one dry, honest "
        "sentence citing the user's own numbers."
    )
    response = _client.messages.create(
        model=config.CME_MODEL,
        max_tokens=800,
        system=("You are Legacy's quest master — a mentor with perfect memory and "
                "a dry wit. Personal, specific, never generic. No fantasy language."),
        output_config={"format": _QUEST_SCHEMA},
        messages=[{"role": "user", "content": prompt}],
    )
    quests = json.loads(next(b.text for b in response.content if b.type == "text"))["quests"]
    for q in quests:
        q["id"] = uuid.uuid4().hex[:8]
        q["status"] = "OPEN"
        q["proof"] = ""
    return quests


def journey() -> list[dict]:
    """Cumulative XP per day — the deterministic shape of your month."""
    entries = sorted(
        (e for e in ledger.load() if e["type"] in ("ACTION", "EVIDENCE")),
        key=lambda e: e["date"],
    )
    days: dict[str, int] = {}
    for e in entries:
        days[e["date"]] = days.get(e["date"], 0) + (25 if e["type"] == "EVIDENCE" else 10)
    out, total = [], 0
    for d in sorted(days):
        total += days[d]
        out.append({"date": d, "xp": total, "gained": days[d]})
    return out


def today() -> dict:
    """Today's quest board (generated once per day) + the character sheet."""
    state = json.loads(_STORE.read_text()) if _STORE.exists() else {}
    if state.get("date") != date.today().isoformat():
        state = {"date": date.today().isoformat(), "quests": _generate()}
        _STORE.write_text(json.dumps(state, indent=2))
    return {**state, "levels": domain_levels(), "journey": journey()}


# ---------------------------------------------------------------- verification
def verify(quest_id: str) -> dict:
    """Prove a quest. Syncs evidence sources, then judges strictly against
    today's memory. Success writes a verified ACTION back into the graph."""
    state = json.loads(_STORE.read_text())
    quest = next((q for q in state["quests"] if q["id"] == quest_id), None)
    if quest is None:
        raise KeyError(quest_id)
    if quest["status"] == "DONE":
        return {"quest": quest, "message": "already proven"}

    # 1. Pull fresh receipts for evidence-based quests.
    if quest["verify"] in ("github", "leetcode"):
        cfg = sources.get_settings()[quest["verify"]]
        if cfg["enabled"] and cfg["username"]:
            {"github": sources.sync_github, "leetcode": sources.sync_leetcode}[quest["verify"]]()
    if quest["verify"] == "github":
        # local git is the freshest truth (GitHub's events API lags minutes)
        observer.look(Path(__file__).resolve().parents[2])

    today_s = date.today().isoformat()
    todays = [e["text"] for e in ledger.load() if e["date"] == today_s][-30:]
    if quest["verify"] == "chat":
        conversation = cognee_client.recall(
            f"Did the user discuss or explain this with Legacy today ({today_s}): "
            f"{quest['title']}? Quote what the graph has.",
        )
        todays.append(f"Conversation memory check: {conversation[:600]}")

    # 2. Strict judgment — the referee is the memory, not the user.
    response = _client.messages.create(
        model=config.CME_MODEL,
        max_tokens=300,
        system=("You judge whether a quest was completed TODAY based only on the "
                "memory entries provided. Strict: no supporting entry, no credit. "
                "Judge INTENT, not letter; later entries supersede earlier notes. "
                "Rules per verify type — github: DONE if any entry shows a commit "
                "or push to the named repo today. leetcode: DONE if any entry "
                "shows an accepted solve today matching the difficulty. chat: DONE "
                "if the conversation memory shows the user genuinely discussed or "
                "explained the named topic today. Reply as JSON only: "
                "{\"done\": true|false, \"proof\": \"one line citing the entry "
                "that proves it, or what is missing\"}"),
        messages=[{"role": "user", "content":
                   f"Quest: {quest['title']} (verify via {quest['verify']})\n\n"
                   f"Today's memory entries:\n" + "\n".join(todays)}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    try:
        verdict = json.loads(text.strip().removeprefix("```json").removesuffix("```"))
    except json.JSONDecodeError:
        verdict = {"done": False, "proof": "judge returned no verdict — try again"}

    if verdict.get("done"):
        quest["status"] = "DONE"
        quest["proof"] = verdict.get("proof", "")
        cognee_client.remember([
            f"[ACTION] user shanks completed the quest '{quest['title']}' "
            f"({quest['domain']}). date {today_s}. confidence 0.9. "
            f"proof: {quest['proof'][:140]}"
        ])
        _STORE.write_text(json.dumps(state, indent=2))
    return {"quest": quest, "verdict": verdict}
