"""Tests for the statuses commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_status(status_id="stat_123", title="In Progress", celebration=False, target_time=None):
    """Create a mock Status model."""
    status = MagicMock()
    status.id = MagicMock()
    status.id.status_id = status_id
    status.title = title
    status.is_archived = False
    status.celebration_enabled = celebration
    status.target_time_in_status = target_time
    return status


class TestStatusesList:
    """Test the statuses list command."""

    def test_list_with_object(self):
        """statuses list --object should return statuses."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_status("stat_1", "Open"),
            _make_mock_status("stat_2", "Closed", True),
        ]

        with patch("attio_cli.commands.statuses.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.statuses.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "statuses", "list", "--object", "deals", "--attribute", "deal_status"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["title"] == "Open"
            mock_client.statuses.list.assert_called_once_with("objects", "deals", "deal_status")

    def test_list_with_list(self):
        """statuses list --list should return statuses for a list attribute."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_status()]

        with patch("attio_cli.commands.statuses.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.statuses.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "statuses", "list", "--list", "pipeline", "--attribute", "stage"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            mock_client.statuses.list.assert_called_once_with("lists", "pipeline", "stage")

    def test_list_no_target_fails(self):
        """statuses list without --object or --list should fail."""
        with patch("attio_cli.commands.statuses.get_client") as mock_gc:
            mock_gc.return_value = MagicMock()
            result = runner.invoke(app, ["--json", "statuses", "list", "--attribute", "stage"])
            assert result.exit_code != 0


class TestStatusesCreate:
    """Test the statuses create command."""

    def test_create_status(self):
        """statuses create should return the created status."""
        mock_status = _make_mock_status(status_id="stat_new", title="New Status")

        with patch("attio_cli.commands.statuses.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.statuses.create.return_value = mock_status
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "statuses", "create",
                    "--object", "deals",
                    "--attribute", "deal_status",
                    "--title", "New Status",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["title"] == "New Status"
            mock_client.statuses.create.assert_called_once()

    def test_create_status_with_celebration(self):
        """statuses create --celebration should create with celebration enabled."""
        mock_status = _make_mock_status(status_id="stat_win", title="Won", celebration=True)

        with patch("attio_cli.commands.statuses.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.statuses.create.return_value = mock_status
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "statuses", "create",
                    "--object", "deals",
                    "--attribute", "deal_status",
                    "--title", "Won",
                    "--celebration",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["celebration_enabled"] is True


class TestStatusesUpdate:
    """Test the statuses update command."""

    def test_update_status(self):
        """statuses update should return the updated status."""
        mock_status = _make_mock_status()
        mock_status.title = "Updated Status"

        with patch("attio_cli.commands.statuses.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.statuses.update.return_value = mock_status
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "statuses", "update", "stat_123",
                    "--object", "deals",
                    "--attribute", "deal_status",
                    "--title", "Updated Status",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["title"] == "Updated Status"
            mock_client.statuses.update.assert_called_once()
