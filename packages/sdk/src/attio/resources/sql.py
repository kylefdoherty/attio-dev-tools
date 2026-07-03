"""SQL resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper
from attio.models.sql import SqlQueryResult
from attio.resources._base import AsyncResource, SyncResource


class _SqlMixin:
    """Shared parameter/body construction logic for the SQL resource."""

    @staticmethod
    def _build_query_body(*, sql: str) -> dict[str, Any]:
        return {"sql": sql}

    @staticmethod
    def _parse_query_response(raw: dict[str, Any]) -> SqlQueryResult:
        wrapper = DataWrapper[SqlQueryResult].model_validate(raw)
        return wrapper.data


class SqlResource(SyncResource, _SqlMixin):
    """Synchronous SQL resource."""

    def query(self, sql: str) -> SqlQueryResult:
        """Query records and lists with read-only SQL. (beta)

        BETA: this endpoint is in beta and requires an Enterprise plan.
        Only ``SELECT`` statements are supported, against the
        ``objects.<slug>`` and ``lists.<slug>`` schemas (a list row is an
        entry). Rate limited to 2 queries per second with a 30 second
        query timeout.
        """
        body = self._build_query_body(sql=sql)
        raw = self._http.request("POST", "/sql", json=body)
        return self._parse_query_response(raw)


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncSqlResource(AsyncResource, _SqlMixin):
    """Asynchronous SQL resource."""

    async def query(self, sql: str) -> SqlQueryResult:
        """Query records and lists with read-only SQL. (beta)

        BETA: this endpoint is in beta and requires an Enterprise plan.
        Only ``SELECT`` statements are supported, against the
        ``objects.<slug>`` and ``lists.<slug>`` schemas (a list row is an
        entry). Rate limited to 2 queries per second with a 30 second
        query timeout.
        """
        body = self._build_query_body(sql=sql)
        raw = await self._http.request("POST", "/sql", json=body)
        return self._parse_query_response(raw)
