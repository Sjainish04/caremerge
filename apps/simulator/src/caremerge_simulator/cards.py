"""Typed cards the simulator UI renders, one per tool result (spec §12.4).

The add-on's structured results are validated here before they reach the
browser, so a malformed result shows no card instead of a broken one. The
``tool`` field discriminates the union, which ``openapi-typescript`` turns
into a typed union for the web app.
"""

from collections.abc import Mapping
from typing import Annotated, Any, Literal

import structlog
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from caremerge_addon.mcp.results import (
    DataDeletedResult,
    ItemsAddedResult,
    OpenQuestionsResult,
    PlanDayResult,
    ReminderProposalResult,
    ReminderStoredResult,
    VisitAddedResult,
    VisitUpdatesResult,
    WhatsChangedResult,
)

log = structlog.get_logger(__name__)


class _Card(BaseModel):
    model_config = ConfigDict(frozen=True)


class VisitUpdatesCard(_Card):
    """New items from a visit, awaiting confirmation."""

    tool: Literal["visit_updates"]
    data: VisitUpdatesResult


class WhatsChangedCard(_Card):
    """What changed since the last visit."""

    tool: Literal["whats_changed"]
    data: WhatsChangedResult


class PlanDayCard(_Card):
    """The plan on one day."""

    tool: Literal["plan_for_day"]
    data: PlanDayResult


class OpenQuestionsCard(_Card):
    """Open clarification questions."""

    tool: Literal["open_questions"]
    data: OpenQuestionsResult


class ReminderProposalCard(_Card):
    """A reminder awaiting confirmation."""

    tool: Literal["propose_reminder"]
    data: ReminderProposalResult


class ItemsAddedCard(_Card):
    """Items just added to the care plan."""

    tool: Literal["confirm_items"]
    data: ItemsAddedResult


class ReminderStoredCard(_Card):
    """A reminder just stored."""

    tool: Literal["confirm_reminder"]
    data: ReminderStoredResult


class VisitAddedCard(_Card):
    """A visit just added from the inbox."""

    tool: Literal["add_visit"]
    data: VisitAddedResult


class DataDeletedCard(_Card):
    """The user's data was deleted."""

    tool: Literal["delete_my_data"]
    data: DataDeletedResult


Card = Annotated[
    VisitUpdatesCard
    | WhatsChangedCard
    | PlanDayCard
    | OpenQuestionsCard
    | ReminderProposalCard
    | ItemsAddedCard
    | ReminderStoredCard
    | VisitAddedCard
    | DataDeletedCard,
    Field(discriminator="tool"),
]
_CARDS: TypeAdapter[Card] = TypeAdapter(Card)


def card_for(tool: str, structured: Mapping[str, Any]) -> Card | None:
    """Return the validated card for a tool result, or ``None`` if it doesn't fit."""
    try:
        return _CARDS.validate_python({"tool": tool, "data": dict(structured)})
    except ValidationError:
        log.warning("card_invalid", tool=tool)
        return None
