"""Auth commands: login, logout, status."""

from __future__ import annotations

from typing import Optional

import typer

from attio_cli._output import console, output_error, output_single, output_success

app = typer.Typer(no_args_is_help=True)


@app.command()
def login(
    ctx: typer.Context,
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key to save (prefer interactive prompt or --1password)."),
    one_password: Optional[str] = typer.Option(None, "--1password", help="1Password secret reference (e.g. op://Vault/Item/field)."),
    profile_name: str = typer.Option("default", "--profile", help="Profile name to save as."),
) -> None:
    """Authenticate with the Attio API.

    Three modes:
      - Interactive: run with no flags, enter key via hidden prompt
      - 1Password: --1password "op://Vault/Attio/credential" (no secret stored on disk)
      - Direct: --api-key sk_... (not recommended, visible in shell history)
    """
    from attio import AttioClient
    from attio._exceptions import AttioError

    from attio_cli._config import save_1password_ref, save_api_key

    if one_password:
        from attio_cli._config import _resolve_1password

        console.print("[dim]Resolving from 1Password...[/dim]", end=" ")
        key = _resolve_1password(one_password)
        if not key:
            output_error(
                "Failed to resolve 1Password reference. Is the `op` CLI installed and authenticated? "
                "Try: op signin",
                ctx,
                exit_code=3,
            )
            return
    elif api_key:
        key = api_key
    else:
        key = typer.prompt("Enter your Attio API key", hide_input=True)

    if not key:
        output_error("No API key provided.", ctx, exit_code=2)
        return

    console.print("[dim]Verifying...[/dim]", end=" ")
    try:
        client = AttioClient(api_key=key)
        info = client.self_.identify()
        workspace_name = info.workspace_name or "Unknown workspace"
        client.close()
    except AttioError as e:
        output_error(f"Authentication failed: {e}", ctx, exit_code=3)
        return

    if one_password:
        save_1password_ref(one_password, profile_name=profile_name, workspace_name=workspace_name)
        output_success(
            f'Authenticated to workspace "{workspace_name}" via 1Password (profile: {profile_name})',
            ctx,
        )
    else:
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
