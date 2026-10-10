# CareMerge

Version control for your care, as an Alexa+ add-on. Entry for **Build, Ship, Shape: Amazon Developer Hackathon** (Devpost).
Deadline: **Friday, Oct 23, 2026, 3:00 PM EDT**.

> **Status:** the MCP add-on, the simulated Alexa+ host, and its screen run end to end on your machine with synthetic visits (milestone M1). Next (M2): Claude on Amazon Bedrock for extraction and routing, DynamoDB, Cognito, and hosting the add-on on Amazon Bedrock AgentCore Runtime. The build spec is [CareMerge_Hackathon_Full_Specification.md](CareMerge_Hackathon_Full_Specification.md).

The sections below double as the Devpost text description — replace each _TBD_ as the project takes shape.

## Track

| | |
| --- | --- |
| Primary track | Alexa+ (MCP add-on, simulated Alexa+ experience) |
| Mini challenges | AWS Builder · Open Source (optional) |

## What it does

After a few appointments, care instructions come from several people: a family doctor, a specialist, a pharmacist. CareMerge keeps them as one care plan you can ask Alexa about.

- **Confirm what was said.** Each visit (synthetic transcripts in this repo) becomes a short list of items, each with the exact words it came from. Nothing enters your care plan until you say yes.
- **Ask what changed.** CareMerge keeps every instruction's history, so it can tell you what changed since your last visit, including changes that start later.
- **Ask about a day.** It answers only from your confirmed plan, names who said it and when, and never decides what's medically correct.
- **Clarify what's missing.** When an instruction leaves something out, such as a hold with no end date, CareMerge turns it into a question for your care team.
- **Set reminders you approved.** It only sets reminders that repeat a confirmed instruction or ask your care team a question, and only after you say yes.

From the demo, as the current build says it:

> **You:** Alexa, what's new from my visit with Dr. Lee?
>
> **Alexa:** Your visit with Dr. Lee on Wednesday, October 7 has 2 new items: your procedure on Wednesday, October 28 and a hold on Medication A starting Sunday, October 25. Should I add them to your care plan?
>
> **You:** Yes.
>
> **Alexa:** Added to your care plan.
>
> **You:** Should I take Medication A on Sunday, October 25?
>
> **Alexa:** On Sunday, October 25, Medication A is on hold in your care plan. That's from Dr. Lee on Wednesday, October 7. CareMerge isn't deciding what's correct. Check with your care team if you're unsure.

## How it works

```text
apps/web                     apps/simulator                    apps/addon
simulated Alexa+ screen ───▶ simulated Alexa+ host ──────────▶ CareMerge MCP add-on
voice, captions, cards  /api routes each request to one  MCP  tools over caremerge-core:
                             tool; asks yes or no itself       visits, changes, plan, questions, reminders
```

- **The add-on is an MCP server** on the MCP Python SDK 2.3, served over Streamable HTTP at `/mcp`. With the SDK's client it negotiates protocol 2026-07-28; the track requires 2025-11-25 or later.
- **Templates speak; the model only routes.** Every tool result carries `speech`, rendered from registered, snapshot-tested templates. The host says it unchanged and shows the result's data as a card.
- **Only your yes changes your data.** Tools that change state (`confirm_items`, `confirm_reminder`, `add_visit`, `delete_my_data`) are app-only through MCP Apps' `_meta.ui.visibility: ["app"]`, so the host never offers them to the model. The host calls them only on your spoken yes or a tap on the screen.
- **A policy gate checks every reminder.** A reminder must restate a verified instruction with its source, or ask your care team an open question.
- **The care plan is bitemporal.** Each instruction records when it applies and when it was said, so the plan for any day, the changes between visits, and the gaps (such as a temporary change with no end) are computed, not guessed.

Where the track technology is called in code:

| What | Where |
| --- | --- |
| MCP server: tools, app-only visibility, error mapping | [`apps/addon/src/caremerge_addon/mcp/server.py`](apps/addon/src/caremerge_addon/mcp/server.py) |
| Streamable HTTP endpoint (`streamable_http_app`) | [`apps/addon/src/caremerge_addon/main.py`](apps/addon/src/caremerge_addon/main.py) |
| MCP client in the simulated Alexa+ host (`mcp.Client`) | [`apps/simulator/src/caremerge_simulator/addon_client.py`](apps/simulator/src/caremerge_simulator/addon_client.py) |
| Simulated Alexa+ host: routing, confirmations, speech | [`apps/simulator/src/caremerge_simulator/host.py`](apps/simulator/src/caremerge_simulator/host.py) |
| Simulated Alexa+ screen | [`apps/web/src/App.tsx`](apps/web/src/App.tsx) |
| Spoken templates | [`packages/caremerge-core/src/caremerge_core/questions.py`](packages/caremerge-core/src/caremerge_core/questions.py) |
| Reminder policy gate | [`packages/caremerge-core/src/caremerge_core/policy.py`](packages/caremerge-core/src/caremerge_core/policy.py) |

In M1 everything runs locally: extraction reads recorded results (`fixtures/extractions`), the ledger is in memory, and a keyword router stands in for the model. M2 replaces these with Claude on Amazon Bedrock, DynamoDB, and AgentCore Runtime behind the same interfaces.

## Getting started

Prerequisites: Python 3.12 with [uv](https://docs.astral.sh/uv/), Node.js 24 with [pnpm](https://pnpm.io/) 11, and Chrome for voice.

Run everything from the repository root, where the settings read `.env` and find `fixtures/`:

```sh
cp .env.example .env          # settings; also lets the web dev server's origin call the host
uv sync

uv run caremerge-addon serve  # terminal 1: the MCP add-on on http://127.0.0.1:8000/mcp
uv run caremerge-sim serve    # terminal 2: the simulated Alexa+ host on http://127.0.0.1:8765

cd apps/web                   # terminal 3: the screen on http://localhost:5173
pnpm install
pnpm dev
```

Try the demo at http://localhost:5173:

1. In the visit inbox, add Dr. Rivera's visit, ask "What's new from my visit with Dr. Rivera?", and say "Yes".
2. Add Dr. Lee's visit and ask "What's new from my visit with Dr. Lee?", then say "Yes".
3. Ask "What changed in my care plan?", "Should I take Medication A on Sunday, October 25?", and "Remind me to ask when the hold ends."

Every setting is a `CAREMERGE_`-prefixed environment variable; see [`.env.example`](.env.example) and spec §14.

Checks:

```sh
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src apps/addon/src apps/simulator/src
uv run pytest

cd apps/web
pnpm lint
pnpm typecheck
pnpm test
```

## Built during the hackathon

_TBD — everything in this repo was created during the submission window (from Oct 1, 2026) unless listed here._

## Repository layout

| Path | Purpose |
| --- | --- |
| [`packages/caremerge-core/`](packages/caremerge-core) | Domain model and deterministic engines: plan, diff, lint, questions, policy (no I/O) |
| [`apps/addon/`](apps/addon) | The CareMerge MCP add-on |
| [`apps/simulator/`](apps/simulator) | The simulated Alexa+ host and its local API |
| [`apps/web/`](apps/web) | The simulated Alexa+ screen (Vite + React) |
| [`fixtures/`](fixtures) | Synthetic visits and recorded extractions |
| [`CareMerge_Hackathon_Full_Specification.md`](CareMerge_Hackathon_Full_Specification.md) | Build spec: scope, contracts, build plan, risks (source of truth) |
| [`ideas.md`](ideas.md) | Idea backlog: out-of-the-box, moonshots, wow-factor, and real-product ideas (with market notes) |
| [`CLAUDE.md`](CLAUDE.md) | Project instructions for Claude Code: hackathon rules, constraints, working agreements |
| [`.claude/skills/`](.claude/skills) | `/friction-log` and `/submission-check` skills for Claude Code |
| [`.github/`](.github) | CI, issue forms, and pull request template |
| [`docs/submission-checklist.md`](docs/submission-checklist.md) | Every Devpost requirement, with a timeline |
| [`docs/friction-log.md`](docs/friction-log.md) | Friction log (up to a 10% judging bonus) |
| [`docs/product-feedback.md`](docs/product-feedback.md) | Required per-tool feedback and optional feature requests |
| [`docs/resources.md`](docs/resources.md) | Verified links per track: SDKs, samples, docs |
| [`docs/research/`](docs/research) | Research notes and the market report behind `ideas.md` |

## License

[MIT](LICENSE)
