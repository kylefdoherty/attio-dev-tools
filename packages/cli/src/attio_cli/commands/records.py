"""Generic records commands for any object type (including custom objects).

Requires --object flag to specify the target object slug.
"""

from __future__ import annotations

from attio_cli.commands._record_factory import create_record_commands

app = create_record_commands("records", is_generic=True)
