"""Tests for error handling and exit code mapping (_errors.py)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli._errors import (
    EXIT_AUTH,
    EXIT_CONFLICT,
    EXIT_ERROR,
    EXIT_NOT_FOUND,
    EXIT_PERMISSION,
    EXIT_RATE_LIMIT,
    EXIT_VALIDATION,
)
from attio_cli.main import app

runner = CliRunner()


class TestExitCodeMapping:
    """Test that SDK exceptions map to the correct exit codes."""

    def test_auth_error_exit_code(self):
        """AuthenticationError should produce exit code 3."""
        from attio._exceptions import AuthenticationError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.side_effect = AuthenticationError(
                "Invalid API key", status_code=401
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_AUTH

    def test_not_found_exit_code(self):
        """NotFoundError should produce exit code 5."""
        from attio._exceptions import NotFoundError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.get.side_effect = NotFoundError(
                "Not found", status_code=404
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "get", "nonexistent"])
            assert result.exit_code == EXIT_NOT_FOUND

    def test_permission_error_exit_code(self):
        """AttioPermissionError should produce exit code 4."""
        from attio._exceptions import AttioPermissionError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.side_effect = AttioPermissionError(
                "Forbidden", status_code=403
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_PERMISSION

    def test_validation_error_exit_code(self):
        """AttioValidationError should produce exit code 8."""
        from attio._exceptions import AttioValidationError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.create.side_effect = AttioValidationError(
                "Bad request", status_code=400
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"name": "test"}'],
            )
            assert result.exit_code == EXIT_VALIDATION

    def test_conflict_error_exit_code(self):
        """ConflictError should produce exit code 6."""
        from attio._exceptions import ConflictError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.create.side_effect = ConflictError(
                "Conflict", status_code=409
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "people", "create", "--values", '{"name": "test"}'],
            )
            assert result.exit_code == EXIT_CONFLICT

    def test_rate_limit_error_exit_code(self):
        """RateLimitError should produce exit code 7."""
        from attio._exceptions import RateLimitError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.side_effect = RateLimitError(
                retry_after=30.0
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_RATE_LIMIT

    def test_generic_error_exit_code(self):
        """Unknown exceptions should produce exit code 1."""
        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.side_effect = RuntimeError("Something broke")
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_ERROR


class TestNoApiKey:
    """Test behavior when no API key is configured."""

    def test_no_api_key_exit_code(self):
        """Missing API key should produce exit code 3."""
        with patch("attio_cli._client.get_api_key", return_value=None):
            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == EXIT_AUTH
