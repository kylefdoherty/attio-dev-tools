"""Integration tests for Select Options resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestSelectOptionsIntegration:
    @my_vcr.use_cassette("select_options_list_companies_categories.yaml")
    def test_list_select_options(self, client):
        """List select options for a select-type attribute.

        Tries companies/categories. If the attribute doesn't exist or has
        no options, the test handles empty results gracefully.
        """
        result = client.select_options.list("objects", "companies", "categories")
        # The endpoint should return a ListResponse; data may be empty
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        if len(result.data) > 0:
            option = result.data[0]
            # Verify shape of a SelectOption
            assert hasattr(option, "id")
            assert isinstance(option.id.workspace_id, str)
            assert isinstance(option.id.object_id, str)
            assert isinstance(option.id.attribute_id, str)
            assert isinstance(option.id.option_id, str)
            assert isinstance(option.title, str)
            assert isinstance(option.is_archived, bool)
