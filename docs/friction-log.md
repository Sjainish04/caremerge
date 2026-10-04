# Friction log

Optional in the Devpost form, but **submissions with friction logs can earn up to a 10% judging bonus**.
Log friction the moment it happens — reconstructing it on submission day loses the exact errors and steps.
In Claude Code, `/friction-log <what went wrong>` appends an entry in this format.

Severity scale:

- **Blocker** — could not proceed without a workaround or outside help
- **High** — lost more than an hour, or had to change the design
- **Medium** — lost 15–60 minutes, or docs were wrong or misleading
- **Low** — paper cut: confusing naming, a missing example, a noisy warning

Rules: no tokens, keys, or personal data (Bee transcripts, Ring video details, addresses) in entries.

## Template

```markdown
### FL-000 — <short title>

- **Date:** YYYY-MM-DD
- **Tool / API / SDK + version:**
- **Task attempted:**
- **Steps taken:**
  1.
  2.
- **Expected:**
- **Actual:** <exact error text or behavior>
- **Severity:** Blocker | High | Medium | Low
- **Workaround:**
- **Actionable suggestion:** <what the Amazon/AWS team should change>
```

## Entries

<!-- Newest last. Number entries sequentially: FL-001, FL-002, ... -->
