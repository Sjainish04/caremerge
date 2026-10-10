"""Keep clarification issues in step with CareLint findings (feature F6).

New findings open issues with templated text. An open issue whose gap has
been filled (for example, a corrected commit gained an end date) is marked
resolved. Dismissed issues stay dismissed.
"""

from collections.abc import Mapping

import structlog

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_core.enums import IssueKind, IssueStatus, TemplateId
from caremerge_core.lint import lint
from caremerge_core.models import Issue
from caremerge_core.plan import known
from caremerge_core.questions import render, template_fields

log = structlog.get_logger(__name__)


def refresh_issues(ctx: PipelineContext) -> None:
    """Open issues for new findings and resolve issues whose gap is gone."""
    snapshot = ctx.repo.snapshot()
    findings = {f.key: f for f in lint(known(snapshot.commits), snapshot.entity_names())}
    existing = {(issue.code, issue.commit_ids): issue for issue in snapshot.issues}
    now = ctx.clock.now()
    for key, finding in findings.items():
        if key in existing:
            continue
        issue = Issue(
            issue_id=ctx.ids.new("iss"),
            kind=IssueKind.LINT,
            code=finding.code,
            entity_id=finding.entity_id,
            commit_ids=finding.commit_ids,
            status=IssueStatus.OPEN,
            message=_render(finding.message_template, finding.params),
            question=_render(finding.question_template, finding.params),
            created_at=now,
        )
        ctx.repo.put_issue(issue)
        log.info("issue_opened", issue_id=issue.issue_id, code=issue.code)
    for key, issue in existing.items():
        if issue.status is IssueStatus.OPEN and key not in findings:
            ctx.repo.put_issue(issue.model_copy(update={"status": IssueStatus.RESOLVED}))
            log.info("issue_resolved", issue_id=issue.issue_id)


def dismiss_issue(issue_id: str, ctx: PipelineContext) -> Issue:
    """Mark an issue as dismissed by the user."""
    issue = next((i for i in ctx.repo.snapshot().issues if i.issue_id == issue_id), None)
    if issue is None:
        raise RecordNotFoundError("issue", issue_id)
    dismissed = issue.model_copy(update={"status": IssueStatus.DISMISSED})
    ctx.repo.put_issue(dismissed)
    return dismissed


def _render(template_id: TemplateId, params: Mapping[str, str]) -> str:
    """Render with exactly the parameters this template uses."""
    return render(template_id, {name: params[name] for name in template_fields(template_id)})
