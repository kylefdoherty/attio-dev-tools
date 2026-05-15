"""Attributes commands: list, get, create, update."""

from __future__ import annotations

import json
from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(name="attributes", help="Manage object and list attributes.", no_args_is_help=True)

ATTRIBUTE_COLUMNS = [
    {"header": "Slug", "accessor": lambda a: a.get("api_slug", "")},
    {"header": "Title", "accessor": lambda a: a.get("title", "")},
    {"header": "Type", "accessor": lambda a: a.get("type", "")},
    {"header": "System?", "accessor": lambda a: str(a.get("is_system_attribute", ""))},
    {"header": "Required?", "accessor": lambda a: str(a.get("is_required", ""))},
    {"header": "Unique?", "accessor": lambda a: str(a.get("is_unique", ""))},
    {"header": "Archived?", "accessor": lambda a: str(a.get("is_archived", ""))},
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


def _attribute_to_dict(attr: object) -> dict:
    """Convert an Attribute model to a simple dict."""
    result: dict = {}
    if hasattr(attr, "id"):
        aid = attr.id  # type: ignore[union-attr]
        result["attribute_id"] = getattr(aid, "attribute_id", str(aid))
    result["title"] = getattr(attr, "title", "")
    result["description"] = getattr(attr, "description", None)
    result["api_slug"] = getattr(attr, "api_slug", "")
    result["type"] = getattr(attr, "type", "")
    result["is_system_attribute"] = getattr(attr, "is_system_attribute", False)
    result["is_writable"] = getattr(attr, "is_writable", False)
    result["is_required"] = getattr(attr, "is_required", False)
    result["is_unique"] = getattr(attr, "is_unique", False)
    result["is_multiselect"] = getattr(attr, "is_multiselect", False)
    result["is_archived"] = getattr(attr, "is_archived", False)
    result["created_at"] = str(getattr(attr, "created_at", ""))
    return result


@app.command("list")
def list_attributes(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    all_results: bool = typer.Option(False, "--all", help="Fetch all results."),
) -> None:
    """List all attributes on an object or list."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        if all_results:
            from attio_cli.commands._record_helpers import collect_offset_pages

            items = collect_offset_pages(lambda off, lim: client.attributes.list(
                target, target_id, limit=lim, offset=off,
            ))
            data = [_attribute_to_dict(a) for a in items]
            output_list(data, ATTRIBUTE_COLUMNS, ctx, title="Attributes (all)")
            return

        result = client.attributes.list(target, target_id)
        data = [_attribute_to_dict(a) for a in result.data]
        output_list(data, ATTRIBUTE_COLUMNS, ctx, title="Attributes")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    attribute: str = typer.Argument(help="Attribute slug or ID."),
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
) -> None:
    """Get an attribute by slug or ID."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        attr = client.attributes.get(target, target_id, attribute)
        data = _attribute_to_dict(attr)
        output_single(data, ctx, title=f"Attribute {attribute}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    title: str = typer.Option(..., "--title", help="Attribute title."),
    slug: str = typer.Option(..., "--slug", help="API slug for the attribute."),
    type: str = typer.Option(..., "--type", help="Attribute type (e.g., text, number, currency)."),
    description: Optional[str] = typer.Option(None, "--description", help="Attribute description."),
    required: bool = typer.Option(False, "--required/--no-required", help="Whether the attribute is required."),
    unique: bool = typer.Option(False, "--unique/--no-unique", help="Whether the attribute is unique."),
    multiselect: bool = typer.Option(False, "--multiselect/--no-multiselect", help="Whether the attribute allows multiselect."),
    config: Optional[str] = typer.Option(None, "--config", help="JSON config object."),
) -> None:
    """Create a new attribute on an object or list."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        config_obj = None
        if config:
            try:
                config_obj = json.loads(config)
            except json.JSONDecodeError as exc:
                raise typer.BadParameter(f"--config must be valid JSON: {exc}")
        attr = client.attributes.create(
            target,
            target_id,
            title=title,
            api_slug=slug,
            type=type,
            description=description,
            is_required=required,
            is_unique=unique,
            is_multiselect=multiselect,
            config=config_obj,
        )
        data = _attribute_to_dict(attr)
        output_single(data, ctx, title="Created Attribute")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    attribute: str = typer.Argument(help="Attribute slug or ID to update."),
    object: Optional[str] = typer.Option(None, "--object", help="Object slug or ID."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug or ID."),
    title: Optional[str] = typer.Option(None, "--title", help="New attribute title."),
    description: Optional[str] = typer.Option(None, "--description", help="New description."),
    required: Optional[bool] = typer.Option(None, "--required/--no-required", help="Whether the attribute is required."),
    unique: Optional[bool] = typer.Option(None, "--unique/--no-unique", help="Whether the attribute is unique."),
    multiselect: Optional[bool] = typer.Option(None, "--multiselect/--no-multiselect", help="Whether the attribute allows multiselect."),
    archived: Optional[bool] = typer.Option(None, "--archived/--no-archived", help="Whether the attribute is archived."),
) -> None:
    """Update an existing attribute on an object or list."""
    target, target_id = _resolve_target(object, list_)
    client = get_client(ctx)
    try:
        attr = client.attributes.update(
            target,
            target_id,
            attribute,
            title=title,
            description=description,
            is_required=required,
            is_unique=unique,
            is_multiselect=multiselect,
            is_archived=archived,
        )
        data = _attribute_to_dict(attr)
        output_single(data, ctx, title="Updated Attribute")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
