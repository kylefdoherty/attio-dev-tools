"""SDK client factory for the Attio CLI.

Creates an AttioClient from resolved configuration (API key from flag, env, or config).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from attio_cli._config import get_api_key

if TYPE_CHECKING:
    from attio import AttioClient
    import typer


def get_client(ctx: typer.Context) -> AttioClient:
    """Create an AttioClient from the current context.

    Resolves the API key from the priority chain:
    flag > ATTIO_API_KEY env var > config file profile.

    Exits with code 3 if no API key is found.
    """
    from attio import AttioClient
    from attio_cli._output import output_error

    obj = ctx.ensure_object(dict)
    api_key = get_api_key(
        flag_value=obj.get("api_key"),
        profile_name=obj.get("profile"),
    )
    if not api_key:
        output_error(
            "No API key found. Set ATTIO_API_KEY, run 'attio auth login', or pass --api-key.",
            ctx,
            exit_code=3,
        )
    return AttioClient(api_key=api_key)
