"""User review of candidate commits: verify, correct, or reject (feature F3).

Every decision updates the commit, appends an audit event, and refreshes
issues, because a verified commit can open an issue and a correction can
resolve one.
"""

import structlog
from pydantic import BaseModel, ConfigDict

from caremerge_addon.errors import RecordNotFoundError
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.pipeline.issues import refresh_issues
from caremerge_core.contracts import Attributes, Effective
from caremerge_core.enums import ReviewState
from caremerge_core.models import CareCommit, Review, ReviewEvent

log = structlog.get_logger(__name__)


class Correction(BaseModel):
    """Fields the user replaced while reviewing a candidate."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    attributes: Attributes | None = None
    effective: Effective | None = None


def verify_commit(commit_id: str, ctx: PipelineContext) -> CareCommit:
    """Accept a candidate as captured."""
    return _decide(commit_id, ReviewState.VERIFIED, None, ctx)


def reject_commit(commit_id: str, ctx: PipelineContext) -> CareCommit:
    """Reject a candidate; it never counts toward the plan."""
    return _decide(commit_id, ReviewState.REJECTED, None, ctx)


def correct_commit(commit_id: str, correction: Correction, ctx: PipelineContext) -> CareCommit:
    """Accept a candidate with fields the user corrected."""
    return _decide(commit_id, ReviewState.CORRECTED, correction, ctx)


def _decide(
    commit_id: str,
    state: ReviewState,
    correction: Correction | None,
    ctx: PipelineContext,
) -> CareCommit:
    commit = next((c for c in ctx.repo.snapshot().commits if c.commit_id == commit_id), None)
    if commit is None:
        raise RecordNotFoundError("commit", commit_id)
    now = ctx.clock.now()
    update: dict[str, object] = {"review": Review(state=state, at=now)}
    if correction is not None and correction.attributes is not None:
        update["attributes"] = correction.attributes
    if correction is not None and correction.effective is not None:
        update["effective"] = correction.effective
    decided = commit.model_copy(update=update)
    ctx.repo.put_commit(decided)
    ctx.repo.append_review(
        ReviewEvent(
            commit_id=commit_id,
            state=state,
            at=now,
            attributes=correction.attributes if correction else None,
            effective=correction.effective if correction else None,
        )
    )
    log.info("commit_reviewed", commit_id=commit_id, state=state)
    refresh_issues(ctx)
    return decided
