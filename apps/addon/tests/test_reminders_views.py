"""Tests for reminders through the policy gate and for the plan and diff views."""

from collections.abc import Callable
from datetime import UTC, date, datetime

import pytest

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.reminders import (
    confirm_reminder,
    default_alarm,
    propose_commit_reminder,
    propose_issue_reminder,
)
from caremerge_addon.pipeline.review import reject_commit, verify_commit
from caremerge_addon.pipeline.views import diff_since_last_visit, plan_on
from caremerge_addon.settings import AddonSettings
from caremerge_core.enums import ActionState, ChangeType, Dimension, IssueStatus
from caremerge_core.policy import PolicyCode, PolicyViolationError

QUESTION = "When should the temporary hold of Medication A for the procedure end?"
RESTATEMENT = 'Reminder from Dr. Lee (October 7): "hold Medication A starting Sunday, October 25"'
DEMO_NOW = datetime(2026, 10, 19, 14, 0, tzinfo=UTC)
VisitAdder = Callable[[int], list[str]]


def _verify_all(commit_ids: list[str], ctx: PipelineContext) -> None:
    for commit_id in commit_ids:
        verify_commit(commit_id, ctx)


def test_question_reminder_is_stored_once_through_the_policy_gate(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(1) + add_visit_n(2), ctx)
    (issue,) = ctx.repo.snapshot().issues
    action = propose_issue_reminder(issue.issue_id, None, ctx)
    assert action.text == f"Ask your care team: {QUESTION}"
    assert action.alarm_at == datetime(2026, 10, 20, 14, 0, tzinfo=UTC)
    executed = confirm_reminder(action.action_id, "conf-1", ctx)
    again = confirm_reminder(action.action_id, "conf-2", ctx)
    assert (executed.state, executed.executed_at) == (ActionState.EXECUTED, DEMO_NOW)
    assert again == executed
    assert [a.state for a in ctx.repo.snapshot().actions] == [ActionState.EXECUTED]


def test_rejecting_the_hold_resolves_the_question_and_blocks_the_reminder(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(2), ctx)
    (issue,) = ctx.repo.snapshot().issues
    action = propose_issue_reminder(issue.issue_id, None, ctx)
    reject_commit(issue.commit_ids[0], ctx)
    (resolved,) = ctx.repo.snapshot().issues
    assert resolved.status is IssueStatus.RESOLVED
    with pytest.raises(PolicyViolationError) as caught:
        confirm_reminder(action.action_id, "conf-1", ctx)
    assert set(caught.value.codes) == {PolicyCode.ISSUE_NOT_OPEN, PolicyCode.UNVERIFIED_COMMIT}
    with pytest.raises(PolicyViolationError) as refused:
        propose_issue_reminder(issue.issue_id, None, ctx)
    assert refused.value.codes == (PolicyCode.ISSUE_NOT_OPEN,)


def test_reminder_restates_a_verified_instruction_with_its_source(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _, hold_id = add_visit_n(2)
    verify_commit(hold_id, ctx)
    action = propose_commit_reminder(hold_id, None, ctx)
    assert (action.text, action.commit_ids, action.issue_ids) == (RESTATEMENT, (hold_id,), ())
    assert confirm_reminder(action.action_id, "conf-1", ctx).state is ActionState.EXECUTED


def test_reminder_from_an_unverified_commit_is_refused(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _, hold_id = add_visit_n(2)
    with pytest.raises(PolicyViolationError) as caught:
        propose_commit_reminder(hold_id, None, ctx)
    assert caught.value.codes == (PolicyCode.UNVERIFIED_COMMIT,)
    assert ctx.repo.snapshot().actions == ()


def test_rejecting_the_commit_after_proposing_blocks_the_reminder(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _, hold_id = add_visit_n(2)
    verify_commit(hold_id, ctx)
    action = propose_commit_reminder(hold_id, None, ctx)
    reject_commit(hold_id, ctx)
    with pytest.raises(PolicyViolationError) as caught:
        confirm_reminder(action.action_id, "conf-1", ctx)
    assert caught.value.codes == (PolicyCode.UNVERIFIED_COMMIT,)


def test_default_alarm_is_tomorrow_at_the_local_reminder_time(settings: AddonSettings) -> None:
    late_evening = datetime(2026, 10, 20, 3, 30, tzinfo=UTC)
    assert default_alarm(late_evening, settings) == datetime(2026, 10, 20, 14, 0, tzinfo=UTC)


def test_diff_and_plan_reflect_only_verified_commits(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(1), ctx)
    hold_ids = add_visit_n(2)
    assert diff_since_last_visit(ctx).entries == ()
    assert [
        e.values for e in plan_on(date(2026, 10, 25), ctx) if e.dimension is Dimension.ACTION
    ] == [("continue",)]
    _verify_all(hold_ids, ctx)
    names = ctx.repo.snapshot().entity_names()
    diff = diff_since_last_visit(ctx)
    assert [(names[e.entity_id], e.dimension, e.change) for e in diff.entries] == [
        ("Medication A", Dimension.ACTION, ChangeType.CHANGED),
        ("procedure", Dimension.SCHEDULED_FOR, ChangeType.ADDED),
    ]
    actions = [e for e in plan_on(date(2026, 10, 25), ctx) if e.dimension is Dimension.ACTION]
    assert [(e.values, e.temporary) for e in actions] == [(("hold",), True)]


def test_unknown_records_raise_not_found(ctx: PipelineContext) -> None:
    with pytest.raises(RecordNotFoundError):
        propose_issue_reminder("iss_404", None, ctx)
    with pytest.raises(RecordNotFoundError):
        propose_commit_reminder("cc_404", None, ctx)
    with pytest.raises(RecordNotFoundError):
        confirm_reminder("act_404", "conf", ctx)
