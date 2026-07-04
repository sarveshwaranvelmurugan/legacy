"""Legacy CLI — the agent in your terminal.

    $ legacy

On launch it perceives where you are (git repo, branch, today's commits) and
remembers it unasked. It primes itself from graph memory, asks any question
it has been holding, then drops into a REPL where plain text is routed
automatically: statements about your day become memory, questions become
graph recall. Slash commands for the rest.
"""
from __future__ import annotations

import sys
from pathlib import Path

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from . import cme, cognee_client, config, engines, ledger, observer

console = Console()
_claude = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

NODE_COLOR = {"GOAL": "green", "ACTION": "blue", "CLAIM": "yellow",
              "EVIDENCE": "cyan", "CONTRADICTION": "red"}


def _route(text: str) -> str:
    """Classify free input: R = reflection to remember, Q = question to answer."""
    r = _claude.messages.create(
        model=config.CME_MODEL,
        max_tokens=3,
        system=("Classify the user's terminal input for a memory agent. Reply with "
                "exactly one letter. R if they are telling you about their work, day, "
                "plans, or feelings (something to remember). Q if they are asking a "
                "question or requesting information."),
        messages=[{"role": "user", "content": text}],
    )
    out = next((b.text for b in r.content if b.type == "text"), "Q")
    return "R" if "R" in out.upper() else "Q"


def _remember(text: str) -> None:
    with console.status("[dim]distilling…[/]"):
        nodes = cme.extract_nodes(text)
    if not nodes:
        console.print("[dim]No signal in that — nothing stored.[/]")
        return
    strings = [cme.format_node_for_cognee(n) for n in nodes]
    with console.status("[dim]cognee.remember()…[/]"):
        cognee_client.remember(strings)
    for n in nodes:
        c = NODE_COLOR.get(n["type"], "white")
        console.print(f"  [{c}]■ {n['type']}[/] {n['text']}")
    if engines.should_ask():
        with console.status("[dim]Legacy is thinking about what it just noticed…[/]"):
            hyp = engines.agent_tick()
        if hyp:
            _ask_hypothesis(hyp)


def _answer(question: str) -> None:
    with console.status("[dim]traversing the graph…[/]"):
        scores = ledger.consistency_report()
        reply = cognee_client.recall(
            f"Exact authoritative action counts per goal:\n{scores}\n\n"
            f"The user asks: {question}",
            system_prompt=(
                "You are Legacy, a mentor with perfect memory of this user's goals, "
                "actions, claims and contradictions. Answer directly and briefly "
                "(under 120 words), grounded in the graph and the counts. Be candid; "
                "cite dates and numbers when they matter."
            ),
        )
    console.print(Panel(Markdown(reply), border_style="dim", title="legacy", title_align="left"))


def _ask_hypothesis(hyp: dict) -> None:
    console.print()
    console.print(Panel(
        f"[bold]{hyp['hypothesis']}[/]\n\n"
        f"[dim]pattern: {hyp['pattern']}\n"
        f"{hyp['confidence']}% confidence · {hyp['supporting_nodes']} supporting nodes[/]",
        title="legacy asks", title_align="left", border_style="yellow",
    ))
    ans = console.input("[yellow]accurate / partial / wrong (or enter to skip) › [/]").strip().lower()
    mapping = {"accurate": "accurate", "a": "accurate", "partial": "partial",
               "p": "partial", "wrong": "inaccurate", "w": "inaccurate", "inaccurate": "inaccurate"}
    if ans not in mapping:
        console.print("[dim]Left pending — it will wait in your report.[/]")
        return
    context = console.input("[dim]anything Legacy is missing? (enter to skip) › [/]").strip()
    with console.status("[dim]recalibrating the graph…[/]"):
        updated = engines.respond_to_hypothesis(hyp["id"], mapping[ans], context)
    console.print(f"[green]✓ graph recalibrated — {updated['status']}, "
                  f"confidence {hyp['confidence']}% → {updated['confidence']}%[/]")


def _report() -> None:
    with console.status("[dim]running all engines (~30s)…[/]"):
        cognee_client.wait_for_processing(timeout_s=120)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as pool:
            contra = pool.submit(engines.contradiction_engine)
            proj = pool.submit(engines.future_self_simulator)
            q = pool.submit(engines.open_question)
            scores = engines.consistency_scorer()
            contra, proj, q = contra.result(), proj.result(), q.result()
    console.print(Panel(Markdown(scores), title="goal consistency", title_align="left", border_style="dim"))
    console.print(Panel(Markdown(contra), title="contradictions", title_align="left", border_style="red"))
    console.print(Panel(Markdown(proj), title="your next year, at this pace", title_align="left", border_style="dim"))
    console.print(Panel(f"[italic]{q}[/]", title="the question you're avoiding", title_align="left", border_style="yellow"))
    for hyp in engines.pending_hypotheses():
        _ask_hypothesis(hyp)


HELP = """[bold]legacy[/] — a mentor that remembers

Just type. Statements are remembered; questions are answered from memory.

  [cyan]/report[/]    the full report: scores, contradictions, projection
  [cyan]/observe[/]   re-scan this workspace (git) into memory
  [cyan]/ask …[/]     force a question   [cyan]/remember …[/]  force a memory
  [cyan]/bye[/]       leave (Legacy keeps remembering)"""


def main() -> None:
    console.print()
    console.print("[bold]Legacy[/][green].[/] [dim italic]are you becoming who you said you wanted to be?[/]")

    # 1. Ambient perception: look at where the user is working.
    with console.status("[dim]looking around…[/]"):
        seen = observer.look(Path.cwd())
    if seen:
        style = "green" if seen["new"] else "dim"
        console.print(f"[{style}]◉ observed: {seen['summary']}[/]")

    # 2. Session priming: what does the graph already know?
    with console.status("[dim]remembering you…[/]"):
        primer = cognee_client.recall(
            "In 3 short lines: what is this user currently working on, which goals "
            "are healthy, and which are being neglected? Be specific and terse.",
            system_prompt="You are Legacy priming a terminal session. Max 3 lines, no preamble.",
        )
    console.print(Panel(Markdown(primer), title="legacy remembers", title_align="left", border_style="dim"))

    # 3. Agent initiative: if Legacy has been holding a question, ask it now.
    for hyp in engines.pending_hypotheses():
        _ask_hypothesis(hyp)

    console.print("[dim]type freely — /help for commands[/]\n")

    # 4. The loop.
    while True:
        try:
            line = console.input("[bold cyan]you ›[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            line = "/bye"
        if not line:
            continue
        if line in ("/bye", "/exit", "/quit"):
            console.print("[dim]the house always remembers.[/]")
            return
        if line == "/help":
            console.print(Panel(HELP, border_style="dim"))
        elif line == "/report":
            _report()
        elif line == "/observe":
            with console.status("[dim]looking around…[/]"):
                seen = observer.look(Path.cwd())
            console.print(f"[green]◉ {seen['summary'] if seen else 'not a git repository — nothing to observe'}[/]")
        elif line.startswith("/ask "):
            _answer(line[5:])
        elif line.startswith("/remember "):
            _remember(line[10:])
        elif line.startswith("/"):
            console.print("[dim]unknown command — /help[/]")
        else:
            (_remember if _route(line) == "R" else _answer)(line)


def one_shot(argv: list[str]) -> None:
    """Non-interactive mode for scripts and other agents (e.g. Claude Code):
        legacy ask <question>      answer from graph memory, then exit
        legacy remember <text>     distill + store, then exit
        legacy observe             observe cwd workspace, then exit
        legacy report              full report, then exit
    """
    cmd, rest = argv[0], " ".join(argv[1:])
    if cmd == "ask" and rest:
        _answer(rest)
    elif cmd == "remember" and rest:
        _remember(rest)
    elif cmd == "observe":
        seen = observer.look(Path.cwd())
        console.print(seen["summary"] if seen else "not a git repository — nothing to observe")
    elif cmd == "report":
        _report()
    else:
        console.print("usage: legacy [ask <q> | remember <text> | observe | report]")
        sys.exit(1)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            one_shot(sys.argv[1:])
        else:
            main()
    except KeyboardInterrupt:
        sys.exit(0)
