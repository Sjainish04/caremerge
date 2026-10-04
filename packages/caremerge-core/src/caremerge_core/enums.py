"""Closed vocabularies shared by every CareMerge component.

Enum values are the wire format: they appear unchanged in agent contracts,
the ledger, and the local API (spec §9.1).
"""

from enum import StrEnum


class CommitKind(StrEnum):
    """What a CareCommit describes."""

    MEDICATION_INSTRUCTION = "medication_instruction"
    MONITORING_INSTRUCTION = "monitoring_instruction"
    APPOINTMENT = "appointment"
    PROCEDURE = "procedure"
    TEST = "test"
    FOLLOW_UP = "follow_up"
    OBSERVATION = "observation"


class MedAction(StrEnum):
    """The action a medication instruction asks for."""

    CONTINUE = "continue"
    START = "start"
    STOP = "stop"
    HOLD = "hold"
    RESUME = "resume"


class TimeOfDay(StrEnum):
    """When in the day an instruction applies."""

    MORNING = "morning"
    MIDDAY = "midday"
    EVENING = "evening"
    BEDTIME = "bedtime"


class FoodRelation(StrEnum):
    """How an instruction relates to meals."""

    WITH_FOOD = "with_food"
    WITHOUT_FOOD = "without_food"


class Weekday(StrEnum):
    """Days of the week, in calendar order."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class DateBasis(StrEnum):
    """How a date was established from the source text."""

    EXPLICIT = "explicit"
    RELATIVE = "relative"
    NONE = "none"


class EntityMatch(StrEnum):
    """How confidently an extracted subject maps to a known entity."""

    MATCHED = "matched"
    POSSIBLE_MATCH = "possible_match"
    NEW = "new"
    AMBIGUOUS = "ambiguous"


class Modality(StrEnum):
    """What kind of statement the source made."""

    INSTRUCTION = "instruction"
    INFORMATION = "information"
    PATIENT_STATEMENT = "patient_statement"
    QUESTION = "question"


class SelfRating(StrEnum):
    """The extractor's own rating. Internal only; never shown as a number."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SpeakerBasis(StrEnum):
    """Where a commit's speaker role came from."""

    SESSION_LABEL = "session_label"
    CONTENT_INFERRED = "content_inferred"


class Role(StrEnum):
    """Care-team role the user assigns to a session at import."""

    FAMILY_PHYSICIAN = "family_physician"
    SPECIALIST = "specialist"
    PHARMACIST = "pharmacist"
    NURSE = "nurse"
    OTHER_CLINICIAN = "other_clinician"
    SELF = "self"


class BeeItemType(StrEnum):
    """The kind of Bee item a source was imported from."""

    CONVERSATION = "conversation"
    VOICE_NOTE = "voice_note"


class ReviewState(StrEnum):
    """Where a commit stands in user review."""

    CANDIDATE = "candidate"
    VERIFIED = "verified"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class Dimension(StrEnum):
    """A comparable aspect of a care item: the unit of plans and diffs."""

    ACTION = "action"
    DOSE = "dose"
    TIME_OF_DAY = "time_of_day"
    FOOD_RELATION = "food_relation"
    DAYS_OF_WEEK = "days_of_week"
    SCHEDULED_FOR = "scheduled_for"
    INTERVAL = "interval"


class ChangeType(StrEnum):
    """How a dimension's schedule changed between two knowledge points."""

    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"


class IssueKind(StrEnum):
    """Family of a clarification issue. Conflicts arrive with feature F9."""

    LINT = "lint"


class IssueStatus(StrEnum):
    """Lifecycle of a clarification issue."""

    OPEN = "open"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class LintCode(StrEnum):
    """CareLint rules implemented so far (spec §9.8)."""

    L002 = "L002"


class ActionState(StrEnum):
    """Lifecycle of a proposed Bee write."""

    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    EXECUTED = "executed"
    FAILED = "failed"


class TemplateId(StrEnum):
    """Registered user-facing text templates (principle P9)."""

    L002_MESSAGE = "l002_message"
    L002_QUESTION = "l002_question"
    L002_QUESTION_NO_CONTEXT = "l002_question_no_context"
    ASK_CARE_TEAM = "ask_care_team"
