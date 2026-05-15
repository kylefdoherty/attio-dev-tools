"""Tests for the webhook signature verification utility."""

from __future__ import annotations

import hashlib
import hmac

from attio.webhook_utils import verify_webhook_signature


class TestVerifyWebhookSignature:
    """Tests for verify_webhook_signature."""

    SECRET = "whsec_test_secret_12345"
    BODY = b'{"event_type":"record.created","data":{"id":"rec_01"}}'

    def _compute_signature(self, body: bytes, secret: str) -> str:
        """Helper to compute a valid HMAC-SHA256 signature."""
        return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    def test_valid_signature(self) -> None:
        """A correctly signed payload should return True."""
        signature = self._compute_signature(self.BODY, self.SECRET)
        assert verify_webhook_signature(self.BODY, signature, self.SECRET) is True

    def test_invalid_signature(self) -> None:
        """A completely wrong signature should return False."""
        assert verify_webhook_signature(self.BODY, "bad_signature_value", self.SECRET) is False

    def test_tampered_body(self) -> None:
        """A valid signature for the original body should fail against a tampered body."""
        signature = self._compute_signature(self.BODY, self.SECRET)
        tampered = b'{"event_type":"record.deleted","data":{"id":"rec_01"}}'
        assert verify_webhook_signature(tampered, signature, self.SECRET) is False

    def test_wrong_secret(self) -> None:
        """A signature computed with a different secret should return False."""
        signature = self._compute_signature(self.BODY, "wrong_secret")
        assert verify_webhook_signature(self.BODY, signature, self.SECRET) is False

    def test_empty_body(self) -> None:
        """An empty body with a matching signature should return True."""
        empty_body = b""
        signature = self._compute_signature(empty_body, self.SECRET)
        assert verify_webhook_signature(empty_body, signature, self.SECRET) is True

    def test_empty_body_wrong_signature(self) -> None:
        """An empty body with a non-matching signature should return False."""
        assert verify_webhook_signature(b"", "not_a_real_sig", self.SECRET) is False
