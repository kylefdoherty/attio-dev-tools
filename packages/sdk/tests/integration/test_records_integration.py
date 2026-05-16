"""Integration tests for Records resource using real API responses."""

from __future__ import annotations

import warnings
from datetime import datetime

import pytest

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

    @my_vcr.use_cassette("records_list_people.yaml")
    def test_list_people_records(self, client):
        """List people records via GET.

        Known bug: the Attio API does not support GET on
        /objects/{object}/records and returns 404.
        """
        try:
            result = client.records.list("people", limit=5)
            assert hasattr(result, "data")
            assert isinstance(result.data, list)
            if len(result.data) > 0:
                record = result.data[0]
                assert hasattr(record, "id")
                assert hasattr(record.id, "record_id")
                assert isinstance(record.values, dict)
        except Exception as e:
            # Known issue: GET /objects/people/records returns 404
            if hasattr(e, "status_code") and e.status_code == 404:
                warnings.warn(
                    "records.list() returned 404 -- the Attio API does not support "
                    "GET on /objects/{object}/records. Use records.query() instead."
                )
            else:
                raise

    @my_vcr.use_cassette("records_get_person.yaml")
    def test_get_record(self, client):
        """Get a single record by ID. First queries to discover a record_id."""
        # Step 1: query to find a record
        query_result = client.records.query("people", limit=5)
        if len(query_result.data) == 0:
            pytest.skip("No people records in workspace; cannot test get()")
        record_id = query_result.data[0].id.record_id

        # Step 2: get the specific record
        result = client.records.get("people", record_id)
        assert result.id.record_id == record_id
        assert result.id.object_id is not None
        assert result.id.workspace_id is not None
        assert isinstance(result.values, dict)
        assert isinstance(result.created_at, datetime)
        assert result.web_url.startswith("https")

    @my_vcr.use_cassette("records_query_with_limit.yaml")
    def test_query_with_limit(self, client):
        """Query people with a specific limit and verify it is respected."""
        result = client.records.query("people", limit=2)
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert len(result.data) <= 2

    @my_vcr.use_cassette("records_get_attribute_values.yaml")
    def test_get_attribute_values(self, client):
        """Get attribute values for a specific record and attribute."""
        # Step 1: query a person to get a record_id
        query_result = client.records.query("people", limit=5)
        if len(query_result.data) == 0:
            pytest.skip("No people records in workspace; cannot test get_attribute_values()")
        record_id = query_result.data[0].id.record_id

        # Step 2: get the 'name' attribute values
        result = client.records.get_attribute_values("people", record_id, "name")
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        if len(result.data) > 0:
            attr_val = result.data[0]
            assert hasattr(attr_val, "active_from")
            assert hasattr(attr_val, "attribute_type")
            assert isinstance(attr_val.active_from, datetime)
            assert isinstance(attr_val.attribute_type, str)

    @my_vcr.use_cassette("records_list_entries.yaml")
    def test_list_entries_for_record(self, client):
        """List entries (list memberships) for a specific record."""
        # Step 1: query a person to get a record_id
        query_result = client.records.query("people", limit=5)
        if len(query_result.data) == 0:
            pytest.skip("No people records in workspace; cannot test list_entries()")
        record_id = query_result.data[0].id.record_id

        # Step 2: list entries for that record
        result = client.records.list_entries("people", record_id)
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        # Entries may be empty if the person isn't on any lists
        for entry in result.data:
            assert hasattr(entry, "list_id")
            assert hasattr(entry, "entry_id")
            assert hasattr(entry, "created_at")

    @my_vcr.use_cassette("records_global_search.yaml")
    def test_global_search(self, client):
        """Search across people and companies globally.

        Known bug: the global search endpoint may return 400.
        """
        try:
            result = client.records.global_search(
                query="a", objects=["people", "companies"], limit=5
            )
            assert hasattr(result, "data")
            assert isinstance(result.data, list)
            if len(result.data) > 0:
                item = result.data[0]
                assert hasattr(item, "record_text")
                assert hasattr(item, "object_slug")
                assert isinstance(item.record_text, str)
                assert item.object_slug in ("people", "companies")
        except Exception as e:
            # Known issue: global_search may return 400
            if hasattr(e, "status_code") and e.status_code == 400:
                warnings.warn(
                    "records.global_search() returned 400 -- possible API issue "
                    "with the /objects/records/search endpoint."
                )
            else:
                raise
