"""Transcripts commands: get call transcripts."""

from __future__ import annotations

from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list

app = typer.Typer(name="transcripts", help="View call transcripts.", no_args_is_help=True)

TRANSCRIPT_COLUMNS = [
    {"header": "Speaker", "accessor": lambda s: s.get("speaker", "")},
    {"header": "Speech", "accessor": lambda s: s.get("speech", "")},
    {"header": "Start Time", "accessor": lambda s: s.get("start_time", "")},
    {"header": "End Time", "accessor": lambda s: s.get("end_time", "")},
]


def _segment_to_dict(s: Any) -> dict[str, Any]:
    """Convert a TranscriptSegment model to a simple dict."""
    return {
        "speaker": getattr(s, "speaker", None) or "",
        "speech": getattr(s, "speech", ""),
        "start_time": getattr(s, "start_time", ""),
        "end_time": getattr(s, "end_time", ""),
    }


@app.command()
def get(
    ctx: typer.Context,
    meeting_id: str = typer.Option(..., "--meeting", help="Meeting ID (required)."),
    recording_id: str = typer.Option(..., "--recording", help="Recording ID (required)."),
    limit: Optional[int] = typer.Option(None, help="Maximum number of segments."),
    cursor: Optional[str] = typer.Option(None, help="Pagination cursor."),
) -> None:
    """Get a transcript for a call recording."""
    client = get_client(ctx)
    try:
        result = client.transcripts.get(
            meeting_id,
            recording_id,
            limit=limit,
            cursor=cursor,
        )
        data = [_segment_to_dict(s) for s in result.data]
        output_list(data, TRANSCRIPT_COLUMNS, ctx, title="Transcript")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
