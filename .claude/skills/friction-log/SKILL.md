---
name: friction-log
description: Append a structured entry to docs/friction-log.md when an Amazon or AWS tool, SDK, API, doc, sample, or simulator gets in the way (Fire TV / Vega, Alexa+ / MCP, Bee, Ring, Bedrock, AgentCore, Strands, Kiro). Use when the user asks to log friction, or right after working around a confusing error, a missing or wrong doc, a broken sample, or a painful setup step in that tooling.
argument-hint: "[what went wrong]"
---

Append one entry to `docs/friction-log.md` under `## Entries`, following the template in that file.
The user's summary, if given: $ARGUMENTS

1. Read `docs/friction-log.md` and use the next number after the highest existing `FL-NNN`.
2. Fill every field from this conversation and terminal output: exact commands, links followed, and verbatim error text.
3. Pick the severity from the scale defined in the file.
4. Make the suggestion actionable for the Amazon/AWS team: name the page, command, or API and what should change.
5. Ask the user only for fields you cannot infer.
6. Never include tokens, keys, account IDs, or personal data (Bee transcripts, Ring video details, names, addresses).

If the friction came from our own code rather than Amazon/AWS tooling, say so and do not log it.
