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
