"""Injected sources of time and identifiers for the simulator."""

from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4


class Clock(Protocol):
    """Source of the current time."""

    def now(self) -> datetime:
        """Return the current time as a timezone-aware datetime."""
        ...


class IdFactory(Protocol):
    """Source of new identifiers."""

    def new(self, prefix: str) -> str:
        """Return a new identifier such as ``conf_<hex>``."""
        ...


class SystemClock:
    """The real clock, in UTC."""

    def now(self) -> datetime:
        """Return the current UTC time."""
        return datetime.now(UTC)


class UuidIds:
    """Random identifiers built from UUID4."""

    def new(self, prefix: str) -> str:
        """Return ``<prefix>_<32 hex chars>``."""
        return f"{prefix}_{uuid4().hex}"
