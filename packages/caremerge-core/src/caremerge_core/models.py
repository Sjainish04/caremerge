"""Stored domain records: sources, entities, commits, reviews, issues, actions.

Records are immutable. A state change produces a new instance (via
``model_copy(update=...)``) that the repository persists (spec §9.2, §10).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from caremerge_core.contracts import (
    Attributes,
    Effective,
    Evidence,
    SourcePayload,
    Utterance,
)
from caremerge_core.enums import (
    ActionState,
    BeeItemType,
    CommitKind,
    DateBasis,
    EntityMatch,
    IssueKind,
    IssueStatus,
    LintCode,
    Modality,
    ReviewState,
    Role,
    SelfRating,
    SpeakerBasis,
    TemplateId,
)

ACTIVE_STATES = frozenset({ReviewState.VERIFIED, ReviewState.CORRECTED})


class RecordModel(BaseModel):
    """Base for stored records: immutable and strict about unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceEvent(RecordModel):
    """A user-selected Bee item, minimized to what extraction needs."""

    source_id: str
    bee_type: BeeItemType
    bee_id: str
    captured_at: datetime
    role: Role
    label: str
    utterances: tuple[Utterance, ...] = Field(min_length=1)
    content_hash: str

    def payload(self) -> SourcePayload:
        """Return the contract payload sent to the extraction service."""
        return SourcePayload(
            source_id=self.source_id,
            captured_at=self.captured_at,
            role=self.role,
            label=self.label,
            utterances=self.utterances,
        )


class Entity(RecordModel):
    """A medication, measurement, event, or care relationship."""

    entity_id: str
    display_name: str
    aliases: tuple[str, ...] = ()


class Signals(RecordModel):
    """Categorical review signals shown instead of confidence numbers."""

    evidence: Literal["verified"] = "verified"
    date: DateBasis
    entity: EntityMatch
    speaker: SpeakerBasis
    model: SelfRating


class SourceRef(RecordModel):
    """Where a commit came from, with its verified evidence."""

    source_id: str
    role: Role
    label: str
    captured_at: datetime
    evidence: tuple[Evidence, ...] = Field(min_length=1)


class Review(RecordModel):
    """The commit's current review state."""

    state: ReviewState = ReviewState.CANDIDATE
    at: datetime | None = None


class Edges(RecordModel):
    """Stored relationships of a commit."""

    branch: str | None = None


class CareCommit(RecordModel):
    """One source-linked instruction or event (spec §9.2)."""

    commit_id: str
    kind: CommitKind
    entity_id: str
    subject_text: str
    attributes: Attributes
    effective: Effective
    temporary: bool
    context: str | None
    modality: Modality
    source: SourceRef
    signals: Signals
    review: Review = Review()
    edges: Edges = Edges()

    @property
    def is_active(self) -> bool:
        """Return whether the commit counts toward the plan."""
        return self.review.state in ACTIVE_STATES


class ReviewEvent(RecordModel):
    """Append-only audit record of a verify, correct, or reject decision."""

    commit_id: str
    state: ReviewState
    at: datetime
    attributes: Attributes | None = None
    effective: Effective | None = None


class Issue(RecordModel):
    """A clarification item with a templated, neutral question."""

    issue_id: str
    kind: IssueKind
    code: LintCode
    entity_id: str
    commit_ids: tuple[str, ...] = Field(min_length=1)
    status: IssueStatus
    message: str
    question: str
    created_at: datetime


class Action(RecordModel):
    """A proposed Bee write and, once executed, its receipt."""

    action_id: str
    template_id: TemplateId
    params: dict[str, str]
    text: str
    alarm_at: datetime
    issue_ids: tuple[str, ...] = ()
    commit_ids: tuple[str, ...] = ()
    state: ActionState = ActionState.PROPOSED
    confirmation_id: str | None = None
    bee_todo_id: str | None = None
    created_at: datetime
    executed_at: datetime | None = None
    error_code: str | None = None
