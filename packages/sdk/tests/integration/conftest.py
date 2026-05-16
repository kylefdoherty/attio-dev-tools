"""Shared fixtures and VCR configuration for integration tests.

These tests use VCR.py to record and replay real API responses.
Cassette files (YAML) are committed to the repo so tests work without an API key.

To record new cassettes:
    VCR_RECORD_MODE=all \
    ATTIO_API_KEY=$(op read "op://Personal/attio-dev-tools/credential") \
    python -m pytest tests/integration/ -v

To replay from existing cassettes (default, no API key needed):
    python -m pytest tests/integration/ -v
"""

from __future__ import annotations

import os
import subprocess

import pytest
import vcr

CASSETTE_DIR = os.path.join(os.path.dirname(__file__), "cassettes")
RECORD_MODE = os.environ.get("VCR_RECORD_MODE", "none")


def get_api_key() -> str | None:
    """Get API key from env var or 1Password CLI."""
    key = os.environ.get("ATTIO_API_KEY")
    if key:
        return key
    try:
        result = subprocess.run(
            ["op", "read", "op://Personal/attio-dev-tools/credential"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _scrub_request(request):
    """Remove sensitive data from recorded requests."""
    if "authorization" in request.headers:
        request.headers["authorization"] = "Bearer sk_test_REDACTED"
    if "Authorization" in request.headers:
        request.headers["Authorization"] = "Bearer sk_test_REDACTED"
    return request


def _scrub_response(response):
    """Scrub PII from recorded responses for public repo safety."""
    import json as _json

    body = response.get("body", {}).get("string", "")
    if body:
        try:
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            data = _json.loads(body)
            _scrub_dict(data)
            response["body"]["string"] = _json.dumps(data)
        except (_json.JSONDecodeError, TypeError, UnicodeDecodeError):
            pass
    return response


_SCRUB_FIELDS = {
    "first_name": "Test",
    "last_name": "User",
    "full_name": "Test User",
    "email_address": "test@example.com",
    "workspace_name": "Test Workspace",
    "workspace_slug": "test-workspace",
    "secret": "REDACTED_WEBHOOK_SECRET",
}


def _scrub_dict(obj):
    """Recursively scrub known PII fields from response data."""
    if isinstance(obj, dict):
        for key, replacement in _SCRUB_FIELDS.items():
            if key in obj and isinstance(obj[key], str):
                obj[key] = replacement
        for value in obj.values():
            _scrub_dict(value)
    elif isinstance(obj, list):
        for item in obj:
            _scrub_dict(item)


def _patch_vcr_httpcore_bytes():
    """Monkey-patch VCR's httpcore stubs to fix str/bytes body mismatch.

    VCR.py 8.x with decode_compressed_response=True stores response bodies
    as Python str in YAML cassettes.  But httpcore.Response(content=...)
    expects bytes, causing a TypeError on playback with httpx 0.28+.

    This patches _deserialize_response to call convert_body_to_bytes before
    constructing the httpcore Response.
    """
    import vcr.stubs.httpcore_stubs as stubs
    from vcr.serializers.compat import convert_body_to_bytes as _to_bytes

    _orig = stubs._deserialize_response

    def _fixed_deserialize_response(vcr_response):
        # Ensure body is bytes for both legacy and modern cassette formats
        if "status_code" not in vcr_response:
            _to_bytes(vcr_response)
        return _orig(vcr_response)

    stubs._deserialize_response = _fixed_deserialize_response


_patch_vcr_httpcore_bytes()


# Shared VCR instance used by all integration test modules
my_vcr = vcr.VCR(
    cassette_library_dir=CASSETTE_DIR,
    record_mode=RECORD_MODE,
    match_on=["method", "path", "query"],
    filter_headers=["authorization", "Authorization", "Cookie"],
    before_record_request=_scrub_request,
    before_record_response=_scrub_response,
    decode_compressed_response=True,
)


@pytest.fixture(scope="session")
def api_key():
    """Provide an API key; skip if recording and no key available."""
    key = get_api_key()
    if RECORD_MODE != "none" and not key:
        pytest.skip("No ATTIO_API_KEY available (set env var or install op CLI)")
    # When replaying, we still need a dummy key for the client constructor
    return key or "sk_test_REPLAY_DUMMY"


@pytest.fixture(scope="session")
def client(api_key):
    """Create a real AttioClient for integration tests."""
    from attio import AttioClient

    c = AttioClient(api_key=api_key)
    yield c
    c.close()
