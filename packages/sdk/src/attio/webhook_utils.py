"""Utilities for verifying Attio webhook signatures."""

from __future__ import annotations

import hashlib
import hmac


def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """Verify that a webhook payload was signed by Attio.

    Args:
        raw_body: The raw request body bytes.
        signature: The signature from the webhook request header.
        secret: The webhook secret provided when the webhook was created.

    Returns:
        True if the signature is valid, False otherwise.
    """
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
