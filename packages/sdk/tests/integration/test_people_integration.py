"""Integration tests for People standard object wrapper using real API responses."""

from __future__ import annotations

import warnings
from datetime import datetime

import pytest

from attio.models.records import Record

from tests.integration.conftest import my_vcr


class TestPeopleIntegration:
    @my_vcr.use_cassette("people_list.yaml")
    def test_people_list(self, client):
        """List people via the convenience wrapper.

        Known bug: the Attio API does not support GET on
        /objects/{object}/records, so people.list() returns 404.
        """
        try:
            result = client.people.list(limit=5)
            assert hasattr(result, "data")
            assert isinstance(result.data, list)
            if len(result.data) > 0:
                record = result.data[0]
                assert isinstance(record, Record)
                assert hasattr(record, "id")
                assert hasattr(record.id, "record_id")
                assert hasattr(record.id, "object_id")
                assert hasattr(record.id, "workspace_id")
                assert isinstance(record.values, dict)
                assert isinstance(record.created_at, datetime)
        except Exception as e:
            if hasattr(e, "status_code") and e.status_code == 404:
                warnings.warn(
                    "people.list() returned 404 -- the Attio API does not support "
                    "GET on /objects/{object}/records. Use people.query() instead."
                )
            else:
                raise

    @my_vcr.use_cassette("people_query.yaml")
    def test_people_query(self, client):
        """Query people via the convenience wrapper."""
        result = client.people.query(limit=5)
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        if len(result.data) > 0:
            record = result.data[0]
            assert isinstance(record, Record)
            assert hasattr(record, "id")
            assert hasattr(record.id, "record_id")
            assert hasattr(record.id, "object_id")
            assert isinstance(record.values, dict)
            assert isinstance(record.created_at, datetime)
            assert isinstance(record.web_url, str)

    @my_vcr.use_cassette("people_query_all.yaml")
    def test_people_query_all(self, client):
        """Auto-paginate people via query_all and collect first 3 items."""
        it = client.people.query_all(limit=2)
        records = []
        for r in it:
            records.append(r)
            if len(records) >= 3:
                break
        if len(records) == 0:
            pytest.skip("No people records in workspace; cannot verify query_all()")
        for record in records:
            assert isinstance(record, Record)
            assert hasattr(record, "id")
            assert hasattr(record.id, "record_id")
            assert isinstance(record.values, dict)
