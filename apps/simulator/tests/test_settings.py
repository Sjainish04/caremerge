"""Tests for simulator settings."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from caremerge_simulator.settings import SimulatorSettings

ENV_EXAMPLE = Path(__file__).resolve().parents[3] / ".env.example"


def test_defaults_match_the_spec() -> None:
    settings = SimulatorSettings(_env_file=None)
    assert (settings.simulator_port, settings.addon_url, settings.orchestrator) == (
        8765,
        "http://127.0.0.1:8000/mcp",
        "keyword",
    )
    assert settings.addon_intake_timeout_s > settings.addon_timeout_s


def test_env_example_lists_every_simulator_setting() -> None:
    lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    keys = {line.split("=", 1)[0] for line in lines if line and not line.startswith("#")}
    assert {f"CAREMERGE_{name.upper()}" for name in SimulatorSettings.model_fields} <= keys
    assert SimulatorSettings(_env_file=ENV_EXAMPLE).dev_origins == ("http://localhost:5173",)


@pytest.mark.parametrize(
    ("field", "value"),
    [("simulator_port", 70000), ("addon_timeout_s", 0), ("timezone", "Mars/Olympus")],
)
def test_invalid_values_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        SimulatorSettings(_env_file=None, **{field: value})
