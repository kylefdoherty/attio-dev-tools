"""Tests for the threads commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_thread(thread_id="thread_123", num_comments=2):
    """Create a mock Thread model."""
    thread = MagicMock()
    thread.id = MagicMock()
    thread.id.thread_id = thread_id
    comments = []
    for i in range(num_comments):
        c = MagicMock()
        c.id = MagicMock()
        c.id.comment_id = f"cmt_{i}"
        c.content_plaintext = f"Comment {i}"
        c.created_at = "2026-01-01T00:00:00Z"
        comments.append(c)
    thread.comments = comments
    thread.created_at = "2026-01-01T00:00:00Z"
    return thread


class TestThreadsList:
    """Test the threads list command."""

    def test_list_threads(self):
        """threads list should return all threads."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_thread("thread_1", 3),
            _make_mock_thread("thread_2", 1),
        ]

        with patch("attio_cli.commands.threads.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.threads.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "threads", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["thread_id"] == "thread_1"
            assert parsed["data"][0]["comment_count"] == 3

    def test_list_threads_with_record_filter(self):
        """threads list --object --record should filter by record."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_thread()]

        with patch("attio_cli.commands.threads.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.threads.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "threads", "list", "--object", "people", "--record", "rec_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            mock_client.threads.list.assert_called_once_with(
                object="people", record_id="rec_123", list=None, entry_id=None,
            )

    def test_list_threads_with_entry_filter(self):
        """threads list --list --entry should filter by entry."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_thread()]

        with patch("attio_cli.commands.threads.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.threads.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "threads", "list", "--list", "pipeline", "--entry", "ent_456"])
            assert result.exit_code == 0
            mock_client.threads.list.assert_called_once_with(
                object=None, record_id=None, list="pipeline", entry_id="ent_456",
            )


class TestThreadsGet:
    """Test the threads get command."""

    def test_get_thread(self):
        """threads get should return a thread with comments."""
        mock_thread = _make_mock_thread("thread_abc", 2)

        with patch("attio_cli.commands.threads.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.threads.get.return_value = mock_thread
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "threads", "get", "thread_abc"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["thread_id"] == "thread_abc"
            assert parsed["data"]["comment_count"] == 2
            assert len(parsed["data"]["comments"]) == 2
            mock_client.threads.get.assert_called_once_with("thread_abc")
