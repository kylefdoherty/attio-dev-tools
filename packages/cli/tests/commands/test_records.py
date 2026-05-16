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

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
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

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
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


class TestRecordsListAll:
    """Test the records list --all command."""

    def test_list_all_with_object(self):
        """records list --all --object should use query_all."""
        mock_record1 = _make_mock_record(record_id="rec_1")
        mock_record2 = _make_mock_record(record_id="rec_2")

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.query_all.return_value = [mock_record1, mock_record2]
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "custom", "--all"]
            )
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert len(data["data"]) == 2
            mock_client.records.query_all.assert_called_once_with("custom", filter=None)


class TestRecordsGet:
    """Test the records get command."""

    def test_get_with_object(self):
        """records get should return a single record."""
        mock_record = _make_mock_record()

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
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

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
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
        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "records", "delete", "rec_123", "--object", "custom", "--yes"],
            )
            assert result.exit_code == 0


class TestRecordsAppend:
    """Test the records append command."""

    def test_append_json_output(self):
        """records append --json should return the updated record."""
        mock_record = _make_mock_record(record_id="rec_123")

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.append.return_value = mock_record
            mock_gc.return_value = mock_client

            values = '{"tags": [{"value": "vip"}]}'
            result = runner.invoke(
                app,
                [
                    "--json", "records", "append", "rec_123",
                    "--object", "custom",
                    "--values", values,
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_123"
            mock_client.records.append.assert_called_once_with(
                "custom", "rec_123", values={"tags": [{"value": "vip"}]}
            )

    def test_append_requires_object(self):
        """records append without --object should fail."""
        result = runner.invoke(
            app,
            ["--json", "records", "append", "rec_123", "--values", '{"a": 1}'],
        )
        assert result.exit_code != 0


class TestRecordsValues:
    """Test the records values command."""

    def test_values_json_output(self):
        """records values --json should return attribute values."""
        mock_value = MagicMock()
        mock_value.model_dump.return_value = {
            "attribute_type": "text",
            "active_from": "2026-01-01T00:00:00Z",
            "active_until": None,
            "value": "Test",
        }
        mock_response = MagicMock()
        mock_response.data = [mock_value]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.get_attribute_values.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "records", "values", "rec_123",
                    "--object", "custom",
                    "--attribute", "name",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["attribute_type"] == "text"
            mock_client.records.get_attribute_values.assert_called_once_with(
                "custom", "rec_123", "name", show_historic=False, limit=25, offset=0
            )


class TestRecordsEntries:
    """Test the records entries command."""

    def test_entries_json_output(self):
        """records entries --json should return entry list."""
        mock_entry = MagicMock()
        mock_entry.list_id = "list_abc"
        mock_entry.list_api_slug = "my-list"
        mock_entry.entry_id = "entry_456"
        mock_entry.created_at = "2026-01-01T00:00:00Z"
        mock_response = MagicMock()
        mock_response.data = [mock_entry]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list_entries.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "records", "entries", "rec_123", "--object", "custom"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["entry_id"] == "entry_456"
            mock_client.records.list_entries.assert_called_once_with(
                "custom", "rec_123", limit=25, offset=0
            )

    def test_entries_requires_object(self):
        """records entries without --object should fail."""
        result = runner.invoke(
            app, ["--json", "records", "entries", "rec_123"]
        )
        assert result.exit_code != 0
