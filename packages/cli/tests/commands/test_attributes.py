"""Tests for the attributes commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_attribute(attribute_id="attr_123", slug="annual_revenue", title="Annual Revenue", type_="currency"):
    """Create a mock Attribute model."""
    attr = MagicMock()
    attr.id = MagicMock()
    attr.id.attribute_id = attribute_id
    attr.title = title
    attr.description = "Revenue per year"
    attr.api_slug = slug
    attr.type = type_
    attr.is_system_attribute = False
    attr.is_writable = True
    attr.is_required = False
    attr.is_unique = False
    attr.is_multiselect = False
    attr.is_archived = False
    attr.created_at = "2026-01-01T00:00:00Z"
    return attr


class TestAttributesList:
    """Test the attributes list command."""

    def test_list_with_object(self):
        """attributes list --object should return attributes for that object."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_attribute("attr_1", "name", "Name", "text"),
            _make_mock_attribute("attr_2", "email", "Email", "email-address"),
        ]

        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.attributes.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "attributes", "list", "--object", "people"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["api_slug"] == "name"
            mock_client.attributes.list.assert_called_once_with("objects", "people")

    def test_list_with_list(self):
        """attributes list --list should return attributes for that list."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_attribute()]

        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.attributes.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "attributes", "list", "--list", "pipeline"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            mock_client.attributes.list.assert_called_once_with("lists", "pipeline")

    def test_list_no_target_fails(self):
        """attributes list without --object or --list should fail."""
        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_gc.return_value = MagicMock()
            result = runner.invoke(app, ["--json", "attributes", "list"])
            assert result.exit_code != 0

    def test_list_both_targets_fails(self):
        """attributes list with both --object and --list should fail."""
        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_gc.return_value = MagicMock()
            result = runner.invoke(app, ["--json", "attributes", "list", "--object", "people", "--list", "pipeline"])
            assert result.exit_code != 0


class TestAttributesGet:
    """Test the attributes get command."""

    def test_get_attribute(self):
        """attributes get should return an attribute by slug."""
        mock_attr = _make_mock_attribute()

        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.attributes.get.return_value = mock_attr
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "attributes", "get", "annual_revenue", "--object", "companies"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["api_slug"] == "annual_revenue"
            mock_client.attributes.get.assert_called_once_with("objects", "companies", "annual_revenue")


class TestAttributesCreate:
    """Test the attributes create command."""

    def test_create_attribute(self):
        """attributes create should return the created attribute."""
        mock_attr = _make_mock_attribute(attribute_id="attr_new", slug="new_attr", title="New Attr", type_="text")

        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.attributes.create.return_value = mock_attr
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "attributes", "create",
                    "--object", "people",
                    "--title", "New Attr",
                    "--slug", "new_attr",
                    "--type", "text",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["api_slug"] == "new_attr"
            mock_client.attributes.create.assert_called_once()


class TestAttributesUpdate:
    """Test the attributes update command."""

    def test_update_attribute(self):
        """attributes update should return the updated attribute."""
        mock_attr = _make_mock_attribute()
        mock_attr.title = "Updated Revenue"

        with patch("attio_cli.commands.attributes.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.attributes.update.return_value = mock_attr
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "attributes", "update", "annual_revenue", "--object", "companies", "--title", "Updated Revenue"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["title"] == "Updated Revenue"
            mock_client.attributes.update.assert_called_once()
