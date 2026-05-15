"""Tests for _exceptions.py."""

from __future__ import annotations

import httpx
import pytest

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
    _raise_for_status,
)


class TestAttioError:
    def test_base_error(self) -> None:
        err = AttioError("something went wrong", status_code=500, code="internal", body={"detail": "oops"})
        assert str(err) == "something went wrong"
        assert err.message == "something went wrong"
        assert err.status_code == 500
        assert err.code == "internal"
        assert err.body == {"detail": "oops"}

    def test_base_error_defaults(self) -> None:
        err = AttioError("fail")
        assert err.status_code == 0
        assert err.code is None
        assert err.body is None

    def test_is_exception(self) -> None:
        assert issubclass(AttioError, Exception)


class TestAttioAPIError:
    def test_inherits_from_attio_error(self) -> None:
        assert issubclass(AttioAPIError, AttioError)

    def test_instantiation(self) -> None:
        err = AttioAPIError("bad request", status_code=400)
        assert err.status_code == 400


class TestRateLimitError:
    def test_instantiation(self) -> None:
        err = RateLimitError(2.0, body={"message": "slow down"})
        assert err.retry_after == 2.0
        assert err.status_code == 429
        assert err.code == "rate_limit_exceeded"
        assert "2.0" in str(err)

    def test_inherits(self) -> None:
        assert issubclass(RateLimitError, AttioAPIError)
        assert issubclass(RateLimitError, AttioError)


class TestAuthenticationError:
    def test_instantiation(self) -> None:
        err = AuthenticationError("unauthorized", status_code=401)
        assert err.status_code == 401
        assert issubclass(AuthenticationError, AttioAPIError)


class TestAttioPermissionError:
    def test_instantiation(self) -> None:
        err = AttioPermissionError("forbidden", status_code=403)
        assert err.status_code == 403


class TestNotFoundError:
    def test_instantiation(self) -> None:
        err = NotFoundError("not found", status_code=404)
        assert err.status_code == 404


class TestConflictError:
    def test_instantiation(self) -> None:
        err = ConflictError("conflict", status_code=409)
        assert err.status_code == 409


class TestAttioValidationError:
    def test_instantiation(self) -> None:
        err = AttioValidationError("validation failed", status_code=400)
        assert err.status_code == 400


class TestAttioConnectionError:
    def test_instantiation(self) -> None:
        err = AttioConnectionError("network error")
        assert err.status_code == 0
        assert issubclass(AttioConnectionError, AttioError)


class TestAttioTimeoutError:
    def test_instantiation(self) -> None:
        err = AttioTimeoutError("timed out")
        assert err.status_code == 0
        assert issubclass(AttioTimeoutError, AttioError)


class TestRaiseForStatus:
    def _make_response(self, status_code: int, json_body: dict | None = None, text: str = "") -> httpx.Response:
        """Helper to create a mock httpx.Response."""
        if json_body is not None:
            import json

            content = json.dumps(json_body).encode()
            headers = {"content-type": "application/json"}
        else:
            content = text.encode()
            headers = {"content-type": "text/plain"}
        return httpx.Response(status_code=status_code, content=content, headers=headers)

    def test_success_no_raise(self) -> None:
        response = self._make_response(200, {"data": {}})
        _raise_for_status(response)  # should not raise

    def test_400_raises_validation_error(self) -> None:
        response = self._make_response(400, {"message": "bad input", "code": "validation_type"})
        with pytest.raises(AttioValidationError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 400
        assert exc_info.value.message == "bad input"
        assert exc_info.value.code == "validation_type"

    def test_401_raises_authentication_error(self) -> None:
        response = self._make_response(401, {"message": "invalid token"})
        with pytest.raises(AuthenticationError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 401

    def test_403_raises_permission_error(self) -> None:
        response = self._make_response(403, {"message": "missing scope"})
        with pytest.raises(AttioPermissionError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 403

    def test_404_raises_not_found_error(self) -> None:
        response = self._make_response(404, {"message": "resource not found", "code": "not_found"})
        with pytest.raises(NotFoundError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 404

    def test_409_raises_conflict_error(self) -> None:
        response = self._make_response(409, {"message": "slug conflict", "code": "slug_conflict"})
        with pytest.raises(ConflictError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 409

    def test_429_raises_rate_limit_error(self) -> None:
        response = httpx.Response(
            status_code=429,
            content=b'{"message": "rate limited"}',
            headers={"content-type": "application/json", "retry-after": "3"},
        )
        with pytest.raises(RateLimitError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.retry_after == 3.0
        assert exc_info.value.status_code == 429

    def test_429_without_retry_after_header(self) -> None:
        response = httpx.Response(
            status_code=429,
            content=b'{"message": "rate limited"}',
            headers={"content-type": "application/json"},
        )
        with pytest.raises(RateLimitError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.retry_after == 1.0

    def test_500_raises_api_error(self) -> None:
        response = self._make_response(500, {"message": "internal error"})
        with pytest.raises(AttioAPIError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 500

    def test_non_json_body(self) -> None:
        response = self._make_response(502, text="Bad Gateway")
        with pytest.raises(AttioAPIError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 502
        assert exc_info.value.body == "Bad Gateway"

    def test_empty_body(self) -> None:
        response = self._make_response(503, text="")
        with pytest.raises(AttioAPIError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 503
