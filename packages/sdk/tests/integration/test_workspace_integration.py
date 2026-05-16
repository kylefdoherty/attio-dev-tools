"""Integration tests for Workspace/Self resources."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestWorkspaceIntegration:
    @my_vcr.use_cassette("self_identify.yaml")
    def test_identify(self, client):
        result = client.self_.identify()
        assert result.active is not None
        assert result.workspace_id is not None
        assert result.workspace_name is not None

    @my_vcr.use_cassette("workspace_members_list.yaml")
    def test_list_members(self, client):
        result = client.workspace_members.list()
        assert len(result.data) > 0
        member = result.data[0]
        assert hasattr(member, "id")
        assert hasattr(member, "first_name")
        assert hasattr(member, "last_name")
        assert hasattr(member, "email_address")
