"""Shared test fixtures for the Attio CLI test suite."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Create a mock AttioClient with all resource properties."""
    client = MagicMock()

    # Mock people resource methods
    client.people = MagicMock()
    client.companies = MagicMock()
    client.deals = MagicMock()
    client.records = MagicMock()
    client.objects = MagicMock()
    client.lists = MagicMock()
    client.entries = MagicMock()
    client.notes = MagicMock()
    client.tasks = MagicMock()
    client.webhooks = MagicMock()
    client.workspace_members = MagicMock()
    client.self_ = MagicMock()

    return client


@pytest.fixture
def mock_record():
    """Create a mock Record with typical structure."""
    record = MagicMock()
    record.id = MagicMock()
    record.id.record_id = "rec_test123"
    record.id.object_id = "obj_people"
    record.id.workspace_id = "ws_test"
    record.created_at = "2026-01-01T00:00:00Z"
    record.web_url = "https://app.attio.com/record/rec_test123"
    record.values = {
        "name": [MagicMock(**{
            "model_dump.return_value": {"first_name": "Jane", "last_name": "Doe", "attribute_type": "personal-name"},
        })],
        "email_addresses": [MagicMock(**{
            "model_dump.return_value": {"email_address": "jane@example.com", "attribute_type": "email"},
        })],
    }
    return record


@pytest.fixture
def mock_list_response(mock_record):
    """Create a mock ListResponse containing records."""
    response = MagicMock()
    response.data = [mock_record]
    return response
