"""Workspace commands: info, members."""

from __future__ import annotations

from typing import Any

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(no_args_is_help=True)


@app.command()
def info(ctx: typer.Context) -> None:
    """Show current workspace information."""
    client = get_client(ctx)
    try:
        self_info = client.self_.identify()
        data = {
            "workspace_name": self_info.workspace_name,
            "workspace_id": self_info.workspace_id,
            "workspace_slug": self_info.workspace_slug,
            "active": self_info.active,
            "scope": self_info.scope,
        }
        fields = [
            ("Workspace", self_info.workspace_name or "N/A"),
            ("ID", self_info.workspace_id or "N/A"),
            ("Slug", self_info.workspace_slug or "N/A"),
            ("Active", str(self_info.active) if self_info.active is not None else "N/A"),
            ("Scopes", self_info.scope or "N/A"),
        ]
        output_single(data, ctx, title="Workspace Info", fields=fields)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


MEMBER_COLUMNS = [
    {"header": "ID", "accessor": lambda m: m.get("member_id", ""), "no_wrap": True},
    {"header": "Name", "accessor": lambda m: m.get("name", "")},
    {"header": "Email", "accessor": lambda m: m.get("email_address", ""), "no_wrap": True},
    {"header": "Role", "accessor": lambda m: m.get("access_level", "")},
]


def _member_to_dict(member: Any) -> dict[str, Any]:
    """Convert a WorkspaceMember model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(member, "id"):
        mid = member.id
        result["member_id"] = getattr(mid, "workspace_member_id", str(mid))
    # Try known fields
    first = getattr(member, "first_name", "")
    last = getattr(member, "last_name", "")
    result["name"] = f"{first} {last}".strip() if (first or last) else getattr(member, "name", "")
    result["email_address"] = getattr(member, "email_address", "")
    result["access_level"] = getattr(member, "access_level", "")
    result["avatar_url"] = getattr(member, "avatar_url", "")
    result["created_at"] = str(getattr(member, "created_at", ""))
    return result


@app.command()
def members(ctx: typer.Context) -> None:
    """List workspace members."""
    client = get_client(ctx)
    try:
        result = client.workspace_members.list()
        data = [_member_to_dict(m) for m in result.data]
        output_list(data, MEMBER_COLUMNS, ctx, title="Workspace Members")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def member(
    ctx: typer.Context,
    member_id: str = typer.Argument(help="Workspace member ID."),
) -> None:
    """Get a workspace member by ID."""
    client = get_client(ctx)
    try:
        result = client.workspace_members.get(member_id)
        data = _member_to_dict(result)
        output_single(data, ctx, title=f"Workspace Member {member_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
