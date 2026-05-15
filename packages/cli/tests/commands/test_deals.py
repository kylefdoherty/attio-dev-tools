"""Tests for the deals commands (append, values, entries)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_record(record_id="rec_d123", name="Big Deal"):
    """Create a mock deal record for testing."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = record_id
    record.id.object_id = "obj_deals"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = f"https://app.attio.com/record/{record_id}"
    record.values = {
        "name": [MagicMock(**{
            "model_dump.return_value": {"value": name, "attribute_type": "text"},
        })],
    }
    return record


class TestDealsAppend:
    """Test the deals append command."""

    def test_append_json_output(self):
        """deals append --json should return the updated record."""
        mock_record = _make_mock_record(record_id="rec_d123")

        with patch("attio_cli.commands.deals.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.deals.append.return_value = mock_record
            mock_gc.return_value = mock_client

            values = '{"tags": [{"value": "priority"}]}'
            result = runner.invoke(
                app, ["--json", "deals", "append", "rec_d123", "--values", values]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["record_id"] == "rec_d123"
            mock_client.deals.append.assert_called_once_with(
                "rec_d123", values={"tags": [{"value": "priority"}]}
            )

    def test_append_requires_values(self):
        """deals append without --values should fail."""
        result = runner.invoke(app, ["--json", "deals", "append", "rec_d123"])
        assert result.exit_code != 0


class TestDealsValues:
    """Test the deals values command."""

    def test_values_json_output(self):
        """deals values --json should return attribute values."""
        mock_value = MagicMock()
        mock_value.model_dump.return_value = {
            "attribute_type": "currency",
            "active_from": "2026-01-01T00:00:00Z",
            "active_until": None,
            "currency_value": 50000,
        }
        mock_response = MagicMock()
        mock_response.data = [mock_value]

        with patch("attio_cli.commands.deals.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.deals.get_attribute_values.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "deals", "values", "rec_d123", "--attribute", "value"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["attribute_type"] == "currency"
            mock_client.deals.get_attribute_values.assert_called_once_with(
                "rec_d123", "value", show_historic=False, limit=25, offset=0
            )


class TestDealsEntries:
    """Test the deals entries command."""

    def test_entries_json_output(self):
        """deals entries --json should return entry list."""
        mock_entry = MagicMock()
        mock_entry.list_id = "list_abc"
        mock_entry.list_api_slug = "deal-pipeline"
        mock_entry.entry_id = "entry_999"
        mock_entry.created_at = "2026-01-01T00:00:00Z"
        mock_response = MagicMock()
        mock_response.data = [mock_entry]

        with patch("attio_cli.commands.deals.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.deals.list_entries.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "deals", "entries", "rec_d123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["entry_id"] == "entry_999"
            assert parsed["data"][0]["list_slug"] == "deal-pipeline"
            mock_client.deals.list_entries.assert_called_once_with(
                "rec_d123", limit=25, offset=0
            )
