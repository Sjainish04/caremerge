"""The web app's card fixtures are real turns: replaying the demo reproduces them.

``apps/web`` tests its cards against JSON recorded from the simulator. This
test replays the same conversation on the pinned video-day clock and compares,
so a change to the simulator API or to a spoken template can't leave the web
tests on stale shapes. After an intended change, record the files again with
``uv run pytest apps/simulator/tests/test_web_fixtures.py --record-web-fixtures``.
"""

import asyncio
import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from caremerge_simulator.host import SimulatorHost

WEB_FIXTURES = Path(__file__).resolve().parents[3] / "apps" / "web" / "src" / "test" / "fixtures"


async def _replay(host: SimulatorHost) -> dict[str, BaseModel]:
    await host.add_visit("visit-1")
    await host.turn("What's new from my visit with Dr. Rivera?")
    await host.turn("Yes")
    recorded: dict[str, BaseModel] = {"visit_added": await host.add_visit("visit-2")}
    recorded["visit_updates"] = await host.turn("What's new from my visit with Dr. Lee?")
    recorded["items_added"] = await host.turn("Yes")
    recorded["whats_changed"] = await host.turn("What changed in my care plan?")
    recorded["plan_for_day"] = await host.turn("Should I take Medication A on Sunday, October 25?")
    recorded["open_questions"] = await host.turn("Any open questions?")
    recorded["reminder_proposal"] = await host.turn("Remind me to ask when the hold ends.")
    recorded["reminder_stored"] = await host.turn("Yes")
    recorded["fallback"] = await host.turn("Play some music")
    recorded["inbox"] = await host.inbox()
    recorded["reminders"] = await host.reminders()
    return recorded


def _as_fixture(model: BaseModel) -> str:
    return json.dumps(model.model_dump(mode="json"), indent=2) + "\n"


def test_web_fixtures_are_recorded_turns(
    host: SimulatorHost, request: pytest.FixtureRequest
) -> None:
    recorded = asyncio.run(_replay(host))
    if request.config.getoption("--record-web-fixtures"):
        for name, model in recorded.items():
            (WEB_FIXTURES / f"{name}.json").write_text(_as_fixture(model))
    for name, model in recorded.items():
        path = WEB_FIXTURES / f"{name}.json"
        assert path.read_text() == _as_fixture(model), f"{path.name} is stale; see the docstring"
    assert {path.stem for path in WEB_FIXTURES.glob("*.json")} == set(recorded)
