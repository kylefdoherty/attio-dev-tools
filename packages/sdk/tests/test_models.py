"""Tests for Pydantic models (Phase 2)."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import DataWrapper, ListResponse, PaginatedResponse, Pagination
from attio.models.common import ActorReference, AttributeValue
from attio.models.lists import AttioList, ListId
from attio.models.objects import Object, ObjectId
from attio.models.self_info import SelfInfo
from attio.models.workspace_members import WorkspaceMember, WorkspaceMemberId


class TestObjectModels:
    def test_object_from_dict(self) -> None:
        raw = {
            "id": {"workspace_id": "ws_01", "object_id": "obj_01"},
            "api_slug": "deals",
            "singular_noun": "Deal",
            "plural_noun": "Deals",
            "created_at": "2024-01-15T10:30:00.000Z",
        }
        obj = Object.model_validate(raw)
        assert obj.id.workspace_id == "ws_01"
        assert obj.id.object_id == "obj_01"
        assert obj.api_slug == "deals"
        assert obj.singular_noun == "Deal"
        assert obj.plural_noun == "Deals"
        assert isinstance(obj.created_at, datetime)

    def test_object_extra_fields_accepted(self) -> None:
        raw = {
            "id": {"workspace_id": "ws_01", "object_id": "obj_01"},
            "api_slug": "deals",
            "created_at": "2024-01-15T10:30:00.000Z",
            "unknown_field": "should not break",
        }
        obj = Object.model_validate(raw)
        assert obj.model_extra is not None
        assert obj.model_extra["unknown_field"] == "should not break"

    def test_object_optional_fields(self) -> None:
        raw = {
            "id": {"workspace_id": "ws_01", "object_id": "obj_01"},
            "created_at": "2024-01-15T10:30:00.000Z",
        }
        obj = Object.model_validate(raw)
        assert obj.api_slug is None
        assert obj.singular_noun is None
        assert obj.plural_noun is None

    def test_object_model_dump_roundtrip(self) -> None:
        raw = {
            "id": {"workspace_id": "ws_01", "object_id": "obj_01"},
            "api_slug": "deals",
            "singular_noun": "Deal",
            "plural_noun": "Deals",
            "created_at": "2024-01-15T10:30:00.000Z",
        }
        obj = Object.model_validate(raw)
        dumped = obj.model_dump()
        assert dumped["id"]["workspace_id"] == "ws_01"
        assert dumped["api_slug"] == "deals"

    def test_object_id(self) -> None:
        oid = ObjectId(workspace_id="ws_01", object_id="obj_01")
        assert oid.workspace_id == "ws_01"
        assert oid.object_id == "obj_01"


class TestListModels:
    def test_list_from_dict(self) -> None:
        raw = {
            "id": {"workspace_id": "ws_01", "list_id": "lst_01"},
            "api_slug": "sales_pipeline",
            "name": "Sales Pipeline",
            "parent_object": ["people"],
            "workspace_access": "full-access",
            "created_by_actor": {"id": "actor_01", "type": "workspace-member"},
            "created_at": "2024-01-15T10:30:00.000Z",
        }
        lst = AttioList.model_validate(raw)
        assert lst.id.list_id == "lst_01"
        assert lst.api_slug == "sales_pipeline"
        assert lst.name == "Sales Pipeline"
        assert isinstance(lst.created_at, datetime)

    def test_list_id(self) -> None:
        lid = ListId(workspace_id="ws_01", list_id="lst_01")
        assert lid.list_id == "lst_01"


class TestWorkspaceMemberModels:
    def test_workspace_member_from_dict(self) -> None:
        raw = {
            "id": {"workspace_id": "ws_01", "workspace_member_id": "wm_01"},
            "first_name": "Jane",
            "last_name": "Doe",
            "email_address": "jane@example.com",
            "avatar_url": None,
            "access_level": "admin",
            "created_at": "2024-01-15T10:30:00.000Z",
        }
        member = WorkspaceMember.model_validate(raw)
        assert member.first_name == "Jane"
        assert member.last_name == "Doe"
        assert member.email_address == "jane@example.com"
        assert member.avatar_url is None

    def test_workspace_member_id(self) -> None:
        wid = WorkspaceMemberId(workspace_id="ws_01", workspace_member_id="wm_01")
        assert wid.workspace_member_id == "wm_01"


class TestSelfInfoModel:
    def test_self_info_from_dict(self) -> None:
        raw = {
            "active": True,
            "scope": "object_configuration:read record_permission:read",
            "workspace_id": "ws_01",
            "workspace_name": "Test Workspace",
            "workspace_slug": "test-workspace",
            "workspace_logo_url": None,
            "authorized_by_workspace_member_id": "wm_01",
        }
        info = SelfInfo.model_validate(raw)
        assert info.active is True
        assert info.workspace_id == "ws_01"
        assert info.workspace_name == "Test Workspace"

    def test_self_info_minimal(self) -> None:
        info = SelfInfo.model_validate({})
        assert info.active is None
        assert info.workspace_id is None


class TestCommonModels:
    def test_actor_reference(self) -> None:
        actor = ActorReference(id="act_01", type="workspace-member")
        assert actor.id == "act_01"
        assert actor.type == "workspace-member"

    def test_actor_reference_no_id(self) -> None:
        actor = ActorReference(type="system")
        assert actor.id is None

    def test_attribute_value(self) -> None:
        raw = {
            "active_from": "2024-01-15T10:30:00.000Z",
            "active_until": None,
            "created_by_actor": {"id": "act_01", "type": "api-token"},
            "attribute_type": "text",
            "value": "Hello world",
        }
        av = AttributeValue.model_validate(raw)
        assert isinstance(av.active_from, datetime)
        assert av.active_until is None
        assert av.attribute_type == "text"
        # extra field captured
        assert av.model_extra is not None
        assert av.model_extra["value"] == "Hello world"

    def test_attribute_value_with_active_until(self) -> None:
        raw = {
            "active_from": "2024-01-15T10:30:00.000Z",
            "active_until": "2024-06-15T10:30:00.000Z",
            "created_by_actor": {"type": "system"},
            "attribute_type": "number",
            "value": 42,
        }
        av = AttributeValue.model_validate(raw)
        assert av.active_until is not None


class TestBaseWrapperModels:
    def test_data_wrapper(self) -> None:
        raw = {
            "data": {
                "id": {"workspace_id": "ws_01", "object_id": "obj_01"},
                "created_at": "2024-01-15T10:30:00.000Z",
            }
        }
        wrapper = DataWrapper[Object].model_validate(raw)
        assert isinstance(wrapper.data, Object)
        assert wrapper.data.id.object_id == "obj_01"

    def test_list_response(self) -> None:
        raw = {
            "data": [
                {"id": {"workspace_id": "ws_01", "object_id": "obj_01"}, "created_at": "2024-01-15T10:30:00.000Z"},
                {"id": {"workspace_id": "ws_01", "object_id": "obj_02"}, "created_at": "2024-01-16T10:30:00.000Z"},
            ]
        }
        response = ListResponse[Object].model_validate(raw)
        assert len(response.data) == 2
        assert response.data[0].id.object_id == "obj_01"

    def test_list_response_empty(self) -> None:
        raw = {"data": []}
        response = ListResponse[Object].model_validate(raw)
        assert len(response.data) == 0

    def test_pagination(self) -> None:
        pag = Pagination(next_cursor="cursor_abc")
        assert pag.next_cursor == "cursor_abc"

    def test_pagination_none(self) -> None:
        pag = Pagination()
        assert pag.next_cursor is None

    def test_paginated_response(self) -> None:
        raw = {
            "data": [
                {"id": {"workspace_id": "ws_01", "object_id": "obj_01"}, "created_at": "2024-01-15T10:30:00.000Z"},
            ],
            "pagination": {"next_cursor": "cursor_123"},
        }
        response = PaginatedResponse[Object].model_validate(raw)
        assert len(response.data) == 1
        assert response.pagination.next_cursor == "cursor_123"

    def test_paginated_response_no_more_pages(self) -> None:
        raw = {
            "data": [],
            "pagination": {"next_cursor": None},
        }
        response = PaginatedResponse[Object].model_validate(raw)
        assert len(response.data) == 0
        assert response.pagination.next_cursor is None
