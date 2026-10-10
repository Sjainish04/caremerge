"""Tests for the visit inbox, the stub extraction client, and the in-memory ledger."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.extraction.stub import StubExtractionClient
from caremerge_addon.store.memory import InMemoryRepository, MemoryLedger
from caremerge_addon.visits.fixture_inbox import FixtureVisitInbox
from caremerge_core.contracts import CompileInput, KnownEntity, SourcePayload, Utterance
from caremerge_core.enums import EntityMatch, Role, SourceKind
from caremerge_core.models import SourceEvent

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"


def test_inbox_lists_visits_in_capture_order() -> None:
    inbox = FixtureVisitInbox.from_dir(FIXTURES / "visits")
    visits = inbox.list_visits()
    assert [(v.visit_id, v.clinician, v.role) for v in visits] == [
        ("visit-1", "Dr. Rivera", Role.FAMILY_PHYSICIAN),
        ("visit-2", "Dr. Lee", Role.SPECIALIST),
        ("visit-3", "Pharmacist", Role.PHARMACIST),
    ]
    assert inbox.get_visit("visit-2").started_at == datetime(2026, 10, 7, 18, 22, tzinfo=UTC)


def test_inbox_rejects_unknown_visits_and_missing_directories(tmp_path: Path) -> None:
    inbox = FixtureVisitInbox.from_dir(FIXTURES / "visits")
    with pytest.raises(RecordNotFoundError):
        inbox.get_visit("visit-9")
    with pytest.raises(FileNotFoundError):
        FixtureVisitInbox.from_dir(tmp_path / "absent")


def test_visit_times_must_carry_a_timezone(tmp_path: Path) -> None:
    visit = {
        "visit_id": "naive-1",
        "title": "No time zone",
        "clinician": "Dr. Rivera",
        "role": "family_physician",
        "started_at": "2026-10-05T14:10:00",
        "utterances": [{"id": "n-u1", "start_ms": 0, "text": "Keep taking Medication A."}],
    }
    (tmp_path / "naive.json").write_text(json.dumps(visit), encoding="utf-8")
    with pytest.raises(ValidationError):
        FixtureVisitInbox.from_dir(tmp_path)


def _request(utterance_ids: list[str], known: tuple[KnownEntity, ...] = ()) -> CompileInput:
    return CompileInput(
        source=SourcePayload(
            source_id="src_1",
            captured_at=datetime(2026, 10, 7, 18, 22, tzinfo=UTC),
            role=Role.SPECIALIST,
            label="Dr. Lee",
            utterances=tuple(Utterance(id=i, start_ms=0, text="x") for i in utterance_ids),
        ),
        known_entities=known,
        timezone="America/New_York",
    )


def test_stub_returns_only_candidates_citing_the_request() -> None:
    stub = StubExtractionClient.from_dir(FIXTURES / "extractions")
    output = stub.compile(_request(["v2-u1", "v2-u2"]))
    assert [c.subject_text for c in output.candidates] == ["procedure", "Medication A"]
    assert stub.compile(_request(["other-u1"])).candidates == ()


def test_stub_matches_known_entities_by_name() -> None:
    stub = StubExtractionClient.from_dir(FIXTURES / "extractions")
    known = (KnownEntity(entity_id="ent_7", display_name="medication a"),)
    hold = stub.compile(_request(["v2-u1", "v2-u2"], known)).candidates[1]
    assert (hold.entity.match, hold.entity.entity_id) == (EntityMatch.MATCHED, "ent_7")


def test_stub_fails_fast_on_a_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        StubExtractionClient.from_dir(tmp_path / "absent")


def _source(source_id: str, external_id: str) -> SourceEvent:
    return SourceEvent(
        source_id=source_id,
        kind=SourceKind.VISIT,
        external_id=external_id,
        captured_at=datetime(2026, 10, 5, 14, 10, tzinfo=UTC),
        role=Role.FAMILY_PHYSICIAN,
        label="Dr. Rivera",
        utterances=(Utterance(id="v1-u1", start_ms=0, text="Keep taking it."),),
        content_hash="sha256:x",
    )


def test_store_keeps_the_first_source_for_a_visit() -> None:
    repo = InMemoryRepository()
    first = repo.add_source(_source("src_1", "visit-1"))
    again = repo.add_source(_source("src_2", "visit-1"))
    assert again == first
    assert [s.source_id for s in repo.snapshot().sources] == ["src_1"]
    repo.delete_all()
    assert repo.snapshot().sources == ()


def test_ledger_keeps_each_user_separate() -> None:
    ledger = MemoryLedger()
    ledger.for_user("alex").add_source(_source("src_1", "visit-1"))
    assert ledger.for_user("alex") is ledger.for_user("alex")
    assert ledger.for_user("sam").snapshot().sources == ()
