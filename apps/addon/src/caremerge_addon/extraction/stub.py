"""A deterministic stand-in for the extraction service, used until M2.

Each ``*.json`` file in the fixture directory is a ``CompileOutput`` written
for one synthetic visit. ``compile`` returns the candidates whose evidence cites
only utterances present in the request, then matches subjects to known
entities by exact (case-insensitive) display name, the way a careful
extractor would.
"""

from pathlib import Path

from caremerge_core.contracts import CandidateCommit, CompileInput, CompileOutput, EntityRef
from caremerge_core.enums import EntityMatch


class StubExtractionClient:
    """Serves canned candidates instead of calling a model."""

    def __init__(self, outputs: list[CompileOutput]) -> None:
        self._candidates = [candidate for output in outputs for candidate in output.candidates]

    @classmethod
    def from_dir(cls, directory: Path) -> "StubExtractionClient":
        """Load every ``*.json`` canned output in ``directory``."""
        if not directory.is_dir():
            msg = f"fixture directory not found: {directory}"
            raise FileNotFoundError(msg)
        outputs = [
            CompileOutput.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(directory.glob("*.json"))
        ]
        return cls(outputs)

    def compile(self, request: CompileInput) -> CompileOutput:
        """Return canned candidates that cite this source's utterances."""
        utterance_ids = {utterance.id for utterance in request.source.utterances}
        known = {
            entity.display_name.casefold(): entity.entity_id for entity in request.known_entities
        }
        matching = [
            _match_entity(candidate, known)
            for candidate in self._candidates
            if {evidence.utterance_id for evidence in candidate.evidence} <= utterance_ids
        ]
        return CompileOutput(candidates=tuple(matching))


def _match_entity(candidate: CandidateCommit, known: dict[str, str]) -> CandidateCommit:
    entity_id = known.get(candidate.subject_text.casefold())
    if entity_id is None:
        return candidate
    return candidate.model_copy(
        update={"entity": EntityRef(match=EntityMatch.MATCHED, entity_id=entity_id)}
    )
