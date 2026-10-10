"""The visit inbox port: where visit transcripts come from.

Adapter: ``FixtureVisitInbox`` (synthetic visits in ``fixtures/visits``). A
production adapter would read a visit recorder or patient portal.
"""

from typing import Protocol

from caremerge_addon.visits.models import Visit


class VisitInbox(Protocol):
    """List visits and fetch one by ID."""

    def list_visits(self) -> list[Visit]:
        """Return every visit in capture order."""
        ...

    def get_visit(self, visit_id: str) -> Visit:
        """Return one visit or raise ``RecordNotFoundError``."""
        ...
