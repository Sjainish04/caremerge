"""Smoke test: the package imports and documents itself."""

import caremerge_core


def test_package_has_a_docstring() -> None:
    assert caremerge_core.__doc__
