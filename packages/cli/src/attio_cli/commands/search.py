"""Global search command: search across all objects."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list

app = typer.Typer(invoke_without_command=True, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def search(
    ctx: typer.Context,
    query: str = typer.Argument(help="Search query string."),
    limit: int = typer.Option(25, help="Maximum number of results."),
    objects_filter: Optional[str] = typer.Option(
        None, "--objects", help="Comma-separated object slugs to search (default: all standard objects)."
    ),
) -> None:
    """Search across all objects in the workspace."""
    client = get_client(ctx)
    try:
        if objects_filter:
            target_objects = [o.strip() for o in objects_filter.split(",")]
        else:
            target_objects = ["people", "companies", "deals"]

        result = client.records.global_search(query=query, objects=target_objects, limit=limit)
        data = [
            {
                "record_id": r.id.record_id,
                "text": r.record_text,
                "object": r.object_slug,
            }
            for r in result.data
        ]
        columns = [
            {"header": "Object", "accessor": lambda r: r.get("object", "")},
            {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
            {"header": "Match", "accessor": lambda r: r.get("text", "")},
        ]
        output_list(data, columns, ctx, title="Search Results")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
