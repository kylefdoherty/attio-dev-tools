"""Direct unit tests for the _record_factory module.

Tests the factory's helper functions and the Typer apps it produces,
exercised through the CLI runner rather than by inspecting internals.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from attio_cli.commands._record_factory import (
    _get_sub_client,
    _plural_title,
    _singular,
    create_record_commands,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers shared across test classes
# ---------------------------------------------------------------------------


def _make_mock_record(record_id="rec_factory_1"):
    """Create a minimal mock record for factory tests."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = record_id
    record.id.object_id = "obj_test"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = f"https://app.attio.com/record/{record_id}"
    record.values = {
        "name": [MagicMock(**{
            "model_dump.return_value": {"value": "Test Record", "attribute_type": "text"},
        })],
    }
    return record


def _wrap_in_app(factory_app: typer.Typer, name: str = "test") -> typer.Typer:
    """Wrap a factory-produced Typer in a parent app so the runner can invoke it."""
    parent = typer.Typer()
    parent.add_typer(factory_app, name=name)

    @parent.callback()
    def main(
        ctx: typer.Context,
        json_output: bool = typer.Option(False, "--json", help="JSON output."),
    ) -> None:
        ctx.ensure_object(dict)
        ctx.obj["json"] = json_output

    return parent


def _command_names(app: typer.Typer) -> set[str]:
    """Extract all command names from a Typer app.

    Typer stores the explicit name in cmd.name when provided (e.g.
    ``@app.command("list")``), but falls back to the callback function name
    when no explicit name is given (e.g. ``@app.command()`` on ``def get``).
    """
    names: set[str] = set()
    for cmd in app.registered_commands:
        name = cmd.name or (cmd.callback.__name__ if cmd.callback else None)
        if name:
            names.add(name)
    return names


# =========================================================================
# 1. _singular() — name derivation
# =========================================================================


class TestSingular:
    """_singular() derives a singular display name from an object slug."""

    def test_people_to_person(self):
        assert _singular("people") == "person"

    def test_companies_to_company(self):
        assert _singular("companies") == "company"

    def test_deals_to_deal(self):
        assert _singular("deals") == "deal"

    def test_custom_things_strips_trailing_s(self):
        assert _singular("custom_things") == "custom_thing"

    def test_no_trailing_s_unchanged(self):
        assert _singular("notrailing") == "notrailing"

    def test_single_char_s(self):
        assert _singular("s") == ""

    def test_empty_string(self):
        assert _singular("") == ""


# =========================================================================
# 2. _plural_title() — formatting
# =========================================================================


class TestPluralTitle:
    """_plural_title() capitalises and un-slugifies an object slug."""

    def test_people(self):
        assert _plural_title("people") == "People"

    def test_custom_object_underscore(self):
        assert _plural_title("custom_object") == "Custom Object"

    def test_custom_object_hyphen(self):
        assert _plural_title("custom-object") == "Custom Object"

    def test_deals(self):
        assert _plural_title("deals") == "Deals"

    def test_already_single_word(self):
        assert _plural_title("companies") == "Companies"


# =========================================================================
# 3. _get_sub_client() — routing
# =========================================================================


class TestGetSubClient:
    """_get_sub_client() routes to dedicated sub-clients for known slugs."""

    def test_known_slug_people(self):
        client = MagicMock()
        client.people = MagicMock(name="people_sub")
        result = _get_sub_client(client, "people")
        assert result is client.people

    def test_known_slug_companies(self):
        client = MagicMock()
        client.companies = MagicMock(name="companies_sub")
        result = _get_sub_client(client, "companies")
        assert result is client.companies

    def test_known_slug_deals(self):
        client = MagicMock()
        client.deals = MagicMock(name="deals_sub")
        result = _get_sub_client(client, "deals")
        assert result is client.deals

    def test_unknown_slug_falls_back_to_records(self):
        client = MagicMock(spec=[])  # no attributes by default
        client.records = MagicMock(name="records_sub")
        result = _get_sub_client(client, "widgets")
        assert result is client.records


# =========================================================================
# 4. Factory output — expected commands
# =========================================================================


class TestFactoryCommands:
    """create_record_commands() produces a Typer app with the expected sub-commands."""

    EXPECTED_COMMANDS = {"list", "get", "create", "update", "upsert", "delete", "search", "append", "values", "entries"}

    def test_known_object_has_all_commands(self):
        """A known-object factory app should register all standard commands."""
        factory_app = create_record_commands("people")
        registered = _command_names(factory_app)
        assert self.EXPECTED_COMMANDS.issubset(registered), (
            f"Missing commands: {self.EXPECTED_COMMANDS - registered}"
        )

    def test_generic_object_has_all_commands(self):
        """A generic factory app should also register all standard commands."""
        factory_app = create_record_commands("records", is_generic=True)
        registered = _command_names(factory_app)
        assert self.EXPECTED_COMMANDS.issubset(registered), (
            f"Missing commands: {self.EXPECTED_COMMANDS - registered}"
        )

    def test_no_args_shows_help(self):
        """Invoking the factory app with no args should show usage info."""
        factory_app = create_record_commands("people")
        parent = _wrap_in_app(factory_app)
        result = runner.invoke(parent, ["test"])
        # no_args_is_help causes Typer to exit with code 0 *or* 2 depending
        # on version; the important thing is that help text is shown.
        assert "Usage" in result.output or "Commands" in result.output


# =========================================================================
# 5. Generic mode — --object flag
# =========================================================================


class TestGenericMode:
    """Generic mode adds --object to every command and routes through client.records."""

    def test_list_requires_object_flag(self):
        """In generic mode, list without --object should fail."""
        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)
        result = runner.invoke(parent, ["--json", "test", "list"])
        assert result.exit_code != 0

    def test_get_requires_object_flag(self):
        """In generic mode, get without --object should fail."""
        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)
        result = runner.invoke(parent, ["--json", "test", "get", "rec_123"])
        assert result.exit_code != 0

    def test_list_with_object_routes_through_records(self):
        """Generic list --object=widgets should call client.records.list('widgets', ...)."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_record()]

        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                parent, ["--json", "test", "list", "--object", "widgets"]
            )
            assert result.exit_code == 0, result.output
            mock_client.records.list.assert_called_once_with("widgets", limit=25, offset=0)

    def test_get_with_object_routes_through_records(self):
        """Generic get --object=widgets should call client.records.get('widgets', record_id)."""
        mock_record = _make_mock_record()

        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.get.return_value = mock_record
            mock_gc.return_value = mock_client

            result = runner.invoke(
                parent, ["--json", "test", "get", "rec_123", "--object", "widgets"]
            )
            assert result.exit_code == 0, result.output
            mock_client.records.get.assert_called_once_with("widgets", "rec_123")

    def test_create_with_object_routes_through_records(self):
        """Generic create --object should call client.records.create(slug, ...)."""
        mock_record = _make_mock_record(record_id="rec_new")

        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.create.return_value = mock_record
            mock_gc.return_value = mock_client

            result = runner.invoke(
                parent,
                [
                    "--json", "test", "create",
                    "--object", "widgets",
                    "--values", '{"name": [{"value": "New"}]}',
                ],
            )
            assert result.exit_code == 0, result.output
            mock_client.records.create.assert_called_once()
            call_args = mock_client.records.create.call_args
            assert call_args[0][0] == "widgets"

    def test_delete_with_object_routes_through_records(self):
        """Generic delete --object --yes should call client.records.delete(slug, id)."""
        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.records.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(
                parent,
                ["--json", "test", "delete", "rec_123", "--object", "widgets", "--yes"],
            )
            assert result.exit_code == 0, result.output
            mock_client.records.delete.assert_called_once_with("widgets", "rec_123")


# =========================================================================
# 5b. Known-object mode — no --object flag, dedicated sub-client
# =========================================================================


class TestKnownObjectMode:
    """Known-object mode uses dedicated sub-clients (client.people, etc.)."""

    def test_list_uses_dedicated_sub_client(self):
        """people list should call client.people.list(...)."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_record()]

        factory_app = create_record_commands("people")
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(parent, ["--json", "test", "list"])
            assert result.exit_code == 0, result.output
            mock_client.people.list.assert_called_once_with(limit=25, offset=0)

    def test_get_uses_dedicated_sub_client(self):
        """people get should call client.people.get(record_id)."""
        mock_record = _make_mock_record()

        factory_app = create_record_commands("people")
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.get.return_value = mock_record
            mock_gc.return_value = mock_client

            result = runner.invoke(parent, ["--json", "test", "get", "rec_123"])
            assert result.exit_code == 0, result.output
            mock_client.people.get.assert_called_once_with("rec_123")

    def test_delete_uses_dedicated_sub_client(self):
        """people delete --yes should call client.people.delete(record_id)."""
        factory_app = create_record_commands("people")
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.people.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(parent, ["--json", "test", "delete", "rec_123", "--yes"])
            assert result.exit_code == 0, result.output
            mock_client.people.delete.assert_called_once_with("rec_123")


# =========================================================================
# 6. Extra commands — extra_commands callback
# =========================================================================


class TestExtraCommands:
    """extra_commands callback attaches additional sub-commands to the app."""

    def test_extra_command_is_registered(self):
        """A callback that adds a 'move' command should make it available."""

        def add_move(app: typer.Typer) -> None:
            @app.command()
            def move(ctx: typer.Context) -> None:
                """Move a record."""
                print("moved")

        factory_app = create_record_commands("deals", extra_commands=add_move)
        registered = _command_names(factory_app)
        assert "move" in registered

    def test_extra_command_is_callable(self):
        """The extra 'move' command should be invocable through the CLI."""

        def add_move(app: typer.Typer) -> None:
            @app.command()
            def move(ctx: typer.Context) -> None:
                """Move a record."""
                print("moved!")

        factory_app = create_record_commands("deals", extra_commands=add_move)
        parent = _wrap_in_app(factory_app)

        result = runner.invoke(parent, ["test", "move"])
        assert result.exit_code == 0
        assert "moved!" in result.output

    def test_no_extra_commands_by_default(self):
        """Without extra_commands, only the standard set is registered."""
        factory_app = create_record_commands("people")
        registered = _command_names(factory_app)
        assert "move" not in registered


# =========================================================================
# 7. Dynamic column integration — generic list uses get_columns_for_object
# =========================================================================


class TestDynamicColumns:
    """Generic mode list command uses get_columns_for_object for custom objects."""

    def test_generic_list_calls_get_columns_for_object(self):
        """Generic list should call get_columns_for_object(slug, client) for column resolution."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_record()]

        factory_app = create_record_commands("records", is_generic=True)
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc, \
             patch("attio_cli.commands._record_factory.get_columns_for_object") as mock_cols:
            mock_client = MagicMock()
            mock_client.records.list.return_value = mock_response
            mock_gc.return_value = mock_client
            # Return generic columns from the mock
            mock_cols.return_value = [
                {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
                {"header": "Name", "accessor": lambda r: r.get("name", "")},
            ]

            result = runner.invoke(
                parent, ["--json", "test", "list", "--object", "my_custom_obj"]
            )
            assert result.exit_code == 0, result.output
            mock_cols.assert_called_once_with("my_custom_obj", mock_client)

    def test_known_object_list_does_not_call_get_columns_for_object(self):
        """Non-generic list should NOT call get_columns_for_object (columns are static)."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_record()]

        factory_app = create_record_commands("people")
        parent = _wrap_in_app(factory_app)

        with patch("attio_cli.commands._record_factory.get_client") as mock_gc, \
             patch("attio_cli.commands._record_factory.get_columns_for_object") as mock_cols:
            mock_client = MagicMock()
            mock_client.people.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(parent, ["--json", "test", "list"])
            assert result.exit_code == 0, result.output
            mock_cols.assert_not_called()
