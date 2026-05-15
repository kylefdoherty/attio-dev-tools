"""Companies commands: list, get, create, update, upsert, delete, search."""

from __future__ import annotations

import sys
from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli.commands._record_helpers import (
    COMPANIES_COLUMNS,
    parse_json_option,
    record_to_dict,
)

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_companies(
    ctx: typer.Context,
    limit: int = typer.Option(25, help="Maximum number of results."),
    offset: int = typer.Option(0, help="Pagination offset."),
    filter: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON."),
    sort: Optional[str] = typer.Option(None, help="Sort by attribute slug."),
    sort_direction: str = typer.Option("asc", help="Sort direction: asc or desc."),
) -> None:
    """List company records with optional filtering and sorting."""
    client = get_client(ctx)
    try:
        filter_obj = parse_json_option(filter)
        if filter_obj or sort:
            from attio.models.records import Sort as SortModel

            sorts = [SortModel(attribute=sort, direction=sort_direction)] if sort else None
            result = client.companies.query(filter=filter_obj, sorts=sorts, limit=limit, offset=offset)
        else:
            result = client.companies.list(limit=limit, offset=offset)
        data = [record_to_dict(r) for r in result.data]
        output_list(data, COMPANIES_COLUMNS, ctx, title="Companies")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to retrieve."),
) -> None:
    """Get a company by record ID."""
    client = get_client(ctx)
    try:
        record = client.companies.get(record_id)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"Company {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
) -> None:
    """Create a new company record."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        record = client.companies.create(values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Created Company")
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
    """Update an existing company record."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        record = client.companies.update(record_id, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Updated Company")
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
    """Create or update a company by matching attribute."""
    client = get_client(ctx)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        record = client.companies.upsert(matching_attribute=matching_attribute, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title="Upserted Company")
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
    """Delete a company record."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete company {record_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.companies.delete(record_id)
        output_success(f"Deleted company {record_id}", ctx)
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
    """Search company records."""
    client = get_client(ctx)
    try:
        result = client.records.global_search(query=query, objects=["companies"], limit=limit)
        data = [
            {"record_id": r.id.record_id, "text": r.record_text, "object": r.object_slug}
            for r in result.data
        ]
        columns = [
            {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
            {"header": "Match", "accessor": lambda r: r.get("text", "")},
        ]
        output_list(data, columns, ctx, title="Company Search Results")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
