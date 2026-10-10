"""The simulated Alexa: one spoken turn at a time (spec §6.3, §11).

A turn either resolves a pending confirmation with a recognized yes or no,
or goes to the orchestrator, which picks one model-visible tool. The host
speaks only the tool's template-rendered ``speech`` or a fixed template, and
it alone calls the app-only tools that change state.
"""

from collections.abc import Mapping
from typing import Any, Literal

import structlog
from pydantic import BaseModel, ConfigDict

from caremerge_addon.mcp.results import ReminderListResult, VisitListResult
from caremerge_core.enums import TemplateId
from caremerge_core.questions import render
from caremerge_simulator.addon_client import AddonTools
from caremerge_simulator.answers import classify_answer
from caremerge_simulator.cards import Card, card_for
from caremerge_simulator.confirmations import (
    CONFIRM_TOOLS,
    PendingConfirmation,
    PendingStore,
    PendingView,
)
from caremerge_simulator.errors import AddonUnavailableError
from caremerge_simulator.orchestrator.base import Orchestrator
from caremerge_simulator.runtime import IdFactory

log = structlog.get_logger(__name__)


class TurnResult(BaseModel):
    """What the simulator says and shows after one turn."""

    model_config = ConfigDict(frozen=True)

    speech: str
    card: Card | None = None
    pending: PendingView | None = None
    error: bool = False


class HealthView(BaseModel):
    """Whether the add-on answers, and how many tools the model may use."""

    model_config = ConfigDict(frozen=True)

    addon_reachable: bool
    model_tools: int


class SimulatorHost:
    """Runs turns against the add-on through an orchestrator."""

    def __init__(
        self,
        addon: AddonTools,
        orchestrator: Orchestrator,
        pending: PendingStore,
        ids: IdFactory,
    ) -> None:
        self._addon = addon
        self._orchestrator = orchestrator
        self._pending = pending
        self._ids = ids

    async def turn(self, text: str) -> TurnResult:
        """Answer one spoken or typed request."""
        current = self._pending.current()
        answer = classify_answer(text)
        if current is not None and answer is not None:
            self._pending.clear()
            if answer == "yes":
                return await self._confirm(current)
            return TurnResult(speech=_say(TemplateId.SPEAK_DECLINED))
        self._pending.clear()
        try:
            tools = await self._addon.model_tools()
        except AddonUnavailableError:
            return TurnResult(speech=_say(TemplateId.SPEAK_UNAVAILABLE), error=True)
        call = await self._orchestrator.route(text, tools)
        if call is None or call.name not in {tool.name for tool in tools}:
            log.info("turn_unrouted")
            return TurnResult(speech=_say(TemplateId.SPEAK_FALLBACK))
        log.info("turn_routed", tool=call.name)
        return await self._run(call.name, call.arguments)

    async def confirm(self, pending_id: str, answer: Literal["yes", "no"]) -> TurnResult:
        """Resolve a pending confirmation from a tap on its card."""
        pending = self._pending.take(pending_id)
        if answer == "yes":
            return await self._confirm(pending)
        return TurnResult(speech=_say(TemplateId.SPEAK_DECLINED))

    async def add_visit(self, visit_id: str) -> TurnResult:
        """Add a visit from the inbox; this waits for extraction."""
        self._pending.clear()
        return await self._run("add_visit", {"visit_id": visit_id}, intake=True)

    async def inbox(self) -> VisitListResult:
        """Return the visit inbox."""
        outcome = await self._addon.call("list_visits", {})
        return VisitListResult.model_validate(outcome.structured)

    async def reminders(self) -> ReminderListResult:
        """Return the stored reminders."""
        outcome = await self._addon.call("list_reminders", {})
        return ReminderListResult.model_validate(outcome.structured)

    async def delete_data(self) -> TurnResult:
        """Delete the user's data; the UI asks for confirmation first."""
        self._pending.clear()
        return await self._run("delete_my_data", {"confirmation_id": self._ids.new("conf")})

    async def health(self) -> HealthView:
        """Report whether the add-on answers."""
        try:
            tools = await self._addon.model_tools()
        except AddonUnavailableError:
            return HealthView(addon_reachable=False, model_tools=0)
        return HealthView(addon_reachable=True, model_tools=len(tools))

    async def _confirm(self, pending: PendingConfirmation) -> TurnResult:
        arguments = {**pending.arguments, "confirmation_id": self._ids.new("conf")}
        log.info("confirmation_resolved", tool=pending.tool)
        return await self._run(pending.tool, arguments)

    async def _run(
        self, name: str, arguments: Mapping[str, Any], *, intake: bool = False
    ) -> TurnResult:
        try:
            outcome = await self._addon.call(name, arguments, intake=intake)
        except AddonUnavailableError:
            return TurnResult(speech=_say(TemplateId.SPEAK_UNAVAILABLE), error=True)
        if outcome.is_error:
            return TurnResult(speech=outcome.speech, error=True)
        pending = self._remember(outcome.structured.get("confirmation"))
        return TurnResult(
            speech=outcome.speech, card=card_for(name, outcome.structured), pending=pending
        )

    def _remember(self, confirmation: Any) -> PendingView | None:
        if not isinstance(confirmation, dict) or confirmation.get("tool") not in CONFIRM_TOOLS:
            return None
        return self._pending.put(
            PendingConfirmation.model_validate(
                {**confirmation, "pending_id": self._ids.new("pend")}
            )
        )


def _say(template_id: TemplateId) -> str:
    return render(template_id, {})
