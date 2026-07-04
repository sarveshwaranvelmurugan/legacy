# LEGACY — Master Project Document
### WeMakeDevs × Cognee Hackathon | Jun 29 – Jul 5, 2026
### Built by: Shanks | Prize Target: $10,000 + MacBook + Job Interview at Cognee

---

## TABLE OF CONTENTS

1. [The Problem Statement](#1-the-problem-statement)
2. [Our Solution — What is Legacy?](#2-our-solution--what-is-legacy)
3. [Why Legacy Wins](#3-why-legacy-wins)
4. [Full System Architecture](#4-full-system-architecture)
5. [The Data Model](#5-the-data-model)
6. [The Compact Memory Engine (CME)](#6-the-compact-memory-engine-cme)
7. [The Four Cognee API Layers](#7-the-four-cognee-api-layers)
8. [The Five Reasoning Engines](#8-the-five-reasoning-engines)
9. [Complete User Flow](#9-complete-user-flow)
10. [The 30-Day Report](#10-the-30-day-report)
11. [Tech Stack](#11-tech-stack)
12. [6-Day Build Plan](#12-6-day-build-plan)
13. [The Demo Script](#13-the-demo-script)
14. [Judge Q&A — Prepared Answers](#14-judge-qa--prepared-answers)
15. [The Submission Narrative](#15-the-submission-narrative)

---

## 1. THE PROBLEM STATEMENT

### The Question No AI Can Currently Answer

> *"Based on everything I've done, learned, decided, and failed at — what should I do next month to become who I want to be in 5 years?"*

Every AI resets. Every session starts at zero.

A student grinding through internships, hackathons, rejections, skill gaps, and growing ambitions is generating an incredibly rich signal about their trajectory — **and every single AI session throws it away.**

### The Deeper Problem

Humans have two sets of goals that almost never match:

- **Stated goals** — what they say they want
- **Revealed preferences** — what their actual behavior shows they are optimizing for

No tool on earth currently bridges this gap with persistent memory and evidence-based reasoning.

A student says: *"I want to get into AI research."*
Their 90 days of behavior shows: 14 hackathons, 11 new frameworks, 0 papers read, 0 experiments replicated.

That gap is not a character flaw. It is **unmeasured data.** And unmeasured data cannot be acted on.

### The Scale of This Problem

- Every first-generation college student navigating their career without an alumni network
- Every self-taught developer who lacks a mentor who remembers their journey
- Every ambitious person whose growth is invisible — even to themselves

**AI assistants for personal growth have the worst memory problem in all of AI.** Cognee fixes exactly that. Legacy is the application that proves it.

---

## 2. OUR SOLUTION — WHAT IS LEGACY?

**Legacy is a persistent life-trajectory agent.**

It doesn't store your conversations. It builds a **living knowledge graph of your evolving self** — your goals, decisions, actions, evidence, failures, claims, and contradictions — and uses Cognee's full memory lifecycle to answer the question that no tool currently answers:

> *"Am I becoming who I said I wanted to be?"*

### What Makes Legacy Different from Every Other "Memory AI"

| Every other memory AI | Legacy |
|---|---|
| Stores facts about you | Tracks the graph of your becoming |
| "You told me you want to work in AI" | "3 months ago: ML research. 2 months ago: MLOps pivot. Last week: product role applied. Contradiction detected." |
| Remembers preferences | Tracks identity drift across time |
| Answers questions | Asks the questions you're avoiding |
| Gets data from you | Verifies data against external evidence |
| Treats all memories as equal | Assigns confidence scores to every node |
| Presents conclusions as facts | Forms hypotheses and asks for confirmation |

### The Core Insight

> **Legacy is the first AI that doesn't just remember what you said — it remembers who you're trying to become, and tells you honestly when you're drifting away from that person.**

---

## 3. WHY LEGACY WINS

### Against Every Judging Criterion

| Criterion | Why Legacy Scores Maximum |
|---|---|
| **Potential Impact** | Every ambitious person without a mentor. Global, emotionally resonant, practically useful. |
| **Creativity & Innovation** | Nobody has built behavioral inference + epistemic confidence on top of a graph memory layer. Zero prior art. |
| **Technical Excellence** | CME distillation layer, multi-hop graph traversal, confidence-weighted nodes, human-in-the-loop calibration. |
| **Best Use of Cognee** | All four APIs used deeply and non-trivially: remember, recall, improve/memify, forget. |
| **User Experience** | One daily reflection → system gets smarter. Contradiction report is actionable, not abstract. |
| **Presentation Quality** | Live demo with real contradictions surfaced in real time. One-line kicker. Story-first narrative. |

### The Unfair Advantage

This project is built by someone who has personally lived the problem — a first-generation engineering student from a Tier-2 city, who built a Springer-published sign language paper, won national hackathons, and navigated every career decision without a network. **Legacy is the mentor that student never had.**

That story, told in the presentation, is worth more than any feature.

---

## 4. FULL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INPUT LAYER                           │
│        Text reflections · Check-ins · GitHub sync · Manual logs    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              COMPACT MEMORY ENGINE (CME)                            │
│                                                                     │
│  ┌─────────────┐   ┌──────────────────┐   ┌───────────────────┐   │
│  │  Extractor  │ → │  Deduplicator    │ → │  Confidence       │   │
│  │             │   │                  │   │  Scorer           │   │
│  │ Goals       │   │ Merge near-      │   │                   │   │
│  │ Actions     │   │ identical nodes  │   │ 0.0 – 1.0         │   │
│  │ Claims      │   │                  │   │ per node          │   │
│  │ Evidence    │   │                  │   │                   │   │
│  │ Contradic.  │   │                  │   │                   │   │
│  └─────────────┘   └──────────────────┘   └───────────────────┘   │
│                                                                     │
│  Raw input (500 words) → Structured nodes (2-6 max)                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ compact node strings
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COGNEE MEMORY LAYER                              │
│              Hybrid Graph-Vector Knowledge Store                    │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────┐ │
│  │ remember()   │  │  recall()    │  │  improve()   │  │forget()│ │
│  │              │  │              │  │  /memify     │  │        │ │
│  │ Ingest CME   │  │ Session      │  │ Weekly graph │  │ Prune  │ │
│  │ nodes into   │  │ priming +    │  │ enrichment + │  │ closed │ │
│  │ graph        │  │ engine       │  │ confidence   │  │ goals  │ │
│  │              │  │ queries      │  │ recalib.     │  │        │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────┘ │
│                                                                     │
│  Knowledge Graph:                                                   │
│  GOAL nodes · ACTION edges · EVIDENCE nodes · CLAIM nodes          │
│  CONTRADICTION flags · HYPOTHESIS nodes · Confidence weights        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FIVE REASONING ENGINES                            │
│                                                                     │
│  ┌──────────────────┐   ┌────────────────────┐                     │
│  │ 1. Contradiction  │   │ 2. Goal Consistency │                    │
│  │    Engine         │   │    Scorer           │                    │
│  │                   │   │                     │                    │
│  │ High certainty    │   │ High certainty       │                    │
│  │ Claim vs evidence │   │ Actions / expected  │                    │
│  │ 14+ day gap       │   │ = 0–100% score      │                    │
│  └──────────────────┘   └────────────────────┘                     │
│                                                                     │
│  ┌──────────────────┐   ┌────────────────────┐                     │
│  │ 3. Behavioral     │   │ 4. Future Self      │                    │
│  │    Inference      │   │    Simulator        │                    │
│  │    Engine (BIE)   │   │                     │                    │
│  │                   │   │ Low-medium cert.    │                    │
│  │ Medium certainty  │   │ Project current     │                    │
│  │ Pattern → Hypoth. │   │ trend → 1yr horizon │                    │
│  │ → User confirms   │   │                     │                    │
│  └──────────────────┘   └────────────────────┘                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │             5. CONFIDENCE ENGINE (cross-cutting)             │  │
│  │  Every insight from every engine gets a confidence score     │  │
│  │  + evidence count + recency weight + verification status     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                                 │
│                                                                     │
│         THE 30-DAY CONTRADICTION & GROWTH REPORT                   │
│                                                                     │
│  · Consistency scores per goal (with % and verdict)                │
│  · Unverified claims ranked by days-without-evidence               │
│  · Behavioral inference hypotheses (awaiting confirmation)         │
│  · 1-year prediction based on current trajectory                   │
│  · 1 open question Legacy wants to ask you                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. THE DATA MODEL

### Node Types

```
GOAL
├── title: str
├── domain: str           (AI, DSA, research, career, health...)
├── deadline: date | null
├── committed_on: date
├── status: OPEN | CLOSED | ABANDONED
└── verified: bool

ACTION
├── description: str
├── linked_goal: str
├── timestamp: date
└── confidence: float     (0.0 – 1.0)

CLAIM
├── text: str             ("I am consistently practicing DSA")
├── confidence: float     (starts at 0.3, rises with evidence)
└── verified: bool

EVIDENCE
├── source: github | leetcode | certificate | hackathon | manual
├── value: str
├── linked_goal: str
├── verified: bool        (true = pulled from external API)
└── timestamp: date

CONTRADICTION
├── claim_text: str
├── counter_evidence: str
├── days_unverified: int
└── severity: low | medium | high

HYPOTHESIS                (generated by Behavioral Inference Engine)
├── pattern_text: str
├── supporting_nodes: int
├── confidence: float
├── status: PENDING | CONFIRMED | REJECTED | PARTIAL
└── user_response: str | null
```

### Edge Types

```
(User) -[COMMITTED_TO]-> (Goal)
(User) -[PERFORMED]-> (Action)
(Action) -[LINKED_TO]-> (Goal)
(User) -[CLAIMS]-> (Claim)
(Evidence) -[SUPPORTS]-> (Claim)
(Evidence) -[SUPPORTS]-> (Goal)
(Contradiction) -[FLAGS]-> (Claim)
(Hypothesis) -[INFERRED_FROM]-> (Action) x N
(Hypothesis) -[CONTRADICTS_STATED]-> (Goal)
```

---

## 6. THE COMPACT MEMORY ENGINE (CME)

### Why It Exists

Raw conversation text dumped into Cognee = bloated graph, slow traversal, noisy recalls.

The CME sits between the user and Cognee. It reads raw input and returns only 2–6 structured nodes. **Cognee never sees noise.**

A 500-word reflection → 3 nodes. A 10-word check-in → 1 node.

### The CME Pipeline

```
User Input (raw text)
        │
        ▼
Claude API call (CME_SYSTEM_PROMPT)
        │
        ▼
JSON: { "nodes": [...] }        ← max 6 nodes, typed, confidence-scored
        │
        ▼
format_node_for_cognee()        ← converts to dense memory strings
        │
        ▼
cognee.remember(compact_string) ← only signal, no noise
```

### What the CME Extracts vs Ignores

| Raw Input Contains | CME Does |
|---|---|
| "So like I've been thinking about DSA lately..." | Creates 0 nodes (vague) |
| "I completed 2 LeetCode problems today, both medium" | Creates 1 ACTION node, confidence 0.8 |
| "I want to be a researcher one day" | Creates 1 CLAIM node, confidence 0.3 (no evidence) |
| "I submitted a PR to Cognee today" | Creates 1 EVIDENCE node, source=github, verified=false |
| "I said I'd do DSA daily but I haven't opened it in 3 weeks" | Creates 1 CONTRADICTION node, severity=high |

### Memory String Format (what goes into Cognee)

```
[GOAL] user:shanks committed_to='Learn System Design' domain=engineering deadline=unset status=OPEN verified=false

[ACTION] user:shanks did='Completed 2 LeetCode mediums' linked_goal='DSA preparation' confidence=0.8

[CLAIM] user:shanks claims='I am consistent with DSA practice' confidence=0.3 verified=false

[EVIDENCE] user:shanks source=github value='commit: Add graph traversal module' repo=legacy verified=true

[CONTRADICTION] user:shanks claim='consistent DSA practice' counter='0 actions in 21 days' severity=high
```

**These strings are small, typed, graph-traversal-friendly. Every node is actionable.**

---

## 7. THE FOUR COGNEE API LAYERS

### `cognee.remember()` — Intake
- Called after every CME run
- Ingests compact node strings into the user's personal knowledge graph
- Dataset namespaced per user: `dataset_name=f"user_{user_id}"`
- Never called with raw text — CME always runs first

### `cognee.recall()` — Query Engine
- Called at session start to prime the context: *"What are this user's open goals and recent contradictions?"*
- Called by each reasoning engine with typed queries: `"[CLAIM] user:X verified=false"`
- Cognee's hybrid routing handles semantic + graph traversal automatically

### `cognee.improve()` / memify — Self-Correcting Memory
- Called after every user confirmation/rejection of a Behavioral Inference hypothesis
- Recalibrates confidence weights across the node cluster
- Also runs weekly in background: prunes low-confidence stale nodes, strengthens frequently-verified ones
- **This is how Legacy gets more accurate the more you push back on it**

### `cognee.forget()` — Conscious Closure
- Called when user marks a goal as consciously abandoned
- Does NOT delete — records a CLOSED node with reason and date
- The graph remembers that you moved on, and why
- Also used for privacy wipe: full dataset deletion on request

---

## 8. THE FIVE REASONING ENGINES

### Engine 1: Contradiction Engine
**Certainty: High (85–98%) | Cognee API: `recall()` multi-hop**

Finds CLAIM nodes with no supporting EVIDENCE nodes, age > 14 days.

```
Query: [CLAIM] user:X verified=false
Query: [EVIDENCE] user:X
Cross-reference → find claims with zero evidence edges

Output:
⚠ CONTRADICTION (HIGH) — 98% confidence
Claim: "I am consistently practicing DSA"
Evidence: 0 LeetCode submissions, 0 action nodes in 21 days
Supporting data: 17 nodes
Days unverified: 21
```

### Engine 2: Goal Consistency Scorer
**Certainty: High | Cognee API: `recall()` + arithmetic**

Counts action nodes linked to each goal vs expected cadence.

```
Formula:
Consistency Score = (actions_taken / expected_actions) × 100

Example:
Goal: Learn System Design
Committed: 30 days ago
Actions taken: 3
Expected (weekly cadence): 12
Score: 25% ⚠ STALLED
```

Verdicts: `ON_TRACK (>75%) | DRIFTING (40-75%) | STALLED (<40%)`

### Engine 3: Behavioral Inference Engine (BIE)
**Certainty: Medium (60–80%) | Cognee API: `recall()` + `improve()` on confirm**

Detects the gap between stated goals and revealed behavioral preferences. **Does NOT present conclusions as facts. Forms hypotheses. Asks for confirmation. Updates graph on response.**

```
Workflow:
1. recall() all ACTION nodes for user (last 90 days)
2. Cluster by domain/type
3. Detect emergent pattern
4. Generate hypothesis with confidence score
5. Surface to user as question, not statement
6. On user response → improve() recalibrates graph

Output:
📊 BEHAVIORAL INFERENCE — 71% confidence
Based on 8 nodes. Needs confirmation.

Observed (last 60 days):
• 14 hackathon-related actions
• 9 LinkedIn / public-facing posts
• 0 research paper reading sessions
• 0 experiment replication sessions

Hypothesis:
"Your recent behavior appears more aligned with engineering
and product building than academic research."

Is this:
○ Accurate
○ Partially accurate — [add context]
○ Missing important context
```

If user says "partially accurate — I've been reading papers offline" → Legacy creates new ACTION nodes, recalibrates confidence, hypothesis status → PARTIAL.

### Engine 4: Future Self Simulator
**Certainty: Low-Medium | Cognee API: All of the above**

Aggregates all goal consistency scores and projects a 1-year trajectory.

```
Input: scored_goals[] from Engine 2 + domain clusters from Engine 3

Output:
At your current pace (1-year projection):

✅ Likely to complete: DSA preparation, Hackathon portfolio
⚠ Likely to stall: Research paper submission, System Design
🚀 Accelerating domains: Applied AI, Public building
📉 Stagnant domains: Interview preparation, Open source

Honest projection:
"You are on track to become a strong applied AI engineer with
hackathon wins as primary proof-of-work. Your research goals will
slip unless you tie them to a submission deadline in the next 30 days.
Interview prep is the biggest gap between your current skills and
your placement outcomes."

Highest-leverage action right now:
"Block 1 hour daily for mock interviews. Log each session."
```

### Engine 5: Confidence Engine (Cross-Cutting)
**Runs across all four engines. Every insight gets a score.**

```
Every output includes:

Confidence: 98%
Reason: 17 supporting nodes, external evidence verified
Status: High certainty — actionable

─────────────────────────────────

Confidence: 71%
Reason: 8 supporting nodes, no external evidence
Status: Medium certainty — needs user confirmation

─────────────────────────────────

Confidence: 43%
Reason: 3 supporting nodes, conflicting signals
Status: Low certainty — treat as hypothesis only
```

**Why this matters:** Legacy never claims to be omniscient. It exposes its own uncertainty. This is what separates a scientific instrument from a party trick.

---

## 9. COMPLETE USER FLOW

```
DAY 1 — New user onboards
│
├── Sets 3–7 goals
├── CME creates GOAL nodes → cognee.remember()
└── Graph initialized

DAILY — User does a 2-min reflection
│
├── Speaks or types what they did today
├── CME runs → extracts ACTION / EVIDENCE / CLAIM nodes
├── cognee.remember() ingests compact nodes
└── Session ends. Takes 2 minutes.

WEEKLY — Legacy runs background enrichment
│
├── GitHub sync → EVIDENCE nodes auto-created
├── cognee.improve() → prune stale, strengthen verified
├── Consistency scores recomputed for all goals
└── BIE runs → new hypotheses generated if pattern threshold met

ON DEMAND — User requests 30-Day Report
│
├── cognee.recall() — pull all nodes
├── Contradiction Engine runs → ranked contradiction list
├── Goal Consistency Scorer → score per goal
├── BIE → pending hypotheses surfaced
├── Future Self Simulator → 1-year projection
└── Full report rendered

ON HYPOTHESIS PROMPT — User responds to BIE
│
├── Confirmed → improve() strengthens pattern cluster
├── Rejected → improve() weakens pattern, creates counter-node
└── Partial → improve() recalibrates + prompts for missing context

ON GOAL CLOSURE — User marks goal complete or abandoned
│
├── cognee.forget() → CLOSED node with date + reason
└── Graph records the transition, not just the deletion
```

---

## 10. THE 30-DAY REPORT

This is the demo centerpiece. This is what you open on stage.

```
╔══════════════════════════════════════════════════════════════╗
║              LEGACY — YOUR 30-DAY REPORT                    ║
║              Generated: July 5, 2026                        ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GOAL CONSISTENCY SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DSA Preparation          ████████░░  78%  ON TRACK
   Actions: 9/12 expected

⚠  System Design            ███░░░░░░░  25%  STALLED
   Actions: 3/12 expected

⚠  Interview Preparation    ██░░░░░░░░  17%  STALLED
   Actions: 2/12 expected

🚀 Hackathon Portfolio      ██████████ 100%  ON TRACK
   Actions: 6/6 expected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNVERIFIED CLAIMS (CONTRADICTIONS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 HIGH — 98% confidence — 17 nodes
   Claim: "I am consistently practicing system design"
   Evidence: 0 verified actions in 21 days
   Unverified for: 21 days

🟠 MEDIUM — 84% confidence — 9 nodes
   Claim: "I'm preparing for ServiceNow campus drive"
   Evidence: 0 interview prep action nodes
   Unverified for: 14 days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEHAVIORAL INFERENCE (AWAITING YOUR RESPONSE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 71% confidence — 8 nodes — needs confirmation

Pattern observed (last 60 days):
  • 14 hackathon-related actions
  • 0 research paper sessions

Hypothesis:
  "Your behavior appears more aligned with product building
   than academic research. Is this accurate?"

  [ Accurate ]  [ Partially ]  [ Missing context ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1-YEAR PROJECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

At your current pace:

"You will likely complete your DSA and hackathon goals.
System design and interview preparation will stall unless
you act in the next 2 weeks. Your biggest risk is arriving
at campus placement season technically strong but
interview-unprepared."

Highest leverage action:
→ "Schedule 1 mock interview this week. Log it here."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEGACY'S OPEN QUESTION FOR YOU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  "You've mentioned 'research' as a goal 7 times in 60 days.
   You've taken 0 research-related actions.
   Is 'research' a goal or an identity label you're not ready
   to act on yet? It's worth knowing the difference."
```

---

## 11. TECH STACK

| Layer | Tool | Why |
|---|---|---|
| Memory core | Cognee Cloud (free with COGNEE-35) | The whole point |
| Graph store | Kuzu (Cognee default) | Fast multi-hop traversal |
| Vector store | LanceDB (Cognee default) | Semantic recall |
| LLM | Claude Sonnet 4.6 via Cognee config | CME + engine reasoning |
| Backend | FastAPI (Python) | Your existing stack |
| Frontend | React + Tailwind | Clean, minimal, journal-like |
| Evidence adapter | GitHub REST API | Verified external evidence |
| CME | Anthropic Python SDK | Distillation layer |

### What We Are NOT Building (Scope Cut — Smart)
- ❌ Voice input / Whisper
- ❌ Complex dashboards with charts
- ❌ LeetCode API integration (v2 feature)
- ❌ Fancy goal-closing animations
- ❌ Mobile app

**A killer demo beats 20 unfinished features. Every time.**

---

## 12. 6-DAY BUILD PLAN

### Day 1 — June 29: Foundation
- [ ] Cognee Cloud account setup (code: COGNEE-35)
- [ ] Configure Anthropic as LLM provider in Cognee `.env`
- [ ] Build CME prompt + test with 5 sample reflections
- [ ] Wire `cognee.remember()` with compact node strings
- [ ] Verify nodes appear in Cognee graph explorer

**End of Day 1 checkpoint:** Can type a reflection, CME produces nodes, nodes live in Cognee graph.

### Day 2 — June 30: Recall + Scoring
- [ ] Build `cognee.recall()` session primer
- [ ] Build Goal Consistency Scorer
- [ ] Test: create 2 goals, log actions over fake dates, generate score
- [ ] Basic FastAPI endpoints: `POST /reflect`, `GET /goals`

**End of Day 2 checkpoint:** Consistency score generates correctly from graph data.

### Day 3 — July 1: Contradiction + Improvement
- [ ] Build Contradiction Engine (recall + cross-reference)
- [ ] Build `cognee.improve()` trigger on hypothesis confirmation
- [ ] Build hypothesis confirmation endpoint: `POST /hypothesis/respond`
- [ ] Test full BIE loop: pattern → hypothesis → user says "partially" → graph updates

**End of Day 3 checkpoint:** Contradiction surfaces. Confirmation updates graph. Memory is self-correcting.

### Day 4 — July 2: Future Self + GitHub Evidence
- [ ] Build Future Self Simulator
- [ ] Build GitHub evidence adapter (last 10 push events → EVIDENCE nodes)
- [ ] Build `cognee.forget()` goal closure flow
- [ ] Confidence Engine wrapper across all four engines

**End of Day 4 checkpoint:** Full pipeline runs end-to-end on real data.

### Day 5 — July 3: Frontend + UX
- [ ] React app: 4 screens
  - Screen 1: Daily reflection input
  - Screen 2: Goal dashboard with consistency scores
  - Screen 3: Contradiction list with severity badges
  - Screen 4: 30-Day Report view
- [ ] Wire all FastAPI endpoints to frontend
- [ ] Hypothesis confirmation UI (3-button response)

**End of Day 5 checkpoint:** Full demo-ready product. Someone can use it without explanation.

### Day 6 — July 4-5: Ship It
- [ ] Seed demo data (simulate 30 days of a real user's journey)
- [ ] Record 3-minute demo video (see Demo Script below)
- [ ] Write README with architecture diagram, setup steps, demo link
- [ ] Declare AI tool usage (Claude used for development — required by rules)
- [ ] Submit

---

## 13. THE DEMO SCRIPT

**Total: 3 minutes. Zero filler.**

---

**[0:00 – 0:30] The Problem**

> "Every AI resets. Every session starts from zero. You've told ChatGPT your goals fifty times and it doesn't remember any of them. This is Legacy. It doesn't just remember what you said — it tracks who you're trying to become."

---

**[0:30 – 1:00] The Input**

> "Every day, a user does a 2-minute reflection. Let me show you what happens under the hood."

*Type: "I've been meaning to study system design but haven't started. I did two hackathons this week though."*

> "Legacy's Compact Memory Engine distills this into structured nodes before Cognee ingests it. Not raw text — typed, confidence-scored, graph-ready nodes. Watch."

*Show CME output: 1 CONTRADICTION node, 1 ACTION node.*

---

**[1:00 – 2:00] The 30-Day Report**

> "After 30 days of reflections and GitHub sync, here's what Legacy generates."

*Open the report.*

> "Consistency scores per goal. System Design: 25%. Stalled. Unverified claims ranked by severity. And look at this — a behavioral inference hypothesis at 71% confidence. Legacy noticed that this user has 14 hackathon actions and zero research sessions, and it's asking: 'Does this reflect your actual priorities?' — not telling. Asking."

*Click "Partially accurate — I've been reading papers offline."*

> "The user pushes back. Legacy updates. The graph recalibrates. Legacy gets more accurate the more you correct it. That's Cognee's improve() API doing active memory calibration."

---

**[2:00 – 2:45] The Prediction**

> "Finally — the question no other AI answers."

*Show Future Self Simulator output.*

> "'At your current pace, you will complete DSA and hackathon goals. Interview preparation will stall. Your biggest risk: arriving at placement season technically strong but interview-unprepared.' And one action. One. The highest-leverage thing to do right now."

---

**[2:45 – 3:00] The Kicker**

> "Every student navigating their career without a mentor is generating data about their trajectory that nobody is reading — including them. Legacy reads it. Cognee remembers it. And every week, it asks the question that matters: are you becoming who you said you wanted to be?"

---

## 14. JUDGE Q&A — PREPARED ANSWERS

**Q: How do you populate evidence nodes? Can users fake them?**

> "Legacy is source-agnostic. Evidence can be manual reflections or external systems. For this hackathon, we've implemented GitHub as our first verified evidence source — every commit automatically becomes a verified EVIDENCE node linked to relevant goals. The architecture supports LeetCode, Notion, Calendar, and LMS integrations as v2 features. Critically, unverified manual evidence gets a confidence of 0.3, while GitHub-verified evidence gets 0.9. The graph knows the difference."

**Q: What if the data is sparse or the user doesn't log consistently?**

> "Sparse data produces lower confidence scores, not wrong answers. The Confidence Engine surfaces uncertainty explicitly. A behavioral inference from 3 nodes says 43% confidence — treat as hypothesis only. An inference from 17 nodes says 98% — actionable. The system is calibrated to be honest about what it doesn't know. That's by design."

**Q: Why not just use a journal app?**

> "A journal stores text. Legacy builds a typed, weighted, cross-session knowledge graph where every node has a confidence score, every claim is checked against evidence, and contradictions surface automatically. A journal can't tell you that you've claimed 'consistent DSA practice' for 21 days with zero supporting evidence. Legacy can — because Cognee's graph traversal finds the connection between a CLAIM node and the absence of ACTION nodes linked to it."

**Q: How does this use Cognee differently than a basic chatbot with memory?**

> "A chatbot with memory stores conversation history. Legacy uses Cognee's hybrid graph-vector layer for typed multi-hop reasoning. The Contradiction Engine traverses CLAIM → EVIDENCE edge absence. The BIE clusters ACTION nodes by domain across 90 days. The Confidence Engine weights nodes by verification status and recency. None of this is possible with flat conversation storage. This is Cognee's graph layer operating at its architectural ceiling."

**Q: What's the business model / who pays for this?**

> "First-generation college students navigating their careers without alumni networks. EdTech platforms. Career coaching services. University career centers. The free tier works for individual students. Institutional licensing works for colleges. The data privacy model is fully self-hosted via Cognee's open-source stack — no user data leaves their instance."

---

## 15. THE SUBMISSION NARRATIVE

### One-Line Description
> *Legacy is a persistent life-trajectory agent that builds a knowledge graph of your evolving self and tells you, honestly, when you're drifting away from who you said you wanted to be.*

### The Pitch (for README and submission form)
> Every AI resets. Every session starts from zero. A student grinding through internships, rejections, and skill gaps is generating rich signal about their trajectory — and every tool throws it away.
>
> Legacy uses Cognee's full memory lifecycle to build a persistent, evidence-based knowledge graph of a user's goals, actions, claims, and contradictions. It doesn't store chat history — it builds a typed graph where GOAL nodes connect to ACTION edges, CLAIM nodes are verified against EVIDENCE nodes, and contradictions surface automatically via multi-hop graph traversal.
>
> The result: a 30-day report that tells you your goal consistency scores, your unverified claims ranked by severity, behavioral inference hypotheses formed from your action patterns, and an honest 1-year projection based on your current trajectory.
>
> Legacy gets more accurate the more you push back on it — every user confirmation or rejection of a hypothesis triggers Cognee's improve() API to recalibrate confidence weights across the node cluster. Memory that learns from being corrected.
>
> This is the mentor that every first-generation student, every self-taught developer, every ambitious person without a network — never had.

### AI Tools Declaration (Required)
> Claude (Anthropic) was used as a development assistant throughout this project. All architecture decisions, system design, and engineering work are original. AI use is disclosed per hackathon rules.

---

## APPENDIX: COGNEE API USAGE SUMMARY

| API | Where Used | How Often |
|---|---|---|
| `cognee.remember()` | After every CME run | Every reflection session |
| `cognee.recall()` | Session primer, all 5 engines | Multiple times per report |
| `cognee.improve()` | After BIE confirmation, weekly enrichment | On user response + weekly cron |
| `cognee.forget()` | Goal closure, privacy wipe | On user request |

**All four APIs used. Deeply, not superficially. This is the judging criterion.**

---

*Document version: 1.0 | Last updated: June 25, 2026*
*Project: Legacy | Hackathon: WeMakeDevs × Cognee | Team: Shanks*
*Target: $10,000 + MacBook Pro + Job Interview at Cognee*

---

> "The house always remembers. Now, so will you."
