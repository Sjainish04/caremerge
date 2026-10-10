"""A visit inbox backed by synthetic fixture files (spec §5.2).

Each ``*.json`` file in the directory is one ``Visit``. Nothing here reads
real recordings or real health data.
"""

from pathlib import Path

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.visits.models import Visit


class FixtureVisitInbox:
    """Serves visits loaded from fixture files."""

    def __init__(self, visits: list[Visit]) -> None:
        self._visits = {visit.visit_id: visit for visit in visits}

    @classmethod
    def from_dir(cls, directory: Path) -> "FixtureVisitInbox":
        """Load every ``*.json`` visit in ``directory``."""
        if not directory.is_dir():
            msg = f"fixture directory not found: {directory}"
            raise FileNotFoundError(msg)
        visits = [
            Visit.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(directory.glob("*.json"))
        ]
        return cls(visits)

    def list_visits(self) -> list[Visit]:
        """Return every visit, oldest first."""
        return sorted(self._visits.values(), key=lambda visit: visit.started_at)

    def get_visit(self, visit_id: str) -> Visit:
        """Return one visit or raise ``RecordNotFoundError``."""
        try:
            return self._visits[visit_id]
        except KeyError:
            raise RecordNotFoundError("visit", visit_id) from None
