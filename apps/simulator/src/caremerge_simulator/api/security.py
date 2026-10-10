"""Request guards for the local API (spec §11).

The simulator host binds to the loopback interface. On top of that:

- the Host header must name the loopback interface, which blocks DNS rebinding;
- a browser ``Origin``, when present, must be the app itself or a configured
  development origin, which blocks cross-site requests from other pages;
- every ``/api`` route except ``/api/session`` needs the per-launch token in
  the ``X-CareMerge-Token`` header.
"""

import secrets
from collections.abc import Callable

from fastapi import HTTPException, Request, status

from caremerge_simulator.settings import SimulatorSettings

LOOPBACK_HOST = "127.0.0.1"
LOOPBACK_NAMES = (LOOPBACK_HOST, "localhost")
# A header name, not a credential; the token value is generated per launch.
TOKEN_HEADER = "X-CareMerge-Token"  # noqa: S105


def allowed_origins(settings: SimulatorSettings) -> frozenset[str]:
    """Return the browser origins allowed to call the API."""
    port = settings.simulator_port
    own = {f"http://{name}:{port}" for name in LOOPBACK_NAMES}
    return frozenset(own | set(settings.dev_origins))


def origin_guard(origins: frozenset[str]) -> Callable[[Request], None]:
    """Build a dependency that rejects requests from foreign browser origins."""

    def check(request: Request) -> None:
        origin = request.headers.get("origin")
        if origin is not None and origin not in origins:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="origin not allowed")

    return check


def token_guard(token: str) -> Callable[[Request], None]:
    """Build a dependency that requires the per-launch session token."""

    def check(request: Request) -> None:
        presented = request.headers.get(TOKEN_HEADER, "")
        if not secrets.compare_digest(presented, token):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="missing or invalid token")

    return check
