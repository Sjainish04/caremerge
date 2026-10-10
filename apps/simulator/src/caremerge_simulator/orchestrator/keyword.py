"""A deterministic phrase router for offline development and tests (spec §11).

It recognizes the demo's requests by keywords and resolves spoken dates
("Sunday", "tomorrow", "October 28") against the clock. The Bedrock
orchestrator replaces it on camera; this one keeps every flow testable
without a model.
"""

import re
from collections.abc import Sequence
from datetime import date, timedelta
from typing import Final
from zoneinfo import ZoneInfo

from caremerge_simulator.addon_client import ToolSpec
from caremerge_simulator.orchestrator.base import ToolCall
from caremerge_simulator.runtime import Clock

_WEEKDAYS: Final = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
_MONTHS: Final = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)
_MONTH_DAY: Final = re.compile(rf"\b({'|'.join(_MONTHS)}) (\d{{1,2}})(?:st|nd|rd|th)?\b")
_SUBJECT: Final = re.compile(
    r"\b(?:take|about)\s+(?P<subject>.+?)(?=\s+(?:on|this|today|tomorrow|next)\b|[?.!]|$)",
    re.IGNORECASE,
)
_CLINICIAN: Final = re.compile(
    r"\b(?:with|from)\s+(?:my\s+|the\s+)?(?P<who>dr\.?\s*\w+|\w*\s*pharmacist)\b", re.IGNORECASE
)


class KeywordOrchestrator:
    """Routes the demo's requests by keyword."""

    def __init__(self, clock: Clock, tz: ZoneInfo) -> None:
        self._clock = clock
        self._tz = tz

    async def route(self, text: str, tools: Sequence[ToolSpec]) -> ToolCall | None:
        """Return the tool call for ``text``, or ``None`` when nothing matches."""
        said = text.casefold()
        if "remind" in said:
            return ToolCall(name="propose_reminder", arguments={})
        if "what changed" in said or "what's changed" in said or "changes" in said:
            return ToolCall(name="whats_changed", arguments={})
        if "new" in said and (
            "visit" in said or "from" in said or said.rstrip("?.! ").endswith("new")
        ):
            return ToolCall(name="visit_updates", arguments=_clinician(text))
        if "question" in said or "clarif" in said:
            return ToolCall(name="open_questions", arguments={})
        day = self._day(said)
        if day is not None or "take" in said or "plan" in said:
            arguments: dict[str, str] = {"day": (day or self._today()).isoformat()}
            subject = _SUBJECT.search(text)
            if subject:
                arguments["subject"] = subject.group("subject").strip()
            return ToolCall(name="plan_for_day", arguments=arguments)
        return None

    def _today(self) -> date:
        return self._clock.now().astimezone(self._tz).date()

    def _day(self, said: str) -> date | None:
        today = self._today()
        if "tomorrow" in said:
            return today + timedelta(days=1)
        if "today" in said:
            return today
        month_day = _MONTH_DAY.search(said)
        if month_day:
            return date(today.year, _MONTHS.index(month_day.group(1)) + 1, int(month_day.group(2)))
        for index, name in enumerate(_WEEKDAYS):
            if re.search(rf"\b{name}\b", said):
                return today + timedelta(days=(index - today.weekday()) % 7)
        return None


def _clinician(text: str) -> dict[str, str]:
    match = _CLINICIAN.search(text)
    if not match:
        return {}
    who = re.sub(r"^dr\.?\s*", "", match.group("who").strip(), flags=re.IGNORECASE)
    return {"clinician": who.casefold()}
