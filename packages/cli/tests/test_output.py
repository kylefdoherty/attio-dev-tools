"""Tests for the output engine (_output.py)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from attio_cli.main import app

runner = CliRunner()


class TestIsJsonMode:
    """Test JSON mode detection."""

    def test_json_flag_forces_json(self):
        """--json flag should force JSON output."""
        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = []
            mock_client.objects.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "objects", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed

    def test_non_json_produces_output(self):
        """Without --json flag, should still produce output (CliRunner is non-TTY so defaults to JSON)."""
        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = []
            mock_client.objects.list.return_value = mock_response
            mock_gc.return_value = mock_client

            # CliRunner is non-TTY, so is_json_mode returns True anyway
            result = runner.invoke(app, ["objects", "list"])
            assert result.exit_code == 0


class TestOutputList:
    """Test list output formatting."""

    def test_json_list_envelope(self):
        """JSON list output should have a 'data' key with an array."""
        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_obj = MagicMock()
            mock_obj.id = MagicMock()
            mock_obj.id.object_id = "obj_123"
            mock_obj.api_slug = "people"
            mock_obj.singular_noun = "person"
            mock_obj.plural_noun = "people"
            mock_obj.created_at = "2026-01-01T00:00:00Z"
            mock_response.data = [mock_obj]
            mock_client.objects.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "objects", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert isinstance(parsed["data"], list)
            assert len(parsed["data"]) == 1

    def test_empty_list_json(self):
        """Empty list should return empty array in JSON."""
        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = []
            mock_client.objects.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "objects", "list"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"] == []


class TestOutputSingle:
    """Test single-item output formatting."""

    def test_json_single_envelope(self):
        """JSON single output should have a 'data' key with an object."""
        with patch("attio_cli.commands.objects.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_obj = MagicMock()
            mock_obj.id = MagicMock()
            mock_obj.id.object_id = "obj_123"
            mock_obj.api_slug = "people"
            mock_obj.singular_noun = "person"
            mock_obj.plural_noun = "people"
            mock_obj.created_at = "2026-01-01T00:00:00Z"
            mock_client.objects.get.return_value = mock_obj
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "objects", "get", "people"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert "data" in parsed
