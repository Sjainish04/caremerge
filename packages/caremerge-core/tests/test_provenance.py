"""Tests for the deterministic evidence check (spec §8.4)."""

import pytest

from caremerge_core.contracts import CandidateCommit, EntityRef, Evidence, Utterance
from caremerge_core.enums import CommitKind, EntityMatch, Modality, SelfRating
from caremerge_core.provenance import ProvenanceFailure, check_provenance, normalize

UTTERANCES = (
    Utterance(id="u_1", start_ms=0, text="Your procedure is on Wednesday, October 28."),
    Utterance(
        id="u_2", start_ms=4200, text="Please hold Medication A starting Sunday, October 25."
    ),
)
MIN_WORDS = 3


def _with_quote(utterance_id: str, quote: str) -> CandidateCommit:
    return CandidateCommit(
        kind=CommitKind.MEDICATION_INSTRUCTION,
        subject_text="Medication A",
        entity=EntityRef(match=EntityMatch.NEW),
        modality=Modality.INSTRUCTION,
        evidence=(Evidence(utterance_id=utterance_id, quote=quote),),
        self_rating=SelfRating.HIGH,
    )


def test_normalize_ignores_case_punctuation_and_spacing() -> None:
    assert (
        normalize("  Hold   Medication-A, starting SUNDAY! ") == "hold medication a starting sunday"
    )


@pytest.mark.parametrize(
    "quote",
    [
        "hold Medication A starting Sunday, October 25",
        "HOLD medication a starting sunday october 25",
        "Please hold Medication A",
    ],
)
def test_faithful_quotes_pass(quote: str) -> None:
    assert check_provenance(_with_quote("u_2", quote), UTTERANCES, MIN_WORDS).ok


@pytest.mark.parametrize(
    ("utterance_id", "quote", "failure"),
    [
        ("u_9", "hold Medication A starting", ProvenanceFailure.UNKNOWN_UTTERANCE),
        ("u_2", "hold it", ProvenanceFailure.QUOTE_TOO_SHORT),
        ("u_2", "hold Medication A until Monday", ProvenanceFailure.QUOTE_NOT_IN_SOURCE),
        ("u_1", "hold Medication A starting", ProvenanceFailure.QUOTE_NOT_IN_SOURCE),
        ("u_2", "old Medication A starting", ProvenanceFailure.QUOTE_NOT_IN_SOURCE),
    ],
)
def test_unfaithful_quotes_fail(utterance_id: str, quote: str, failure: ProvenanceFailure) -> None:
    result = check_provenance(_with_quote(utterance_id, quote), UTTERANCES, MIN_WORDS)
    assert result.failures == (failure,)


def test_contractions_match_after_normalization() -> None:
    utterances = (
        Utterance(
            id="u_3",
            start_ms=0,
            text="Take Medication A with food. It's best taken in the evening.",
        ),
    )
    assert check_provenance(
        _with_quote("u_3", "it's best taken in the evening"), utterances, MIN_WORDS
    ).ok


def test_a_quote_spanning_two_utterances_fails() -> None:
    result = check_provenance(
        _with_quote("u_1", "October 28. Please hold Medication A"), UTTERANCES, MIN_WORDS
    )
    assert result.failures == (ProvenanceFailure.QUOTE_NOT_IN_SOURCE,)
