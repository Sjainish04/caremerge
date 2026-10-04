"""Deterministic provenance checks for extracted candidates (spec §8.4).

A candidate survives only if every evidence quote appears, word for word,
in the utterance it cites. Matching ignores case and punctuation, so a
dropped comma doesn't reject a faithful quote. The words and their order
must still match exactly.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from caremerge_core.contracts import CandidateCommit, Utterance

_NON_WORD = re.compile(r"\W+")


def normalize(text: str) -> str:
    """Casefold, turn punctuation into spaces, and collapse whitespace."""
    return " ".join(_NON_WORD.sub(" ", text.casefold()).split())


class ProvenanceFailure(StrEnum):
    """Why an evidence quote was rejected."""

    UNKNOWN_UTTERANCE = "unknown_utterance"
    QUOTE_TOO_SHORT = "quote_too_short"
    QUOTE_NOT_IN_SOURCE = "quote_not_in_source"


@dataclass(frozen=True)
class ProvenanceResult:
    """Outcome of checking one candidate's evidence."""

    failures: tuple[ProvenanceFailure, ...]

    @property
    def ok(self) -> bool:
        """Return whether every quote passed."""
        return not self.failures


def check_provenance(
    candidate: CandidateCommit,
    utterances: Sequence[Utterance],
    min_quote_words: int,
) -> ProvenanceResult:
    """Check that each evidence quote is a whole-word substring of its utterance."""
    by_id = {utterance.id: utterance for utterance in utterances}
    failures: list[ProvenanceFailure] = []
    for evidence in candidate.evidence:
        cited = by_id.get(evidence.utterance_id)
        if cited is None:
            failures.append(ProvenanceFailure.UNKNOWN_UTTERANCE)
            continue
        quote = normalize(evidence.quote)
        if len(quote.split()) < min_quote_words:
            failures.append(ProvenanceFailure.QUOTE_TOO_SHORT)
            continue
        if f" {quote} " not in f" {normalize(cited.text)} ":
            failures.append(ProvenanceFailure.QUOTE_NOT_IN_SOURCE)
    return ProvenanceResult(tuple(failures))
