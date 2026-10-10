"""Tests for the add-on's tool logic: results, speech, cards, and confirmations (spec §7.2)."""

from collections.abc import Callable
from datetime import UTC, date, datetime

import pytest

from caremerge_addon.errors import InvalidRequestError, RecordNotFoundError
from caremerge_addon.mcp import tools
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.review import verify_commit
from caremerge_core.enums import ActionState, ChangeType, Dimension, ReviewState

VisitAdder = Callable[[int], list[str]]
QUESTION = "When should the temporary hold of Medication A for the procedure end?"


def _verify_all(commit_ids: list[str], ctx: PipelineContext) -> None:
    for commit_id in commit_ids:
        verify_commit(commit_id, ctx)


def test_inbox_lists_visits_and_marks_added_ones(ctx: PipelineContext) -> None:
    assert [(v.visit_id, v.added) for v in tools.list_visits(ctx).visits] == [
        ("visit-1", False),
        ("visit-2", False),
        ("visit-3", False),
    ]
    added = tools.add_visit(ctx, "visit-2")
    assert added.speech == "Your visit with Dr. Lee on Wednesday, October 7 is ready to review."
    assert (added.created, added.rejected, added.visit.added) == (2, 0, True)
    again = tools.add_visit(ctx, "visit-2")
    assert again.speech.endswith("is already in CareMerge.")
    assert again.created == 0
    assert [v.added for v in tools.list_visits(ctx).visits] == [False, True, False]


def test_visit_updates_offer_the_newest_visit_for_confirmation(ctx: PipelineContext) -> None:
    assert tools.visit_updates(ctx, None).speech == "There's nothing new to review."
    tools.add_visit(ctx, "visit-1")
    tools.add_visit(ctx, "visit-2")
    updates = tools.visit_updates(ctx, None)
    assert updates.clinician == "Dr. Lee"
    assert [item.summary for item in updates.items] == [
        "your procedure on Wednesday, October 28",
        "a hold on Medication A starting Sunday, October 25",
    ]
    hold = updates.items[1]
    assert (hold.source.quote, hold.source.date) == (
        "hold Medication A starting Sunday, October 25",
        date(2026, 10, 7),
    )
    assert updates.confirmation is not None
    assert updates.confirmation.tool == "confirm_items"
    assert updates.confirmation.arguments["commit_ids"] == [
        item.commit_id for item in updates.items
    ]
    rivera = tools.visit_updates(ctx, "dr. rivera")
    assert rivera.clinician == "Dr. Rivera"
    assert len(rivera.items) == 3


def test_confirming_items_verifies_only_candidates(ctx: PipelineContext) -> None:
    tools.add_visit(ctx, "visit-2")
    updates = tools.visit_updates(ctx, None)
    ids = [item.commit_id for item in updates.items]
    added = tools.confirm_items(ctx, ids, "conf-1")
    assert (added.speech, added.commit_ids) == ("Added to your care plan.", ids)
    states = {c.commit_id: c.review.state for c in ctx.repo.snapshot().commits}
    assert set(states.values()) == {ReviewState.VERIFIED}
    assert tools.confirm_items(ctx, ids, "conf-2").commit_ids == []
    assert len(ctx.repo.snapshot().reviews) == 2
    with pytest.raises(RecordNotFoundError):
        tools.confirm_items(ctx, ["cc_404"], "conf-3")


def test_whats_changed_returns_cards_with_their_sources(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(1), ctx)
    _verify_all(add_visit_n(2), ctx)
    result = tools.whats_changed(ctx)
    assert result.speech.startswith("Since your last visit, 2 things changed in your care plan.")
    assert result.open_questions == 1
    action, procedure = result.changes
    assert (action.subject, action.dimension, action.change) == (
        "Medication A",
        Dimension.ACTION,
        ChangeType.CHANGED,
    )
    assert [segment.values for segment in action.before] == [["active"]]
    assert [segment.values for segment in action.after] == [["active"], ["on hold"]]
    assert (action.future_effective, action.temporary, action.end_not_captured) == (
        True,
        True,
        True,
    )
    assert {source.clinician for source in action.sources} == {"Dr. Rivera", "Dr. Lee"}
    assert (procedure.subject, procedure.change) == ("procedure", ChangeType.ADDED)


def test_plan_for_day_answers_with_cards(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    _verify_all(add_visit_n(1), ctx)
    _verify_all(add_visit_n(2), ctx)
    result = tools.plan_for_day(ctx, date(2026, 10, 25), "Medication A")
    assert result.speech.startswith("On Sunday, October 25, Medication A is on hold")
    actions = [entry for entry in result.entries if entry.dimension is Dimension.ACTION]
    assert [(entry.values, entry.temporary, entry.source.clinician) for entry in actions] == [
        (["on hold"], True, "Dr. Lee")
    ]
    assert {entry.subject for entry in result.entries} == {"Medication A"}


def test_open_questions_and_reminders(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    assert tools.propose_reminder(ctx, None, None, None).speech == (
        "There's no open question to remind you about."
    )
    _verify_all(add_visit_n(2), ctx)
    (question,) = tools.open_questions(ctx).questions
    assert (question.question, question.subject) == (QUESTION, "Medication A")
    proposal = tools.propose_reminder(ctx, None, None, None)
    assert proposal.speech == (
        f"I can remind you tomorrow at 10 AM: Ask your care team: {QUESTION} Should I add it?"
    )
    assert proposal.reminder is not None
    assert proposal.reminder.based_on is not None
    assert proposal.reminder.based_on.clinician == "Dr. Lee"
    assert proposal.confirmation is not None
    assert proposal.confirmation.tool == "confirm_reminder"
    action_id = proposal.confirmation.arguments["action_id"]
    stored = tools.confirm_reminder(ctx, str(action_id), "conf-1")
    assert (stored.speech, stored.reminder.state) == (
        "Done. It's in your reminders.",
        ActionState.EXECUTED,
    )
    assert [r.text for r in tools.list_reminders(ctx).reminders] == [
        f"Ask your care team: {QUESTION}"
    ]


def test_reminder_can_restate_a_confirmed_instruction(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _, hold_id = add_visit_n(2)
    verify_commit(hold_id, ctx)
    alarm = datetime(2026, 10, 24, 22, 0, tzinfo=UTC)
    proposal = tools.propose_reminder(ctx, None, hold_id, alarm)
    assert proposal.speech == (
        "I can remind you on Saturday, October 24 at 6 PM: Reminder from Dr. Lee "
        '(October 7): "hold Medication A starting Sunday, October 25" Should I add it?'
    )
    with pytest.raises(InvalidRequestError, match="one of"):
        tools.propose_reminder(ctx, "iss_1", hold_id, None)


def test_delete_my_data_empties_the_ledger(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    add_visit_n(1)
    assert tools.delete_my_data(ctx, "conf-1").speech == "Your CareMerge data is deleted."
    assert ctx.repo.snapshot().sources == ()
