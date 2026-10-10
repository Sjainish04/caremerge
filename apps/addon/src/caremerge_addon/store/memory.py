"""In-memory Care Graph repositories for local development and tests.

``InMemoryRepository`` implements ``caremerge_core.repository.CareGraphRepository``
with plain dictionaries, and ``MemoryLedger`` keeps one per user. Data lives
only as long as the process; the DynamoDB ledger replaces it in M2.
"""

from caremerge_core.models import Action, CareCommit, Entity, Issue, ReviewEvent, SourceEvent
from caremerge_core.repository import GraphSnapshot


class InMemoryRepository:
    """Stores one user's Care Graph in process memory."""

    def __init__(self) -> None:
        self._sources: dict[tuple[str, str], SourceEvent] = {}
        self._entities: dict[str, Entity] = {}
        self._commits: dict[str, CareCommit] = {}
        self._reviews: list[ReviewEvent] = []
        self._issues: dict[str, Issue] = {}
        self._actions: dict[str, Action] = {}

    def snapshot(self) -> GraphSnapshot:
        """Return every record; sources are ordered by capture time."""
        return GraphSnapshot(
            sources=tuple(sorted(self._sources.values(), key=lambda source: source.captured_at)),
            entities=tuple(self._entities.values()),
            commits=tuple(self._commits.values()),
            reviews=tuple(self._reviews),
            issues=tuple(self._issues.values()),
            actions=tuple(self._actions.values()),
        )

    def add_source(self, source: SourceEvent) -> SourceEvent:
        """Store a source unless its kind and external ID exist; return the stored one."""
        key = (source.kind.value, source.external_id)
        return self._sources.setdefault(key, source)

    def put_entity(self, entity: Entity) -> None:
        """Insert or replace an entity."""
        self._entities[entity.entity_id] = entity

    def put_commit(self, commit: CareCommit) -> None:
        """Insert or replace a commit."""
        self._commits[commit.commit_id] = commit

    def append_review(self, event: ReviewEvent) -> None:
        """Append a review event."""
        self._reviews.append(event)

    def put_issue(self, issue: Issue) -> None:
        """Insert or replace an issue."""
        self._issues[issue.issue_id] = issue

    def put_action(self, action: Action) -> None:
        """Insert or replace an action."""
        self._actions[action.action_id] = action

    def delete_all(self) -> None:
        """Delete every record."""
        self._sources.clear()
        self._entities.clear()
        self._commits.clear()
        self._reviews.clear()
        self._issues.clear()
        self._actions.clear()


class MemoryLedger:
    """One in-memory repository per user, created on first use."""

    def __init__(self) -> None:
        self._repositories: dict[str, InMemoryRepository] = {}

    def for_user(self, user_id: str) -> InMemoryRepository:
        """Return ``user_id``'s repository."""
        return self._repositories.setdefault(user_id, InMemoryRepository())
