"""Read models: what changed since the last visit, and the plan on a day.

All views are computed on read from the ledger snapshot (spec §10.2), so
they always reflect the latest verified state.
"""

from datetime import date, timedelta

from caremerge_addon.pipeline.context import PipelineContext
from caremerge_core.diff import CareDiff, care_diff
from caremerge_core.plan import DateWindow, PlanEntry, plan_at


def diff_since_last_visit(ctx: PipelineContext) -> CareDiff:
    """Compare the plan known before the most recent visit with the plan now."""
    snapshot = ctx.repo.snapshot()
    latest = snapshot.sources[-1].captured_at if snapshot.sources else None
    today = ctx.clock.now().astimezone(ctx.settings.tz).date()
    window = DateWindow(start=today, end=today + timedelta(days=ctx.settings.plan_horizon_days))
    return care_diff(
        snapshot.commits,
        known_before=latest,
        window=window,
        tz=ctx.settings.tz,
        entity_names=snapshot.entity_names(),
    )


def plan_on(day: date, ctx: PipelineContext) -> tuple[PlanEntry, ...]:
    """Return the plan's values on ``day``; only verified commits count."""
    return plan_at(ctx.repo.snapshot().commits, day, ctx.settings.tz)
