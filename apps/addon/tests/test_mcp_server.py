"""MCP contract tests: an in-process client against the add-on server (spec §7, §16.3)."""

import asyncio
import re
import time
from collections.abc import Awaitable, Callable
from typing import Any

from mcp import Client
from mcp.types import CallToolResult, TextContent

from caremerge_addon.mcp.server import create_server
from caremerge_addon.services import AddonServices

SPOKEN_TOOLS = {
    "visit_updates",
    "whats_changed",
    "plan_for_day",
    "open_questions",
    "propose_reminder",
}
APP_ONLY_TOOLS = {
    "confirm_items",
    "confirm_reminder",
    "add_visit",
    "list_visits",
    "list_reminders",
    "delete_my_data",
}
QUESTION = "When should the temporary hold of Medication A for the procedure end?"
ID_PATTERN = re.compile(r"\b(cc|iss|act|src|ent)_\w+")


def _run(services: AddonServices, body: Callable[[Client], Awaitable[Any]]) -> Any:
    async def main() -> Any:
        async with Client(create_server(services)) as client:
            return await body(client)

    return asyncio.run(main())


def _speech(result: CallToolResult) -> str:
    (content,) = result.content
    assert isinstance(content, TextContent)
    return content.text


def test_tools_are_split_between_the_model_and_the_app(services: AddonServices) -> None:
    async def body(client: Client) -> None:
        tools = (await client.list_tools()).tools
        assert {tool.name for tool in tools} == SPOKEN_TOOLS | APP_ONLY_TOOLS
        app_only = {
            tool.name
            for tool in tools
            if (tool.meta or {}).get("ui", {}).get("visibility") == ["app"]
        }
        assert app_only == APP_ONLY_TOOLS
        assert all(tool.output_schema for tool in tools)
        assert all(tool.description for tool in tools if tool.name in SPOKEN_TOOLS)

    _run(services, body)


def test_the_demo_conversation_end_to_end(services: AddonServices) -> None:
    async def body(client: Client) -> list[str]:
        said: list[str] = []

        async def call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            started = time.perf_counter()
            result = await client.call_tool(name, arguments)
            elapsed = time.perf_counter() - started
            assert not result.is_error, _speech(result)
            structured = result.structured_content or {}
            assert _speech(result) == structured["speech"]
            if name in SPOKEN_TOOLS:
                assert elapsed < 0.5, f"{name} took {elapsed:.3f}s"
                assert not ID_PATTERN.search(_speech(result))
                said.append(_speech(result))
            return structured

        await call("add_visit", {"visit_id": "visit-1"})
        first = await call("visit_updates", {})
        await call(
            "confirm_items", {**first["confirmation"]["arguments"], "confirmation_id": "c-1"}
        )
        await call("add_visit", {"visit_id": "visit-2"})
        updates = await call("visit_updates", {"clinician": "Dr. Lee"})
        confirmation = updates["confirmation"]
        assert confirmation["tool"] == "confirm_items"
        await call(confirmation["tool"], {**confirmation["arguments"], "confirmation_id": "c-2"})
        changed = await call("whats_changed", {})
        assert changed["open_questions"] == 1
        await call("plan_for_day", {"day": "2026-10-25", "subject": "Medication A"})
        await call("open_questions", {})
        proposal = await call("propose_reminder", {})
        stored = await call(
            "confirm_reminder",
            {**proposal["confirmation"]["arguments"], "confirmation_id": "c-3"},
        )
        assert stored["reminder"]["state"] == "executed"
        reminders = await call("list_reminders", {})
        assert [r["text"] for r in reminders["reminders"]] == [f"Ask your care team: {QUESTION}"]
        return said

    said = _run(services, body)
    assert said[1].startswith("Your visit with Dr. Lee on Wednesday, October 7 has 2 new items:")
    assert said[2].startswith("Since your last visit, 2 things changed in your care plan.")
    assert said[3].startswith("On Sunday, October 25, Medication A is on hold in your care plan.")
    assert said[5] == (
        f"I can remind you tomorrow at 10 AM: Ask your care team: {QUESTION} Should I add it?"
    )


def test_errors_are_spoken_from_templates_with_codes_only(services: AddonServices) -> None:
    async def body(client: Client) -> tuple[CallToolResult, CallToolResult, CallToolResult]:
        missing = await client.call_tool(
            "confirm_reminder", {"action_id": "act_404", "confirmation_id": "c-1"}
        )
        await client.call_tool("add_visit", {"visit_id": "visit-2"})
        updates = await client.call_tool("visit_updates", {})
        hold_id = (updates.structured_content or {})["items"][1]["commit_id"]
        refused = await client.call_tool("propose_reminder", {"commit_id": hold_id})
        both = await client.call_tool(
            "propose_reminder", {"question_id": "iss_1", "commit_id": hold_id}
        )
        return missing, refused, both

    missing, refused, both = _run(services, body)
    assert missing.is_error and _speech(missing) == "I couldn't find that in your care plan."
    assert (missing.structured_content or {})["code"] == "not_found"
    assert refused.is_error
    assert (refused.structured_content or {})["codes"] == ["unverified_commit"]
    assert _speech(refused) == (
        "I can't do that, because it no longer matches your confirmed care plan."
    )
    assert (both.structured_content or {})["code"] == "invalid_arguments"
