"""Legacy — opt-in evidence sources.

Legacy is zero-trust about claims but consent-first about surveillance:
every external source is an explicit toggle the user controls. When a source
is ON, syncing pulls real public activity and stores it as *verified*
EVIDENCE nodes (confidence 0.9). Synced items are watermarked so repeat
syncs never duplicate.

Sources:
  github   — public push events (REST, no auth)
  leetcode — recent accepted submissions (public GraphQL, no auth)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import cognee_client

_SETTINGS = Path(__file__).resolve().parents[1] / "sources.json"

DEFAULTS = {
    "github": {"enabled": False, "username": "", "last_sync_watermark": ""},
    "leetcode": {"enabled": False, "username": "", "last_sync_watermark": ""},
}


def get_settings() -> dict:
    if _SETTINGS.exists():
        stored = json.loads(_SETTINGS.read_text())
        return {k: {**v, **stored.get(k, {})} for k, v in DEFAULTS.items()}
    return json.loads(json.dumps(DEFAULTS))


def update_settings(patch: dict) -> dict:
    settings = get_settings()
    for source, cfg in patch.items():
        if source in settings:
            settings[source].update({k: v for k, v in cfg.items()
                                     if k in ("enabled", "username")})
    _SETTINGS.write_text(json.dumps(settings, indent=2))
    return settings


def _save(settings: dict) -> None:
    _SETTINGS.write_text(json.dumps(settings, indent=2))


# ------------------------------------------------------------------ github
def sync_github() -> dict:
    settings = get_settings()
    cfg = settings["github"]
    if not cfg["enabled"]:
        return {"error": "GitHub source is switched off — enable it first."}
    if not cfg["username"]:
        return {"error": "Set a GitHub username first."}

    try:
        r = httpx.get(
            f"https://api.github.com/users/{cfg['username']}/events/public",
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "legacy-agent"},
            timeout=30,
        )
    except httpx.HTTPError as e:
        return {"error": f"GitHub unreachable ({type(e).__name__}) — check network and retry."}
    if r.status_code == 404:
        return {"error": f"GitHub user '{cfg['username']}' not found."}
    if r.status_code in (403, 429):
        return {"error": "GitHub rate limit hit (60 req/hour unauthenticated). "
                         "Wait a bit and sync again — nothing was lost."}
    r.raise_for_status()

    watermark = cfg.get("last_sync_watermark", "")
    strings, newest = [], watermark
    for event in r.json():
        if event["type"] != "PushEvent":
            continue
        created = event["created_at"]
        if watermark and created <= watermark:
            continue
        newest = max(newest, created)
        repo = event["repo"]["name"]
        head = event["payload"].get("head", "")
        branch = event["payload"].get("ref", "").removeprefix("refs/heads/")
        # The unauthenticated events API omits commit details — fetch the head
        # commit's message directly so evidence is specific and unique per SHA.
        msg = ""
        if head:
            try:
                c = httpx.get(
                    f"https://api.github.com/repos/{repo}/commits/{head}",
                    headers={"Accept": "application/vnd.github+json",
                             "User-Agent": "legacy-agent"},
                    timeout=20,
                )
                if c.status_code == 200:
                    msg = ((c.json().get("commit", {}).get("message") or "").splitlines() or [""])[0]
            except httpx.HTTPError:
                pass  # evidence still records the push; message is a bonus
        strings.append(
            f"[EVIDENCE] user shanks pushed commit {head[:7]} to {repo} "
            f"on branch {branch}: '{msg}'. date {created[:10]}. "
            f"source github. verified true. confidence 0.9."
        )
    if strings:
        cognee_client.remember(strings)
        cfg["last_sync_watermark"] = newest
        _save(settings)
    return {"synced": len(strings), "evidence": strings[:5]}


# ---------------------------------------------------------------- leetcode
_LC_QUERY = """
query recentAc($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id title titleSlug timestamp
  }
}"""


def sync_leetcode(limit: int = 15) -> dict:
    settings = get_settings()
    cfg = settings["leetcode"]
    if not cfg["enabled"]:
        return {"error": "LeetCode source is switched off — enable it first."}
    if not cfg["username"]:
        return {"error": "Set a LeetCode username first."}

    try:
        r = httpx.post(
        "https://leetcode.com/graphql",
        json={"query": _LC_QUERY,
              "variables": {"username": cfg["username"], "limit": limit}},
        headers={"Content-Type": "application/json",
                 "Referer": "https://leetcode.com",
                 "User-Agent": "Mozilla/5.0 (legacy-agent)"},
        timeout=30,
        )
    except httpx.HTTPError as e:
        return {"error": f"LeetCode unreachable ({type(e).__name__}) — check network and retry."}
    if r.status_code == 429:
        return {"error": "LeetCode is rate-limiting — wait a minute and sync again."}
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        return {"error": f"LeetCode: {payload['errors'][0].get('message', 'user not found or profile private')}"}
    subs = (payload.get("data") or {}).get("recentAcSubmissionList") or []

    watermark = cfg.get("last_sync_watermark", "")
    strings, newest = [], watermark
    for s in subs:
        ts = s["timestamp"]
        if watermark and int(ts) <= int(watermark or 0):
            continue
        newest = max(newest, ts, key=int) if newest else ts
        day = datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat()
        strings.append(
            f"[EVIDENCE] user shanks solved LeetCode problem '{s['title']}' "
            f"(accepted submission). date {day}. source leetcode. verified true. "
            f"confidence 0.9. domain DSA."
        )
    if strings:
        cognee_client.remember(strings)
        cfg["last_sync_watermark"] = str(newest)
        _save(settings)
    return {"synced": len(strings), "evidence": strings[:5]}
