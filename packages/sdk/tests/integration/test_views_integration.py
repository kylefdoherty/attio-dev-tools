"""Integration tests for Views resource."""

from __future__ import annotations

from datetime import datetime

from tests.integration.conftest import my_vcr


class TestViewsIntegration:
    @my_vcr.use_cassette("views_list_for_people.yaml")
    def test_list_views_for_people(self, client):
        """List views for the people object."""
        result = client.views.list_for_object("people")

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert hasattr(result, "pagination")

        if len(result.data) > 0:
            view = result.data[0]
            assert hasattr(view.id, "view_id")
            assert isinstance(view.id.view_id, str)
            assert isinstance(view.title, str)
            assert isinstance(view.created_at, datetime)

    @my_vcr.use_cassette("views_list_for_list.yaml")
    def test_list_views_for_list(self, client):
        """List all lists first to find a slug, then list views for that list."""
        all_lists = client.lists.list()

        if len(all_lists.data) == 0:
            # No lists in workspace -- nothing to test
            return

        slug = all_lists.data[0].api_slug
        result = client.views.list_for_list(slug)

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert hasattr(result, "pagination")

        if len(result.data) > 0:
            view = result.data[0]
            assert hasattr(view.id, "view_id")
            assert isinstance(view.title, str)
            assert isinstance(view.created_at, datetime)
