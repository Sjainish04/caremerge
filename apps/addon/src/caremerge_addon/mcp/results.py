"""Structured results of the add-on's MCP tools (spec §7.2).

Each result carries ``speech``, the template-rendered sentence a voice host
says, plus the data a screen renders as cards. Values are words a person
reads ("on hold", "every morning"), never internal codes; IDs are present
only so a host can call the next tool, and are never spoken.
"""

from datetime import date
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict

from caremerge_core.enums import ActionState, ChangeType, CommitKind, Dimension, Role
from caremerge_core.models import Signals


class ResultModel(BaseModel):
    """Base for tool results: immutable, with the sentence to speak."""

    model_config = ConfigDict(frozen=True)

    speech: str


class SourceInfo(BaseModel):
    """Where an item came from: who said it, when, and the exact words."""

    model_config = ConfigDict(frozen=True)

    clinician: str
    role: Role
    date: date
    quote: str


class PendingConfirmation(BaseModel):
    """The app-only tool a host calls, with these arguments, after the user says yes."""

    model_config = ConfigDict(frozen=True)

    tool: Literal["confirm_items", "confirm_reminder"]
    arguments: dict[str, str | list[str]]


class ItemCard(BaseModel):
    """One captured item awaiting the user's confirmation."""

    model_config = ConfigDict(frozen=True)

    commit_id: str
    kind: CommitKind
    subject: str
    summary: str
    temporary: bool
    source: SourceInfo
    signals: Signals


class VisitUpdatesResult(ResultModel):
    """New items from one visit, and the confirmation that adds them."""

    clinician: str | None
    visit_date: date | None
    items: list[ItemCard]
    confirmation: PendingConfirmation | None


class ItemsAddedResult(ResultModel):
    """The items this confirmation verified."""

    commit_ids: list[str]


class SegmentCard(BaseModel):
    """A run of days with the same value; ``end`` is exclusive."""

    model_config = ConfigDict(frozen=True)

    start: date
    end: date
    values: list[str]
    temporary: bool
    end_captured: bool


class ChangeCard(BaseModel):
    """How one subject's dimension changed, with before and after runs."""

    model_config = ConfigDict(frozen=True)

    subject: str
    dimension: Dimension
    change: ChangeType
    before: list[SegmentCard]
    after: list[SegmentCard]
    future_effective: bool
    temporary: bool
    end_not_captured: bool
    sources: list[SourceInfo]


class WhatsChangedResult(ResultModel):
    """The CareDiff since the last visit and the open-question count."""

    changes: list[ChangeCard]
    open_questions: int


class PlanEntryCard(BaseModel):
    """What the plan says about one subject's dimension on a day."""

    model_config = ConfigDict(frozen=True)

    subject: str
    dimension: Dimension
    values: list[str]
    temporary: bool
    end_captured: bool
    source: SourceInfo


class PlanDayResult(ResultModel):
    """The plan on one day."""

    day: date
    entries: list[PlanEntryCard]


class QuestionCard(BaseModel):
    """An open clarification question and where its gap came from."""

    model_config = ConfigDict(frozen=True)

    issue_id: str
    question: str
    subject: str
    source: SourceInfo


class OpenQuestionsResult(ResultModel):
    """Every open clarification question."""

    questions: list[QuestionCard]


class ReminderCard(BaseModel):
    """A proposed or stored reminder."""

    model_config = ConfigDict(frozen=True)

    action_id: str
    text: str
    alarm_at: AwareDatetime
    state: ActionState
    based_on: SourceInfo | None


class ReminderProposalResult(ResultModel):
    """A proposed reminder and the confirmation that stores it, if there was a topic."""

    reminder: ReminderCard | None
    confirmation: PendingConfirmation | None


class ReminderStoredResult(ResultModel):
    """The reminder this confirmation stored."""

    reminder: ReminderCard


class VisitCard(BaseModel):
    """One visit in the inbox."""

    model_config = ConfigDict(frozen=True)

    visit_id: str
    title: str
    clinician: str
    role: Role
    date: date
    added: bool


class VisitAddedResult(ResultModel):
    """The visit added and what compiling it produced."""

    visit: VisitCard
    created: int
    rejected: int


class VisitListResult(ResultModel):
    """Every visit in the inbox."""

    visits: list[VisitCard]


class ReminderListResult(ResultModel):
    """Every stored reminder, soonest first."""

    reminders: list[ReminderCard]


class DataDeletedResult(ResultModel):
    """The user's partition was emptied."""


class ToolErrorResult(ResultModel):
    """Why a tool could not act; codes only, never content."""

    code: Literal["not_found", "policy_violation", "invalid_arguments"]
    codes: list[str]
