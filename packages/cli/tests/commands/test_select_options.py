"""Tests for the select-options commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


def _make_mock_option(option_id="opt_123", title="Option A"):
    """Create a mock SelectOption model."""
    opt = MagicMock()
    opt.id = MagicMock()
    opt.id.option_id = option_id
    opt.title = title
    opt.is_archived = False
    return opt


class TestSelectOptionsList:
    """Test the select-options list command."""

    def test_list_with_object(self):
        """select-options list --object should return options."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_option("opt_1", "Active"),
            _make_mock_option("opt_2", "Inactive"),
        ]

        with patch("attio_cli.commands.select_options.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.select_options.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "select-options", "list", "--object", "deals", "--attribute", "stage"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["title"] == "Active"
            mock_client.select_options.list.assert_called_once_with("objects", "deals", "stage")

    def test_list_with_list(self):
        """select-options list --list should return options for a list attribute."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_option()]

        with patch("attio_cli.commands.select_options.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.select_options.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "select-options", "list", "--list", "pipeline", "--attribute", "priority"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 1
            mock_client.select_options.list.assert_called_once_with("lists", "pipeline", "priority")

    def test_list_no_target_fails(self):
        """select-options list without --object or --list should fail."""
        with patch("attio_cli.commands.select_options.get_client") as mock_gc:
            mock_gc.return_value = MagicMock()
            result = runner.invoke(app, ["--json", "select-options", "list", "--attribute", "stage"])
            assert result.exit_code != 0


class TestSelectOptionsCreate:
    """Test the select-options create command."""

    def test_create_option(self):
        """select-options create should return the created option."""
        mock_opt = _make_mock_option(option_id="opt_new", title="New Option")

        with patch("attio_cli.commands.select_options.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.select_options.create.return_value = mock_opt
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "select-options", "create",
                    "--object", "deals",
                    "--attribute", "stage",
                    "--title", "New Option",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["title"] == "New Option"
            mock_client.select_options.create.assert_called_once_with("objects", "deals", "stage", title="New Option")


class TestSelectOptionsUpdate:
    """Test the select-options update command."""

    def test_update_option(self):
        """select-options update should return the updated option."""
        mock_opt = _make_mock_option()
        mock_opt.title = "Updated Option"

        with patch("attio_cli.commands.select_options.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.select_options.update.return_value = mock_opt
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "select-options", "update", "opt_123",
                    "--object", "deals",
                    "--attribute", "stage",
                    "--title", "Updated Option",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["title"] == "Updated Option"
            mock_client.select_options.update.assert_called_once_with(
                "objects", "deals", "stage", "opt_123",
                title="Updated Option", is_archived=None,
            )

    def test_update_archive_option(self):
        """select-options update --archived should archive an option."""
        mock_opt = _make_mock_option()
        mock_opt.is_archived = True

        with patch("attio_cli.commands.select_options.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.select_options.update.return_value = mock_opt
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "select-options", "update", "opt_123",
                    "--object", "deals",
                    "--attribute", "stage",
                    "--archived",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["is_archived"] is True
