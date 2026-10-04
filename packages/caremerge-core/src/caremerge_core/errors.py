"""Base error type for CareMerge core.

Specific errors live next to the code that raises them, such as
``TemplateError`` in ``questions`` and ``PolicyViolationError`` in ``policy``.
"""


class CareMergeError(Exception):
    """Base class for errors raised by caremerge-core."""
