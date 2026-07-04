"""Legacy — FastAPI backend.

Endpoints:
  POST /reflect             daily reflection -> CME -> cognee.remember()
  GET  /report              the 30-Day Contradiction & Growth Report
  GET  /hypotheses          pending BIE hypotheses awaiting user response
  POST /hypothesis/respond  the improve() loop: user feedback recalibrates the graph
  POST /goal/close          conscious closure -> recorded, then forgettable
  GET  /graph               raw graph nodes/edges for visualization
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import cme, cognee_client, config, engines, ledger, sources

app = FastAPI(title="Legacy", version="0.2.0")


@app.exception_handler(Exception)
async def unhandled_error(request, exc):
    """A crash must never hang the UI — always answer with clean JSON."""
    return JSONResponse(status_code=502, content={
        "detail": f"{type(exc).__name__}: {exc}",
        "hint": "An upstream service (Anthropic/Cognee) may be slow or unreachable — try again.",
    })


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Reflection(BaseModel):
    text: str
    date: str | None = None


class HypothesisResponse(BaseModel):
    id: str
    response: str  # accurate | partial | inaccurate
    context: str = ""


class GoalClosure(BaseModel):
    goal: str
    reason: str


@app.get("/health")
def health():
    return {"status": "ok", "dataset": config.DATASET_NAME}


@app.post("/reflect")
def reflect(r: Reflection, background: BackgroundTasks):
    nodes = cme.extract_nodes(r.text, r.date)
    if not nodes:
        return {"nodes": [], "memory_strings": [], "message": "No signal extracted — nothing stored."}
    strings = [cme.format_node_for_cognee(n) for n in nodes]
    cognee_client.remember(strings)
    # Agent initiative: Legacy decides on its own whether the new behavior
    # warrants challenging the user with a fresh hypothesis.
    will_ask = engines.should_ask()
    if will_ask:
        background.add_task(engines.agent_tick)
    return {"nodes": nodes, "memory_strings": strings, "agent_will_ask": will_ask}


@app.get("/report")
def report():
    cognee_client.wait_for_processing(timeout_s=120)
    # The three narrative engines are independent recall() calls — run them
    # concurrently so the report takes one traversal's time, not three.
    with ThreadPoolExecutor(max_workers=3) as pool:
        contradictions = pool.submit(engines.contradiction_engine)
        projection = pool.submit(engines.future_self_simulator)
        question = pool.submit(engines.open_question)
        return {
            "generated": date.today().isoformat(),
            "alignment": ledger.alignment(),
            "consistency": engines.consistency_scorer(),
            "hypotheses": engines.pending_hypotheses(),
            "contradictions": contradictions.result(),
            "projection": projection.result(),
            "open_question": question.result(),
        }


@app.post("/hypothesis/generate")
def generate_hypothesis():
    return engines.behavioral_inference()


@app.get("/hypotheses")
def hypotheses():
    return engines.pending_hypotheses()


@app.post("/hypothesis/respond")
def hypothesis_respond(hr: HypothesisResponse):
    if hr.response not in ("accurate", "partial", "inaccurate"):
        raise HTTPException(400, "response must be accurate | partial | inaccurate")
    try:
        return engines.respond_to_hypothesis(hr.id, hr.response, hr.context)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.post("/goal/close")
def close_goal(gc: GoalClosure):
    """Conscious closure: the graph records that you moved on, and why."""
    closure = (
        f"[GOAL] user shanks consciously closed the goal '{gc.goal}' on "
        f"{date.today().isoformat()}. status CLOSED. reason: {gc.reason}."
    )
    cognee_client.remember([closure])
    return {"closed": gc.goal, "recorded": closure}


class SourcePatch(BaseModel):
    github: dict | None = None
    leetcode: dict | None = None


@app.get("/sources")
def get_sources():
    return sources.get_settings()


@app.post("/sources")
def set_sources(patch: SourcePatch):
    return sources.update_settings({k: v for k, v in patch.model_dump().items() if v})


@app.post("/sources/github/sync")
def github_sync():
    return sources.sync_github()


@app.post("/sources/leetcode/sync")
def leetcode_sync():
    return sources.sync_leetcode()


@app.get("/graph")
def graph():
    datasets = cognee_client.list_datasets()
    ds = next((d for d in datasets if d["name"] == config.DATASET_NAME), None)
    if ds is None:
        raise HTTPException(404, "dataset not found")
    return cognee_client.get_graph(ds["id"])
