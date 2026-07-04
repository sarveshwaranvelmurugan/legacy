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
