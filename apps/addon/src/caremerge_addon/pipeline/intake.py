"""Add a visit from the inbox as a minimized source (feature F1, spec §7.5).

Only the visit's utterances are kept, once per utterance ID, with its role,
clinician label, and capture time. The inbox title never enters a
``SourceEvent``. Adding a visit again returns the stored source unchanged.
"""

import hashlib
import json
from collections.abc import Sequence

import structlog
from pydantic import BaseModel, ConfigDict

from caremerge_addon.pipeline.context import PipelineContext
from caremerge_core.contracts import Utterance
from caremerge_core.enums import SourceKind
from caremerge_core.models import SourceEvent

log = structlog.get_logger(__name__)


class AddedVisit(BaseModel):
    """A stored source and whether this call created it."""

    model_config = ConfigDict(frozen=True)

    source: SourceEvent
    is_new: bool


def content_hash(utterances: Sequence[Utterance]) -> str:
    """Return a stable SHA-256 over the utterances' canonical JSON."""
    canonical = json.dumps(
        [utterance.model_dump(mode="json") for utterance in utterances],
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def add_visit(visit_id: str, ctx: PipelineContext) -> AddedVisit:
    """Store a minimized source for one inbox visit."""
    visit = ctx.inbox.get_visit(visit_id)
    utterances = _unique(visit.utterances)
    fresh = SourceEvent(
        source_id=ctx.ids.new("src"),
        kind=SourceKind.VISIT,
        external_id=visit.visit_id,
        captured_at=visit.started_at,
        role=visit.role,
        label=visit.clinician,
        utterances=utterances,
        content_hash=content_hash(utterances),
    )
    stored = ctx.repo.add_source(fresh)
    is_new = stored.source_id == fresh.source_id
    log.info(
        "visit_added",
        source_id=stored.source_id,
        is_new=is_new,
        utterances=len(utterances),
    )
    return AddedVisit(source=stored, is_new=is_new)


def _unique(utterances: Sequence[Utterance]) -> tuple[Utterance, ...]:
    """Keep the first utterance for each ID, in order (spec §16.1)."""
    first: dict[str, Utterance] = {}
    for utterance in utterances:
        first.setdefault(utterance.id, utterance)
    return tuple(first.values())
