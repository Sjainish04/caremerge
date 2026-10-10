# CareMerge Alexa+ simulator UI

The simulated Alexa+ screen (spec §12). You talk to it by voice in Chrome or by typing; it shows what Alexa says as captions and the CareMerge add-on's results as cards. Every reply it speaks is the host's template-rendered `speech`, unchanged; the UI never writes a health sentence of its own.

It runs on top of two local servers: the CareMerge MCP add-on (`apps/addon`) and the simulator host (`apps/simulator`), which owns the conversation and serves the API this app calls.

## Run it

From the repository root, start the servers (see the root README for details):

```sh
cp .env.example .env          # lets the dev server's origin (localhost:5173) call the host
uv sync
uv run caremerge-addon serve  # terminal 1
uv run caremerge-sim serve    # terminal 2
```

Then, in this folder:

```sh
pnpm install
pnpm dev                      # http://localhost:5173
```

Open it in Chrome for the microphone; other browsers use the text box and suggestions.

Configuration comes from the repository's `.env`, like the other apps. The dev server proxies `/api` to the host on `CAREMERGE_SIMULATOR_PORT` (default 8765), so the browser stays same-origin. The page reads only `VITE_CAREMERGE_*` variables: how long to wait for the host (`src/settings.ts`).

## Scripts

| Script | What it does |
| --- | --- |
| `pnpm dev` | Dev server on port 5173 |
| `pnpm build` | Type-check, then build to `dist/` |
| `pnpm typecheck` | `tsc -b` |
| `pnpm lint` | ESLint |
| `pnpm test` | Vitest (jsdom) |
| `pnpm gen:api` | Generate `src/api/schema.d.ts` from `src/api/openapi.json` |

## The API contract

The simulator host's OpenAPI document is the contract (spec §11). When the host's API changes, refresh both generated files from the repository root:

```sh
uv run caremerge-sim openapi > apps/web/src/api/openapi.json
pnpm --dir apps/web gen:api
```

CI fails if either file is stale. The card tests use real turns recorded from the simulator; `apps/simulator/tests/test_web_fixtures.py` checks them and records them again with `--record-web-fixtures`.

## Layout

| Path | Purpose |
| --- | --- |
| `src/api/` | Typed client (`openapi-fetch`) with the per-launch session token; generated types |
| `src/state/useSimulator.ts` | Conversation state: say, answer, add a visit, delete data |
| `src/voice/voice.ts` | Web Speech API: recognition for requests, synthesis for replies |
| `src/components/` | The device, the talk bar, the visit inbox, and reminders |
| `src/components/cards/` | One card per result: visit updates, changes, the plan for a day, questions, reminders |
| `src/test/fixtures/` | Turns recorded from the simulator, for the card tests |
