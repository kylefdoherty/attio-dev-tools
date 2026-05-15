"""Tests for the views commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from attio_cli.commands.views import app as views_app

runner = CliRunner()

# Create a test app with the views command group registered.
app = typer.Typer()
app.add_typer(views_app, name="views")


@app.callback()
def _main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output


def _make_mock_view(view_id="view_123", title="All People", object_id="obj_people", list_id=None):
    """Create a mock View model."""
    v = MagicMock()
    v.id = MagicMock()
    v.id.view_id = view_id
    v.id.object_id = object_id
    v.id.list_id = list_id
    v.title = title
    v.created_at = "2026-01-01T00:00:00Z"
    return v


class TestViewsListForObject:
    """Test the views list command with --object."""

    def test_list_for_object(self):
        """views list --object should list views for an object."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_view("view_1", "All People"),
            _make_mock_view("view_2", "Active Leads"),
        ]

        with patch("attio_cli.commands.views.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.views.list_for_object.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "views", "list", "--object", "people"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["title"] == "All People"

    def test_list_for_object_with_archived(self):
        """views list --object --show-archived should pass flag to SDK."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_view()]

        with patch("attio_cli.commands.views.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.views.list_for_object.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "views", "list", "--object", "people", "--show-archived"]
            )
            assert result.exit_code == 0
            mock_client.views.list_for_object.assert_called_once_with(
                "people",
                show_archived=True,
                limit=None,
                cursor=None,
            )


class TestViewsListForList:
    """Test the views list command with --list."""

    def test_list_for_list(self):
        """views list --list should list views for a list."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_view("view_3", "Pipeline View", object_id=None, list_id="list_deals"),
        ]

        with patch("attio_cli.commands.views.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.views.list_for_list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "views", "list", "--list", "deals"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            assert parsed["data"][0]["title"] == "Pipeline View"


class TestViewsValidation:
    """Test views list validation."""

    def test_neither_object_nor_list_fails(self):
        """views list without --object or --list should fail."""
        result = runner.invoke(app, ["--json", "views", "list"])
        assert result.exit_code != 0

    def test_both_object_and_list_fails(self):
        """views list with both --object and --list should fail."""
        result = runner.invoke(
            app, ["--json", "views", "list", "--object", "people", "--list", "deals"]
        )
        assert result.exit_code != 0
