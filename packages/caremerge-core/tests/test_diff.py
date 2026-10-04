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


def test_change_in_effect_on_the_first_day_is_not_future_effective(commit: Builder) -> None:
    keep = commit("cc_keep", attributes=Attributes(action=MedAction.CONTINUE))
    hold = commit(
        "cc_hold",
        attributes=Attributes(action=MedAction.HOLD),
        effective=Effective(start=date(2026, 10, 10), end=date(2026, 10, 21)),
        temporary=True,
        captured_at=SCENE_2_AT,
        source_id="src_2",
    )
    (entry,) = care_diff(
        [keep, hold], known_before=SCENE_2_AT, window=WINDOW, tz=TZ, entity_names=NAMES
    ).entries
    assert (entry.change, entry.future_effective) == (ChangeType.CHANGED, False)


def test_entities_sharing_a_name_are_ordered_by_id(commit: Builder) -> None:
    entity_ids = [f"ent_{letter}" for letter in "hcfadgbe"]
    procedures = [
        commit(
            f"cc_{entity_id}",
            kind=CommitKind.PROCEDURE,
            entity_id=entity_id,
            subject_text="procedure",
            attributes=Attributes(scheduled_for=date(2026, 10, 28)),
        )
        for entity_id in entity_ids
    ]
    names = dict.fromkeys(entity_ids, "Procedure")
    diff = care_diff(procedures, known_before=None, window=WINDOW, tz=TZ, entity_names=names)
    assert [entry.entity_id for entry in diff.entries] == sorted(entity_ids)
