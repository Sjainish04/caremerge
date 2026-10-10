"""Tests for add-on settings and the injected runtime sources."""

import re
from datetime import UTC
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from caremerge_addon.runtime import SystemClock, UuidIds
from caremerge_addon.settings import AddonSettings

ENV_EXAMPLE = Path(__file__).resolve().parents[3] / ".env.example"


def test_defaults_match_the_spec() -> None:
    settings = AddonSettings(_env_file=None)
    assert settings.tz == ZoneInfo("America/New_York")
    assert (settings.plan_horizon_days, settings.min_quote_words, settings.addon_port) == (
        60,
        3,
        8000,
    )
    assert (settings.extraction, settings.store, settings.local_user_id) == (
        "stub",
        "memory",
        "demo",
    )


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CAREMERGE_PLAN_HORIZON_DAYS", "30")
    monkeypatch.setenv("CAREMERGE_ADDON_HOST", "localhost")
    settings = AddonSettings(_env_file=None)
    assert (settings.plan_horizon_days, settings.addon_host) == (30, "localhost")


@pytest.mark.parametrize(
    ("field", "value"),
    [("timezone", "Mars/Olympus"), ("plan_horizon_days", 0), ("addon_port", 70000)],
)
def test_invalid_values_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        AddonSettings(_env_file=None, **{field: value})


def test_env_example_lists_every_addon_setting() -> None:
    lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    keys = {line.split("=", 1)[0] for line in lines if line and not line.startswith("#")}
    assert {f"CAREMERGE_{name.upper()}" for name in AddonSettings.model_fields} <= keys
    AddonSettings(_env_file=ENV_EXAMPLE)


def test_runtime_sources_are_unique_and_utc() -> None:
    ids = UuidIds()
    first, second = ids.new("cc"), ids.new("cc")
    assert re.fullmatch(r"cc_[0-9a-f]{32}", first)
    assert first != second
    assert SystemClock().now().tzinfo is UTC
