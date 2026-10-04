---
name: submission-check
description: Audit the repository against the Devpost submission requirements in docs/submission-checklist.md and report what is still missing.
disable-model-invocation: true
---

Audit this repo against `docs/submission-checklist.md` without modifying any files. Give each item one status:

- **done** — cite evidence (file path and line, or command output)
- **missing** — say what to add and where
- **human** — needs a person (video upload, Devpost form, collaborator invites); say exactly what to do

Verify, don't just read:

- `README.md` has no `_TBD_` left in "What it does", "How it works", and "Getting started".
- The primary track's technology is actually called in code: find the import, entry point, or loaded MCP/agent config and cite it.
- `docs/product-feedback.md` has a section for every SDK, API, and AWS service found in dependency manifests and code.
- `docs/friction-log.md` has at least one entry.
- `LICENSE` exists if the repo will be public.
- No secrets in tracked files or git history: scan `git log -p` for token/secret/key patterns and report the file and commit only, never the value.
- Days left until Friday, Oct 23, 2026, 3:00 PM EDT.

Output a table (item | status | evidence or next step), then the three most important next actions.
