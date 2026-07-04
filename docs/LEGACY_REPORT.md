# Legacy — Complete Project Report

**The Hangover Part AI: Where's My Context? — WeMakeDevs × Cognee Hackathon (June 29 – July 5, 2026)**

---

## Executive Summary

Legacy is a persistent-memory AI agent: chat with it like ChatGPT, and unlike every
other AI, it still knows you tomorrow — your preferences, your projects, your work
patterns, across every session and every tool you use. It builds a living knowledge
graph of you on Cognee, gathers *verified evidence* of what you actually do (git
history, LeetCode solves, coding-session transcripts — all opt-in), and on top of
that memory delivers what no chatbot can: honest insight into whether your behavior
matches your intentions, and a self-improvement game whose completion can only be
*proven*, never faked.

Legacy runs as one memory with five faces: a web app, a terminal agent, an MCP
server (native tools inside Claude Code, Cursor, Claude Desktop), an installable
agent skill, and automatic session hooks. The commands you teach your coding agent
today become knowledge a new teammate can query next month. Total inference cost of
the entire system in operation: fractions of a cent per interaction.

One line: **every AI remembers what you say; Legacy checks what you actually did —
and it's one memory shared by every AI you use.**

---

## 1. Introduction — the problem

Large language models are structurally amnesiac. Every session starts at zero: the
assistant that helped you architect a project yesterday cannot recall it today; the
preferences you explained fifty times evaporate on every "New chat." The industry's
patch — stuffing conversation history into prompts — is expensive, unscalable, and
shallow: it stores *what was said*, not *what is true about you*.

The deeper problem is trust. A memory that only stores your claims learns a
flattering fiction. People say "I practice DSA consistently" and behave otherwise;
an assistant that remembers only the claim is a yes-man with a diary. A useful
personal AI needs memory that distinguishes **what you said** from **what you did**
— and evidence for the difference.

Legacy addresses both: persistent, structured, cross-tool memory (the hackathon's
theme), and a zero-trust evidence layer on top of it (our differentiation).

## 2. What Legacy is

Legacy is **the AI that actually knows you**:

- **Talk to it** — a real conversational assistant (analysis, advice, anything)
  that reaches into your memory when your past matters and quietly remembers the
  durable parts of every exchange. Tell it about your new bike today; ask "what's
  my favourite bike?" in a fresh session next week — it knows, with the date.
- **Work near it** — it ambiently observes your git repos, distills the workflow
  knowledge from your coding-agent sessions, and syncs your public GitHub and
  LeetCode activity as verified evidence. All opt-in; off means off.
- **Let it notice** — because it holds both your stated goals and your verified
  behavior, it can compute consistency, surface contradictions with dates and
  confidence, hypothesize about your real priorities (and ask, never tell), and
  project your trajectory a year forward.
- **Play it** — daily quests generated from your own graph, completable only by
  proof: a real commit, a real solve, or a genuine explanation judged from
  conversation memory.

## 3. Architecture

```
 conversations · reflections · git observations · session transcripts · GitHub/LeetCode
        │
        ▼
 COMPACT MEMORY ENGINE (Claude Haiku 4.5)
 raw input → 0-6 typed, dated, confidence-scored nodes; noise discarded
        │
        ▼  cognee add_text + cognify  ("remember")
 ┌─────────────────────────────────────────────────────────┐
 │            COGNEE CLOUD MEMORY LAYER                    │
 │      hybrid graph-vector store · one lifelong graph     │
 │  GOAL ACTION CLAIM EVIDENCE CONTRADICTION PREFERENCE    │
 │  FACT PROJECT WORKFLOW CALIBRATION  (+ typed edges)     │
 └───────────────┬─────────────────────────────────────────┘
                 │  cognee recall (GRAPH_COMPLETION, top-K)
        ┌────────┴──────────┬───────────────┬──────────────┐
        ▼                   ▼               ▼              ▼
   Conversational      Insight engines   Quest system   Profile
   engine (chat w/     (contradiction,   (generate →    ("what Legacy
   search_memory       inference, pro-   prove → level) knows about
   tool)               jection, ...)                     you")
                 ▲
   DETERMINISTIC LEDGER (local, exact) — consistency scores, alignment,
   XP/levels: arithmetic over the exact node list, reproducible on stage
```

**The key architectural split:** narrative reasoning runs on Cognee's graph
completion (semantic, multi-hop); *numbers* — consistency scores, the alignment
metric, XP and levels — are computed by plain arithmetic over a local ledger of
every ingested node. Scores you can recompute by hand; reasoning from the graph.
This also answers the hallucination question: the LLM extracts and narrates, but
it never invents a score.

**The scalability property:** recall never loads the whole memory. Retrieval is
top-K (vector + graph traversal) followed by synthesis, so the token cost of
remembering is constant whether the graph holds one month or ten years. The CME
compresses at the front door (2–6 dense nodes per interaction, never transcripts),
so the graph grows with signal, not chatter.

## 4. The memory model

Every memory is a typed, dated, confidence-scored node rendered as a dense string
before ingestion (Cognee never sees noise):

| Type | What it captures | Confidence discipline |
|---|---|---|
| GOAL | commitments ("interview-ready by August") | status OPEN/CLOSED |
| ACTION | what you actually did, dated | 0.7–0.9 |
| CLAIM | self-assessment with no proof attached | starts 0.3 |
| EVIDENCE | verifiable output (commit, solve) | 0.9 when externally verified |
| CONTRADICTION | admitted say/do gaps | severity low/med/high |
| PREFERENCE / FACT | the person: favourite bike, commute, context | 0.8, durable |
| PROJECT | a studied project: stack, architecture, patterns | from metadata only |
| WORKFLOW | how things are done: commands, rituals, conventions | distilled from sessions |
| CALIBRATION | your corrections of Legacy's hypotheses | the learning loop |

The claimed-versus-verified distinction is enforced *numerically*: a self-reported
claim enters at 0.3 confidence; a GitHub-verified commit enters at 0.9. The graph
itself knows the difference between talk and receipts.

## 5. One memory, five surfaces

1. **Web app** (React + FastAPI): Chat · Profile · Quests · Insights · Memory Graph.
2. **Terminal agent** (`./legacy`): on launch it observes your workspace, primes
   itself from memory, asks any question it has been holding, then converses.
   Full one-shot CLI: `ask, remember, observe, learn, distill, report, sources,
   connect/disconnect/sync, autocapture, setup, hook, help`.
3. **MCP server**: seven native tools (`legacy_recall, legacy_remember,
   legacy_observe, legacy_learn_project, legacy_sync_evidence,
   legacy_store_session, legacy_alignment`) available in every Claude Code /
   Cursor / Claude Desktop session. `./legacy setup` registers it.
4. **Agent skill + rules**: installable hookups for Claude Code skills,
   Cursor rules, and a generic AGENTS.md for any terminal-capable agent.
5. **Hooks**: an opt-in Claude Code SessionEnd hook that automatically observes
   the workspace and distills the session's workflow knowledge.

All five read and write the same Cognee graph. Sessions die; the person Legacy
knows doesn't. It runs today as shared memory between two machines (developer and
demo runner) — the smallest proof of the team-memory story.

## 6. The conversational engine

Chat is the front door. It answers like a capable assistant, and it holds a
`search_memory` tool over the graph with one hard rule: *it may never claim
ignorance about the user without searching first.* After every exchange, a
background pass distills the durable parts (preferences, facts, decisions,
conclusions) into memory — the chat stays fast, and a quick goodbye can't lose a
memory (exit waits for in-flight writes).

Verified behavior: a bike described in one terminal session was correctly recalled
— with purchase month and usage pattern — by a fresh web session, which then wove
the memory into a follow-up answer ("you've already had positive experience with
it, so you know it handles your route").

## 7. Ambient and evidence capture

- **Workspace observer**: reads repo, branch, commits, and dirty state from git —
  verified evidence, deduplicated per repo per day.
- **Session workflow distillation**: at session end (hook/MCP/CLI), Legacy skims
  the session for *how-things-are-done* knowledge — "lint is `make lint` from repo
  root; go tests need `config/` copied into the service folder first" — and stores
  it as WORKFLOW memory. Distillation, not transcription: commands and conventions
  only; code and secrets are never extracted.
- **Evidence sources**: GitHub (public pushes, per-commit messages) and LeetCode
  (accepted solves via public GraphQL) — each an explicit consent toggle with
  watermark deduplication. Off means off: the sync endpoint refuses.

## 8. Project knowledge

`legacy learn` deep-studies a finished project from metadata only (README,
manifests, directory tree, commit messages — never source bodies) into PROJECT
nodes: purpose, stack, architecture, features, patterns. Verified end-to-end: two
sample apps with different stacks were learned; a fresh session asked to "build a
new app following the patterns of app-a and app-b, combining both" and received
accurate per-project breakdowns plus a merged-architecture recommendation grounded
in the user's actual prior decisions.

## 9. The insight engines

- **Alignment Score (0–100)** — the headline: how closely verified behavior
  matches stated goals. Deterministic; ships with its own explanation.
- **Goal consistency** — per-area scores with the exact dated actions counted.
- **Contradiction engine** — claims with no same-domain evidence, ranked by
  days-unverified and severity, merged across repetitions, every finding dated.
- **Behavioral inference** — clusters actions versus stated goals and generates a
  *hypothesis*, presented as a question with confidence and supporting-node count.
  The user's response (accurate / partial / wrong, plus context) recalibrates the
  graph — corrections become CALIBRATION nodes and missing context becomes new
  memory. Memory that learns from being argued with.
- **Future-self projection** — an honest 1-year trajectory from current pace,
  ending in one highest-leverage action.
- **The open question** — the single largest talk-to-action gap, asked directly.

Agent initiative: after new activity accumulates, Legacy decides on its own to
generate a fresh hypothesis — it asks you; you don't ask it.

## 10. Quests — improvement as a game you can't cheat

Daily, Legacy generates three challenges from the graph: one attacking the weakest
area, one advancing the active project, one making a real interest productive
(one quest was generated from the user's bike conversation). Completion is never
a checkbox: **"Prove it"** re-syncs evidence, re-reads local git, and a strict
judge validates against today's memory — no receipt, no credit (observed live:
the judge refused a commit-quest twice until the evidence actually existed).
Completed quests write verified ACTIONs back into the graph, moving the real
scores. The character sheet shows deterministic domain levels (evidence worth
2.5× a self-report), and an animated journey chart plots cumulative verified XP
across the month. No streaks, no mercy, no cheats.

## 11. Privacy and trust design

- **Consent-first everywhere**: evidence sources and auto-capture are opt-in
  switches; disconnection is one command and takes effect immediately.
- **Distillation over transcription**: observers and session capture extract
  metadata and workflow facts; source code, file contents, and secrets are
  excluded by design.
- **Provenance**: insights cite node dates and counts; scores are recomputable.
- **The right to forget**: goals can be consciously closed with a reason (the
  graph remembers that you moved on, not just that data vanished), and full
  dataset wipe is supported by the memory layer.

## 12. Depth of Cognee usage

| Cognee capability | Where Legacy uses it |
|---|---|
| `add_text` + `cognify` | every memory write: chat distillations, reflections, observations, evidence, workflow facts, calibrations |
| `recall` (GRAPH_COMPLETION, top-K, custom system prompts) | chat's search_memory tool, all four narrative engines, profile narrative, quest chat-verification |
| `forget` | conscious goal closure; privacy wipe |
| datasets / raw-data API | deterministic ledger rebuild on fresh clones |
| graph endpoint | the in-app Memory Graph visualization (~500 nodes, 1,500 edges) |
| node sets, backdated timestamps | typed tagging; temporal reasoning (recall does day-count arithmetic over node dates) |

## 13. Engineering and verification

FastAPI backend (global exception hardening — a crash returns clean JSON, never a
hung UI), React/Vite/Tailwind frontend, Python CLI with rich, MCP over stdio.
Every feature was verified end-to-end during development, including scripted
Playwright browser sessions with console-error monitoring and screenshots;
cross-session memory, quest proof verification, transcript distillation, and the
new-teammate onboarding recall were each demonstrated against the live system.
Total Anthropic inference spend for the entire build and all testing: well under
one dollar — persistent memory is not just better UX than context-stuffing, it is
dramatically cheaper.

## 14. Future work

Consolidation ("sleep" for memory: merge duplicates, decay stale low-confidence
claims), team workspaces on Cognee's per-dataset permissions (personal vs. org
graphs — the onboarding-that-writes-itself story), additional evidence adapters
(wearables, calendars, CI systems), and richer quest arcs. None are speculative
architecture: each is an extension of interfaces that already exist in this repo.

---

*The house always remembers. Now, so do you.*
