"""Integration tests for Threads resource."""

from __future__ import annotations

from datetime import datetime

import pytest

from tests.integration.conftest import my_vcr


class TestThreadsIntegration:
    @my_vcr.use_cassette("threads_list.yaml")
    def test_list_threads(self, client):
        """List threads for a company record and verify structure if any exist."""
        # Threads API requires record_id and object params
        companies = client.records.query("companies", limit=1)
        assert len(companies.data) > 0, "Need at least one company for threads test"
        record_id = companies.data[0].id.record_id

        result = client.threads.list(record_id=record_id, object="companies")
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        if len(result.data) == 0:
            pytest.skip("No threads for this record to verify field structure")
        for thread in result.data:
            assert hasattr(thread.id, "thread_id")
            assert isinstance(thread.id.thread_id, str)
            assert len(thread.id.thread_id) > 0
            assert isinstance(thread.comments, list)
            assert isinstance(thread.created_at, datetime)
