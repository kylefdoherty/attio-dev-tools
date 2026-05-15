"""Error handling and semantic exit code mapping for the Attio CLI.

Maps SDK exceptions to structured error output with meaningful exit codes
so agents can branch on failure modes without parsing error messages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typer

# Semantic exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_AUTH = 3
EXIT_PERMISSION = 4
EXIT_NOT_FOUND = 5
EXIT_CONFLICT = 6
EXIT_RATE_LIMIT = 7
EXIT_VALIDATION = 8


def handle_api_error(e: Exception, ctx: typer.Context) -> None:
    """Map SDK exceptions to semantic exit codes and formatted output.

    Catches all Attio SDK exception types and routes them to output_error
    with the appropriate exit code.
    """
    from attio._exceptions import (
        AttioConnectionError,
        AttioPermissionError,
        AttioTimeoutError,
        AttioValidationError,
        AuthenticationError,
        ConflictError,
        NotFoundError,
        RateLimitError,
    )
    from attio_cli._output import output_error

    if isinstance(e, AuthenticationError):
        exit_code = EXIT_AUTH
        suggestion = "Check your API key or run 'attio auth login'."
    elif isinstance(e, AttioPermissionError):
        exit_code = EXIT_PERMISSION
        suggestion = "Insufficient permissions. Verify your API key scopes."
    elif isinstance(e, NotFoundError):
        exit_code = EXIT_NOT_FOUND
        suggestion = "Resource not found. Verify the ID and object type."
    elif isinstance(e, ConflictError):
        exit_code = EXIT_CONFLICT
        suggestion = "Resource conflict. The resource may already exist."
    elif isinstance(e, RateLimitError):
        exit_code = EXIT_RATE_LIMIT
        suggestion = f"Rate limited. Retry after {e.retry_after}s."
    elif isinstance(e, AttioValidationError):
        exit_code = EXIT_VALIDATION
        suggestion = "Validation error. Check your input values."
    elif isinstance(e, AttioConnectionError):
        exit_code = EXIT_ERROR
        suggestion = "Connection failed. Check your network."
    elif isinstance(e, AttioTimeoutError):
        exit_code = EXIT_ERROR
        suggestion = "Request timed out. Try again."
    else:
        exit_code = EXIT_ERROR
        suggestion = ""

    message = str(e)
    if suggestion:
        message = f"{message}\n{suggestion}"

    output_error(message, ctx, exit_code=exit_code)
