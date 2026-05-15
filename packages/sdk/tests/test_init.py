"""Tests for the public API surface of the attio package."""

from __future__ import annotations

import attio

# The complete set of names that must be importable from the top-level package.
EXPECTED_PUBLIC_NAMES = {
    # Clients
    "AttioClient",
    "AsyncAttioClient",
    # Exceptions
    "AttioError",
    "AttioAPIError",
    "RateLimitError",
    "AuthenticationError",
    "AttioPermissionError",
    "NotFoundError",
    "ConflictError",
    "AttioValidationError",
    "AttioConnectionError",
    "AttioTimeoutError",
    # Webhook helpers
    "verify_webhook_signature",
    "WebhookEventType",
}


class TestPublicAPI:
    """Verify that the public API surface is complete and correct."""

    def test_version_is_set(self) -> None:
        assert hasattr(attio, "__version__")
        assert isinstance(attio.__version__, str)
        assert attio.__version__ == "0.1.0"

    def test_all_is_defined(self) -> None:
        assert hasattr(attio, "__all__")
        assert isinstance(attio.__all__, list)

    def test_all_matches_expected(self) -> None:
        actual = set(attio.__all__)
        assert actual == EXPECTED_PUBLIC_NAMES, (
            f"Mismatch between __all__ and expected names.\n"
            f"  Missing from __all__: {EXPECTED_PUBLIC_NAMES - actual}\n"
            f"  Extra in __all__: {actual - EXPECTED_PUBLIC_NAMES}"
        )

    def test_all_names_importable(self) -> None:
        for name in EXPECTED_PUBLIC_NAMES:
            obj = getattr(attio, name, None)
            assert obj is not None, f"{name!r} is listed in expected names but not importable from attio"

    def test_all_entries_are_importable(self) -> None:
        """Every entry in __all__ should be an attribute of the module."""
        for name in attio.__all__:
            assert hasattr(attio, name), f"{name!r} is in __all__ but not an attribute of attio"

    def test_attio_client_importable(self) -> None:
        from attio import AttioClient

        assert AttioClient is not None

    def test_async_attio_client_importable(self) -> None:
        from attio import AsyncAttioClient

        assert AsyncAttioClient is not None

    def test_exceptions_importable(self) -> None:
        from attio import (
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

        # Verify exception hierarchy
        assert issubclass(AttioAPIError, AttioError)
        assert issubclass(RateLimitError, AttioAPIError)
        assert issubclass(AuthenticationError, AttioAPIError)
        assert issubclass(AttioPermissionError, AttioAPIError)
        assert issubclass(NotFoundError, AttioAPIError)
        assert issubclass(ConflictError, AttioAPIError)
        assert issubclass(AttioValidationError, AttioAPIError)
        assert issubclass(AttioConnectionError, AttioError)
        assert issubclass(AttioTimeoutError, AttioError)

    def test_webhook_event_type_importable(self) -> None:
        from attio import WebhookEventType

        assert hasattr(WebhookEventType, "RECORD_CREATED")
        assert WebhookEventType.RECORD_CREATED == "record.created"

    def test_verify_webhook_signature_importable(self) -> None:
        from attio import verify_webhook_signature

        assert callable(verify_webhook_signature)

    def test_client_has_all_resources(self) -> None:
        """Verify AttioClient exposes all expected resource properties."""
        expected_resources = [
            "objects",
            "records",
            "entries",
            "lists",
            "attributes",
            "select_options",
            "statuses",
            "notes",
            "tasks",
            "webhooks",
            "workspace_members",
            "self_",
            "views",
            "comments",
            "threads",
            "files",
            "meetings",
            "call_recordings",
            "transcripts",
            # Convenience wrappers
            "people",
            "companies",
            "deals",
            "users",
            "workspaces_",
        ]
        client = attio.AttioClient(api_key="test-key")
        for resource_name in expected_resources:
            assert hasattr(client, resource_name), (
                f"AttioClient missing resource: {resource_name}"
            )
        client.close()

    def test_async_client_has_all_resources(self) -> None:
        """Verify AsyncAttioClient exposes all expected resource properties."""
        expected_resources = [
            "objects",
            "records",
            "entries",
            "lists",
            "attributes",
            "select_options",
            "statuses",
            "notes",
            "tasks",
            "webhooks",
            "workspace_members",
            "self_",
            "views",
            "comments",
            "threads",
            "files",
            "meetings",
            "call_recordings",
            "transcripts",
            # Convenience wrappers
            "people",
            "companies",
            "deals",
            "users",
            "workspaces_",
        ]
        client = attio.AsyncAttioClient(api_key="test-key")
        for resource_name in expected_resources:
            assert hasattr(client, resource_name), (
                f"AsyncAttioClient missing resource: {resource_name}"
            )
