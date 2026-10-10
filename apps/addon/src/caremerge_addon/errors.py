"""Errors raised by the add-on when a referenced record is missing."""


class AddonError(Exception):
    """Base class for add-on errors."""


class RecordNotFoundError(AddonError):
    """Raised when a visit, source, commit, issue, or action ID is unknown."""

    def __init__(self, kind: str, record_id: str) -> None:
        self.kind = kind
        self.record_id = record_id
        super().__init__(f"{kind} not found: {record_id}")
