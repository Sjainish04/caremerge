"""The dependencies every pipeline step receives, bundled for injection.

The composition root (``caremerge_addon.main``) builds one ``PipelineContext``
per request, for the caller's ledger; tests build their own with fakes. No
step reaches for globals.
"""

from dataclasses import dataclass

from caremerge_addon.extraction.client import ExtractionClient
from caremerge_addon.runtime import Clock, IdFactory
from caremerge_addon.settings import AddonSettings
from caremerge_addon.visits.inbox import VisitInbox
from caremerge_core.repository import CareGraphRepository


@dataclass(frozen=True)
class PipelineContext:
    """Settings, ports, and runtime sources for one user's request."""

    settings: AddonSettings
    repo: CareGraphRepository
    inbox: VisitInbox
    extraction: ExtractionClient
    clock: Clock
    ids: IdFactory
