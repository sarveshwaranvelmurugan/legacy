# Legacy — 3-Minute Demo Script

Record at http://localhost:5199 with both servers running. Practice once before recording.
Before recording: verify the Report tab has ONE pending hypothesis (if not, run
`curl -X POST http://localhost:8400/hypothesis/generate`). Keep the Cognee dashboard
graph explorer open in a second tab for the flyover shot.

---

**[0:00 – 0:20] Cold open — the terminal (optional but strong)**

*Screen: a terminal. Run `./legacy` inside the project.*

> "I didn't tell it anything. Watch." *(point at the ◉ observed line)* "It looked at my terminal, saw the repo, the branch, today's commits — and remembered. Then it told me what it already knows about me. And then — it asked me a question it's been holding."

*If using this cold open, compress the next section to 0:20–0:40.*

**[0:00 – 0:25] The problem**

> "Your AI woke up in Vegas with no memory of last night — that's every chatbot, every session. You've told it your goals fifty times; it remembers none of them. This is Legacy. It doesn't just remember what you said. It tracks who you're trying to become — and tells you, honestly, when you're drifting."

*Show the app header: "Are you becoming who you said you wanted to be?"*

**[0:25 – 1:00] The input — watch the distillation**

*Type into Reflect:* "I've been meaning to study system design but haven't started. I did two hackathon sessions this week though, and pushed a big commit."

> "Every day: two minutes of honesty. Legacy's Compact Memory Engine distills raw text into typed, confidence-scored nodes before Cognee ever sees it — watch: one CONTRADICTION, two ACTIONs. Not chat history. Signal. And notice — Legacy itself just decided a pattern is forming. It will have a question for me."

*Point at the amber "Legacy noticed a pattern forming" line.*

**Transparency note (say it, judges respect it):** "The June history you'll see is a seeded simulation of a student's month — but the evidence sync is live and real: my actual GitHub pushes and LeetCode solves, pulled on stage."

**[0:55 – 1:10] The receipts — Sync Evidence (NEW)**

*On the Reflect tab, scroll to Evidence Sources. Flip the LeetCode toggle ON.*

> "Legacy doesn't trust claims — including mine. Evidence sources are opt-in: when I flip this switch, Legacy may pull my real public activity. Watch." *Click Sync on GitHub, then LeetCode.* "Real commits, real accepted solves, timestamped, straight into the graph as verified evidence — confidence zero-point-nine, versus zero-point-three for anything I merely claim. You can't lie to this thing about shipping code."

**[1:10 – 2:05] The 30-Day Report**

*Switch tabs, click Generate (pre-warm before recording so you can cut the wait).*

> "Thirty days of reflections live in a Cognee knowledge graph. Four engines traverse it. Consistency scores — exact arithmetic over every node: hackathons 100%, DSA drifting at 50%, interview prep zero. Contradictions — found by graph traversal: 'committed to system design, twenty-two days, zero evidence, high severity.' And this — the Behavioral Inference Engine noticed my actions cluster in building while my stated goals say interviews and research. Seventy-two percent confidence, eleven supporting nodes. It's not telling me. It's asking."

*Click "Partially", after typing: "I've been reading system design chapters offline, just never logged them."*

> "I push back — and the graph recalibrates. My correction becomes memory. Legacy gets more accurate every time you correct it. That's Cognee's memory lifecycle doing active calibration, live."

*Show the green "Graph recalibrated" card.*

**[2:05 – 2:40] The projection + the question**

*Scroll to the projection.*

> "Then the question no AI answers: at this pace, who do you become? 'You will finish the hackathon portfolio. Every interview-prep goal stalls. Your biggest risk is arriving at placement season technically strong and interview-unprepared.' And finally — Legacy asks the question I've been avoiding."

*Scroll to the Open Question. Read it out loud, verbatim. Pause one beat.*

**[2:40 – 3:00] The kicker**

*Switch to the Memory Graph tab — the in-app force-graph of the actual Cognee knowledge graph. Zoom in slowly on the green entity cluster.*

> "Every ambitious person without a mentor is generating data about their trajectory that nobody reads — including them. Legacy reads it. Cognee remembers it. And every week it asks: are you becoming who you said you wanted to be? The house always remembers. Now, so do you."

---

## Judge Q&A crib sheet

- **"Can users fake evidence?"** — Source-agnostic with confidence tiers: manual claims start at 0.3, GitHub-verified evidence at 0.9. The graph knows the difference. LeetCode/Notion/Calendar are v2 adapters on the same interface.
- **"Sparse data?"** — Sparse data produces *lower confidence*, not wrong answers. Every insight ships with its confidence and supporting-node count. 3 nodes → "hypothesis only." 17 nodes → actionable.
- **"Why not a journal app?"** — A journal stores text. Legacy cross-references CLAIM nodes against the *absence* of ACTION edges via graph traversal, with temporal day-count reasoning. A journal can't tell you you've claimed consistency for 21 days with zero evidence.
- **"How is this deep Cognee usage?"** — Typed memory strings shaped for graph extraction; backdated timestamps recall reasons over temporally; four purpose-built GRAPH_COMPLETION engines; calibration nodes closing the improve loop; forget-with-a-reason closure. Flat conversation storage can do none of this.
- **"Why the local ledger for scores?"** — Deliberate split: semantic/graph reasoning belongs to Cognee; score arithmetic must be deterministic and reproducible on stage. Right tool for each layer.
- **"Business model?"** — First-gen students without alumni networks; university career centers; EdTech licensing. Self-hostable via Cognee OSS for privacy.
