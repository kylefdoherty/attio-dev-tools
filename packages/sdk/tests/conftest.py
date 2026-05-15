"""Shared test fixtures for the Attio SDK test suite."""

from __future__ import annotations

import pytest
import respx

from attio import AsyncAttioClient, AttioClient

BASE_URL = "https://api.attio.com/v2"
TEST_API_KEY = "test_api_key_12345"


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def sync_client() -> AttioClient:
    """Create a sync client with a test API key and zero retry delay for fast tests."""
    return AttioClient(
        api_key=TEST_API_KEY,
        base_url=BASE_URL,
        max_retries=3,
        retry_delay=0.0,
        timeout=5.0,
    )


@pytest.fixture
def async_client() -> AsyncAttioClient:
    """Create an async client with a test API key and zero retry delay for fast tests."""
    return AsyncAttioClient(
        api_key=TEST_API_KEY,
        base_url=BASE_URL,
        max_retries=3,
        retry_delay=0.0,
        timeout=5.0,
    )


@pytest.fixture
def mock_api() -> respx.MockRouter:
    """Create a respx mock router targeting the Attio API base URL."""
    with respx.mock(base_url=BASE_URL) as router:
        yield router
