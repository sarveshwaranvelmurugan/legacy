"""Legacy — GitHub evidence adapter.

Pulls recent public push events and turns each into a *verified* EVIDENCE node.
This is the difference between "user says they coded" (confidence 0.3-0.5) and
"GitHub proves they coded" (confidence 0.9). The graph knows the difference.

Requires GITHUB_USERNAME in .env (public events only; no token needed).
"""
from __future__ import annotations

import os

import httpx

from . import cognee_client


def fetch_push_evidence(username: str | None = None, limit: int = 10) -> list[str]:
    username = username or os.environ.get("GITHUB_USERNAME", "")
    if not username:
        raise RuntimeError("Set GITHUB_USERNAME in .env")
    r = httpx.get(
        f"https://api.github.com/users/{username}/events/public",
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )
    r.raise_for_status()
    strings: list[str] = []
    for event in r.json():
        if event["type"] != "PushEvent":
            continue
        repo = event["repo"]["name"]
        day = event["created_at"][:10]
        commits = event["payload"].get("commits", [])
        msgs = "; ".join(((c.get("message") or "").splitlines() or [""])[0] for c in commits[:3])
        strings.append(
            f"[EVIDENCE] user shanks pushed {len(commits)} commit(s) to {repo} "
            f"({msgs}). date {day}. source github. verified true. confidence 0.9."
        )
        if len(strings) >= limit:
            break
    return strings


def sync(username: str | None = None, limit: int = 10) -> dict:
    strings = fetch_push_evidence(username, limit)
    if not strings:
        return {"synced": 0}
    cognee_client.remember(strings)
    return {"synced": len(strings), "evidence": strings}
