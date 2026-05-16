"""Tests for error handling and exit code mapping (_errors.py).

Covers:
- Exit code mapping for every SDK exception type
- Error message content (keywords agents/users rely on)
- JSON mode structured error output format
- Rich (non-JSON) mode output
- Network/connection and timeout errors
- Server errors (500 via AttioAPIError)
- Suggestion text appended to messages
- Multiple CLI commands (list, get, create, delete)
- No-API-key path
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio._exceptions import (
    AttioAPIError,
    AttioConnectionError,
    AttioPermissionError,
    AttioTimeoutError,
    AttioValidationError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
)
from attio_cli._errors import (
    EXIT_AUTH,
    EXIT_CONFLICT,
    EXIT_ERROR,
    EXIT_NOT_FOUND,
    EXIT_PERMISSION,
    EXIT_RATE_LIMIT,
    EXIT_SUCCESS,
    EXIT_USAGE,
    EXIT_VALIDATION,
)
from attio_cli.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_client_raising(attr_chain: str, exception: Exception):
    """Return a patched get_client context manager whose sub-client raises *exception*.

    *attr_chain* is a dotted path like ``"people.list"`` resolved on the mock client.
    """
    parts = attr_chain.split(".")
    mock_client = MagicMock()
    target = mock_client
    for part in parts[:-1]:
        target = getattr(target, part)
    getattr(target, parts[-1]).side_effect = exception
    return patch(
        "attio_cli.commands._record_factory.get_client",
        return_value=mock_client,
    )


def _parse_json_error(output: str) -> dict:
    """Parse the JSON error envelope from CLI output."""
    return json.loads(output)


# ===================================================================
# 1. Exit code mapping (extends original tests with message checks)
# ===================================================================


class TestExitCodeMapping:
    """Test that SDK exceptions map to the correct exit codes."""

    def test_auth_error_exit_code(self):
        """AuthenticationError should produce exit code 3."""
        with _mock_client_raising(
            "people.list",
            AuthenticationError("Invalid API key", status_code=401),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_AUTH

    def test_not_found_exit_code(self):
        """NotFoundError should produce exit code 5."""
        with _mock_client_raising(
            "people.get",
            NotFoundError("Not found", status_code=404),
        ):
            result = runner.invoke(app, ["--json", "people", "get", "nonexistent"])
            assert result.exit_code == EXIT_NOT_FOUND

    def test_permission_error_exit_code(self):
        """AttioPermissionError should produce exit code 4."""
        with _mock_client_raising(
            "people.list",
            AttioPermissionError("Forbidden", status_code=403),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_PERMISSION

    def test_validation_error_exit_code(self):
        """AttioValidationError should produce exit code 8."""
        with _mock_client_raising(
            "people.create",
            AttioValidationError("Bad request", status_code=400),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"name": "test"}'],
            )
            assert result.exit_code == EXIT_VALIDATION

    def test_conflict_error_exit_code(self):
        """ConflictError should produce exit code 6."""
        with _mock_client_raising(
            "people.create",
            ConflictError("Conflict", status_code=409),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"name": "test"}'],
            )
            assert result.exit_code == EXIT_CONFLICT

    def test_rate_limit_error_exit_code(self):
        """RateLimitError should produce exit code 7."""
        with _mock_client_raising(
            "people.list",
            RateLimitError(retry_after=30.0),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_RATE_LIMIT

    def test_generic_error_exit_code(self):
        """Unknown exceptions should produce exit code 1."""
        with _mock_client_raising(
            "people.list",
            RuntimeError("Something broke"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_ERROR


# ===================================================================
# 2. Error message content
# ===================================================================


class TestErrorMessageContent:
    """Verify that error output contains the keywords agents rely on."""

    def test_auth_error_message_includes_authentication(self):
        """Auth error output should mention authentication-related guidance."""
        with _mock_client_raising(
            "people.list",
            AuthenticationError("Invalid API key", status_code=401),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "api key" in msg

    def test_permission_error_message_includes_permission(self):
        """Permission error output should mention 'permission' or 'scopes'."""
        with _mock_client_raising(
            "people.list",
            AttioPermissionError("Forbidden", status_code=403),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "permission" in msg

    def test_not_found_error_message_includes_not_found(self):
        """Not-found error output should mention 'not found'."""
        with _mock_client_raising(
            "people.get",
            NotFoundError("Person not found", status_code=404),
        ):
            result = runner.invoke(app, ["--json", "people", "get", "bad-id"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "not found" in msg

    def test_rate_limit_message_includes_retry_info(self):
        """Rate-limit error should mention retry timing."""
        with _mock_client_raising(
            "people.list",
            RateLimitError(retry_after=42.0),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"]
            assert "42.0" in msg
            assert "etry" in msg.lower()  # "Retry" or "retry"

    def test_validation_error_preserves_details(self):
        """Validation error should include the API's error detail."""
        detail = "Field 'email' must be a valid email address"
        with _mock_client_raising(
            "people.create",
            AttioValidationError(detail, status_code=400),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"email": "bad"}'],
            )
            body = _parse_json_error(result.output)
            msg = body["error"]["message"]
            assert detail in msg

    def test_conflict_error_message(self):
        """Conflict error should mention 'conflict' or 'already exist'."""
        with _mock_client_raising(
            "people.create",
            ConflictError("Resource already exists", status_code=409),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"name": "dup"}'],
            )
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "already exist" in msg or "conflict" in msg


# ===================================================================
# 3. Suggestion text
# ===================================================================


class TestSuggestionText:
    """Verify the actionable suggestion is appended to each error type."""

    def test_auth_suggestion_mentions_login(self):
        with _mock_client_raising(
            "people.list",
            AuthenticationError("Unauthorized", status_code=401),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"]
            assert "attio auth login" in msg

    def test_permission_suggestion_mentions_scopes(self):
        with _mock_client_raising(
            "people.list",
            AttioPermissionError("Forbidden", status_code=403),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "scope" in msg

    def test_not_found_suggestion_mentions_verify(self):
        with _mock_client_raising(
            "people.get",
            NotFoundError("Not found", status_code=404),
        ):
            result = runner.invoke(app, ["--json", "people", "get", "abc"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "verify" in msg

    def test_rate_limit_suggestion_includes_seconds(self):
        with _mock_client_raising(
            "people.list",
            RateLimitError(retry_after=15.0),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"]
            assert "15.0s" in msg

    def test_validation_suggestion_mentions_input(self):
        with _mock_client_raising(
            "people.create",
            AttioValidationError("invalid", status_code=400),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"x": 1}'],
            )
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "input" in msg

    def test_connection_error_suggestion_mentions_network(self):
        with _mock_client_raising(
            "people.list",
            AttioConnectionError("Connection refused"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "network" in msg

    def test_timeout_error_suggestion_mentions_try_again(self):
        with _mock_client_raising(
            "people.list",
            AttioTimeoutError("Request timed out"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "timed out" in msg or "try again" in msg


# ===================================================================
# 4. JSON mode structured error format
# ===================================================================


class TestJsonErrorFormat:
    """In JSON mode, errors must be a parseable JSON envelope on output."""

    def test_json_envelope_has_error_key(self):
        """JSON error output must have an 'error' key with a 'message' sub-key."""
        with _mock_client_raising(
            "people.list",
            AuthenticationError("bad key", status_code=401),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            assert "error" in body
            assert "message" in body["error"]
            assert isinstance(body["error"]["message"], str)

    def test_json_output_is_single_object(self):
        """JSON error output should be exactly one JSON object, no extra text."""
        with _mock_client_raising(
            "people.get",
            NotFoundError("gone", status_code=404),
        ):
            result = runner.invoke(app, ["--json", "people", "get", "x"])
            # Should parse without leftover data
            stripped = result.output.strip()
            body = json.loads(stripped)
            assert isinstance(body, dict)

    def test_json_error_does_not_contain_rich_markup(self):
        """JSON error output must not leak Rich markup like [red] or [bold]."""
        with _mock_client_raising(
            "people.list",
            AttioPermissionError("Forbidden", status_code=403),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert "[red" not in result.output
            assert "[bold" not in result.output


# ===================================================================
# 5. Rich (non-JSON) mode output
# ===================================================================


class TestRichModeOutput:
    """When not in JSON mode, errors should be human-readable plain text."""

    def _invoke_rich(self, cli_args, exception):
        """Invoke CLI with is_json_mode forced False to test Rich path."""
        attr = cli_args[-1]  # last part is usually the subcommand
        with _mock_client_raising(
            "people.list",
            exception,
        ), patch("attio_cli._output.is_json_mode", return_value=False):
            return runner.invoke(app, ["people", "list"])

    def test_rich_auth_error_shows_error_prefix(self):
        result = self._invoke_rich(
            ["people", "list"],
            AuthenticationError("Invalid API key", status_code=401),
        )
        assert result.exit_code == EXIT_AUTH
        assert "Error:" in result.output
        assert "Invalid API key" in result.output

    def test_rich_not_found_error(self):
        with _mock_client_raising(
            "people.get",
            NotFoundError("Person not found", status_code=404),
        ), patch("attio_cli._output.is_json_mode", return_value=False):
            result = runner.invoke(app, ["people", "get", "bad-id"])
        assert result.exit_code == EXIT_NOT_FOUND
        assert "Person not found" in result.output

    def test_rich_output_does_not_contain_json_envelope(self):
        """Rich mode should not wrap errors in {"error": ...}."""
        with _mock_client_raising(
            "people.list",
            AttioPermissionError("Forbidden", status_code=403),
        ), patch("attio_cli._output.is_json_mode", return_value=False):
            result = runner.invoke(app, ["people", "list"])
        assert '{"error"' not in result.output


# ===================================================================
# 6. Network / connection / timeout errors
# ===================================================================


class TestNetworkErrors:
    """Connection and timeout errors map to EXIT_ERROR (1)."""

    def test_connection_error_exit_code(self):
        with _mock_client_raising(
            "people.list",
            AttioConnectionError("Connection refused"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_ERROR

    def test_timeout_error_exit_code(self):
        with _mock_client_raising(
            "people.list",
            AttioTimeoutError("Request timed out"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_ERROR

    def test_connection_error_message_content(self):
        with _mock_client_raising(
            "people.list",
            AttioConnectionError("Could not resolve host"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"]
            assert "Could not resolve host" in msg

    def test_timeout_error_message_content(self):
        with _mock_client_raising(
            "people.list",
            AttioTimeoutError("Read timed out after 30s"),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"]
            assert "timed out" in msg.lower()


# ===================================================================
# 7. Server errors (500 via AttioAPIError)
# ===================================================================


class TestServerError:
    """Generic AttioAPIError (e.g. 500) should map to EXIT_ERROR."""

    def test_500_server_error_exit_code(self):
        with _mock_client_raising(
            "people.list",
            AttioAPIError("Internal server error", status_code=500),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_ERROR

    def test_502_bad_gateway_exit_code(self):
        with _mock_client_raising(
            "people.list",
            AttioAPIError("Bad gateway", status_code=502),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_ERROR

    def test_server_error_message_preserved(self):
        with _mock_client_raising(
            "people.list",
            AttioAPIError("Internal server error", status_code=500),
        ):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            assert "Internal server error" in body["error"]["message"]


# ===================================================================
# 8. Errors through different CLI commands
# ===================================================================


class TestErrorsThroughCommands:
    """Verify error propagation through different command paths."""

    def test_get_with_not_found(self):
        """'people get <bad-id>' with a 404 should produce exit 5."""
        with _mock_client_raising(
            "people.get",
            NotFoundError("Record not found", status_code=404),
        ):
            result = runner.invoke(app, ["--json", "people", "get", "nonexistent-id"])
            assert result.exit_code == EXIT_NOT_FOUND
            body = _parse_json_error(result.output)
            assert "not found" in body["error"]["message"].lower()

    def test_create_with_validation_error(self):
        """'people create' with invalid values should produce exit 8."""
        with _mock_client_raising(
            "people.create",
            AttioValidationError(
                "email_addresses: must be a valid email", status_code=400
            ),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"email_addresses": "bad"}'],
            )
            assert result.exit_code == EXIT_VALIDATION
            body = _parse_json_error(result.output)
            assert "email" in body["error"]["message"].lower()

    def test_delete_with_not_found(self):
        """'people delete' on a missing record should produce exit 5."""
        with _mock_client_raising(
            "people.delete",
            NotFoundError("Record not found", status_code=404),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "delete", "gone-id", "--yes"],
            )
            assert result.exit_code == EXIT_NOT_FOUND

    def test_list_with_rate_limit(self):
        """'companies list' hitting rate limit should produce exit 7."""
        with _mock_client_raising(
            "companies.list",
            RateLimitError(retry_after=60.0),
        ):
            result = runner.invoke(app, ["--json", "companies", "list"])
            assert result.exit_code == EXIT_RATE_LIMIT
            body = _parse_json_error(result.output)
            assert "60.0" in body["error"]["message"]

    def test_update_with_permission_error(self):
        """'people update' with a 403 should produce exit 4."""
        with _mock_client_raising(
            "people.update",
            AttioPermissionError("Insufficient scopes", status_code=403),
        ):
            result = runner.invoke(
                app,
                ["--json", "people", "update", "rec-1", "--values", '{"name": "x"}'],
            )
            assert result.exit_code == EXIT_PERMISSION


# ===================================================================
# 9. No API key
# ===================================================================


class TestNoApiKey:
    """Test behavior when no API key is configured."""

    def test_no_api_key_exit_code(self):
        """Missing API key should produce exit code 3."""
        with patch("attio_cli._client.get_api_key", return_value=None):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_AUTH

    def test_no_api_key_message_mentions_api_key(self):
        """Missing API key message should tell the user what to do."""
        with patch("attio_cli._client.get_api_key", return_value=None):
            result = runner.invoke(app, ["--json", "people", "list"])
            body = _parse_json_error(result.output)
            msg = body["error"]["message"].lower()
            assert "api key" in msg or "attio_api_key" in msg

    def test_no_api_key_in_rich_mode(self):
        """Missing API key in Rich mode should show readable error."""
        with patch("attio_cli._client.get_api_key", return_value=None), \
             patch("attio_cli._output.is_json_mode", return_value=False):
            result = runner.invoke(app, ["people", "list"])
            assert result.exit_code == EXIT_AUTH
            assert "API key" in result.output or "api key" in result.output.lower()


# ===================================================================
# 10. Exit code constant values
# ===================================================================


class TestExitCodeConstants:
    """Verify the numeric values of exit code constants match the specification."""

    def test_exit_success(self):
        assert EXIT_SUCCESS == 0

    def test_exit_error(self):
        assert EXIT_ERROR == 1

    def test_exit_usage(self):
        assert EXIT_USAGE == 2

    def test_exit_auth(self):
        assert EXIT_AUTH == 3

    def test_exit_permission(self):
        assert EXIT_PERMISSION == 4

    def test_exit_not_found(self):
        assert EXIT_NOT_FOUND == 5

    def test_exit_conflict(self):
        assert EXIT_CONFLICT == 6

    def test_exit_rate_limit(self):
        assert EXIT_RATE_LIMIT == 7

    def test_exit_validation(self):
        assert EXIT_VALIDATION == 8
