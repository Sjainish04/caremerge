"""Tests for the simulator's entry point and its content-free logs (spec §16.2)."""

import asyncio
import json
from typing import Any

import pytest
import structlog
from structlog.testing import capture_logs

from caremerge_simulator import cli
from caremerge_simulator.host import SimulatorHost


def test_serve_runs_uvicorn_on_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_run(app: object, **kwargs: Any) -> None:
        calls.append({"app": app, **kwargs})

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setenv("CAREMERGE_SIMULATOR_PORT", "9124")
    try:
        assert cli.main(["serve"]) == 0
    finally:
        structlog.reset_defaults()
    (call,) = calls
    assert (call["host"], call["port"]) == ("127.0.0.1", 9124)


def test_turn_logs_never_contain_what_was_said(host: SimulatorHost) -> None:
    said = [
        "What's new from my visit with Dr. Lee?",
        "Yes",
        "Should I take Medication A on Sunday?",
        "Remind me to ask when the hold ends.",
        "Play some music",
    ]

    async def body() -> None:
        await host.add_visit("visit-2")
        for text in said:
            await host.turn(text)

    with capture_logs() as logs:
        asyncio.run(body())
    assert logs
    rendered = repr(logs).casefold()
    for word in ("medication a", "dr. lee", "sunday", "music", "hold"):
        assert word not in rendered


def test_openapi_prints_the_api_document(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["openapi"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert {"/api/turn", "/api/inbox", "/api/reminders"} <= set(document["paths"])
