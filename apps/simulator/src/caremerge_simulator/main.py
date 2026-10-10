"""Composition root: builds the simulator host and its API.

Only this module constructs adapters: the MCP client for the add-on at
``CAREMERGE_ADDON_URL``, the keyword orchestrator, and a fresh session token
per launch.
"""

import secrets

from fastapi import FastAPI

from caremerge_simulator.addon_client import McpAddonClient
from caremerge_simulator.api.routes import create_app
from caremerge_simulator.confirmations import PendingStore
from caremerge_simulator.host import SimulatorHost
from caremerge_simulator.orchestrator.keyword import KeywordOrchestrator
from caremerge_simulator.runtime import SystemClock, UuidIds
from caremerge_simulator.settings import SimulatorSettings


def build_host(settings: SimulatorSettings) -> SimulatorHost:
    """Wire the add-on client and the orchestrator into a host."""
    addon = McpAddonClient(
        settings.addon_url,
        timeout_s=settings.addon_timeout_s,
        intake_timeout_s=settings.addon_intake_timeout_s,
    )
    orchestrator = KeywordOrchestrator(SystemClock(), settings.tz)
    return SimulatorHost(addon, orchestrator, PendingStore(), UuidIds())


def build_app(settings: SimulatorSettings) -> FastAPI:
    """Build the simulator API with a fresh session token."""
    return create_app(build_host(settings), settings, token=secrets.token_urlsafe(32))
