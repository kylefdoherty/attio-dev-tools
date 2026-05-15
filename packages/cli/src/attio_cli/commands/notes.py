"""Notes commands: list, get, create, delete."""

from __future__ import annotations

import sys
from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success

app = typer.Typer(no_args_is_help=True)

NOTE_COLUMNS = [
    {"header": "ID", "accessor": lambda n: n.get("note_id", ""), "no_wrap": True},
    {"header": "Title", "accessor": lambda n: n.get("title", "")},
    {"header": "Object", "accessor": lambda n: n.get("parent_object", "")},
    {"header": "Record", "accessor": lambda n: n.get("parent_record_id", ""), "no_wrap": True},
    {"header": "Created", "accessor": lambda n: n.get("created_at", "")[:10] if n.get("created_at") else ""},
]


def _note_to_dict(note: Any) -> dict[str, Any]:
    """Convert a Note model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(note, "id"):
        nid = note.id
        result["note_id"] = getattr(nid, "note_id", str(nid))
    result["parent_object"] = getattr(note, "parent_object", "")
    result["parent_record_id"] = getattr(note, "parent_record_id", "")
    result["title"] = getattr(note, "title", "")
    result["content_plaintext"] = getattr(note, "content_plaintext", "")
    result["content_markdown"] = getattr(note, "content_markdown", "")
    result["format"] = getattr(note, "format", "")
    result["created_at"] = str(getattr(note, "created_at", ""))
    return result


@app.command("list")
def list_notes(
    ctx: typer.Context,
    parent_object: Optional[str] = typer.Option(None, "--object", help="Filter by parent object slug."),
    parent_record_id: Optional[str] = typer.Option(None, "--record", help="Filter by parent record ID."),
    limit: int = typer.Option(25, help="Maximum number of results."),
    offset: int = typer.Option(0, help="Pagination offset."),
    all_results: bool = typer.Option(False, "--all", help="Fetch all results."),
) -> None:
    """List notes, optionally filtered by parent object and record."""
    client = get_client(ctx)
    try:
        if all_results:
            from attio_cli.commands._record_helpers import collect_offset_pages

            items = collect_offset_pages(lambda off, lim: client.notes.list(
                parent_object=parent_object,
                parent_record_id=parent_record_id,
                limit=lim,
                offset=off,
            ))
            data = [_note_to_dict(n) for n in items]
            output_list(data, NOTE_COLUMNS, ctx, title="Notes (all)")
            return

        result = client.notes.list(
            parent_object=parent_object,
            parent_record_id=parent_record_id,
            limit=limit,
            offset=offset,
        )
        data = [_note_to_dict(n) for n in result.data]
        output_list(data, NOTE_COLUMNS, ctx, title="Notes")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    note_id: str = typer.Argument(help="The note ID to retrieve."),
) -> None:
    """Get a note by ID."""
    client = get_client(ctx)
    try:
        note = client.notes.get(note_id)
        data = _note_to_dict(note)
        output_single(data, ctx, title=f"Note {note_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    parent_object: str = typer.Option(..., "--object", help="Parent object slug (e.g., 'people')."),
    parent_record_id: str = typer.Option(..., "--record", help="Parent record ID."),
    title: str = typer.Option(..., help="Note title."),
    content: str = typer.Option(..., "--body", help="Note body content."),
    format: str = typer.Option("plaintext", help="Content format: plaintext or markdown."),
) -> None:
    """Create a new note attached to a record."""
    client = get_client(ctx)
    try:
        note = client.notes.create(
            parent_object=parent_object,
            parent_record_id=parent_record_id,
            title=title,
            format=format,
            content=content,
        )
        data = _note_to_dict(note)
        output_single(data, ctx, title="Created Note")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    note_id: str = typer.Argument(help="The note ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a note."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete note {note_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.notes.delete(note_id)
        output_success(f"Deleted note {note_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
