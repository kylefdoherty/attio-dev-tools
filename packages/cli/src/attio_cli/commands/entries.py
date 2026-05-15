"""Entries commands: list, get, create, update, upsert, delete."""

from __future__ import annotations

import json
import sys
from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli.commands._record_helpers import parse_json_option

app = typer.Typer(no_args_is_help=True)

ENTRY_COLUMNS = [
    {"header": "Entry ID", "accessor": lambda e: e.get("entry_id", ""), "no_wrap": True},
    {"header": "Record ID", "accessor": lambda e: e.get("parent_record_id", ""), "no_wrap": True},
    {"header": "Object", "accessor": lambda e: e.get("parent_object", "")},
    {"header": "Created", "accessor": lambda e: e.get("created_at", "")[:10] if e.get("created_at") else ""},
]


def _entry_to_dict(entry: Any) -> dict[str, Any]:
    """Convert an Entry model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(entry, "id"):
        eid = entry.id
        result["entry_id"] = getattr(eid, "entry_id", str(eid))
        result["list_id"] = getattr(eid, "list_id", "")
    result["parent_record_id"] = getattr(entry, "parent_record_id", "")
    result["parent_object"] = getattr(entry, "parent_object", "")
    result["created_at"] = str(getattr(entry, "created_at", ""))

    # Flatten entry_values
    entry_values = getattr(entry, "entry_values", {})
    if isinstance(entry_values, dict):
        for k, v in entry_values.items():
            if v and isinstance(v, list):
                first = v[0]
                if hasattr(first, "model_dump"):
                    first = first.model_dump(mode="json")
                result[k] = str(first) if first else ""
            else:
                result[k] = str(v)

    return result


@app.command("list")
def list_entries(
    ctx: typer.Context,
    list_slug: str = typer.Option(..., "--list", help="List slug or ID."),
    limit: int = typer.Option(25, help="Maximum number of results."),
    offset: int = typer.Option(0, help="Pagination offset."),
    filter: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON."),
) -> None:
    """List entries in a list."""
    client = get_client(ctx)
    try:
        filter_obj = parse_json_option(filter)
        if filter_obj:
            result = client.entries.query(list_slug, filter=filter_obj, limit=limit, offset=offset)
        else:
            result = client.entries.list(list_slug, limit=limit, offset=offset)
        data = [_entry_to_dict(e) for e in result.data]
        output_list(data, ENTRY_COLUMNS, ctx, title=f"Entries ({list_slug})")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    entry_id: str = typer.Argument(help="The entry ID to retrieve."),
    list_slug: str = typer.Option(..., "--list", help="List slug or ID."),
) -> None:
    """Get an entry by ID."""
    client = get_client(ctx)
    try:
        entry = client.entries.get(list_slug, entry_id)
        data = _entry_to_dict(entry)
        output_single(data, ctx, title=f"Entry {entry_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    list_slug: str = typer.Option(..., "--list", help="List slug or ID."),
    parent_record_id: str = typer.Option(..., "--record", help="Parent record ID."),
    parent_object: str = typer.Option(..., "--object", help="Parent object slug."),
    entry_values: Optional[str] = typer.Option(None, "--values", help="JSON entry values."),
) -> None:
    """Create a new entry in a list."""
    client = get_client(ctx)
    try:
        vals = parse_json_option(entry_values)
        entry = client.entries.create(
            list_slug,
            parent_record_id=parent_record_id,
            parent_object=parent_object,
            entry_values=vals,
        )
        data = _entry_to_dict(entry)
        output_single(data, ctx, title="Created Entry")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    entry_id: str = typer.Argument(help="The entry ID to update."),
    list_slug: str = typer.Option(..., "--list", help="List slug or ID."),
    entry_values: str = typer.Option(..., "--values", help="JSON entry values."),
) -> None:
    """Update an existing entry."""
    client = get_client(ctx)
    try:
        vals = parse_json_option(entry_values)
        if not vals:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        entry = client.entries.update(list_slug, entry_id, entry_values=vals)
        data = _entry_to_dict(entry)
        output_single(data, ctx, title="Updated Entry")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def upsert(
    ctx: typer.Context,
    list_slug: str = typer.Option(..., "--list", help="List slug or ID."),
    parent_record_id: str = typer.Option(..., "--record", help="Parent record ID."),
    parent_object: str = typer.Option(..., "--object", help="Parent object slug."),
    entry_values: Optional[str] = typer.Option(None, "--values", help="JSON entry values."),
) -> None:
    """Create or update an entry by parent record."""
    client = get_client(ctx)
    try:
        vals = parse_json_option(entry_values)
        entry = client.entries.upsert(
            list_slug,
            parent_record_id=parent_record_id,
            parent_object=parent_object,
            entry_values=vals,
        )
        data = _entry_to_dict(entry)
        output_single(data, ctx, title="Upserted Entry")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    entry_id: str = typer.Argument(help="The entry ID to delete."),
    list_slug: str = typer.Option(..., "--list", help="List slug or ID."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete an entry from a list."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete entry {entry_id} from {list_slug}?", abort=True)

    client = get_client(ctx)
    try:
        client.entries.delete(list_slug, entry_id)
        output_success(f"Deleted entry {entry_id} from {list_slug}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
