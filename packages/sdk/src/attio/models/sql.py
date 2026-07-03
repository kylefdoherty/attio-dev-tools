"""Models for the SQL resource."""

from __future__ import annotations

from typing import Any

from attio.models._base import AttioModel


class SqlQueryResult(AttioModel):
    """Result of a SQL query.

    Each row is a mapping of the selected column names to their values.
    """

    rows: list[dict[str, Any]]
