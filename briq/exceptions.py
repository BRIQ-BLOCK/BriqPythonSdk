"""
Exception classes for the Briq client.
"""


class BriqError(Exception):
    """Base exception for all Briq-related errors."""


class BriqAuthError(BriqError):
    """Raised when authentication fails."""


class BriqAPIError(BriqError):
    """Raised when the API returns an error."""


class BriqRequestError(BriqError):
    """Raised when a request to the API fails."""


class BriqConfigError(BriqError):
    """Raised when there's a configuration error."""


class BriqValidationError(BriqError):
    """Raised when the API returns a 422 validation error."""

    def __init__(self, message: str, detail: list | None = None) -> None:
        super().__init__(message)
        self.detail: list = detail or []
