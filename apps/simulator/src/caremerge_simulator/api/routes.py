"""FastAPI application for the simulator's local API (spec §11).

``create_app`` wires routes to a ``SimulatorHost`` through closures, so the
app holds no globals. Response bodies are typed (turns carry a discriminated
card union), and FastAPI publishes them in ``/openapi.json``, from which the
web app generates its types.
"""

from typing import Literal

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from caremerge_addon.mcp.results import ReminderListResult, VisitListResult
from caremerge_simulator.api.security import (
    LOOPBACK_NAMES,
    allowed_origins,
    origin_guard,
    token_guard,
)
from caremerge_simulator.errors import AddonUnavailableError, UnknownConfirmationError
from caremerge_simulator.host import SimulatorHost, TurnResult
from caremerge_simulator.settings import SimulatorSettings


class SessionView(BaseModel):
    """The per-launch token the web app sends on every other request."""

    model_config = ConfigDict(frozen=True)

    token: str


class HealthResponse(BaseModel):
    """Connection status for the simulator header."""

    model_config = ConfigDict(frozen=True)

    addon_reachable: bool
    model_tools: int
    orchestrator: str


class TurnRequest(BaseModel):
    """One spoken or typed request."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(min_length=1, max_length=500)


class ConfirmRequest(BaseModel):
    """A tap on a confirmation card."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    answer: Literal["yes", "no"]


def create_app(host: SimulatorHost, settings: SimulatorSettings, token: str) -> FastAPI:
    """Build the simulator API for one host and session token."""
    app = FastAPI(title="CareMerge Alexa+ simulator API", version="0.1.0")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(LOOPBACK_NAMES))
    check_origin = Depends(origin_guard(allowed_origins(settings)))
    public = APIRouter(prefix="/api", dependencies=[check_origin])
    private = APIRouter(prefix="/api", dependencies=[check_origin, Depends(token_guard(token))])

    @public.get("/session")
    def session() -> SessionView:
        return SessionView(token=token)

    @private.get("/health")
    async def health() -> HealthResponse:
        view = await host.health()
        return HealthResponse(
            addon_reachable=view.addon_reachable,
            model_tools=view.model_tools,
            orchestrator=settings.orchestrator,
        )

    @private.post("/turn")
    async def turn(request: TurnRequest) -> TurnResult:
        return await host.turn(request.text)

    @private.post("/confirmations/{pending_id}")
    async def confirm(pending_id: str, request: ConfirmRequest) -> TurnResult:
        return await host.confirm(pending_id, request.answer)

    @private.get("/inbox")
    async def inbox() -> VisitListResult:
        return await host.inbox()

    @private.post("/inbox/{visit_id}")
    async def add_visit(visit_id: str) -> TurnResult:
        return await host.add_visit(visit_id)

    @private.get("/reminders")
    async def reminders() -> ReminderListResult:
        return await host.reminders()

    @private.delete("/data")
    async def delete_data() -> TurnResult:
        return await host.delete_data()

    app.include_router(public)
    app.include_router(private)

    @app.exception_handler(UnknownConfirmationError)
    def unknown_confirmation(_: Request, error: UnknownConfirmationError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": "nothing is waiting for that"})

    @app.exception_handler(AddonUnavailableError)
    def unavailable(_: Request, error: AddonUnavailableError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": "add-on unavailable"})

    return app
