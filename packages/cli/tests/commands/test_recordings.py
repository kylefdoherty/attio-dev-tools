"""Tests for the recordings commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from attio_cli.commands.recordings import app as recordings_app

runner = CliRunner()

# Create a test app with the recordings command group registered.
app = typer.Typer()
app.add_typer(recordings_app, name="recordings")


@app.callback()
def _main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output


def _make_mock_recording(recording_id="rec_123", status="completed"):
    """Create a mock CallRecording model."""
    r = MagicMock()
    r.id = MagicMock()
    r.id.call_recording_id = recording_id
    r.meeting_id = "mtg_123"
    r.status = status
    r.web_url = "https://app.attio.com/recordings/rec_123"
    r.created_at = "2026-01-01T00:00:00Z"
    return r


class TestRecordingsList:
    """Test the recordings list command."""

    def test_list_json(self):
        """recordings list --meeting should return recordings."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_recording("rec_1", "completed"),
            _make_mock_recording("rec_2", "processing"),
        ]

        with patch("attio_cli.commands.recordings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.call_recordings.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "recordings", "list", "--meeting", "mtg_123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["status"] == "completed"

    def test_list_calls_sdk_correctly(self):
        """recordings list should pass meeting_id to the SDK."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_recording()]

        with patch("attio_cli.commands.recordings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.call_recordings.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "recordings", "list", "--meeting", "mtg_456"]
            )
            assert result.exit_code == 0
            mock_client.call_recordings.list.assert_called_once_with(
                "mtg_456",
                limit=None,
                cursor=None,
            )

    def test_list_missing_meeting_fails(self):
        """recordings list without --meeting should fail."""
        result = runner.invoke(app, ["--json", "recordings", "list"])
        assert result.exit_code != 0


class TestRecordingsGet:
    """Test the recordings get command."""

    def test_get_by_id(self):
        """recordings get should return a recording by ID."""
        mock_recording = _make_mock_recording()

        with patch("attio_cli.commands.recordings.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.call_recordings.get.return_value = mock_recording
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "recordings", "get", "rec_123", "--meeting", "mtg_123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["id"] == "rec_123"
            assert parsed["data"]["status"] == "completed"
