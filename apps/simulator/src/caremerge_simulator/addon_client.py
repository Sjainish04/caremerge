"""The simulator's MCP client for the CareMerge add-on (spec §7, §11).

``McpAddonClient`` connects per call, over Streamable HTTP for a URL or in
process for a server instance (tests). ``model_tools`` drops every tool whose
``_meta.ui.visibility`` excludes ``"model"`` (MCP Apps), so the orchestrator
is never offered a tool that changes state.
"""

from collections.abc import Mapping
from typing import Any, Protocol

import structlog
from mcp import Client
from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, TextContent, Tool
from pydantic import BaseModel, ConfigDict

from caremerge_simulator.errors import AddonUnavailableError

log = structlog.get_logger(__name__)


class ToolSpec(BaseModel):
    """A tool the orchestrator may call."""

    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    input_schema: dict[str, Any]


class ToolOutcome(BaseModel):
    """What a tool call returned: the sentence to speak and the card data."""

    model_config = ConfigDict(frozen=True)

    speech: str
    structured: dict[str, Any]
    is_error: bool


class AddonTools(Protocol):
    """The add-on, as the simulator sees it."""

    async def model_tools(self) -> list[ToolSpec]:
        """Return the tools the model may call."""
        ...

    async def call(
        self, name: str, arguments: Mapping[str, Any], *, intake: bool = False
    ) -> ToolOutcome:
        """Call one tool; ``intake`` allows the longer extraction timeout."""
        ...


class McpAddonClient:
    """Calls the add-on over MCP, one connection per call."""

    def __init__(
        self, target: str | MCPServer, *, timeout_s: float, intake_timeout_s: float
    ) -> None:
        self._target = target
        self._timeout_s = timeout_s
        self._intake_timeout_s = intake_timeout_s

    async def model_tools(self) -> list[ToolSpec]:
        """Return the model-visible tools."""
        try:
            async with Client(self._target, read_timeout_seconds=self._timeout_s) as client:
                listed = await client.list_tools()
        except Exception as error:
            raise _unavailable(error) from error
        return [
            ToolSpec(
                name=tool.name, description=tool.description or "", input_schema=tool.input_schema
            )
            for tool in listed.tools
            if _model_visible(tool)
        ]

    async def call(
        self, name: str, arguments: Mapping[str, Any], *, intake: bool = False
    ) -> ToolOutcome:
        """Call one tool and return its speech and structured content."""
        timeout = self._intake_timeout_s if intake else self._timeout_s
        try:
            async with Client(self._target, read_timeout_seconds=timeout) as client:
                result = await client.call_tool(name, dict(arguments))
        except Exception as error:
            raise _unavailable(error) from error
        return ToolOutcome(
            speech=_text(result),
            structured=result.structured_content or {},
            is_error=bool(result.is_error),
        )


def _model_visible(tool: Tool) -> bool:
    visibility = (tool.meta or {}).get("ui", {}).get("visibility")
    return visibility is None or "model" in visibility


def _text(result: CallToolResult) -> str:
    return " ".join(block.text for block in result.content if isinstance(block, TextContent))


def _unavailable(error: Exception) -> AddonUnavailableError:
    log.warning("addon_unavailable", error_type=type(error).__name__)
    return AddonUnavailableError(type(error).__name__)
