"""Typed settings for the CareMerge add-on (spec §14).

Values come from ``CAREMERGE_``-prefixed environment variables or a ``.env``
file in the working directory. No other add-on module hard-codes them.
"""

from datetime import time
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AddonSettings(BaseSettings):
    """Configuration for the add-on."""

    model_config = SettingsConfigDict(env_prefix="CAREMERGE_", env_file=".env", extra="ignore")

    timezone: str = "America/New_York"
    plan_horizon_days: int = Field(default=60, gt=0)
    default_reminder_time: time = time(10, 0)
    min_quote_words: int = Field(default=3, gt=0)
    visits_dir: Path = Path("fixtures/visits")
    extraction: Literal["stub"] = "stub"
    stub_extractions_dir: Path = Path("fixtures/extractions")
    store: Literal["memory"] = "memory"
    addon_host: str = "127.0.0.1"
    addon_port: int = Field(default=8000, gt=0, lt=65536)
    local_user_id: str = Field(default="demo", min_length=1)

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
