"""Command-line entry point: ``caremerge-addon serve``.

Configures content-free JSON logging, builds the app through the composition
root, and serves the MCP endpoint at ``/mcp`` on the configured host and port.
"""

import argparse
from collections.abc import Sequence

import structlog
import uvicorn

from caremerge_addon.main import build_app
from caremerge_addon.settings import AddonSettings


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    _parser().parse_args(argv)
    settings = AddonSettings()
    _configure_logging()
    uvicorn.run(build_app(settings), host=settings.addon_host, port=settings.addon_port)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="caremerge-addon", description="CareMerge MCP add-on")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="serve the MCP endpoint")
    return parser


def _configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ]
    )
