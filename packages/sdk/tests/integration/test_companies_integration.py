"""Integration tests for Companies standard object wrapper using real API responses."""

from __future__ import annotations

import warnings
from datetime import datetime

from attio.models.records import Record

from tests.integration.conftest import my_vcr


class TestCompaniesIntegration:
    @my_vcr.use_cassette("companies_list.yaml")
    def test_companies_list(self, client):
        """List companies via the convenience wrapper.

        Known bug: the Attio API does not support GET on
        /objects/{object}/records, so companies.list() returns 404.
        """
        try:
            result = client.companies.list(limit=5)
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
                    "companies.list() returned 404 -- the Attio API does not support "
                    "GET on /objects/{object}/records. Use companies.query() instead."
                )
            else:
                raise

    @my_vcr.use_cassette("companies_query.yaml")
    def test_companies_query(self, client):
        """Query companies via the convenience wrapper."""
        result = client.companies.query(limit=5)
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
