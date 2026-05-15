"""Objects commands: list, get, create, update."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(no_args_is_help=True)

OBJECT_COLUMNS = [
    {"header": "ID", "accessor": lambda o: o.get("object_id", ""), "no_wrap": True},
    {"header": "Slug", "accessor": lambda o: o.get("api_slug", "")},
    {"header": "Singular", "accessor": lambda o: o.get("singular_noun", "")},
    {"header": "Plural", "accessor": lambda o: o.get("plural_noun", "")},
    {"header": "Created", "accessor": lambda o: o.get("created_at", "")[:10] if o.get("created_at") else ""},
]


def _object_to_dict(obj: object) -> dict:
    """Convert an Object model to a simple dict."""
    result = {}
    if hasattr(obj, "id"):
        oid = obj.id  # type: ignore[union-attr]
        result["object_id"] = getattr(oid, "object_id", str(oid))
    result["api_slug"] = getattr(obj, "api_slug", "")
    result["singular_noun"] = getattr(obj, "singular_noun", "")
    result["plural_noun"] = getattr(obj, "plural_noun", "")
    result["created_at"] = str(getattr(obj, "created_at", ""))
    return result


@app.command("list")
def list_objects(ctx: typer.Context) -> None:
    """List all objects in the workspace."""
    client = get_client(ctx)
    try:
        result = client.objects.list()
        data = [_object_to_dict(o) for o in result.data]
        output_list(data, OBJECT_COLUMNS, ctx, title="Objects")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    object_id: str = typer.Argument(help="Object slug or ID."),
) -> None:
    """Get an object definition by slug or ID."""
    client = get_client(ctx)
    try:
        obj = client.objects.get(object_id)
        data = _object_to_dict(obj)
        output_single(data, ctx, title=f"Object {object_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    api_slug: str = typer.Option(..., help="API slug for the new object."),
    singular_noun: str = typer.Option(..., help="Singular noun (e.g., 'project')."),
    plural_noun: str = typer.Option(..., help="Plural noun (e.g., 'projects')."),
) -> None:
    """Create a new custom object."""
    client = get_client(ctx)
    try:
        obj = client.objects.create(
            api_slug=api_slug,
            singular_noun=singular_noun,
            plural_noun=plural_noun,
        )
        data = _object_to_dict(obj)
        output_single(data, ctx, title="Created Object")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    object_id: str = typer.Argument(help="Object slug or ID to update."),
    singular_noun: Optional[str] = typer.Option(None, help="New singular noun."),
    plural_noun: Optional[str] = typer.Option(None, help="New plural noun."),
) -> None:
    """Update an existing object definition."""
    client = get_client(ctx)
    try:
        obj = client.objects.update(
            object_id,
            singular_noun=singular_noun,
            plural_noun=plural_noun,
        )
        data = _object_to_dict(obj)
        output_single(data, ctx, title="Updated Object")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
