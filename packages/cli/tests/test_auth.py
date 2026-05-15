"""Tests for auth commands (login, logout, status)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


class TestAuthLogin:
    """Test the auth login command."""

    def test_login_with_api_key_flag(self):
        """Login with --api-key flag should validate and save."""
        mock_client_instance = MagicMock()
        mock_info = MagicMock()
        mock_info.workspace_name = "Test Workspace"
        mock_client_instance.self_.identify.return_value = mock_info
        mock_client_instance.close.return_value = None

        with (
            patch("attio.AttioClient", return_value=mock_client_instance),
            patch("attio_cli._config.save_api_key") as mock_save,
        ):
            result = runner.invoke(app, ["auth", "login", "--api-key", "test_key_123"])
            assert result.exit_code == 0
            mock_save.assert_called_once_with(
                "test_key_123",
                profile_name="default",
                workspace_name="Test Workspace",
            )

    def test_login_with_invalid_key(self):
        """Login with invalid key should exit with error."""
        from attio._exceptions import AuthenticationError

        with patch(
            "attio.AttioClient",
            side_effect=AuthenticationError("Unauthorized", status_code=401),
        ):
            result = runner.invoke(app, ["auth", "login", "--api-key", "bad_key"])
            assert result.exit_code != 0


class TestAuthLogout:
    """Test the auth logout command."""

    def test_logout_with_stored_creds(self):
        """Logout should remove stored credentials."""
        with patch("attio_cli._config.remove_api_key", return_value=True):
            result = runner.invoke(app, ["auth", "logout"])
            assert result.exit_code == 0

    def test_logout_no_stored_creds(self):
        """Logout with no stored credentials should report error."""
        with patch("attio_cli._config.remove_api_key", return_value=False):
            result = runner.invoke(app, ["auth", "logout"])
            assert result.exit_code == 1


class TestAuthStatus:
    """Test the auth status command."""

    def test_status_json(self):
        """Status with --json should output structured data."""
        mock_info = MagicMock()
        mock_info.workspace_name = "Test WS"
        mock_info.workspace_id = "ws_123"
        mock_info.active = True
        mock_info.scope = "record_permission:read"
        mock_info.model_dump.return_value = {
            "workspace_name": "Test WS",
            "workspace_id": "ws_123",
            "active": True,
            "scope": "record_permission:read",
        }

        mock_client = MagicMock()
        mock_client.self_.identify.return_value = mock_info
        mock_client.close.return_value = None

        with (
            patch("attio_cli._client.get_client", return_value=mock_client),
            patch("attio_cli._config.get_active_profile_name", return_value="default"),
        ):
            result = runner.invoke(app, ["--json", "auth", "status"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["workspace_name"] == "Test WS"
