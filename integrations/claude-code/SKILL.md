---
name: legacy
description: Query or update the user's Legacy memory agent — a persistent knowledge graph of their projects, goals, actions, and history that survives across all Claude sessions. Use when the user references their past projects by name or pattern ("build it like app-a", "follow the pattern of my earlier apps", "combine the functionality of X and Y"), asks what they were working on or about their goals/progress, announces completing a project or milestone (log it + learn the repo), or at the start of a task where the user's prior work context would help.
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

# DISTILL — at the end of a substantial work session, store its workflow
# knowledge (commands the user taught you, rituals, conventions — never code):
echo "user taught: lint = make lint from repo root; go tests need config/ copied into the service folder first" | /Users/sarveshwaran/hangover/legacy distill -

# LEARN — deep-study a project's stack/architecture/features/patterns into
# memory (metadata only: README, manifests, tree, commit messages — no source).
# Run from inside the project directory. Do this when a project is finished.
/Users/sarveshwaran/hangover/legacy learn
```

## When to use which

- User says "build it like <project>" / "follow the pattern of my apps A and B" →
  `ask` Legacy to describe those projects' stacks, architectures, features and
  patterns, then use that answer as the design basis for the new work.
- User asks about their own past/progress/goals → `ask`, then answer from the output.
- User says they finished/started/decided something notable → `remember` it,
  and if it's a project in a git repo, also run `observe` + `learn` from that
  project's directory so the project's patterns enter memory.
- Starting substantial work in a repo → optionally `observe` so Legacy tracks it.

## Notes

- Requires the Legacy backend keys in `/Users/sarveshwaran/hangover/.env`
  (already configured). No servers needed — the CLI talks to Cognee Cloud directly.
- Output is rich-formatted text; read it and relay the substance to the user.
- Do not store secrets, credentials, or third-party private information in Legacy.
