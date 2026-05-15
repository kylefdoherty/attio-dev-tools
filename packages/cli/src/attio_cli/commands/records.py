"""Generic records commands for any object type (including custom objects).

Requires --object flag to specify the target object slug.
"""

from __future__ import annotations

import sys
from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli._values import expand_values
from attio_cli.commands._record_helpers import (
    ENTRY_LIST_COLUMNS,
    GENERIC_COLUMNS,
    VALUE_COLUMNS,
    parse_json_option,
    record_to_dict,
)

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_records(
    ctx: typer.Context,
    object: str = typer.Option(..., "--object", help="Object slug (e.g., people, companies, or custom)."),
    limit: int = typer.Option(25, help="Maximum number of results."),
    offset: int = typer.Option(0, help="Pagination offset."),
    filter: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON."),
    sort: Optional[str] = typer.Option(None, help="Sort by attribute slug."),
    sort_direction: str = typer.Option("asc", help="Sort direction: asc or desc."),
    all_results: bool = typer.Option(False, "--all", help="Fetch all results."),
) -> None:
    """List records for a given object with optional filtering and sorting."""
    client = get_client(ctx)
    try:
        if all_results:
            filter_obj = parse_json_option(filter) if filter else None
            iterator = client.records.query_all(object, filter=filter_obj)
            all_data = [record_to_dict(r) for r in iterator]
            output_list(all_data, GENERIC_COLUMNS, ctx, title=f"Records ({object}) (all)")
            return

        filter_obj = parse_json_option(filter)
        if filter_obj or sort:
            from attio.models.records import Sort as SortModel

            sorts = [SortModel(attribute=sort, direction=sort_direction)] if sort else None
            result = client.records.query(object, filter=filter_obj, sorts=sorts, limit=limit, offset=offset)
        else:
            result = client.records.list(object, limit=limit, offset=offset)
        data = [record_to_dict(r) for r in result.data]
        output_list(data, GENERIC_COLUMNS, ctx, title=f"Records ({object})")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to retrieve."),
    object: str = typer.Option(..., "--object", help="Object slug."),
) -> None:
    """Get a record by ID."""
    client = get_client(ctx)
    try:
        record = client.records.get(object, record_id)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"Record {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    object: str = typer.Option(..., "--object", help="Object slug."),
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Create a new record."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, object, values_obj)
        record = client.records.create(object, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Created Record")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to update."),
    object: str = typer.Option(..., "--object", help="Object slug."),
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Update an existing record."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, object, values_obj)
        record = client.records.update(object, record_id, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Updated Record")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def upsert(
    ctx: typer.Context,
    object: str = typer.Option(..., "--object", help="Object slug."),
    matching_attribute: str = typer.Option(..., "--matching-attribute", help="Attribute slug to match on."),
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Create or update a record by matching attribute."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, object, values_obj)
        record = client.records.upsert(object, matching_attribute=matching_attribute, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Upserted Record")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to delete."),
    object: str = typer.Option(..., "--object", help="Object slug."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a record."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete record {record_id} from {object}?", abort=True)

    client = get_client(ctx)
    try:
        client.records.delete(object, record_id)
        output_success(f"Deleted record {record_id} from {object}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def search(
    ctx: typer.Context,
    query: str = typer.Argument(help="Search query string."),
    object: str = typer.Option(..., "--object", help="Object slug to search within."),
    limit: int = typer.Option(25, help="Maximum number of results."),
) -> None:
    """Search records within a specific object."""
    client = get_client(ctx)
    try:
        result = client.records.global_search(query=query, objects=[object], limit=limit)
        data = [
            {"record_id": r.id.record_id, "text": r.record_text, "object": r.object_slug}
            for r in result.data
        ]
        columns = [
            {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
            {"header": "Match", "accessor": lambda r: r.get("text", "")},
            {"header": "Object", "accessor": lambda r: r.get("object", "")},
        ]
        output_list(data, columns, ctx, title=f"Search Results ({object})")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def append(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="Record ID."),
    object: str = typer.Option(..., "--object", help="Object slug."),
    values: str = typer.Option(..., "--values", help="JSON values to append."),
) -> None:
    """Append values to a record (adds to multiselect fields without overwriting)."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, object, values_obj)
        result = client.records.append(object, record_id, values=values_obj)
        output_single(record_to_dict(result), ctx, title=f"Appended Record {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command("values")
def get_values(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="Record ID."),
    object: str = typer.Option(..., "--object", help="Object slug."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
    show_historic: bool = typer.Option(False, "--show-historic", help="Include historical values."),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
    offset: int = typer.Option(0, "--offset", help="Pagination offset."),
) -> None:
    """Get attribute values for a record."""
    client = get_client(ctx)
    try:
        result = client.records.get_attribute_values(
            object, record_id, attribute, show_historic=show_historic, limit=limit, offset=offset
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
    object: str = typer.Option(..., "--object", help="Object slug."),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
    offset: int = typer.Option(0, "--offset", help="Pagination offset."),
) -> None:
    """List entries (list memberships) for a record."""
    client = get_client(ctx)
    try:
        result = client.records.list_entries(object, record_id, limit=limit, offset=offset)
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
