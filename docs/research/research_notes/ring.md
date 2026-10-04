# Ring — research notes

Verified 2026-10-01 against primary pages. Re-check the linked docs before relying on a detail.
Docs base: `https://developer.amazon.com/docs/ring/` — abbreviated `…/` below.

## Bottom line

- The official **Amazon Vision API** (`https://api.amazonvision.com`) is **read-only**: devices, event history, live view, clips, snapshots, webhooks. **No** control of alarms, locks, lights, or sirens, and **no two-way talk** ([FAQ](https://developer.amazon.com/docs/ring/developer-faq.html)).
- Ring's own AI video descriptions are not exposed — *"Ring provides the pixels — add your own CV or AI models"* ([developer.ring.com](https://developer.ring.com/)).
- Demo without hardware via the **Playground** (released 2026-05-28): a sandbox token valid 30 minutes with simulated **Package, Vehicle, and Motion** events, no app or subscription needed ([release notes](https://developer.amazon.com/docs/ring/release-notes.html)). Whether it works for accounts with no devices or outside the US is UNVERIFIED. Build a replay harness that sends HMAC-signed webhooks so the demo is repeatable.
- **Uncovered gap: accessibility** (visual/haptic doorbell alerts, narrated snapshots). Business-system integrations and Ring → Home Assistant/Matter bridges are also open.

## Platform and lifecycle

- Landing: [developer.ring.com](https://developer.ring.com/) · console: `https://developer.amazon.com/ring/console` · [get started](https://developer.amazon.com/docs/ring/get-started.html). Appstore GA announced 2026-03-31 ([community](https://community.amazondeveloper.com/t/28126)).
- Configure: Client ID, Client Secret, HMAC key (each shown once); scopes (Cameras & Doorbells, Sensors, Chimes); Account Link URL, Token Exchange URL, Webhook URL, privacy/terms URLs ([configure](https://developer.amazon.com/docs/ring/configure.html)).
- Build with plain REST, or the **Ring knowledge MCP server** `https://knowledge.appstore-mcp.ring.amazon.dev/mcp` ([Ring MCP](https://developer.amazon.com/docs/ring/ring-mcp.html)).
- Test: up to 10 staging users, each needing a Ring Protection plan; US-located devices only ([develop](https://developer.amazon.com/docs/ring/develop.html)).
- Certify: Privacy & Legal questionnaire incl. "AI governance"; "90% < 48 hours" ([certify](https://developer.amazon.com/docs/ring/certify.html)). Publish: beta (≤ 10 users), gradual, or full; US-wide or chosen states ([publish](https://developer.amazon.com/docs/ring/publish.html)).
- **Private Apps** track skips certification for up to 10 accounts per the FAQ (release notes say 5).
- Anyone can register; government-ID verification before submitting. Free to publish; Ring takes a 10% fee. Distribution US-only ([program requirements](https://developer.amazon.com/docs/ring/program-requirements.html)).

## API ([reference](https://developer.amazon.com/docs/ring/api-documentation.html))

- **Auth:** OAuth 2.0, user-scoped, server-to-server only (browsers blocked by CORS). Ring-driven one-way linking: exchange the code at `oauth.ring.com/oauth/token` within 60 s, verify an HMAC nonce, then POST/PATCH `/v1/accounts/me/app-integrations`. Partner-initiated OAuth + PKCE is invitation-only. Only scope `ava.v1:read`. Access token ~4 h, refresh ~30 days. Devices need a Ring base plan to be shared.
- **Endpoints:** `GET /v1/devices` (+ `/status`, `/capabilities`, `/location`, `/configurations`); `GET /v1/history/devices/{id}/events` (post-consent only); WHEP live view (`POST …/media/streaming/whep/sessions`) or RTSPS — receive-only, capped at 30 s (battery) / 60 s (wired); MP4 clip download (≤ 15 min); JPEG/PNG snapshots; chime audio playback; `GET /v1/users/me`; `/v1/accounts/me/subscriptions`.
- **Media:** all media carries a non-removable watermark. TAKE-encrypted video unreadable; E2EE devices hidden.
- **Early Access** (can't publish until GA): sensors (contact, flood/freeze, temperature/humidity, air quality — standalone Sidewalk sensors, Sandbox/Test flow only) and chimes.
- **Webhooks:** `motion_detected` (sub_type `motion` / `human` / `vehicle` / `other_motion`), `button_press`, `device_added`/`removed`, `device_online`/`offline`, `app_integration_*`, `subscription_*`. HMAC-SHA256 in `X-Signature: sha256=…` over the raw body. Return 200 within 5 s; de-duplicate on `meta.request_id`; 7 retries over ~1 h, then a 72 h dead-letter queue. Smart Alerts settings and zones can silently suppress motion events.
- **Rate limit:** 100 req/s per `client_id` (429 + `Retry-After`).
- **SDKs:** none official. Unofficial libraries ([dgreif/ring](https://github.com/dgreif/ring), [python-ring-doorbell](https://github.com/python-ring-doorbell/python-ring-doorbell)) use reverse-engineered APIs and conflict with the "approved auth methods only" rule — don't use them for the entry.

## Starter: [AmazonAppDev/ring-api-helloworld](https://github.com/AmazonAppDev/ring-api-helloworld) (MIT)

- Python scripts for device, status, capabilities, location, configuration, history, and user endpoints.
- Next.js 14 / TypeScript app: WHEP live view, webhook dashboard over SSE, video-processor plugins (MediaPipe hand game, motion heatmap, brightness analyser). Runs on a Playground token or a refresh token.
- Friction-log material: the five README doc links return 404; README says webhook auth is a Bearer token, but the docs require HMAC signatures.

## Already live — avoid duplicating

Density Routines (elder care, falls, routine changes), Beside Care (elder care), QueueFlow (queues), StoreTraffic (foot traffic, lines), Lumeo (business alerts, people counting), Minut (rental hosts), WhatsThatBird.AI (bird ID), LawnWatch (lawn health), memories.ai (fire, smoke, falls, leaks), ProxView (loitering), Package Protect (packages), Visionify (workplace safety), Ring Cheer Chime (Toast tips), MySentry (panic-alarm live feed), Video Wall Live (multi-camera grid on TV). Another hackathon entrant is building "Porchlight" (caregiving on a contact sensor). Sources: [Ring blog](https://blog.ring.com/about-ring/introducing-the-ring-appstore-ring-cameras-just-got-smarter/), [TechCrunch](https://techcrunch.com/2026/03/31/ring-app-store-bets-on-ai-to-go-beyond-home-security/), [community](https://community.amazondeveloper.com/t/29248). The store catalogue loads client-side, so this list may be incomplete.

## UX rules ([UX design guide](https://developer.amazon.com/docs/ring/ux-design-guide.html))

- "Create Account" as the primary action; passwordless linking with the Ring email; never block linking on email verification.
- Post-link confirmation screen listing devices and status; skippable first-visit tutorial.
- Show device names, never IDs; keep offline devices visible but dimmed; useful empty states.
- Settings are read-only: explain problems as "what's wrong → why it matters → where to fix it in the Ring app".
- **Never display, analyse, or store privacy-zone areas.**
- Subscriptions only via Ring My Apps; refresh tokens silently; ≤ ~1 routine email/SMS per day; fine-grained notification controls; CAN-SPAM/TCPA.
- WCAG 2.2 AA; in-app data deletion.
- No "Ring" or "Amazon" in the product name; say "Compatible with Ring cameras", not "Built with Ring" ([marketing guidelines](https://developer.amazon.com/docs/ring/marketing-guidelines.html)).

## Policy constraints ([content policy](https://developer.amazon.com/docs/ring/content-policy.html), [program requirements](https://developer.amazon.com/docs/ring/program-requirements.html))

- Banned: stalking/covert access, tracking people or vehicles across accounts, matching faces to social media or plates to DMV records, watchlists, vigilante coordination, shaming, suspect registries, **apps aimed at children**.
- Facial recognition only for customer-enrolled people, with extra review ("may or may not be approved"); Ring's CEO said face recognition and plate reading won't be permitted ([TechCrunch](https://techcrunch.com/2026/03/31/ring-app-store-bets-on-ai-to-go-beyond-home-security/)).
- No standing law-enforcement access; per-request customer consent, revocable.
- Disclose retention; delete all copies including downstream; no marketing use without consent.
- **Nothing where a failure could cause death or injury (2.8)** — frame care ideas as awareness, not life safety. Alarm dispatch needs licences (2.19–2.20). Training AI on Ring data is a material change (§7).

## Friction-log candidates (bonus up to 10%)

Helloworld 404 links and webhook-auth mismatch; sandbox described in the glossary but undocumented; 5-vs-10 private-app limit; monthly-vs-annual billing; GA date conflict (release notes say "April 21, 2025"); staging devices returning 403 ([community](https://community.amazondeveloper.com/t/28731)).
