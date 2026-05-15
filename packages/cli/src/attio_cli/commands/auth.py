"""Auth commands: login, logout, status."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._output import console, output_error, output_single, output_success

app = typer.Typer(no_args_is_help=True)


@app.command()
def login(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key to save."),
    profile_name: str = typer.Option("default", "--profile", help="Profile name to save as."),
) -> None:
    """Authenticate with the Attio API by providing an API key."""
    from attio import AttioClient
    from attio._exceptions import AttioError

    from attio_cli._config import save_api_key

    key = api_key
    if not key:
        key = typer.prompt("Enter your Attio API key", hide_input=True)

    if not key:
        output_error("No API key provided.", ctx, exit_code=2)

    # Validate the key by calling the identify endpoint
    console.print("[dim]Verifying...[/dim]", end=" ")
    try:
        client = AttioClient(api_key=key)
        info = client.self_.identify()
        workspace_name = info.workspace_name or "Unknown workspace"
        client.close()
    except AttioError as e:
        output_error(f"Authentication failed: {e}", ctx, exit_code=3)
        return  # unreachable, output_error raises SystemExit

    save_api_key(key, profile_name=profile_name, workspace_name=workspace_name)
    output_success(f'Authenticated to workspace "{workspace_name}" (profile: {profile_name})', ctx)


@app.command()
def logout(
    ctx: typer.Context,
    profile_name: Optional[str] = typer.Option(None, "--profile", help="Profile to log out."),
) -> None:
    """Remove stored credentials."""
    from attio_cli._config import remove_api_key

    removed = remove_api_key(profile_name=profile_name)
    if removed:
        output_success("Credentials removed.", ctx)
    else:
        output_error("No stored credentials found.", ctx, exit_code=1)


@app.command()
def status(ctx: typer.Context) -> None:
    """Show current authentication state, workspace name, and scopes."""
    from attio_cli._client import get_client
    from attio_cli._config import get_active_profile_name
    from attio_cli._errors import handle_api_error
    from attio_cli._output import is_json_mode

    try:
        client = get_client(ctx)
        info = client.self_.identify()
        client.close()
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
        return

    profile = get_active_profile_name()
    fields = [
        ("Profile", profile),
        ("Workspace", info.workspace_name or "N/A"),
        ("Workspace ID", info.workspace_id or "N/A"),
        ("Active", str(info.active) if info.active is not None else "N/A"),
        ("Scopes", info.scope or "N/A"),
    ]

    if is_json_mode(ctx):
        data = {
            "profile": profile,
            "workspace_name": info.workspace_name,
            "workspace_id": info.workspace_id,
            "active": info.active,
            "scope": info.scope,
        }
        output_single(data, ctx, title="Auth Status")
    else:
        output_single(info, ctx, title="Auth Status", fields=fields)
