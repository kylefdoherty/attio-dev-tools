"""Integration tests for Deals standard object wrapper using real API responses."""

from __future__ import annotations

from datetime import datetime

from attio.models.records import Record

from tests.integration.conftest import my_vcr


class TestDealsIntegration:
    @my_vcr.use_cassette("deals_list.yaml")
    def test_deals_list(self, client):
        """List deals via the convenience wrapper.

        Note: The deals object may need to be enabled in the workspace.
        If it 404s, the workspace likely doesn't have deals configured.
        """
        try:
            result = client.deals.list(limit=5)
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
        except Exception as e:
            if hasattr(e, "status_code") and e.status_code == 404:
                import warnings

                warnings.warn(
                    "deals.list() returned 404 -- the deals object may not be "
                    "enabled in this workspace."
                )
            else:
                raise

    @my_vcr.use_cassette("deals_query.yaml")
    def test_deals_query(self, client):
        """Query deals via the convenience wrapper."""
        try:
            result = client.deals.query(limit=5)
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
        except Exception as e:
            if hasattr(e, "status_code") and e.status_code == 404:
                import warnings

                warnings.warn(
                    "deals.query() returned 404 -- the deals object may not be "
                    "enabled in this workspace."
                )
            else:
                raise
