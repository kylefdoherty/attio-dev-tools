"""Dual-mode output engine for the Attio CLI.

Supports Rich table output for humans and JSON output for agents/scripts.
Data always goes to stdout; progress/errors go to stderr.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, Callable

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# stderr console for progress/errors; stdout console for data
console = Console(stderr=True)
output_console = Console()


def is_json_mode(ctx: typer.Context) -> bool:
    """Check if we should output JSON (explicit flag or non-TTY stdout)."""
    obj = ctx.ensure_object(dict)
    return obj.get("json", False) or not sys.stdout.isatty()


def _serialize(data: Any) -> Any:
    """Convert data to JSON-serializable form."""
    if hasattr(data, "model_dump"):
        return data.model_dump(mode="json")
    if isinstance(data, list):
        return [_serialize(item) for item in data]
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    if isinstance(data, datetime):
        return data.isoformat()
    return data


def output_list(
    data: list[Any],
    columns: list[dict[str, Any]],
    ctx: typer.Context,
    *,
    title: str | None = None,
) -> None:
    """Output a list of items as either a Rich table or JSON.

    columns: list of dicts with 'header' (str) and 'accessor' (callable).
    """
    if is_json_mode(ctx):
        envelope = {"data": _serialize(data)}
        sys.stdout.write(json.dumps(envelope, indent=2, default=str) + "\n")
    else:
        table = Table(title=title, show_header=True, header_style="bold")
        for col in columns:
            table.add_column(col["header"], no_wrap=col.get("no_wrap", False))
        for item in data:
            row_values: list[str] = []
            for col in columns:
                accessor: Callable[..., str] = col["accessor"]
                try:
                    val = accessor(item)
                except Exception:
                    val = ""
                row_values.append(str(val) if val is not None else "")
            table.add_row(*row_values)
        output_console.print(table)
        if data:
            output_console.print(f"\n[dim]{len(data)} result(s)[/dim]")


def output_single(
    data: Any,
    ctx: typer.Context,
    *,
    title: str | None = None,
    fields: list[tuple[str, Any]] | None = None,
) -> None:
    """Output a single item as JSON or a Rich panel with key-value pairs.

    fields: optional list of (label, value) tuples for human display.
    """
    if is_json_mode(ctx):
        envelope = {"data": _serialize(data)}
        sys.stdout.write(json.dumps(envelope, indent=2, default=str) + "\n")
    else:
        if fields:
            lines = []
            for label, value in fields:
                lines.append(f"[bold]{label}:[/bold] {value}")
            panel_content = "\n".join(lines)
        else:
            serialized = _serialize(data)
            panel_content = json.dumps(serialized, indent=2, default=str)
        output_console.print(Panel(panel_content, title=title, expand=False))


def output_success(message: str, ctx: typer.Context) -> None:
    """Output a success message to stderr (human) or JSON to stdout (machine)."""
    if is_json_mode(ctx):
        envelope = {"status": "success", "message": message}
        sys.stdout.write(json.dumps(envelope) + "\n")
    else:
        console.print(f"[green]OK[/green] {message}")


def output_error(message: str, ctx: typer.Context, *, exit_code: int = 1) -> None:
    """Output an error and exit with the given code.

    In JSON mode, writes structured error to stderr.
    Always raises SystemExit.
    """
    if is_json_mode(ctx):
        envelope = {"error": {"message": message}}
        sys.stderr.write(json.dumps(envelope) + "\n")
    else:
        console.print(f"[red bold]Error:[/red bold] {message}")
    raise SystemExit(exit_code)
