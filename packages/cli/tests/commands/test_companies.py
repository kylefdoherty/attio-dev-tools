"""Tests for the companies commands (append, values, entries)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_record(record_id="rec_c123", name="Acme Corp", domain="acme.com"):
    """Create a mock company record for testing."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = record_id
    record.id.object_id = "obj_companies"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = f"https://app.attio.com/record/{record_id}"
    record.values = {
        "name": [MagicMock(**{
            "model_dump.return_value": {"value": name, "attribute_type": "text"},
        })],
        "domains": [MagicMock(**{
            "model_dump.return_value": {"domain": domain, "attribute_type": "domain"},
        })],
    }
    return record


class TestCompaniesAppend:
    """Test the companies append command."""

    def test_append_json_output(self):
        """companies append --json should return the updated record."""
        mock_record = _make_mock_record(record_id="rec_c123")

        with patch("attio_cli.commands.companies.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.companies.append.return_value = mock_record
            mock_gc.return_value = mock_client

            values = '{"tags": [{"value": "enterprise"}]}'
            result = runner.invoke(
                app, ["--json", "companies", "append", "rec_c123", "--values", values]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_c123"
            mock_client.companies.append.assert_called_once_with(
                "rec_c123", values={"tags": [{"value": "enterprise"}]}
            )

    def test_append_requires_values(self):
        """companies append without --values should fail."""
        result = runner.invoke(app, ["--json", "companies", "append", "rec_c123"])
        assert result.exit_code != 0


class TestCompaniesValues:
    """Test the companies values command."""

    def test_values_json_output(self):
        """companies values --json should return attribute values."""
        mock_value = MagicMock()
        mock_value.model_dump.return_value = {
            "attribute_type": "domain",
            "active_from": "2026-01-01T00:00:00Z",
            "active_until": None,
            "domain": "acme.com",
        }
        mock_response = MagicMock()
        mock_response.data = [mock_value]

        with patch("attio_cli.commands.companies.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.companies.get_attribute_values.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "companies", "values", "rec_c123", "--attribute", "domains"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["attribute_type"] == "domain"
            mock_client.companies.get_attribute_values.assert_called_once_with(
                "rec_c123", "domains", show_historic=False, limit=25, offset=0
            )


class TestCompaniesEntries:
    """Test the companies entries command."""

    def test_entries_json_output(self):
        """companies entries --json should return entry list."""
        mock_entry = MagicMock()
        mock_entry.list_id = "list_abc"
        mock_entry.list_api_slug = "sales-pipeline"
        mock_entry.entry_id = "entry_789"
        mock_entry.created_at = "2026-01-01T00:00:00Z"
        mock_response = MagicMock()
        mock_response.data = [mock_entry]

        with patch("attio_cli.commands.companies.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.companies.list_entries.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "companies", "entries", "rec_c123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["entry_id"] == "entry_789"
            assert parsed["data"][0]["list_slug"] == "sales-pipeline"
            mock_client.companies.list_entries.assert_called_once_with(
                "rec_c123", limit=25, offset=0
            )
