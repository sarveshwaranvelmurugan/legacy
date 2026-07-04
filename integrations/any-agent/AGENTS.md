# Legacy memory agent (for any AI coding agent)

This user has Legacy — a persistent memory agent backed by a Cognee knowledge
graph. Your session is amnesiac; Legacy is not. Bridge through its CLI
(adjust the path to the Legacy repo location):

    ~/hangover/legacy ask "what was the user working on this week?"
    ~/hangover/legacy remember "finished the payments refactor, shipped to staging"
    ~/hangover/legacy observe    # record this repo's git state as verified evidence
    ~/hangover/legacy learn      # deep-study this project's patterns (metadata only)
    echo "<session workflow summary>" | ~/hangover/legacy distill -   # store how-things-are-done knowledge at session end

Rules of thumb:
- User references past projects or patterns -> `ask` first, design from the answer.
- User finishes/decides something notable -> `remember` it; in a git repo also
  `observe` + `learn`.
- End of a session where the user taught you commands/rituals/conventions ->
  summarize them and pipe to `distill -` (commands and how-tos only; never code or secrets).
- Never store secrets or third-party private data in Legacy.

Copy this section into your tool's agent-instructions file (AGENTS.md,
.cursor/rules/, CLAUDE.md, etc.).
