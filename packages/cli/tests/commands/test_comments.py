"""Tests for the comments commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_comment(comment_id="cmt_123"):
    """Create a mock Comment model."""
    comment = MagicMock()
    comment.id = MagicMock()
    comment.id.comment_id = comment_id
    comment.thread_id = "thread_456"
    comment.content_plaintext = "Great progress"
    comment.created_at = "2026-01-01T00:00:00Z"
    comment.author = MagicMock()
    comment.author.model_dump.return_value = {"type": "workspace-member", "id": "user_789"}
    comment.record = None
    comment.entry = None
    return comment


class TestCommentsCreate:
    """Test the comments create command."""

    def test_create_with_thread(self):
        """comments create --thread should create a comment on a thread."""
        mock_comment = _make_mock_comment()

        with patch("attio_cli.commands.comments.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.comments.create.return_value = mock_comment
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "comments", "create",
                    "--body", "Great progress",
                    "--author", '{"type": "workspace-member", "id": "user_789"}',
                    "--thread", "thread_456",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["content_plaintext"] == "Great progress"
            mock_client.comments.create.assert_called_once_with(
                thread_id="thread_456",
                record=None,
                entry=None,
                content="Great progress",
                author={"type": "workspace-member", "id": "user_789"},
            )

    def test_create_with_record(self):
        """comments create --record should create a comment on a record."""
        mock_comment = _make_mock_comment()

        with patch("attio_cli.commands.comments.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.comments.create.return_value = mock_comment
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "comments", "create",
                    "--body", "Nice work",
                    "--author", '{"type": "workspace-member", "id": "user_789"}',
                    "--record", '{"object": "people", "record_id": "rec_123"}',
                ],
            )
            assert result.exit_code == 0
            mock_client.comments.create.assert_called_once_with(
                thread_id=None,
                record={"object": "people", "record_id": "rec_123"},
                entry=None,
                content="Nice work",
                author={"type": "workspace-member", "id": "user_789"},
            )

    def test_create_with_entry(self):
        """comments create --entry should create a comment on an entry."""
        mock_comment = _make_mock_comment()

        with patch("attio_cli.commands.comments.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.comments.create.return_value = mock_comment
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "comments", "create",
                    "--body", "Entry comment",
                    "--author", '{"type": "workspace-member", "id": "user_789"}',
                    "--entry", '{"list": "pipeline", "entry_id": "ent_123"}',
                ],
            )
            assert result.exit_code == 0
            mock_client.comments.create.assert_called_once_with(
                thread_id=None,
                record=None,
                entry={"list": "pipeline", "entry_id": "ent_123"},
                content="Entry comment",
                author={"type": "workspace-member", "id": "user_789"},
            )

    def test_create_no_target_fails(self):
        """comments create without any target should fail."""
        result = runner.invoke(
            app,
            [
                "--json", "comments", "create",
                "--body", "No target",
                "--author", '{"type": "workspace-member", "id": "user_789"}',
            ],
        )
        assert result.exit_code != 0

    def test_create_multiple_targets_fails(self):
        """comments create with multiple targets should fail."""
        result = runner.invoke(
            app,
            [
                "--json", "comments", "create",
                "--body", "Multiple targets",
                "--author", '{"type": "workspace-member", "id": "user_789"}',
                "--thread", "thread_456",
                "--record", '{"object": "people", "record_id": "rec_123"}',
            ],
        )
        assert result.exit_code != 0


class TestCommentsGet:
    """Test the comments get command."""

    def test_get_comment(self):
        """comments get should return a comment by ID."""
        mock_comment = _make_mock_comment()

        with patch("attio_cli.commands.comments.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.comments.get.return_value = mock_comment
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "comments", "get", "cmt_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["comment_id"] == "cmt_123"
            mock_client.comments.get.assert_called_once_with("cmt_123")


class TestCommentsDelete:
    """Test the comments delete command."""

    def test_delete_comment(self):
        """comments delete --yes should delete without prompting."""
        with patch("attio_cli.commands.comments.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "comments", "delete", "cmt_123", "--yes"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["status"] == "success"
            mock_client.comments.delete.assert_called_once_with("cmt_123")
