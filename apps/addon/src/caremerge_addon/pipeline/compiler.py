"""Compile a source into candidate CareCommits (feature F2, spec §8.4).

The extraction client proposes candidates; this module is the trust
boundary. Each candidate must pass the provenance check before it is stored
as a ``candidate`` commit awaiting the user's review.
"""

import structlog
from pydantic import BaseModel, ConfigDict

from caremerge_addon.pipeline.context import PipelineContext
from caremerge_core.branches import branch_key
from caremerge_core.contracts import CandidateCommit, CompileInput, KnownEntity
from caremerge_core.enums import EntityMatch, SpeakerBasis
from caremerge_core.models import CareCommit, Edges, Entity, Signals, SourceEvent, SourceRef
from caremerge_core.provenance import check_provenance, normalize

log = structlog.get_logger(__name__)


class CompileReport(BaseModel):
    """What compiling one source produced."""

    model_config = ConfigDict(frozen=True)

    source_id: str
    created: tuple[str, ...]
    rejected: int


def compile_source(source: SourceEvent, ctx: PipelineContext) -> CompileReport:
    """Extract, validate, and store candidate commits for ``source``."""
    snapshot = ctx.repo.snapshot()
    entities = {entity.entity_id: entity for entity in snapshot.entities}
    request = CompileInput(
        source=source.payload(),
        known_entities=tuple(
            KnownEntity(entity_id=e.entity_id, display_name=e.display_name, aliases=e.aliases)
            for e in snapshot.entities
        ),
        timezone=ctx.settings.timezone,
    )
    output = ctx.extraction.compile(request)
    new_entities: dict[str, str] = {}
    created: list[str] = []
    rejected = 0
    for candidate in output.candidates:
        if not check_provenance(candidate, source.utterances, ctx.settings.min_quote_words).ok:
            rejected += 1
            continue
        entity_id, match = _resolve_entity(candidate, entities, new_entities, ctx)
        commit = _commit_from(candidate, source, entity_id, match, ctx)
        commit = commit.model_copy(
            update={"edges": Edges(branch=branch_key(candidate, output.candidates))}
        )
        ctx.repo.put_commit(commit)
        created.append(commit.commit_id)
    log.info("source_compiled", source_id=source.source_id, created=len(created), rejected=rejected)
    return CompileReport(source_id=source.source_id, created=tuple(created), rejected=rejected)


def _resolve_entity(
    candidate: CandidateCommit,
    entities: dict[str, Entity],
    new_entities: dict[str, str],
    ctx: PipelineContext,
) -> tuple[str, EntityMatch]:
    """Link to a known entity, or create one; possible matches never auto-merge."""
    ref = candidate.entity
    if ref.match is EntityMatch.MATCHED and ref.entity_id in entities:
        return ref.entity_id, EntityMatch.MATCHED
    match = EntityMatch.NEW if ref.match is EntityMatch.MATCHED else ref.match
    key = normalize(candidate.subject_text)
    if key not in new_entities:
        entity = Entity(entity_id=ctx.ids.new("ent"), display_name=candidate.subject_text)
        ctx.repo.put_entity(entity)
        new_entities[key] = entity.entity_id
    return new_entities[key], match


def _commit_from(
    candidate: CandidateCommit,
    source: SourceEvent,
    entity_id: str,
    match: EntityMatch,
    ctx: PipelineContext,
) -> CareCommit:
    return CareCommit(
        commit_id=ctx.ids.new("cc"),
        kind=candidate.kind,
        entity_id=entity_id,
        subject_text=candidate.subject_text,
        attributes=candidate.attributes,
        effective=candidate.effective,
        temporary=candidate.temporary,
        context=candidate.context,
        modality=candidate.modality,
        source=SourceRef(
            source_id=source.source_id,
            role=source.role,
            label=source.label,
            captured_at=source.captured_at,
            evidence=candidate.evidence,
        ),
        signals=Signals(
            date=candidate.effective.date_basis,
            entity=match,
            speaker=SpeakerBasis.SESSION_LABEL,
            model=candidate.self_rating,
        ),
    )
