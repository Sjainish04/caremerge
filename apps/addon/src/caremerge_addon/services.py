"""The add-on's injected dependencies, and the per-user pipeline context they build.

The composition root (``caremerge_addon.main``) builds one ``AddonServices``
per process; every tool call resolves the caller's ledger through it. Tests
build their own with fakes.
"""

from dataclasses import dataclass

from caremerge_addon.extraction.client import ExtractionClient
from caremerge_addon.pipeline.context import PipelineContext
from caremerge_addon.runtime import Clock, IdFactory
from caremerge_addon.settings import AddonSettings
from caremerge_addon.store.ledger import Ledger
from caremerge_addon.visits.inbox import VisitInbox


@dataclass(frozen=True)
class AddonServices:
    """Settings, ports, and runtime sources shared by every request."""

    settings: AddonSettings
    ledger: Ledger
    inbox: VisitInbox
    extraction: ExtractionClient
    clock: Clock
    ids: IdFactory

    def context_for(self, user_id: str) -> PipelineContext:
        """Return the pipeline context for one user's ledger."""
        return PipelineContext(
            settings=self.settings,
            repo=self.ledger.for_user(user_id),
            inbox=self.inbox,
            extraction=self.extraction,
            clock=self.clock,
            ids=self.ids,
        )
