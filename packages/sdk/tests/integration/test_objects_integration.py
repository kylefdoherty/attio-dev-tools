"""Integration tests for Objects resource using real API responses."""

from __future__ import annotations

from datetime import datetime

from tests.integration.conftest import my_vcr


class TestObjectsIntegration:
    @my_vcr.use_cassette("objects_list.yaml")
    def test_list_objects(self, client):
        result = client.objects.list()
        assert len(result.data) > 0
        obj = result.data[0]
        # Verify real response shape matches our model
        assert hasattr(obj, "id")
        assert hasattr(obj.id, "workspace_id")
        assert hasattr(obj.id, "object_id")
        assert hasattr(obj, "api_slug")
        assert hasattr(obj, "singular_noun")
        assert hasattr(obj, "plural_noun")
        assert hasattr(obj, "created_at")
        # Verify types
        assert isinstance(obj.id.workspace_id, str)
        assert isinstance(obj.id.object_id, str)
        assert isinstance(obj.created_at, datetime)
        if obj.api_slug is not None:
            assert isinstance(obj.api_slug, str)
        if obj.singular_noun is not None:
            assert isinstance(obj.singular_noun, str)
        if obj.plural_noun is not None:
            assert isinstance(obj.plural_noun, str)

    @my_vcr.use_cassette("objects_get_people.yaml")
    def test_get_people_object(self, client):
        result = client.objects.get("people")
        assert result.api_slug == "people"
        assert result.id.object_id is not None
        assert result.id.workspace_id is not None
        assert isinstance(result.id.workspace_id, str)
        assert isinstance(result.id.object_id, str)
        assert isinstance(result.created_at, datetime)

    @my_vcr.use_cassette("objects_get_companies.yaml")
    def test_get_companies_object(self, client):
        result = client.objects.get("companies")
        assert result.api_slug == "companies"
        assert result.id.object_id is not None
        assert result.id.workspace_id is not None
        assert isinstance(result.id.workspace_id, str)
        assert isinstance(result.id.object_id, str)
        assert isinstance(result.created_at, datetime)
        if result.singular_noun is not None:
            assert isinstance(result.singular_noun, str)
        if result.plural_noun is not None:
            assert isinstance(result.plural_noun, str)
