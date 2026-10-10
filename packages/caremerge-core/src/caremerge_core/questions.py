"""User-facing text templates (principle P9: the model reads, templates write).

Every sentence CareMerge shows or speaks about a person's care is rendered
here from structured values; the ``speak_`` templates are spoken sentences and
the ``phrase_`` templates are the fragments they are built from. Rendering
fails loudly when parameters don't match the template, so a template can
never be filled with the wrong fields.
"""

from collections.abc import Mapping, Set
from string import Formatter
from types import MappingProxyType
from typing import Final

from caremerge_core.enums import MedAction, TemplateId
from caremerge_core.errors import CareMergeError

TEMPLATES: Final[Mapping[TemplateId, str]] = MappingProxyType(
    {
        TemplateId.L002_MESSAGE: "This temporary change has no captured end.",
        TemplateId.L002_QUESTION: (
            "When should the temporary {action_noun} of {entity} for the {context} end?"
        ),
        TemplateId.L002_QUESTION_NO_CONTEXT: (
            "When should the temporary {action_noun} of {entity} end?"
        ),
        TemplateId.ASK_CARE_TEAM: "Ask your care team: {question}",
        TemplateId.REMIND_VERIFIED_INSTRUCTION: 'Reminder from {source} ({date}): "{quote}"',
        TemplateId.SPEAK_VISIT_UPDATES: (
            "Your visit with {clinician} on {date} has {item_count}: {item_list}. Should I add "
            "{item_pronoun} to your care plan?"
        ),
        TemplateId.SPEAK_NO_VISIT_UPDATES: "There's nothing new to review.",
        TemplateId.SPEAK_ITEMS_ADDED: "Added to your care plan.",
        TemplateId.SPEAK_VISIT_READY: "Your visit with {clinician} on {date} is ready to review.",
        TemplateId.SPEAK_VISIT_ALREADY_ADDED: (
            "Your visit with {clinician} on {date} is already in CareMerge."
        ),
        TemplateId.SPEAK_NO_CHANGES: "Nothing has changed in your care plan since your last visit.",
        TemplateId.SPEAK_CHANGES_INTRO: "Since your last visit, {change_count} in your care plan.",
        TemplateId.SPEAK_CHANGE_STATE: "{subject} goes from {old} to {new}{timing}.",
        TemplateId.SPEAK_CHANGE_DETAIL: (
            "The {dimension} for {subject} goes from {old} to {new}{timing}."
        ),
        TemplateId.SPEAK_CHANGE_NEW: "New: {item}.",
        TemplateId.SPEAK_CHANGE_REMOVED: "{subject} is no longer in your care plan.",
        TemplateId.SPEAK_END_NOT_CAPTURED: "No end was captured.",
        TemplateId.SPEAK_MORE_ON_SCREEN: "There's more on your screen.",
        TemplateId.SPEAK_QUESTIONS_PENDING: "{question_count} {question_verb} clarifying.",
        TemplateId.SPEAK_PLAN_DAY: "On {date}, {subject} is {state} in your care plan{details}.",
        TemplateId.SPEAK_PLAN_EVENT: "Your {subject} is on {date} in your care plan.",
        TemplateId.SPEAK_PLAN_CONFLICT: (
            "On {date}, the captured instructions about {subject} differ. CareMerge won't decide "
            "which applies."
        ),
        TemplateId.SPEAK_PLAN_NOTHING: "Nothing was captured about {subject} for {date}.",
        TemplateId.SPEAK_PLAN_EMPTY: "Nothing in your care plan applies to {date}.",
        TemplateId.SPEAK_PLAN_OVERVIEW: "On {date}, your care plan has {item_list}.",
        TemplateId.SPEAK_SOURCE: "That's from {clinician} on {date}.",
        TemplateId.SPEAK_NOT_DECIDING: (
            "CareMerge isn't deciding what's correct. Check with your care team if you're unsure."
        ),
        TemplateId.SPEAK_NO_QUESTIONS: "There are no open questions right now.",
        TemplateId.SPEAK_QUESTIONS: (
            "{question_count} {question_verb} clarifying: {question_list} I can remind you to ask "
            "your care team."
        ),
        TemplateId.SPEAK_REMINDER_PROPOSAL: "I can remind you {when}: {text} Should I add it?",
        TemplateId.SPEAK_REMINDER_ADDED: "Done. It's in your reminders.",
        TemplateId.SPEAK_NO_REMINDER_TOPIC: "There's no open question to remind you about.",
        TemplateId.SPEAK_NOT_FOUND: "I couldn't find that in your care plan.",
        TemplateId.SPEAK_REFUSED: (
            "I can't do that, because it no longer matches your confirmed care plan."
        ),
        TemplateId.SPEAK_DATA_DELETED: "Your CareMerge data is deleted.",
        TemplateId.SPEAK_FALLBACK: (
            "I can tell you what changed in your care plan, what it says for a day, what still "
            "needs clarifying, or set a reminder to ask your care team."
        ),
        TemplateId.SPEAK_DECLINED: "Okay, I won't change anything.",
        TemplateId.SPEAK_UNAVAILABLE: "CareMerge isn't reachable right now. Try again in a moment.",
        TemplateId.PHRASE_EVENT: "your {subject} on {date}",
        TemplateId.PHRASE_EVENT_UNDATED: "your {subject}",
        TemplateId.PHRASE_FOLLOW_UP: "a follow-up",
        TemplateId.PHRASE_FOLLOW_UP_INTERVAL: "a follow-up in {interval}",
        TemplateId.PHRASE_FOLLOW_UP_DATE: "a follow-up on {date}",
        TemplateId.PHRASE_MONITORING: "checking {subject} on {days}",
        TemplateId.PHRASE_MONITORING_UNDATED: "checking {subject}",
        TemplateId.PHRASE_MED_CONTINUE: "continuing {subject}",
        TemplateId.PHRASE_MED_START: "starting {subject}",
        TemplateId.PHRASE_MED_STOP: "stopping {subject}",
        TemplateId.PHRASE_MED_HOLD: "a hold on {subject}",
        TemplateId.PHRASE_MED_RESUME: "restarting {subject}",
        TemplateId.PHRASE_MED_PLAIN: "{subject}",
        TemplateId.PHRASE_STARTING: "starting {date}",
        TemplateId.PHRASE_UNTIL: "until {end}",
        TemplateId.PHRASE_FOR_CONTEXT: "for your {context}",
    }
)

_ACTION_NOUNS: Final[Mapping[MedAction, str]] = MappingProxyType(
    {
        MedAction.HOLD: "hold",
        MedAction.STOP: "stop",
        MedAction.START: "start",
        MedAction.RESUME: "restart",
        MedAction.CONTINUE: "change",
    }
)


class TemplateError(CareMergeError):
    """Raised when parameters don't match a template's fields."""

    def __init__(self, template_id: TemplateId, missing: Set[str], unexpected: Set[str]) -> None:
        self.template_id = template_id
        self.missing = frozenset(missing)
        self.unexpected = frozenset(unexpected)
        super().__init__(
            f"{template_id}: missing={sorted(missing)} unexpected={sorted(unexpected)}"
        )


def template_fields(template_id: TemplateId) -> frozenset[str]:
    """Return the placeholder names a template requires."""
    return frozenset(field for _, field, _, _ in Formatter().parse(TEMPLATES[template_id]) if field)


def render(template_id: TemplateId, params: Mapping[str, str]) -> str:
    """Render a registered template with exactly its required parameters."""
    expected = template_fields(template_id)
    given = set(params)
    if given != expected:
        raise TemplateError(template_id, missing=expected - given, unexpected=given - expected)
    return TEMPLATES[template_id].format_map(params)


def action_noun(action: MedAction | None) -> str:
    """Return the noun used in questions about a temporary change."""
    return _ACTION_NOUNS[action] if action else "change"
