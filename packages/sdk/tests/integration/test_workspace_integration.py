"""Integration tests for Workspace/Self resources."""

from __future__ import annotations

from datetime import datetime

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

    @my_vcr.use_cassette("workspace_member_get.yaml")
    def test_get_workspace_member(self, client):
        """List members first, then get one by ID."""
        members = client.workspace_members.list()
        assert len(members.data) > 0

        member_id = members.data[0].id.workspace_member_id
        member = client.workspace_members.get(member_id)

        assert member.id.workspace_member_id == member_id
        assert isinstance(member.first_name, str)
        assert isinstance(member.last_name, str)
        assert isinstance(member.email_address, str)
        assert isinstance(member.access_level, str)
        assert isinstance(member.created_at, datetime)
