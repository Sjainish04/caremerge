# Submission checklist

Devpost deadline: **Friday, Oct 23, 2026 @ 3:00 PM EDT** (19:00 UTC).
Target: submit on **Oct 22** and keep the last day as buffer.
Run `/submission-check` in Claude Code to audit the repo against this list.

## Suggested timeline

| Dates | Goal |
| --- | --- |
| Oct 1–3 | Pick the idea and track; spike the riskiest API call (auth + one real request) |
| Oct 4–14 | Build the core loop end to end, then widen |
| Oct 15–18 | Polish the demo path; freeze features; write the README and feedback |
| Oct 19–21 | Script, record, and edit the video; send reviewer invites if the repo is private |
| Oct 22 | Submit on Devpost; verify every link in an incognito window |

## Required

- [ ] **Text description** — what it does and how it works (draft lives in `README.md`)
- [ ] **Code repository** — all source, assets, and run instructions; a fresh clone runs by following the README
- [ ] **Repo access** — pick one:
  - [ ] **Public** with an open-source license (`LICENSE` is MIT), or
  - [ ] **Private**, shared with `testing@devpost.com` and the Amazon reviewers via Settings → Collaborators:
        `chris-trag`, `knmeiss`, `giolaq`, `anishamalde`, `mosesroth`, `emersonsklar`
        - Invitations **expire after 7 days** — send them at submission time, not earlier
        - Re-send any invitation that lapsed; check acceptance before the deadline
- [ ] **Track tech is called in code** (Alexa+, Bee, Ring) — an import, entry point, or loaded agent/flow/MCP config; a README mention does not count
  - Alexa+: Agent Skill or self-hosted MCP server (spec 2025-11-25+, Streamable HTTP) shown in action; the simulated-experience path still needs its source in the repo
  - Bee: the video **and** code show live Bee data doing something useful for a person
  - Ring: shown working through a simulator or a real Ring device
  - Fire TV: the video shows the app on a real Fire TV device or the Fire TV/Vega simulator
- [ ] **Demo video** — under 3 minutes, YouTube or Vimeo, public, in English
  - Best material in the first 30 seconds; judges need not watch past 3:00
  - No third-party trademarks or copyrighted music/footage without permission
- [ ] **Product feedback** for every tool/API/SDK used, AWS services included (`docs/product-feedback.md`)
- [ ] **Track and mini challenges** selected on the form (one track prize + one mini-challenge prize max per project)
- [ ] **Pre-existing work** — if anything existed before the window, explain what was built or changed during it
- [ ] **Eligibility** — every team member is above the age of majority in their country of residence

## Mini challenges (if entered)

- [ ] **AWS Builder** — AWS services used with documented integrations (where in the code, what each does)
- [ ] **Open Source** — a new open-source project (with license) or a contribution (branch, fork, or PR) to a public repo made during the window; provide:
  - [ ] Contribution URL
  - [ ] Our repo URL
  - [ ] GitHub username
  - [ ] Short description: what we did, how it works, why it matters

## Optional (worth it)

- [ ] **Friction log** entries (`docs/friction-log.md`) — up to a 10% judging bonus
- [ ] **Feature requests** with urgency (critical / important / nice-to-have) — in `docs/product-feedback.md`

## Final verification (Oct 22)

- [ ] Fresh clone → follow README → app runs
- [ ] Video plays logged-out, in an incognito window
- [ ] All Devpost links open; repo access confirmed for reviewers
- [ ] No secrets or personal data in git history (`git log -p | grep -iE "token|secret|api[_-]?key"` is clean)

## After submitting

- [ ] Keep every hosted backend, MCP endpoint, and demo account alive through judging — **Nov 9–20** per the rules and FAQ (the schedule page says Oct 26–Nov 20); winners around Dec 3
- [ ] Judging is a pass/fail stage, then 1–5 on four equally weighted criteria: Tech Implementation, Design, Potential Impact, Quality of the Idea
