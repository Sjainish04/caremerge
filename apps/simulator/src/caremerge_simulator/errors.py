"""Errors raised by the simulator host."""


class SimulatorError(Exception):
    """Base class for simulator errors."""


class AddonUnavailableError(SimulatorError):
    """Raised when the CareMerge add-on cannot be reached or does not answer in time."""


class UnknownConfirmationError(SimulatorError):
    """Raised when a confirmation refers to nothing pending, or to something already resolved."""
