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
