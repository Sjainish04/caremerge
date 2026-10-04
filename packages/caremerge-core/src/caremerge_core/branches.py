"""Temporary pathways ("branches") such as a procedure (spec §9.6).

A temporary candidate with a context joins a branch keyed by that context
plus the date of the matching event captured in the same source, for
example ``procedure-2026-10-28``. Without a dated event, the key is the
context alone.
"""

from collections.abc import Sequence

from caremerge_core.contracts import CandidateCommit
from caremerge_core.plan import EVENT_KINDS
from caremerge_core.provenance import normalize


def slug(text: str) -> str:
    """Return a lowercase, hyphen-separated key for ``text``."""
    return "-".join(normalize(text).split())


def branch_key(candidate: CandidateCommit, siblings: Sequence[CandidateCommit]) -> str | None:
    """Return the branch a temporary candidate belongs to, or ``None``."""
    if not candidate.temporary or not candidate.context:
        return None
    context = slug(candidate.context)
    events = [
        sibling
        for sibling in siblings
        if sibling.kind in EVENT_KINDS and sibling.attributes.scheduled_for is not None
    ]
    named = [event for event in events if context in {slug(event.subject_text), event.kind.value}]
    chosen = named or (events if len(events) == 1 else [])
    if not chosen:
        return context
    scheduled = chosen[0].attributes.scheduled_for
    return f"{context}-{scheduled.isoformat()}" if scheduled else context
