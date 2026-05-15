"""Tests for _config.py."""

from __future__ import annotations

from attio._config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    ClientConfig,
)


class TestClientConfig:
    def test_defaults(self) -> None:
        config = ClientConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.base_url == DEFAULT_BASE_URL
        assert config.max_retries == DEFAULT_MAX_RETRIES
        assert config.retry_delay == DEFAULT_RETRY_DELAY
        assert config.timeout == DEFAULT_TIMEOUT

    def test_custom_values(self) -> None:
        config = ClientConfig(
            api_key="sk_custom",
            base_url="https://custom.api.com",
            max_retries=5,
            retry_delay=2.0,
            timeout=60.0,
        )
        assert config.api_key == "sk_custom"
        assert config.base_url == "https://custom.api.com"
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.timeout == 60.0

    def test_frozen(self) -> None:
        config = ClientConfig(api_key="test-key")
        try:
            config.api_key = "new-key"  # type: ignore[misc]
            raise AssertionError("Expected FrozenInstanceError")
        except AttributeError:
            pass

    def test_default_constants(self) -> None:
        assert DEFAULT_BASE_URL == "https://api.attio.com/v2"
        assert DEFAULT_MAX_RETRIES == 3
        assert DEFAULT_RETRY_DELAY == 1.0
        assert DEFAULT_TIMEOUT == 30.0
