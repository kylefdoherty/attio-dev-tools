"""Integration tests for Records resource using real API responses."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestRecordsIntegration:
    @my_vcr.use_cassette("records_query_people.yaml")
    def test_query_people(self, client):
        """Query people records (the primary way to list records in Attio)."""
        result = client.records.query("people", limit=5)
        assert hasattr(result, "data")
        if len(result.data) > 0:
            record = result.data[0]
            assert hasattr(record, "id")
            assert hasattr(record.id, "record_id")
            assert hasattr(record.id, "object_id")
            assert hasattr(record.id, "workspace_id")
            assert hasattr(record, "values")
            assert hasattr(record, "created_at")
            assert hasattr(record, "web_url")
            assert isinstance(record.values, dict)

    @my_vcr.use_cassette("records_query_companies.yaml")
    def test_query_companies(self, client):
        """Query company records to verify cross-object support."""
        result = client.records.query("companies", limit=5)
        assert hasattr(result, "data")
        if len(result.data) > 0:
            record = result.data[0]
            assert record.id.object_id is not None
            assert record.id.record_id is not None
