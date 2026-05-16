"""Deals commands: list, get, create, update, upsert, delete, search, move, append, values, entries."""

from __future__ import annotations

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_single
from attio_cli.commands._record_factory import create_record_commands
from attio_cli.commands._record_helpers import DEALS_COLUMNS, record_to_dict


def _add_move_command(app: typer.Typer) -> None:
    """Attach the deals-specific ``move`` command."""

    @app.command()
    def move(
        ctx: typer.Context,
        record_id: str = typer.Argument(help="The deal record ID."),
        stage: str = typer.Argument(help="The target pipeline stage name or ID."),
    ) -> None:
        """Move a deal to a different pipeline stage.

        This is a convenience wrapper that updates the deal's stage attribute.
        """
        client = get_client(ctx)
        try:
            record = client.deals.update(
                record_id,
                values={"stage": [{"status": stage}]},
            )
            data = record_to_dict(record)
            output_single(data, ctx, title=f"Moved Deal {record_id}")
        except SystemExit:
            raise
        except Exception as e:
            handle_api_error(e, ctx)


app = create_record_commands("deals", columns=DEALS_COLUMNS, extra_commands=_add_move_command)
