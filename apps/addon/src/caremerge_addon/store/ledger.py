"""The ledger port: one Care Graph repository per user (spec §10).

The add-on serves whoever's token arrives, so every request resolves its
user's repository. Adapters: ``MemoryLedger`` (local development) and the
DynamoDB ledger (M2), whose partition key is ``USER#{user_id}``.
"""

from typing import Protocol

from caremerge_core.repository import CareGraphRepository


class Ledger(Protocol):
    """Hands out the repository for one user's partition."""

    def for_user(self, user_id: str) -> CareGraphRepository:
        """Return the repository for ``user_id``."""
        ...
