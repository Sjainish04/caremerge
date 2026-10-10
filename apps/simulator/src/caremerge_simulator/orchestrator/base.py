"""The orchestrator port: a spoken request in, at most one tool call out.

An orchestrator only routes. Its own words are never spoken (principle P9);
the host speaks the chosen tool's template-rendered result.
"""

from collections.abc import Sequence
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from caremerge_simulator.addon_client import ToolSpec


class ToolCall(BaseModel):
    """The tool to call and its arguments."""

    model_config = ConfigDict(frozen=True)

    name: str
    arguments: dict[str, Any]


class Orchestrator(Protocol):
    """Map one request to one model-visible tool, or to nothing."""

    async def route(self, text: str, tools: Sequence[ToolSpec]) -> ToolCall | None:
        """Return the tool call for ``text``, or ``None`` when no tool fits."""
        ...
