"""Tests for the api escape-hatch command."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


@patch("attio_cli.commands.api.get_client")
class TestApiGet:
    def test_get_basic(self, mock_gc):
        mock_client = MagicMock()
        mock_client.http.request.return_value = {"data": [{"slug": "people"}]}
        mock_gc.return_value = mock_client
        result = runner.invoke(app, ["api", "GET", "/objects"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["slug"] == "people"
        mock_client.http.request.assert_called_once_with("GET", "/objects", json=None, params=None)

    def test_get_with_limit_offset(self, mock_gc):
        mock_client = MagicMock()
        mock_client.http.request.return_value = {"data": []}
        mock_gc.return_value = mock_client
        result = runner.invoke(app, ["api", "GET", "/objects", "--limit", "5", "--offset", "10"])
        assert result.exit_code == 0
        mock_client.http.request.assert_called_once_with("GET", "/objects", json=None, params={"limit": 5, "offset": 10})

    def test_get_strips_v2_prefix(self, mock_gc):
        mock_client = MagicMock()
        mock_client.http.request.return_value = {"data": []}
        mock_gc.return_value = mock_client
        result = runner.invoke(app, ["api", "GET", "/v2/objects"])
        assert result.exit_code == 0
        mock_client.http.request.assert_called_once_with("GET", "/objects", json=None, params=None)

    def test_get_adds_leading_slash(self, mock_gc):
        mock_client = MagicMock()
        mock_client.http.request.return_value = {"data": []}
        mock_gc.return_value = mock_client
        result = runner.invoke(app, ["api", "GET", "objects"])
        assert result.exit_code == 0
        mock_client.http.request.assert_called_once_with("GET", "/objects", json=None, params=None)


@patch("attio_cli.commands.api.get_client")
class TestApiPost:
    def test_post_with_body(self, mock_gc):
        mock_client = MagicMock()
        mock_client.http.request.return_value = {"data": []}
        mock_gc.return_value = mock_client
        body = '{"filter": {"name": "Jane"}}'
        result = runner.invoke(app, ["api", "POST", "/objects/people/records/query", "--body", body])
        assert result.exit_code == 0
        mock_client.http.request.assert_called_once_with(
            "POST", "/objects/people/records/query", json={"filter": {"name": "Jane"}}, params=None
        )

    def test_post_invalid_body(self, mock_gc):
        result = runner.invoke(app, ["api", "POST", "/path", "--body", "not-json"])
        assert result.exit_code != 0


@patch("attio_cli.commands.api.get_client")
class TestApiErrors:
    def test_invalid_method(self, mock_gc):
        result = runner.invoke(app, ["api", "INVALID", "/path"])
        assert result.exit_code != 0

    def test_api_error_handling(self, mock_gc):
        from attio import NotFoundError

        mock_client = MagicMock()
        mock_client.http.request.side_effect = NotFoundError(
            "Not found", status_code=404, code="not_found"
        )
        mock_gc.return_value = mock_client
        result = runner.invoke(app, ["api", "GET", "/objects/nonexistent"])
        assert result.exit_code != 0


@patch("attio_cli.commands.api.get_client")
class TestApiOutput:
    def test_always_json_output(self, mock_gc):
        mock_client = MagicMock()
        mock_client.http.request.return_value = {"data": "test"}
        mock_gc.return_value = mock_client
        # Even without --json flag, api command outputs JSON
        result = runner.invoke(app, ["api", "GET", "/test"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"] == "test"
