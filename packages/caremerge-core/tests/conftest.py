"""Shared builders for caremerge-core tests.

``make_commit`` builds a verified medication commit by default; tests
override only the fields they care about. Times are fixture dates from
spec §5.2 (scene 1 is captured on Oct 5).
"""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest

from caremerge_core.contracts import Attributes, Effective, Evidence
from caremerge_core.enums import (
    CommitKind,
    DateBasis,
    EntityMatch,
    Modality,
    ReviewState,
    Role,
    SelfRating,
    SpeakerBasis,
)
from caremerge_core.models import CareCommit, Review, Signals, SourceRef

SCENE_1_AT = datetime(2026, 10, 5, 14, 10, tzinfo=UTC)


def make_commit(
    commit_id: str = "cc_1",
    *,
    kind: CommitKind = CommitKind.MEDICATION_INSTRUCTION,
    entity_id: str = "ent_med_a",
    subject_text: str = "Medication A",
    attributes: Attributes | None = None,
    effective: Effective | None = None,
    temporary: bool = False,
    context: str | None = None,
    captured_at: datetime = SCENE_1_AT,
    state: ReviewState = ReviewState.VERIFIED,
    source_id: str = "src_1",
    **overrides: Any,
) -> CareCommit:
    """Build a commit with sensible defaults for tests."""
    commit = CareCommit(
        commit_id=commit_id,
        kind=kind,
        entity_id=entity_id,
        subject_text=subject_text,
        attributes=attributes or Attributes(),
        effective=effective or Effective(),
        temporary=temporary,
        context=context,
        modality=Modality.INSTRUCTION,
        source=SourceRef(
            source_id=source_id,
            role=Role.FAMILY_PHYSICIAN,
            label="Dr. Rivera",
            captured_at=captured_at,
            evidence=(Evidence(utterance_id="u_1", quote="keep taking Medication A"),),
        ),
        signals=Signals(
            date=DateBasis.NONE,
            entity=EntityMatch.MATCHED,
            speaker=SpeakerBasis.SESSION_LABEL,
            model=SelfRating.HIGH,
        ),
        review=Review(state=state, at=captured_at),
    )
    return commit.model_copy(update=overrides) if overrides else commit


@pytest.fixture
def commit() -> Callable[..., CareCommit]:
    """Return the ``make_commit`` builder."""
    return make_commit
