"""People commands: list, get, create, update, upsert, delete, search, append, values, entries."""

from __future__ import annotations

from attio_cli.commands._record_factory import create_record_commands
from attio_cli.commands._record_helpers import PEOPLE_COLUMNS

app = create_record_commands("people", columns=PEOPLE_COLUMNS)
