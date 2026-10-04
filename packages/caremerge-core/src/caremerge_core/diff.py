"""CareDiff: what changed in the plan between two knowledge points (spec §9.5).

The diff compares schedules computed from what was known *before* a moment
with what is known now, over the same window of days. Output order is
deterministic: entity name, then entity ID (for entities that share a
name), then dimension order.
"""

from collections.abc import Mapping, Sequence
from datetime import date, datetime
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
    """How one entity dimension's schedule changed.

    ``future_effective`` is True when the plan on the window's first day is
    unchanged, so the change only takes effect later.
    """

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

    ``known_before`` is exclusive: to diff since the last session, pass the
    newest session's ``captured_at``. With ``known_before=None`` nothing
    counts as previously known, so every stated dimension appears as added.
    """
    before = known(commits, before=known_before) if known_before else []
    after = known(commits)
    keys = sorted(
        set(dimension_keys(before)) | set(dimension_keys(after)),
        key=lambda key: (
            entity_names.get(key[0], key[0]).casefold(),
            key[0],
            DIMENSION_ORDER[key[1]],
        ),
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
        future_effective=_holding(old, window.start) == _holding(new, window.start),
        temporary=any(segment.temporary for segment in changed),
        end_not_captured=any(segment.temporary and not segment.end_captured for segment in changed),
    )


def _holding(segments: Sequence[Segment], day: date) -> tuple[tuple[str, ...], bool, bool] | None:
    """Return what holds on ``day``: the covering segment's values and flags."""
    for segment in segments:
        if segment.start <= day < segment.end:
            return (segment.values, segment.temporary, segment.end_captured)
    return None
