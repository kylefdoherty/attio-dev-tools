"""Files commands: list, get, upload, download, create-folder, delete."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success

app = typer.Typer(name="files", help="Manage files attached to records.", no_args_is_help=True)

FILE_COLUMNS = [
    {"header": "File ID", "accessor": lambda f: f.get("id", ""), "no_wrap": True},
    {"header": "Name", "accessor": lambda f: f.get("name", "")},
    {"header": "Type", "accessor": lambda f: f.get("file_type", "")},
    {"header": "Size", "accessor": lambda f: f.get("content_size", 0)},
    {"header": "Created", "accessor": lambda f: f.get("created_at", "")[:10] if f.get("created_at") else ""},
]


def _file_to_dict(f: Any) -> dict[str, Any]:
    """Convert an AttioFile model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(f, "id"):
        fid = f.id
        result["id"] = getattr(fid, "file_id", str(fid))
    result["name"] = getattr(f, "name", "")
    result["file_type"] = getattr(f, "file_type", "")
    result["content_type"] = getattr(f, "content_type", "") or ""
    result["content_size"] = getattr(f, "content_size", 0) or 0
    result["object_id"] = getattr(f, "object_id", "")
    result["object_slug"] = getattr(f, "object_slug", "")
    result["record_id"] = getattr(f, "record_id", "")
    result["storage_provider"] = getattr(f, "storage_provider", "")
    result["parent_folder_id"] = getattr(f, "parent_folder_id", None)
    result["created_at"] = str(getattr(f, "created_at", ""))
    return result


@app.command("list")
def list_files(
    ctx: typer.Context,
    object: str = typer.Option(..., "--object", help="Object slug."),
    record_id: str = typer.Option(..., "--record", help="Record ID."),
    storage_provider: Optional[str] = typer.Option(None, "--storage-provider", help="Filter by storage provider."),
    parent_folder_id: Optional[str] = typer.Option(None, "--parent-folder", help="Parent folder ID."),
    limit: Optional[int] = typer.Option(None, help="Maximum number of results."),
    cursor: Optional[str] = typer.Option(None, help="Pagination cursor."),
    all_results: bool = typer.Option(False, "--all", help="Fetch all results."),
) -> None:
    """List files for a record."""
    client = get_client(ctx)
    try:
        if all_results:
            from attio_cli.commands._record_helpers import collect_cursor_pages

            items = collect_cursor_pages(lambda cur: client.files.list(
                object=object, record_id=record_id, storage_provider=storage_provider,
                parent_folder_id=parent_folder_id, cursor=cur,
            ))
            data = [_file_to_dict(f) for f in items]
            output_list(data, FILE_COLUMNS, ctx, title="Files (all)")
            return

        result = client.files.list(
            object=object,
            record_id=record_id,
            storage_provider=storage_provider,
            parent_folder_id=parent_folder_id,
            limit=limit,
            cursor=cursor,
        )
        data = [_file_to_dict(f) for f in result.data]
        output_list(data, FILE_COLUMNS, ctx, title="Files")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    file_id: str = typer.Argument(help="The file ID to retrieve."),
) -> None:
    """Get a file by ID."""
    client = get_client(ctx)
    try:
        f = client.files.get(file_id)
        data = _file_to_dict(f)
        output_single(data, ctx, title=f"File {file_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def upload(
    ctx: typer.Context,
    file: Path = typer.Option(..., "--file", exists=True, help="Path to file to upload."),
    object: str = typer.Option(..., "--object", help="Object slug."),
    record_id: str = typer.Option(..., "--record", help="Record ID."),
    parent_folder_id: Optional[str] = typer.Option(None, "--parent-folder", help="Parent folder ID."),
) -> None:
    """Upload a file to a record."""
    client = get_client(ctx)
    try:
        file_bytes = file.read_bytes()
        result = client.files.upload(
            file=file_bytes,
            filename=file.name,
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        data = _file_to_dict(result)
        output_single(data, ctx, title="Uploaded File")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def download(
    ctx: typer.Context,
    file_id: str = typer.Argument(help="The file ID to download."),
) -> None:
    """Get a download URL for a file."""
    client = get_client(ctx)
    try:
        result = client.files.download(file_id)
        data = {"file_id": file_id, "url": result.url}
        output_single(data, ctx, title=f"Download URL for {file_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command("create-folder")
def create_folder(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", help="Folder name."),
    object: str = typer.Option(..., "--object", help="Object slug."),
    record_id: str = typer.Option(..., "--record", help="Record ID."),
    parent_folder_id: Optional[str] = typer.Option(None, "--parent-folder", help="Parent folder ID."),
) -> None:
    """Create a folder on a record."""
    client = get_client(ctx)
    try:
        result = client.files.create_folder(
            name=name,
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        data = _file_to_dict(result)
        output_single(data, ctx, title="Created Folder")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    file_id: str = typer.Argument(help="The file ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a file."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete file {file_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.files.delete(file_id)
        output_success(f"Deleted file {file_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
