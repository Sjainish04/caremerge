"""Agent contracts: what the bridge sends for extraction and what comes back.

These models are shared by the bridge and the AgentCore agent (spec §8.2,
§8.5). They are a shared interface: changing them needs a review from both
tracks (spec §15.3). Unknown fields are rejected, so malformed model output
fails validation instead of slipping through.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from caremerge_core.enums import (
    CommitKind,
    DateBasis,
    EntityMatch,
    FoodRelation,
    MedAction,
    Modality,
    Role,
    SelfRating,
    TimeOfDay,
    Weekday,
)


class ContractModel(BaseModel):
    """Base for contract models: immutable and strict about unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Utterance(ContractModel):
    """One transcribed utterance from a Bee item."""

    id: str = Field(min_length=1)
    start_ms: int = Field(ge=0)
    text: str
    speaker_hint: str | None = None


class SourcePayload(ContractModel):
    """The minimized source sent for extraction (spec §7.5)."""

    source_id: str
    captured_at: datetime
    role: Role
    label: str
    utterances: tuple[Utterance, ...] = Field(min_length=1)


class KnownEntity(ContractModel):
    """An entity already in the ledger, offered so the extractor can match it."""

    entity_id: str
    display_name: str
    aliases: tuple[str, ...] = ()


class EntityRef(ContractModel):
    """How an extracted subject relates to the known entities."""

    match: EntityMatch
    entity_id: str | None = None


class Attributes(ContractModel):
    """Instruction details. Unknown values stay ``None``; nothing is inferred."""

    action: MedAction | None = None
    dose_text: str | None = None
    dose_quantity: float | None = None
    time_of_day: TimeOfDay | None = None
    food_relation: FoodRelation | None = None
    days_of_week: tuple[Weekday, ...] | None = None
    scheduled_for: date | None = None
    interval_text: str | None = None


class Effective(ContractModel):
    """Valid time of an instruction. ``end`` is the last day it applies."""

    start: date | None = None
    end: date | None = None
    end_condition: str | None = None
    date_basis: DateBasis = DateBasis.NONE
    date_raw: str | None = None


class Evidence(ContractModel):
    """A verbatim quote from one cited utterance."""

    utterance_id: str
    quote: str = Field(min_length=1)


class CandidateCommit(ContractModel):
    """One extracted care item, before validation and user review."""

    kind: CommitKind
    subject_text: str = Field(min_length=1)
    entity: EntityRef
    attributes: Attributes = Attributes()
    effective: Effective = Effective()
    temporary: bool = False
    context: str | None = None
    modality: Modality
    evidence: tuple[Evidence, ...] = Field(min_length=1)
    self_rating: SelfRating


class CompileInput(ContractModel):
    """Request body of the ``compile_source`` task."""

    source: SourcePayload
    known_entities: tuple[KnownEntity, ...] = ()
    timezone: str


class CompileOutput(ContractModel):
    """Response body of the ``compile_source`` task."""

    candidates: tuple[CandidateCommit, ...] = ()
