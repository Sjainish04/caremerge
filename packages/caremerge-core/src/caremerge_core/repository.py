"""The persistence port for the Care Graph ledger (spec §10).

Reads return the whole user partition as one snapshot; engines fold it in
memory. Writes are single-record and idempotent by ID. Adapters (in-memory,
DynamoDB) live in the bridge, so the core stays free of I/O.
"""

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from caremerge_core.models import (
    Action,
    CareCommit,
    Entity,
    Issue,
    ReviewEvent,
    SourceEvent,
)


class GraphSnapshot(BaseModel):
    """Every record in the user's partition at one moment."""

    model_config = ConfigDict(frozen=True)

    sources: tuple[SourceEvent, ...] = ()
    entities: tuple[Entity, ...] = ()
    commits: tuple[CareCommit, ...] = ()
    reviews: tuple[ReviewEvent, ...] = ()
    issues: tuple[Issue, ...] = ()
    actions: tuple[Action, ...] = ()

    def entity_names(self) -> dict[str, str]:
        """Map entity IDs to display names."""
        return {entity.entity_id: entity.display_name for entity in self.entities}


class CareGraphRepository(Protocol):
    """Storage for one user's Care Graph."""

    def snapshot(self) -> GraphSnapshot:
        """Return every record in the partition."""
        ...

    def add_source(self, source: SourceEvent) -> SourceEvent:
        """Store a source unless its kind and external ID exist; return the stored one."""
        ...

    def put_entity(self, entity: Entity) -> None:
        """Insert or replace an entity."""
        ...

    def put_commit(self, commit: CareCommit) -> None:
        """Insert or replace a commit."""
        ...

    def append_review(self, event: ReviewEvent) -> None:
        """Append a review event to the audit trail."""
        ...

    def put_issue(self, issue: Issue) -> None:
        """Insert or replace an issue."""
        ...

    def put_action(self, action: Action) -> None:
        """Insert or replace an action."""
        ...

    def delete_all(self) -> None:
        """Delete every record in the partition."""
        ...
