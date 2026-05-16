"""Tests for the people commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_record(record_id="rec_123", name_first="Jane", name_last="Doe", email="jane@example.com"):
    """Create a mock record for testing."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = record_id
    record.id.object_id = "obj_people"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = f"https://app.attio.com/record/{record_id}"
    record.values = {
        "name": [MagicMock(**{
            "model_dump.return_value": {
                "first_name": name_first,
                "last_name": name_last,
                "attribute_type": "personal-name",
            },
        })],
        "email_addresses": [MagicMock(**{
            "model_dump.return_value": {
                "email_address": email,
                "attribute_type": "email",
            },
        })],
    }
    return record


class TestPeopleList:
    """Test the people list command."""

    def test_list_json_output(self):
        """people list --json should return valid JSON with data array."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_record()]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["record_id"] == "rec_123"

    def test_list_with_limit(self):
        """people list --limit should pass limit to SDK."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list", "--limit", "10"])
            assert result.exit_code == 0
            mock_client.people.list.assert_called_once_with(limit=10, offset=0)

    def test_list_with_filter(self):
        """people list --filter should use query instead of list."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.query.return_value = mock_response
            mock_gc.return_value = mock_client

            filter_json = '{"email_addresses": {"$contains": "@acme.com"}}'
            result = runner.invoke(
                app, ["--json", "people", "list", "--filter", filter_json]
            )
            assert result.exit_code == 0
            mock_client.people.query.assert_called_once()

    def test_list_empty(self):
        """people list with no results should return empty data array."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"] == []


class TestPeopleListAll:
    """Test the people list --all command."""

    def test_list_all_flag(self):
        """people list --all should use query_all and return all results."""
        mock_record1 = _make_mock_record(record_id="rec_1")
        mock_record2 = _make_mock_record(record_id="rec_2")

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.query_all.return_value = [mock_record1, mock_record2]
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "list", "--all"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert len(data["data"]) == 2
            mock_client.people.query_all.assert_called_once()

    def test_list_all_with_filter(self):
        """people list --all --filter should pass filter to query_all."""
        mock_record = _make_mock_record()

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.query_all.return_value = [mock_record]
            mock_gc.return_value = mock_client

            filter_json = '{"email_addresses": {"$contains": "@acme.com"}}'
            result = runner.invoke(
                app, ["--json", "people", "list", "--all", "--filter", filter_json]
            )
            assert result.exit_code == 0
            mock_client.people.query_all.assert_called_once_with(
                filter={"email_addresses": {"$contains": "@acme.com"}}
            )


class TestPeopleGet:
    """Test the people get command."""

    def test_get_json_output(self):
        """people get --json should return a single record."""
        mock_record = _make_mock_record()

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.get.return_value = mock_record
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "get", "rec_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_123"

    def test_get_not_found(self):
        """people get with bad ID should return exit code 5."""
        from attio._exceptions import NotFoundError

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.get.side_effect = NotFoundError("Not found", status_code=404)
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "get", "bad_id"])
            assert result.exit_code == 5


class TestPeopleCreate:
    """Test the people create command."""

    def test_create_json_output(self):
        """people create --json should return the created record."""
        mock_record = _make_mock_record(record_id="rec_new")

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.create.return_value = mock_record
            mock_gc.return_value = mock_client

            values = '{"name": [{"first_name": "Jane", "last_name": "Doe"}]}'
            result = runner.invoke(
                app, ["--json", "people", "create", "--values", values]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_new"


class TestPeopleDelete:
    """Test the people delete command."""

    def test_delete_with_yes_flag(self):
        """people delete --yes should skip confirmation."""
        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "people", "delete", "rec_123", "--yes"]
            )
            assert result.exit_code == 0
            mock_client.people.delete.assert_called_once_with("rec_123")


class TestPeopleSearch:
    """Test the people search command."""

    def test_search_json_output(self):
        """people search --json should return search results."""
        mock_result = MagicMock()
        search_item = MagicMock()
        search_item.id = MagicMock()
        search_item.id.record_id = "rec_123"
        search_item.record_text = "Jane Doe"
        search_item.object_slug = "people"
        mock_result.data = [search_item]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.global_search.return_value = mock_result
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "people", "search", "Jane"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["record_id"] == "rec_123"


class TestPeopleAppend:
    """Test the people append command."""

    def test_append_json_output(self):
        """people append --json should return the updated record."""
        mock_record = _make_mock_record(record_id="rec_123")

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.append.return_value = mock_record
            mock_gc.return_value = mock_client

            values = '{"tags": [{"value": "vip"}]}'
            result = runner.invoke(
                app, ["--json", "people", "append", "rec_123", "--values", values]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_123"
            mock_client.people.append.assert_called_once_with(
                "rec_123", values={"tags": [{"value": "vip"}]}
            )

    def test_append_requires_values(self):
        """people append without --values should fail."""
        result = runner.invoke(app, ["--json", "people", "append", "rec_123"])
        assert result.exit_code != 0


class TestPeopleValues:
    """Test the people values command."""

    def test_values_json_output(self):
        """people values --json should return attribute values."""
        mock_value = MagicMock()
        mock_value.model_dump.return_value = {
            "attribute_type": "email",
            "active_from": "2026-01-01T00:00:00Z",
            "active_until": None,
            "email_address": "jane@example.com",
        }
        mock_response = MagicMock()
        mock_response.data = [mock_value]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.get_attribute_values.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "people", "values", "rec_123", "--attribute", "email_addresses"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["attribute_type"] == "email"
            mock_client.people.get_attribute_values.assert_called_once_with(
                "rec_123", "email_addresses", show_historic=False, limit=25, offset=0
            )

    def test_values_with_show_historic(self):
        """people values --show-historic should pass flag to SDK."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.get_attribute_values.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "people", "values", "rec_123",
                    "--attribute", "email_addresses",
                    "--show-historic",
                ],
            )
            assert result.exit_code == 0
            mock_client.people.get_attribute_values.assert_called_once_with(
                "rec_123", "email_addresses", show_historic=True, limit=25, offset=0
            )


class TestPeopleEntries:
    """Test the people entries command."""

    def test_entries_json_output(self):
        """people entries --json should return entry list."""
        mock_entry = MagicMock()
        mock_entry.list_id = "list_abc"
        mock_entry.list_api_slug = "my-list"
        mock_entry.entry_id = "entry_456"
        mock_entry.created_at = "2026-01-01T00:00:00Z"
        mock_response = MagicMock()
        mock_response.data = [mock_entry]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list_entries.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "people", "entries", "rec_123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["entry_id"] == "entry_456"
            assert parsed["data"][0]["list_slug"] == "my-list"
            mock_client.people.list_entries.assert_called_once_with(
                "rec_123", limit=25, offset=0
            )

    def test_entries_with_limit(self):
        """people entries --limit should pass limit to SDK."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list_entries.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "people", "entries", "rec_123", "--limit", "5"]
            )
            assert result.exit_code == 0
            mock_client.people.list_entries.assert_called_once_with(
                "rec_123", limit=5, offset=0
            )
