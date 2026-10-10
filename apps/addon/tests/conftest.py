"""Shared fixtures for add-on tests: pinned clock, counter IDs, fixture adapters.

The clock is pinned to Monday Oct 19 2026, 10:00 EDT, the planned video day,
so visit 2's procedure (Oct 28) and hold (from Oct 25) are still in the
future, as they will be on camera.
"""

from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from caremerge_addon.extraction.stub import StubExtractionClient
from caremerge_addon.pipeline.compiler import compile_source
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.intake import add_visit
from caremerge_addon.services import AddonServices
from caremerge_addon.settings import AddonSettings
from caremerge_addon.store.memory import InMemoryRepository, MemoryLedger
from caremerge_addon.visits.fixture_inbox import FixtureVisitInbox

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"
DEMO_NOW = datetime(2026, 10, 19, 14, 0, tzinfo=UTC)
VisitAdder = Callable[[int], list[str]]


class FixedClock:
    """A clock that returns a set time until moved."""

    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current


class CounterIds:
    """Readable, deterministic IDs: ``cc_1``, ``cc_2``, ``iss_1``, ..."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()

    def new(self, prefix: str) -> str:
        self._counts[prefix] += 1
        return f"{prefix}_{self._counts[prefix]}"


@pytest.fixture
def settings() -> AddonSettings:
    return AddonSettings(
        _env_file=None,
        visits_dir=FIXTURES / "visits",
        stub_extractions_dir=FIXTURES / "extractions",
    )


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(DEMO_NOW)


@pytest.fixture
def inbox() -> FixtureVisitInbox:
    return FixtureVisitInbox.from_dir(FIXTURES / "visits")


@pytest.fixture
def ctx(settings: AddonSettings, inbox: FixtureVisitInbox, clock: FixedClock) -> PipelineContext:
    return PipelineContext(
        settings=settings,
        repo=InMemoryRepository(),
        inbox=inbox,
        extraction=StubExtractionClient.from_dir(FIXTURES / "extractions"),
        clock=clock,
        ids=CounterIds(),
    )


@pytest.fixture
def add_visit_n(ctx: PipelineContext) -> VisitAdder:
    """Add and compile visit ``n``; return the new commit IDs."""

    def run(n: int) -> list[str]:
        added = add_visit(f"visit-{n}", ctx)
        return list(compile_source(added.source, ctx).created)

    return run


@pytest.fixture
def services(settings: AddonSettings, inbox: FixtureVisitInbox, clock: FixedClock) -> AddonServices:
    return AddonServices(
        settings=settings,
        ledger=MemoryLedger(),
        inbox=inbox,
        extraction=StubExtractionClient.from_dir(FIXTURES / "extractions"),
        clock=clock,
        ids=CounterIds(),
    )
