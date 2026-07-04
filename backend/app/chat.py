"""Legacy — the conversational engine.

A ChatGPT-style conversation that never forgets: Legacy chats like a capable
assistant (analysis, advice, anything), reaches into the Cognee graph with a
search_memory tool when your past is relevant, and after every exchange
quietly distills the durable parts — preferences, facts, decisions, work —
into permanent memory.

Session dies; the person Legacy knows doesn't.
"""
from __future__ import annotations

import threading

import anthropic

from . import cme, cognee_client, config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

CHAT_SYSTEM = """You are Legacy, the user's personal AI with permanent memory. You are a \
capable, direct, warm assistant — analysis, advice, explanations, opinions, anything — \
and unlike other AIs you actually know this user across every past session.

You have a search_memory tool over the user's lifelong knowledge graph (their projects, \
goals, preferences, facts, history, work activity). HARD RULE: before you ever say you \
don't know, don't have a record, or haven't been told something ABOUT THE USER (their \
possessions, preferences, projects, history, plans), you MUST call search_memory first — \
claiming ignorance about the user without searching is the one failure you may never \
commit. Also search whenever their past would improve your answer. Skip it only for \
pure general-knowledge questions.

Style: conversational and concise (this renders in a terminal). Reference what you \
remember about the user naturally, like a friend would — not like a database report."""

_TOOLS = [{
    "name": "search_memory",
    "description": (
        "Search the user's permanent memory graph: their projects, goals, "
        "preferences, personal facts, work history, and past conversations. "
        "Takes ~15s. Use when their past or personal context is relevant."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "what to look up about the user"},
        },
        "required": ["query"],
    },
}]


def converse(history: list[dict], on_status=None) -> str:
    """One chat turn. `history` is the running message list (user/assistant).
    Returns the reply text; memory extraction runs in a background thread."""
    messages = list(history)
    reply_parts: list[str] = []

    for _ in range(3):  # at most 2 memory lookups per turn
        response = _client.messages.create(
            model=config.CME_MODEL,
            max_tokens=1200,
            system=[{"type": "text", "text": CHAT_SYSTEM, "cache_control": {"type": "ephemeral"}}],
            tools=_TOOLS,
            messages=messages,
        )
        reply_parts = [b.text for b in response.content if b.type == "text"]
        if response.stop_reason != "tool_use":
            break
        tool_use = next(b for b in response.content if b.type == "tool_use")
        if on_status:
            on_status(f"remembering: {tool_use.input.get('query', '')[:60]}…")
        recalled = cognee_client.recall(
            tool_use.input["query"],
            system_prompt=(
                "Return the relevant facts about this user from the graph, dense "
                "and factual, with dates where present. If nothing relevant, say so."
            ),
        )
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": tool_use.id,
                         "content": recalled or "no relevant memory found"}],
        })

    return "\n".join(p for p in reply_parts if p.strip()) or "(no reply)"


def remember_exchange(user_msg: str, reply: str) -> list[dict]:
    """Distill the durable parts of one exchange into memory. Called in the
    background after each turn — chat stays fast, memory happens anyway."""
    exchange = (
        f"From a conversation with the user today. User said: {user_msg}\n"
        f"The conversation reached this conclusion (store the takeaway itself as a "
        f"FACT node too, e.g. 'user shanks and Legacy concluded that ...'): "
        f"{reply[:600]}"
    )
    nodes = cme.extract_nodes(exchange)
    if nodes:
        strings = [cme.format_node_for_cognee(n) for n in nodes]
        cognee_client.remember(strings)
    return nodes


_pending: list[threading.Thread] = []


def remember_exchange_async(user_msg: str, reply: str, on_done=None) -> None:
    def _run():
        try:
            nodes = remember_exchange(user_msg, reply)
            if on_done:
                on_done(nodes)
        except Exception:
            pass  # memory failure must never crash the chat

    t = threading.Thread(target=_run, daemon=True)
    _pending.append(t)
    t.start()


def wait_pending(timeout_s: float = 60.0) -> None:
    """Block until in-flight memory writes finish — call before process exit
    so a quick goodbye never loses a memory."""
    for t in list(_pending):
        t.join(timeout=timeout_s)
    _pending.clear()
