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
    """Return active commits, optionally only those captured strictly before ``before``.

    To diff "since the last session", pass the newest session's ``captured_at``:
    what was captured before it is what was known at the previous session.
    """
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

    Only active (verified or corrected) commits count, so candidates and
    rejected commits never reach the plan. Temporary commits override
    persistent ones inside their interval (a branch).
    Overlapping persistent commits with different values yield one segment
    holding every value; detecting that as a conflict is feature F9.
    """
    spans = [
        _span(commit, value, tz)
        for commit in commits
        if commit.is_active
        and commit.entity_id == entity_id
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
    """Return every entity dimension's value(s) on ``day``, from active commits."""
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
