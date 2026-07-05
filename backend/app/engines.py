"""Legacy — the reasoning engines.

Each engine is a typed multi-hop query over the Cognee knowledge graph via
recall(), with a purpose-built system prompt. Cognee's graph completion does
the traversal and reasoning; we shape the question and the output contract.

  1. Contradiction Engine   — CLAIM nodes with no supporting EVIDENCE
  2. Goal Consistency Scorer — actions taken vs expected cadence per goal
  3. Behavioral Inference    — stated goals vs revealed behavioral preferences
  4. Future Self Simulator   — 1-year projection from current trajectory
"""
from __future__ import annotations

import json
import uuid
from datetime import date
from pathlib import Path

from . import cme, cognee_client, config, ledger

_STORE = Path(__file__).resolve().parents[1] / "hypotheses.json"


def _today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------- engine 1
def contradiction_engine() -> str:
    return cognee_client.recall(
        f"Today is {_today()}. Find every CLAIM or CONTRADICTION for user shanks "
        "that is NOT backed up by ACTION or EVIDENCE nodes in the same domain. "
        "Cross-reference carefully: a claim about DSA consistency is supported if "
        "there are recent DSA actions; a claim about hackathons is supported by "
        "hackathon wins or commits. Only report genuinely unsupported claims. "
        "For each: the claim text, how many days it has been unverified (from its "
        "date to today), a severity (high if >14 days unverified, medium if >7, "
        "else low), and a confidence percentage based on how many graph nodes "
        "support the finding.",
        system_prompt=(
            "You are the Contradiction Engine of a life-trajectory agent. Be direct "
            "and factual. Output a ranked markdown list (max 5 findings), most "
            "severe first. If the same claim recurs on multiple dates, merge it "
            "into ONE finding, count days-unverified from its EARLIEST date, and "
            "note how many times it was repeated. Every finding must cite dates "
            "from the graph. Never soften the findings, but never report a claim "
            "as unsupported when same-domain actions exist."
        ),
        top_k=40,
    )


# ---------------------------------------------------------------- engine 2
def consistency_scorer() -> str:
    """Deterministic: counts every ACTION/EVIDENCE node in the local ledger.

    The narrative engines reason over the Cognee graph; scores are arithmetic
    over the exact node list, so they are reproducible on stage.
    """
    return ledger.consistency_report()


# ---------------------------------------------------------------- engine 3
def behavioral_inference() -> dict:
    """Detect the gap between stated goals and revealed preferences.

    Returns a hypothesis dict (stored locally, awaiting user confirmation).
    The hypothesis is phrased as a QUESTION, never a verdict.
    """
    analysis = cognee_client.recall(
        "Cluster all ACTION and EVIDENCE nodes for user shanks by domain. Compare "
        "the distribution of actual behavior against the stated GOAL nodes. What "
        "emergent pattern does the behavior show, and which stated goals does it "
        "contradict? Count the supporting nodes.",
        system_prompt=(
            "You are the Behavioral Inference Engine. Respond with JSON only, no "
            "markdown fences: {\"pattern\": one-sentence observed pattern, "
            "\"hypothesis\": one-sentence hypothesis phrased tentatively, "
            "\"supporting_nodes\": integer, \"confidence\": integer 0-100, "
            "\"contradicts_goal\": goal name or \"\"}"
        ),
    )
    try:
        data = json.loads(analysis.strip().removeprefix("```json").removesuffix("```"))
        if not isinstance(data, dict):
            raise ValueError("not an object")
    except (json.JSONDecodeError, ValueError):
        data = {}
    # normalize: free-form recall output is not schema-enforced — never trust shape
    def _int(v, d):
        try:
            return int(v)
        except (TypeError, ValueError):
            return d
    hypothesis = {
        "id": uuid.uuid4().hex[:8],
        "created": _today(),
        "status": "PENDING",
        "pattern": str(data.get("pattern") or analysis[:300]),
        "hypothesis": str(data.get("hypothesis") or analysis[:200]),
        "supporting_nodes": _int(data.get("supporting_nodes"), 0),
        "confidence": max(1, min(99, _int(data.get("confidence"), 50))),
        "contradicts_goal": str(data.get("contradicts_goal") or ""),
    }
    _save_hypothesis(hypothesis)
    return hypothesis


def respond_to_hypothesis(hypothesis_id: str, response: str, context: str = "") -> dict:
    """The improve() loop: user confirms/rejects/corrects a hypothesis and the
    graph recalibrates. This is memory that learns from being corrected."""
    hyps = _load_hypotheses()
    hyp = next((h for h in hyps if h["id"] == hypothesis_id), None)
    if hyp is None:
        raise KeyError(f"unknown hypothesis {hypothesis_id}")

    status = {"accurate": "CONFIRMED", "partial": "PARTIAL", "inaccurate": "REJECTED"}[response]
    old_conf = hyp.get("confidence", 50)
    delta = {"CONFIRMED": +15, "PARTIAL": -8, "REJECTED": -25}[status]
    new_conf = max(5, min(98, old_conf + delta))
    calibration = (
        f"[CALIBRATION] On {_today()} user shanks marked the hypothesis "
        f"'{hyp.get('hypothesis', '')}' as {status}."
        + (f" User context: {context}." if context else "")
        + f" Hypothesis confidence recalibrated from {old_conf} to {new_conf}."
    )
    strings = [calibration]
    # If the user supplied missing context, extract it as real nodes too.
    if context:
        strings += [cme.format_node_for_cognee(n) for n in cme.extract_nodes(context)]
    # Graph write FIRST — if it fails, the hypothesis stays PENDING and
    # answerable rather than silently vanishing half-committed.
    cognee_client.remember(strings)
    hyp["status"] = status
    hyp["user_response"] = context
    hyp["confidence"] = new_conf
    _save_all(hyps)
    return hyp


# ---------------------------------------------------------------- engine 4
def future_self_simulator() -> str:
    scores = ledger.consistency_report()
    return cognee_client.recall(
        f"Today is {_today()}. These action counts per goal are exact and "
        f"authoritative — use these numbers, do not recount:\n{scores}\n\n"
        "Based on these counts plus the goals, claims, contradictions and "
        "calibrations in the graph for user shanks: project their trajectory "
        "1 year forward at the current pace. Which goals will likely complete, "
        "which will stall, which domains are accelerating or stagnant?",
        system_prompt=(
            "You are the Future Self Simulator. Output: (1) 'Likely to complete' and "
            "'Likely to stall' lists, (2) a 3-sentence honest projection paragraph — "
            "candid, specific, grounded in the graph data, no motivational fluff, "
            "(3) the single highest-leverage action to take this week, one line."
        ),
    )


# ---------------------------------------------------------------- engine 5
def open_question() -> str:
    """The question you're avoiding. One per report. Asked, not told."""
    scores = ledger.consistency_report()
    return cognee_client.recall(
        f"Today is {_today()}. Exact authoritative action counts per goal:\n"
        f"{scores}\n\nLooking at these counts and all of user shanks's goals, "
        "claims and contradictions in the graph: which single stated goal has the "
        "largest gap between how often it is talked about and how little is done "
        "about it?",
        system_prompt=(
            "You are Legacy, a mentor with perfect memory. Output ONE short open "
            "question (2-3 sentences max) addressed directly to the user as 'you', "
            "naming the specific goal and the specific numbers from the graph. The "
            "question should make them decide whether this is a real goal or an "
            "identity label they are not ready to act on. No preamble, no list."
        ),
    )


# ------------------------------------------------------- agent initiative
def should_ask(min_new_reflections: int = 3) -> bool:
    """Legacy's own decision: has enough new behavior accumulated since the
    last hypothesis to justify challenging the user again?"""
    if pending_hypotheses():
        return False  # never stack questions
    hyps = _load_hypotheses()
    last = max((h["created"] for h in hyps), default="1970-01-01")
    new_nodes = [e for e in ledger.load() if e["date"] >= last]
    return len(new_nodes) >= min_new_reflections


def agent_tick() -> dict | None:
    """One beat of Legacy's autonomous loop, run after every reflection:
    observe -> decide -> (maybe) act by generating a new hypothesis."""
    if not should_ask():
        return None
    return behavioral_inference()


# ---------------------------------------------------------------- storage
def _load_hypotheses() -> list[dict]:
    if _STORE.exists():
        return json.loads(_STORE.read_text())
    return []


def _save_hypothesis(hyp: dict) -> None:
    hyps = _load_hypotheses()
    hyps.append(hyp)
    _save_all(hyps)


def _save_all(hyps: list[dict]) -> None:
    _STORE.write_text(json.dumps(hyps, indent=2))


def pending_hypotheses() -> list[dict]:
    return [h for h in _load_hypotheses() if h["status"] == "PENDING"]
