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

    def test_login_interactive(self):
        """Login with interactive prompt should validate and save."""
        mock_client_instance = MagicMock()
        mock_info = MagicMock()
        mock_info.workspace_name = "Test Workspace"
        mock_client_instance.self_.identify.return_value = mock_info
        mock_client_instance.close.return_value = None

        with (
            patch("attio.AttioClient", return_value=mock_client_instance),
            patch("attio_cli._config.save_api_key") as mock_save,
        ):
            result = runner.invoke(app, ["auth", "login"], input="test_key_123\n")
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
            result = runner.invoke(app, ["auth", "login"], input="bad_key\n")
            assert result.exit_code != 0

    def test_login_with_1password(self):
        """Login with --1password should resolve via op CLI and save reference."""
        mock_client_instance = MagicMock()
        mock_info = MagicMock()
        mock_info.workspace_name = "1P Workspace"
        mock_client_instance.self_.identify.return_value = mock_info
        mock_client_instance.close.return_value = None

        with (
            patch("attio_cli._config._resolve_1password", return_value="sk_live_from_1password"),
            patch("attio.AttioClient", return_value=mock_client_instance),
            patch("attio_cli._config.save_1password_ref") as mock_save,
        ):
            result = runner.invoke(app, ["auth", "login", "--1password", "op://Vault/Attio/credential"])
            assert result.exit_code == 0
            assert "1Password" in result.output
            mock_save.assert_called_once_with(
                "op://Vault/Attio/credential",
                profile_name="default",
                workspace_name="1P Workspace",
            )

    def test_login_with_1password_op_not_installed(self):
        """Login with --1password should fail gracefully if op CLI is missing."""
        with patch("attio_cli._config._resolve_1password", return_value=None):
            result = runner.invoke(app, ["auth", "login", "--1password", "op://Vault/Attio/credential"])
            assert result.exit_code != 0
            assert "op" in result.output.lower() or "1password" in result.output.lower()


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


class TestOnePasswordIntegration:
    """Test 1Password config integration."""

    def test_resolve_1password_success(self):
        """_resolve_1password should call op read and return the secret."""
        from attio_cli._config import _resolve_1password

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "sk_live_secret_key\n"

        with patch("attio_cli._config.subprocess.run", return_value=mock_result) as mock_run:
            result = _resolve_1password("op://Vault/Attio/credential")
            assert result == "sk_live_secret_key"
            mock_run.assert_called_once_with(
                ["op", "read", "op://Vault/Attio/credential"],
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_resolve_1password_op_not_found(self):
        """_resolve_1password should return None if op is not installed."""
        from attio_cli._config import _resolve_1password

        with patch("attio_cli._config.subprocess.run", side_effect=FileNotFoundError):
            result = _resolve_1password("op://Vault/Attio/credential")
            assert result is None

    def test_resolve_1password_op_error(self):
        """_resolve_1password should return None if op returns non-zero."""
        from attio_cli._config import _resolve_1password

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("attio_cli._config.subprocess.run", return_value=mock_result):
            result = _resolve_1password("op://Vault/Attio/credential")
            assert result is None

    def test_get_api_key_from_1password_profile(self):
        """get_api_key should resolve op_reference from profile config."""
        from attio_cli._config import get_api_key

        config = {
            "active_profile": "default",
            "profiles": {
                "default": {"op_reference": "op://Vault/Attio/credential"},
            },
        }
        with (
            patch("attio_cli._config._read_config", return_value=config),
            patch("attio_cli._config._resolve_1password", return_value="sk_live_resolved") as mock_op,
        ):
            result = get_api_key()
            assert result == "sk_live_resolved"
            mock_op.assert_called_once_with("op://Vault/Attio/credential")
