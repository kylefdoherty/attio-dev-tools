"""Tests for the objects commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_object(object_id="obj_123", slug="custom_obj"):
    """Create a mock Object model."""
    obj = MagicMock()
    obj.id = MagicMock()
    obj.id.object_id = object_id
    obj.api_slug = slug
    obj.singular_noun = "item"
    obj.plural_noun = "items"
    obj.created_at = "2026-01-01T00:00:00Z"
    return obj


class TestObjectsList:
    """Test the objects list command."""

    def test_list_json(self):
        """objects list --json should return all objects."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_object("obj_people", "people"),
            _make_mock_object("obj_companies", "companies"),
        ]

        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.objects.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "objects", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["api_slug"] == "people"


class TestObjectsGet:
    """Test the objects get command."""

    def test_get_by_slug(self):
        """objects get should return an object by slug."""
        mock_obj = _make_mock_object()

        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.objects.get.return_value = mock_obj
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "objects", "get", "custom_obj"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["api_slug"] == "custom_obj"


class TestObjectsCreate:
    """Test the objects create command."""

    def test_create_object(self):
        """objects create should return the created object."""
        mock_obj = _make_mock_object(object_id="obj_new", slug="new_obj")

        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.objects.create.return_value = mock_obj
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "objects", "create",
                    "--api-slug", "new_obj",
                    "--singular-noun", "item",
                    "--plural-noun", "items",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["api_slug"] == "new_obj"


class TestObjectsUpdate:
    """Test the objects update command."""

    def test_update_object(self):
        """objects update should return the updated object."""
        mock_obj = _make_mock_object()
        mock_obj.singular_noun = "widget"

        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.objects.update.return_value = mock_obj
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "objects", "update", "custom_obj", "--singular-noun", "widget"],
            )
            assert result.exit_code == 0
