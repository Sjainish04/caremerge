"""Recognize a spoken yes or no without a model (spec §11, turn rules).

Only whole, short answers count, so "yes, but only the procedure" is not a
yes: anything else goes back to the orchestrator and cancels the pending
change.
"""

import re
from typing import Final, Literal

_YES: Final = frozenset(
    {"yes", "yeah", "yep", "sure", "go ahead", "please do", "do it", "ok", "okay", "yes please"}
)
_NO: Final = frozenset({"no", "nope", "not now", "cancel", "no thanks", "never mind", "dont"})
_PUNCTUATION: Final = re.compile(r"[^\w\s]")


def classify_answer(text: str) -> Literal["yes", "no"] | None:
    """Return ``"yes"`` or ``"no"`` for a bare answer, otherwise ``None``."""
    words = _PUNCTUATION.sub("", text.casefold()).split()
    if words[:1] == ["alexa"]:
        words = words[1:]
    said = " ".join(words)
    if said in _YES:
        return "yes"
    if said in _NO:
        return "no"
    return None
