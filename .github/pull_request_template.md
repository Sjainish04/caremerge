## What changed

<!-- One or two sentences. Link the issue if there is one. -->

## Why it matters for the demo

<!-- Which moment of the < 3-minute video does this enable or improve? "None" is a valid answer — then ask whether it belongs in this hackathon. -->

## Track requirement

- [ ] Touches the required track tech (Alexa+ MCP/Agent Skill, Bee CLI/MCP/Skill, Ring API, Fire TV/Vega app) — call path still works end to end
- [ ] Does not touch the required track tech

## Hygiene

- [ ] No secrets, tokens, or personal data (Bee transcripts, Ring clips, faces, addresses) in the diff
- [ ] Config read through the typed settings layer — no hardcoded IDs, URLs, timeouts, or model names
- [ ] Every external call has a timeout
- [ ] Friction hit while building this is logged in `docs/friction-log.md`
- [ ] New tools/SDKs used are listed in `docs/product-feedback.md`

## How I tested it

<!-- Commands run, device or simulator used, screenshots or a short clip. -->
