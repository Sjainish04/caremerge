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


class SourceKind(StrEnum):
    """Where a source came from: a visit transcript or, with F13, a spoken note."""

    VISIT = "visit"
    NOTE = "note"


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
    """Lifecycle of a proposed reminder."""

    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    EXECUTED = "executed"
    FAILED = "failed"


class TemplateId(StrEnum):
    """Registered user-facing text templates, on screen and spoken (principle P9)."""

    L002_MESSAGE = "l002_message"
    L002_QUESTION = "l002_question"
    L002_QUESTION_NO_CONTEXT = "l002_question_no_context"
    ASK_CARE_TEAM = "ask_care_team"
    REMIND_VERIFIED_INSTRUCTION = "remind_verified_instruction"
    SPEAK_VISIT_UPDATES = "speak_visit_updates"
    SPEAK_NO_VISIT_UPDATES = "speak_no_visit_updates"
    SPEAK_ITEMS_ADDED = "speak_items_added"
    SPEAK_VISIT_READY = "speak_visit_ready"
    SPEAK_VISIT_ALREADY_ADDED = "speak_visit_already_added"
    SPEAK_NO_CHANGES = "speak_no_changes"
    SPEAK_CHANGES_INTRO = "speak_changes_intro"
    SPEAK_CHANGE_STATE = "speak_change_state"
    SPEAK_CHANGE_DETAIL = "speak_change_detail"
    SPEAK_CHANGE_NEW = "speak_change_new"
    SPEAK_CHANGE_REMOVED = "speak_change_removed"
    SPEAK_END_NOT_CAPTURED = "speak_end_not_captured"
    SPEAK_MORE_ON_SCREEN = "speak_more_on_screen"
    SPEAK_QUESTIONS_PENDING = "speak_questions_pending"
    SPEAK_PLAN_DAY = "speak_plan_day"
    SPEAK_PLAN_EVENT = "speak_plan_event"
    SPEAK_PLAN_CONFLICT = "speak_plan_conflict"
    SPEAK_PLAN_NOTHING = "speak_plan_nothing"
    SPEAK_PLAN_EMPTY = "speak_plan_empty"
    SPEAK_PLAN_OVERVIEW = "speak_plan_overview"
    SPEAK_SOURCE = "speak_source"
    SPEAK_NOT_DECIDING = "speak_not_deciding"
    SPEAK_NO_QUESTIONS = "speak_no_questions"
    SPEAK_QUESTIONS = "speak_questions"
    SPEAK_REMINDER_PROPOSAL = "speak_reminder_proposal"
    SPEAK_REMINDER_ADDED = "speak_reminder_added"
    SPEAK_NO_REMINDER_TOPIC = "speak_no_reminder_topic"
    SPEAK_NOT_FOUND = "speak_not_found"
    SPEAK_REFUSED = "speak_refused"
    SPEAK_DATA_DELETED = "speak_data_deleted"
    SPEAK_FALLBACK = "speak_fallback"
    SPEAK_DECLINED = "speak_declined"
    SPEAK_UNAVAILABLE = "speak_unavailable"
    PHRASE_EVENT = "phrase_event"
    PHRASE_EVENT_UNDATED = "phrase_event_undated"
    PHRASE_FOLLOW_UP = "phrase_follow_up"
    PHRASE_FOLLOW_UP_INTERVAL = "phrase_follow_up_interval"
    PHRASE_FOLLOW_UP_DATE = "phrase_follow_up_date"
    PHRASE_MONITORING = "phrase_monitoring"
    PHRASE_MONITORING_UNDATED = "phrase_monitoring_undated"
    PHRASE_MED_CONTINUE = "phrase_med_continue"
    PHRASE_MED_START = "phrase_med_start"
    PHRASE_MED_STOP = "phrase_med_stop"
    PHRASE_MED_HOLD = "phrase_med_hold"
    PHRASE_MED_RESUME = "phrase_med_resume"
    PHRASE_MED_PLAIN = "phrase_med_plain"
    PHRASE_STARTING = "phrase_starting"
    PHRASE_UNTIL = "phrase_until"
    PHRASE_FOR_CONTEXT = "phrase_for_context"
