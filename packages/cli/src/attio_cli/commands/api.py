"""Raw API escape hatch command for the Attio CLI.

Lets users hit any Attio API endpoint with auth already handled,
similar to `gh api` for GitHub.
"""

from __future__ import annotations

import json
import sys
from typing import Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error

VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def api_command(
    ctx: typer.Context,
    method: str = typer.Argument(help="HTTP method: GET, POST, PUT, PATCH, DELETE."),
    path: str = typer.Argument(help="API path, e.g. /objects or /v2/objects."),
    body: Optional[str] = typer.Option(None, "--body", "-d", help="JSON request body."),
    limit: Optional[int] = typer.Option(None, "--limit", help="Add limit query parameter."),
    offset: Optional[int] = typer.Option(None, "--offset", help="Add offset query parameter."),
) -> None:
    """Make raw API requests with authentication."""
    method = method.upper()
    if method not in VALID_METHODS:
        raise typer.BadParameter(f"Method must be one of: {', '.join(sorted(VALID_METHODS))} (got: '{method}')")

    # Normalize path: strip /v2 prefix, ensure leading /
    if path.startswith("/v2/"):
        path = path[3:]
    elif path.startswith("/v2"):
        path = path[3:] or "/"
    if not path.startswith("/"):
        path = "/" + path

    # Parse body
    body_obj = None
    if body is not None:
        try:
            body_obj = json.loads(body)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"--body must be valid JSON: {e}")

    # Build query params
    params: dict[str, int] | None = None
    if limit is not None or offset is not None:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

    client = get_client(ctx)
    try:
        result = client.http.request(method, path, json=body_obj, params=params)
        sys.stdout.write(json.dumps(result, indent=2, default=str) + "\n")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
