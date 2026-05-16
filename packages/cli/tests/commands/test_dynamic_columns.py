"""Tests for dynamic attribute-based column display logic.

Verifies that:
- Standard objects (people, companies, deals) return their pre-built columns
- Custom objects get columns built from attribute metadata
- The attribute cache prevents redundant API calls
- Fallback to GENERIC_COLUMNS when the API call fails or no client is provided
- Non-displayable attribute types are excluded
- Archived attributes are excluded
- Column count is capped at _MAX_DYNAMIC_COLUMNS
- The generic ``records list`` command uses dynamic columns for custom objects
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.commands._record_helpers import (
    COMPANIES_COLUMNS,
    DEALS_COLUMNS,
    GENERIC_COLUMNS,
    PEOPLE_COLUMNS,
    _build_columns_from_attributes,
    _MAX_DYNAMIC_COLUMNS,
    clear_attribute_cache,
    get_columns_for_object,
)
from attio_cli.main import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_attribute(
    slug: str,
    title: str,
    attr_type: str,
    *,
    is_archived: bool = False,
    is_system: bool = False,
) -> MagicMock:
    """Create a mock Attribute model."""
    attr = MagicMock()
    attr.api_slug = slug
    attr.title = title
    attr.type = attr_type
    attr.is_archived = is_archived
    attr.is_system_attribute = is_system
    return attr


def _make_mock_record(record_id="rec_123", values=None):
    """Create a mock record for testing."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = record_id
    record.id.object_id = "obj_custom"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = f"https://app.attio.com/record/{record_id}"
    record.values = values or {
        "name": [MagicMock(**{
            "model_dump.return_value": {"value": "Test Record", "attribute_type": "text"},
        })],
        "priority": [MagicMock(**{
            "model_dump.return_value": {"value": "High", "attribute_type": "select"},
        })],
    }
    return record


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the attribute column cache before each test."""
    clear_attribute_cache()
    yield
    clear_attribute_cache()


# ---------------------------------------------------------------------------
# Unit tests: get_columns_for_object
# ---------------------------------------------------------------------------


class TestGetColumnsForStandardObjects:
    """Standard objects should return their pre-built column definitions."""

    def test_people_returns_people_columns(self):
        assert get_columns_for_object("people") is PEOPLE_COLUMNS

    def test_companies_returns_companies_columns(self):
        assert get_columns_for_object("companies") is COMPANIES_COLUMNS

    def test_deals_returns_deals_columns(self):
        assert get_columns_for_object("deals") is DEALS_COLUMNS

    def test_standard_objects_ignore_client(self):
        """Even if a client is passed, standard objects use pre-built columns."""
        client = MagicMock()
        assert get_columns_for_object("people", client) is PEOPLE_COLUMNS
        # The attributes API should never be called for standard objects
        client.attributes.list.assert_not_called()


class TestGetColumnsForCustomObjects:
    """Custom objects should build columns from attribute metadata."""

    def test_custom_object_fetches_attributes(self):
        """A custom object slug triggers an attributes.list() call."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_attribute("project_name", "Project Name", "text"),
            _make_mock_attribute("status", "Status", "status"),
        ]
        client.attributes.list.return_value = mock_response

        cols = get_columns_for_object("projects", client)

        client.attributes.list.assert_called_once_with("objects", "projects")
        # Should have ID + 2 attribute cols + Created = 4
        assert len(cols) == 4
        headers = [c["header"] for c in cols]
        assert headers == ["ID", "Project Name", "Status", "Created"]

    def test_dynamic_accessors_read_correct_keys(self):
        """Dynamic column accessors should read from the flattened record dict."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_attribute("project_name", "Project Name", "text"),
        ]
        client.attributes.list.return_value = mock_response

        cols = get_columns_for_object("projects", client)
        # The second column (index 1) should be "Project Name"
        accessor = cols[1]["accessor"]
        assert accessor({"project_name": "Alpha"}) == "Alpha"
        assert accessor({}) == ""

    def test_no_client_falls_back_to_generic(self):
        """Without a client, custom objects use GENERIC_COLUMNS."""
        cols = get_columns_for_object("my_custom_object")
        assert cols is GENERIC_COLUMNS

    def test_api_error_falls_back_to_generic(self):
        """If the API call fails, fall back to GENERIC_COLUMNS."""
        client = MagicMock()
        client.attributes.list.side_effect = Exception("API error")

        cols = get_columns_for_object("broken_object", client)
        assert cols is GENERIC_COLUMNS

    def test_empty_attributes_falls_back_to_generic(self):
        """If the object has no attributes, use GENERIC_COLUMNS."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []
        client.attributes.list.return_value = mock_response

        cols = get_columns_for_object("empty_object", client)
        assert cols is GENERIC_COLUMNS


class TestAttributeCache:
    """The attribute column cache should avoid redundant API calls."""

    def test_second_call_uses_cache(self):
        """Calling get_columns_for_object twice should only fetch once."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_attribute("name", "Name", "text"),
        ]
        client.attributes.list.return_value = mock_response

        cols1 = get_columns_for_object("tickets", client)
        cols2 = get_columns_for_object("tickets", client)

        assert cols1 is cols2
        client.attributes.list.assert_called_once()

    def test_clear_cache_allows_refetch(self):
        """clear_attribute_cache() should allow a fresh fetch."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_attribute("name", "Name", "text"),
        ]
        client.attributes.list.return_value = mock_response

        get_columns_for_object("tickets", client)
        clear_attribute_cache()
        get_columns_for_object("tickets", client)

        assert client.attributes.list.call_count == 2


# ---------------------------------------------------------------------------
# Unit tests: _build_columns_from_attributes
# ---------------------------------------------------------------------------


class TestBuildColumnsFromAttributes:
    """Test the column-building logic in isolation."""

    def test_filters_non_displayable_types(self):
        """Types like record-reference should be excluded."""
        attrs = [
            _make_mock_attribute("name", "Name", "text"),
            _make_mock_attribute("owner", "Owner", "record-reference"),
            _make_mock_attribute("interaction", "Last Interaction", "interaction"),
        ]
        cols = _build_columns_from_attributes(attrs)
        headers = [c["header"] for c in cols]
        assert "Name" in headers
        assert "Owner" not in headers
        assert "Last Interaction" not in headers

    def test_excludes_archived_attributes(self):
        """Archived attributes should not appear in columns."""
        attrs = [
            _make_mock_attribute("name", "Name", "text"),
            _make_mock_attribute("old_field", "Old Field", "text", is_archived=True),
        ]
        cols = _build_columns_from_attributes(attrs)
        headers = [c["header"] for c in cols]
        assert "Old Field" not in headers

    def test_caps_at_max_columns(self):
        """Should not include more than _MAX_DYNAMIC_COLUMNS attribute columns."""
        attrs = [
            _make_mock_attribute(f"field_{i}", f"Field {i}", "text")
            for i in range(10)
        ]
        cols = _build_columns_from_attributes(attrs)
        # ID + up to _MAX_DYNAMIC_COLUMNS + Created
        assert len(cols) == 2 + _MAX_DYNAMIC_COLUMNS

    def test_always_includes_id_and_created(self):
        """ID and Created columns are always present."""
        attrs = [_make_mock_attribute("name", "Name", "text")]
        cols = _build_columns_from_attributes(attrs)
        assert cols[0]["header"] == "ID"
        assert cols[-1]["header"] == "Created"

    def test_skips_attributes_without_slug(self):
        """Attributes with empty api_slug are skipped."""
        attr = _make_mock_attribute("", "No Slug", "text")
        attrs = [attr]
        cols = _build_columns_from_attributes(attrs)
        # Only ID + Created
        assert len(cols) == 2

    def test_all_displayable_types_included(self):
        """All types in _DISPLAYABLE_ATTR_TYPES should be included."""
        displayable_types = [
            "text", "number", "checkbox", "currency", "date", "timestamp",
            "email", "phone", "domain", "select", "status", "rating",
            "personal-name", "location",
        ]
        attrs = [
            _make_mock_attribute(f"f_{t.replace('-', '_')}", f"F {t}", t)
            for t in displayable_types
        ]
        cols = _build_columns_from_attributes(attrs)
        # Should have ID + min(len(displayable_types), _MAX_DYNAMIC_COLUMNS) + Created
        expected_attr_count = min(len(displayable_types), _MAX_DYNAMIC_COLUMNS)
        assert len(cols) == 2 + expected_attr_count


# ---------------------------------------------------------------------------
# Integration tests: records list with dynamic columns
# ---------------------------------------------------------------------------


class TestRecordsListDynamicColumns:
    """Test that ``records list --object custom`` uses dynamic columns."""

    def test_custom_object_uses_dynamic_columns(self):
        """records list --object custom_projects should fetch attributes and display them."""
        mock_response = MagicMock()
        mock_record = _make_mock_record()
        mock_response.data = [mock_record]

        mock_attr_response = MagicMock()
        mock_attr_response.data = [
            _make_mock_attribute("name", "Name", "text"),
            _make_mock_attribute("priority", "Priority", "select"),
        ]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_client.attributes.list.return_value = mock_attr_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "custom_projects"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            # Verify attributes were fetched
            mock_client.attributes.list.assert_called_once_with("objects", "custom_projects")

    def test_standard_object_via_records_skips_attribute_fetch(self):
        """records list --object people should use pre-built columns, no attribute fetch."""
        mock_response = MagicMock()
        mock_response.data = []

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "people"]
            )
            assert result.exit_code == 0
            # Should NOT have called attributes.list for a standard object
            mock_client.attributes.list.assert_not_called()

    def test_attribute_fetch_failure_falls_back_gracefully(self):
        """If attributes.list fails, records list should still work with generic columns."""
        mock_response = MagicMock()
        mock_record = _make_mock_record()
        mock_response.data = [mock_record]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_client.attributes.list.side_effect = Exception("Permission denied")
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "secret_object"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1

    def test_custom_object_list_all_uses_dynamic_columns(self):
        """records list --all --object custom should also use dynamic columns."""
        mock_record = _make_mock_record()

        mock_attr_response = MagicMock()
        mock_attr_response.data = [
            _make_mock_attribute("name", "Name", "text"),
        ]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.query_all.return_value = [mock_record]
            mock_client.attributes.list.return_value = mock_attr_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "custom_tasks", "--all"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            mock_client.attributes.list.assert_called_once_with("objects", "custom_tasks")

    def test_json_output_unchanged_for_standard_objects(self):
        """JSON output for standard objects (people) should not change."""
        mock_response = MagicMock()
        mock_record = MagicMock()
        mock_record.id = MagicMock()
        mock_record.id.record_id = "rec_p123"
        mock_record.id.object_id = "obj_people"
        mock_record.created_at = "2026-01-01T00:00:00Z"
        mock_record.web_url = "https://app.attio.com/record/rec_p123"
        mock_record.values = {
            "name": [MagicMock(**{
                "model_dump.return_value": {"first_name": "Jane", "last_name": "Doe"},
            })],
        }
        mock_response.data = [mock_record]

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "records", "list", "--object", "people"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"][0]["record_id"] == "rec_p123"
            assert parsed["data"][0]["name"] == "Jane Doe"
