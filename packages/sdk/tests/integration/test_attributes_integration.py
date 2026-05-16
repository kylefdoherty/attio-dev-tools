"""Integration tests for Attributes resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestAttributesIntegration:
    @my_vcr.use_cassette("attributes_list_people.yaml")
    def test_list_people_attributes(self, client):
        result = client.attributes.list("objects", "people")
        assert len(result.data) > 0
        attr = result.data[0]
        assert hasattr(attr, "id")
        assert hasattr(attr, "title")
        assert hasattr(attr, "api_slug")
        assert hasattr(attr, "type")
        assert hasattr(attr, "is_system_attribute")
        assert hasattr(attr, "is_writable")
        assert hasattr(attr, "is_required")
        assert hasattr(attr, "is_unique")
        assert hasattr(attr, "is_multiselect")
        assert hasattr(attr, "config")
