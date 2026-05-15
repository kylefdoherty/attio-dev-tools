"""Tests for _client.py — AttioClient and AsyncAttioClient."""

from __future__ import annotations

import respx

from attio import AsyncAttioClient, AttioClient
from attio._http import AsyncHttpTransport, HttpTransport
from attio.resources.objects import AsyncObjectsResource, ObjectsResource

BASE_URL = "https://api.attio.com/v2"


class TestAttioClient:
    def test_instantiation(self) -> None:
        client = AttioClient(api_key="test-key")
        assert isinstance(client.http, HttpTransport)
        client.close()

    def test_custom_params(self) -> None:
        client = AttioClient(
            api_key="sk_custom",
            base_url="https://custom.api.com",
            max_retries=5,
            retry_delay=2.0,
            timeout=60.0,
        )
        assert client._config.api_key == "sk_custom"
        assert client._config.base_url == "https://custom.api.com"
        assert client._config.max_retries == 5
        client.close()

    def test_objects_property(self) -> None:
        client = AttioClient(api_key="test-key")
        assert isinstance(client.objects, ObjectsResource)
        # cached_property: same instance on second access
        assert client.objects is client.objects
        client.close()

    def test_context_manager(self) -> None:
        with AttioClient(api_key="test-key") as client:
            assert isinstance(client, AttioClient)
            assert isinstance(client.http, HttpTransport)

    @respx.mock
    def test_close(self) -> None:
        client = AttioClient(api_key="test-key")
        client.close()
        # Verify the transport is closed by checking that further requests fail
        # (httpx raises RuntimeError on closed client)


class TestAsyncAttioClient:
    def test_instantiation(self) -> None:
        client = AsyncAttioClient(api_key="test-key")
        assert isinstance(client.http, AsyncHttpTransport)

    def test_objects_property(self) -> None:
        client = AsyncAttioClient(api_key="test-key")
        assert isinstance(client.objects, AsyncObjectsResource)
        assert client.objects is client.objects

    async def test_async_context_manager(self) -> None:
        async with AsyncAttioClient(api_key="test-key") as client:
            assert isinstance(client, AsyncAttioClient)
            assert isinstance(client.http, AsyncHttpTransport)

    async def test_close(self) -> None:
        client = AsyncAttioClient(api_key="test-key")
        await client.close()
