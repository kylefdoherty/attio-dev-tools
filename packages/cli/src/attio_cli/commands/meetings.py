"""Meetings commands: list, get."""

from __future__ import annotations

from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single

app = typer.Typer(name="meetings", help="List and view meetings.", no_args_is_help=True)

MEETING_COLUMNS = [
    {"header": "Meeting ID", "accessor": lambda m: m.get("id", ""), "no_wrap": True},
    {"header": "Title", "accessor": lambda m: m.get("title", "")},
    {"header": "Start", "accessor": lambda m: m.get("start_time", "")},
    {"header": "End", "accessor": lambda m: m.get("end_time", "")},
    {"header": "Participants", "accessor": lambda m: m.get("participants", 0)},
]


def _meeting_to_dict(m: Any) -> dict[str, Any]:
    """Convert a Meeting model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(m, "id"):
        mid = m.id
        result["id"] = getattr(mid, "meeting_id", str(mid))
    result["title"] = getattr(m, "title", None) or "(untitled)"
    result["description"] = getattr(m, "description", None) or ""
    result["start_time"] = str(getattr(m, "start_time", "")) if getattr(m, "start_time", None) else ""
    result["end_time"] = str(getattr(m, "end_time", "")) if getattr(m, "end_time", None) else ""
    participants = getattr(m, "participants", [])
    result["participants"] = len(participants) if participants else 0
    result["linked_records"] = getattr(m, "linked_records", [])
    result["created_at"] = str(getattr(m, "created_at", ""))
    return result


@app.command("list")
def list_meetings(
    ctx: typer.Context,
    limit: Optional[int] = typer.Option(None, help="Maximum number of results."),
    cursor: Optional[str] = typer.Option(None, help="Pagination cursor."),
    object: Optional[str] = typer.Option(None, "--object", help="Filter by linked object slug."),
    record: Optional[str] = typer.Option(None, "--record", help="Filter by linked record ID."),
    participants: Optional[str] = typer.Option(None, "--participants", help="Comma-separated participant emails."),
    sort: Optional[str] = typer.Option(None, "--sort", help="Sort order."),
    ends_from: Optional[str] = typer.Option(None, "--ends-from", help="Filter meetings ending from this time."),
    starts_before: Optional[str] = typer.Option(None, "--starts-before", help="Filter meetings starting before this time."),
    timezone: Optional[str] = typer.Option(None, "--timezone", help="Timezone for time filters."),
) -> None:
    """List meetings."""
    client = get_client(ctx)
    try:
        participants_list: list[str] | None = None
        if participants:
            participants_list = [p.strip() for p in participants.split(",")]

        result = client.meetings.list(
            limit=limit,
            cursor=cursor,
            linked_object=object,
            linked_record_id=record,
            participants=participants_list,
            sort=sort,
            ends_from=ends_from,
            starts_before=starts_before,
            timezone=timezone,
        )
        data = [_meeting_to_dict(m) for m in result.data]
        output_list(data, MEETING_COLUMNS, ctx, title="Meetings")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    meeting_id: str = typer.Argument(help="The meeting ID to retrieve."),
) -> None:
    """Get a meeting by ID."""
    client = get_client(ctx)
    try:
        m = client.meetings.get(meeting_id)
        data = _meeting_to_dict(m)
        output_single(data, ctx, title=f"Meeting {meeting_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
