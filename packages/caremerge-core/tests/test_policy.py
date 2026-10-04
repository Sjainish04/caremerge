"""Tests for the deterministic Bee-write policy gate (spec §9.10)."""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from caremerge_core.enums import (
    ActionState,
    IssueKind,
    IssueStatus,
    LintCode,
    ReviewState,
    TemplateId,
)
from caremerge_core.models import Action, CareCommit, Issue
from caremerge_core.policy import PolicyCode, PolicyViolationError, check_bee_write
from caremerge_core.questions import render

NOW = datetime(2026, 10, 19, 14, 0, tzinfo=UTC)
QUESTION = "When should the temporary hold of Medication A for the procedure end?"
Builder = Callable[..., CareCommit]


def _issue(status: IssueStatus = IssueStatus.OPEN) -> Issue:
    return Issue(
        issue_id="iss_1",
        kind=IssueKind.LINT,
        code=LintCode.L002,
        entity_id="ent_med_a",
        commit_ids=("cc_hold",),
        status=status,
        message="This temporary change has no captured end.",
        question=QUESTION,
        created_at=NOW,
    )


def _action(**overrides: object) -> Action:
    params = {"question": QUESTION}
    action = Action(
        action_id="act_1",
        template_id=TemplateId.ASK_CARE_TEAM,
        params=params,
        text=render(TemplateId.ASK_CARE_TEAM, params),
        alarm_at=NOW,
        issue_ids=("iss_1",),
        state=ActionState.CONFIRMED,
        confirmation_id="conf_1",
        created_at=NOW,
    )
    return action.model_copy(update=overrides)


def _check(
    action: Action,
    commit: Builder,
    *,
    issue: Issue | None = None,
    state: ReviewState = ReviewState.VERIFIED,
) -> None:
    commits = {"cc_hold": commit("cc_hold", state=state)}
    check_bee_write(action, commits, {"iss_1": issue or _issue()})


def test_confirmed_template_action_on_an_open_issue_passes(commit: Builder) -> None:
    _check(_action(), commit)


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"state": ActionState.PROPOSED}, PolicyCode.NOT_CONFIRMED),
        ({"confirmation_id": None}, PolicyCode.NOT_CONFIRMED),
        ({"bee_todo_id": "todo_1"}, PolicyCode.ALREADY_EXECUTED),
        ({"issue_ids": ()}, PolicyCode.NO_REFERENCES),
        ({"issue_ids": ("iss_404",)}, PolicyCode.UNKNOWN_ISSUE),
        ({"issue_ids": (), "commit_ids": ("cc_404",)}, PolicyCode.UNKNOWN_COMMIT),
        ({"template_id": TemplateId.L002_QUESTION}, PolicyCode.TEMPLATE_NOT_ALLOWED),
        ({"text": "Stop taking Medication A."}, PolicyCode.TEXT_NOT_FROM_TEMPLATE),
        ({"params": {"question": "Something else?"}}, PolicyCode.TEXT_NOT_FROM_TEMPLATE),
        ({"params": {}}, PolicyCode.TEXT_NOT_FROM_TEMPLATE),
    ],
)
def test_each_rule_refuses_with_its_code(
    commit: Builder, overrides: dict[str, object], code: PolicyCode
) -> None:
    with pytest.raises(PolicyViolationError) as caught:
        _check(_action(**overrides), commit)
    assert code in caught.value.codes


def test_issue_must_still_be_open(commit: Builder) -> None:
    with pytest.raises(PolicyViolationError) as caught:
        _check(_action(), commit, issue=_issue(IssueStatus.RESOLVED))
    assert caught.value.codes == (PolicyCode.ISSUE_NOT_OPEN,)


def test_commits_behind_the_issue_must_be_verified(commit: Builder) -> None:
    with pytest.raises(PolicyViolationError) as caught:
        _check(_action(), commit, state=ReviewState.CANDIDATE)
    assert caught.value.codes == (PolicyCode.UNVERIFIED_COMMIT,)
