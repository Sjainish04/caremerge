"""Tests for yes/no recognition and the keyword orchestrator's routing."""

import asyncio
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from caremerge_simulator.answers import classify_answer
from caremerge_simulator.orchestrator.base import ToolCall
from caremerge_simulator.orchestrator.keyword import KeywordOrchestrator


class _Clock:
    def now(self) -> datetime:
        return datetime(2026, 10, 19, 14, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("said", "answer"),
    [
        ("Yes.", "yes"),
        ("Alexa, yes please", "yes"),
        ("Sure", "yes"),
        ("Go ahead.", "yes"),
        ("No thanks", "no"),
        ("not now", "no"),
        ("Cancel", "no"),
        ("Yes, but only the procedure", None),
        ("What changed?", None),
    ],
)
def test_yes_and_no_are_recognized_exactly(said: str, answer: str | None) -> None:
    assert classify_answer(said) == answer


@pytest.mark.parametrize(
    ("said", "call"),
    [
        (
            "Alexa, what's new from my visit with Dr. Lee?",
            ToolCall(name="visit_updates", arguments={"clinician": "lee"}),
        ),
        ("What's new?", ToolCall(name="visit_updates", arguments={})),
        ("What changed in my care plan?", ToolCall(name="whats_changed", arguments={})),
        (
            "Should I take Medication A on Sunday?",
            ToolCall(
                name="plan_for_day", arguments={"day": "2026-10-25", "subject": "Medication A"}
            ),
        ),
        (
            "What's my plan for tomorrow?",
            ToolCall(name="plan_for_day", arguments={"day": "2026-10-20"}),
        ),
        (
            "What does my plan say about the procedure on October 28?",
            ToolCall(
                name="plan_for_day", arguments={"day": "2026-10-28", "subject": "the procedure"}
            ),
        ),
        ("Any open questions?", ToolCall(name="open_questions", arguments={})),
        ("Remind me to ask when the hold ends.", ToolCall(name="propose_reminder", arguments={})),
        ("Play some music", None),
    ],
)
def test_keyword_routes_demo_requests(said: str, call: ToolCall | None) -> None:
    orchestrator = KeywordOrchestrator(_Clock(), ZoneInfo("America/New_York"))
    assert asyncio.run(orchestrator.route(said, [])) == call
