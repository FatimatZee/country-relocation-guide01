"""Custom exceptions for expected Country Compass failures."""


class CountryCompassError(Exception):
    """Base class for errors that can be shown clearly in the app interface."""


class CountryAPIError(CountryCompassError):
    """Raised when REST Countries cannot provide usable data."""


class StorageError(CountryCompassError):
    """Raised when saved JSON data cannot be read or written."""


class GuideGenerationError(CountryCompassError):
    """Raised when an AI relocation guide cannot be generated."""

