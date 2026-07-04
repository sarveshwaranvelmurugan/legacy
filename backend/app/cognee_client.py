"""Legacy — thin client for the Cognee Cloud REST API.

Wraps the four memory-lifecycle operations Legacy uses:
  remember  -> POST /api/v1/add_text  (+ cognify to build the graph)
  recall    -> POST /api/v1/recall    (GRAPH_COMPLETION over the user's graph)
  forget    -> POST /api/v1/forget
  visualize -> GET  /api/v1/datasets/{id}/graph
"""
from __future__ import annotations

import time
from typing import Any

import httpx

from . import config

_client = httpx.Client(
    base_url=config.COGNEE_BASE_URL,
    headers={"X-Api-Key": config.COGNEE_API_KEY},
    timeout=httpx.Timeout(300.0, connect=20.0),
)


def remember(memory_strings: list[str], dataset: str = config.DATASET_NAME) -> dict:
    """Ingest compact CME node strings and build the knowledge graph."""
    from . import ledger
    for s in memory_strings:
        ledger.append(s)
    r = _client.post(
        "/api/v1/add_text",
        json={
            "textData": memory_strings,
            "datasetName": dataset,
            "nodeSet": config.NODE_SET,
        },
    )
    r.raise_for_status()
    ingest = r.json()

    r = _client.post(
        "/api/v1/cognify",
        json={"datasets": [dataset], "runInBackground": True},
    )
    r.raise_for_status()
    return {"ingest": ingest, "cognify": r.json()}


def wait_for_processing(dataset_id: str | None = None, timeout_s: int = 600) -> str:
    """Poll dataset status until cognify completes."""
    deadline = time.time() + timeout_s
    status = "UNKNOWN"
    while time.time() < deadline:
        r = _client.get("/api/v1/datasets/status")
        r.raise_for_status()
        statuses = r.json()
        if dataset_id:
            status = statuses.get(dataset_id, "UNKNOWN")
        else:
            values = list(statuses.values())
            status = values[0] if values else "UNKNOWN"
            if values and all("COMPLETED" in v or "ERRORED" in v for v in values):
                return status
        if "COMPLETED" in status or "ERRORED" in status:
            return status
        time.sleep(10)
    return status


def recall(
    query: str,
    system_prompt: str | None = None,
    dataset: str = config.DATASET_NAME,
    top_k: int = 20,
    only_context: bool = False,
) -> str:
    """Query the knowledge graph. Returns the completion text (or raw context)."""
    body: dict[str, Any] = {
        "query": query,
        "datasets": [dataset],
        "searchType": "GRAPH_COMPLETION",
        "topK": top_k,
        "onlyContext": only_context,
    }
    if system_prompt:
        body["systemPrompt"] = system_prompt
    r = _client.post("/api/v1/recall", json=body)
    r.raise_for_status()
    results = r.json()
    if not results:
        return ""
    return results[0].get("text") or str(results[0].get("raw", ""))


def forget(dataset: str, memory_only: bool = False) -> dict:
    """Remove a dataset (or just its graph memory) from Cognee."""
    r = _client.post(
        "/api/v1/forget",
        json={"dataset": dataset, "memoryOnly": memory_only},
    )
    r.raise_for_status()
    return r.json() if r.content else {"status": "ok"}


def list_datasets() -> list[dict]:
    r = _client.get("/api/v1/datasets/")
    r.raise_for_status()
    return r.json()


def get_graph(dataset_id: str) -> dict:
    """Fetch raw graph nodes/edges for visualization."""
    r = _client.get(f"/api/v1/datasets/{dataset_id}/graph")
    r.raise_for_status()
    return r.json()
