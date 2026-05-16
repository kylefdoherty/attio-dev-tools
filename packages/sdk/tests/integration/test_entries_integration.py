"""Integration tests for Entries resource."""

from __future__ import annotations

import pytest

from attio._exceptions import NotFoundError
from tests.integration.conftest import my_vcr


class TestEntriesIntegration:
    @my_vcr.use_cassette("entries_list.yaml")
    def test_list_entries_not_supported(self, client):
        """entries.list() uses GET /lists/{slug}/entries which does not exist in
        the Attio v2 API (only POST=create and PUT=upsert are defined on that
        path).  This test documents the bug so it can be fixed later -- use
        entries.query() to list entries instead."""
        all_lists = client.lists.list()
        if len(all_lists.data) == 0:
            pytest.skip("No lists in workspace")

        slug = all_lists.data[0].api_slug
        with pytest.raises(NotFoundError):
            client.entries.list(slug, limit=5)

    @my_vcr.use_cassette("entries_query_list.yaml")
    def test_list_entries_via_query(self, client):
        """Use query (the correct endpoint) to list entries."""
        all_lists = client.lists.list()
        assert len(all_lists.data) >= 0

        if len(all_lists.data) == 0:
            return

        slug = all_lists.data[0].api_slug
        result = client.entries.query(slug, limit=5)

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

        for entry in result.data:
            assert hasattr(entry.id, "entry_id") and entry.id.entry_id
            assert entry.parent_record_id
            assert entry.parent_object
            assert entry.created_at is not None
            # Critical: the model field is entry_values, NOT values
            assert hasattr(entry, "entry_values")
            assert isinstance(entry.entry_values, dict)

    @my_vcr.use_cassette("entries_query.yaml")
    def test_query_entries(self, client):
        all_lists = client.lists.list()
        assert len(all_lists.data) >= 0

        if len(all_lists.data) == 0:
            return

        slug = all_lists.data[0].api_slug
        result = client.entries.query(slug, limit=5)

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert len(result.data) >= 0

        for entry in result.data:
            assert hasattr(entry.id, "entry_id") and entry.id.entry_id
            assert entry.parent_record_id
            assert entry.parent_object
            assert entry.created_at is not None
            assert hasattr(entry, "entry_values")
            assert isinstance(entry.entry_values, dict)

    @my_vcr.use_cassette("entries_get.yaml")
    def test_get_entry(self, client):
        all_lists = client.lists.list()
        assert len(all_lists.data) >= 0

        if len(all_lists.data) == 0:
            return

        slug = all_lists.data[0].api_slug

        # Query to find an entry_id
        query_result = client.entries.query(slug, limit=1)
        if len(query_result.data) == 0:
            return

        entry_id = query_result.data[0].id.entry_id

        # Fetch the individual entry
        entry = client.entries.get(slug, entry_id)
        assert entry.id.entry_id == entry_id
        assert entry.parent_record_id
        assert entry.parent_object
        assert entry.created_at is not None
        assert hasattr(entry, "entry_values")
        assert isinstance(entry.entry_values, dict)
