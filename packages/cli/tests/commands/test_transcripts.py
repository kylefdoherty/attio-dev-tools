"""Tests for the transcripts commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from attio_cli.commands.transcripts import app as transcripts_app

runner = CliRunner()

# Create a test app with the transcripts command group registered.
app = typer.Typer()
app.add_typer(transcripts_app, name="transcripts")


@app.callback()
def _main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output


def _make_mock_segment(speaker="Alice", speech="Hello everyone", start=0.0, end=2.5):
    """Create a mock TranscriptSegment model."""
    s = MagicMock()
    s.speaker = speaker
    s.speech = speech
    s.start_time = start
    s.end_time = end
    return s


class TestTranscriptsGet:
    """Test the transcripts get command."""

    def test_get_json(self):
        """transcripts get should return transcript segments."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_segment("Alice", "Hello everyone", 0.0, 2.5),
            _make_mock_segment("Bob", "Hi Alice", 3.0, 4.0),
        ]

        with patch("attio_cli.commands.transcripts.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.transcripts.get.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "transcripts", "get", "--meeting", "mtg_123", "--recording", "rec_123"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["speaker"] == "Alice"
            assert parsed["data"][1]["speech"] == "Hi Alice"

    def test_get_calls_sdk_correctly(self):
        """transcripts get should pass meeting and recording IDs to the SDK."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_segment()]

        with patch("attio_cli.commands.transcripts.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.transcripts.get.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "transcripts", "get",
                    "--meeting", "mtg_456",
                    "--recording", "rec_789",
                    "--limit", "10",
                ],
            )
            assert result.exit_code == 0
            mock_client.transcripts.get.assert_called_once_with(
                "mtg_456",
                "rec_789",
                limit=10,
                cursor=None,
            )
