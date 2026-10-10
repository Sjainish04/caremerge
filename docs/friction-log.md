# Friction log

Optional in the Devpost form, but **submissions with friction logs can earn up to a 10% judging bonus**.
Log friction the moment it happens — reconstructing it on submission day loses the exact errors and steps.
In Claude Code, `/friction-log <what went wrong>` appends an entry in this format.

Severity scale:

- **Blocker** — could not proceed without a workaround or outside help
- **High** — lost more than an hour, or had to change the design
- **Medium** — lost 15–60 minutes, or docs were wrong or misleading
- **Low** — paper cut: confusing naming, a missing example, a noisy warning

Rules: no tokens, keys, or personal data (Bee transcripts, Ring video details, addresses) in entries.

## Template

```markdown
### FL-000 — <short title>

- **Date:** YYYY-MM-DD
- **Tool / API / SDK + version:**
- **Task attempted:**
- **Steps taken:**
  1.
  2.
- **Expected:**
- **Actual:** <exact error text or behavior>
- **Severity:** Blocker | High | Medium | Low
- **Workaround:**
- **Actionable suggestion:** <what the Amazon/AWS team should change>
```

## Entries

<!-- Newest last. Number entries sequentially: FL-001, FL-002, ... -->

### FL-001 — AgentCore's MCP guide uses an API the current MCP Python SDK removed

- **Date:** 2026-10-09
- **Tool / API / SDK + version:** Amazon Bedrock AgentCore Runtime developer guide, "Deploy MCP servers in AgentCore Runtime" (`runtime-mcp`); MCP Python SDK `mcp` 2.3.0
- **Task attempted:** Build the CareMerge MCP server to deploy on AgentCore Runtime, following the guide.
- **Steps taken:**
  1. Read the guide's Step 1, which says `pip install mcp` and then `from mcp.server.fastmcp import FastMCP`.
  2. Installed the current SDK with `uv add mcp` (resolved to 2.3.0).
  3. Ran the guide's import: `python -c "from mcp.server.fastmcp import FastMCP"`.
- **Expected:** The sample runs with the package the guide tells you to install.
- **Actual:** `ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer (from mcp.server.mcpserver import MCPServer) and other APIs changed; see the migration guide at https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver or pin 'mcp<2' to keep running v1 code.`
- **Severity:** Medium
- **Workaround:** Use `from mcp.server.mcpserver import MCPServer`, serve `server.streamable_http_app(stateless_http=True, host="0.0.0.0")` with uvicorn on port 8000, and test with `mcp.Client(url)`.
- **Actionable suggestion:** Update the `runtime-mcp` guide's server and client samples to the 2.x API (`MCPServer`, `mcp.Client`), or pin `mcp<2` in the guide's `requirements.txt` until they are updated.
