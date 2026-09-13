"""
Exception classes for the Briq client.
"""

from __future__ import annotations


class BriqError(Exception):
    """Base exception for all Briq-related errors."""


class BriqAuthError(BriqError):
    """Raised when authentication fails."""


class BriqAPIError(BriqError):
    """Raised when the API returns an error.

    Envelope failures (``{success, data, errors, request_id}``) populate
    ``code``, ``errors``, ``request_id``, and ``data`` so callers can branch
    on ``errors[0].code`` without parsing the message string (Email codes
    such as ``INSUFFICIENT_ALLOCATION``, WhatsApp ``WINDOW_CLOSED``, etc.).
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        code: str | None = None,
        errors: list | None = None,
        request_id: str | None = None,
        data: dict | None = None,
        body: dict | list | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code: int | None = status_code
        self.code: str | None = code
        self.errors: list = errors or []
        self.request_id: str | None = request_id
        self.data: dict | None = data
        self.body: dict | list | None = body

    @classmethod
    def from_envelope(cls, body: dict, status_code: int) -> BriqAPIError:
        """Build an error from a Karibu ``{success, data, errors, request_id}`` body."""
        errors = body.get("errors") or []
        first = errors[0] if errors and isinstance(errors[0], dict) else {}
        code = first.get("code")
        message = first.get("message") or f"API error: {code or status_code}"
        data = body.get("data")
        return cls(
            message,
            status_code=status_code,
            code=code,
            errors=errors if isinstance(errors, list) else [],
            request_id=body.get("request_id"),
            data=data if isinstance(data, dict) else None,
            body=body,
        )


class BriqRequestError(BriqError):
    """Raised when a request to the API fails."""


class BriqConfigError(BriqError):
    """Raised when there's a configuration error."""


class BriqValidationError(BriqError):
    """Raised when the API returns a 422 validation error."""

    def __init__(self, message: str, detail: list | None = None) -> None:
        super().__init__(message)
        self.detail: list = detail or []
