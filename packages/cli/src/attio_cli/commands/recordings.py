"""Recordings commands: list, get call recordings."""

from __future__ import annotations

from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(name="recordings", help="List and view call recordings.", no_args_is_help=True)

RECORDING_COLUMNS = [
    {"header": "Recording ID", "accessor": lambda r: r.get("id", ""), "no_wrap": True},
    {"header": "Status", "accessor": lambda r: r.get("status", "")},
    {"header": "Web URL", "accessor": lambda r: r.get("web_url", "")},
    {"header": "Created", "accessor": lambda r: r.get("created_at", "")[:10] if r.get("created_at") else ""},
]


def _recording_to_dict(r: Any) -> dict[str, Any]:
    """Convert a CallRecording model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(r, "id"):
        rid = r.id
        result["id"] = getattr(rid, "call_recording_id", str(rid))
    result["meeting_id"] = getattr(r, "meeting_id", "")
    result["status"] = getattr(r, "status", "")
    result["web_url"] = getattr(r, "web_url", None) or ""
    result["created_at"] = str(getattr(r, "created_at", ""))
    return result


@app.command("list")
def list_recordings(
    ctx: typer.Context,
    meeting_id: str = typer.Option(..., "--meeting", help="Meeting ID (required)."),
    limit: Optional[int] = typer.Option(None, help="Maximum number of results."),
    cursor: Optional[str] = typer.Option(None, help="Pagination cursor."),
) -> None:
    """List call recordings for a meeting."""
    client = get_client(ctx)
    try:
        result = client.call_recordings.list(
            meeting_id,
            limit=limit,
            cursor=cursor,
        )
        data = [_recording_to_dict(r) for r in result.data]
        output_list(data, RECORDING_COLUMNS, ctx, title="Call Recordings")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    recording_id: str = typer.Argument(help="The recording ID to retrieve."),
    meeting_id: str = typer.Option(..., "--meeting", help="Meeting ID (required)."),
) -> None:
    """Get a call recording by ID."""
    client = get_client(ctx)
    try:
        r = client.call_recordings.get(meeting_id, recording_id)
        data = _recording_to_dict(r)
        output_single(data, ctx, title=f"Recording {recording_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
