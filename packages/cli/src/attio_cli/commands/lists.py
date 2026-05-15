"""Lists commands: list, get, create, update."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(no_args_is_help=True)

LIST_COLUMNS = [
    {"header": "ID", "accessor": lambda l: l.get("list_id", ""), "no_wrap": True},
    {"header": "Slug", "accessor": lambda l: l.get("api_slug", "")},
    {"header": "Name", "accessor": lambda l: l.get("name", "")},
    {"header": "Parent Object", "accessor": lambda l: str(l.get("parent_object", ""))},
    {"header": "Created", "accessor": lambda l: l.get("created_at", "")[:10] if l.get("created_at") else ""},
]


def _list_to_dict(lst: object) -> dict:
    """Convert an AttioList model to a simple dict."""
    result = {}
    if hasattr(lst, "id"):
        lid = lst.id  # type: ignore[union-attr]
        result["list_id"] = getattr(lid, "list_id", str(lid))
    result["api_slug"] = getattr(lst, "api_slug", "")
    result["name"] = getattr(lst, "name", "")
    result["parent_object"] = getattr(lst, "parent_object", "")
    result["workspace_access"] = getattr(lst, "workspace_access", "")
    result["created_at"] = str(getattr(lst, "created_at", ""))
    return result


@app.command("list")
def list_lists(ctx: typer.Context) -> None:
    """List all lists in the workspace."""
    client = get_client(ctx)
    try:
        result = client.lists.list()
        data = [_list_to_dict(l) for l in result.data]
        output_list(data, LIST_COLUMNS, ctx, title="Lists")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    list_slug: str = typer.Argument(help="List slug or ID."),
) -> None:
    """Get a list definition by slug or ID."""
    client = get_client(ctx)
    try:
        lst = client.lists.get(list_slug)
        data = _list_to_dict(lst)
        output_single(data, ctx, title=f"List {list_slug}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Option(..., help="List display name."),
    api_slug: str = typer.Option(..., help="API slug for the list."),
    parent_object: str = typer.Option(..., help="Parent object slug (e.g., 'people')."),
    workspace_access: Optional[str] = typer.Option(None, help="Workspace access level."),
) -> None:
    """Create a new list."""
    client = get_client(ctx)
    try:
        lst = client.lists.create(
            name=name,
            api_slug=api_slug,
            parent_object=parent_object,
            workspace_access=workspace_access,
        )
        data = _list_to_dict(lst)
        output_single(data, ctx, title="Created List")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    list_slug: str = typer.Argument(help="List slug or ID to update."),
    name: Optional[str] = typer.Option(None, help="New display name."),
    api_slug_new: Optional[str] = typer.Option(None, "--api-slug", help="New API slug."),
    workspace_access: Optional[str] = typer.Option(None, help="New workspace access level."),
) -> None:
    """Update an existing list."""
    client = get_client(ctx)
    try:
        lst = client.lists.update(
            list_slug,
            name=name,
            api_slug=api_slug_new,
            workspace_access=workspace_access,
        )
        data = _list_to_dict(lst)
        output_single(data, ctx, title="Updated List")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
