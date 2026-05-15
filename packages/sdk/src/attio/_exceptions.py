"""Exception hierarchy for the Attio SDK."""

from __future__ import annotations

from typing import Any

import httpx


class AttioError(Exception):
    """Base exception for all Attio SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 0,
        code: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.body = body


class AttioAPIError(AttioError):
    """Raised for non-2xx responses from the Attio API."""


class RateLimitError(AttioAPIError):
    """Raised when HTTP 429 and all retries are exhausted."""

    def __init__(self, retry_after: float, *, body: Any = None) -> None:
        super().__init__(
            f"Rate limited. Retry after {retry_after}s",
            status_code=429,
            code="rate_limit_exceeded",
            body=body,
        )
        self.retry_after = retry_after


class AuthenticationError(AttioAPIError):
    """Raised for 401 Unauthorized."""


class AttioPermissionError(AttioAPIError):
    """Raised for 403 Forbidden (missing required scopes)."""


class NotFoundError(AttioAPIError):
    """Raised for 404 Not Found."""


class ConflictError(AttioAPIError):
    """Raised for 409 Conflict."""


class AttioValidationError(AttioAPIError):
    """Raised for 400 Bad Request with validation errors."""


class AttioConnectionError(AttioError):
    """Raised for network/connection failures."""


class AttioTimeoutError(AttioError):
    """Raised when a request times out."""


_STATUS_CODE_TO_EXCEPTION: dict[int, type[AttioAPIError]] = {
    400: AttioValidationError,
    401: AuthenticationError,
    403: AttioPermissionError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


def _extract_error_info(response: httpx.Response) -> tuple[str, str | None, Any]:
    """Extract message, code, and body from an error response."""
    body: Any = None
    message = f"Attio API error {response.status_code}"
    code: str | None = None

    try:
        body = response.json()
    except Exception:
        body = response.text or None

    if isinstance(body, dict):
        if isinstance(body.get("message"), str):
            message = body["message"]
        elif isinstance(body.get("error"), str):
            message = body["error"]
        if isinstance(body.get("code"), str):
            code = body["code"]

    return message, code, body


def _raise_for_status(response: httpx.Response) -> None:
    """Inspect an HTTP response and raise the appropriate exception for non-2xx status codes."""
    if response.is_success:
        return

    message, code, body = _extract_error_info(response)
    status_code = response.status_code

    # Special handling for 429: extract retry_after
    if status_code == 429:
        retry_after_header = response.headers.get("retry-after")
        retry_after = float(retry_after_header) if retry_after_header else 1.0
        raise RateLimitError(retry_after, body=body)

    exc_class = _STATUS_CODE_TO_EXCEPTION.get(status_code, AttioAPIError)
    raise exc_class(
        message,
        status_code=status_code,
        code=code,
        body=body,
    )
