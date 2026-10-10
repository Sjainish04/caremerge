"""Tests for the add-on's entry point and the no-content-in-logs invariant (spec §16.2)."""

from collections.abc import Callable
from typing import Any

import pytest
import structlog
from structlog.testing import capture_logs

from caremerge_addon import cli
from caremerge_addon.main import build_app
from caremerge_addon.mcp import tools
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.settings import AddonSettings

VisitAdder = Callable[[int], list[str]]


def test_serve_runs_uvicorn_on_the_configured_host_and_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def fake_run(app: object, **kwargs: Any) -> None:
        calls.append({"app": app, **kwargs})

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)
    monkeypatch.setenv("CAREMERGE_ADDON_PORT", "9123")
    try:
        assert cli.main(["serve"]) == 0
    finally:
        structlog.reset_defaults()
    (call,) = calls
    assert (call["host"], call["port"]) == ("127.0.0.1", 9123)


def test_the_app_serves_mcp_at_the_spec_path(settings: AddonSettings) -> None:
    app = build_app(settings)
    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/mcp" in paths


def test_pipeline_logs_never_contain_transcript_text(ctx: PipelineContext) -> None:
    with capture_logs() as logs:
        for visit_id in ("visit-1", "visit-2"):
            tools.add_visit(ctx, visit_id)
            updates = tools.visit_updates(ctx, None)
            tools.confirm_items(ctx, [item.commit_id for item in updates.items], "c-1")
        proposal = tools.propose_reminder(ctx, None, None, None)
        assert proposal.reminder is not None
        tools.confirm_reminder(ctx, proposal.reminder.action_id, "c-2")
    assert logs
    rendered = repr(logs).casefold()
    for source in ctx.repo.snapshot().sources:
        for utterance in source.utterances:
            assert utterance.text.casefold() not in rendered
    for word in ("medication a", "dr. lee", "procedure", "ask your care team"):
        assert word not in rendered
