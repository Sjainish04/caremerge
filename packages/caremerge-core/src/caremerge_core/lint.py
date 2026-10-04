"""CareLint: deterministic structural gaps in the plan (spec §9.8).

Findings carry template IDs and parameters, never free text. The bridge
turns them into issues with rendered, neutral questions.
"""

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field

from caremerge_core.enums import LintCode, TemplateId
from caremerge_core.models import CareCommit
from caremerge_core.questions import action_noun


@dataclass(frozen=True)
class LintFinding:
    """One structural gap, ready to render as an issue."""

    code: LintCode
    entity_id: str
    commit_ids: tuple[str, ...]
    message_template: TemplateId
    question_template: TemplateId
    params: Mapping[str, str] = field(default_factory=dict)

    @property
    def key(self) -> tuple[LintCode, tuple[str, ...]]:
        """Return the identity used to avoid duplicate issues."""
        return (self.code, self.commit_ids)


def lint(commits: Sequence[CareCommit], entity_names: Mapping[str, str]) -> list[LintFinding]:
    """Run every implemented rule over the active commits."""
    return list(_temporary_change_without_end(commits, entity_names))


def _temporary_change_without_end(
    commits: Sequence[CareCommit], entity_names: Mapping[str, str]
) -> Iterator[LintFinding]:
    """L002: a temporary change with no captured end date or end condition."""
    for commit in commits:
        effective = commit.effective
        if not (commit.is_active and commit.temporary):
            continue
        if effective.end is not None or effective.end_condition is not None:
            continue
        params = {
            "action_noun": action_noun(commit.attributes.action),
            "entity": entity_names.get(commit.entity_id, commit.subject_text),
        }
        if commit.context:
            question = TemplateId.L002_QUESTION
            params["context"] = commit.context
        else:
            question = TemplateId.L002_QUESTION_NO_CONTEXT
        yield LintFinding(
            code=LintCode.L002,
            entity_id=commit.entity_id,
            commit_ids=(commit.commit_id,),
            message_template=TemplateId.L002_MESSAGE,
            question_template=question,
            params=params,
        )
