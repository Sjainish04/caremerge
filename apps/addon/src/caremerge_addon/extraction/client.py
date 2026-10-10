"""The extraction port: the add-on's view of the ``compile_source`` task (spec §8).

Adapters: ``StubExtractionClient`` (canned outputs, M1) and the Bedrock
client (M2). Callers always re-validate the output; this port is not a trust
boundary.
"""

from typing import Protocol

from caremerge_core.contracts import CompileInput, CompileOutput


class ExtractionClient(Protocol):
    """Turn a minimized source into candidate commits."""

    def compile(self, request: CompileInput) -> CompileOutput:
        """Return candidates for ``request.source``."""
        ...
