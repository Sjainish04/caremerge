# Alexa+ and MCP — research notes

Verified 2026-10-01. Re-check the linked docs before relying on a detail.

## Bottom line

- The real Alexa+ **MCP Toolkit / Category SDK is private preview, select partners only** ([add-ons home](https://developer.amazon.com/docs/alexaplus/add-ons/home.html), [development stages](https://developer.amazon.com/docs/alexaplus/add-ons/alexa-plus-add-on-development-stages.html)). An individual entrant almost certainly cannot attach a self-hosted MCP server to a real Alexa+ account.
- Plan on the **simulated path**: a real, public Streamable HTTP MCP server plus a web "Alexa+ simulator" (agent as MCP client, voice in/out, MCP Apps renderer). The [rules](https://amazonappdev2026.devpost.com/rules) accept a simulation as long as the demo clearly shows it working.
- Organizer hint ([update](https://amazonappdev2026.devpost.com/updates/46456-got-an-idea)): *"a single turn Q&A bot works, an agentic workflow that orchestrates across services or keeps context across sessions stands out more."*

## MCP spec

**2025-11-25** ([changelog](https://modelcontextprotocol.io/specification/2025-11-25/changelog)) vs 2025-06-18:

- Experimental **Tasks** (durable requests with polling, SEP-1686); **URL-mode elicitation** (SEP-1036); **sampling with tools** (SEP-1577); **icons** (SEP-973).
- **OAuth Client ID Metadata Documents** recommended for client registration (SEP-991); OIDC discovery; incremental scope consent via `WWW-Authenticate` (SEP-835).
- Tool-name guidance (SEP-986); input-validation failures returned as tool errors (SEP-1303); SSE polling (SEP-1699); JSON Schema 2020-12 default; invalid `Origin` → HTTP 403.

**Streamable HTTP** ([transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)):

- One endpoint for POST and GET. Each client message is a POST with `Accept: application/json, text/event-stream`; the server answers with JSON or an SSE stream (202 for notifications/responses). GET opens a server→client SSE stream or returns 405.
- Optional `MCP-Session-Id` from initialize, then sent on every request (404 → re-initialize; DELETE ends it). `MCP-Protocol-Version` header required after init.
- Servers MUST validate `Origin`, SHOULD bind to localhost when local, SHOULD authenticate. Auth, if used, is OAuth 2.1 with Protected Resource Metadata (RFC 9728), PKCE S256, and the RFC 8707 `resource` parameter ([authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)).

**Newer revision 2026-07-28** ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)): stateless (no `initialize`, no session ID; `server/discover` required), `Mcp-Method`/`Mcp-Name` headers, multi-round-trip `input_required` replaces server-initiated requests, `subscriptions/listen` replaces the GET stream, Tasks moved to an extension, Roots/Sampling/Logging and DCR deprecated. Alexa+ docs do not state support for it; Amazon's client example still sends `protocolVersion: "2025-03-26"` ([client lifecycle](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-client-lifecycle.html)).

**SDKs** ([tiers](https://modelcontextprotocol.io/docs/sdk)):

- TypeScript: `@modelcontextprotocol/sdk` 1.23.0 added 2025-11-25 features; v2 split packages `@modelcontextprotocol/server` / `client` (2.2.0, Sep 28 2026) serve both protocol generations ([protocol versions](https://ts.sdk.modelcontextprotocol.io/v2/protocol-versions)).
- Python: `mcp` 1.23.0 caught up to 2025-11-25; v2.0.0 (Jul 28 2026) serves 2026-07-28 and every earlier revision; FastMCP renamed `MCPServer`; v1.x security fixes only ([v2.0.0](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.0.0)).
- Go and C# reportedly serve both generations — UNVERIFIED.

**Recommendation:** target 2025-11-25 behavior (what Alexa+ documents) with an SDK that also serves 2026-07-28; don't depend on sampling, roots, logging, or core Tasks.

## Agent Skills

- Open format: a folder with `SKILL.md` (YAML frontmatter + Markdown) and optional `scripts/`, `references/`, `assets/` ([agentskills.io](https://agentskills.io/), [spec](https://agentskills.io/specification)). `name` ≤ 64 chars, lowercase/digits/hyphens, matches the folder; `description` ≤ 1024 chars. Supported by Claude Code, Codex, Gemini CLI, Copilot, Cursor, Kiro, Goose, and others.
- The hackathon's **"Build with Agent Skills"** link points to the **MCP Apps** docs ([link](https://apps.extensions.modelcontextprotocol.io/api/#build-with-agent-skills)): skills `create-mcp-app`, `migrate-oai-app`, `add-app-to-server`, `convert-web-app`. Install in Claude Code with `/plugin marketplace add modelcontextprotocol/ext-apps`. MCP Apps (`ui://` resources in sandboxed iframes) stable since 2026-01-26 ([repo](https://github.com/modelcontextprotocol/ext-apps)).
- **Alexa+ supports the MCP Apps extension** for visuals on screen devices ([MCP Toolkit overview](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-overview.html)).
- Amazon ships an "Add-on Agent Skill" that walks a coding agent through inspecting, scaffolding, deploying, and submitting an MCP add-on ([quickstart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart.html)). No evidence Alexa+ loads `SKILL.md` at runtime (UNVERIFIED) — Agent Skills look like build-time tooling. Not the same as classic Alexa Skills (ASK).

## Alexa+ developer story

- Feb 2025: Action, Web Action, and Multi-Agent SDKs announced as early access ([blog](https://developer.amazon.com/en-US/blogs/alexa/alexa-skills-kit/2025/02/new-alexa-announce-blog)). Today "Alexa+ for Builders" lists Category SDK, MCP Toolkit, Smart Home AI Toolkit ([page](https://developer.amazon.com/en-US/alexa/alexa-ai)).
- Jul 23 2026: MCP Toolkit, Category SDKs, Amazon Wallet, Smart Home toolkit in Preview ([blog](https://developer.amazon.com/alexaplus/blogs/2026/07/alexa-plus-new-ways-to-build-experiences)).
- Partner flow (US only, MCP 2025-11-25 over Streamable HTTP): `npm i -g @alexa-ai/cli` → `alexa-ai configure` → `alexa-ai new mcp --mcp-server-url …` → edit `addon.json` → `alexa-ai deploy` → test in web simulator or device → `alexa-ai submit`. Tool changes need a redeploy ([dev environment](https://developer.amazon.com/docs/alexaplus/add-ons/set-up-your-development-environment.html)).
- Community workaround: classic Alexa Skill + Strands agent on AgentCore imitating the orchestrator on a real Echo ([alexa-skill-mcp-bridge](https://github.com/KayLerch/alexa-skill-mcp-bridge)) — not real Alexa+ orchestration; present honestly if used.

## Who is already on Alexa+ (avoid these niches)

- OpenTable, Vagaro, Grubhub, Uber Eats, Uber, Ticketmaster, Thumbtack, Fodor's, Tripadvisor, Suno ([features](https://www.aboutamazon.com/news/devices/new-alexa-top-features)); Expedia, Yelp, Angi, Square ([2026 integrations](https://www.aboutamazon.com/news/devices/alexa-plus-voice-booking-integrations)).
- First MCP brands: Canva, Cengage, Crystal Dynamics, Headspace, Priceline, Viator, Virgin Atlantic, Weekend, Lyft, Distribusion (Brightline/FlixBus/Greyhound). Amazon Wallet: Atom Tickets, Fandango, TaskRabbit.
- Crowded: dining, food delivery, rides, ticketing, home services, beauty/local booking, hotels/travel, music, meditation, education. Other entrants already building a "stateful HomeOps MCP" and an "AgentPOS" commerce add-on (seen in search; not reviewed).

## Design rules to bake in

- Tool round trip **< 500 ms** ([integration approach](https://developer.amazon.com/docs/alexaplus/add-ons/choose-the-proper-alexaplus-integration-approach.html)); search results within 3 s with progress messages ([functional requirements](https://developer.amazon.com/docs/alexaplus/add-ons/functional-requirements.html)).
- Speech < 30 s; ≤ 5 options; read back key details and require an explicit yes; never speak tool names, JSON, or IDs; accept several details in one utterance.
- One tool per customer intent, no overlaps; always return data ([tool schema design](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-addon-tools-schema-data-design.html)) — "you influence Alexa's response through the data you return" ([conversation surface](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-addon-conversation-surface.html)).
- Purchases: voice **and** written confirmation; > 100 USD adds a 4-digit voice code; full price breakdown ([policy](https://developer.amazon.com/docs/alexaplus/add-ons/policy-requirements.html)). Amazon Wallet checkout is UCP-compatible; brand is merchant of record ([payments](https://developer.amazon.com/docs/alexaplus/add-ons/payments.html)).
- Auth: OAuth 2.1, PKCE S256, `resource` parameter; service-level `client_credentials` (`mcp:service`) plus user-level auth code; refresh tokens required; DCR/OIDC/step-up not supported ([authentication](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-authentication.html)). Linking starts when a protected tool returns 401/403; screens show a QR code ([account linking](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-account-linking.html)).
