# AWS Builder and Open Source mini challenges — research notes

Verified 2026-10-01. Re-check the linked docs before relying on a detail.

## Do these first

- **Request the $150 hackathon credits now** — the form closes **Oct 21, 12 PM PT**, is first-come-first-served, can take up to 5 business days, and declines answers that don't name a track ([form](https://forms.gle/GaHFxSbBQNG9Kti6A)). It asks for email, name, country, Devpost profile URL, track, and a 2–3 sentence project description; one code per participant.
- **Free-plan AWS accounts can't redeem promotional credits** and **AgentCore is "Paid plan exclusive"** ([free tier plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html), [aws.amazon.com/free](https://aws.amazon.com/free/)). Upgrade to the Paid plan before redeeming.
- Rules: describe which AWS services were used and how **in the Product Feedback answer**; one track prize + one mini-challenge prize per project ([rules](https://amazonappdev2026.devpost.com/rules)).

## Amazon Bedrock

- Claude: **Sonnet 5.5** (`global.anthropic.claude-sonnet-5-5`, Sep 28 2026, 1M context, text + image input — [card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5-5.html)), **Opus 5.5** (Sep 22 2026 — [card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5-5.html)). Fable 5.1 needs the `aws_review` data-retention opt-in; Mythos 5.1 is limited to vetted orgs. Claude needs a one-time Anthropic use-case form plus a Marketplace payment method ([model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)); Amazon's own models don't.
- **Nova 2 Lite** — GA Dec 2025; web grounding, code interpreter, remote MCP tools ([what's new](https://aws.amazon.com/about-aws/whats-new/2025/12/nova-2-foundation-models-amazon-bedrock/)).
- **Nova 2 Sonic** — speech-to-speech via `InvokeModelWithBidirectionalStream`; us-east-1, us-west-2, eu-north-1, ap-northeast-1; 20 concurrent sessions, not raisable ([card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-sonic.html)).
- **Nova Multimodal Embeddings** — text, documents, images, video, audio; us-east-1 ([blog](https://aws.amazon.com/blogs/aws/amazon-nova-multimodal-embeddings-now-available-in-amazon-bedrock/)).
- **Nova Act** — browser-automation agents, GA, us-east-1, $4.75 per agent-hour ([what's new](https://aws.amazon.com/about-aws/whats-new/2025/12/build-automate-production-ui-workflows-nova-act/), [pricing](https://aws.amazon.com/nova/pricing/)).
- **Image/video generation is mostly gone:** Nova Canvas and Nova Reel reached end-of-life **Sep 30 2026**; Titan Image Generator v2 on Jun 30 2026 ([Canvas card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-canvas.html), [Reel card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-reel.html)). Only Stability AI "Stable Image" edit/control/upscale tools remain listed. Nova 2 Omni (image generation) is preview for Nova Forge customers only — status UNVERIFIED.
- Useful features: [Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html), [Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) (not for Nova 2 Sonic), image input on Claude 5.x and Nova 2 Lite, long-term Bedrock API keys.

## Amazon Bedrock AgentCore

- GA since Oct 13 2025 ([what's new](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available/)). Components: Harness, Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability, Payments, Evaluations, Optimization, Policy, Registry ([overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), [release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html)).
- **Runtime hosts MCP servers over Streamable HTTP** (stateless or stateful; container serves `0.0.0.0:8000/mcp`): `npm i -g @aws/agentcore` → `agentcore add agent --protocol MCP` → `agentcore deploy`; OAuth (JWT) or IAM auth ([runtime MCP](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html)). Also A2A, AG-UI, WebSocket bidirectional streaming ([bidi](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-bidirectional-streaming.html)).
- **Gateway turns REST APIs, Lambda, OpenAPI, and Smithy into MCP tools**, with semantic tool search ([gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), [targets](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-targets-mcp.html)).
- Pricing: Runtime $0.0895/vCPU-hour + $0.00945/GB-hour; Gateway $0.005 per 1,000 calls; Web Search $7 per 1,000 queries ([pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)). No AgentCore-specific free tier.
- Whether Alexa+ could call an AgentCore Runtime endpoint directly is UNVERIFIED (Alexa+ wants < 500 ms tool round trips).

## Strands Agents SDK

- Python `strands-agents` 1.57.2 (Oct 1 2026, [PyPI](https://pypi.org/project/strands-agents/)); TypeScript `@strands-agents/sdk` 1.19.0 ([npm](https://www.npmjs.com/package/@strands-agents/sdk); TS 1.0 on Apr 30 2026). Apache-2.0 ([repo](https://github.com/strands-agents/harness-sdk)).
- MCP over stdio, SSE, and Streamable HTTP in both languages ([MCP transports](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-transports/)); agents-as-tools, A2A, Swarm, Graph, Workflow ([multi-agent](https://strandsagents.com/docs/user-guide/sdk/multi-agent/multi-agent-patterns/)).
- **Voice:** `from strands.bidi import BidiAgent` (Python only) with Nova Sonic, OpenAI Realtime, or Gemini Live ([bidi](https://strandsagents.com/docs/user-guide/sdk/bidi/)).

## Kiro and Kiro Crew

- **Kiro:** spec-driven agentic coding — IDE, CLI, web, Crew, mobile ([kiro.dev](https://kiro.dev/)); IDE/CLI GA Nov 17 2025.
- **Kiro Crew** (launched Aug 4 2026, [blog](https://kiro.dev/blog/introducing-kiro-crew/)): open source, Apache-2.0 ([kirodotdev/kirocrew](https://github.com/kirodotdev/kirocrew), v0.7.2). A persistent, self-learning agent workspace on your own hardware with memory, scheduled jobs, and Apps; used from a desktop app, web dashboard, CLI, or Slack/Discord ([docs](https://kiro.dev/docs/crew/)). The harness itself stays closed ([Forbes](https://www.forbes.com/sites/janakirammsv/2026/08/06/aws-open-sources-kiro-crew-but-keeps-the-agent-harness-closed/)).
- Install ([docs](https://kiro.dev/docs/crew/installation/)): `curl -fsSL https://download.crew.kiro.dev/cli.sh | sh` → `kirocrew setup` → `kirocrew doctor` → `kirocrew gateway` (localhost:5476). Drives the model through `kiro-cli`.
- **Its App registry is "curated through pull requests"** ([apps](https://kiro.dev/docs/crew/apps/)) — a Crew App PR can count toward both AWS Builder and Open Source (only one mini prize can be won).
- Pricing ([kiro.dev/pricing](https://kiro.dev/pricing/)): Free $0 / 50 credits; Pro $20 / 1,000; Pro+ $40 / 2,000; Pro Max $100 / 5,000; Power $200 / 10,000; overage $0.04/credit; subscription covers Crew. One user burned 5,000+ credits in a week on Crew ([report](https://www.playingaws.com/posts/what-is-kirocrew/)).

## AWS Free Tier

Since Jul 15 2025, new accounts get $100 at sign-up plus up to $100 for completing activities; the Free plan lasts 6 months or until credits run out ([blog](https://aws.amazon.com/blogs/aws/aws-free-tier-update-new-customers-can-get-started-and-explore-aws-with-up-to-200-in-credits/)).

## Hacktoberfest 2026

PRs/MRs no longer count (low-effort spam) ([FAQ](https://hacktoberfest.com/questions/)). Now: 300+ in-person Fests, DEV Challenges, MLH livestreams, Global Hack Week Oct 9–15 ([GHW](https://ghw.mlh.com/events/open-source)), virtual stickers. Theme: open-source AI and open-weight models ([hacktoberfest.com](https://hacktoberfest.com/)). The hackathon's Open Source mini challenge still accepts PRs — Hacktoberfest is independent.

## Cheapest credible AWS Builder paths

1. **Kiro Crew** ($0–$20) qualifies on its own per the rules — document specs, tasks, and schedules in the feedback answer.
2. **Bedrock with Nova 2 Lite / Nova 2 Sonic** — Amazon models avoid the Marketplace requirements.
3. **Strands + a Bedrock model** — a named Strands integration; `BidiAgent` adds voice.
4. **AgentCore Runtime hosting an MCP server** — needs the Paid plan plus credits.

## Open-source contribution targets

- **Fire TV:** a new Agent Skill for [AmazonAppDev/devices-agent-skills](https://github.com/AmazonAppDev/devices-agent-skills) (MIT, CONTRIBUTING.md, only 2 skills so far).
- **Alexa+:** an Apache-2.0 "Alexa+ MCP add-on on AWS" starter (Streamable HTTP 2025-11-25, MCP Apps UI, OAuth + PKCE, 500 ms latency test), upstreamable to [amazon-bedrock-agentcore-samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples).
- **Kiro Crew:** an App (e.g., Ring event triage, Bee daily review) PR'd to the [kirocrew](https://github.com/kirodotdev/kirocrew) registry.
- **Ring:** PR [ring-api-helloworld](https://github.com/AmazonAppDev/ring-api-helloworld) (MIT) with a webhook-verification helper or an **OpenAPI description of the Ring API** — which AgentCore Gateway can turn into MCP tools.
- **Bee:** PR [bee-cli](https://github.com/bee-computer/bee-cli) (MIT), e.g., a Kiro or Strands connector. [bee-skill](https://github.com/bee-computer/bee-skill) has no LICENSE file — a good small PR.
