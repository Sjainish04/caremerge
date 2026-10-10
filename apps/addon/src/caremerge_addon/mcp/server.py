"""The CareMerge MCP server: tools registered with their visibility (spec §7.1, §7.2).

Spoken tools are visible to the model and answer requests. Tools that change
state carry ``_meta.ui.visibility: ["app"]`` (MCP Apps), so a host never
offers them to the model; only the user's tap or recognized "yes" reaches
them. Every result's text content is its template-rendered ``speech``; the
structured content is the card data. Errors become templated speech with
codes only.
"""

from collections.abc import Callable
from datetime import date
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import AwareDatetime, Field

from caremerge_addon import speech
from caremerge_addon.errors import InvalidRequestError, RecordNotFoundError
from caremerge_addon.mcp import tools
from caremerge_addon.mcp.results import (
    DataDeletedResult,
    ItemsAddedResult,
    OpenQuestionsResult,
    PlanDayResult,
    ReminderListResult,
    ReminderProposalResult,
    ReminderStoredResult,
    ResultModel,
    ToolErrorResult,
    VisitAddedResult,
    VisitListResult,
    VisitUpdatesResult,
    WhatsChangedResult,
)
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.services import AddonServices
from caremerge_core.enums import TemplateId
from caremerge_core.policy import PolicyViolationError

INSTRUCTIONS = (
    "CareMerge keeps a versioned care plan built from the user's care visits. "
    "Say each result's text exactly as given; it is written from verified records. "
    "Never give medical advice or decide between instructions. Tools that change the "
    "care plan are confirmed by the user, never by you."
)
SPOKEN = ToolAnnotations(read_only_hint=True, open_world_hint=False)
PROPOSES = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False)
CHANGES = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False)
DELETES = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=False)
ConfirmationId = Annotated[str, Field(min_length=1)]


def _app_only() -> dict[str, Any]:
    return {"ui": {"visibility": ["app"]}}


def create_server(services: AddonServices) -> MCPServer:
    """Build the add-on's MCP server over ``services``."""
    server = MCPServer(
        name="caremerge",
        title="CareMerge",
        version="0.1.0",
        instructions=INSTRUCTIONS,
    )

    def context() -> PipelineContext:
        return services.context_for(services.settings.local_user_id)

    @server.tool(
        description=(
            "New care items from the user's most recent visit that still need their "
            "confirmation. Use when they ask what's new from a visit or a clinician."
        ),
        annotations=SPOKEN,
    )
    def visit_updates(
        clinician: str | None = None,
    ) -> Annotated[CallToolResult, VisitUpdatesResult]:
        return respond(lambda: tools.visit_updates(context(), clinician))

    @server.tool(
        description="What changed in the user's confirmed care plan since their last visit.",
        annotations=SPOKEN,
    )
    def whats_changed() -> Annotated[CallToolResult, WhatsChangedResult]:
        return respond(lambda: tools.whats_changed(context()))

    @server.tool(
        description=(
            "What the user's confirmed care plan says on a date, optionally for one "
            "medication or event, e.g. 'should I take Medication A on Sunday?'. "
            "Resolve the date to an ISO date first."
        ),
        annotations=SPOKEN,
    )
    def plan_for_day(
        day: date, subject: str | None = None
    ) -> Annotated[CallToolResult, PlanDayResult]:
        return respond(lambda: tools.plan_for_day(context(), day, subject))

    @server.tool(
        description="Open questions about the care plan that need clarifying with the care team.",
        annotations=SPOKEN,
    )
    def open_questions() -> Annotated[CallToolResult, OpenQuestionsResult]:
        return respond(lambda: tools.open_questions(context()))

    @server.tool(
        description=(
            "Propose a reminder to ask the care team an open question (question_id), or "
            "to restate a confirmed instruction (commit_id). With neither, the newest open "
            "question is used. The user confirms the reminder, never you."
        ),
        annotations=PROPOSES,
    )
    def propose_reminder(
        question_id: str | None = None,
        commit_id: str | None = None,
        alarm_at: AwareDatetime | None = None,
    ) -> Annotated[CallToolResult, ReminderProposalResult]:
        return respond(lambda: tools.propose_reminder(context(), question_id, commit_id, alarm_at))

    @server.tool(
        description="Add confirmed visit items to the care plan (app only).",
        annotations=CHANGES,
        meta=_app_only(),
    )
    def confirm_items(
        commit_ids: Annotated[list[str], Field(min_length=1)],
        confirmation_id: ConfirmationId,
    ) -> Annotated[CallToolResult, ItemsAddedResult]:
        return respond(lambda: tools.confirm_items(context(), commit_ids, confirmation_id))

    @server.tool(
        description="Store a confirmed reminder (app only).",
        annotations=CHANGES,
        meta=_app_only(),
    )
    def confirm_reminder(
        action_id: str, confirmation_id: ConfirmationId
    ) -> Annotated[CallToolResult, ReminderStoredResult]:
        return respond(lambda: tools.confirm_reminder(context(), action_id, confirmation_id))

    @server.tool(
        description="Add a visit from the inbox and read it (app only).",
        annotations=CHANGES,
        meta=_app_only(),
    )
    def add_visit(visit_id: str) -> Annotated[CallToolResult, VisitAddedResult]:
        return respond(lambda: tools.add_visit(context(), visit_id))

    @server.tool(description="List inbox visits (app only).", annotations=SPOKEN, meta=_app_only())
    def list_visits() -> Annotated[CallToolResult, VisitListResult]:
        return respond(lambda: tools.list_visits(context()))

    @server.tool(
        description="List stored reminders (app only).", annotations=SPOKEN, meta=_app_only()
    )
    def list_reminders() -> Annotated[CallToolResult, ReminderListResult]:
        return respond(lambda: tools.list_reminders(context()))

    @server.tool(
        description="Delete all of the user's CareMerge data (app only).",
        annotations=DELETES,
        meta=_app_only(),
    )
    def delete_my_data(
        confirmation_id: ConfirmationId,
    ) -> Annotated[CallToolResult, DataDeletedResult]:
        return respond(lambda: tools.delete_my_data(context(), confirmation_id))

    return server


def respond(produce: Callable[[], ResultModel]) -> CallToolResult:
    """Run a tool and turn its result, or a known error, into a ``CallToolResult``."""
    try:
        result = produce()
    except RecordNotFoundError:
        return _error("not_found", TemplateId.SPEAK_NOT_FOUND, [])
    except PolicyViolationError as error:
        return _error("policy_violation", TemplateId.SPEAK_REFUSED, [str(c) for c in error.codes])
    except InvalidRequestError:
        return _error("invalid_arguments", TemplateId.SPEAK_NOT_FOUND, [])
    return CallToolResult(
        content=[TextContent(type="text", text=result.speech)],
        structured_content=result.model_dump(mode="json"),
    )


def _error(code: str, template_id: TemplateId, codes: list[str]) -> CallToolResult:
    error = ToolErrorResult.model_validate(
        {"speech": speech.sentence(template_id), "code": code, "codes": codes}
    )
    return CallToolResult(
        content=[TextContent(type="text", text=error.speech)],
        structured_content=error.model_dump(mode="json"),
        is_error=True,
    )
