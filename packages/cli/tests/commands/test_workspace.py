"""Tests for the workspace commands (member get)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_member(member_id="mem_123", first="Jane", last="Doe", email="jane@example.com"):
    """Create a mock workspace member for testing."""
    member = MagicMock()
    member.id = MagicMock()
    member.id.workspace_member_id = member_id
    member.first_name = first
    member.last_name = last
    member.email_address = email
    member.access_level = "member"
    member.avatar_url = "https://example.com/avatar.png"
    member.created_at = "2026-01-01T00:00:00Z"
    return member


class TestWorkspaceMember:
    """Test the workspace member command."""

    def test_member_json_output(self):
        """workspace member --json should return member details."""
        mock_member = _make_mock_member()

        with patch("attio_cli.commands.workspace.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.workspace_members.get.return_value = mock_member
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "workspace", "member", "mem_123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["member_id"] == "mem_123"
            assert parsed["data"]["name"] == "Jane Doe"
            assert parsed["data"]["email_address"] == "jane@example.com"
            assert parsed["data"]["access_level"] == "member"
            mock_client.workspace_members.get.assert_called_once_with("mem_123")

    def test_member_not_found(self):
        """workspace member with bad ID should return exit code 5."""
        from attio._exceptions import NotFoundError

        with patch("attio_cli.commands.workspace.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.workspace_members.get.side_effect = NotFoundError(
                "Not found", status_code=404
            )
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "workspace", "member", "bad_id"]
            )
            assert result.exit_code == 5
