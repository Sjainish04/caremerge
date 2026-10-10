# Product feedback

**Required** in the Devpost submission: feedback on *every* tool, API, or SDK used.
If we build with AWS services, describe which ones and how **in this answer** (it doubles as AWS Builder evidence).
Fill a section in as soon as a tool enters the project; polish wording at submission time.

## Template

```markdown
### <Tool / API / SDK name> (<version>)

- **What we used it for:**
- **What worked well:**
- **What needs work:**
- **Onboarding:** <time to first success, docs quality, sample quality>
- **Would we build with it again?** Yes / No / Maybe — because ...
```

## Tools

<!-- One section per tool. -->

### uv (0.10)

- **What we used it for:** the Python workspace (`packages/caremerge-core`, later `apps/*`), the lockfile, and `uv sync --locked` in CI.
- **What worked well:** `uv add` keeps `pyproject.toml` and `uv.lock` in step; locked installs make CI match local runs.
- **What needs work:** a plain `uv sync` does not install a workspace member unless the root project depends on it (or `--all-packages` is passed). Our first CI run would have failed; `uv add caremerge-core` at the root fixed it.
- **Onboarding:** familiar tool; the workspace docs answered the member-install question.
- **Would we build with it again?** Yes — fast and reproducible.

### Pydantic (2.13)

- **What we used it for:** frozen domain records and agent contracts (`extra="forbid"`), validators, and `AwareDatetime`.
- **What worked well:** strict validation at the trust boundary; malformed model output fails loudly.
- **What needs work:** a plain `datetime` field accepts naive values, which silently uses the host's zone downstream. Review caught it; we switched to `AwareDatetime`.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### ruff (0.16)

- **What we used it for:** formatting and linting (pydocstyle, bugbear, bandit, naming, pyupgrade rules).
- **What worked well:** N818 pushed exception names to the `Error` suffix; one tool replaces several.
- **What needs work:** 0.16 also formats Python code blocks inside Markdown, which flagged our archived spec. We excluded `*.md`.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### mypy (2.4, `--strict`, Pydantic plugin)

- **What we used it for:** strict type checks of `caremerge-core` in CI.
- **What worked well:** caught a `set` annotation receiving a `frozenset` before it shipped.
- **What needs work:** nothing blocking so far.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### pytest (9.1)

- **What we used it for:** table-driven unit tests of the core engines, written test-first.
- **What worked well:** parametrized cases keep the spec's scenarios readable.
- **What needs work:** nothing blocking so far.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### GitHub Actions (`actions/checkout@v7`, `astral-sh/setup-uv` v10.2.0)

- **What we used it for:** CI on every push and PR (format, lint, types, tests).
- **What worked well:** `setup-uv` plus `uv sync --locked` gives a short workflow file.
- **What needs work:** `astral-sh/setup-uv` publishes no floating major tags after v7, so `@v10` fails with "unable to find version `v10`" before any step runs. Its README pins a release commit SHA with a version comment; we do the same.
- **Onboarding:** familiar tool. The error was clear, but nothing local catches a bad action reference.
- **Would we build with it again?** Yes.

### MCP Python SDK (`mcp` 2.3)

- **What we used it for:** the CareMerge add-on's MCP server (Streamable HTTP, stateless), app-only tool visibility through `_meta.ui.visibility`, and the simulator's MCP client.
- **What worked well:** `Annotated[CallToolResult, Model]` returns spoken text and typed card data while still advertising and validating the output schema; `mcp.Client(server)` runs contract tests in process.
- **What needs work:** 2.x renamed FastMCP to `MCPServer`, while AWS's AgentCore guide still shows the 1.x import (see the friction log, FL-001). The SDK's error message explains the rename, which helped.
- **Onboarding:** reading the installed SDK's source answered every question; the migration guide link in the error is useful.
- **Would we build with it again?** Yes.

### FastAPI (0.143), uvicorn (0.54), structlog (26.1), pydantic-settings (2.15)

- **What we used it for:** the simulator host's local API, serving both apps, content-free JSON logs, and typed settings from `CAREMERGE_` variables.
- **What worked well:** a discriminated union of card models becomes a typed union in the OpenAPI document, which `openapi-typescript` turns into TypeScript types; `structlog.testing.capture_logs` makes the no-content-in-logs invariant a plain test.
- **What needs work:** Starlette's `TestClient` now wants `httpx2`; with `httpx` it warns.
- **Onboarding:** familiar tools.
- **Would we build with it again?** Yes.

### Vite (8.3), React (19.2), Tailwind CSS (4.3), openapi-typescript (7.13) + openapi-fetch (0.17), Vitest (5.0)

- **What we used it for:** the Alexa+ simulator UI, its API types generated from the simulator's OpenAPI document, and its tests.
- **What worked well:** `create-vite --no-interactive --eslint` scaffolds without prompts; generated types turn every contract change into a type error.
- **What needs work:** React templates now default to Oxlint, so ESLint needs the `--eslint` flag.
- **Onboarding:** familiar tools.
- **Would we build with it again?** Yes.

### Web Speech API (Chrome)

- **What we used it for:** push-to-talk speech recognition and spoken replies in the simulator.
- **What worked well:** no dependency and no cloud call for a local demo.
- **What needs work:** recognition is Chrome-only, so the simulator keeps a text box and suggested requests as a fallback.
- **Onboarding:** short. TypeScript 6.0's DOM types have the recognition event and result types but not the `SpeechRecognition` constructor, so we declare a minimal interface.
- **Would we build with it again?** Yes, with Amazon Polly for the voice (P1).

## AWS services used

<!-- Service → what it does in our architecture → link to the file that calls it. -->

## Feature requests (optional)

| What we want built | Why it matters | Urgency |
| --- | --- | --- |
| | | critical / important / nice-to-have |
