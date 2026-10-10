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
from caremerge_core.questions import TEMPLATES, TemplateError, action_noun, render

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


def test_templates_are_registered_verbatim() -> None:
    assert dict(TEMPLATES) == {
        TemplateId.L002_MESSAGE: "This temporary change has no captured end.",
        TemplateId.L002_QUESTION: (
            "When should the temporary {action_noun} of {entity} for the {context} end?"
        ),
        TemplateId.L002_QUESTION_NO_CONTEXT: (
            "When should the temporary {action_noun} of {entity} end?"
        ),
        TemplateId.ASK_CARE_TEAM: "Ask your care team: {question}",
        TemplateId.REMIND_VERIFIED_INSTRUCTION: 'Reminder from {source} ({date}): "{quote}"',
        TemplateId.SPEAK_VISIT_UPDATES: (
            "Your visit with {clinician} on {date} has {item_count}: {item_list}. Should I add "
            "{item_pronoun} to your care plan?"
        ),
        TemplateId.SPEAK_NO_VISIT_UPDATES: "There's nothing new to review.",
        TemplateId.SPEAK_ITEMS_ADDED: "Added to your care plan.",
        TemplateId.SPEAK_VISIT_READY: "Your visit with {clinician} on {date} is ready to review.",
        TemplateId.SPEAK_VISIT_ALREADY_ADDED: (
            "Your visit with {clinician} on {date} is already in CareMerge."
        ),
        TemplateId.SPEAK_NO_CHANGES: "Nothing has changed in your care plan since your last visit.",
        TemplateId.SPEAK_CHANGES_INTRO: "Since your last visit, {change_count} in your care plan.",
        TemplateId.SPEAK_CHANGE_STATE: "{subject} goes from {old} to {new}{timing}.",
        TemplateId.SPEAK_CHANGE_DETAIL: (
            "The {dimension} for {subject} goes from {old} to {new}{timing}."
        ),
        TemplateId.SPEAK_CHANGE_NEW: "New: {item}.",
        TemplateId.SPEAK_CHANGE_REMOVED: "{subject} is no longer in your care plan.",
        TemplateId.SPEAK_END_NOT_CAPTURED: "No end was captured.",
        TemplateId.SPEAK_MORE_ON_SCREEN: "There's more on your screen.",
        TemplateId.SPEAK_QUESTIONS_PENDING: "{question_count} {question_verb} clarifying.",
        TemplateId.SPEAK_PLAN_DAY: "On {date}, {subject} is {state} in your care plan{details}.",
        TemplateId.SPEAK_PLAN_EVENT: "Your {subject} is on {date} in your care plan.",
        TemplateId.SPEAK_PLAN_CONFLICT: (
            "On {date}, the captured instructions about {subject} differ. CareMerge won't decide "
            "which applies."
        ),
        TemplateId.SPEAK_PLAN_NOTHING: "Nothing was captured about {subject} for {date}.",
        TemplateId.SPEAK_PLAN_EMPTY: "Nothing in your care plan applies to {date}.",
        TemplateId.SPEAK_PLAN_OVERVIEW: "On {date}, your care plan has {item_list}.",
        TemplateId.SPEAK_SOURCE: "That's from {clinician} on {date}.",
        TemplateId.SPEAK_NOT_DECIDING: (
            "CareMerge isn't deciding what's correct. Check with your care team if you're unsure."
        ),
        TemplateId.SPEAK_NO_QUESTIONS: "There are no open questions right now.",
        TemplateId.SPEAK_QUESTIONS: (
            "{question_count} {question_verb} clarifying: {question_list} I can remind you to ask "
            "your care team."
        ),
        TemplateId.SPEAK_REMINDER_PROPOSAL: "I can remind you {when}: {text} Should I add it?",
        TemplateId.SPEAK_REMINDER_ADDED: "Done. It's in your reminders.",
        TemplateId.SPEAK_NO_REMINDER_TOPIC: "There's no open question to remind you about.",
        TemplateId.SPEAK_NOT_FOUND: "I couldn't find that in your care plan.",
        TemplateId.SPEAK_REFUSED: (
            "I can't do that, because it no longer matches your confirmed care plan."
        ),
        TemplateId.SPEAK_DATA_DELETED: "Your CareMerge data is deleted.",
        TemplateId.SPEAK_FALLBACK: (
            "I can tell you what changed in your care plan, what it says for a day, what still "
            "needs clarifying, or set a reminder to ask your care team."
        ),
        TemplateId.SPEAK_DECLINED: "Okay, I won't change anything.",
        TemplateId.SPEAK_UNAVAILABLE: "CareMerge isn't reachable right now. Try again in a moment.",
        TemplateId.PHRASE_EVENT: "your {subject} on {date}",
        TemplateId.PHRASE_EVENT_UNDATED: "your {subject}",
        TemplateId.PHRASE_FOLLOW_UP: "a follow-up",
        TemplateId.PHRASE_FOLLOW_UP_INTERVAL: "a follow-up in {interval}",
        TemplateId.PHRASE_FOLLOW_UP_DATE: "a follow-up on {date}",
        TemplateId.PHRASE_MONITORING: "checking {subject} on {days}",
        TemplateId.PHRASE_MONITORING_UNDATED: "checking {subject}",
        TemplateId.PHRASE_MED_CONTINUE: "continuing {subject}",
        TemplateId.PHRASE_MED_START: "starting {subject}",
        TemplateId.PHRASE_MED_STOP: "stopping {subject}",
        TemplateId.PHRASE_MED_HOLD: "a hold on {subject}",
        TemplateId.PHRASE_MED_RESUME: "restarting {subject}",
        TemplateId.PHRASE_MED_PLAIN: "{subject}",
        TemplateId.PHRASE_STARTING: "starting {date}",
        TemplateId.PHRASE_UNTIL: "until {end}",
        TemplateId.PHRASE_FOR_CONTEXT: "for your {context}",
    }
