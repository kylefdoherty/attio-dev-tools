"""Threads commands: list, get."""

from __future__ import annotations

from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(name="threads", help="Manage comment threads.", no_args_is_help=True)

THREAD_COLUMNS = [
    {"header": "Thread ID", "accessor": lambda t: t.get("thread_id", ""), "no_wrap": True},
    {"header": "Comment Count", "accessor": lambda t: str(t.get("comment_count", 0))},
    {"header": "Created", "accessor": lambda t: t.get("created_at", "")[:10] if t.get("created_at") else ""},
]


def _thread_to_dict(thread: Any) -> dict[str, Any]:
    """Convert a Thread model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(thread, "id"):
        tid = thread.id
        result["thread_id"] = getattr(tid, "thread_id", str(tid))
    comments = getattr(thread, "comments", [])
    result["comment_count"] = len(comments)
    result["comments"] = [
        {
            "comment_id": getattr(getattr(c, "id", None), "comment_id", str(getattr(c, "id", ""))),
            "content_plaintext": getattr(c, "content_plaintext", ""),
            "created_at": str(getattr(c, "created_at", "")),
        }
        for c in comments
    ]
    result["created_at"] = str(getattr(thread, "created_at", ""))
    return result


@app.command("list")
def list_threads(
    ctx: typer.Context,
    object: Optional[str] = typer.Option(None, "--object", help="Object slug to filter by."),
    record: Optional[str] = typer.Option(None, "--record", help="Record ID to filter by."),
    list_: Optional[str] = typer.Option(None, "--list", help="List slug to filter by."),
    entry: Optional[str] = typer.Option(None, "--entry", help="Entry ID to filter by."),
) -> None:
    """List comment threads, optionally filtered by record or entry."""
    client = get_client(ctx)
    try:
        result = client.threads.list(
            object=object,
            record_id=record,
            list=list_,
            entry_id=entry,
        )
        data = [_thread_to_dict(t) for t in result.data]
        output_list(data, THREAD_COLUMNS, ctx, title="Threads")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    thread_id: str = typer.Argument(help="The thread ID to retrieve."),
) -> None:
    """Get a thread with its comments."""
    client = get_client(ctx)
    try:
        thread = client.threads.get(thread_id)
        data = _thread_to_dict(thread)
        output_single(data, ctx, title=f"Thread {thread_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
