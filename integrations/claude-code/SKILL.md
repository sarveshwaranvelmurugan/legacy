---
name: legacy
description: Query or update the user's Legacy memory agent — a persistent knowledge graph of their projects, goals, actions, and history that survives across all Claude sessions. Use when the user asks what they were working on, about their past projects/goals/progress ("what was I doing last week?", "am I on track?", "what did I finish?"), when they announce completing a project or milestone (log it), or at the start of a task where knowing the user's current work context would help.
---

# Legacy — the user's persistent memory agent

Legacy maintains a Cognee knowledge graph of this user's life trajectory:
goals, dated actions, verified evidence (git history), claims, and
contradictions. Claude sessions are amnesiac; Legacy is not. Bridge through it.

## Commands (run via Bash)

The CLI lives at `/Users/sarveshwaran/hangover/legacy` and works from any cwd:

```bash
# RECALL — answer questions from the user's memory graph (~15-30s)
/Users/sarveshwaran/hangover/legacy ask "what was the user working on this week?"

# CAPTURE — store a milestone or fact the user just told you
/Users/sarveshwaran/hangover/legacy remember "finished the payments-service refactor and shipped it to staging"

# OBSERVE — record the current repo's git state as verified evidence
# (run from inside the project directory being discussed)
/Users/sarveshwaran/hangover/legacy observe
```

## When to use which

- User asks about their own past/progress/goals → `ask`, then answer from the output.
- User says they finished/started/decided something notable → `remember` it
  (one dense sentence, third person is fine), and ALSO run `observe` from that
  project's directory if it is a git repo — commits are verified evidence.
- Starting substantial work in a repo → optionally `observe` so Legacy tracks it.

## Notes

- Requires the Legacy backend keys in `/Users/sarveshwaran/hangover/.env`
  (already configured). No servers needed — the CLI talks to Cognee Cloud directly.
- Output is rich-formatted text; read it and relay the substance to the user.
- Do not store secrets, credentials, or third-party private information in Legacy.
