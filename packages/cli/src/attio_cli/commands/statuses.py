"""Statuses commands: list, create, update."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(name="statuses", help="Manage status attribute options.", no_args_is_help=True)

STATUS_COLUMNS = [
    {"header": "Status ID", "accessor": lambda s: s.get("status_id", ""), "no_wrap": True},
    {"header": "Title", "accessor": lambda s: s.get("title", "")},
    {"header": "Celebration?", "accessor": lambda s: str(s.get("celebration_enabled", ""))},
    {"header": "Target Time", "accessor": lambda s: s.get("target_time_in_status", "") or ""},
    {"header": "Archived?", "accessor": lambda s: str(s.get("is_archived", ""))},
]


def _resolve_target(
    object: Optional[str],
    list_: Optional[str],
) -> tuple[str, str]:
    """Resolve --object/--list to (target, target_id). Exactly one must be provided."""
    if object and list_:
        raise typer.BadParameter("Provide either --object or --list, not both.")
    if not object and not list_:
        raise typer.BadParameter("One of --object or --list is required.")
    if object:
        return "objects", object
    return "lists", list_  # type: ignore[return-value]


def _status_to_dict(status: object) -> dict:
    """Convert a Status model to a simple dict."""
    result: dict = {}
    if hasattr(status, "id"):
        sid = status.id  # type: ignore[union-attr]
        result["status_id"] = getattr(sid, "status_id", str(sid))
    result["title"] = getattr(status, "title", "")
    result["is_archived"] = getattr(status, "is_archived", False)
    result["celebration_enabled"] = getattr(status, "celebration_enabled", False)
    result["target_time_in_status"] = getattr(status, "target_time_in_status", None)
    return result


@app.command("list")
def list_statuses(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
) -> None:
    """List all statuses for an attribute."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        result = client.statuses.list(target, target_id, attribute)
        data = [_status_to_dict(s) for s in result.data]
        output_list(data, STATUS_COLUMNS, ctx, title="Statuses")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
    title: str = typer.Option(..., "--title", help="Title for the new status."),
    celebration: bool = typer.Option(False, "--celebration/--no-celebration", help="Enable celebration for this status."),
    target_time: Optional[str] = typer.Option(None, "--target-time", help="Target time in status (e.g., P7D)."),
) -> None:
    """Create a new status for an attribute."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        status = client.statuses.create(
            target,
            target_id,
            attribute,
            title=title,
            celebration_enabled=celebration,
            target_time_in_status=target_time,
        )
        data = _status_to_dict(status)
        output_single(data, ctx, title="Created Status")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    status_id: str = typer.Argument(help="The status ID to update."),
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
    title: Optional[str] = typer.Option(None, "--title", help="New title for the status."),
    archived: Optional[bool] = typer.Option(None, "--archived/--no-archived", help="Whether the status is archived."),
    celebration: Optional[bool] = typer.Option(None, "--celebration/--no-celebration", help="Enable/disable celebration."),
    target_time: Optional[str] = typer.Option(None, "--target-time", help="Target time in status (e.g., P7D)."),
) -> None:
    """Update an existing status."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        status = client.statuses.update(
            target,
            target_id,
            attribute,
            status_id,
            title=title,
            is_archived=archived,
            celebration_enabled=celebration,
            target_time_in_status=target_time,
        )
        data = _status_to_dict(status)
        output_single(data, ctx, title="Updated Status")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
