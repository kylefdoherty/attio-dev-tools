"""Tests for the SQL resource (sync and async)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio._exceptions import AttioPermissionError, AttioValidationError
from attio.models.sql import SqlQueryResult
from tests.fixtures.factory import (
    MOCK_PERMISSION_ERROR,
    MOCK_SQL_RESULT,
    MOCK_SQL_SYNTAX_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_sql"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestSqlResourceSync:
    @respx.mock
    def test_query(self) -> None:
        route = respx.post(f"{BASE_URL}/sql").mock(
            return_value=httpx.Response(200, json=MOCK_SQL_RESULT)
        )
        client = _sync_client()
        result = client.sql.query("SELECT * FROM companies")

        assert route.called
        assert isinstance(result, SqlQueryResult)
        assert len(result.rows) == 2
        assert result.rows[0]["name"] == "Acme Corp"
        assert result.rows[1]["domains"] == ["globex.com"]

        # Verify request body
        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {"sql": "SELECT * FROM companies"}
        client.close()

    @respx.mock
    def test_query_syntax_error(self) -> None:
        respx.post(f"{BASE_URL}/sql").mock(
            return_value=httpx.Response(400, json=MOCK_SQL_SYNTAX_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioValidationError) as exc_info:
            client.sql.query("SELEC * FORM companies")
        assert exc_info.value.status_code == 400
        assert exc_info.value.code == "filter_error"
        client.close()

    @respx.mock
    def test_query_permission_error(self) -> None:
        """Non-Enterprise plans get a 403."""
        respx.post(f"{BASE_URL}/sql").mock(
            return_value=httpx.Response(403, json=MOCK_PERMISSION_ERROR)
        )
        client = _sync_client()
        with pytest.raises(AttioPermissionError) as exc_info:
            client.sql.query("SELECT * FROM companies")
        assert exc_info.value.status_code == 403
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestSqlResourceAsync:
    @respx.mock
    async def test_query(self) -> None:
        route = respx.post(f"{BASE_URL}/sql").mock(
            return_value=httpx.Response(200, json=MOCK_SQL_RESULT)
        )
        client = _async_client()
        result = await client.sql.query("SELECT * FROM companies")

        assert route.called
        assert isinstance(result, SqlQueryResult)
        assert len(result.rows) == 2
        assert result.rows[0]["name"] == "Acme Corp"
        await client.close()

    @respx.mock
    async def test_query_syntax_error(self) -> None:
        respx.post(f"{BASE_URL}/sql").mock(
            return_value=httpx.Response(400, json=MOCK_SQL_SYNTAX_ERROR)
        )
        client = _async_client()
        with pytest.raises(AttioValidationError):
            await client.sql.query("SELEC * FORM companies")
        await client.close()
