"""Legacy — local ledger of ingested memory strings.

Cognee's graph handles semantic reasoning; the ledger gives the Consistency
Scorer a deterministic node list so scores are arithmetic, not vibes.
Every remember() appends here.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

_LEDGER = Path(__file__).resolve().parents[1] / "ledger.jsonl"

GOAL_AREAS = {
    "DSA / LeetCode practice": ["leetcode", "dsa", "dynamic programming", " dp ", "sliding window", "graphs problem"],
    "System design": ["system design", "ddia", "data-intensive", "load balancer"],
    "Interview prep (ServiceNow)": ["mock interview", "interview prep", "servicenow"],
    "Hackathon portfolio": ["hackathon", "codecrafters", "wemakedevs", "commit", "repo", "whiteboard", "prototype"],
    "AI research": ["research paper", "read a paper", "papers", "arxiv"],
}


def append_unique(memory_string: str) -> bool:
    """Append only if this exact string isn't already in the ledger —
    prevents double-counting when the same content is submitted twice."""
    if _LEDGER.exists() and any(
        json.loads(l)["text"] == memory_string
        for l in _LEDGER.read_text().splitlines() if l.strip()
    ):
        return False
    append(memory_string)
    return True


def append(memory_string: str) -> None:
    m = re.search(r"date (\d{4}-\d{2}-\d{2})", memory_string)
    t = re.match(r"\[(\w+)\]", memory_string)
    entry = {
        "type": t.group(1) if t else "UNKNOWN",
        "date": m.group(1) if m else date.today().isoformat(),
        "text": memory_string,
    }
    with _LEDGER.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def load() -> list[dict]:
    if not _LEDGER.exists():
        return []
    return [json.loads(line) for line in _LEDGER.read_text().splitlines() if line.strip()]


def classify(text: str) -> str | None:
    low = " " + text.lower() + " "
    for area, keywords in GOAL_AREAS.items():
        if any(k in low for k in keywords):
            return area
    return None


def consistency_report(expected_per_month: int = 12) -> str:
    """Deterministic scorer: count ACTION/EVIDENCE nodes per goal area."""
    entries = [e for e in load() if e["type"] in ("ACTION", "EVIDENCE")]
    lines = []
    for area in GOAL_AREAS:
        matched = [e for e in entries if classify(e["text"]) == area]
        n = len(matched)
        score = min(100, round(n / expected_per_month * 100))
        verdict = "ON_TRACK" if score > 75 else "DRIFTING" if score >= 40 else "STALLED"
        icon = {"ON_TRACK": "🟢", "DRIFTING": "🟡", "STALLED": "🔴"}[verdict]
        dates = ", ".join(sorted({e["date"][5:] for e in matched})) or "none"
        lines.append(
            f"- {icon} **{area}** — {n} actions ({dates}) — **{score}%** — {verdict}"
        )
    return "\n".join(lines)


def alignment() -> dict:
    """The headline number: 0-100, how closely verified behavior matches
    stated goals. Deterministic — the mean of the goal-area consistency
    scores, with the share of externally verified evidence reported alongside.
    """
    entries = [e for e in load() if e["type"] in ("ACTION", "EVIDENCE")]
    scores = []
    for area in GOAL_AREAS:
        n = len([e for e in entries if classify(e["text"]) == area])
        scores.append(min(100, round(n / 12 * 100)))
    score = round(sum(scores) / len(scores)) if scores else 0
    verified = len([e for e in entries if e["type"] == "EVIDENCE"])
    verdict = ("ALIGNED" if score > 75 else
               "DRIFTING" if score >= 40 else "OFF COURSE")
    return {
        "score": score,
        "verdict": verdict,
        "verified_evidence": verified,
        "total_actions": len(entries),
        "explanation": (
            f"Mean of {len(scores)} goal-area consistency scores; "
            f"{verified} of {len(entries)} behavior nodes are externally verified."
        ),
    }
