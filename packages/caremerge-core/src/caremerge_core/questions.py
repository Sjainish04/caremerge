"""User-facing text templates (principle P9: the model reads, templates write).

Every sentence CareMerge shows about a person's care is rendered here from
structured values. Rendering fails loudly when parameters don't match the
template, so a template can never be filled with the wrong fields.
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
