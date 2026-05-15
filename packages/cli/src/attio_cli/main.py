"""Root Typer app for the Attio CLI.

Registers all command groups, defines global flags, and provides the entry point.
"""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli import __version__
from attio_cli.commands import (
    attributes,
    auth,
    comments,
    companies,
    deals,
    entries,
    files,
    lists,
    meetings,
    notes,
    objects,
    people,
    records,
    recordings,
    search,
    select_options,
    statuses,
    tasks,
    threads,
    transcripts,
    views,
    webhooks,
    workspace,
)

app = typer.Typer(
    name="attio",
    help="The Attio CRM command-line interface.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth", help="Authenticate with the Attio API.")
app.add_typer(people.app, name="people", help="Manage people records.")
app.add_typer(companies.app, name="companies", help="Manage company records.")
app.add_typer(deals.app, name="deals", help="Manage deal records.")
app.add_typer(records.app, name="records", help="Manage records for any object.")
app.add_typer(objects.app, name="objects", help="Manage object definitions.")
app.add_typer(lists.app, name="lists", help="Manage list definitions.")
app.add_typer(entries.app, name="entries", help="Manage list entries.")
app.add_typer(notes.app, name="notes", help="Manage notes.")
app.add_typer(tasks.app, name="tasks", help="Manage tasks.")
app.add_typer(webhooks.app, name="webhooks", help="Manage webhooks.")
app.add_typer(workspace.app, name="workspace", help="Workspace info and members.")
app.add_typer(search.app, name="search", help="Search across all objects.")
app.add_typer(attributes.app, name="attributes", help="Manage object and list attributes.")
app.add_typer(select_options.app, name="select-options", help="Manage select attribute options.")
app.add_typer(statuses.app, name="statuses", help="Manage status attribute options.")
app.add_typer(comments.app, name="comments", help="Manage comments.")
app.add_typer(threads.app, name="threads", help="Manage comment threads.")
app.add_typer(files.app, name="files", help="Manage files.")
app.add_typer(views.app, name="views", help="List saved views.")
app.add_typer(meetings.app, name="meetings", help="List and view meetings.")
app.add_typer(recordings.app, name="recordings", help="List and view call recordings.")
app.add_typer(transcripts.app, name="transcripts", help="View call transcripts.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"attio-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output as JSON."),
    limit: Optional[int] = typer.Option(None, "--limit", help="Default result limit."),
    debug: bool = typer.Option(False, "--debug", help="Print debug info to stderr."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output."),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="ATTIO_API_KEY", help="API key override."),
    profile: Optional[str] = typer.Option(None, "--profile", help="Use a named auth profile."),
    version: bool = typer.Option(False, "--version", callback=_version_callback, is_eager=True, help="Show version."),
) -> None:
    """Global flags shared by all commands."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["limit"] = limit
    ctx.obj["debug"] = debug
    ctx.obj["quiet"] = quiet
    ctx.obj["no_color"] = no_color
    ctx.obj["api_key"] = api_key
    ctx.obj["profile"] = profile


if __name__ == "__main__":
    app()
