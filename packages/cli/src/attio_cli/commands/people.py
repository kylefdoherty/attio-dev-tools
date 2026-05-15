"""People commands: list, get, create, update, upsert, delete, search, append, values, entries."""

from __future__ import annotations

import sys
from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli.commands._record_helpers import (
    ENTRY_LIST_COLUMNS,
    PEOPLE_COLUMNS,
    VALUE_COLUMNS,
    parse_json_option,
    record_to_dict,
)

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_people(
    ctx: typer.Context,
    limit: int = typer.Option(25, help="Maximum number of results."),
    offset: int = typer.Option(0, help="Pagination offset."),
    filter: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON."),
    sort: Optional[str] = typer.Option(None, help="Sort by attribute slug."),
    sort_direction: str = typer.Option("asc", help="Sort direction: asc or desc."),
) -> None:
    """List people records with optional filtering and sorting."""
    client = get_client(ctx)
    try:
        filter_obj = parse_json_option(filter)
        if filter_obj or sort:
            from attio.models.records import Sort as SortModel

            sorts = [SortModel(attribute=sort, direction=sort_direction)] if sort else None
            result = client.people.query(filter=filter_obj, sorts=sorts, limit=limit, offset=offset)
        else:
            result = client.people.list(limit=limit, offset=offset)
        data = [record_to_dict(r) for r in result.data]
        output_list(data, PEOPLE_COLUMNS, ctx, title="People")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to retrieve."),
) -> None:
    """Get a person by record ID."""
    client = get_client(ctx)
    try:
        record = client.people.get(record_id)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"Person {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Create a new person record."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        record = client.people.create(values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Created Person")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to update."),
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Update an existing person record."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        record = client.people.update(record_id, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Updated Person")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def upsert(
    ctx: typer.Context,
    matching_attribute: str = typer.Option(..., "--matching-attribute", help="Attribute slug to match on."),
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Create or update a person by matching attribute."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        record = client.people.upsert(matching_attribute=matching_attribute, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Upserted Person")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a person record."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete person {record_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.people.delete(record_id)
        output_success(f"Deleted person {record_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def search(
    ctx: typer.Context,
    query: str = typer.Argument(help="Search query string."),
    limit: int = typer.Option(25, help="Maximum number of results."),
) -> None:
    """Search people records."""
    client = get_client(ctx)
    try:
        result = client.records.global_search(query=query, objects=["people"], limit=limit)
        data = [
            {"record_id": r.id.record_id, "text": r.record_text, "object": r.object_slug}
            for r in result.data
        ]
        columns = [
            {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
            {"header": "Match", "accessor": lambda r: r.get("text", "")},
        ]
        output_list(data, columns, ctx, title="People Search Results")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def append(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="Record ID to append values to."),
    values: str = typer.Option(..., "--values", help="JSON values to append."),
) -> None:
    """Append values to a record (adds to multiselect fields without overwriting)."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        result = client.people.append(record_id, values=values_obj)
        output_single(record_to_dict(result), ctx, title=f"Appended Person {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command("values")
def get_values(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="Record ID."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
    show_historic: bool = typer.Option(False, "--show-historic", help="Include historical values."),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
    offset: int = typer.Option(0, "--offset", help="Pagination offset."),
) -> None:
    """Get attribute values for a record."""
    client = get_client(ctx)
    try:
        result = client.people.get_attribute_values(
            record_id, attribute, show_historic=show_historic, limit=limit, offset=offset
        )
        output_list(
            [v.model_dump(mode="json") for v in result.data],
            VALUE_COLUMNS,
            ctx,
            title=f"Values: {attribute}",
        )
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command("entries")
def list_entries(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="Record ID."),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
    offset: int = typer.Option(0, "--offset", help="Pagination offset."),
) -> None:
    """List entries (list memberships) for a record."""
    client = get_client(ctx)
    try:
        result = client.people.list_entries(record_id, limit=limit, offset=offset)
        entry_dicts = [
            {
                "list_id": e.list_id,
                "list_slug": e.list_api_slug,
                "entry_id": e.entry_id,
                "created_at": str(e.created_at),
            }
            for e in result.data
        ]
        output_list(entry_dicts, ENTRY_LIST_COLUMNS, ctx, title="Record Entries")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
