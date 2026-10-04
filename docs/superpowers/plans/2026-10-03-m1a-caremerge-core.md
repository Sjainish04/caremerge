# M1a · caremerge-core Foundation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `caremerge-core`, the I/O-free domain library, inside a uv workspace with CI. It includes:

- typed agent contracts and stored records
- deterministic provenance checks
- the bitemporal plan view and CareDiff
- branch keys, question templates, and CareLint L002
- the Bee-write policy gate

Everything is fully tested, lint-clean, and strictly type-checked.

**Architecture:**

- A uv workspace at the repo root with one member, `packages/caremerge-core` (src layout, built with `uv_build`).
- Every engine is a pure function over immutable Pydantic models.
- Timezones, thresholds, and date windows are parameters supplied by callers, never module-level settings. The caller is the bridge, built in plan M1b.
- Tests are table-driven pytest suites, including the spec §9.5 golden diff.

**Tech stack:** Python 3.12 (uv-managed) · uv 0.10 workspaces · Pydantic 2.13 · pytest 9.1 · ruff 0.16 · mypy 2.4 (strict, Pydantic plugin) · GitHub Actions (`actions/checkout@v7`, `astral-sh/setup-uv@v10`).

**Spec:** `CareMerge_Hackathon_Full_Specification.md` v1.2:

- §8.4–8.5: contracts and validation
- §9: domain model and algorithms
- §14–15: configuration and conventions
- §16.1–16.2: tests and invariants

**Scope:** This is the first of two M1 plans for Track A. Plan M1b (next) builds `apps/bridge` and serves the FastAPI P0 API with `caremerge serve --fake`. It covers:

- settings
- `FakeBeeGateway`
- the stub extractor
- the in-memory repository
- the pipeline

**Verification status:** every command and code block below was run in a scratch copy on 2026-10-03. Results: 66 tests passing; ruff format and lint clean; `mypy --strict` clean on 13 source files.

## Global Constraints

Every task's requirements implicitly include this section.

**Toolchain**

- Python `3.12` is pinned in `.python-version`, with `requires-python = ">=3.12"`.
- Add dependencies only with `uv add`. Never edit dependency lists or `uv.lock` by hand. `[tool.*]` sections are configuration and are edited by hand.
- Checks that must pass after every task:
  - `uv run ruff format --check`
  - `uv run ruff check`
  - `uv run mypy packages/caremerge-core/src`
  - `uv run pytest`

**Design rules for `caremerge-core`**

- No I/O, no client construction, no global mutable state. Module constants are immutable (`frozenset`, `MappingProxyType`, `Final`).
- Thresholds, timezones, and windows are function parameters (spec §14): `min_quote_words: int`, `tz: ZoneInfo`, `window: DateWindow`.
- Every module and every public class or function has a docstring (ruff `D`, Google convention). Tests are exempt.
- Enum values are the wire format (spec §9.1). Contract and record models are frozen with `extra="forbid"`.
- Never expose a numeric confidence. Review signals are categorical (spec §8.4).
- User-facing sentences come only from `questions.TEMPLATES` (principle P9).
- Exception names end in `Error`: `TemplateError`, `PolicyViolationError`.

**Data semantics**

- `Effective.end` is the last day an instruction applies (inclusive).
- `Segment.end` is the first day after a run (exclusive).
- All test data is synthetic. Real Bee data never appears in the repo (spec §13.2).

**Commits**

- Use an imperative subject line.
- Commits use only the repo-local identity (`jainish.solanki@mail.utoronto.ca`); no other emails or IDs appear in commit messages.

## Review Focus

These five inputs are implied by the spec but not naturally exercised by feature tests. Each now has a pinning test in the task that owns the code.

1. **Late-evening capture.** A source captured late in the evening local time (after midnight UTC) must use the **local** capture date. Task 4, `test_capture_date_uses_the_local_timezone`.
2. **Window clipping.** A temporary change that began before the diff window and ends inside it must be clipped, then hand back to the persistent value. Task 4, `test_temporary_change_started_before_the_window_is_clipped`.
3. **Unverified candidates.** Candidates must never change the plan or the diff (F3 acceptance). Task 5, `test_unverified_candidates_never_change_the_diff`.
4. **Quote edge cases.** A quote containing a contraction must pass. A quote stitched across two utterances under one utterance ID must fail. Task 3, `test_contractions_match_after_normalization` and `test_a_quote_spanning_two_utterances_fails`.
5. **Braces in user text.** User-entered text containing braces (e.g., `{entity}`) must render literally, never as a template field. Task 6, `test_render_inserts_values_literally`.

## File Structure

```text
.python-version                       Python pin (3.12)
pyproject.toml                        uv workspace root; dev tools; ruff/mypy/pytest config
uv.lock                               lockfile, generated by uv
.github/workflows/ci.yml              format, lint, type-check, test on push and PR
packages/caremerge-core/
  pyproject.toml                      package metadata; depends on pydantic
  src/caremerge_core/
    __init__.py                       package docstring only
    py.typed                          PEP 561 marker (generated by uv)
    errors.py                         CareMergeError base class
    enums.py                          closed vocabularies (wire values)
    contracts.py                      agent contracts, shared with apps/agent later
    models.py                         stored records
    repository.py                     GraphSnapshot + CareGraphRepository Protocol
    provenance.py                     normalize, check_provenance
    plan.py                           DateWindow, Segment, known, schedule, plan_at
    diff.py                           DiffEntry, CareDiff, care_diff
    questions.py                      TEMPLATES, render, action_noun
    branches.py                       slug, branch_key
    lint.py                           LintFinding, lint (rule L002)
    policy.py                         PolicyCode, PolicyViolationError, check_bee_write
  tests/
    conftest.py                       make_commit builder fixture
    test_package.py
    test_types.py
    test_provenance.py
    test_plan.py
    test_diff.py
    test_branches_lint_questions.py
    test_policy.py
```

---

## Before Task 1: baseline commit and branch

Run every command from the repo root, `amazon-developer-hackathon/`.

- [ ] **Step 1: Confirm the starting point**

Run: `git status --short`
Expected: untracked `.claude/`, `.github/`, `.gitignore`, `CLAUDE.md`, `CareMerge_Hackathon_Full_Specification.md`, `LICENSE`, `README.md`, `docs/`, `ideas.md`, with no `pyproject.toml` and no commits yet.

- [ ] **Step 2: Commit the baseline on `main`**

```bash
git add -A
git commit -m "chore: add hackathon scaffold and CareMerge spec v1.2"
```

- [ ] **Step 3: Branch for Track A**

```bash
git switch -c a/m1-core
```

---

### Task 1: Workspace scaffold, tooling, and CI

**Files:**

- Create (via uv): `pyproject.toml`, `.python-version`, `uv.lock`, `packages/caremerge-core/pyproject.toml`, `packages/caremerge-core/src/caremerge_core/py.typed`
- Create, then replace: `packages/caremerge-core/src/caremerge_core/__init__.py`
- Create: `packages/caremerge-core/tests/test_package.py`, `.github/workflows/ci.yml`
- Modify: `pyproject.toml` (append the `[tool.*]` sections)

**Interfaces:**

- Consumes: nothing.
- Produces: an importable `caremerge_core` package, the workspace check commands from Global Constraints, and CI running them.

- [ ] **Step 1: Create the workspace root and pin Python**

```bash
uv init --bare --name caremerge-workspace --author-from none
uv python pin 3.12
```

Expected: `Initialized project \`caremerge-workspace\`` and `Pinned \`.python-version\` to \`3.12\``.

- [ ] **Step 2: Create the core package as a workspace member**

```bash
uv init --lib --name caremerge-core \
  --description "CareMerge domain model and deterministic engines (no I/O)" \
  --vcs none --no-readme --no-pin-python --author-from none \
  packages/caremerge-core
```

Expected: `Adding \`caremerge-core\` as member of workspace …`.

- `--vcs none` avoids a nested git repo.
- `--author-from none` keeps your email out of a public `pyproject.toml`.

- [ ] **Step 3: Add dependencies with uv**

```bash
uv add --package caremerge-core pydantic
uv add caremerge-core
uv add --dev pytest ruff mypy
```

Expected:

- `packages/caremerge-core/pyproject.toml` gains `pydantic>=2.13.5`.
- The root `pyproject.toml` gains:
  - `dependencies = ["caremerge-core"]`
  - `[tool.uv.sources] caremerge-core = { workspace = true }`
  - `[tool.uv.workspace] members = ["packages/caremerge-core"]`
  - a `[dependency-groups] dev` list

Why the root depends on the member: a plain `uv sync` installs only the root project and its dependencies. Verified on 2026-10-03, a fresh `uv sync --locked` without this line leaves `caremerge_core` uninstalled, and CI fails with `ModuleNotFoundError`. With the dependency in place, `uv sync` and `uv run` work with no extra flags.

- [ ] **Step 4: Append the tool configuration to the root `pyproject.toml`**

Append this block exactly (hand-edited configuration, not dependencies):

```toml

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "D", "N", "S", "SIM", "RUF"]
ignore = ["D105", "D107"]

[tool.ruff.lint.isort]
known-first-party = ["caremerge_core"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"**/tests/**" = ["D", "S101"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
testpaths = ["packages/caremerge-core/tests"]
addopts = ["-q", "--import-mode=importlib"]
```

- [ ] **Step 5: Write the failing smoke test**

Create `packages/caremerge-core/tests/test_package.py`:

```python
"""Smoke test: the package imports and documents itself."""

import caremerge_core


def test_package_has_a_docstring() -> None:
    assert caremerge_core.__doc__
```

- [ ] **Step 6: Run it and watch it fail**

Run: `uv run pytest packages/caremerge-core/tests/test_package.py`
Expected: FAIL. The uv-generated `__init__.py` contains a `hello()` stub and no module docstring.

- [ ] **Step 7: Replace the generated `__init__.py`**

Overwrite `packages/caremerge-core/src/caremerge_core/__init__.py` with exactly:

```python
"""CareMerge core: domain model and deterministic engines. Performs no I/O."""
```

- [ ] **Step 8: Run every check**

```bash
uv run pytest
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: `1 passed`; `2 files already formatted`; `All checks passed!`; `Success: no issues found in 1 source file`.

- [ ] **Step 9: Add CI**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v10
      - name: Install
        run: uv sync --locked
      - name: Format
        run: uv run ruff format --check
      - name: Lint
        run: uv run ruff check
      - name: Type-check
        run: uv run mypy packages/caremerge-core/src
      - name: Test
        run: uv run pytest
```

- [ ] **Step 10: Commit**

```bash
git add .python-version pyproject.toml uv.lock packages/caremerge-core .github/workflows/ci.yml
git commit -m "build: add uv workspace, caremerge-core package, and CI"
```

---

### Task 2: Domain vocabulary, agent contracts, records, and the repository port

**Files:**

- Create: `packages/caremerge-core/src/caremerge_core/errors.py`, `enums.py`, `contracts.py`, `models.py`, `repository.py`
- Test: `packages/caremerge-core/tests/conftest.py`, `packages/caremerge-core/tests/test_types.py`

**Interfaces:**

- Consumes: nothing beyond Task 1.
- Produces:
  - `caremerge_core.errors.CareMergeError(Exception)`
  - `caremerge_core.enums`:
    - content vocabularies: `CommitKind`, `MedAction`, `TimeOfDay`, `FoodRelation`, `Weekday`, `DateBasis`, `EntityMatch`, `Modality`, `SelfRating`, `SpeakerBasis`, `Role`, `BeeItemType`
    - workflow vocabularies: `ReviewState`, `Dimension`, `ChangeType`, `IssueKind`, `IssueStatus`, `LintCode`, `ActionState`, `TemplateId`
    - all are `StrEnum`s whose values are the wire format
  - `caremerge_core.contracts`: `Utterance(id, start_ms, text, speaker_hint)`, `SourcePayload`, `KnownEntity`, `EntityRef(match, entity_id)`, `Attributes`, `Effective(start, end, end_condition, date_basis, date_raw)`, `Evidence(utterance_id, quote)`, `CandidateCommit`, `CompileInput(source, known_entities, timezone)`, `CompileOutput(candidates)`
  - `caremerge_core.models`:
    - `ACTIVE_STATES`
    - `SourceEvent`, which has `.payload() -> SourcePayload`
    - `Entity`, `Signals`, `SourceRef`, `Review`, `Edges(branch)`
    - `CareCommit`, which has `.is_active -> bool`
    - `ReviewEvent`, `Issue`, `Action`
  - `caremerge_core.repository`:
    - `GraphSnapshot`, which has `.entity_names() -> dict[str, str]`
    - `CareGraphRepository(Protocol)` with `snapshot()`, `add_source(source) -> SourceEvent`, `put_entity`, `put_commit`, `append_review`, `put_issue`, `put_action`, `delete_all`
  - Test fixture `commit` returns `make_commit(commit_id="cc_1", *, kind, entity_id="ent_med_a", subject_text="Medication A", attributes, effective, temporary=False, context=None, captured_at=SCENE_1_AT, state=VERIFIED, source_id="src_1", **overrides) -> CareCommit`.

- [ ] **Step 1: Write the shared test builder**

Create `packages/caremerge-core/tests/conftest.py`:

```python
"""Shared builders for caremerge-core tests.

``make_commit`` builds a verified medication commit by default; tests
override only the fields they care about. Times are fixture dates from
spec §5.2 (scene 1 is captured on Oct 5).
"""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest

from caremerge_core.contracts import Attributes, Effective, Evidence
from caremerge_core.enums import (
    CommitKind,
    DateBasis,
    EntityMatch,
    Modality,
    ReviewState,
    Role,
    SelfRating,
    SpeakerBasis,
)
from caremerge_core.models import CareCommit, Review, Signals, SourceRef

SCENE_1_AT = datetime(2026, 10, 5, 14, 10, tzinfo=UTC)


def make_commit(
    commit_id: str = "cc_1",
    *,
    kind: CommitKind = CommitKind.MEDICATION_INSTRUCTION,
    entity_id: str = "ent_med_a",
    subject_text: str = "Medication A",
    attributes: Attributes | None = None,
    effective: Effective | None = None,
    temporary: bool = False,
    context: str | None = None,
    captured_at: datetime = SCENE_1_AT,
    state: ReviewState = ReviewState.VERIFIED,
    source_id: str = "src_1",
    **overrides: Any,
) -> CareCommit:
    """Build a commit with sensible defaults for tests."""
    commit = CareCommit(
        commit_id=commit_id,
        kind=kind,
        entity_id=entity_id,
        subject_text=subject_text,
        attributes=attributes or Attributes(),
        effective=effective or Effective(),
        temporary=temporary,
        context=context,
        modality=Modality.INSTRUCTION,
        source=SourceRef(
            source_id=source_id,
            role=Role.FAMILY_PHYSICIAN,
            label="Dr. Rivera",
            captured_at=captured_at,
            evidence=(Evidence(utterance_id="u_1", quote="keep taking Medication A"),),
        ),
        signals=Signals(
            date=DateBasis.NONE,
            entity=EntityMatch.MATCHED,
            speaker=SpeakerBasis.SESSION_LABEL,
            model=SelfRating.HIGH,
        ),
        review=Review(state=state, at=captured_at),
    )
    return commit.model_copy(update=overrides) if overrides else commit


@pytest.fixture
def commit() -> Callable[..., CareCommit]:
    """Return the ``make_commit`` builder."""
    return make_commit
```

- [ ] **Step 2: Write the failing type tests**

Create `packages/caremerge-core/tests/test_types.py`:

```python
"""Tests for contracts and stored models: validation and wire format."""

from collections.abc import Callable
from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from caremerge_core.contracts import (
    Attributes,
    CandidateCommit,
    Effective,
    EntityRef,
    Evidence,
    Utterance,
)
from caremerge_core.enums import (
    BeeItemType,
    CommitKind,
    EntityMatch,
    MedAction,
    Modality,
    ReviewState,
    Role,
    SelfRating,
)
from caremerge_core.models import CareCommit, SourceEvent


def _candidate(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "kind": "medication_instruction",
        "subject_text": "Medication A",
        "entity": {"match": "new"},
        "attributes": {"action": "hold"},
        "effective": {"start": "2026-10-25", "date_basis": "explicit"},
        "temporary": True,
        "context": "procedure",
        "modality": "instruction",
        "evidence": [{"utterance_id": "u_2", "quote": "hold Medication A starting Sunday"}],
        "self_rating": "high",
    }
    data.update(overrides)
    return data


def test_candidate_parses_wire_format() -> None:
    candidate = CandidateCommit.model_validate(_candidate())
    assert candidate.attributes.action is MedAction.HOLD
    assert candidate.effective.start == date(2026, 10, 25)
    assert candidate.entity == EntityRef(match=EntityMatch.NEW)


def test_candidate_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        CandidateCommit.model_validate(_candidate(evidence=[]))


def test_candidate_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CandidateCommit.model_validate(_candidate(confidence=0.97))


def test_candidate_rejects_unknown_enum_values() -> None:
    with pytest.raises(ValidationError):
        CandidateCommit.model_validate(_candidate(attributes={"action": "double"}))


def test_enums_serialize_as_plain_values() -> None:
    candidate = CandidateCommit(
        kind=CommitKind.MEDICATION_INSTRUCTION,
        subject_text="Medication A",
        entity=EntityRef(match=EntityMatch.NEW),
        attributes=Attributes(action=MedAction.CONTINUE),
        effective=Effective(),
        modality=Modality.INSTRUCTION,
        evidence=(Evidence(utterance_id="u_1", quote="keep taking Medication A"),),
        self_rating=SelfRating.HIGH,
    )
    dumped = candidate.model_dump(mode="json")
    assert dumped["kind"] == "medication_instruction"
    assert dumped["attributes"]["action"] == "continue"
    assert dumped["effective"]["date_basis"] == "none"


@pytest.mark.parametrize(
    ("state", "active"),
    [
        (ReviewState.CANDIDATE, False),
        (ReviewState.VERIFIED, True),
        (ReviewState.CORRECTED, True),
        (ReviewState.REJECTED, False),
    ],
)
def test_only_verified_or_corrected_commits_are_active(
    commit: Callable[..., CareCommit], state: ReviewState, active: bool
) -> None:
    assert commit(state=state).is_active is active


def test_source_payload_carries_only_minimized_fields() -> None:
    source = SourceEvent(
        source_id="src_1",
        bee_type=BeeItemType.CONVERSATION,
        bee_id="6531525",
        captured_at=datetime(2026, 10, 5, 14, 10, tzinfo=UTC),
        role=Role.FAMILY_PHYSICIAN,
        label="Dr. Rivera",
        utterances=(Utterance(id="u_1", start_ms=0, text="Keep taking Medication A."),),
        content_hash="sha256:abc",
    )
    payload = source.payload().model_dump()
    assert set(payload) == {"source_id", "captured_at", "role", "label", "utterances"}
```

- [ ] **Step 3: Run the tests and watch them fail**

Run: `uv run pytest packages/caremerge-core/tests/test_types.py`
Expected: FAIL during collection with `ModuleNotFoundError: No module named 'caremerge_core.contracts'` (raised by `conftest.py`).

- [ ] **Step 4: Write `errors.py`**

```python
"""Base error type for CareMerge core.

Specific errors live next to the code that raises them, such as
``TemplateError`` in ``questions`` and ``PolicyViolationError`` in ``policy``.
"""


class CareMergeError(Exception):
    """Base class for errors raised by caremerge-core."""
```

- [ ] **Step 5: Write `enums.py`**

```python
"""Closed vocabularies shared by every CareMerge component.

Enum values are the wire format: they appear unchanged in agent contracts,
the ledger, and the local API (spec §9.1).
"""

from enum import StrEnum


class CommitKind(StrEnum):
    """What a CareCommit describes."""

    MEDICATION_INSTRUCTION = "medication_instruction"
    MONITORING_INSTRUCTION = "monitoring_instruction"
    APPOINTMENT = "appointment"
    PROCEDURE = "procedure"
    TEST = "test"
    FOLLOW_UP = "follow_up"
    OBSERVATION = "observation"


class MedAction(StrEnum):
    """The action a medication instruction asks for."""

    CONTINUE = "continue"
    START = "start"
    STOP = "stop"
    HOLD = "hold"
    RESUME = "resume"


class TimeOfDay(StrEnum):
    """When in the day an instruction applies."""

    MORNING = "morning"
    MIDDAY = "midday"
    EVENING = "evening"
    BEDTIME = "bedtime"


class FoodRelation(StrEnum):
    """How an instruction relates to meals."""

    WITH_FOOD = "with_food"
    WITHOUT_FOOD = "without_food"


class Weekday(StrEnum):
    """Days of the week, in calendar order."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class DateBasis(StrEnum):
    """How a date was established from the source text."""

    EXPLICIT = "explicit"
    RELATIVE = "relative"
    NONE = "none"


class EntityMatch(StrEnum):
    """How confidently an extracted subject maps to a known entity."""

    MATCHED = "matched"
    POSSIBLE_MATCH = "possible_match"
    NEW = "new"
    AMBIGUOUS = "ambiguous"


class Modality(StrEnum):
    """What kind of statement the source made."""

    INSTRUCTION = "instruction"
    INFORMATION = "information"
    PATIENT_STATEMENT = "patient_statement"
    QUESTION = "question"


class SelfRating(StrEnum):
    """The extractor's own rating. Internal only; never shown as a number."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SpeakerBasis(StrEnum):
    """Where a commit's speaker role came from."""

    SESSION_LABEL = "session_label"
    CONTENT_INFERRED = "content_inferred"


class Role(StrEnum):
    """Care-team role the user assigns to a session at import."""

    FAMILY_PHYSICIAN = "family_physician"
    SPECIALIST = "specialist"
    PHARMACIST = "pharmacist"
    NURSE = "nurse"
    OTHER_CLINICIAN = "other_clinician"
    SELF = "self"


class BeeItemType(StrEnum):
    """The kind of Bee item a source was imported from."""

    CONVERSATION = "conversation"
    VOICE_NOTE = "voice_note"


class ReviewState(StrEnum):
    """Where a commit stands in user review."""

    CANDIDATE = "candidate"
    VERIFIED = "verified"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class Dimension(StrEnum):
    """A comparable aspect of a care item: the unit of plans and diffs."""

    ACTION = "action"
    DOSE = "dose"
    TIME_OF_DAY = "time_of_day"
    FOOD_RELATION = "food_relation"
    DAYS_OF_WEEK = "days_of_week"
    SCHEDULED_FOR = "scheduled_for"
    INTERVAL = "interval"


class ChangeType(StrEnum):
    """How a dimension's schedule changed between two knowledge points."""

    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"


class IssueKind(StrEnum):
    """Family of a clarification issue. Conflicts arrive with feature F9."""

    LINT = "lint"


class IssueStatus(StrEnum):
    """Lifecycle of a clarification issue."""

    OPEN = "open"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class LintCode(StrEnum):
    """CareLint rules implemented so far (spec §9.8)."""

    L002 = "L002"


class ActionState(StrEnum):
    """Lifecycle of a proposed Bee write."""

    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    EXECUTED = "executed"
    FAILED = "failed"


class TemplateId(StrEnum):
    """Registered user-facing text templates (principle P9)."""

    L002_MESSAGE = "l002_message"
    L002_QUESTION = "l002_question"
    L002_QUESTION_NO_CONTEXT = "l002_question_no_context"
    ASK_CARE_TEAM = "ask_care_team"
```

- [ ] **Step 6: Write `contracts.py`**

```python
"""Agent contracts: what the bridge sends for extraction and what comes back.

These models are shared by the bridge and the AgentCore agent (spec §8.2,
§8.5). They are a shared interface: changing them needs a review from both
tracks (spec §15.3). Unknown fields are rejected, so malformed model output
fails validation instead of slipping through.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from caremerge_core.enums import (
    CommitKind,
    DateBasis,
    EntityMatch,
    FoodRelation,
    MedAction,
    Modality,
    Role,
    SelfRating,
    TimeOfDay,
    Weekday,
)


class ContractModel(BaseModel):
    """Base for contract models: immutable and strict about unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Utterance(ContractModel):
    """One transcribed utterance from a Bee item."""

    id: str = Field(min_length=1)
    start_ms: int = Field(ge=0)
    text: str
    speaker_hint: str | None = None


class SourcePayload(ContractModel):
    """The minimized source sent for extraction (spec §7.5)."""

    source_id: str
    captured_at: datetime
    role: Role
    label: str
    utterances: tuple[Utterance, ...] = Field(min_length=1)


class KnownEntity(ContractModel):
    """An entity already in the ledger, offered so the extractor can match it."""

    entity_id: str
    display_name: str
    aliases: tuple[str, ...] = ()


class EntityRef(ContractModel):
    """How an extracted subject relates to the known entities."""

    match: EntityMatch
    entity_id: str | None = None


class Attributes(ContractModel):
    """Instruction details. Unknown values stay ``None``; nothing is inferred."""

    action: MedAction | None = None
    dose_text: str | None = None
    dose_quantity: float | None = None
    time_of_day: TimeOfDay | None = None
    food_relation: FoodRelation | None = None
    days_of_week: tuple[Weekday, ...] | None = None
    scheduled_for: date | None = None
    interval_text: str | None = None


class Effective(ContractModel):
    """Valid time of an instruction. ``end`` is the last day it applies."""

    start: date | None = None
    end: date | None = None
    end_condition: str | None = None
    date_basis: DateBasis = DateBasis.NONE
    date_raw: str | None = None


class Evidence(ContractModel):
    """A verbatim quote from one cited utterance."""

    utterance_id: str
    quote: str = Field(min_length=1)


class CandidateCommit(ContractModel):
    """One extracted care item, before validation and user review."""

    kind: CommitKind
    subject_text: str = Field(min_length=1)
    entity: EntityRef
    attributes: Attributes = Attributes()
    effective: Effective = Effective()
    temporary: bool = False
    context: str | None = None
    modality: Modality
    evidence: tuple[Evidence, ...] = Field(min_length=1)
    self_rating: SelfRating


class CompileInput(ContractModel):
    """Request body of the ``compile_source`` task."""

    source: SourcePayload
    known_entities: tuple[KnownEntity, ...] = ()
    timezone: str


class CompileOutput(ContractModel):
    """Response body of the ``compile_source`` task."""

    candidates: tuple[CandidateCommit, ...] = ()
```

- [ ] **Step 7: Write `models.py`**

```python
"""Stored domain records: sources, entities, commits, reviews, issues, actions.

Records are immutable. A state change produces a new instance (via
``model_copy(update=...)``) that the repository persists (spec §9.2, §10).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from caremerge_core.contracts import (
    Attributes,
    Effective,
    Evidence,
    SourcePayload,
    Utterance,
)
from caremerge_core.enums import (
    ActionState,
    BeeItemType,
    CommitKind,
    DateBasis,
    EntityMatch,
    IssueKind,
    IssueStatus,
    LintCode,
    Modality,
    ReviewState,
    Role,
    SelfRating,
    SpeakerBasis,
    TemplateId,
)

ACTIVE_STATES = frozenset({ReviewState.VERIFIED, ReviewState.CORRECTED})


class RecordModel(BaseModel):
    """Base for stored records: immutable and strict about unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceEvent(RecordModel):
    """A user-selected Bee item, minimized to what extraction needs."""

    source_id: str
    bee_type: BeeItemType
    bee_id: str
    captured_at: datetime
    role: Role
    label: str
    utterances: tuple[Utterance, ...] = Field(min_length=1)
    content_hash: str

    def payload(self) -> SourcePayload:
        """Return the contract payload sent to the extraction service."""
        return SourcePayload(
            source_id=self.source_id,
            captured_at=self.captured_at,
            role=self.role,
            label=self.label,
            utterances=self.utterances,
        )


class Entity(RecordModel):
    """A medication, measurement, event, or care relationship."""

    entity_id: str
    display_name: str
    aliases: tuple[str, ...] = ()


class Signals(RecordModel):
    """Categorical review signals shown instead of confidence numbers."""

    evidence: Literal["verified"] = "verified"
    date: DateBasis
    entity: EntityMatch
    speaker: SpeakerBasis
    model: SelfRating


class SourceRef(RecordModel):
    """Where a commit came from, with its verified evidence."""

    source_id: str
    role: Role
    label: str
    captured_at: datetime
    evidence: tuple[Evidence, ...] = Field(min_length=1)


class Review(RecordModel):
    """The commit's current review state."""

    state: ReviewState = ReviewState.CANDIDATE
    at: datetime | None = None


class Edges(RecordModel):
    """Stored relationships of a commit."""

    branch: str | None = None


class CareCommit(RecordModel):
    """One source-linked instruction or event (spec §9.2)."""

    commit_id: str
    kind: CommitKind
    entity_id: str
    subject_text: str
    attributes: Attributes
    effective: Effective
    temporary: bool
    context: str | None
    modality: Modality
    source: SourceRef
    signals: Signals
    review: Review = Review()
    edges: Edges = Edges()

    @property
    def is_active(self) -> bool:
        """Return whether the commit counts toward the plan."""
        return self.review.state in ACTIVE_STATES


class ReviewEvent(RecordModel):
    """Append-only audit record of a verify, correct, or reject decision."""

    commit_id: str
    state: ReviewState
    at: datetime
    attributes: Attributes | None = None
    effective: Effective | None = None


class Issue(RecordModel):
    """A clarification item with a templated, neutral question."""

    issue_id: str
    kind: IssueKind
    code: LintCode
    entity_id: str
    commit_ids: tuple[str, ...] = Field(min_length=1)
    status: IssueStatus
    message: str
    question: str
    created_at: datetime


class Action(RecordModel):
    """A proposed Bee write and, once executed, its receipt."""

    action_id: str
    template_id: TemplateId
    params: dict[str, str]
    text: str
    alarm_at: datetime
    issue_ids: tuple[str, ...] = ()
    commit_ids: tuple[str, ...] = ()
    state: ActionState = ActionState.PROPOSED
    confirmation_id: str | None = None
    bee_todo_id: str | None = None
    created_at: datetime
    executed_at: datetime | None = None
    error_code: str | None = None
```

- [ ] **Step 8: Write `repository.py`**

```python
"""The persistence port for the Care Graph ledger (spec §10).

Reads return the whole user partition as one snapshot; engines fold it in
memory. Writes are single-record and idempotent by ID. Adapters (in-memory,
DynamoDB) live in the bridge, so the core stays free of I/O.
"""

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from caremerge_core.models import (
    Action,
    CareCommit,
    Entity,
    Issue,
    ReviewEvent,
    SourceEvent,
)


class GraphSnapshot(BaseModel):
    """Every record in the user's partition at one moment."""

    model_config = ConfigDict(frozen=True)

    sources: tuple[SourceEvent, ...] = ()
    entities: tuple[Entity, ...] = ()
    commits: tuple[CareCommit, ...] = ()
    reviews: tuple[ReviewEvent, ...] = ()
    issues: tuple[Issue, ...] = ()
    actions: tuple[Action, ...] = ()

    def entity_names(self) -> dict[str, str]:
        """Map entity IDs to display names."""
        return {entity.entity_id: entity.display_name for entity in self.entities}


class CareGraphRepository(Protocol):
    """Storage for one user's Care Graph."""

    def snapshot(self) -> GraphSnapshot:
        """Return every record in the partition."""
        ...

    def add_source(self, source: SourceEvent) -> SourceEvent:
        """Store a source unless its Bee item exists; return the stored record."""
        ...

    def put_entity(self, entity: Entity) -> None:
        """Insert or replace an entity."""
        ...

    def put_commit(self, commit: CareCommit) -> None:
        """Insert or replace a commit."""
        ...

    def append_review(self, event: ReviewEvent) -> None:
        """Append a review event to the audit trail."""
        ...

    def put_issue(self, issue: Issue) -> None:
        """Insert or replace an issue."""
        ...

    def put_action(self, action: Action) -> None:
        """Insert or replace an action."""
        ...

    def delete_all(self) -> None:
        """Delete every record in the partition."""
        ...
```

- [ ] **Step 9: Run the tests**

Run: `uv run pytest`
Expected: `11 passed`.

- [ ] **Step 10: Run the remaining checks**

```bash
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: all clean (`Success: no issues found in 6 source files`).

- [ ] **Step 11: Commit**

```bash
git add packages/caremerge-core
git commit -m "feat(core): add vocabularies, agent contracts, records, and repository port"
```

---

### Task 3: Provenance checks

**Files:**

- Create: `packages/caremerge-core/src/caremerge_core/provenance.py`
- Test: `packages/caremerge-core/tests/test_provenance.py`

**Interfaces:**

- Consumes: `CandidateCommit`, `Evidence`, `Utterance`, `EntityRef` (Task 2).
- Produces:
  - `normalize(text: str) -> str`
  - `ProvenanceFailure` (StrEnum: `UNKNOWN_UTTERANCE`, `QUOTE_TOO_SHORT`, `QUOTE_NOT_IN_SOURCE`)
  - `ProvenanceResult(failures)`, which has `.ok -> bool`
  - `check_provenance(candidate, utterances, min_quote_words: int) -> ProvenanceResult`

- [ ] **Step 1: Write the failing tests**

Create `packages/caremerge-core/tests/test_provenance.py`:

```python
"""Tests for the deterministic evidence check (spec §8.4)."""

import pytest

from caremerge_core.contracts import CandidateCommit, EntityRef, Evidence, Utterance
from caremerge_core.enums import CommitKind, EntityMatch, Modality, SelfRating
from caremerge_core.provenance import ProvenanceFailure, check_provenance, normalize

UTTERANCES = (
    Utterance(id="u_1", start_ms=0, text="Your procedure is on Wednesday, October 28."),
    Utterance(
        id="u_2", start_ms=4200, text="Please hold Medication A starting Sunday, October 25."
    ),
)
MIN_WORDS = 3


def _with_quote(utterance_id: str, quote: str) -> CandidateCommit:
    return CandidateCommit(
        kind=CommitKind.MEDICATION_INSTRUCTION,
        subject_text="Medication A",
        entity=EntityRef(match=EntityMatch.NEW),
        modality=Modality.INSTRUCTION,
        evidence=(Evidence(utterance_id=utterance_id, quote=quote),),
        self_rating=SelfRating.HIGH,
    )


def test_normalize_ignores_case_punctuation_and_spacing() -> None:
    assert (
        normalize("  Hold   Medication-A, starting SUNDAY! ") == "hold medication a starting sunday"
    )


@pytest.mark.parametrize(
    "quote",
    [
        "hold Medication A starting Sunday, October 25",
        "HOLD medication a starting sunday october 25",
        "Please hold Medication A",
    ],
)
def test_faithful_quotes_pass(quote: str) -> None:
    assert check_provenance(_with_quote("u_2", quote), UTTERANCES, MIN_WORDS).ok


@pytest.mark.parametrize(
    ("utterance_id", "quote", "failure"),
    [
        ("u_9", "hold Medication A starting", ProvenanceFailure.UNKNOWN_UTTERANCE),
        ("u_2", "hold it", ProvenanceFailure.QUOTE_TOO_SHORT),
        ("u_2", "hold Medication A until Monday", ProvenanceFailure.QUOTE_NOT_IN_SOURCE),
        ("u_1", "hold Medication A starting", ProvenanceFailure.QUOTE_NOT_IN_SOURCE),
        ("u_2", "old Medication A starting", ProvenanceFailure.QUOTE_NOT_IN_SOURCE),
    ],
)
def test_unfaithful_quotes_fail(utterance_id: str, quote: str, failure: ProvenanceFailure) -> None:
    result = check_provenance(_with_quote(utterance_id, quote), UTTERANCES, MIN_WORDS)
    assert result.failures == (failure,)


def test_contractions_match_after_normalization() -> None:
    utterances = (
        Utterance(
            id="u_3",
            start_ms=0,
            text="Take Medication A with food. It's best taken in the evening.",
        ),
    )
    assert check_provenance(
        _with_quote("u_3", "it's best taken in the evening"), utterances, MIN_WORDS
    ).ok


def test_a_quote_spanning_two_utterances_fails() -> None:
    result = check_provenance(
        _with_quote("u_1", "October 28. Please hold Medication A"), UTTERANCES, MIN_WORDS
    )
    assert result.failures == (ProvenanceFailure.QUOTE_NOT_IN_SOURCE,)
```

- [ ] **Step 2: Run the tests and watch them fail**

Run: `uv run pytest packages/caremerge-core/tests/test_provenance.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'caremerge_core.provenance'`.

- [ ] **Step 3: Write `provenance.py`**

```python
"""Deterministic provenance checks for extracted candidates (spec §8.4).

A candidate survives only if every evidence quote appears, word for word,
in the utterance it cites. Matching ignores case and punctuation, so a
dropped comma doesn't reject a faithful quote. The words and their order
must still match exactly.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from caremerge_core.contracts import CandidateCommit, Utterance

_NON_WORD = re.compile(r"\W+")


def normalize(text: str) -> str:
    """Casefold, turn punctuation into spaces, and collapse whitespace."""
    return " ".join(_NON_WORD.sub(" ", text.casefold()).split())


class ProvenanceFailure(StrEnum):
    """Why an evidence quote was rejected."""

    UNKNOWN_UTTERANCE = "unknown_utterance"
    QUOTE_TOO_SHORT = "quote_too_short"
    QUOTE_NOT_IN_SOURCE = "quote_not_in_source"


@dataclass(frozen=True)
class ProvenanceResult:
    """Outcome of checking one candidate's evidence."""

    failures: tuple[ProvenanceFailure, ...]

    @property
    def ok(self) -> bool:
        """Return whether every quote passed."""
        return not self.failures


def check_provenance(
    candidate: CandidateCommit,
    utterances: Sequence[Utterance],
    min_quote_words: int,
) -> ProvenanceResult:
    """Check that each evidence quote is a whole-word substring of its utterance."""
    by_id = {utterance.id: utterance for utterance in utterances}
    failures: list[ProvenanceFailure] = []
    for evidence in candidate.evidence:
        cited = by_id.get(evidence.utterance_id)
        if cited is None:
            failures.append(ProvenanceFailure.UNKNOWN_UTTERANCE)
            continue
        quote = normalize(evidence.quote)
        if len(quote.split()) < min_quote_words:
            failures.append(ProvenanceFailure.QUOTE_TOO_SHORT)
            continue
        if f" {quote} " not in f" {normalize(cited.text)} ":
            failures.append(ProvenanceFailure.QUOTE_NOT_IN_SOURCE)
    return ProvenanceResult(tuple(failures))
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest`
Expected: `22 passed` (11 from earlier tasks plus 11 new).

- [ ] **Step 5: Run the remaining checks**

```bash
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add packages/caremerge-core
git commit -m "feat(core): verify evidence quotes against cited utterances"
```

---

### Task 4: Bitemporal plan view

**Files:**

- Create: `packages/caremerge-core/src/caremerge_core/plan.py`
- Test: `packages/caremerge-core/tests/test_plan.py`

**Interfaces:**

- Consumes: `CareCommit` (Task 2) and `normalize` (Task 3).
- Produces:
  - Constants: `EVENT_KINDS`, `DIMENSION_ORDER`.
  - `DateWindow(start, end)`: half-open; validation fails if `end <= start`.
  - `Segment(start, end, values, commit_ids, temporary, end_captured, origin_start)`, which has `.shape()`.
  - `PlanEntry(entity_id, dimension, values, commit_ids, temporary, end_captured)`.
  - `known(commits, before: datetime | None = None) -> list[CareCommit]`
  - `dimension_values(commit) -> dict[Dimension, str]`
  - `dimension_keys(commits) -> list[tuple[str, Dimension]]`
  - `valid_start(commit, tz) -> date`
  - `schedule(commits, entity_id, dimension, window, tz) -> tuple[Segment, ...]`
  - `plan_at(commits, day, tz) -> tuple[PlanEntry, ...]`

- [ ] **Step 1: Write the failing tests**

Create `packages/caremerge-core/tests/test_plan.py`:

```python
"""Tests for the bitemporal plan view (spec §9.4)."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from caremerge_core.contracts import Attributes, Effective
from caremerge_core.enums import (
    CommitKind,
    Dimension,
    MedAction,
    ReviewState,
    TimeOfDay,
    Weekday,
)
from caremerge_core.models import CareCommit
from caremerge_core.plan import DateWindow, dimension_values, known, plan_at, schedule

TZ = ZoneInfo("America/New_York")
SCENE_2_AT = datetime(2026, 10, 7, 18, 22, tzinfo=UTC)
WINDOW = DateWindow(start=date(2026, 10, 19), end=date(2026, 12, 18))
Builder = Callable[..., CareCommit]


def test_window_rejects_empty_ranges() -> None:
    with pytest.raises(ValidationError):
        DateWindow(start=date(2026, 10, 19), end=date(2026, 10, 19))


def test_known_keeps_active_commits_captured_before_the_cutoff(commit: Builder) -> None:
    early = commit("cc_early")
    late = commit("cc_late", captured_at=SCENE_2_AT)
    pending = commit("cc_pending", state=ReviewState.CANDIDATE)
    rejected = commit("cc_rejected", state=ReviewState.REJECTED)
    commits = [early, late, pending, rejected]
    assert known(commits) == [early, late]
    assert known(commits, before=SCENE_2_AT) == [early]


def test_dimension_values_cover_each_kind(commit: Builder) -> None:
    med = commit(
        attributes=Attributes(
            action=MedAction.CONTINUE, dose_text="One tablet,", time_of_day=TimeOfDay.MORNING
        )
    )
    monitoring = commit(
        kind=CommitKind.MONITORING_INSTRUCTION,
        attributes=Attributes(days_of_week=(Weekday.FRIDAY, Weekday.TUESDAY)),
    )
    procedure = commit(
        kind=CommitKind.PROCEDURE, attributes=Attributes(scheduled_for=date(2026, 10, 28))
    )
    follow_up = commit(kind=CommitKind.FOLLOW_UP, attributes=Attributes(interval_text="Four weeks"))
    observation = commit(kind=CommitKind.OBSERVATION)
    assert dimension_values(med) == {
        Dimension.ACTION: "continue",
        Dimension.DOSE: "one tablet",
        Dimension.TIME_OF_DAY: "morning",
    }
    assert dimension_values(monitoring) == {Dimension.DAYS_OF_WEEK: "tuesday,friday"}
    assert dimension_values(procedure) == {Dimension.SCHEDULED_FOR: "2026-10-28"}
    assert dimension_values(follow_up) == {Dimension.INTERVAL: "four weeks"}
    assert dimension_values(observation) == {}


def test_persistent_instruction_starts_on_its_capture_date(commit: Builder) -> None:
    keep = commit(attributes=Attributes(action=MedAction.CONTINUE))
    (segment,) = schedule([keep], "ent_med_a", Dimension.ACTION, WINDOW, TZ)
    assert (segment.start, segment.end, segment.values) == (WINDOW.start, WINDOW.end, ("continue",))
    assert segment.origin_start == date(2026, 10, 5)
    assert segment.temporary is False


def test_temporary_change_overrides_inside_its_interval(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    hold = commit(
        "cc_hold",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 25)),
        temporary=True,
        context="procedure",
        captured_at=SCENE_2_AT,
    )
    first, second = schedule([keep, hold], "ent_med_a", Dimension.ACTION, WINDOW, TZ)
    assert (first.start, first.end, first.values) == (
        WINDOW.start,
        date(2026, 10, 25),
        ("continue",),
    )
    assert (second.start, second.end, second.values) == (date(2026, 10, 25), WINDOW.end, ("hold",))
    assert second.temporary is True
    assert second.end_captured is False


def test_persistent_value_returns_after_a_temporary_end(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    hold = commit(
        "cc_hold",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 25), end=date(2026, 10, 29)),
        temporary=True,
    )
    segments = schedule([keep, hold], "ent_med_a", Dimension.ACTION, WINDOW, TZ)
    assert [(s.start, s.end, s.values) for s in segments] == [
        (WINDOW.start, date(2026, 10, 25), ("continue",)),
        (date(2026, 10, 25), date(2026, 10, 30), ("hold",)),
        (date(2026, 10, 30), WINDOW.end, ("continue",)),
    ]
    assert segments[1].end_captured is True


def test_disagreeing_persistent_instructions_keep_every_value(commit: Builder) -> None:
    morning = commit("cc_morning", attributes=Attributes(time_of_day=TimeOfDay.MORNING))
    evening = commit(
        "cc_evening", attributes=Attributes(time_of_day=TimeOfDay.EVENING), captured_at=SCENE_2_AT
    )
    (segment,) = schedule([morning, evening], "ent_med_a", Dimension.TIME_OF_DAY, WINDOW, TZ)
    assert segment.values == ("evening", "morning")
    assert segment.commit_ids == ("cc_evening", "cc_morning")


def test_plan_at_reports_the_value_on_a_given_day(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    hold = commit(
        "cc_hold",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 25)),
        temporary=True,
    )
    (before,) = plan_at([keep, hold], date(2026, 10, 24), TZ)
    (during,) = plan_at([keep, hold], date(2026, 10, 25), TZ)
    assert before.values == ("continue",)
    assert (during.values, during.temporary) == (("hold",), True)


def test_capture_date_uses_the_local_timezone(commit: Builder) -> None:
    late_evening = commit(
        attributes=Attributes(action=MedAction.CONTINUE),
        captured_at=datetime(2026, 10, 6, 2, 30, tzinfo=UTC),
    )
    (segment,) = schedule([late_evening], "ent_med_a", Dimension.ACTION, WINDOW, TZ)
    assert segment.origin_start == date(2026, 10, 5)


def test_temporary_change_started_before_the_window_is_clipped(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    hold = commit(
        "cc_hold",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 10), end=date(2026, 10, 21)),
        temporary=True,
    )
    segments = schedule([keep, hold], "ent_med_a", Dimension.ACTION, WINDOW, TZ)
    assert [(s.start, s.end, s.values) for s in segments] == [
        (WINDOW.start, date(2026, 10, 22), ("hold",)),
        (date(2026, 10, 22), WINDOW.end, ("continue",)),
    ]
    assert segments[0].origin_start == date(2026, 10, 10)
```

- [ ] **Step 2: Run the tests and watch them fail**

Run: `uv run pytest packages/caremerge-core/tests/test_plan.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'caremerge_core.plan'`.

- [ ] **Step 3: Write `plan.py`**

```python
"""Bitemporal plan view: which instruction values hold on which days (spec §9.4).

Knowledge time is when a commit's source was captured; valid time is the
commit's effective interval. ``known`` filters by knowledge time, and
``schedule`` lays one dimension's values out over a window of days, with
temporary commits overriding persistent ones inside their interval.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import pairwise
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, model_validator

from caremerge_core.enums import CommitKind, Dimension, Weekday
from caremerge_core.models import CareCommit
from caremerge_core.provenance import normalize

EVENT_KINDS = frozenset({CommitKind.APPOINTMENT, CommitKind.PROCEDURE, CommitKind.TEST})
DIMENSION_ORDER = {dimension: index for index, dimension in enumerate(Dimension)}
_WEEKDAY_ORDER = {day: index for index, day in enumerate(Weekday)}


class DateWindow(BaseModel):
    """Half-open range of days ``[start, end)``."""

    model_config = ConfigDict(frozen=True)

    start: date
    end: date

    @model_validator(mode="after")
    def _check_order(self) -> "DateWindow":
        if self.end <= self.start:
            msg = "window end must be after its start"
            raise ValueError(msg)
        return self


class Segment(BaseModel):
    """A run of days on which one dimension holds the same value(s).

    ``end`` is exclusive. More than one value means captured sources disagree.
    ``end_captured`` is False when a temporary change has no captured end.
    ``origin_start`` is the earliest valid start before clipping to the window.
    """

    model_config = ConfigDict(frozen=True)

    start: date
    end: date
    values: tuple[str, ...]
    commit_ids: tuple[str, ...]
    temporary: bool
    end_captured: bool
    origin_start: date

    def shape(self) -> tuple[date, date, tuple[str, ...], bool, bool]:
        """Return the fields that define a change, ignoring which commits said it."""
        return (self.start, self.end, self.values, self.temporary, self.end_captured)


class PlanEntry(BaseModel):
    """The value(s) of one entity dimension on one day."""

    model_config = ConfigDict(frozen=True)

    entity_id: str
    dimension: Dimension
    values: tuple[str, ...]
    commit_ids: tuple[str, ...]
    temporary: bool
    end_captured: bool


@dataclass(frozen=True)
class _Span:
    """One commit's value over its valid interval; ``end`` is exclusive or open."""

    start: date
    end: date | None
    value: str
    commit_id: str
    temporary: bool
    end_captured: bool

    def covers(self, lo: date, hi: date) -> bool:
        """Return whether the span covers every day in ``[lo, hi)``."""
        return self.start <= lo and (self.end is None or self.end >= hi)


def known(commits: Iterable[CareCommit], before: datetime | None = None) -> list[CareCommit]:
    """Return active commits, optionally only those captured before ``before``."""
    return [
        commit
        for commit in commits
        if commit.is_active and (before is None or commit.source.captured_at < before)
    ]


def dimension_values(commit: CareCommit) -> dict[Dimension, str]:
    """Return the comparable values a commit states, keyed by dimension."""
    attrs = commit.attributes
    values: dict[Dimension, str | None]
    if commit.kind is CommitKind.MEDICATION_INSTRUCTION:
        values = {
            Dimension.ACTION: attrs.action,
            Dimension.DOSE: normalize(attrs.dose_text) if attrs.dose_text else None,
            Dimension.TIME_OF_DAY: attrs.time_of_day,
            Dimension.FOOD_RELATION: attrs.food_relation,
        }
    elif commit.kind is CommitKind.MONITORING_INSTRUCTION:
        days = sorted(attrs.days_of_week or (), key=_WEEKDAY_ORDER.__getitem__)
        values = {Dimension.DAYS_OF_WEEK: ",".join(days) or None}
    elif commit.kind in EVENT_KINDS:
        scheduled = attrs.scheduled_for
        values = {Dimension.SCHEDULED_FOR: scheduled.isoformat() if scheduled else None}
    elif commit.kind is CommitKind.FOLLOW_UP:
        scheduled = attrs.scheduled_for
        values = {
            Dimension.SCHEDULED_FOR: scheduled.isoformat() if scheduled else None,
            Dimension.INTERVAL: normalize(attrs.interval_text) if attrs.interval_text else None,
        }
    else:
        values = {}
    return {dimension: str(value) for dimension, value in values.items() if value is not None}


def dimension_keys(commits: Iterable[CareCommit]) -> list[tuple[str, Dimension]]:
    """Return each (entity, dimension) pair the commits state, in stable order."""
    keys = {
        (commit.entity_id, dimension)
        for commit in commits
        for dimension in dimension_values(commit)
    }
    return sorted(keys, key=lambda key: (key[0], DIMENSION_ORDER[key[1]]))


def valid_start(commit: CareCommit, tz: ZoneInfo) -> date:
    """Return the first day a commit applies: its stated start or its capture date."""
    return commit.effective.start or commit.source.captured_at.astimezone(tz).date()


def schedule(
    commits: Sequence[CareCommit],
    entity_id: str,
    dimension: Dimension,
    window: DateWindow,
    tz: ZoneInfo,
) -> tuple[Segment, ...]:
    """Lay out one entity dimension's values over ``window``.

    Temporary commits override persistent ones inside their interval (a branch).
    Overlapping persistent commits with different values yield one segment
    holding every value; detecting that as a conflict is feature F9.
    """
    spans = [
        _span(commit, value, tz)
        for commit in commits
        if commit.entity_id == entity_id
        and (value := dimension_values(commit).get(dimension)) is not None
    ]
    cuts = {window.start, window.end}
    for span in spans:
        cuts.update(
            day for day in (span.start, span.end) if day and window.start < day < window.end
        )
    pieces = [
        piece for lo, hi in pairwise(sorted(cuts)) if (piece := _piece(spans, lo, hi)) is not None
    ]
    return tuple(_merge(pieces))


def plan_at(commits: Sequence[CareCommit], day: date, tz: ZoneInfo) -> tuple[PlanEntry, ...]:
    """Return every entity dimension's value(s) on ``day``."""
    window = DateWindow(start=day, end=day + timedelta(days=1))
    entries: list[PlanEntry] = []
    for entity_id, dimension in dimension_keys(commits):
        segments = schedule(commits, entity_id, dimension, window, tz)
        if segments:
            segment = segments[0]
            entries.append(
                PlanEntry(
                    entity_id=entity_id,
                    dimension=dimension,
                    values=segment.values,
                    commit_ids=segment.commit_ids,
                    temporary=segment.temporary,
                    end_captured=segment.end_captured,
                )
            )
    return tuple(entries)


def _span(commit: CareCommit, value: str, tz: ZoneInfo) -> _Span:
    effective = commit.effective
    return _Span(
        start=valid_start(commit, tz),
        end=effective.end + timedelta(days=1) if effective.end else None,
        value=value,
        commit_id=commit.commit_id,
        temporary=commit.temporary,
        end_captured=effective.end is not None or effective.end_condition is not None,
    )


def _piece(spans: Sequence[_Span], lo: date, hi: date) -> Segment | None:
    covering = [span for span in spans if span.covers(lo, hi)]
    temporary = [span for span in covering if span.temporary]
    chosen = temporary or covering
    if not chosen:
        return None
    return Segment(
        start=lo,
        end=hi,
        values=tuple(sorted({span.value for span in chosen})),
        commit_ids=tuple(sorted({span.commit_id for span in chosen})),
        temporary=bool(temporary),
        end_captured=all(span.end_captured for span in temporary),
        origin_start=min(span.start for span in chosen),
    )


def _merge(pieces: Sequence[Segment]) -> list[Segment]:
    merged: list[Segment] = []
    for piece in pieces:
        last = merged[-1] if merged else None
        if (
            last is not None
            and last.end == piece.start
            and (last.values, last.temporary, last.end_captured)
            == (piece.values, piece.temporary, piece.end_captured)
        ):
            merged[-1] = last.model_copy(
                update={
                    "end": piece.end,
                    "commit_ids": tuple(sorted({*last.commit_ids, *piece.commit_ids})),
                    "origin_start": min(last.origin_start, piece.origin_start),
                }
            )
        else:
            merged.append(piece)
    return merged
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest`
Expected: `32 passed`.

- [ ] **Step 5: Run the remaining checks**

```bash
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add packages/caremerge-core
git commit -m "feat(core): add bitemporal plan view with temporary overrides"
```

---

### Task 5: CareDiff

**Files:**

- Create: `packages/caremerge-core/src/caremerge_core/diff.py`
- Test: `packages/caremerge-core/tests/test_diff.py`

**Interfaces:**

- Consumes: `DIMENSION_ORDER`, `DateWindow`, `Segment`, `dimension_keys`, `known`, `schedule` (Task 4).
- Produces:
  - `DiffEntry(entity_id, dimension, change, before, after, future_effective, temporary, end_not_captured)`
  - `CareDiff(window, entries)`
  - `care_diff(commits, *, known_before: datetime | None, window, tz, entity_names) -> CareDiff`

- [ ] **Step 1: Write the failing tests**

Create `packages/caremerge-core/tests/test_diff.py`:

```python
"""Tests for CareDiff, including the spec §9.5 golden expectation."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from caremerge_core.contracts import Attributes, Effective
from caremerge_core.diff import care_diff
from caremerge_core.enums import (
    ChangeType,
    CommitKind,
    Dimension,
    MedAction,
    ReviewState,
    TimeOfDay,
    Weekday,
)
from caremerge_core.models import CareCommit
from caremerge_core.plan import DateWindow

TZ = ZoneInfo("America/New_York")
SCENE_2_AT = datetime(2026, 10, 7, 18, 22, tzinfo=UTC)
WINDOW = DateWindow(start=date(2026, 10, 19), end=date(2026, 12, 18))
NAMES = {
    "ent_med_a": "Medication A",
    "ent_bp": "Blood pressure",
    "ent_procedure": "Procedure",
}
Builder = Callable[..., CareCommit]


def _scenes(commit: Builder) -> list[CareCommit]:
    scene_1 = [
        commit(
            "cc_keep",
            attributes=Attributes(
                action=MedAction.CONTINUE, dose_text="one tablet", time_of_day=TimeOfDay.MORNING
            ),
        ),
        commit(
            "cc_bp",
            kind=CommitKind.MONITORING_INSTRUCTION,
            entity_id="ent_bp",
            subject_text="blood pressure",
            attributes=Attributes(days_of_week=(Weekday.TUESDAY, Weekday.FRIDAY)),
        ),
    ]
    scene_2 = [
        commit(
            "cc_procedure",
            kind=CommitKind.PROCEDURE,
            entity_id="ent_procedure",
            subject_text="procedure",
            attributes=Attributes(scheduled_for=date(2026, 10, 28)),
            captured_at=SCENE_2_AT,
            source_id="src_2",
        ),
        commit(
            "cc_hold",
            attributes=Attributes(action=MedAction.HOLD),
            effective=Effective(start=date(2026, 10, 25)),
            temporary=True,
            context="procedure",
            captured_at=SCENE_2_AT,
            source_id="src_2",
        ),
    ]
    return scene_1 + scene_2


def test_golden_diff_after_the_specialist_visit(commit: Builder) -> None:
    diff = care_diff(
        _scenes(commit), known_before=SCENE_2_AT, window=WINDOW, tz=TZ, entity_names=NAMES
    )
    assert [(e.entity_id, e.dimension, e.change) for e in diff.entries] == [
        ("ent_med_a", Dimension.ACTION, ChangeType.CHANGED),
        ("ent_procedure", Dimension.SCHEDULED_FOR, ChangeType.ADDED),
    ]
    action = diff.entries[0]
    (old,) = action.before
    assert (old.values, old.origin_start) == (("continue",), date(2026, 10, 5))
    kept, held = action.after
    assert (kept.values, kept.end) == (("continue",), date(2026, 10, 25))
    assert (held.values, held.start, held.temporary, held.end_captured) == (
        ("hold",),
        date(2026, 10, 25),
        True,
        False,
    )
    assert (action.future_effective, action.temporary, action.end_not_captured) == (
        True,
        True,
        True,
    )
    procedure = diff.entries[1]
    assert procedure.after[0].values == ("2026-10-28",)


def test_restating_an_instruction_is_not_a_change(commit: Builder) -> None:
    first = commit("cc_first", attributes=Attributes(action=MedAction.CONTINUE))
    again = commit(
        "cc_again",
        attributes=Attributes(action=MedAction.CONTINUE),
        captured_at=SCENE_2_AT,
        source_id="src_2",
    )
    diff = care_diff(
        [first, again], known_before=SCENE_2_AT, window=WINDOW, tz=TZ, entity_names=NAMES
    )
    assert diff.entries == ()


def test_first_session_shows_everything_as_added(commit: Builder) -> None:
    diff = care_diff(_scenes(commit), known_before=None, window=WINDOW, tz=TZ, entity_names=NAMES)
    assert {entry.change for entry in diff.entries} == {ChangeType.ADDED}
    assert diff.entries[0].entity_id == "ent_bp"


def test_unverified_candidates_never_change_the_diff(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    pending = commit(
        "cc_pending",
        attributes=Attributes(action=MedAction.STOP),
        captured_at=SCENE_2_AT,
        state=ReviewState.CANDIDATE,
    )
    diff = care_diff(
        [keep, pending], known_before=SCENE_2_AT, window=WINDOW, tz=TZ, entity_names=NAMES
    )
    assert diff.entries == ()
```

- [ ] **Step 2: Run the tests and watch them fail**

Run: `uv run pytest packages/caremerge-core/tests/test_diff.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'caremerge_core.diff'`.

- [ ] **Step 3: Write `diff.py`**

```python
"""CareDiff: what changed in the plan between two knowledge points (spec §9.5).

The diff compares schedules computed from what was known *before* a moment
with what is known now, over the same window of days. Output order is
deterministic: entity name, then dimension order.
"""

from collections.abc import Mapping, Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict

from caremerge_core.enums import ChangeType, Dimension
from caremerge_core.models import CareCommit
from caremerge_core.plan import (
    DIMENSION_ORDER,
    DateWindow,
    Segment,
    dimension_keys,
    known,
    schedule,
)


class DiffEntry(BaseModel):
    """How one entity dimension's schedule changed."""

    model_config = ConfigDict(frozen=True)

    entity_id: str
    dimension: Dimension
    change: ChangeType
    before: tuple[Segment, ...]
    after: tuple[Segment, ...]
    future_effective: bool
    temporary: bool
    end_not_captured: bool


class CareDiff(BaseModel):
    """Every changed entity dimension within a window."""

    model_config = ConfigDict(frozen=True)

    window: DateWindow
    entries: tuple[DiffEntry, ...]


def care_diff(
    commits: Sequence[CareCommit],
    *,
    known_before: datetime | None,
    window: DateWindow,
    tz: ZoneInfo,
    entity_names: Mapping[str, str],
) -> CareDiff:
    """Compare the plan known before ``known_before`` with the plan known now.

    With ``known_before=None`` nothing counts as previously known, so every
    stated dimension appears as added.
    """
    before = known(commits, before=known_before) if known_before else []
    after = known(commits)
    keys = sorted(
        set(dimension_keys(before)) | set(dimension_keys(after)),
        key=lambda key: (entity_names.get(key[0], key[0]).casefold(), DIMENSION_ORDER[key[1]]),
    )
    entries = [
        entry
        for entity_id, dimension in keys
        if (entry := _entry(before, after, entity_id, dimension, window, tz)) is not None
    ]
    return CareDiff(window=window, entries=tuple(entries))


def _entry(
    before: Sequence[CareCommit],
    after: Sequence[CareCommit],
    entity_id: str,
    dimension: Dimension,
    window: DateWindow,
    tz: ZoneInfo,
) -> DiffEntry | None:
    old = schedule(before, entity_id, dimension, window, tz)
    new = schedule(after, entity_id, dimension, window, tz)
    old_shapes = {segment.shape() for segment in old}
    if old_shapes == {segment.shape() for segment in new}:
        return None
    changed = [segment for segment in new if segment.shape() not in old_shapes]
    if not old:
        change = ChangeType.ADDED
    elif not new:
        change = ChangeType.REMOVED
    else:
        change = ChangeType.CHANGED
    return DiffEntry(
        entity_id=entity_id,
        dimension=dimension,
        change=change,
        before=old,
        after=new,
        future_effective=any(segment.start > window.start for segment in changed),
        temporary=any(segment.temporary for segment in changed),
        end_not_captured=any(segment.temporary and not segment.end_captured for segment in changed),
    )
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest`
Expected: `36 passed`.

- [ ] **Step 5: Run the remaining checks**

```bash
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add packages/caremerge-core
git commit -m "feat(core): add CareDiff with the spec golden scenario"
```

---

### Task 6: Question templates, branch keys, and CareLint L002

**Files:**

- Create: `packages/caremerge-core/src/caremerge_core/questions.py`, `branches.py`, `lint.py`
- Test: `packages/caremerge-core/tests/test_branches_lint_questions.py`

**Interfaces:**

- Consumes: `CareMergeError` (Task 2), `normalize` (Task 3), `EVENT_KINDS` (Task 4), and the records and enums from Task 2.
- Produces:
  - `questions`:
    - `TEMPLATES: Mapping[TemplateId, str]`
    - `TemplateError(template_id, missing, unexpected)`
    - `template_fields(template_id) -> frozenset[str]`
    - `render(template_id, params) -> str`
    - `action_noun(action: MedAction | None) -> str`
  - `branches`:
    - `slug(text) -> str`
    - `branch_key(candidate, siblings) -> str | None`
  - `lint`:
    - `LintFinding(code, entity_id, commit_ids, message_template, question_template, params)`, which has `.key`
    - `lint(commits, entity_names) -> list[LintFinding]`

- [ ] **Step 1: Write the failing tests**

Create `packages/caremerge-core/tests/test_branches_lint_questions.py`:

```python
"""Tests for branch keys, question templates, and CareLint L002."""

from collections.abc import Callable
from datetime import date

import pytest

from caremerge_core.branches import branch_key, slug
from caremerge_core.contracts import (
    Attributes,
    CandidateCommit,
    Effective,
    EntityRef,
    Evidence,
)
from caremerge_core.enums import (
    CommitKind,
    EntityMatch,
    LintCode,
    MedAction,
    Modality,
    ReviewState,
    SelfRating,
    TemplateId,
)
from caremerge_core.lint import lint
from caremerge_core.models import CareCommit
from caremerge_core.questions import TemplateError, action_noun, render

Builder = Callable[..., CareCommit]


def _candidate(
    kind: CommitKind,
    subject: str,
    *,
    temporary: bool = False,
    context: str | None = None,
    scheduled_for: date | None = None,
) -> CandidateCommit:
    return CandidateCommit(
        kind=kind,
        subject_text=subject,
        entity=EntityRef(match=EntityMatch.NEW),
        attributes=Attributes(scheduled_for=scheduled_for),
        temporary=temporary,
        context=context,
        modality=Modality.INSTRUCTION,
        evidence=(Evidence(utterance_id="u_1", quote="your procedure is on"),),
        self_rating=SelfRating.HIGH,
    )


HOLD = _candidate(
    CommitKind.MEDICATION_INSTRUCTION, "Medication A", temporary=True, context="Procedure"
)
PROCEDURE = _candidate(CommitKind.PROCEDURE, "procedure", scheduled_for=date(2026, 10, 28))
CLEANING = _candidate(CommitKind.APPOINTMENT, "dental cleaning", scheduled_for=date(2026, 11, 2))


def test_slug_is_lowercase_and_hyphenated() -> None:
    assert slug("Knee  Procedure!") == "knee-procedure"


@pytest.mark.parametrize(
    ("candidate", "siblings", "expected"),
    [
        (HOLD, [HOLD, PROCEDURE], "procedure-2026-10-28"),
        (HOLD, [HOLD, CLEANING, PROCEDURE], "procedure-2026-10-28"),
        (HOLD, [HOLD, CLEANING], "procedure-2026-11-02"),
        (HOLD, [HOLD], "procedure"),
        (PROCEDURE, [HOLD, PROCEDURE], None),
    ],
)
def test_branch_key(
    candidate: CandidateCommit, siblings: list[CandidateCommit], expected: str | None
) -> None:
    assert branch_key(candidate, siblings) == expected


def test_render_fills_exactly_the_template_fields() -> None:
    text = render(
        TemplateId.L002_QUESTION,
        {"action_noun": "hold", "entity": "Medication A", "context": "procedure"},
    )
    assert text == "When should the temporary hold of Medication A for the procedure end?"


@pytest.mark.parametrize(
    "params",
    [
        {"action_noun": "hold", "entity": "Medication A"},
        {"action_noun": "hold", "entity": "Medication A", "context": "x", "dose": "y"},
    ],
)
def test_render_rejects_mismatched_params(params: dict[str, str]) -> None:
    with pytest.raises(TemplateError):
        render(TemplateId.L002_QUESTION, params)


def test_action_noun_defaults_to_change() -> None:
    assert action_noun(MedAction.HOLD) == "hold"
    assert action_noun(None) == "change"


def test_l002_flags_a_verified_temporary_change_without_an_end(commit: Builder) -> None:
    hold = commit(
        "cc_hold",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 25)),
        temporary=True,
        context="procedure",
    )
    (finding,) = lint([hold], {"ent_med_a": "Medication A"})
    assert (finding.code, finding.commit_ids, finding.key) == (
        LintCode.L002,
        ("cc_hold",),
        (LintCode.L002, ("cc_hold",)),
    )
    assert render(finding.question_template, finding.params) == (
        "When should the temporary hold of Medication A for the procedure end?"
    )
    assert render(finding.message_template, {}) == "This temporary change has no captured end."


def test_l002_without_context_uses_the_short_question(commit: Builder) -> None:
    hold = commit(attributes=Attributes(action=MedAction.STOP), temporary=True)
    (finding,) = lint([hold], {})
    assert finding.question_template is TemplateId.L002_QUESTION_NO_CONTEXT
    assert render(finding.question_template, finding.params) == (
        "When should the temporary stop of Medication A end?"
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"effective": Effective(end=date(2026, 10, 29))},
        {"effective": Effective(end_condition="after the procedure")},
        {"state": ReviewState.CANDIDATE},
        {"temporary": False},
    ],
)
def test_l002_ignores_changes_that_are_bounded_unverified_or_persistent(
    commit: Builder, overrides: dict[str, object]
) -> None:
    settings: dict[str, object] = {
        "temporary": True,
        "attributes": Attributes(action=MedAction.HOLD),
    }
    settings.update(overrides)
    assert lint([commit(**settings)], {}) == []


def test_render_inserts_values_literally() -> None:
    text = render(TemplateId.ASK_CARE_TEAM, {"question": "Is {entity} still on hold?"})
    assert text == "Ask your care team: Is {entity} still on hold?"
```

- [ ] **Step 2: Run the tests and watch them fail**

Run: `uv run pytest packages/caremerge-core/tests/test_branches_lint_questions.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'caremerge_core.branches'`.

- [ ] **Step 3: Write `questions.py`**

```python
"""User-facing text templates (principle P9: the model reads, templates write).

Every sentence CareMerge shows about a person's care is rendered here from
structured values. Rendering fails loudly when parameters don't match the
template, so a template can never be filled with the wrong fields.
"""

from collections.abc import Mapping, Set
from string import Formatter
from types import MappingProxyType
from typing import Final

from caremerge_core.enums import MedAction, TemplateId
from caremerge_core.errors import CareMergeError

TEMPLATES: Final[Mapping[TemplateId, str]] = MappingProxyType(
    {
        TemplateId.L002_MESSAGE: "This temporary change has no captured end.",
        TemplateId.L002_QUESTION: (
            "When should the temporary {action_noun} of {entity} for the {context} end?"
        ),
        TemplateId.L002_QUESTION_NO_CONTEXT: (
            "When should the temporary {action_noun} of {entity} end?"
        ),
        TemplateId.ASK_CARE_TEAM: "Ask your care team: {question}",
    }
)

_ACTION_NOUNS: Final[Mapping[MedAction, str]] = MappingProxyType(
    {
        MedAction.HOLD: "hold",
        MedAction.STOP: "stop",
        MedAction.START: "start",
        MedAction.RESUME: "restart",
        MedAction.CONTINUE: "change",
    }
)


class TemplateError(CareMergeError):
    """Raised when parameters don't match a template's fields."""

    def __init__(self, template_id: TemplateId, missing: Set[str], unexpected: Set[str]) -> None:
        self.template_id = template_id
        self.missing = frozenset(missing)
        self.unexpected = frozenset(unexpected)
        super().__init__(
            f"{template_id}: missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )


def template_fields(template_id: TemplateId) -> frozenset[str]:
    """Return the placeholder names a template requires."""
    return frozenset(field for _, field, _, _ in Formatter().parse(TEMPLATES[template_id]) if field)


def render(template_id: TemplateId, params: Mapping[str, str]) -> str:
    """Render a registered template with exactly its required parameters."""
    expected = template_fields(template_id)
    given = set(params)
    if given != expected:
        raise TemplateError(template_id, missing=expected - given, unexpected=given - expected)
    return TEMPLATES[template_id].format_map(params)


def action_noun(action: MedAction | None) -> str:
    """Return the noun used in questions about a temporary change."""
    return _ACTION_NOUNS[action] if action else "change"
```

- [ ] **Step 4: Write `branches.py`**

```python
"""Temporary pathways ("branches") such as a procedure (spec §9.6).

A temporary candidate with a context joins a branch keyed by that context
plus the date of the matching event captured in the same source, for
example ``procedure-2026-10-28``. Without a dated event, the key is the
context alone.
"""

from collections.abc import Sequence

from caremerge_core.contracts import CandidateCommit
from caremerge_core.plan import EVENT_KINDS
from caremerge_core.provenance import normalize


def slug(text: str) -> str:
    """Return a lowercase, hyphen-separated key for ``text``."""
    return "-".join(normalize(text).split())


def branch_key(candidate: CandidateCommit, siblings: Sequence[CandidateCommit]) -> str | None:
    """Return the branch a temporary candidate belongs to, or ``None``."""
    if not candidate.temporary or not candidate.context:
        return None
    context = slug(candidate.context)
    events = [
        sibling
        for sibling in siblings
        if sibling.kind in EVENT_KINDS and sibling.attributes.scheduled_for is not None
    ]
    named = [event for event in events if context in {slug(event.subject_text), event.kind.value}]
    chosen = named or (events if len(events) == 1 else [])
    if not chosen:
        return context
    scheduled = chosen[0].attributes.scheduled_for
    return f"{context}-{scheduled.isoformat()}" if scheduled else context
```

- [ ] **Step 5: Write `lint.py`**

```python
"""CareLint: deterministic structural gaps in the plan (spec §9.8).

Findings carry template IDs and parameters, never free text. The bridge
turns them into issues with rendered, neutral questions.
"""

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field

from caremerge_core.enums import LintCode, TemplateId
from caremerge_core.models import CareCommit
from caremerge_core.questions import action_noun


@dataclass(frozen=True)
class LintFinding:
    """One structural gap, ready to render as an issue."""

    code: LintCode
    entity_id: str
    commit_ids: tuple[str, ...]
    message_template: TemplateId
    question_template: TemplateId
    params: Mapping[str, str] = field(default_factory=dict)

    @property
    def key(self) -> tuple[LintCode, tuple[str, ...]]:
        """Return the identity used to avoid duplicate issues."""
        return (self.code, self.commit_ids)


def lint(commits: Sequence[CareCommit], entity_names: Mapping[str, str]) -> list[LintFinding]:
    """Run every implemented rule over the active commits."""
    return list(_temporary_change_without_end(commits, entity_names))


def _temporary_change_without_end(
    commits: Sequence[CareCommit], entity_names: Mapping[str, str]
) -> Iterator[LintFinding]:
    """L002: a temporary change with no captured end date or end condition."""
    for commit in commits:
        effective = commit.effective
        if not (commit.is_active and commit.temporary):
            continue
        if effective.end is not None or effective.end_condition is not None:
            continue
        params = {
            "action_noun": action_noun(commit.attributes.action),
            "entity": entity_names.get(commit.entity_id, commit.subject_text),
        }
        if commit.context:
            question = TemplateId.L002_QUESTION
            params["context"] = commit.context
        else:
            question = TemplateId.L002_QUESTION_NO_CONTEXT
        yield LintFinding(
            code=LintCode.L002,
            entity_id=commit.entity_id,
            commit_ids=(commit.commit_id,),
            message_template=TemplateId.L002_MESSAGE,
            question_template=question,
            params=params,
        )
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest`
Expected: `53 passed`.

- [ ] **Step 7: Run the remaining checks**

```bash
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: all clean.

- [ ] **Step 8: Commit**

```bash
git add packages/caremerge-core
git commit -m "feat(core): add question templates, branch keys, and CareLint L002"
```

---

### Task 7: Bee-write policy gate

**Files:**

- Create: `packages/caremerge-core/src/caremerge_core/policy.py`
- Test: `packages/caremerge-core/tests/test_policy.py`

**Interfaces:**

- Consumes: `Action`, `CareCommit`, `Issue` (Task 2) and `render`, `TemplateError` (Task 6).
- Produces:
  - `TODO_TEMPLATES`
  - `PolicyCode` (StrEnum)
  - `PolicyViolationError(codes)`, which has `.codes: tuple[PolicyCode, ...]`
  - `check_bee_write(action, commits: Mapping[str, CareCommit], issues: Mapping[str, Issue]) -> None`

- [ ] **Step 1: Write the failing tests**

Create `packages/caremerge-core/tests/test_policy.py`:

```python
"""Tests for the deterministic Bee-write policy gate (spec §9.10)."""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from caremerge_core.enums import (
    ActionState,
    IssueKind,
    IssueStatus,
    LintCode,
    ReviewState,
    TemplateId,
)
from caremerge_core.models import Action, CareCommit, Issue
from caremerge_core.policy import PolicyCode, PolicyViolationError, check_bee_write
from caremerge_core.questions import render

NOW = datetime(2026, 10, 19, 14, 0, tzinfo=UTC)
QUESTION = "When should the temporary hold of Medication A for the procedure end?"
Builder = Callable[..., CareCommit]


def _issue(status: IssueStatus = IssueStatus.OPEN) -> Issue:
    return Issue(
        issue_id="iss_1",
        kind=IssueKind.LINT,
        code=LintCode.L002,
        entity_id="ent_med_a",
        commit_ids=("cc_hold",),
        status=status,
        message="This temporary change has no captured end.",
        question=QUESTION,
        created_at=NOW,
    )


def _action(**overrides: object) -> Action:
    params = {"question": QUESTION}
    action = Action(
        action_id="act_1",
        template_id=TemplateId.ASK_CARE_TEAM,
        params=params,
        text=render(TemplateId.ASK_CARE_TEAM, params),
        alarm_at=NOW,
        issue_ids=("iss_1",),
        state=ActionState.CONFIRMED,
        confirmation_id="conf_1",
        created_at=NOW,
    )
    return action.model_copy(update=overrides)


def _check(
    action: Action,
    commit: Builder,
    *,
    issue: Issue | None = None,
    state: ReviewState = ReviewState.VERIFIED,
) -> None:
    commits = {"cc_hold": commit("cc_hold", state=state)}
    check_bee_write(action, commits, {"iss_1": issue or _issue()})


def test_confirmed_template_action_on_an_open_issue_passes(commit: Builder) -> None:
    _check(_action(), commit)


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"state": ActionState.PROPOSED}, PolicyCode.NOT_CONFIRMED),
        ({"confirmation_id": None}, PolicyCode.NOT_CONFIRMED),
        ({"bee_todo_id": "todo_1"}, PolicyCode.ALREADY_EXECUTED),
        ({"issue_ids": ()}, PolicyCode.NO_REFERENCES),
        ({"issue_ids": ("iss_404",)}, PolicyCode.UNKNOWN_ISSUE),
        ({"issue_ids": (), "commit_ids": ("cc_404",)}, PolicyCode.UNKNOWN_COMMIT),
        ({"template_id": TemplateId.L002_QUESTION}, PolicyCode.TEMPLATE_NOT_ALLOWED),
        ({"text": "Stop taking Medication A."}, PolicyCode.TEXT_NOT_FROM_TEMPLATE),
        ({"params": {"question": "Something else?"}}, PolicyCode.TEXT_NOT_FROM_TEMPLATE),
        ({"params": {}}, PolicyCode.TEXT_NOT_FROM_TEMPLATE),
    ],
)
def test_each_rule_refuses_with_its_code(
    commit: Builder, overrides: dict[str, object], code: PolicyCode
) -> None:
    with pytest.raises(PolicyViolationError) as caught:
        _check(_action(**overrides), commit)
    assert code in caught.value.codes


def test_issue_must_still_be_open(commit: Builder) -> None:
    with pytest.raises(PolicyViolationError) as caught:
        _check(_action(), commit, issue=_issue(IssueStatus.RESOLVED))
    assert caught.value.codes == (PolicyCode.ISSUE_NOT_OPEN,)


def test_commits_behind_the_issue_must_be_verified(commit: Builder) -> None:
    with pytest.raises(PolicyViolationError) as caught:
        _check(_action(), commit, state=ReviewState.CANDIDATE)
    assert caught.value.codes == (PolicyCode.UNVERIFIED_COMMIT,)
```

- [ ] **Step 2: Run the tests and watch them fail**

Run: `uv run pytest packages/caremerge-core/tests/test_policy.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'caremerge_core.policy'`.

- [ ] **Step 3: Write `policy.py`**

```python
"""Policy gate for Bee writes (spec §9.10).

Nothing reaches Bee unless the user confirmed it, it rests on verified and
sourced commits or open issues, and its text is exactly what an approved
template renders. The gate is deterministic; it never consults a model.
"""

from collections.abc import Mapping
from enum import StrEnum
from typing import Final

from caremerge_core.enums import ActionState, IssueStatus, TemplateId
from caremerge_core.errors import CareMergeError
from caremerge_core.models import Action, CareCommit, Issue
from caremerge_core.questions import TemplateError, render

TODO_TEMPLATES: Final = frozenset({TemplateId.ASK_CARE_TEAM})


class PolicyCode(StrEnum):
    """Why a Bee write was refused."""

    NOT_CONFIRMED = "not_confirmed"
    ALREADY_EXECUTED = "already_executed"
    NO_REFERENCES = "no_references"
    UNKNOWN_ISSUE = "unknown_issue"
    ISSUE_NOT_OPEN = "issue_not_open"
    UNKNOWN_COMMIT = "unknown_commit"
    UNVERIFIED_COMMIT = "unverified_commit"
    TEMPLATE_NOT_ALLOWED = "template_not_allowed"
    TEXT_NOT_FROM_TEMPLATE = "text_not_from_template"


class PolicyViolationError(CareMergeError):
    """Raised when an action fails the gate. Carries codes, never content."""

    def __init__(self, codes: tuple[PolicyCode, ...]) -> None:
        self.codes = codes
        super().__init__(", ".join(codes))


def check_bee_write(
    action: Action,
    commits: Mapping[str, CareCommit],
    issues: Mapping[str, Issue],
) -> None:
    """Raise ``PolicyViolationError`` unless ``action`` may be written to Bee."""
    codes: list[PolicyCode] = []
    if action.state is not ActionState.CONFIRMED or not action.confirmation_id:
        codes.append(PolicyCode.NOT_CONFIRMED)
    if action.bee_todo_id is not None:
        codes.append(PolicyCode.ALREADY_EXECUTED)
    if not action.issue_ids and not action.commit_ids:
        codes.append(PolicyCode.NO_REFERENCES)
    referenced = set(action.commit_ids)
    for issue_id in action.issue_ids:
        issue = issues.get(issue_id)
        if issue is None:
            codes.append(PolicyCode.UNKNOWN_ISSUE)
            continue
        if issue.status is not IssueStatus.OPEN:
            codes.append(PolicyCode.ISSUE_NOT_OPEN)
        referenced.update(issue.commit_ids)
    for commit_id in sorted(referenced):
        commit = commits.get(commit_id)
        if commit is None:
            codes.append(PolicyCode.UNKNOWN_COMMIT)
        elif not commit.is_active:
            codes.append(PolicyCode.UNVERIFIED_COMMIT)
    codes.extend(_template_codes(action))
    if codes:
        raise PolicyViolationError(tuple(dict.fromkeys(codes)))


def _template_codes(action: Action) -> list[PolicyCode]:
    if action.template_id not in TODO_TEMPLATES:
        return [PolicyCode.TEMPLATE_NOT_ALLOWED]
    try:
        expected = render(action.template_id, action.params)
    except TemplateError:
        return [PolicyCode.TEXT_NOT_FROM_TEMPLATE]
    return [] if expected == action.text else [PolicyCode.TEXT_NOT_FROM_TEMPLATE]
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest`
Expected: `66 passed`.

- [ ] **Step 5: Run the remaining checks**

```bash
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
```

Expected: `21 files already formatted`, `All checks passed!`, `Success: no issues found in 13 source files`.

- [ ] **Step 6: Commit**

```bash
git add packages/caremerge-core
git commit -m "feat(core): add deterministic policy gate for Bee writes"
```

---

## After Task 7: hand-off

- [ ] **Step 1: Full verification from a clean environment**

```bash
rm -rf .venv
uv sync --locked
uv run ruff format --check
uv run ruff check
uv run mypy packages/caremerge-core/src
uv run pytest
```

Expected: `66 passed`, with every check clean.

- [ ] **Step 2: Report and wait for publishing approval**

Report the results to the user. Pushing `a/m1-core` and opening the PR into `main` are outward-facing, so they wait for the user's explicit go-ahead (repo rules). After the push, CI runs the same four checks on GitHub.

- [ ] **Step 3: Next plan**

Plan M1b, `apps/bridge`, builds on these exact interfaces. In particular, `CareGraphRepository` is implemented by the in-memory store, and `CompileInput`/`CompileOutput` are served by the stub extractor.
