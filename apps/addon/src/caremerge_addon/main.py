"""Composition root: builds the add-on's services and its HTTP app.

Only this module constructs adapters. Local development wires the fixture
inbox, the stub extractor, and the in-memory ledger; M2 adds Bedrock
extraction and the DynamoDB ledger behind the same ports.
"""

from starlette.applications import Starlette

from caremerge_addon.extraction.stub import StubExtractionClient
from caremerge_addon.mcp.server import create_server
from caremerge_addon.runtime import SystemClock, UuidIds
from caremerge_addon.services import AddonServices
from caremerge_addon.settings import AddonSettings
from caremerge_addon.store.memory import MemoryLedger
from caremerge_addon.visits.fixture_inbox import FixtureVisitInbox


def build_services(settings: AddonSettings) -> AddonServices:
    """Wire the fixture inbox and stub extractor to an in-memory ledger."""
    return AddonServices(
        settings=settings,
        ledger=MemoryLedger(),
        inbox=FixtureVisitInbox.from_dir(settings.visits_dir),
        extraction=StubExtractionClient.from_dir(settings.stub_extractions_dir),
        clock=SystemClock(),
        ids=UuidIds(),
    )


def build_app(settings: AddonSettings) -> Starlette:
    """Build the Streamable HTTP app that serves the MCP endpoint at ``/mcp``."""
    server = create_server(build_services(settings))
    return server.streamable_http_app(stateless_http=True, host=settings.addon_host)
