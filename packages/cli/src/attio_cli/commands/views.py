"""Views commands: list saved views on objects or lists."""

from __future__ import annotations

from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list

app = typer.Typer(name="views", help="List saved views on objects or lists.", no_args_is_help=True)

VIEW_COLUMNS = [
    {"header": "View ID", "accessor": lambda v: v.get("view_id", ""), "no_wrap": True},
    {"header": "Title", "accessor": lambda v: v.get("title", "")},
    {"header": "Created", "accessor": lambda v: v.get("created_at", "")[:10] if v.get("created_at") else ""},
]


def _view_to_dict(v: Any) -> dict[str, Any]:
    """Convert a View model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(v, "id"):
        vid = v.id
        result["view_id"] = getattr(vid, "view_id", str(vid))
        result["object_id"] = getattr(vid, "object_id", None)
        result["list_id"] = getattr(vid, "list_id", None)
    result["title"] = getattr(v, "title", "")
    result["created_at"] = str(getattr(v, "created_at", ""))
    return result


@app.command("list")
def list_views(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug to list views for."),
    list_slug: Optional[str] = typer.Option(None, "--list", help="List slug to list views for."),
    show_archived: bool = typer.Option(False, "--show-archived", help="Include archived views."),
    limit: Optional[int] = typer.Option(None, help="Maximum number of results."),
    cursor: Optional[str] = typer.Option(None, help="Pagination cursor."),
) -> None:
    """List views for an object or list. Exactly one of --object or --list is required."""
    if object and list_slug:
        raise typer.BadParameter("Specify only one of --object or --list, not both.")
    if not object and not list_slug:
        raise typer.BadParameter("Specify one of --object or --list.")

    client = get_client(ctx)
    try:
        if object:
            result = client.views.list_for_object(
                object,
                show_archived=show_archived,
                limit=limit,
                cursor=cursor,
            )
        else:
            result = client.views.list_for_list(
                list_slug,  # type: ignore[arg-type]
                show_archived=show_archived,
                limit=limit,
                cursor=cursor,
            )
        data = [_view_to_dict(v) for v in result.data]
        output_list(data, VIEW_COLUMNS, ctx, title="Views")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
