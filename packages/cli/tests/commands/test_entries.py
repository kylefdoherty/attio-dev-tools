"""Tests for the entries commands (append, values)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_entry(entry_id="entry_123", parent_record_id="rec_456"):
    """Create a mock entry for testing."""
    entry = MagicMock()
    entry.id = MagicMock()
    entry.id.entry_id = entry_id
    entry.id.list_id = "list_abc"
    entry.parent_record_id = parent_record_id
    entry.parent_object = "people"
    entry.created_at = "2026-01-01T00:00:00Z"
    entry.entry_values = {}
    return entry


class TestEntriesAppend:
    """Test the entries append command."""

    def test_append_json_output(self):
        """entries append --json should return the updated entry."""
        mock_entry = _make_mock_entry()

        with patch("attio_cli.commands.entries.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.entries.append.return_value = mock_entry
            mock_gc.return_value = mock_client

            values = '{"status": [{"value": "active"}]}'
            result = runner.invoke(
                app,
                [
                    "--json", "entries", "append", "entry_123",
                    "--list", "my-list",
                    "--values", values,
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["entry_id"] == "entry_123"
            mock_client.entries.append.assert_called_once_with(
                "my-list", "entry_123", entry_values={"status": [{"value": "active"}]}
            )

    def test_append_requires_list(self):
        """entries append without --list should fail."""
        result = runner.invoke(
            app,
            ["--json", "entries", "append", "entry_123", "--values", '{"a": 1}'],
        )
        assert result.exit_code != 0

    def test_append_requires_values(self):
        """entries append without --values should fail."""
        result = runner.invoke(
            app,
            ["--json", "entries", "append", "entry_123", "--list", "my-list"],
        )
        assert result.exit_code != 0


class TestEntriesValues:
    """Test the entries values command."""

    def test_values_json_output(self):
        """entries values --json should return attribute values."""
        mock_value = MagicMock()
        mock_value.model_dump.return_value = {
            "attribute_type": "text",
            "active_from": "2026-01-01T00:00:00Z",
            "active_until": None,
            "value": "Some text",
        }
        mock_response = MagicMock()
        mock_response.data = [mock_value]

        with patch("attio_cli.commands.entries.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.entries.get_attribute_values.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "entries", "values", "entry_123",
                    "--list", "my-list",
                    "--attribute", "notes",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["attribute_type"] == "text"
            mock_client.entries.get_attribute_values.assert_called_once_with(
                "my-list", "entry_123", "notes",
                show_historic=False, limit=25, offset=0
            )

    def test_values_requires_list(self):
        """entries values without --list should fail."""
        result = runner.invoke(
            app,
            ["--json", "entries", "values", "entry_123", "--attribute", "notes"],
        )
        assert result.exit_code != 0

    def test_values_requires_attribute(self):
        """entries values without --attribute should fail."""
        result = runner.invoke(
            app,
            ["--json", "entries", "values", "entry_123", "--list", "my-list"],
        )
        assert result.exit_code != 0
