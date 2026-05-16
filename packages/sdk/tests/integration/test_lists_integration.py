"""Integration tests for Lists resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestListsIntegration:
    @my_vcr.use_cassette("lists_list.yaml")
    def test_list_lists(self, client):
        result = client.lists.list()
        assert hasattr(result, "data")
        if len(result.data) > 0:
            lst = result.data[0]
            assert hasattr(lst, "id")
            assert hasattr(lst, "api_slug")
            assert hasattr(lst, "name")

    @my_vcr.use_cassette("lists_get.yaml")
    def test_get_list(self, client):
        # First list all lists to discover a valid slug
        all_lists = client.lists.list()
        assert len(all_lists.data) >= 0

        if len(all_lists.data) == 0:
            # No lists in workspace -- nothing to fetch
            return

        slug = all_lists.data[0].api_slug

        # Fetch the individual list by slug
        lst = client.lists.get(slug)
        assert lst.api_slug == slug
        assert isinstance(lst.name, str) and len(lst.name) > 0
        assert hasattr(lst.id, "list_id") and lst.id.list_id
        assert lst.created_at is not None
