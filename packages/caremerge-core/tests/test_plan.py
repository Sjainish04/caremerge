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


def test_plan_ignores_unverified_and_rejected_commits(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    pending = commit(
        "cc_pending", attributes=Attributes(action=MedAction.STOP), state=ReviewState.CANDIDATE
    )
    rejected = commit(
        "cc_rejected",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 19)),
        temporary=True,
        state=ReviewState.REJECTED,
    )
    (entry,) = plan_at([keep, pending, rejected], date(2026, 10, 19), TZ)
    assert (entry.values, entry.commit_ids, entry.temporary) == (
        ("continue",),
        ("cc_keep",),
        False,
    )
