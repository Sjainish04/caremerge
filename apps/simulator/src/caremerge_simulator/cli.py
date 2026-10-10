"""Command-line entry point: ``caremerge-sim serve``.

Configures content-free JSON logging, builds the app through the composition
root, and serves it on the loopback interface only.
"""

import argparse
from collections.abc import Sequence

import structlog
import uvicorn

from caremerge_simulator.api.security import LOOPBACK_HOST
from caremerge_simulator.main import build_app
from caremerge_simulator.settings import SimulatorSettings


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    _parser().parse_args(argv)
    settings = SimulatorSettings()
    _configure_logging()
    uvicorn.run(build_app(settings), host=LOOPBACK_HOST, port=settings.simulator_port)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="caremerge-sim", description="CareMerge Alexa+ simulator")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="serve the simulator API on the loopback interface")
    return parser


def _configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ]
    )
