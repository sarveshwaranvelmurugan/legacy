"""Legacy — MCP server.

Exposes Legacy's memory as native tools for any MCP client (Claude Code,
Claude Desktop, Cursor, …). One registration, and every session in every
project can recall, remember, learn, and sync — no skill-triggering luck.

Run (stdio):  python -m app.mcp_server
Register in Claude Code:
  claude mcp add legacy -- <repo>/.venv/bin/python -m app.mcp_server
  (with cwd/PYTHONPATH pointing at <repo>/backend — `legacy setup` prints
   the exact command for this machine)
"""
from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import cme, cognee_client, engines, ledger, observer, project_learner, sources

mcp = FastMCP(
    "legacy",
    instructions=(
        "Legacy is the user's persistent memory agent — a Cognee knowledge "
        "graph of their projects, goals, actions, verified evidence, and "
        "contradictions that survives across every session and tool. Use "
        "legacy_recall when the user references past work, projects, goals or "
        "patterns; legacy_remember when they tell you something worth keeping; "
        "legacy_learn_project / legacy_observe when they finish work in a repo."
    ),
)


@mcp.tool()
def legacy_recall(question: str) -> str:
    """Answer a question from the user's persistent memory graph: past
    projects (stacks, architectures, patterns), goals, progress, history.
    Use whenever the user references their earlier work or asks about
    themselves. Takes ~15-30s."""
    scores = ledger.consistency_report()
    return cognee_client.recall(
        f"Exact authoritative action counts per goal:\n{scores}\n\n"
        f"Question: {question}",
        system_prompt=(
            "You are Legacy, the user's memory agent. Answer directly and "
            "concretely from the graph; cite dates and numbers when they matter."
        ),
    )


@mcp.tool()
def legacy_remember(fact: str) -> str:
    """Store something the user did, decided, finished, or committed to.
    Pass one dense factual sentence (third person). It is distilled into
    typed memory nodes and woven into the knowledge graph."""
    nodes = cme.extract_nodes(fact)
    if not nodes:
        return "No durable signal extracted — nothing stored."
    strings = [cme.format_node_for_cognee(n) for n in nodes]
    cognee_client.remember(strings)
    return f"Remembered {len(strings)} node(s): " + "; ".join(
        f"[{n['type']}] {n['text'][:60]}" for n in nodes)


@mcp.tool()
def legacy_observe(project_path: str) -> str:
    """Record a project's current git state (repo, branch, today's commits)
    as verified evidence. Call with the absolute path of the project being
    discussed, typically after the user pushes or finishes a work session."""
    seen = observer.look(Path(project_path))
    return seen["summary"] if seen else "Not a git repository — nothing to observe."


@mcp.tool()
def legacy_learn_project(project_path: str) -> str:
    """Deep-study a finished project into memory (METADATA ONLY: README,
    manifests, directory tree, commit messages — never source code bodies).
    Afterwards the user can say 'build it like <project>' in any session."""
    result = project_learner.learn(Path(project_path))
    k = result["knowledge"]
    return (f"Learned '{result['name']}' ({result['nodes']} nodes). "
            f"Stack: {k['stack'][:120]}. Patterns: {k['patterns'][:120]}")


@mcp.tool()
def legacy_sync_evidence() -> str:
    """Sync all connected evidence sources (GitHub pushes, LeetCode solves)
    into the graph as verified evidence. Sources the user has switched off
    are never read."""
    out = []
    for name, cfg in sources.get_settings().items():
        if not (cfg["enabled"] and cfg["username"]):
            out.append(f"{name}: off")
            continue
        fn = {"github": sources.sync_github, "leetcode": sources.sync_leetcode}[name]
        r = fn()
        out.append(f"{name}: {r.get('error') or str(r['synced']) + ' new verified node(s)'}")
    return " | ".join(out)


@mcp.tool()
def legacy_alignment() -> str:
    """The user's current alignment score (0-100): how closely their verified
    behavior matches their stated goals. Deterministic, with explanation."""
    al = ledger.alignment()
    return (f"{al['score']}/100 — {al['verdict']}. {al['explanation']}")


if __name__ == "__main__":
    mcp.run()
