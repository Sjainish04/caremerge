"""Typed settings for the simulated Alexa+ host (spec §14).

Values come from ``CAREMERGE_``-prefixed environment variables or a ``.env``
file in the working directory. No other simulator module hard-codes them.
"""

from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SimulatorSettings(BaseSettings):
    """Configuration for the simulator host."""

    model_config = SettingsConfigDict(env_prefix="CAREMERGE_", env_file=".env", extra="ignore")

    timezone: str = "America/New_York"
    simulator_port: int = Field(default=8765, gt=0, lt=65536)
    dev_origins: tuple[str, ...] = ()
    addon_url: str = "http://127.0.0.1:8000/mcp"
    addon_timeout_s: float = Field(default=10, gt=0)
    addon_intake_timeout_s: float = Field(default=90, gt=0)
    orchestrator: Literal["keyword"] = "keyword"

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            msg = f"unknown timezone: {value}"
            raise ValueError(msg) from error
        return value

    @property
    def tz(self) -> ZoneInfo:
        """Return the configured timezone."""
        return ZoneInfo(self.timezone)
