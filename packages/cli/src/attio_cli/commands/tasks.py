"""Tasks commands: list, get, create, update, delete, complete."""

from __future__ import annotations

import sys
from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli.commands._record_helpers import parse_json_option

app = typer.Typer(no_args_is_help=True)

TASK_COLUMNS = [
    {"header": "ID", "accessor": lambda t: t.get("task_id", ""), "no_wrap": True},
    {"header": "Content", "accessor": lambda t: (t.get("content_plaintext", "") or "")[:60]},
    {"header": "Completed", "accessor": lambda t: str(t.get("is_completed", ""))},
    {"header": "Deadline", "accessor": lambda t: t.get("deadline_at", "") or ""},
    {"header": "Created", "accessor": lambda t: t.get("created_at", "")[:10] if t.get("created_at") else ""},
]


def _task_to_dict(task: Any) -> dict[str, Any]:
    """Convert a Task model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(task, "id"):
        tid = task.id
        result["task_id"] = getattr(tid, "task_id", str(tid))
    result["content_plaintext"] = getattr(task, "content_plaintext", "")
    result["content_markdown"] = getattr(task, "content_markdown", "")
    result["format"] = getattr(task, "format", "")
    result["is_completed"] = getattr(task, "is_completed", False)
    result["completed_at"] = str(getattr(task, "completed_at", "")) if getattr(task, "completed_at", None) else ""
    result["deadline_at"] = str(getattr(task, "deadline_at", "")) if getattr(task, "deadline_at", None) else ""
    result["created_at"] = str(getattr(task, "created_at", ""))
    return result


@app.command("list")
def list_tasks(
    ctx: typer.Context,
    linked_object: Optional[str] = typer.Option(None, "--object", help="Filter by linked object slug."),
    linked_record_id: Optional[str] = typer.Option(None, "--record", help="Filter by linked record ID."),
    is_completed: Optional[bool] = typer.Option(None, "--completed", help="Filter by completion status."),
    assignee: Optional[str] = typer.Option(None, help="Filter by assignee ID."),
    limit: int = typer.Option(25, help="Maximum number of results."),
    offset: int = typer.Option(0, help="Pagination offset."),
) -> None:
    """List tasks with optional filters."""
    client = get_client(ctx)
    try:
        result = client.tasks.list(
            linked_object=linked_object,
            linked_record_id=linked_record_id,
            is_completed=is_completed,
            assignee=assignee,
            limit=limit,
            offset=offset,
        )
        data = [_task_to_dict(t) for t in result.data]
        output_list(data, TASK_COLUMNS, ctx, title="Tasks")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    task_id: str = typer.Argument(help="The task ID to retrieve."),
) -> None:
    """Get a task by ID."""
    client = get_client(ctx)
    try:
        task = client.tasks.get(task_id)
        data = _task_to_dict(task)
        output_single(data, ctx, title=f"Task {task_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    content: str = typer.Option(..., "--content", help="Task content text."),
    format: str = typer.Option("plaintext", help="Content format: plaintext or markdown."),
    deadline_at: Optional[str] = typer.Option(None, "--deadline", help="Deadline ISO timestamp."),
    linked_records: Optional[str] = typer.Option(None, "--linked-records", help="JSON array of linked records."),
    assignees: Optional[str] = typer.Option(None, help="JSON array of assignees."),
) -> None:
    """Create a new task."""
    client = get_client(ctx)
    try:
        linked = parse_json_option(linked_records) if linked_records else None
        assignee_list = parse_json_option(assignees) if assignees else None
        task = client.tasks.create(
            content=content,
            format=format,
            deadline_at=deadline_at,
            linked_records=linked,
            assignees=assignee_list,
        )
        data = _task_to_dict(task)
        output_single(data, ctx, title="Created Task")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    task_id: str = typer.Argument(help="The task ID to update."),
    content: Optional[str] = typer.Option(None, "--content", help="New task content."),
    is_completed: Optional[bool] = typer.Option(None, "--completed", help="Mark as completed or not."),
    deadline_at: Optional[str] = typer.Option(None, "--deadline", help="New deadline ISO timestamp."),
) -> None:
    """Update an existing task."""
    client = get_client(ctx)
    try:
        task = client.tasks.update(
            task_id,
            content=content,
            is_completed=is_completed,
            deadline_at=deadline_at,
        )
        data = _task_to_dict(task)
        output_single(data, ctx, title="Updated Task")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    task_id: str = typer.Argument(help="The task ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a task."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete task {task_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.tasks.delete(task_id)
        output_success(f"Deleted task {task_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def complete(
    ctx: typer.Context,
    task_id: str = typer.Argument(help="The task ID to mark as completed."),
) -> None:
    """Mark a task as completed (convenience command)."""
    client = get_client(ctx)
    try:
        task = client.tasks.update(task_id, is_completed=True)
        data = _task_to_dict(task)
        output_single(data, ctx, title=f"Completed Task {task_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
