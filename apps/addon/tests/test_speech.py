"""Tests for spoken sentences: exact demo lines and the formatting they rely on (spec §5.3)."""

from collections.abc import Callable
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from caremerge_addon import speech
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.reminders import propose_issue_reminder
from caremerge_addon.pipeline.review import verify_commit
from caremerge_addon.pipeline.views import diff_since_last_visit, plan_on

TZ = ZoneInfo("America/New_York")
DEMO_NOW = datetime(2026, 10, 19, 14, 0, tzinfo=UTC)
QUESTION = "When should the temporary hold of Medication A for the procedure end?"
VisitAdder = Callable[[int], list[str]]


def _verify_all(commit_ids: list[str], ctx: PipelineContext) -> None:
    for commit_id in commit_ids:
        verify_commit(commit_id, ctx)


@pytest.mark.parametrize(
    ("day", "spoken"),
    [(date(2026, 10, 7), "Wednesday, October 7"), (date(2026, 10, 25), "Sunday, October 25")],
)
def test_dates_are_spelled_out(day: date, spoken: str) -> None:
    assert speech.spoken_date(day) == spoken


@pytest.mark.parametrize(
    ("moment", "spoken"),
    [
        (time(10, 0), "10 AM"),
        (time(14, 30), "2:30 PM"),
        (time(0, 0), "12 AM"),
        (time(12, 5), "12:05 PM"),
    ],
)
def test_times_are_spoken_on_a_twelve_hour_clock(moment: time, spoken: str) -> None:
    assert speech.spoken_time(moment) == spoken


@pytest.mark.parametrize(
    ("alarm", "spoken"),
    [
        (datetime(2026, 10, 20, 14, 0, tzinfo=UTC), "tomorrow at 10 AM"),
        (datetime(2026, 10, 19, 20, 0, tzinfo=UTC), "today at 4 PM"),
        (datetime(2026, 10, 24, 14, 0, tzinfo=UTC), "on Saturday, October 24 at 10 AM"),
    ],
)
def test_alarm_times_are_relative_when_close(alarm: datetime, spoken: str) -> None:
    assert speech.spoken_when(alarm, DEMO_NOW, TZ) == spoken


@pytest.mark.parametrize(
    ("items", "joined"),
    [(["a"], "a"), (["a", "b"], "a and b"), (["a", "b", "c"], "a, b, and c")],
)
def test_lists_join_naturally(items: list[str], joined: str) -> None:
    assert speech.join_list(items) == joined


def test_visit_updates_read_each_new_item(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    add_visit_n(2)
    snapshot = ctx.repo.snapshot()
    (source,) = snapshot.sources
    assert speech.visit_updates(source, list(snapshot.commits), TZ) == (
        "Your visit with Dr. Lee on Wednesday, October 7 has 2 new items: your procedure on "
        "Wednesday, October 28 and a hold on Medication A starting Sunday, October 25. "
        "Should I add them to your care plan?"
    )


def test_item_phrases_cover_each_kind(ctx: PipelineContext, add_visit_n: VisitAdder) -> None:
    add_visit_n(1)
    add_visit_n(3)
    phrases = [speech.item_phrase(commit) for commit in ctx.repo.snapshot().commits]
    assert phrases == [
        "continuing Medication A, one tablet every morning",
        "checking blood pressure on Tuesdays and Fridays",
        "a follow-up in four weeks",
        "Medication A with food",
        "Medication A every evening",
    ]


def test_what_changed_after_the_specialist_visit(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(1), ctx)
    _verify_all(add_visit_n(2), ctx)
    snapshot = ctx.repo.snapshot()
    spoken = speech.changes(
        diff_since_last_visit(ctx),
        {c.commit_id: c for c in snapshot.commits},
        snapshot.entity_names(),
        open_questions=1,
    )
    assert spoken == (
        "Since your last visit, 2 things changed in your care plan. Medication A goes from "
        "active to on hold starting Sunday, October 25, for your procedure. No end was "
        "captured. New: your procedure on Wednesday, October 28. 1 question needs clarifying."
    )


def test_nothing_changed_is_said_plainly(ctx: PipelineContext) -> None:
    assert speech.changes(diff_since_last_visit(ctx), {}, {}, open_questions=0) == (
        "Nothing has changed in your care plan since your last visit."
    )


def test_plan_for_a_day_names_the_source_and_never_decides(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(1), ctx)
    _verify_all(add_visit_n(2), ctx)
    snapshot = ctx.repo.snapshot()
    commits = {c.commit_id: c for c in snapshot.commits}
    names = snapshot.entity_names()

    def say(day: date, subject: str | None) -> str:
        return speech.plan_day(day, subject, plan_on(day, ctx), commits, names, TZ)

    assert say(date(2026, 10, 25), "medication a") == (
        "On Sunday, October 25, Medication A is on hold in your care plan. That's from "
        "Dr. Lee on Wednesday, October 7. CareMerge isn't deciding what's correct. Check "
        "with your care team if you're unsure."
    )
    assert say(date(2026, 10, 24), "Medication A") == (
        "On Saturday, October 24, Medication A is active in your care plan: one tablet every "
        "morning. That's from Dr. Rivera on Monday, October 5. CareMerge isn't deciding "
        "what's correct. Check with your care team if you're unsure."
    )
    assert say(date(2026, 10, 25), "the procedure") == (
        "Your procedure is on Wednesday, October 28 in your care plan. That's from Dr. Lee "
        "on Wednesday, October 7."
    )
    assert say(date(2026, 10, 25), "Medication B") == (
        "Nothing was captured about Medication B for Sunday, October 25."
    )


def test_open_questions_and_reminder_proposal(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    _verify_all(add_visit_n(2), ctx)
    (issue,) = ctx.repo.snapshot().issues
    assert speech.questions([issue.question]) == (
        f"1 question needs clarifying: {QUESTION} I can remind you to ask your care team."
    )
    assert speech.questions([]) == "There are no open questions right now."
    action = propose_issue_reminder(issue.issue_id, None, ctx)
    assert speech.reminder_proposal(action, DEMO_NOW, TZ) == (
        f"I can remind you tomorrow at 10 AM: Ask your care team: {QUESTION} Should I add it?"
    )


def test_plan_overview_lists_every_subject_for_the_day(
    ctx: PipelineContext, add_visit_n: VisitAdder
) -> None:
    assert speech.plan_day(date(2026, 10, 25), None, (), {}, {}, TZ) == (
        "Nothing in your care plan applies to Sunday, October 25."
    )
    _verify_all(add_visit_n(1), ctx)
    _verify_all(add_visit_n(2), ctx)
    snapshot = ctx.repo.snapshot()
    commits = {c.commit_id: c for c in snapshot.commits}
    day = date(2026, 10, 25)
    spoken = speech.plan_day(day, None, plan_on(day, ctx), commits, snapshot.entity_names(), TZ)
    assert spoken == (
        "On Sunday, October 25, your care plan has Medication A on hold, checking blood "
        "pressure on Tuesdays and Fridays, a follow-up in four weeks, and your procedure on "
        "Wednesday, October 28. CareMerge isn't deciding what's correct. Check with your care "
        "team if you're unsure."
    )
