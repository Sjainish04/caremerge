"""Policy gate for reminders (spec §9.10).

No reminder is stored unless the user confirmed it, it rests on verified and
sourced commits or open issues, and its text is exactly what an approved
template renders. A reminder may only restate one verified commit's own
quote and source, so it is never a new instruction. The gate is
deterministic; it never consults a model.
"""

from collections.abc import Mapping
from enum import StrEnum
from typing import Final

from caremerge_core.enums import ActionState, IssueStatus, TemplateId
from caremerge_core.errors import CareMergeError
from caremerge_core.models import Action, CareCommit, Issue
from caremerge_core.questions import TemplateError, render

TODO_TEMPLATES: Final = frozenset(
    {TemplateId.ASK_CARE_TEAM, TemplateId.REMIND_VERIFIED_INSTRUCTION}
)


class PolicyCode(StrEnum):
    """Why a reminder was refused."""

    NOT_CONFIRMED = "not_confirmed"
    ALREADY_EXECUTED = "already_executed"
    NO_REFERENCES = "no_references"
    UNKNOWN_ISSUE = "unknown_issue"
    ISSUE_NOT_OPEN = "issue_not_open"
    UNKNOWN_COMMIT = "unknown_commit"
    UNVERIFIED_COMMIT = "unverified_commit"
    TEMPLATE_NOT_ALLOWED = "template_not_allowed"
    TEXT_NOT_FROM_TEMPLATE = "text_not_from_template"
    NOT_A_RESTATEMENT = "not_a_restatement"


class PolicyViolationError(CareMergeError):
    """Raised when an action fails the gate. Carries codes, never content."""

    def __init__(self, codes: tuple[PolicyCode, ...]) -> None:
        self.codes = codes
        super().__init__(", ".join(codes))


def check_reminder(
    action: Action,
    commits: Mapping[str, CareCommit],
    issues: Mapping[str, Issue],
) -> None:
    """Raise ``PolicyViolationError`` unless ``action`` may be stored as a reminder."""
    codes: list[PolicyCode] = []
    if action.state is not ActionState.CONFIRMED or not action.confirmation_id:
        codes.append(PolicyCode.NOT_CONFIRMED)
    if action.state is ActionState.EXECUTED or action.executed_at is not None:
        codes.append(PolicyCode.ALREADY_EXECUTED)
    if not action.issue_ids and not action.commit_ids:
        codes.append(PolicyCode.NO_REFERENCES)
    referenced = set(action.commit_ids)
    for issue_id in action.issue_ids:
        issue = issues.get(issue_id)
        if issue is None:
            codes.append(PolicyCode.UNKNOWN_ISSUE)
            continue
        if issue.status is not IssueStatus.OPEN:
            codes.append(PolicyCode.ISSUE_NOT_OPEN)
        referenced.update(issue.commit_ids)
    for commit_id in sorted(referenced):
        commit = commits.get(commit_id)
        if commit is None:
            codes.append(PolicyCode.UNKNOWN_COMMIT)
        elif not commit.is_active:
            codes.append(PolicyCode.UNVERIFIED_COMMIT)
    codes.extend(_template_codes(action))
    if action.template_id is TemplateId.REMIND_VERIFIED_INSTRUCTION:
        codes.extend(_restatement_codes(action, commits))
    if codes:
        raise PolicyViolationError(tuple(dict.fromkeys(codes)))


def _template_codes(action: Action) -> list[PolicyCode]:
    if action.template_id not in TODO_TEMPLATES:
        return [PolicyCode.TEMPLATE_NOT_ALLOWED]
    try:
        expected = render(action.template_id, action.params)
    except TemplateError:
        return [PolicyCode.TEXT_NOT_FROM_TEMPLATE]
    return [] if expected == action.text else [PolicyCode.TEXT_NOT_FROM_TEMPLATE]


def _restatement_codes(action: Action, commits: Mapping[str, CareCommit]) -> list[PolicyCode]:
    """A reminder must quote exactly one commit's own evidence and source label."""
    if action.issue_ids or len(action.commit_ids) != 1:
        return [PolicyCode.NOT_A_RESTATEMENT]
    commit = commits.get(action.commit_ids[0])
    if commit is None:
        return []
    quotes = {evidence.quote for evidence in commit.source.evidence}
    if action.params.get("quote") in quotes and action.params.get("source") == commit.source.label:
        return []
    return [PolicyCode.NOT_A_RESTATEMENT]
