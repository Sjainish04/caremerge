# Product feedback

**Required** in the Devpost submission: feedback on *every* tool, API, or SDK used.
If we build with AWS services, describe which ones and how **in this answer** (it doubles as AWS Builder evidence).
Fill a section in as soon as a tool enters the project; polish wording at submission time.

## Template

```markdown
### <Tool / API / SDK name> (<version>)

- **What we used it for:**
- **What worked well:**
- **What needs work:**
- **Onboarding:** <time to first success, docs quality, sample quality>
- **Would we build with it again?** Yes / No / Maybe — because ...
```

## Tools

<!-- One section per tool. -->

### uv (0.10)

- **What we used it for:** the Python workspace (`packages/caremerge-core`, later `apps/*`), the lockfile, and `uv sync --locked` in CI.
- **What worked well:** `uv add` keeps `pyproject.toml` and `uv.lock` in step; locked installs make CI match local runs.
- **What needs work:** a plain `uv sync` does not install a workspace member unless the root project depends on it (or `--all-packages` is passed). Our first CI run would have failed; `uv add caremerge-core` at the root fixed it.
- **Onboarding:** familiar tool; the workspace docs answered the member-install question.
- **Would we build with it again?** Yes — fast and reproducible.

### Pydantic (2.13)

- **What we used it for:** frozen domain records and agent contracts (`extra="forbid"`), validators, and `AwareDatetime`.
- **What worked well:** strict validation at the trust boundary; malformed model output fails loudly.
- **What needs work:** a plain `datetime` field accepts naive values, which silently uses the host's zone downstream. Review caught it; we switched to `AwareDatetime`.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### ruff (0.16)

- **What we used it for:** formatting and linting (pydocstyle, bugbear, bandit, naming, pyupgrade rules).
- **What worked well:** N818 pushed exception names to the `Error` suffix; one tool replaces several.
- **What needs work:** 0.16 also formats Python code blocks inside Markdown, which flagged our archived spec. We excluded `*.md`.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### mypy (2.4, `--strict`, Pydantic plugin)

- **What we used it for:** strict type checks of `caremerge-core` in CI.
- **What worked well:** caught a `set` annotation receiving a `frozenset` before it shipped.
- **What needs work:** nothing blocking so far.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### pytest (9.1)

- **What we used it for:** table-driven unit tests of the core engines, written test-first.
- **What worked well:** parametrized cases keep the spec's scenarios readable.
- **What needs work:** nothing blocking so far.
- **Onboarding:** familiar tool.
- **Would we build with it again?** Yes.

### GitHub Actions (`actions/checkout@v7`, `astral-sh/setup-uv` v10.2.0)

- **What we used it for:** CI on every push and PR (format, lint, types, tests).
- **What worked well:** `setup-uv` plus `uv sync --locked` gives a short workflow file.
- **What needs work:** `astral-sh/setup-uv` publishes no floating major tags after v7, so `@v10` fails with "unable to find version `v10`" before any step runs. Its README pins a release commit SHA with a version comment; we do the same.
- **Onboarding:** familiar tool. The error was clear, but nothing local catches a bad action reference.
- **Would we build with it again?** Yes.

## AWS services used

<!-- Service → what it does in our architecture → link to the file that calls it. -->

## Feature requests (optional)

| What we want built | Why it matters | Urgency |
| --- | --- | --- |
| | | critical / important / nice-to-have |
