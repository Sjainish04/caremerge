"""Spoken sentences for tool results (spec §7.4, principle P9).

Every sentence is a registered template from ``caremerge_core.questions``,
filled with values from verified records. This module only chooses
templates, formats dates and times without locale data, and joins phrases;
it never writes free text, and no model output reaches it.
"""

from collections.abc import Mapping, Sequence
from datetime import date, datetime, time, timedelta
from itertools import groupby
from types import MappingProxyType
from typing import Final
from zoneinfo import ZoneInfo

from caremerge_core.contracts import Effective
from caremerge_core.diff import CareDiff, DiffEntry
from caremerge_core.enums import (
    ChangeType,
    CommitKind,
    Dimension,
    FoodRelation,
    MedAction,
    TemplateId,
    TimeOfDay,
    Weekday,
)
from caremerge_core.models import Action, CareCommit, SourceEvent
from caremerge_core.plan import EVENT_KINDS, PlanEntry
from caremerge_core.questions import render

MAX_SPOKEN_ITEMS: Final = 5
MAX_SPOKEN_QUESTIONS: Final = 3

_WEEKDAYS: Final = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
_MONTHS: Final = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_MEDICATION_PHRASES: Final[Mapping[MedAction | None, TemplateId]] = MappingProxyType(
    {
        MedAction.CONTINUE: TemplateId.PHRASE_MED_CONTINUE,
        MedAction.START: TemplateId.PHRASE_MED_START,
        MedAction.STOP: TemplateId.PHRASE_MED_STOP,
        MedAction.HOLD: TemplateId.PHRASE_MED_HOLD,
        MedAction.RESUME: TemplateId.PHRASE_MED_RESUME,
        None: TemplateId.PHRASE_MED_PLAIN,
    }
)
_STATE_WORDS: Final[Mapping[MedAction, str]] = MappingProxyType(
    {
        MedAction.CONTINUE: "active",
        MedAction.START: "active",
        MedAction.RESUME: "active",
        MedAction.HOLD: "on hold",
        MedAction.STOP: "stopped",
    }
)
_PAUSED_STATES: Final = frozenset({MedAction.HOLD, MedAction.STOP})
_TIME_WORDS: Final[Mapping[TimeOfDay, str]] = MappingProxyType(
    {
        TimeOfDay.MORNING: "every morning",
        TimeOfDay.MIDDAY: "at midday",
        TimeOfDay.EVENING: "every evening",
        TimeOfDay.BEDTIME: "at bedtime",
    }
)
_FOOD_WORDS: Final[Mapping[FoodRelation, str]] = MappingProxyType(
    {FoodRelation.WITH_FOOD: "with food", FoodRelation.WITHOUT_FOOD: "without food"}
)
_DAY_PLURALS: Final[Mapping[Weekday, str]] = MappingProxyType(
    {day: f"{_WEEKDAYS[index]}s" for index, day in enumerate(Weekday)}
)
_DIMENSION_NAMES: Final[Mapping[Dimension, str]] = MappingProxyType(
    {
        Dimension.DOSE: "dose",
        Dimension.TIME_OF_DAY: "timing",
        Dimension.FOOD_RELATION: "food instructions",
        Dimension.DAYS_OF_WEEK: "days",
        Dimension.SCHEDULED_FOR: "date",
        Dimension.INTERVAL: "follow-up interval",
    }
)


def spoken_date(day: date) -> str:
    """Return a date as it is said: ``Wednesday, October 7``."""
    return f"{_WEEKDAYS[day.weekday()]}, {_MONTHS[day.month - 1]} {day.day}"


def spoken_time(moment: time) -> str:
    """Return a time on a twelve-hour clock: ``10 AM``, ``2:30 PM``."""
    hour = moment.hour % 12 or 12
    suffix = "AM" if moment.hour < 12 else "PM"
    return f"{hour} {suffix}" if moment.minute == 0 else f"{hour}:{moment.minute:02d} {suffix}"


def spoken_when(alarm: datetime, now: datetime, tz: ZoneInfo) -> str:
    """Return when an alarm rings, relative to today when it is close."""
    local = alarm.astimezone(tz)
    today = now.astimezone(tz).date()
    at = spoken_time(local.time())
    if local.date() == today:
        return f"today at {at}"
    if local.date() == today + timedelta(days=1):
        return f"tomorrow at {at}"
    return f"on {spoken_date(local.date())} at {at}"


def join_list(items: Sequence[str]) -> str:
    """Join phrases the way they are spoken: ``a``, ``a and b``, ``a, b, and c``."""
    if len(items) <= 2:
        return " and ".join(items)
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def local_date(moment: datetime, tz: ZoneInfo) -> date:
    """Return the calendar date of ``moment`` in ``tz``."""
    return moment.astimezone(tz).date()


def item_phrase(commit: CareCommit) -> str:
    """Return a short phrase describing what a commit captured."""
    attrs = commit.attributes
    subject = commit.subject_text
    if commit.kind in EVENT_KINDS:
        if attrs.scheduled_for:
            date_text = spoken_date(attrs.scheduled_for)
            return render(TemplateId.PHRASE_EVENT, {"subject": subject, "date": date_text})
        return render(TemplateId.PHRASE_EVENT_UNDATED, {"subject": subject})
    if commit.kind is CommitKind.FOLLOW_UP:
        if attrs.scheduled_for:
            date_text = spoken_date(attrs.scheduled_for)
            return render(TemplateId.PHRASE_FOLLOW_UP_DATE, {"date": date_text})
        if attrs.interval_text:
            return render(TemplateId.PHRASE_FOLLOW_UP_INTERVAL, {"interval": attrs.interval_text})
        return render(TemplateId.PHRASE_FOLLOW_UP, {})
    if commit.kind is CommitKind.MONITORING_INSTRUCTION:
        if attrs.days_of_week:
            days = _days_words(attrs.days_of_week)
            return render(TemplateId.PHRASE_MONITORING, {"subject": subject, "days": days})
        return render(TemplateId.PHRASE_MONITORING_UNDATED, {"subject": subject})
    return _medication_phrase(commit)


def visit_updates(source: SourceEvent, commits: Sequence[CareCommit], tz: ZoneInfo) -> str:
    """Return the sentence that reads a visit's new items and asks to add them."""
    phrases = [item_phrase(commit) for commit in commits]
    count = len(phrases)
    sentence = render(
        TemplateId.SPEAK_VISIT_UPDATES,
        {
            "clinician": source.label,
            "date": spoken_date(local_date(source.captured_at, tz)),
            "item_count": f"{count} new {'item' if count == 1 else 'items'}",
            "item_list": join_list(phrases[:MAX_SPOKEN_ITEMS]),
            "item_pronoun": "it" if count == 1 else "them",
        },
    )
    return _with_more(sentence, count > MAX_SPOKEN_ITEMS)


def visit_added(source: SourceEvent, *, is_new: bool, tz: ZoneInfo) -> str:
    """Return the sentence that says a visit is ready, or was already added."""
    template = TemplateId.SPEAK_VISIT_READY if is_new else TemplateId.SPEAK_VISIT_ALREADY_ADDED
    date_text = spoken_date(local_date(source.captured_at, tz))
    return render(template, {"clinician": source.label, "date": date_text})


def changes(
    diff: CareDiff,
    commits: Mapping[str, CareCommit],
    names: Mapping[str, str],
    *,
    open_questions: int,
) -> str:
    """Return the spoken CareDiff, grouped by entity, then the open-question count."""
    if not diff.entries:
        return render(TemplateId.SPEAK_NO_CHANGES, {})
    groups = [
        (entity_id, list(entries))
        for entity_id, entries in groupby(diff.entries, key=lambda entry: entry.entity_id)
    ]
    sentences: list[str] = []
    for entity_id, entries in groups:
        sentences.extend(_entity_changes(entries, diff, commits, names.get(entity_id, entity_id)))
    count = len(groups)
    intro = render(
        TemplateId.SPEAK_CHANGES_INTRO,
        {"change_count": f"{count} {'thing' if count == 1 else 'things'} changed"},
    )
    spoken = sentences[:MAX_SPOKEN_ITEMS]
    if len(sentences) > MAX_SPOKEN_ITEMS:
        spoken.append(render(TemplateId.SPEAK_MORE_ON_SCREEN, {}))
    if open_questions:
        spoken.append(render(TemplateId.SPEAK_QUESTIONS_PENDING, _question_count(open_questions)))
    return " ".join([intro, *spoken])


def plan_day(
    day: date,
    subject: str | None,
    entries: Sequence[PlanEntry],
    commits: Mapping[str, CareCommit],
    names: Mapping[str, str],
    tz: ZoneInfo,
) -> str:
    """Return what the plan says on ``day``, for one subject or for everything."""
    date_text = spoken_date(day)
    if subject is None:
        return _plan_overview(day, entries, commits, names)
    wanted = {entity_id for entity_id, name in names.items() if _matches(subject, name)}
    matched = [entry for entry in entries if entry.entity_id in wanted]
    if not matched:
        return render(TemplateId.SPEAK_PLAN_NOTHING, {"subject": subject, "date": date_text})
    display = names[matched[0].entity_id]
    if any(len(entry.values) > 1 for entry in matched):
        return render(TemplateId.SPEAK_PLAN_CONFLICT, {"date": date_text, "subject": display})
    by_dimension = {entry.dimension: entry for entry in matched}
    lead = by_dimension.get(Dimension.ACTION) or matched[0]
    commit = _latest_commit(lead, commits)
    source = render(
        TemplateId.SPEAK_SOURCE,
        {
            "clinician": commit.source.label,
            "date": spoken_date(local_date(commit.source.captured_at, tz)),
        },
    )
    if commit.kind in EVENT_KINDS and Dimension.SCHEDULED_FOR in by_dimension:
        scheduled = date.fromisoformat(by_dimension[Dimension.SCHEDULED_FOR].values[0])
        statement = render(
            TemplateId.SPEAK_PLAN_EVENT, {"subject": display, "date": spoken_date(scheduled)}
        )
        return f"{statement} {source}"
    if commit.kind is not CommitKind.MEDICATION_INSTRUCTION:
        overview = render(
            TemplateId.SPEAK_PLAN_OVERVIEW, {"date": date_text, "item_list": item_phrase(commit)}
        )
        return f"{overview} {source}"
    statement = render(
        TemplateId.SPEAK_PLAN_DAY, _medication_state(display, date_text, by_dimension)
    )
    return " ".join([statement, source, render(TemplateId.SPEAK_NOT_DECIDING, {})])


def questions(question_texts: Sequence[str]) -> str:
    """Return the open clarification questions, or say there are none."""
    if not question_texts:
        return render(TemplateId.SPEAK_NO_QUESTIONS, {})
    sentence = render(
        TemplateId.SPEAK_QUESTIONS,
        {
            **_question_count(len(question_texts)),
            "question_list": " ".join(question_texts[:MAX_SPOKEN_QUESTIONS]),
        },
    )
    return _with_more(sentence, len(question_texts) > MAX_SPOKEN_QUESTIONS)


def reminder_proposal(action: Action, now: datetime, tz: ZoneInfo) -> str:
    """Return the read-back of a proposed reminder and the question that confirms it."""
    when = spoken_when(action.alarm_at, now, tz)
    return render(TemplateId.SPEAK_REMINDER_PROPOSAL, {"when": when, "text": action.text})


def sentence(template_id: TemplateId) -> str:
    """Return a fixed sentence that takes no values."""
    return render(template_id, {})


def _medication_phrase(commit: CareCommit) -> str:
    attrs = commit.attributes
    base = render(_MEDICATION_PHRASES[attrs.action], {"subject": commit.subject_text})
    details = " ".join(
        word
        for word in (
            _TIME_WORDS.get(attrs.time_of_day) if attrs.time_of_day else None,
            _FOOD_WORDS.get(attrs.food_relation) if attrs.food_relation else None,
        )
        if word
    )
    if attrs.dose_text:
        phrase = f"{base}, {attrs.dose_text}" + (f" {details}" if details else "")
    else:
        phrase = f"{base} {details}" if details else base
    return phrase + _timing(commit.effective)


def _timing(effective: Effective) -> str:
    parts = []
    if effective.start:
        parts.append(render(TemplateId.PHRASE_STARTING, {"date": spoken_date(effective.start)}))
    if effective.end:
        parts.append(render(TemplateId.PHRASE_UNTIL, {"end": spoken_date(effective.end)}))
    elif effective.end_condition:
        parts.append(render(TemplateId.PHRASE_UNTIL, {"end": effective.end_condition}))
    return f" {' '.join(parts)}" if parts else ""


def _entity_changes(
    entries: Sequence[DiffEntry],
    diff: CareDiff,
    commits: Mapping[str, CareCommit],
    subject: str,
) -> list[str]:
    if all(entry.change is ChangeType.ADDED for entry in entries):
        commit_ids = dict.fromkeys(cid for entry in entries for cid in entry.after[0].commit_ids)
        phrases = list(dict.fromkeys(item_phrase(commits[cid]) for cid in commit_ids))
        return [render(TemplateId.SPEAK_CHANGE_NEW, {"item": join_list(phrases)})]
    sentences: list[str] = []
    for entry in entries:
        if entry.change is ChangeType.REMOVED:
            sentences.append(render(TemplateId.SPEAK_CHANGE_REMOVED, {"subject": subject}))
        elif entry.change is ChangeType.ADDED:
            commit = commits[entry.after[0].commit_ids[0]]
            sentences.append(render(TemplateId.SPEAK_CHANGE_NEW, {"item": item_phrase(commit)}))
        else:
            sentences.extend(_changed(entry, diff, commits, subject))
    return sentences


def _changed(
    entry: DiffEntry, diff: CareDiff, commits: Mapping[str, CareCommit], subject: str
) -> list[str]:
    old = entry.before[0]
    new = next(
        (s for s in entry.after if (s.values, s.temporary) != (old.values, old.temporary)),
        entry.after[-1],
    )
    timing_parts = []
    if new.start > diff.window.start:
        timing_parts.append(render(TemplateId.PHRASE_STARTING, {"date": spoken_date(new.start)}))
    context = commits[new.commit_ids[0]].context if new.temporary else None
    if context:
        timing_parts.append(render(TemplateId.PHRASE_FOR_CONTEXT, {"context": context}))
    params = {
        "subject": subject,
        "old": _value_words(entry.dimension, old.values),
        "new": _value_words(entry.dimension, new.values),
        "timing": f" {', '.join(timing_parts)}" if timing_parts else "",
    }
    if entry.dimension is Dimension.ACTION:
        said = render(TemplateId.SPEAK_CHANGE_STATE, params)
    else:
        params["dimension"] = _DIMENSION_NAMES[entry.dimension]
        said = render(TemplateId.SPEAK_CHANGE_DETAIL, params)
    if new.temporary and not new.end_captured:
        return [said, render(TemplateId.SPEAK_END_NOT_CAPTURED, {})]
    return [said]


def _value_words(dimension: Dimension, values: Sequence[str]) -> str:
    return join_list([_one_value(dimension, value) for value in values])


def _one_value(dimension: Dimension, value: str) -> str:
    if dimension is Dimension.ACTION:
        return _STATE_WORDS[MedAction(value)]
    if dimension is Dimension.TIME_OF_DAY:
        return _TIME_WORDS[TimeOfDay(value)]
    if dimension is Dimension.FOOD_RELATION:
        return _FOOD_WORDS[FoodRelation(value)]
    if dimension is Dimension.DAYS_OF_WEEK:
        return f"on {_days_words(tuple(Weekday(day) for day in value.split(',')))}"
    if dimension is Dimension.SCHEDULED_FOR:
        return spoken_date(date.fromisoformat(value))
    if dimension is Dimension.INTERVAL:
        return f"in {value}"
    return value


def _days_words(days: Sequence[Weekday]) -> str:
    ordered = sorted(set(days), key=list(Weekday).index)
    return join_list([_DAY_PLURALS[day] for day in ordered])


def _medication_state(
    subject: str, date_text: str, by_dimension: Mapping[Dimension, PlanEntry]
) -> dict[str, str]:
    action_entry = by_dimension.get(Dimension.ACTION)
    action = MedAction(action_entry.values[0]) if action_entry else MedAction.CONTINUE
    details = ""
    if action not in _PAUSED_STATES:
        words = [
            _one_value(dimension, by_dimension[dimension].values[0])
            for dimension in (Dimension.DOSE, Dimension.TIME_OF_DAY, Dimension.FOOD_RELATION)
            if dimension in by_dimension
        ]
        details = f": {' '.join(words)}" if words else ""
    return {
        "date": date_text,
        "subject": subject,
        "state": _STATE_WORDS[action],
        "details": details,
    }


def _plan_overview(
    day: date,
    entries: Sequence[PlanEntry],
    commits: Mapping[str, CareCommit],
    names: Mapping[str, str],
) -> str:
    date_text = spoken_date(day)
    if not entries:
        return render(TemplateId.SPEAK_PLAN_EMPTY, {"date": date_text})
    items = []
    for entity_id, group in groupby(entries, key=lambda entry: entry.entity_id):
        by_dimension = {entry.dimension: entry for entry in group}
        lead = by_dimension.get(Dimension.ACTION) or next(iter(by_dimension.values()))
        commit = _latest_commit(lead, commits)
        if commit.kind is CommitKind.MEDICATION_INSTRUCTION:
            action_entry = by_dimension.get(Dimension.ACTION)
            action = MedAction(action_entry.values[0]) if action_entry else MedAction.CONTINUE
            items.append(f"{names.get(entity_id, entity_id)} {_STATE_WORDS[action]}")
        else:
            items.append(item_phrase(commit))
    overview = render(
        TemplateId.SPEAK_PLAN_OVERVIEW,
        {"date": date_text, "item_list": join_list(items[:MAX_SPOKEN_ITEMS])},
    )
    return " ".join([overview, render(TemplateId.SPEAK_NOT_DECIDING, {})])


def _latest_commit(entry: PlanEntry, commits: Mapping[str, CareCommit]) -> CareCommit:
    candidates = [commits[commit_id] for commit_id in entry.commit_ids]
    return max(candidates, key=lambda commit: commit.source.captured_at)


def _matches(subject: str, name: str) -> bool:
    wanted, known = subject.casefold().strip(), name.casefold().strip()
    return bool(wanted) and (wanted == known or known in wanted or wanted in known)


def _question_count(count: int) -> dict[str, str]:
    return {
        "question_count": f"{count} {'question' if count == 1 else 'questions'}",
        "question_verb": "needs" if count == 1 else "need",
    }


def _with_more(sentence: str, more: bool) -> str:
    return f"{sentence} {render(TemplateId.SPEAK_MORE_ON_SCREEN, {})}" if more else sentence
