"""Comments commands: create, get, delete."""

from __future__ import annotations

import json
import sys
from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_single, output_success

app = typer.Typer(name="comments", help="Manage comments on records and entries.", no_args_is_help=True)


def _comment_to_dict(comment: Any) -> dict[str, Any]:
    """Convert a Comment model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(comment, "id"):
        cid = comment.id
        result["comment_id"] = getattr(cid, "comment_id", str(cid))
    result["thread_id"] = getattr(comment, "thread_id", "")
    result["content_plaintext"] = getattr(comment, "content_plaintext", "")
    result["created_at"] = str(getattr(comment, "created_at", ""))
    author = getattr(comment, "author", None)
    if author and hasattr(author, "model_dump"):
        result["author"] = author.model_dump(mode="json")
    elif author:
        result["author"] = str(author)
    result["record"] = getattr(comment, "record", None)
    result["entry"] = getattr(comment, "entry", None)
    return result


def _parse_json_arg(value: str, name: str) -> dict[str, str]:
    """Parse a JSON string argument into a dict."""
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"--{name} must be valid JSON: {exc}")
    if not isinstance(parsed, dict):
        raise typer.BadParameter(f"--{name} must be a JSON object.")
    return parsed


@app.command()
def create(
    ctx: typer.Context,
    body: str = typer.Option(..., "--body", help="Comment body text."),
    author: str = typer.Option(..., "--author", help='JSON author object, e.g., \'{"type": "workspace-member", "id": "..."}\''),
    thread: Optional[str] = typer.Option(None, "--thread", help="Thread ID to comment on."),
    record: Optional[str] = typer.Option(None, "--record", help='JSON record target, e.g., \'{"object": "people", "record_id": "..."}\''),
    entry: Optional[str] = typer.Option(None, "--entry", help='JSON entry target, e.g., \'{"list": "pipeline", "entry_id": "..."}\''),
) -> None:
    """Create a comment on a thread, record, or entry."""
    # Validate exactly one target
    targets = sum(x is not None for x in (thread, record, entry))
    if targets == 0:
        raise typer.BadParameter("Exactly one of --thread, --record, or --entry is required.")
    if targets > 1:
        raise typer.BadParameter("Provide exactly one of --thread, --record, or --entry.")

    author_obj = _parse_json_arg(author, "author")

    record_obj = None
    entry_obj = None
    if record:
        record_obj = _parse_json_arg(record, "record")
    if entry:
        entry_obj = _parse_json_arg(entry, "entry")

    client = get_client(ctx)
    try:
        comment = client.comments.create(
            thread_id=thread,
            record=record_obj,
            entry=entry_obj,
            content=body,
            author=author_obj,
        )
        data = _comment_to_dict(comment)
        output_single(data, ctx, title="Created Comment")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    comment_id: str = typer.Argument(help="The comment ID to retrieve."),
) -> None:
    """Get a comment by ID."""
    client = get_client(ctx)
    try:
        comment = client.comments.get(comment_id)
        data = _comment_to_dict(comment)
        output_single(data, ctx, title=f"Comment {comment_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    comment_id: str = typer.Argument(help="The comment ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a comment."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete comment {comment_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.comments.delete(comment_id)
        output_success(f"Deleted comment {comment_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
