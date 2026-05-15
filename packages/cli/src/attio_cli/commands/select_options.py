"""Select options commands: list, create, update."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(name="select-options", help="Manage select attribute options.", no_args_is_help=True)

SELECT_OPTION_COLUMNS = [
    {"header": "Option ID", "accessor": lambda o: o.get("option_id", ""), "no_wrap": True},
    {"header": "Title", "accessor": lambda o: o.get("title", "")},
    {"header": "Archived?", "accessor": lambda o: str(o.get("is_archived", ""))},
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


def _option_to_dict(opt: object) -> dict:
    """Convert a SelectOption model to a simple dict."""
    result: dict = {}
    if hasattr(opt, "id"):
        oid = opt.id  # type: ignore[union-attr]
        result["option_id"] = getattr(oid, "option_id", str(oid))
    result["title"] = getattr(opt, "title", "")
    result["is_archived"] = getattr(opt, "is_archived", False)
    return result


@app.command("list")
def list_options(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
) -> None:
    """List all select options for an attribute."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        result = client.select_options.list(target, target_id, attribute)
        data = [_option_to_dict(o) for o in result.data]
        output_list(data, SELECT_OPTION_COLUMNS, ctx, title="Select Options")
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
    title: str = typer.Option(..., "--title", help="Title for the new option."),
) -> None:
    """Create a new select option for an attribute."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        opt = client.select_options.create(target, target_id, attribute, title=title)
        data = _option_to_dict(opt)
        output_single(data, ctx, title="Created Select Option")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    option_id: str = typer.Argument(help="The option ID to update."),
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
    title: Optional[str] = typer.Option(None, "--title", help="New title for the option."),
    archived: Optional[bool] = typer.Option(None, "--archived/--no-archived", help="Whether the option is archived."),
) -> None:
    """Update an existing select option."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        opt = client.select_options.update(
            target,
            target_id,
            attribute,
            option_id,
            title=title,
            is_archived=archived,
        )
        data = _option_to_dict(opt)
        output_single(data, ctx, title="Updated Select Option")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
