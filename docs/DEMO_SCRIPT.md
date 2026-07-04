# Legacy — Demo Script (final product, July 5)

Two cuts from the same beats: the **3-minute video** (beats 1–6, tight) and the
**extended live demo** (all beats, ~6 min) for judges who ask for more.
SAY lines are written to be spoken verbatim; tweak to your voice.

---

## Pre-flight checklist (do ALL of this before recording)

- [ ] `git pull` · backend on :8400 · frontend on :5199 · `curl localhost:8400/health`
- [ ] Fresh clone? `cd backend && ../.venv/bin/python backfill_ledger.py`
- [ ] Connect YOUR sources: `./legacy connect github <user>` + `./legacy connect leetcode <user>` + `./legacy sync`
- [ ] Solve one easy LeetCode problem within 24h of recording (fresh receipt on camera)
- [ ] One pending hypothesis exists: `curl -X POST localhost:8400/hypothesis/generate`
- [ ] Pre-generate the report once (first gen ~30s; regenerate is faster — cut waits in edit)
- [ ] Tell Legacy something personal in chat the DAY BEFORE (e.g., your bike/hobby) so cross-session recall is real on camera
- [ ] Have vanilla ChatGPT open in a second browser window (beat 1)
- [ ] Terminal font large, app at ~110% zoom, notifications off

**Transparency line — say it once, judges respect it enormously:**
> "Full disclosure: the June history in this graph is a seeded simulation of a
> student's month. Everything I sync and do on camera — commits, solves, chat —
> is live and real."

---

## Beat 1 — The split-screen kill shot (0:00–0:20)

*Screen: ChatGPT left, Legacy Chat tab right. Type the same question into both:
"what's my favourite bike?"*

**SAY:** "Same question, two AIs. ChatGPT — an AI I've used for years — has no
idea. Legacy answers with the model, when I bought it, and what I use it for…
because I mentioned it once, in a different session, days ago. Every AI you've
ever used woke up this morning with amnesia. This one didn't."

*Note: let ChatGPT's shrug sit on screen for a full second before reading
Legacy's answer. The silence is the pitch.*

## Beat 2 — The terminal agent: it looks around (0:20–0:50)

*Screen: terminal in the project repo. Run `./legacy`.*

**SAY:** "Legacy isn't an app you visit — it lives where I work. Watch what
happens when I open it in a repo. I haven't typed anything." *(point at the
◉ observed line)* "It looked around: repo, branch, today's commits — remembered
as verified evidence, because git history doesn't lie. Then it tells me what it
already knows about me. And here — it's been holding a question for me. I don't
prompt my AI. My AI prompts me."

*(Answer the hypothesis with `p` for partial + one line of context; point at the
confidence shifting.)*

**SAY:** "I pushed back — and the memory recalibrated. Legacy gets more accurate
every time you argue with it."

## Beat 3 — Profile + consent (0:50–1:20)

*Screen: web app → Profile tab.*

**SAY:** "This is what it knows: who I am, my preferences, my projects, my
strengths — and my weak spots, with dates and counts, straight from the graph.
No other AI can show you this page, because no other AI has receipts."

*Scroll to Evidence Sources. Flip LeetCode ON, hit Sync — a fresh solve lands.*

**SAY:** "And here's the trust model: evidence sources are switches I control.
When it's on, Legacy pulls my real public activity — that's the LeetCode problem
I solved this morning, timestamped, entering memory as verified evidence at 0.9
confidence. My unproven claims sit at 0.3. The graph knows the difference between
what I say and what I do. And off means off — nothing is read."

## Beat 4 — Quests: a game you can't cheat (1:20–2:00)

*Screen: Quests tab. Let the journey chart draw in.*

**SAY:** "Because Legacy knows my gaps, it trains me. Every day: three quests
generated from my own graph — one attacks my weakest area, one advances my real
project, and look at this one—" *(point)* "—generated from a casual chat about
my bike. My character sheet isn't vibes: levels are arithmetic over verified
actions. Interview prep, level zero. That's not a judgment, that's a count."

*Click "Prove it" on the commit quest.*

**SAY:** "And here's what no habit app can do: there are no checkboxes. I claim
nothing. Legacy checks my actual commits, my actual solves, my actual
conversations — no receipt, no credit. I watched it refuse me until the evidence
existed. The referee is my own memory."

*(Green glow, +XP pop, proof line citing commit SHAs.)*

## Beat 5 — Insights: what a real memory notices (2:00–2:35)

*Screen: Insights tab, pre-generated.*

**SAY:** "Storage remembers. A real memory *notices*. My alignment score — forty,
drifting — computed, not guessed. Contradictions found by graph traversal: I
claimed system design was underway; twenty-two days, zero evidence, high
severity. A one-year projection at my current pace. And at the bottom, the
question I've been avoiding—" *(read the open question verbatim, then one beat
of silence)* "—no dashboard has ever asked me that."

## Beat 6 — One memory, every tool + the kicker (2:35–3:00)

*Screen: Memory Graph tab, slow zoom into the green entity cluster. Optionally
splice a 3-second Claude Code clip calling the `legacy` MCP tools.*

**SAY:** "This is the actual graph — five hundred nodes of me. And it's not
locked in this app: it's a native tool inside Claude Code and Cursor via MCP, a
terminal agent, a session hook. When I teach my coding agent 'go tests need the
config folder copied first,' that becomes permanent memory a new teammate can
query next month. Coding agents are brilliant and amnesiac. Legacy is the memory
they all share."

**SAY (kicker, over the graph):** "Every AI today forgets you at midnight.
Legacy is the AI that actually knows you — and checks whether you're becoming
who you said you'd be. Built on Cognee. The house always remembers. Now, so
do I."

---

## Extended live beats (judges' Q&A ammo)

- **The onboarding demo** (if B2B comes up): in chat or CLI ask *"A new team
  member asks: how do I run the unit tests in the payments service — anything
  needed first?"* → Legacy returns the exact 3-step ritual including the
  config-copy prerequisite it distilled from a coding session. Line: "the
  senior's workflow became the org's onboarding doc, automatically."
- **Cross-tool proof**: open a NEW Claude Code chat, ask "what have I been
  working on this week?" — it reaches into Legacy on its own.
- **The numbers**: "Six Cognee operations used deeply, nine typed node kinds,
  five surfaces, ~500 graph nodes — and the entire build's inference bill was
  under a dollar. Memory-native architecture is cheap: recall is top-K
  retrieval plus synthesis, so the token cost is constant whether the graph
  holds one month or ten years."

## Judge Q&A crib sheet

- **"How is this different from ChatGPT memory?"** — ChatGPT stores text about
  you and trusts it. Legacy builds a typed graph, demands evidence for claims
  (0.3 vs 0.9 confidence), computes its scores deterministically, learns from
  your corrections, and is shared infrastructure across every tool, not a
  feature inside one.
- **"Can users fake evidence?"** — Claims enter at 0.3. Verified sources (git,
  LeetCode) at 0.9. The quest judge refuses anything without a receipt — we
  watched it refuse us during development.
- **"What prevents hallucinated insights?"** — The LLM extracts and narrates;
  it never computes. Scores, levels, alignment: plain arithmetic over an exact
  node ledger, reproducible by hand. Every insight cites node dates.
- **"Sparse data?"** — Lower confidence, not wrong answers: every insight
  carries its supporting-node count and confidence.
- **"Privacy?"** — Opt-in switches (off means off), metadata-only project
  learning, workflow distillation that never stores code or secrets,
  forget-with-a-reason, self-hostable via Cognee OSS, and full provenance.
- **"Scale?"** — Recall is top-K + synthesis: constant tokens regardless of
  graph size. The CME stores 2–6 dense nodes per interaction, so the graph
  grows with signal, not transcripts. Long-term precision → consolidation
  (merge/decay), the first roadmap item.
- **"Business?"** — Freemium personal → Pro (auto evidence sync, quests) →
  Teams (shared org memory: onboarding that writes itself) → Enterprise
  (self-hosted). The moat: six months of graph makes switching unthinkable —
  memory is the stickiest surface in software.
