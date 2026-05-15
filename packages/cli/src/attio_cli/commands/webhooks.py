"""Webhooks commands: list, get, create, update, delete, events."""

from __future__ import annotations

import sys
from typing import Any, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli.commands._record_helpers import parse_json_option

app = typer.Typer(no_args_is_help=True)

WEBHOOK_COLUMNS = [
    {"header": "ID", "accessor": lambda w: w.get("webhook_id", ""), "no_wrap": True},
    {"header": "URL", "accessor": lambda w: w.get("target_url", "")},
    {"header": "Status", "accessor": lambda w: w.get("status", "")},
    {"header": "Events", "accessor": lambda w: str(w.get("event_count", 0))},
    {"header": "Created", "accessor": lambda w: w.get("created_at", "")[:10] if w.get("created_at") else ""},
]


def _webhook_to_dict(webhook: Any) -> dict[str, Any]:
    """Convert a Webhook model to a simple dict."""
    result: dict[str, Any] = {}
    if hasattr(webhook, "id"):
        wid = webhook.id
        result["webhook_id"] = getattr(wid, "webhook_id", str(wid))
    result["target_url"] = getattr(webhook, "target_url", "")
    result["status"] = getattr(webhook, "status", "")
    subs = getattr(webhook, "subscriptions", [])
    result["subscriptions"] = [
        {"event_type": s.event_type, "filter": s.filter} if hasattr(s, "event_type") else s
        for s in subs
    ]
    result["event_count"] = len(subs)
    result["secret"] = getattr(webhook, "secret", None)
    result["created_at"] = str(getattr(webhook, "created_at", ""))
    return result


@app.command("list")
def list_webhooks(ctx: typer.Context) -> None:
    """List all webhooks in the workspace."""
    client = get_client(ctx)
    try:
        result = client.webhooks.list()
        data = [_webhook_to_dict(w) for w in result.data]
        output_list(data, WEBHOOK_COLUMNS, ctx, title="Webhooks")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def get(
    ctx: typer.Context,
    webhook_id: str = typer.Argument(help="The webhook ID to retrieve."),
) -> None:
    """Get a webhook by ID."""
    client = get_client(ctx)
    try:
        webhook = client.webhooks.get(webhook_id)
        data = _webhook_to_dict(webhook)
        output_single(data, ctx, title=f"Webhook {webhook_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def create(
    ctx: typer.Context,
    target_url: str = typer.Option(..., "--url", help="Target URL for webhook delivery."),
    subscriptions: str = typer.Option(
        ..., "--events", help='JSON array of subscriptions, e.g., \'[{"event_type": "record.created"}]\'.'
    ),
) -> None:
    """Create a new webhook."""
    client = get_client(ctx)
    try:
        subs = parse_json_option(subscriptions)
        if not subs or not isinstance(subs, list):
            raise typer.BadParameter("--events must be a JSON array of subscription objects.")
        webhook = client.webhooks.create(target_url=target_url, subscriptions=subs)
        data = _webhook_to_dict(webhook)
        output_single(data, ctx, title="Created Webhook")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def update(
    ctx: typer.Context,
    webhook_id: str = typer.Argument(help="The webhook ID to update."),
    target_url: Optional[str] = typer.Option(None, "--url", help="New target URL."),
    subscriptions: Optional[str] = typer.Option(None, "--events", help="New JSON array of subscriptions."),
) -> None:
    """Update an existing webhook."""
    client = get_client(ctx)
    try:
        subs = None
        if subscriptions:
            subs = parse_json_option(subscriptions)
            if not isinstance(subs, list):
                raise typer.BadParameter("--events must be a JSON array.")
        webhook = client.webhooks.update(
            webhook_id,
            target_url=target_url,
            subscriptions=subs,
        )
        data = _webhook_to_dict(webhook)
        output_single(data, ctx, title="Updated Webhook")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def delete(
    ctx: typer.Context,
    webhook_id: str = typer.Argument(help="The webhook ID to delete."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Delete a webhook."""
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete webhook {webhook_id}?", abort=True)

    client = get_client(ctx)
    try:
        client.webhooks.delete(webhook_id)
        output_success(f"Deleted webhook {webhook_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


@app.command()
def events(ctx: typer.Context) -> None:
    """List all available webhook event types."""
    from attio.models.webhooks import WebhookEventType

    data = [{"event_type": e.value} for e in WebhookEventType]
    columns = [
        {"header": "Event Type", "accessor": lambda e: e.get("event_type", "")},
    ]
    output_list(data, columns, ctx, title="Webhook Event Types")
