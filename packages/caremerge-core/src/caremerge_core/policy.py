"""Policy gate for Bee writes (spec §9.10).

Nothing reaches Bee unless the user confirmed it, it rests on verified and
sourced commits or open issues, and its text is exactly what an approved
template renders. The gate is deterministic; it never consults a model.
"""

from collections.abc import Mapping
from enum import StrEnum
from typing import Final

from caremerge_core.enums import ActionState, IssueStatus, TemplateId
from caremerge_core.errors import CareMergeError
from caremerge_core.models import Action, CareCommit, Issue
from caremerge_core.questions import TemplateError, render

TODO_TEMPLATES: Final = frozenset({TemplateId.ASK_CARE_TEAM})


class PolicyCode(StrEnum):
    """Why a Bee write was refused."""

    NOT_CONFIRMED = "not_confirmed"
    ALREADY_EXECUTED = "already_executed"
    NO_REFERENCES = "no_references"
    UNKNOWN_ISSUE = "unknown_issue"
    ISSUE_NOT_OPEN = "issue_not_open"
    UNKNOWN_COMMIT = "unknown_commit"
    UNVERIFIED_COMMIT = "unverified_commit"
    TEMPLATE_NOT_ALLOWED = "template_not_allowed"
    TEXT_NOT_FROM_TEMPLATE = "text_not_from_template"


class PolicyViolationError(CareMergeError):
    """Raised when an action fails the gate. Carries codes, never content."""

    def __init__(self, codes: tuple[PolicyCode, ...]) -> None:
        self.codes = codes
        super().__init__(", ".join(codes))


def check_bee_write(
    action: Action,
    commits: Mapping[str, CareCommit],
    issues: Mapping[str, Issue],
) -> None:
    """Raise ``PolicyViolationError`` unless ``action`` may be written to Bee."""
    codes: list[PolicyCode] = []
    if action.state is not ActionState.CONFIRMED or not action.confirmation_id:
        codes.append(PolicyCode.NOT_CONFIRMED)
    if action.bee_todo_id is not None:
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
