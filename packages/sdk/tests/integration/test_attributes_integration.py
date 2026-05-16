"""Integration tests for Attributes resource."""

from __future__ import annotations

from datetime import datetime

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
        # Verify types on the first attribute
        assert isinstance(attr.id.workspace_id, str)
        assert isinstance(attr.id.object_id, str)
        assert isinstance(attr.id.attribute_id, str)
        assert isinstance(attr.title, str)
        assert isinstance(attr.api_slug, str)
        assert isinstance(attr.type, str)
        assert isinstance(attr.is_system_attribute, bool)
        assert isinstance(attr.is_writable, bool)
        assert isinstance(attr.is_required, bool)
        assert isinstance(attr.is_unique, bool)
        assert isinstance(attr.is_multiselect, bool)
        assert isinstance(attr.created_at, datetime)

    @my_vcr.use_cassette("attributes_get_people_name.yaml")
    def test_get_people_name_attribute(self, client):
        result = client.attributes.get("objects", "people", "name")
        assert result.api_slug == "name"
        assert isinstance(result.type, str)
        assert result.is_system_attribute is True
        assert isinstance(result.id.workspace_id, str)
        assert isinstance(result.id.object_id, str)
        assert isinstance(result.id.attribute_id, str)
        assert isinstance(result.title, str)
        assert isinstance(result.created_at, datetime)

    @my_vcr.use_cassette("attributes_list_companies.yaml")
    def test_list_companies_attributes(self, client):
        result = client.attributes.list("objects", "companies")
        assert len(result.data) > 0
        attr = result.data[0]
        # Verify same shape as people attributes
        assert isinstance(attr.id.workspace_id, str)
        assert isinstance(attr.id.object_id, str)
        assert isinstance(attr.id.attribute_id, str)
        assert isinstance(attr.title, str)
        assert isinstance(attr.api_slug, str)
        assert isinstance(attr.type, str)
        assert isinstance(attr.is_system_attribute, bool)
        assert isinstance(attr.created_at, datetime)
