"""Shared fixtures for simulator tests: the real add-on server in process, pinned clock.

The clock is pinned to Monday Oct 19 2026, 10:00 EDT, the planned video day.
"""

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pytest
from mcp.server.mcpserver import MCPServer

from caremerge_addon.extraction.stub import StubExtractionClient
from caremerge_addon.mcp.server import create_server
from caremerge_addon.services import AddonServices
from caremerge_addon.settings import AddonSettings
from caremerge_addon.store.memory import MemoryLedger
from caremerge_addon.visits.fixture_inbox import FixtureVisitInbox
from caremerge_simulator.addon_client import McpAddonClient
from caremerge_simulator.confirmations import PendingStore
from caremerge_simulator.host import SimulatorHost
from caremerge_simulator.orchestrator.keyword import KeywordOrchestrator
from caremerge_simulator.settings import SimulatorSettings

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"
DEMO_NOW = datetime(2026, 10, 19, 14, 0, tzinfo=UTC)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--record-web-fixtures",
        action="store_true",
        help="record apps/web/src/test/fixtures again from a replay of the demo",
    )


class FixedClock:
    """A clock that returns a set time."""

    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current


class CounterIds:
    """Readable, deterministic IDs."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()

    def new(self, prefix: str) -> str:
        self._counts[prefix] += 1
        return f"{prefix}_{self._counts[prefix]}"


@pytest.fixture
def addon_server() -> MCPServer:
    settings = AddonSettings(
        _env_file=None,
        visits_dir=FIXTURES / "visits",
        stub_extractions_dir=FIXTURES / "extractions",
    )
    return create_server(
        AddonServices(
            settings=settings,
            ledger=MemoryLedger(),
            inbox=FixtureVisitInbox.from_dir(FIXTURES / "visits"),
            extraction=StubExtractionClient.from_dir(FIXTURES / "extractions"),
            clock=FixedClock(DEMO_NOW),
            ids=CounterIds(),
        )
    )


@pytest.fixture
def settings() -> SimulatorSettings:
    return SimulatorSettings(_env_file=None)


@pytest.fixture
def addon(addon_server: MCPServer, settings: SimulatorSettings) -> McpAddonClient:
    return McpAddonClient(
        addon_server,
        timeout_s=settings.addon_timeout_s,
        intake_timeout_s=settings.addon_intake_timeout_s,
    )


@pytest.fixture
def host(addon: McpAddonClient, settings: SimulatorSettings) -> SimulatorHost:
    orchestrator = KeywordOrchestrator(FixedClock(DEMO_NOW), settings.tz)
    return SimulatorHost(addon, orchestrator, PendingStore(), CounterIds())
