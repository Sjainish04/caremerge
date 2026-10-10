"""Pending confirmations: the one state change awaiting the user's yes (spec §6.3).

A tool result may name an app-only tool to call after the user agrees. The
host keeps it here, outside the model's reach, until a recognized yes or a
tap resolves it. Any other request cancels it.
"""

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict

from caremerge_simulator.errors import UnknownConfirmationError

ConfirmTool = Literal["confirm_items", "confirm_reminder"]
CONFIRM_TOOLS: Final = frozenset({"confirm_items", "confirm_reminder"})


class PendingConfirmation(BaseModel):
    """An app-only call to make if, and only if, the user says yes."""

    model_config = ConfigDict(frozen=True)

    pending_id: str
    tool: ConfirmTool
    arguments: dict[str, str | list[str]]


class PendingView(BaseModel):
    """What the UI needs to offer a confirmation button."""

    model_config = ConfigDict(frozen=True)

    pending_id: str
    tool: ConfirmTool


class PendingStore:
    """Holds at most one pending confirmation for the local user."""

    def __init__(self) -> None:
        self._pending: PendingConfirmation | None = None

    def put(self, confirmation: PendingConfirmation) -> PendingView:
        """Replace any pending confirmation with ``confirmation``."""
        self._pending = confirmation
        return PendingView(pending_id=confirmation.pending_id, tool=confirmation.tool)

    def current(self) -> PendingConfirmation | None:
        """Return the pending confirmation, if any."""
        return self._pending

    def take(self, pending_id: str) -> PendingConfirmation:
        """Remove and return the pending confirmation with ``pending_id``."""
        pending = self._pending
        if pending is None or pending.pending_id != pending_id:
            raise UnknownConfirmationError(pending_id)
        self._pending = None
        return pending

    def clear(self) -> None:
        """Drop any pending confirmation."""
        self._pending = None
