# Bee — research notes

Verified 2026-10-01. Re-check the linked docs before relying on a detail.

## Bottom line

- Plumbing is cheap — MCP is one command, plus a Skill, a TypeScript library, and a local REST proxy. **The use case is the differentiator.**
- **Write-back is narrow:** only **facts** (create/update/confirm/delete) and **todos** (create with alarm, update, complete, delete, accept/dismiss suggestions). Everything else is read-only.
- **Speaker identity is unreliable** — Bee's own docs example labels speakers "Unknown", and one entrant reports all 10,336 of its utterances came back "Unknown". Don't build features that depend on who said what; **voice notes (journals) are deliberate owner input** and the best channel for owner commands.
- **Real-time is best-effort:** `bee stream` emits `new-utterance` events at-most-once with no replay; pair it with cursor polling of `bee changed`. Don't promise sub-second voice commands.
- **Run locally, not on edge/serverless:** the direct API uses a private CA that reportedly breaks Cloudflare Workers, Vercel Edge, and Lambda ([issue #5](https://github.com/bee-computer/bee-cli/issues/5)).
- **Start recording now:** the device ships US-only and the demo needs real data. Double-pressing the device button forces processing of a conversation ([Pioneer page](https://bee.computer/bee-pioneer)).

## Access and auth ([docs](https://docs.bee.computer/))

- No OAuth app registration and no API-key console. Enable **Developer Mode**: Bee app → Settings → tap the app version 5 times ([developer mode](https://docs.bee.computer/docs/developer-mode); Android: user name → About → App Version, per [issue #13](https://github.com/bee-computer/bee-cli/issues/13)).
- `npm i -g @beeai/cli` → `bee login` → approve the `https://bee.computer/connect#<id>` link (or `--qr`) in the app within ~5 min. Token in the OS keychain (fallback `~/.bee/token-prod`); `--token` / `--token-stdin` for headless use ([CLI](https://docs.bee.computer/docs/cli)).

## Surfaces

- **CLI** ([docs](https://docs.bee.computer/docs/cli)): `today` (calendar + email brief), `now` (last 10 h of conversations with utterances), `changed` (cursor changefeed), `search` (BM25 over conversations, daily summaries, facts; `--neural` for conversations; [search](https://docs.bee.computer/docs/search)), `facts`, `todos` (incl. suggestions), `conversations`, `daily`, `journals` (voice notes), `insights`, `locations`, `photos` (synced from the phone gallery), `sync`, `stream`, `proxy`, `mcp`. Markdown by default, `--json` everywhere.
- **MCP** ([docs](https://docs.bee.computer/docs/mcp)): `bee mcp connect claude-code` (also `claude`, `codex`). stdio, or HTTP on `127.0.0.1:8790` with a ≥ 32-char bearer token. ~34–35 tools.
- **Agent Skill:** [bee-computer/bee-skill](https://github.com/bee-computer/bee-skill) — `npx skills add bee-computer/bee-skill`. Tells the agent to start with `bee now` and prefer verbatim utterances over summaries; includes a multi-agent "learn the owner" workflow. README says MIT but there is no LICENSE file.
- **API** ([proxy](https://docs.bee.computer/docs/proxy)): `/v1/*` via `bee proxy` on `localhost:8787` (no auth, local only) or directly at `https://app-api-developer.ce.bee.amazon.dev/` with a Bearer token and Bee's private CA. Also: todo suggestions, insights, `locations/{clusters,current,recent}`, photos, today brief, SSE `/v1/stream`.
- **Library:** `@beeai/cli/lib` exports `createBeeClient` ([source](https://github.com/bee-computer/bee-cli/blob/main/sources/lib/index.ts)).
- **Sync** ([docs](https://docs.bee.computer/docs/sync)): `bee sync` writes `facts.md`, `todos.md`, `daily/<date>/summary.md`, `conversations/<date>/<id>.md`; incremental, deletions only on `--full`. Point it at `data/private/` (git-ignored).
- **Real-time** ([docs](https://docs.bee.computer/docs/realtime)): `bee stream` with `--webhook-endpoint` forwarding. Third-party report: todo events never arrive on the stream, changes show up via `changed` ~35 s later, and the stream dies after ~43 h ([ringfence](https://github.com/harshpuri84/ringfence)).
- Rate limits: none documented (client has no 429 handling) — UNVERIFIED server-side.

## Data shapes that enable features

Timestamped verbatim utterances; a location (lat/long + name) per conversation and place clusters; daily summaries that include calendar and email summaries; confirmed and pending facts; todo suggestions; insights; voice-note journals.
Natural fits: lecture → quiz/spaced repetition (education), meeting → issues/decisions (developer experience), place-aware reminders and commitment tracking (productivity).

## Repos

- [bee-computer/bee-cli](https://github.com/bee-computer/bee-cli): TypeScript, MIT, last commit 2026-08-17; npm `@beeai/cli` 0.7.3 (2026-06-27). Open bugs: `/v1/todos` and `/v1/daily` return 500 (#14), `bee now` duplicates utterances (#3), TLS cert rejected on Workers/Lambda/Vercel Edge (#5).

## Device and app

- **Bee Pioneer:** $49.99, ships to the US only, ~7 days battery, mute/process button, LED ([Pioneer page](https://bee.computer/bee-pioneer)). No subscription today; Premium promised "in the future" (was $19/month in July 2025 per [TechCrunch](https://techcrunch.com/2025/07/22/amazon-acquires-bee-the-ai-wearable-that-records-everything-you-say/)).
- **Apple Watch:** watchOS companion of the "Bee – Your Personal AI" iPhone app (iOS 17.6+, watchOS 10+) ([App Store](https://apps.apple.com/us/app/bee-your-personal-ai/id6480349491)). Founders described limits in Feb 2025 — must be turned on, phone calls interrupt it, battery ([Latent Space](https://www.latent.space/p/bee)) — current status UNVERIFIED.
- Transcribes "up to 40" languages; app UI English-only. Android app is early access and "not actively being supported".
- **Privacy** ([Amazon, 2026-09-23](https://www.aboutamazon.com/news/devices/bee-private-compute-data-protection)): audio transcribed in real time then discarded; transcripts/summaries/todos encrypted with device-controlled keys and processed in "Bee Private Compute" on AWS Nitro. No bystander-consent feature found; topic/location fencing is "future".

## Already built — avoid duplicating

- Earlier community: [BeeMCP](https://github.com/OkGoDoIt/beemcp) (old API, likely dead), [reinvent-notetaker](https://github.com/brookejamieson/reinvent-notetaker) (Bee + Strands + Bedrock), [bee-homeassistant-addon](https://github.com/FinestDice17/bee-homeassistant-addon).
- Public hackathon entries: [ringfence](https://github.com/harshpuri84/ringfence) (spoken tasks → coding-agent runs, approved by ticking a Bee todo), [bee-bystander](https://github.com/AtchayamG/bee-bystander) (consent/redaction layer), [ambient-guard](https://github.com/andywongpt-my/ambient-guard) (Bee + weather), [beereflect-ai](https://github.com/rassulakhiyarov-afk/beereflect-ai) (journal on Bedrock).
