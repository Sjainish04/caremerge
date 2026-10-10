"""Reminders: propose, then confirm through the policy gate (feature F8).

A proposal renders the exact reminder text from a template: a question for
the care team about an open issue, or a reminder that restates one verified
instruction with its source (spec §9.10). Confirmation runs
``check_reminder`` and only then stores the reminder as executed; the
simulated Alexa lists executed reminders. Confirming an executed reminder
again is a no-op, so retries never create duplicates.
"""

from datetime import UTC, datetime, timedelta

import structlog

from caremerge_addon import speech
from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.settings import AddonSettings
from caremerge_core.enums import ActionState, IssueStatus, TemplateId
from caremerge_core.models import Action, CareCommit
from caremerge_core.policy import PolicyCode, PolicyViolationError, check_reminder
from caremerge_core.questions import render

log = structlog.get_logger(__name__)


def default_alarm(now: datetime, settings: AddonSettings) -> datetime:
    """Return tomorrow at the configured local reminder time, in UTC."""
    tomorrow = (now.astimezone(settings.tz) + timedelta(days=1)).date()
    local = datetime.combine(tomorrow, settings.default_reminder_time, tzinfo=settings.tz)
    return local.astimezone(UTC)


def propose_issue_reminder(
    issue_id: str, alarm_at: datetime | None, ctx: PipelineContext
) -> Action:
    """Propose an "ask your care team" reminder for an open issue.

    Raises ``PolicyViolationError`` when the issue is no longer open, because
    the gate would refuse the reminder.
    """
    issue = next((i for i in ctx.repo.snapshot().issues if i.issue_id == issue_id), None)
    if issue is None:
        raise RecordNotFoundError("issue", issue_id)
    if issue.status is not IssueStatus.OPEN:
        raise PolicyViolationError((PolicyCode.ISSUE_NOT_OPEN,))
    params = {"question": issue.question}
    return _propose(TemplateId.ASK_CARE_TEAM, params, alarm_at, ctx, issue_ids=(issue_id,))


def propose_commit_reminder(
    commit_id: str, alarm_at: datetime | None, ctx: PipelineContext
) -> Action:
    """Propose a reminder that restates one verified instruction with its source.

    Raises ``PolicyViolationError`` when the commit is not verified or
    corrected, because the gate would refuse the reminder.
    """
    commit = next((c for c in ctx.repo.snapshot().commits if c.commit_id == commit_id), None)
    if commit is None:
        raise RecordNotFoundError("commit", commit_id)
    if not commit.is_active:
        raise PolicyViolationError((PolicyCode.UNVERIFIED_COMMIT,))
    params = _restatement(commit, ctx)
    template_id = TemplateId.REMIND_VERIFIED_INSTRUCTION
    return _propose(template_id, params, alarm_at, ctx, commit_ids=(commit_id,))


def confirm_reminder(action_id: str, confirmation_id: str, ctx: PipelineContext) -> Action:
    """Confirm a proposal and store the reminder; raises ``PolicyViolationError`` if refused."""
    snapshot = ctx.repo.snapshot()
    action = next((a for a in snapshot.actions if a.action_id == action_id), None)
    if action is None:
        raise RecordNotFoundError("action", action_id)
    if action.state is ActionState.EXECUTED:
        return action
    confirmed = action.model_copy(
        update={"state": ActionState.CONFIRMED, "confirmation_id": confirmation_id}
    )
    check_reminder(
        confirmed,
        {commit.commit_id: commit for commit in snapshot.commits},
        {issue.issue_id: issue for issue in snapshot.issues},
    )
    executed = confirmed.model_copy(
        update={"state": ActionState.EXECUTED, "executed_at": ctx.clock.now()}
    )
    ctx.repo.put_action(executed)
    log.info("reminder_stored", action_id=action_id)
    return executed


def _propose(
    template_id: TemplateId,
    params: dict[str, str],
    alarm_at: datetime | None,
    ctx: PipelineContext,
    *,
    issue_ids: tuple[str, ...] = (),
    commit_ids: tuple[str, ...] = (),
) -> Action:
    now = ctx.clock.now()
    action = Action(
        action_id=ctx.ids.new("act"),
        template_id=template_id,
        params=params,
        text=render(template_id, params),
        alarm_at=alarm_at or default_alarm(now, ctx.settings),
        issue_ids=issue_ids,
        commit_ids=commit_ids,
        created_at=now,
    )
    ctx.repo.put_action(action)
    log.info("reminder_proposed", action_id=action.action_id, template_id=template_id)
    return action


def _restatement(commit: CareCommit, ctx: PipelineContext) -> dict[str, str]:
    """Return the template fields that restate ``commit`` with its source."""
    captured = commit.source.captured_at.astimezone(ctx.settings.tz).date()
    return {
        "source": commit.source.label,
        "date": speech.month_day(captured),
        "quote": commit.source.evidence[0].quote,
    }
