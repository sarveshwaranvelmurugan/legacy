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

from . import cme, cognee_client, config, engines, installer, ledger, observer, project_learner, sources

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
    al = ledger.alignment()
    color = "green" if al["score"] > 75 else "yellow" if al["score"] >= 40 else "red"
    console.print(Panel(
        f"[bold {color}]{al['score']} / 100 — {al['verdict']}[/]\n[dim]{al['explanation']}[/]",
        title="alignment", title_align="left", border_style=color))
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
  [cyan]/learn[/]     deep-study this project (metadata only) into memory
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
        elif line == "/learn":
            with console.status("[dim]studying this project (metadata only)…[/]"):
                result = project_learner.learn(Path.cwd())
            console.print(f"[green]✓ learned '{result['name']}' — {result['nodes']} knowledge nodes remembered[/]")
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


USAGE = """usage: legacy <command>

  memory      ask <q> | remember <text> | observe | learn | report
  sources     sources | connect github|leetcode <username> | disconnect <source> | sync [source]
  install     setup   (wire Claude Code globally)
              hook    (wire THIS project for Cursor + AGENTS.md agents)

  no command  interactive session (observes workspace, primes, chats)"""


def _print_sources() -> None:
    s = sources.get_settings()
    for name, cfg in s.items():
        state = "[green]● connected[/]" if cfg["enabled"] and cfg["username"] else (
            "[yellow]● enabled, no username[/]" if cfg["enabled"] else "[dim]○ off[/]")
        user = f" as [bold]{cfg['username']}[/]" if cfg["username"] else ""
        console.print(f"  {name:<10} {state}{user}")


def _sync_source(name: str) -> None:
    fn = {"github": sources.sync_github, "leetcode": sources.sync_leetcode}[name]
    with console.status(f"[dim]syncing {name}…[/]"):
        r = fn()
    if r.get("error"):
        console.print(f"[red]{name}: {r['error']}[/]")
        return
    console.print(f"[green]✓ {name}: {r['synced']} verified evidence node(s) synced[/]")
    for s_ in r.get("evidence", []):
        console.print(f"  [dim]{s_[:110]}[/]")


def one_shot(argv: list[str]) -> None:
    """Non-interactive mode for scripts, other agents, and source management."""
    cmd, rest = argv[0], " ".join(argv[1:])
    if cmd == "ask" and rest:
        _answer(rest)
    elif cmd == "remember" and rest:
        _remember(rest)
    elif cmd == "learn":
        with console.status("[dim]studying this project (metadata only)…[/]"):
            result = project_learner.learn(Path.cwd())
        console.print(f"[green]✓ learned '{result['name']}' — {result['nodes']} knowledge nodes remembered[/]")
        console.print(f"  [dim]stack:[/] {result['knowledge']['stack'][:100]}")
        console.print(f"  [dim]patterns:[/] {result['knowledge']['patterns'][:100]}")
    elif cmd == "observe":
        seen = observer.look(Path.cwd())
        console.print(seen["summary"] if seen else "not a git repository — nothing to observe")
    elif cmd == "report":
        _report()
    elif cmd == "sources":
        _print_sources()
    elif cmd == "connect" and len(argv) >= 3 and argv[1] in ("github", "leetcode"):
        sources.update_settings({argv[1]: {"enabled": True, "username": argv[2]}})
        console.print(f"[green]✓ {argv[1]} connected as {argv[2]}[/] — run [bold]legacy sync {argv[1]}[/] to pull evidence")
    elif cmd == "disconnect" and len(argv) >= 2 and argv[1] in ("github", "leetcode"):
        sources.update_settings({argv[1]: {"enabled": False}})
        console.print(f"[yellow]○ {argv[1]} disconnected[/] — Legacy will not read it")
    elif cmd == "sync":
        targets = [argv[1]] if len(argv) >= 2 and argv[1] in ("github", "leetcode") else [
            n for n, c in sources.get_settings().items() if c["enabled"] and c["username"]]
        if not targets:
            console.print("[dim]no connected sources — try: legacy connect github <username>[/]")
        for t in targets:
            _sync_source(t)
    elif cmd == "setup":
        dst = installer.setup_claude_skill()
        console.print(f"[green]✓ Claude Code skill installed[/] → {dst}")
        ok, mcp_cmd = installer.setup_mcp()
        if ok:
            console.print("[green]✓ MCP server registered with Claude Code[/] — Legacy tools are now native in every session")
        else:
            console.print(f"[yellow]MCP not auto-registered[/] (is the claude CLI installed?). Register manually:\n  [dim]{mcp_cmd}[/]")
        import json as _json
        console.print("[dim]Cursor MCP (add to ~/.cursor/mcp.json):[/]")
        console.print("[dim]" + _json.dumps(installer.mcp_configs()["cursor"], indent=1) + "[/]")
        console.print("[dim]per-project wiring (Cursor rules + AGENTS.md): run [bold]legacy hook[/] inside a project.[/]")
    elif cmd == "hook":
        for f in installer.hook_project(Path.cwd()):
            console.print(f"[green]✓[/] {f}")
        console.print("[dim]this project's Cursor agent + AGENTS.md readers now know about Legacy.[/]")
    else:
        console.print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            one_shot(sys.argv[1:])
        else:
            main()
    except KeyboardInterrupt:
        sys.exit(0)
