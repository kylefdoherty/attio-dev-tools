"""Configuration constants and client config for the Attio SDK."""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_BASE_URL: str = "https://api.attio.com/v2"
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_DELAY: float = 1.0  # seconds
DEFAULT_TIMEOUT: float = 30.0  # seconds
API_VERSION: str = "v2"
SDK_VERSION: str = "0.1.0"
USER_AGENT: str = f"attio-python/{SDK_VERSION}"


@dataclass(frozen=True)
class ClientConfig:
    """Internal configuration for the Attio HTTP transport."""

    api_key: str
    base_url: str = field(default=DEFAULT_BASE_URL)
    max_retries: int = field(default=DEFAULT_MAX_RETRIES)
    retry_delay: float = field(default=DEFAULT_RETRY_DELAY)
    timeout: float = field(default=DEFAULT_TIMEOUT)
