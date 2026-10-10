"""Tests for reviewing candidates and keeping clarification issues in step."""

from collections.abc import Callable
from datetime import date

import pytest

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.issues import dismiss_issue
from caremerge_addon.pipeline.review import (
    Correction,
    correct_commit,
    reject_commit,
    verify_commit,
)
from caremerge_core.contracts import Effective
from caremerge_core.enums import IssueStatus, ReviewState

QUESTION = "When should the temporary hold of Medication A for the procedure end?"
VisitAdder = Callable[[int], list[str]]


def _verify_all(commit_ids: list[str], ctx: PipelineContext) -> None:
    for commit_id in commit_ids:
        verify_commit(commit_id, ctx)


def test_verifying_the_hold_opens_one_neutral_question(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(1), ctx)
    assert ctx.repo.snapshot().issues == ()
    _verify_all(add_visit_n(2), ctx)
    (issue,) = ctx.repo.snapshot().issues
    assert (issue.status, issue.question) == (IssueStatus.OPEN, QUESTION)
    assert issue.message == "This temporary change has no captured end."


def test_rejecting_a_candidate_keeps_it_out_and_records_the_decision(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    procedure_id, hold_id = add_visit_n(2)
    rejected = reject_commit(hold_id, ctx)
    verify_commit(procedure_id, ctx)
    snapshot = ctx.repo.snapshot()
    assert rejected.review.state is ReviewState.REJECTED
    assert snapshot.issues == ()
    assert [(e.commit_id, e.state) for e in snapshot.reviews] == [
        (hold_id, ReviewState.REJECTED),
        (procedure_id, ReviewState.VERIFIED),
    ]


def test_correcting_the_hold_with_an_end_resolves_the_question(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(2), ctx)
    (issue,) = ctx.repo.snapshot().issues
    hold_id = issue.commit_ids[0]
    end = Effective(start=date(2026, 10, 25), end=date(2026, 10, 29))
    correct_commit(hold_id, Correction(effective=end), ctx)
    snapshot = ctx.repo.snapshot()
    assert [i.status for i in snapshot.issues] == [IssueStatus.RESOLVED]
    hold = next(c for c in snapshot.commits if c.commit_id == hold_id)
    assert (hold.review.state, hold.effective.end) == (ReviewState.CORRECTED, date(2026, 10, 29))
    assert snapshot.reviews[-1].state is ReviewState.CORRECTED


def test_dismissed_issues_stay_dismissed(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    _verify_all(add_visit_n(2), ctx)
    (issue,) = ctx.repo.snapshot().issues
    dismiss_issue(issue.issue_id, ctx)
    _verify_all(add_visit_n(1), ctx)
    assert [i.status for i in ctx.repo.snapshot().issues] == [IssueStatus.DISMISSED]


def test_unknown_commits_and_issues_raise_not_found(ctx: PipelineContext) -> None:
    with pytest.raises(RecordNotFoundError):
        verify_commit("cc_404", ctx)
    with pytest.raises(RecordNotFoundError):
        dismiss_issue("iss_404", ctx)
