"""Tests for the simulated Alexa: spoken turns, confirmations, and the model boundary."""

import asyncio
from datetime import UTC, datetime

import pytest

from caremerge_simulator.addon_client import McpAddonClient
from caremerge_simulator.confirmations import PendingStore
from caremerge_simulator.errors import UnknownConfirmationError
from caremerge_simulator.host import SimulatorHost
from caremerge_simulator.orchestrator.keyword import KeywordOrchestrator
from caremerge_simulator.settings import SimulatorSettings

QUESTION = "When should the temporary hold of Medication A for the procedure end?"
SPOKEN_TOOLS = {
    "visit_updates",
    "whats_changed",
    "plan_for_day",
    "open_questions",
    "propose_reminder",
}


class _Clock:
    def now(self) -> datetime:
        return datetime(2026, 10, 19, 14, 0, tzinfo=UTC)


class _Ids:
    def new(self, prefix: str) -> str:
        return f"{prefix}_1"


def test_the_demo_conversation_by_voice(host: SimulatorHost) -> None:
    async def body() -> None:
        await host.add_visit("visit-1")
        first = await host.turn("What's new from my visit with Dr. Rivera?")
        assert first.pending is not None
        assert (await host.turn("Yes.")).speech == "Added to your care plan."
        arrived = await host.add_visit("visit-2")
        assert (
            arrived.speech == "Your visit with Dr. Lee on Wednesday, October 7 is ready to review."
        )
        updates = await host.turn("Alexa, what's new from my visit with Dr. Lee?")
        assert updates.speech.startswith(
            "Your visit with Dr. Lee on Wednesday, October 7 has 2 new"
        )
        assert updates.card is not None and updates.card.tool == "visit_updates"
        assert (await host.turn("Yes")).speech == "Added to your care plan."
        changed = await host.turn("What changed in my care plan?")
        assert changed.speech.startswith("Since your last visit, 2 things changed")
        plan = await host.turn("Should I take Medication A on Sunday?")
        assert plan.speech.startswith("On Sunday, October 25, Medication A is on hold")
        proposal = await host.turn("Remind me to ask when the hold ends.")
        assert proposal.speech == (
            f"I can remind you tomorrow at 10 AM: Ask your care team: {QUESTION} Should I add it?"
        )
        assert (await host.turn("yes please")).speech == "Done. It's in your reminders."
        reminders = await host.reminders()
        assert [r.text for r in reminders.reminders] == [f"Ask your care team: {QUESTION}"]

    asyncio.run(body())


def test_no_declines_and_anything_else_cancels_the_pending_change(host: SimulatorHost) -> None:
    async def body() -> None:
        await host.add_visit("visit-2")
        await host.turn("What's new from my visit with Dr. Lee?")
        assert (await host.turn("No.")).speech == "Okay, I won't change anything."
        await host.turn("What's new from my visit with Dr. Lee?")
        await host.turn("What changed in my care plan?")
        fallback = await host.turn("Yes")
        assert fallback.speech.startswith("I can tell you what changed in your care plan")
        still_new = await host.turn("What's new from my visit with Dr. Lee?")
        assert still_new.card is not None and still_new.card.tool == "visit_updates"
        assert len(still_new.card.data.items) == 2

    asyncio.run(body())


def test_a_tap_confirms_by_pending_id_once(host: SimulatorHost) -> None:
    async def body() -> None:
        await host.add_visit("visit-2")
        updates = await host.turn("What's new from my visit with Dr. Lee?")
        assert updates.pending is not None
        tapped = await host.confirm(updates.pending.pending_id, "yes")
        assert tapped.speech == "Added to your care plan."
        with pytest.raises(UnknownConfirmationError):
            await host.confirm(updates.pending.pending_id, "yes")

    asyncio.run(body())


def test_the_model_is_never_offered_app_only_tools(addon: McpAddonClient) -> None:
    tools = asyncio.run(addon.model_tools())
    assert {tool.name for tool in tools} == SPOKEN_TOOLS


def test_requests_outside_care_get_the_fallback(host: SimulatorHost) -> None:
    said = asyncio.run(host.turn("Play some music")).speech
    assert said == (
        "I can tell you what changed in your care plan, what it says for a day, what still "
        "needs clarifying, or set a reminder to ask your care team."
    )


def test_an_unreachable_addon_is_spoken_not_raised(settings: SimulatorSettings) -> None:
    offline = McpAddonClient("http://127.0.0.1:9/mcp", timeout_s=1, intake_timeout_s=1)
    host = SimulatorHost(
        offline, KeywordOrchestrator(_Clock(), settings.tz), PendingStore(), _Ids()
    )
    result = asyncio.run(host.turn("What changed in my care plan?"))
    assert (result.speech, result.error) == (
        "CareMerge isn't reachable right now. Try again in a moment.",
        True,
    )
