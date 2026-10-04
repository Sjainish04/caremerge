"""Tests for contracts and stored models: validation and wire format."""

from collections.abc import Callable
from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from caremerge_core.contracts import (
    Attributes,
    CandidateCommit,
    Effective,
    EntityRef,
    Evidence,
    Utterance,
)
from caremerge_core.enums import (
    BeeItemType,
    CommitKind,
    EntityMatch,
    MedAction,
    Modality,
    ReviewState,
    Role,
    SelfRating,
)
from caremerge_core.models import CareCommit, SourceEvent


def _candidate(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "kind": "medication_instruction",
        "subject_text": "Medication A",
        "entity": {"match": "new"},
        "attributes": {"action": "hold"},
        "effective": {"start": "2026-10-25", "date_basis": "explicit"},
        "temporary": True,
        "context": "procedure",
        "modality": "instruction",
        "evidence": [{"utterance_id": "u_2", "quote": "hold Medication A starting Sunday"}],
        "self_rating": "high",
    }
    data.update(overrides)
    return data


def test_candidate_parses_wire_format() -> None:
    candidate = CandidateCommit.model_validate(_candidate())
    assert candidate.attributes.action is MedAction.HOLD
    assert candidate.effective.start == date(2026, 10, 25)
    assert candidate.entity == EntityRef(match=EntityMatch.NEW)


def test_candidate_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        CandidateCommit.model_validate(_candidate(evidence=[]))


def test_candidate_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CandidateCommit.model_validate(_candidate(confidence=0.97))


def test_candidate_rejects_unknown_enum_values() -> None:
    with pytest.raises(ValidationError):
        CandidateCommit.model_validate(_candidate(attributes={"action": "double"}))


def test_enums_serialize_as_plain_values() -> None:
    candidate = CandidateCommit(
        kind=CommitKind.MEDICATION_INSTRUCTION,
        subject_text="Medication A",
        entity=EntityRef(match=EntityMatch.NEW),
        attributes=Attributes(action=MedAction.CONTINUE),
        effective=Effective(),
        modality=Modality.INSTRUCTION,
        evidence=(Evidence(utterance_id="u_1", quote="keep taking Medication A"),),
        self_rating=SelfRating.HIGH,
    )
    dumped = candidate.model_dump(mode="json")
    assert dumped["kind"] == "medication_instruction"
    assert dumped["attributes"]["action"] == "continue"
    assert dumped["effective"]["date_basis"] == "none"


@pytest.mark.parametrize(
    ("state", "active"),
    [
        (ReviewState.CANDIDATE, False),
        (ReviewState.VERIFIED, True),
        (ReviewState.CORRECTED, True),
        (ReviewState.REJECTED, False),
    ],
)
def test_only_verified_or_corrected_commits_are_active(
    commit: Callable[..., CareCommit], state: ReviewState, active: bool
) -> None:
    assert commit(state=state).is_active is active


def test_source_payload_carries_only_minimized_fields() -> None:
    source = SourceEvent(
        source_id="src_1",
        bee_type=BeeItemType.CONVERSATION,
        bee_id="6531525",
        captured_at=datetime(2026, 10, 5, 14, 10, tzinfo=UTC),
        role=Role.FAMILY_PHYSICIAN,
        label="Dr. Rivera",
        utterances=(Utterance(id="u_1", start_ms=0, text="Keep taking Medication A."),),
        content_hash="sha256:abc",
    )
    payload = source.payload().model_dump()
    assert set(payload) == {"source_id", "captured_at", "role", "label", "utterances"}
