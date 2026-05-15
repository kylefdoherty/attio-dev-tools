"""Tests for the meetings commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from attio_cli.commands.meetings import app as meetings_app

runner = CliRunner()

# Create a test app with the meetings command group registered.
app = typer.Typer()
app.add_typer(meetings_app, name="meetings")


@app.callback()
def _main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output


def _make_mock_meeting(meeting_id="mtg_123", title="Weekly Sync", num_participants=3):
    """Create a mock Meeting model."""
    m = MagicMock()
    m.id = MagicMock()
    m.id.meeting_id = meeting_id
    m.title = title
    m.description = "A weekly sync meeting"
    m.start_time = "2026-01-15T10:00:00Z"
    m.end_time = "2026-01-15T11:00:00Z"
    m.participants = [MagicMock() for _ in range(num_participants)]
    m.linked_records = []
    m.created_at = "2026-01-01T00:00:00Z"
    return m


class TestMeetingsList:
    """Test the meetings list command."""

    def test_list_json(self):
        """meetings list --json should return meetings."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_meeting("mtg_1", "Standup"),
            _make_mock_meeting("mtg_2", "Design Review"),
        ]

        with patch("attio_cli.commands.meetings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.meetings.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "meetings", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["title"] == "Standup"

    def test_list_with_filters(self):
        """meetings list with filters should pass them to the SDK."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_meeting()]

        with patch("attio_cli.commands.meetings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.meetings.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "meetings", "list",
                    "--object", "people",
                    "--record", "rec_123",
                    "--sort", "start_time",
                ],
            )
            assert result.exit_code == 0
            mock_client.meetings.list.assert_called_once_with(
                limit=None,
                cursor=None,
                linked_object="people",
                linked_record_id="rec_123",
                participants=None,
                sort="start_time",
                ends_from=None,
                starts_before=None,
                timezone=None,
            )

    def test_list_with_participants(self):
        """meetings list --participants should split comma-separated emails."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_meeting()]

        with patch("attio_cli.commands.meetings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.meetings.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "meetings", "list", "--participants", "alice@co.com,bob@co.com"],
            )
            assert result.exit_code == 0
            call_kwargs = mock_client.meetings.list.call_args[1]
            assert call_kwargs["participants"] == ["alice@co.com", "bob@co.com"]


class TestMeetingsGet:
    """Test the meetings get command."""

    def test_get_by_id(self):
        """meetings get should return a meeting by ID."""
        mock_meeting = _make_mock_meeting()

        with patch("attio_cli.commands.meetings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.meetings.get.return_value = mock_meeting
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "meetings", "get", "mtg_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["id"] == "mtg_123"
            assert parsed["data"]["title"] == "Weekly Sync"

    def test_get_untitled_meeting(self):
        """meetings get with no title should display (untitled)."""
        mock_meeting = _make_mock_meeting(title=None)

        with patch("attio_cli.commands.meetings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.meetings.get.return_value = mock_meeting
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "meetings", "get", "mtg_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["title"] == "(untitled)"
