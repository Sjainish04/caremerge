"""The visit model the inbox serves (spec §5.2).

``title`` is display-only and never enters a ``SourceEvent`` (spec §7.5).
Times must carry a timezone, so a capture date is never read in the host's
zone.
"""

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from caremerge_core.contracts import Utterance
from caremerge_core.enums import Role


class Visit(BaseModel):
    """One care visit's transcript, with who spoke for the care team and when."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    visit_id: str = Field(min_length=1)
    title: str
    clinician: str = Field(min_length=1)
    role: Role
    started_at: AwareDatetime
    utterances: tuple[Utterance, ...] = Field(min_length=1)
