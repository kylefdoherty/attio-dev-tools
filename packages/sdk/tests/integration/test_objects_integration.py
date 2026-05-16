"""Integration tests for Objects resource using real API responses."""

from __future__ import annotations

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

    @my_vcr.use_cassette("objects_get_people.yaml")
    def test_get_people_object(self, client):
        result = client.objects.get("people")
        assert result.api_slug == "people"
        assert result.id.object_id is not None
        assert result.id.workspace_id is not None
