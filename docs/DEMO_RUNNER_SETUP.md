# Demo Runner Setup (for the person recording the demo)

You'll clone this repo, run Legacy locally, connect **your own** GitHub and
LeetCode as evidence sources, and record the demo following
[DEMO_SCRIPT.md](DEMO_SCRIPT.md). Budget ~30 minutes for setup.

## 0. Get the keys — privately

Ask Sarvesh for the `.env` file **over a private channel** (never commit it,
never paste it in an issue/chat that's public). Put it at the repo root as
`.env`. Using his `.env` means you connect to the already-seeded Cognee graph
(30 days of demo history + hypotheses) — this is what you want for the video.

> If you instead use your own Cognee/Anthropic accounts: copy `.env.example`,
> fill your keys, then run `cd backend && ../.venv/bin/python seed_demo.py`
> (takes a few minutes) to build the demo history from scratch.

## 1. Backend

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd backend
../.venv/bin/uvicorn app.main:app --port 8400 --reload
```

Check: `curl http://localhost:8400/health` → `{"status":"ok", ...}`

## 2. Rebuild the local ledger (IMPORTANT on a fresh clone)

The consistency scores are computed from a local node ledger that is not in
git. Without this step the report shows 0 actions everywhere.

```bash
cd backend && ../.venv/bin/python backfill_ledger.py
# expect: "ledger rebuilt with 70+ entries"
```

## 3. Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5199    # → http://localhost:5199
```

## 4. Connect YOUR evidence sources

On the **Reflect** tab → Evidence Sources panel:
- flip the GitHub toggle on, enter your GitHub username, hit **Sync**
- flip the LeetCode toggle on, enter your LeetCode username, hit **Sync**

Your real public pushes and accepted solves land in the graph as verified
evidence — this is the "live receipts" beat of the demo. Solve one easy
LeetCode problem shortly before recording so the sync visibly pulls
something fresh.

## 5. Try the terminal agent

```bash
./legacy            # observes the repo, primes from memory, then chat
./legacy ask "what is this user working on?"
```

## 6. Pre-recording checklist

- [ ] Backend + frontend both up; app loads at http://localhost:5199
- [ ] `curl -X POST http://localhost:8400/hypothesis/generate` → ensures ONE
      pending hypothesis is waiting in the report (the money-shot moment)
- [ ] Generate the report once BEFORE recording (first run takes ~30s;
      regenerate is faster and you can cut waits in the edit)
- [ ] Memory Graph tab renders (~460+ nodes) — this is the closing shot
- [ ] Both your evidence sources sync successfully on camera-ready data
- [ ] Read [DEMO_SCRIPT.md](DEMO_SCRIPT.md) twice; note the transparency
      line about seeded history vs live evidence — say it, judges respect it

## Troubleshooting

- **Report sections show errors** → an upstream call timed out; hit retry.
- **Consistency all 0%** → you skipped step 2 (`backfill_ledger.py`).
- **Sync says "switched off"** → flip the toggle first; off means off.
- **Fresh Cognee tenant DNS errors** → see README troubleshooting (pinned-IP
  fallback in `backend/app/config.py`).
