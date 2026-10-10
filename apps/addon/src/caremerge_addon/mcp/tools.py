"""The add-on's tool logic: pipeline calls in, typed results with speech out.

Each function serves one MCP tool (spec §7.2). The MCP layer in
``caremerge_addon.mcp.server`` only registers these and maps errors, so the
logic is tested without a protocol in the way.
"""

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from zoneinfo import ZoneInfo

from caremerge_addon import speech
from caremerge_addon.errors import InvalidRequestError, RecordNotFoundError
from caremerge_addon.mcp.results import (
    ChangeCard,
    DataDeletedResult,
    ItemCard,
    ItemsAddedResult,
    OpenQuestionsResult,
    PendingConfirmation,
    PlanDayResult,
    PlanEntryCard,
    QuestionCard,
    ReminderCard,
    ReminderListResult,
    ReminderProposalResult,
    ReminderStoredResult,
    SegmentCard,
    SourceInfo,
    VisitAddedResult,
    VisitCard,
    VisitListResult,
    VisitUpdatesResult,
    WhatsChangedResult,
)
from caremerge_addon.pipeline import intake, reminders
from caremerge_addon.pipeline.compiler import compile_source
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.review import verify_commit
from caremerge_addon.pipeline.views import diff_since_last_visit, plan_on
from caremerge_addon.visits.models import Visit
from caremerge_core.diff import DiffEntry
from caremerge_core.enums import ActionState, IssueStatus, ReviewState, TemplateId
from caremerge_core.models import Action, CareCommit, Issue
from caremerge_core.plan import PlanEntry, Segment


def list_visits(ctx: PipelineContext) -> VisitListResult:
    """Return every inbox visit, marking the ones already added."""
    added = {source.external_id for source in ctx.repo.snapshot().sources}
    visits = [_visit_card(visit, visit.visit_id in added, ctx) for visit in ctx.inbox.list_visits()]
    return VisitListResult(speech="", visits=visits)


def add_visit(ctx: PipelineContext, visit_id: str) -> VisitAddedResult:
    """Add one inbox visit and compile it if it is new."""
    visit = ctx.inbox.get_visit(visit_id)
    added = intake.add_visit(visit_id, ctx)
    report = compile_source(added.source, ctx) if added.is_new else None
    return VisitAddedResult(
        speech=speech.visit_added(added.source, is_new=added.is_new, tz=ctx.settings.tz),
        visit=_visit_card(visit, True, ctx),
        created=len(report.created) if report else 0,
        rejected=report.rejected if report else 0,
    )


def visit_updates(ctx: PipelineContext, clinician: str | None) -> VisitUpdatesResult:
    """Return the newest visit's unconfirmed items, optionally for one clinician."""
    snapshot = ctx.repo.snapshot()
    pending: dict[str, list[CareCommit]] = {}
    for commit in snapshot.commits:
        if commit.review.state is ReviewState.CANDIDATE:
            pending.setdefault(commit.source.source_id, []).append(commit)
    sources = [
        source
        for source in snapshot.sources
        if source.source_id in pending and (clinician is None or _matches(clinician, source.label))
    ]
    if not sources:
        return VisitUpdatesResult(
            speech=speech.sentence(TemplateId.SPEAK_NO_VISIT_UPDATES),
            clinician=None,
            visit_date=None,
            items=[],
            confirmation=None,
        )
    source = sources[-1]
    items = pending[source.source_id]
    tz = ctx.settings.tz
    return VisitUpdatesResult(
        speech=speech.visit_updates(source, items, tz),
        clinician=source.label,
        visit_date=speech.local_date(source.captured_at, tz),
        items=[_item_card(commit, tz) for commit in items],
        confirmation=PendingConfirmation(
            tool="confirm_items",
            arguments={"commit_ids": [commit.commit_id for commit in items]},
        ),
    )


def confirm_items(
    ctx: PipelineContext, commit_ids: Sequence[str], confirmation_id: str
) -> ItemsAddedResult:
    """Verify the listed candidates; already-reviewed items are left as they are."""
    commits = {commit.commit_id: commit for commit in ctx.repo.snapshot().commits}
    missing = [commit_id for commit_id in commit_ids if commit_id not in commits]
    if missing:
        raise RecordNotFoundError("commit", missing[0])
    verified = [
        commit_id
        for commit_id in commit_ids
        if commits[commit_id].review.state is ReviewState.CANDIDATE
    ]
    for commit_id in verified:
        verify_commit(commit_id, ctx)
    return ItemsAddedResult(
        speech=speech.sentence(TemplateId.SPEAK_ITEMS_ADDED), commit_ids=verified
    )


def whats_changed(ctx: PipelineContext) -> WhatsChangedResult:
    """Return the CareDiff since the last visit, spoken and as cards."""
    diff = diff_since_last_visit(ctx)
    snapshot = ctx.repo.snapshot()
    commits = {commit.commit_id: commit for commit in snapshot.commits}
    names = snapshot.entity_names()
    open_count = sum(1 for issue in snapshot.issues if issue.status is IssueStatus.OPEN)
    tz = ctx.settings.tz
    return WhatsChangedResult(
        speech=speech.changes(diff, commits, names, open_questions=open_count),
        changes=[_change_card(entry, commits, names, tz) for entry in diff.entries],
        open_questions=open_count,
    )


def plan_for_day(ctx: PipelineContext, day: date, subject: str | None) -> PlanDayResult:
    """Return what the confirmed plan says on ``day``, optionally for one subject."""
    entries = plan_on(day, ctx)
    snapshot = ctx.repo.snapshot()
    commits = {commit.commit_id: commit for commit in snapshot.commits}
    names = snapshot.entity_names()
    tz = ctx.settings.tz
    shown = [
        entry
        for entry in entries
        if subject is None or _matches(subject, names.get(entry.entity_id, ""))
    ]
    return PlanDayResult(
        speech=speech.plan_day(day, subject, entries, commits, names, tz),
        day=day,
        entries=[_plan_card(entry, commits, names, tz) for entry in shown],
    )


def open_questions(ctx: PipelineContext) -> OpenQuestionsResult:
    """Return every open clarification question."""
    snapshot = ctx.repo.snapshot()
    commits = {commit.commit_id: commit for commit in snapshot.commits}
    names = snapshot.entity_names()
    issues = [issue for issue in snapshot.issues if issue.status is IssueStatus.OPEN]
    tz = ctx.settings.tz
    return OpenQuestionsResult(
        speech=speech.questions([issue.question for issue in issues]),
        questions=[_question_card(issue, commits, names, tz) for issue in issues],
    )


def propose_reminder(
    ctx: PipelineContext,
    question_id: str | None,
    commit_id: str | None,
    alarm_at: datetime | None,
) -> ReminderProposalResult:
    """Propose a reminder for a question or a confirmed instruction, then await a yes.

    With neither ID, the newest open question is used. Raises ``InvalidRequestError``
    when both are given.
    """
    if question_id and commit_id:
        msg = "give at most one of question_id or commit_id"
        raise InvalidRequestError(msg)
    if commit_id:
        action = reminders.propose_commit_reminder(commit_id, alarm_at, ctx)
    else:
        issue_id = question_id or _newest_open_issue(ctx)
        if issue_id is None:
            return ReminderProposalResult(
                speech=speech.sentence(TemplateId.SPEAK_NO_REMINDER_TOPIC),
                reminder=None,
                confirmation=None,
            )
        action = reminders.propose_issue_reminder(issue_id, alarm_at, ctx)
    return ReminderProposalResult(
        speech=speech.reminder_proposal(action, ctx.clock.now(), ctx.settings.tz),
        reminder=_reminder_card(action, ctx),
        confirmation=PendingConfirmation(
            tool="confirm_reminder", arguments={"action_id": action.action_id}
        ),
    )


def confirm_reminder(
    ctx: PipelineContext, action_id: str, confirmation_id: str
) -> ReminderStoredResult:
    """Store a proposed reminder after the user's yes, through the policy gate."""
    action = reminders.confirm_reminder(action_id, confirmation_id, ctx)
    return ReminderStoredResult(
        speech=speech.sentence(TemplateId.SPEAK_REMINDER_ADDED),
        reminder=_reminder_card(action, ctx),
    )


def list_reminders(ctx: PipelineContext) -> ReminderListResult:
    """Return every stored reminder, soonest first."""
    stored = sorted(
        (a for a in ctx.repo.snapshot().actions if a.state is ActionState.EXECUTED),
        key=lambda action: action.alarm_at,
    )
    return ReminderListResult(speech="", reminders=[_reminder_card(a, ctx) for a in stored])


def delete_my_data(ctx: PipelineContext, confirmation_id: str) -> DataDeletedResult:
    """Delete every record in the user's partition."""
    ctx.repo.delete_all()
    return DataDeletedResult(speech=speech.sentence(TemplateId.SPEAK_DATA_DELETED))


def _visit_card(visit: Visit, added: bool, ctx: PipelineContext) -> VisitCard:
    return VisitCard(
        visit_id=visit.visit_id,
        title=visit.title,
        clinician=visit.clinician,
        role=visit.role,
        date=speech.local_date(visit.started_at, ctx.settings.tz),
        added=added,
    )


def _source_info(commit: CareCommit, tz: ZoneInfo) -> SourceInfo:
    return SourceInfo(
        clinician=commit.source.label,
        role=commit.source.role,
        date=speech.local_date(commit.source.captured_at, tz),
        quote=commit.source.evidence[0].quote,
    )


def _item_card(commit: CareCommit, tz: ZoneInfo) -> ItemCard:
    return ItemCard(
        commit_id=commit.commit_id,
        kind=commit.kind,
        subject=commit.subject_text,
        summary=speech.item_phrase(commit),
        temporary=commit.temporary,
        source=_source_info(commit, tz),
        signals=commit.signals,
    )


def _segment_cards(entry: DiffEntry, segments: Sequence[Segment]) -> list[SegmentCard]:
    return [
        SegmentCard(
            start=segment.start,
            end=segment.end,
            values=[speech.value_words(entry.dimension, (value,)) for value in segment.values],
            temporary=segment.temporary,
            end_captured=segment.end_captured,
        )
        for segment in segments
    ]


def _change_card(
    entry: DiffEntry,
    commits: Mapping[str, CareCommit],
    names: Mapping[str, str],
    tz: ZoneInfo,
) -> ChangeCard:
    commit_ids = dict.fromkeys(cid for segment in entry.after for cid in segment.commit_ids)
    return ChangeCard(
        subject=names.get(entry.entity_id, entry.entity_id),
        dimension=entry.dimension,
        change=entry.change,
        before=_segment_cards(entry, entry.before),
        after=_segment_cards(entry, entry.after),
        future_effective=entry.future_effective,
        temporary=entry.temporary,
        end_not_captured=entry.end_not_captured,
        sources=[_source_info(commits[cid], tz) for cid in commit_ids],
    )


def _plan_card(
    entry: PlanEntry,
    commits: Mapping[str, CareCommit],
    names: Mapping[str, str],
    tz: ZoneInfo,
) -> PlanEntryCard:
    latest = max((commits[cid] for cid in entry.commit_ids), key=lambda c: c.source.captured_at)
    return PlanEntryCard(
        subject=names.get(entry.entity_id, entry.entity_id),
        dimension=entry.dimension,
        values=[speech.value_words(entry.dimension, (value,)) for value in entry.values],
        temporary=entry.temporary,
        end_captured=entry.end_captured,
        source=_source_info(latest, tz),
    )


def _question_card(
    issue: Issue,
    commits: Mapping[str, CareCommit],
    names: Mapping[str, str],
    tz: ZoneInfo,
) -> QuestionCard:
    return QuestionCard(
        issue_id=issue.issue_id,
        question=issue.question,
        subject=names.get(issue.entity_id, issue.entity_id),
        source=_source_info(commits[issue.commit_ids[0]], tz),
    )


def _reminder_card(action: Action, ctx: PipelineContext) -> ReminderCard:
    snapshot = ctx.repo.snapshot()
    commits = {commit.commit_id: commit for commit in snapshot.commits}
    issues = {issue.issue_id: issue for issue in snapshot.issues}
    referenced = list(action.commit_ids) + [
        cid for iid in action.issue_ids if iid in issues for cid in issues[iid].commit_ids
    ]
    basis = next((commits[cid] for cid in referenced if cid in commits), None)
    return ReminderCard(
        action_id=action.action_id,
        text=action.text,
        alarm_at=action.alarm_at,
        state=action.state,
        based_on=_source_info(basis, ctx.settings.tz) if basis else None,
    )


def _newest_open_issue(ctx: PipelineContext) -> str | None:
    open_issues = [i for i in ctx.repo.snapshot().issues if i.status is IssueStatus.OPEN]
    if not open_issues:
        return None
    return max(open_issues, key=lambda issue: issue.created_at).issue_id


def _matches(wanted: str, name: str) -> bool:
    wanted_text, known = wanted.casefold().strip(), name.casefold().strip()
    return bool(wanted_text) and (wanted_text in known or known in wanted_text)
