# Legacy as an MCP server

Legacy's memory becomes **native tools** in any MCP client — no skill-triggering
luck, the tools are just there in every session:

| Tool | What it does |
|---|---|
| `legacy_recall` | answer from the user's memory graph (projects, goals, history, patterns) |
| `legacy_remember` | store a fact/milestone the user just shared |
| `legacy_observe` | record a repo's git state as verified evidence |
| `legacy_learn_project` | deep-study a finished project (metadata only) |
| `legacy_sync_evidence` | pull GitHub/LeetCode activity from connected sources |
| `legacy_alignment` | the user's current 0-100 alignment score |

## Claude Code

`./legacy setup` registers it automatically. Manual form:

```bash
claude mcp add -s user legacy -e PYTHONPATH=<repo>/backend -- <repo>/.venv/bin/python -m app.mcp_server
```

## Cursor / Claude Desktop / any MCP client

Add to the client's MCP config (e.g. `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "legacy": {
      "command": "<repo>/.venv/bin/python",
      "args": ["-m", "app.mcp_server"],
      "env": { "PYTHONPATH": "<repo>/backend" }
    }
  }
}
```

`./legacy setup` prints both, with `<repo>` already filled in for your machine.
Requires the repo's `.env` (Cognee + Anthropic keys) at the repo root.
