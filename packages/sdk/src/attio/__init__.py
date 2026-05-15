"""Attio Python SDK — Official Python client for the Attio API."""

from attio._client import AsyncAttioClient, AttioClient
from attio._exceptions import (
    AttioAPIError,
    AttioConnectionError,
    AttioError,
    AttioPermissionError,
    AttioTimeoutError,
    AttioValidationError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
)
from attio.models.webhooks import WebhookEventType
from attio.webhook_utils import verify_webhook_signature

__all__ = [
    "AsyncAttioClient",
    "AttioAPIError",
    "AttioClient",
    "AttioConnectionError",
    "AttioError",
    "AttioPermissionError",
    "AttioTimeoutError",
    "AttioValidationError",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "RateLimitError",
    "WebhookEventType",
    "verify_webhook_signature",
]

__version__ = "0.1.0"
