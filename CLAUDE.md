# CLAUDE.md

Project instructions for Claude Code in this repository.

## Project

Entry for **Build, Ship, Shape: Amazon Developer Hackathon** (Devpost, online).

- **Deadline:** Friday, Oct 23, 2026, 3:00 PM EDT — target submitting on Oct 22.
- **Phase:** build. The product is **CareMerge**. `CareMerge_Hackathon_Full_Specification.md` (v2.0, Alexa+) is the source of truth for scope, contracts, and the build plan (§17), so read it before changing anything. v1.0 and v1.2 (Bee) are archived in `docs/archive/`.

## Decisions

- Idea: CareMerge — version control for care instructions, as an Alexa+ add-on
- Primary track: **Alexa+** (a self-hosted MCP add-on, demonstrated through a simulated Alexa+ experience) · Mini challenges: AWS Builder (Open Source optional, P2)
- Data: **synthetic visit transcripts only** (`fixtures/visits`). No Bee device, Apple Watch, or hardware purchase (decided Oct 4)
- Stack: Python 3.12 + uv (`packages/caremerge-core`, `apps/addon`, `apps/simulator`, `infra`); TypeScript + pnpm with Vite + React (`apps/web`)
- AWS: AgentCore Runtime hosting the MCP add-on (Cognito `CUSTOM_JWT`), Bedrock (Claude Opus 5.5 extracts, Claude Sonnet 5.5 plays Alexa), Strands, DynamoDB + KMS, Cognito, CDK
- Safety: templates speak and the model only routes; state-changing tools are MCP Apps app-only, so the model never sees them
- Repo: public, MIT (no reviewer invites needed)
- Team: Jainish Solanki (Track A — engine & cloud) and Siddhartha (Track B — experience); split and shared interfaces in spec §17.1. Since Oct 9, Claude builds both tracks

## Rules that constrain every design choice

- One primary track: Fire TV, Alexa+, Bee, or Ring. A project wins at most one track prize plus one mini-challenge prize.
- Alexa+, Bee, Ring: the track technology must be **called in code** — an import, an entry point, or a loaded agent/flow/MCP config. A README mention does not count.
  - Alexa+: a self-hosted MCP server on spec **2025-11-25 or later** over **Streamable HTTP**, or an Agent Skill — or a simulated Alexa+ web app whose source is in this repo.
  - Bee: must use **live Bee data** (Bee device or Apple Watch running Bee) through the Bee CLI, MCP, or Agent Skill, doing something useful for a person.
  - Ring: must work against the Ring APIs through a simulator or a real device.
- Fire TV: any framework (React Native, web, Kotlin/Java) on Fire OS or Vega OS; the video must show it on a real device or the Fire TV/Vega simulator.
- Demo video under 3 minutes. Build demo-first: every feature should earn a moment in the video, the strongest within the first 30 seconds. No copyrighted footage or music.
- Judging (Nov 9–20) is a pass/fail stage, then four equally weighted criteria: Tech Implementation, Design, Potential Impact, Quality of the Idea. Anything hosted must stay up until judging ends.
- AWS Builder: AWS services with documented integrations (Bedrock, AgentCore, Strands, Kiro, SageMaker). Open Source: a new OSS project with a license, or a contribution (branch, fork, PR) to a public repo, made during the window.
- Full requirement list: `docs/submission-checklist.md`.

## Working agreements

- **Re-verify platform facts before coding against them.** Fire TV/Vega, Alexa+, Bee, Ring, and AgentCore changed quickly in 2025–2026. `docs/resources.md` and `docs/research/` were verified on 2026-10-01; check the live docs before relying on a detail.
- **Log friction as it happens.** When Amazon or AWS tooling gets in the way, run `/friction-log` right away (friction logs earn up to a 10% judging bonus). Add every adopted tool to `docs/product-feedback.md`.
- **Personal data stays local.** Bee transcripts, Ring clips and snapshots, faces, and addresses live in `data/private/` (git-ignored) and never appear in commits, logs, fixtures, issues, or the demo video without consent. Tests use synthetic fixtures.
- **Configuration** goes through one typed settings module fed by environment variables; commit only a `.env.example` with placeholder values.
- Run `/submission-check` before submitting.

## Engineering conventions

Spec §15.2–15.3 is binding for both teammates. In short:

- Add dependencies only through package managers (`uv add`, `pnpm add`); never edit manifests or lockfiles by hand.
- **Nothing hard-coded.** Settings, defaults, timeouts, model IDs, thresholds, and table names live in the typed settings module (spec §14).
- Every external call (subprocess, AWS, HTTP) has a timeout taken from settings.
- Domain types are Pydantic models and Enums; ports are `Protocol`s. Each app has one composition root; no import-time clients, singletons, or global mutable state.
- `packages/caremerge-core` does no I/O; side effects live in adapters at the edges.
- Every module has a docstring. Errors are defined in the package that owns the failure.
- Logs are structured and content-free: IDs, counts, codes, latencies — never transcript text, quotes, or health details.
- Checks: Python — ruff, mypy `--strict`, pytest. Web — ESLint, `tsc --noEmit`, Vitest. Write tests first for `caremerge-core` engines.
- YAGNI: build only what a P0/P1 feature needs. Verify API and SDK details against current docs before relying on them.
- Collaboration: work on `a/<topic>` or `b/<topic>` branches and merge through PRs. Changes to `caremerge_core/contracts.py`, the MCP tool contract (spec §7.2), or the simulator API (spec §11) need the other track's review.

## Layout

Target layout: spec §15.1.

- `packages/caremerge-core` — domain and engines
- `apps/addon` — the CareMerge MCP add-on (AgentCore Runtime; local on port 8000)
- `apps/simulator` — the simulated Alexa+ host (orchestrator, confirmations, local API)
- `apps/web` — the Alexa+ simulator UI
- `infra/` — CDK
- `fixtures/` — synthetic data only
- `ideas.md` — the original idea backlog
- `docs/` — submission checklist, friction log, product feedback, resources, research, archive
- `.claude/skills/` — `/friction-log`, `/submission-check`
- `.github/` — issue forms and PR template
