"""Tests for the generic records commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_record(record_id="rec_123"):
    """Create a mock record for testing."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = record_id
    record.id.object_id = "obj_custom"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = f"https://app.attio.com/record/{record_id}"
    record.values = {
        "name": [MagicMock(**{
            "model_dump.return_value": {"value": "Test Record", "attribute_type": "text"},
        })],
    }
    return record


class TestRecordsList:
    """Test the records list command."""

    def test_list_requires_object(self):
        """records list without --object should fail."""
        result = runner.invoke(app, ["--json", "records", "list"])
        assert result.exit_code != 0

    def test_list_with_object(self):
        """records list --object=custom should work."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_record()]

        with patch("attio_cli.commands.records.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "custom"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1

    def test_list_with_filter(self):
        """records list --filter should use query endpoint."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands.records.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.query.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "records", "list",
                    "--object", "custom",
                    "--filter", '{"name": {"$eq": "test"}}',
                ],
            )
            assert result.exit_code == 0
            mock_client.records.query.assert_called_once()


class TestRecordsGet:
    """Test the records get command."""

    def test_get_with_object(self):
        """records get should return a single record."""
        mock_record = _make_mock_record()

        with patch("attio_cli.commands.records.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.get.return_value = mock_record
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "get", "rec_123", "--object", "custom"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_123"


class TestRecordsCreate:
    """Test the records create command."""

    def test_create_with_values(self):
        """records create should return the created record."""
        mock_record = _make_mock_record(record_id="rec_new")

        with patch("attio_cli.commands.records.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.create.return_value = mock_record
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "records", "create",
                    "--object", "custom",
                    "--values", '{"name": [{"value": "New"}]}',
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_new"


class TestRecordsDelete:
    """Test the records delete command."""

    def test_delete_with_yes(self):
        """records delete --yes should skip confirmation."""
        with patch("attio_cli.commands.records.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "records", "delete", "rec_123", "--object", "custom", "--yes"],
            )
            assert result.exit_code == 0
