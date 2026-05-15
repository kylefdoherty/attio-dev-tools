"""Mock data factories for Attio API responses.

These mirror the response shapes from the actual Attio API documentation.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Objects
# ---------------------------------------------------------------------------

MOCK_OBJECT: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
    },
    "api_slug": "deals",
    "singular_noun": "Deal",
    "plural_noun": "Deals",
    "created_at": "2024-01-15T10:30:00.000Z",
}

MOCK_OBJECT_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_02xyz789ghi012",
    },
    "api_slug": "people",
    "singular_noun": "Person",
    "plural_noun": "People",
    "created_at": "2024-01-10T08:00:00.000Z",
}

MOCK_OBJECTS_LIST: dict[str, Any] = {
    "data": [MOCK_OBJECT, MOCK_OBJECT_2],
}

MOCK_OBJECT_SINGLE: dict[str, Any] = {
    "data": MOCK_OBJECT,
}

MOCK_OBJECT_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_03new456abc789",
        },
        "api_slug": "projects",
        "singular_noun": "Project",
        "plural_noun": "Projects",
        "created_at": "2024-06-01T12:00:00.000Z",
    },
}

MOCK_OBJECT_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
        },
        "api_slug": "deals",
        "singular_noun": "Opportunity",
        "plural_noun": "Opportunities",
        "created_at": "2024-01-15T10:30:00.000Z",
    },
}

# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------

MOCK_LIST: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "list_id": "list_01abc123def456",
    },
    "api_slug": "sales_pipeline",
    "name": "Sales Pipeline",
    "parent_object": ["people"],
    "workspace_access": "full-access",
    "workspace_member_access": [],
    "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
    "created_at": "2024-02-01T09:00:00.000Z",
}

MOCK_LIST_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "list_id": "list_02xyz789ghi012",
    },
    "api_slug": "hiring_pipeline",
    "name": "Hiring Pipeline",
    "parent_object": ["people"],
    "workspace_access": "read-only",
    "workspace_member_access": [],
    "created_by_actor": {"id": "actor_01abc", "type": "workspace-member"},
    "created_at": "2024-02-10T14:30:00.000Z",
}

MOCK_LISTS_LIST: dict[str, Any] = {
    "data": [MOCK_LIST, MOCK_LIST_2],
}

MOCK_LIST_SINGLE: dict[str, Any] = {
    "data": MOCK_LIST,
}

MOCK_LIST_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "list_id": "list_03new456abc789",
        },
        "api_slug": "onboarding",
        "name": "Onboarding",
        "parent_object": ["companies"],
        "workspace_access": "full-access",
        "workspace_member_access": [],
        "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
        "created_at": "2024-06-01T12:00:00.000Z",
    },
}

MOCK_LIST_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "list_id": "list_01abc123def456",
        },
        "api_slug": "sales_pipeline",
        "name": "Updated Pipeline",
        "parent_object": ["people"],
        "workspace_access": "read-only",
        "workspace_member_access": [],
        "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
        "created_at": "2024-02-01T09:00:00.000Z",
    },
}

# ---------------------------------------------------------------------------
# Workspace Members
# ---------------------------------------------------------------------------

MOCK_WORKSPACE_MEMBER: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "workspace_member_id": "wm_01abc123def456",
    },
    "first_name": "Jane",
    "last_name": "Doe",
    "email_address": "jane.doe@example.com",
    "avatar_url": "https://example.com/avatar/jane.png",
    "access_level": "admin",
    "created_at": "2024-01-01T00:00:00.000Z",
}

MOCK_WORKSPACE_MEMBER_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "workspace_member_id": "wm_02xyz789ghi012",
    },
    "first_name": "John",
    "last_name": "Smith",
    "email_address": "john.smith@example.com",
    "avatar_url": None,
    "access_level": "member",
    "created_at": "2024-03-15T08:30:00.000Z",
}

MOCK_WORKSPACE_MEMBERS_LIST: dict[str, Any] = {
    "data": [MOCK_WORKSPACE_MEMBER, MOCK_WORKSPACE_MEMBER_2],
}

MOCK_WORKSPACE_MEMBER_SINGLE: dict[str, Any] = {
    "data": MOCK_WORKSPACE_MEMBER,
}

# ---------------------------------------------------------------------------
# Self
# ---------------------------------------------------------------------------

MOCK_SELF_INFO: dict[str, Any] = {
    "active": True,
    "scope": "object_configuration:read record_permission:read",
    "client_id": "client_01abc",
    "token_type": "Bearer",
    "exp": None,
    "iat": 1704067200,
    "sub": "ws_01abc123def456",
    "aud": "https://api.attio.com",
    "iss": "attio.com",
    "authorized_by_workspace_member_id": "wm_01abc123def456",
    "workspace_id": "ws_01abc123def456",
    "workspace_name": "Test Workspace",
    "workspace_slug": "test-workspace",
    "workspace_logo_url": "https://example.com/logo.png",
}

# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

MOCK_VIEW: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "view_id": "view_01abc123def456",
    },
    "title": "All Deals",
    "created_at": "2024-01-20T11:00:00.000Z",
}

MOCK_VIEW_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "view_id": "view_02xyz789ghi012",
    },
    "title": "Active Deals",
    "created_at": "2024-02-15T16:00:00.000Z",
}

MOCK_VIEW_3: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "list_id": "list_01abc123def456",
        "view_id": "view_03list456abc789",
    },
    "title": "Pipeline View",
    "created_at": "2024-03-01T09:00:00.000Z",
}

MOCK_VIEWS_FOR_OBJECT: dict[str, Any] = {
    "data": [MOCK_VIEW, MOCK_VIEW_2],
    "pagination": {"next_cursor": None},
}

MOCK_VIEWS_FOR_OBJECT_PAGE_1: dict[str, Any] = {
    "data": [MOCK_VIEW],
    "pagination": {"next_cursor": "cursor_page2"},
}

MOCK_VIEWS_FOR_OBJECT_PAGE_2: dict[str, Any] = {
    "data": [MOCK_VIEW_2],
    "pagination": {"next_cursor": None},
}

MOCK_VIEWS_FOR_LIST: dict[str, Any] = {
    "data": [MOCK_VIEW_3],
    "pagination": {"next_cursor": None},
}

MOCK_VIEWS_EMPTY: dict[str, Any] = {
    "data": [],
    "pagination": {"next_cursor": None},
}

# ---------------------------------------------------------------------------
# Attributes
# ---------------------------------------------------------------------------

MOCK_ATTRIBUTE: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "attribute_id": "attr_01abc123def456",
    },
    "title": "Deal Value",
    "description": "The monetary value of the deal",
    "api_slug": "deal_value",
    "type": "currency",
    "is_system_attribute": False,
    "is_writable": True,
    "is_required": False,
    "is_unique": False,
    "is_multiselect": False,
    "is_default_value_enabled": False,
    "is_archived": False,
    "default_value": None,
    "relationship": None,
    "created_at": "2024-01-20T10:00:00.000Z",
    "config": {
        "currency": {"default_currency_code": "USD", "display_type": "short"},
        "record_reference": None,
    },
}

MOCK_ATTRIBUTE_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "attribute_id": "attr_02xyz789ghi012",
    },
    "title": "Name",
    "description": None,
    "api_slug": "name",
    "type": "text",
    "is_system_attribute": True,
    "is_writable": True,
    "is_required": True,
    "is_unique": True,
    "is_multiselect": False,
    "is_default_value_enabled": False,
    "is_archived": False,
    "default_value": None,
    "relationship": None,
    "created_at": "2024-01-10T08:00:00.000Z",
    "config": {
        "currency": None,
        "record_reference": None,
    },
}

MOCK_ATTRIBUTES_LIST: dict[str, Any] = {
    "data": [MOCK_ATTRIBUTE, MOCK_ATTRIBUTE_2],
}

MOCK_ATTRIBUTE_SINGLE: dict[str, Any] = {
    "data": MOCK_ATTRIBUTE,
}

MOCK_ATTRIBUTE_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
            "attribute_id": "attr_03new456abc789",
        },
        "title": "Priority",
        "description": "Task priority level",
        "api_slug": "priority",
        "type": "select",
        "is_system_attribute": False,
        "is_writable": True,
        "is_required": True,
        "is_unique": False,
        "is_multiselect": False,
        "is_default_value_enabled": False,
        "is_archived": False,
        "default_value": None,
        "relationship": None,
        "created_at": "2024-06-01T12:00:00.000Z",
        "config": {},
    },
}

MOCK_ATTRIBUTE_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
            "attribute_id": "attr_01abc123def456",
        },
        "title": "Deal Amount",
        "description": "The monetary value of the deal",
        "api_slug": "deal_value",
        "type": "currency",
        "is_system_attribute": False,
        "is_writable": True,
        "is_required": True,
        "is_unique": False,
        "is_multiselect": False,
        "is_default_value_enabled": False,
        "is_archived": False,
        "default_value": None,
        "relationship": None,
        "created_at": "2024-01-20T10:00:00.000Z",
        "config": {
            "currency": {"default_currency_code": "USD", "display_type": "short"},
            "record_reference": None,
        },
    },
}

# ---------------------------------------------------------------------------
# Select Options
# ---------------------------------------------------------------------------

MOCK_SELECT_OPTION: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "attribute_id": "attr_01abc123def456",
        "option_id": "opt_01abc123def456",
    },
    "title": "High",
    "is_archived": False,
}

MOCK_SELECT_OPTION_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "attribute_id": "attr_01abc123def456",
        "option_id": "opt_02xyz789ghi012",
    },
    "title": "Low",
    "is_archived": False,
}

MOCK_SELECT_OPTIONS_LIST: dict[str, Any] = {
    "data": [MOCK_SELECT_OPTION, MOCK_SELECT_OPTION_2],
}

MOCK_SELECT_OPTION_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
            "attribute_id": "attr_01abc123def456",
            "option_id": "opt_03new456abc789",
        },
        "title": "Medium",
        "is_archived": False,
    },
}

MOCK_SELECT_OPTION_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
            "attribute_id": "attr_01abc123def456",
            "option_id": "opt_01abc123def456",
        },
        "title": "Critical",
        "is_archived": False,
    },
}

# ---------------------------------------------------------------------------
# Statuses
# ---------------------------------------------------------------------------

MOCK_STATUS: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "attribute_id": "attr_01abc123def456",
        "status_id": "sta_01abc123def456",
    },
    "title": "Open",
    "is_archived": False,
    "celebration_enabled": False,
    "target_time_in_status": None,
}

MOCK_STATUS_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "object_id": "obj_01abc123def456",
        "attribute_id": "attr_01abc123def456",
        "status_id": "sta_02xyz789ghi012",
    },
    "title": "Won",
    "is_archived": False,
    "celebration_enabled": True,
    "target_time_in_status": None,
}

MOCK_STATUSES_LIST: dict[str, Any] = {
    "data": [MOCK_STATUS, MOCK_STATUS_2],
}

MOCK_STATUS_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
            "attribute_id": "attr_01abc123def456",
            "status_id": "sta_03new456abc789",
        },
        "title": "In Progress",
        "is_archived": False,
        "celebration_enabled": False,
        "target_time_in_status": "P7D",
    },
}

MOCK_STATUS_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "object_id": "obj_01abc123def456",
            "attribute_id": "attr_01abc123def456",
            "status_id": "sta_01abc123def456",
        },
        "title": "Closed",
        "is_archived": False,
        "celebration_enabled": True,
        "target_time_in_status": "P30D",
    },
}

# ---------------------------------------------------------------------------
# Error responses
# ---------------------------------------------------------------------------

MOCK_NOT_FOUND_ERROR: dict[str, Any] = {
    "status_code": 404,
    "type": "invalid_request_error",
    "code": "not_found",
    "message": "The requested resource was not found.",
}

MOCK_PERMISSION_ERROR: dict[str, Any] = {
    "status_code": 403,
    "type": "invalid_request_error",
    "code": "forbidden",
    "message": "Forbidden: missing required API scope.",
}

MOCK_VALIDATION_ERROR: dict[str, Any] = {
    "status_code": 400,
    "type": "invalid_request_error",
    "code": "validation_type",
    "message": "Validation failed: api_slug is required.",
}

MOCK_RATE_LIMIT_ERROR: dict[str, Any] = {
    "status_code": 429,
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please retry after the indicated time.",
}

# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

MOCK_NOTE: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "note_id": "note_01abc123def456",
    },
    "parent_object": "people",
    "parent_record_id": "rec_01abc123def456",
    "title": "Meeting notes",
    "content_plaintext": "Discussed Q3 roadmap.",
    "content_markdown": None,
    "format": "plaintext",
    "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
    "created_at": "2024-03-10T14:00:00.000Z",
}

MOCK_NOTE_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "note_id": "note_02xyz789ghi012",
    },
    "parent_object": "companies",
    "parent_record_id": "rec_02xyz789ghi012",
    "title": "Follow-up summary",
    "content_plaintext": None,
    "content_markdown": "# Follow-up\n\nSent proposal.",
    "format": "markdown",
    "created_by_actor": {"id": "wm_01abc", "type": "workspace-member"},
    "created_at": "2024-03-12T09:30:00.000Z",
}

MOCK_NOTES_LIST: dict[str, Any] = {
    "data": [MOCK_NOTE, MOCK_NOTE_2],
}

MOCK_NOTE_SINGLE: dict[str, Any] = {
    "data": MOCK_NOTE,
}

MOCK_NOTE_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "note_id": "note_03new456abc789",
        },
        "parent_object": "deals",
        "parent_record_id": "rec_03new456abc789",
        "title": "New note",
        "content_plaintext": "Some content here.",
        "content_markdown": None,
        "format": "plaintext",
        "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
        "created_at": "2024-06-01T12:00:00.000Z",
    },
}

MOCK_NOTE_DELETE: dict[str, Any] = {}

# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

MOCK_TASK: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "task_id": "task_01abc123def456",
    },
    "content_plaintext": "Send proposal to Acme Corp",
    "content_markdown": None,
    "format": "plaintext",
    "is_completed": False,
    "completed_at": None,
    "deadline_at": "2024-04-01T17:00:00.000Z",
    "linked_records": [
        {
            "target_object": "companies",
            "target_record_id": "rec_01abc123def456",
        }
    ],
    "assignees": [
        {
            "referenced_actor_type": "workspace-member",
            "referenced_actor_id": "wm_01abc123def456",
        }
    ],
    "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
    "created_at": "2024-03-15T10:00:00.000Z",
}

MOCK_TASK_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "task_id": "task_02xyz789ghi012",
    },
    "content_plaintext": "Review contract",
    "content_markdown": None,
    "format": "plaintext",
    "is_completed": True,
    "completed_at": "2024-03-20T16:00:00.000Z",
    "deadline_at": None,
    "linked_records": [],
    "assignees": [],
    "created_by_actor": {"id": "wm_01abc", "type": "workspace-member"},
    "created_at": "2024-03-18T08:00:00.000Z",
}

MOCK_TASKS_LIST: dict[str, Any] = {
    "data": [MOCK_TASK, MOCK_TASK_2],
}

MOCK_TASK_SINGLE: dict[str, Any] = {
    "data": MOCK_TASK,
}

MOCK_TASK_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "task_id": "task_03new456abc789",
        },
        "content_plaintext": "Draft agenda",
        "content_markdown": None,
        "format": "plaintext",
        "is_completed": False,
        "completed_at": None,
        "deadline_at": "2024-07-01T09:00:00.000Z",
        "linked_records": [
            {
                "target_object": "deals",
                "target_record_id": "rec_03new456abc789",
            }
        ],
        "assignees": [
            {
                "referenced_actor_type": "workspace-member",
                "referenced_actor_id": "wm_02xyz789ghi012",
            }
        ],
        "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
        "created_at": "2024-06-01T12:00:00.000Z",
    },
}

MOCK_TASK_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "task_id": "task_01abc123def456",
        },
        "content_plaintext": "Send proposal to Acme Corp (updated)",
        "content_markdown": None,
        "format": "plaintext",
        "is_completed": True,
        "completed_at": "2024-04-01T15:00:00.000Z",
        "deadline_at": "2024-04-01T17:00:00.000Z",
        "linked_records": [
            {
                "target_object": "companies",
                "target_record_id": "rec_01abc123def456",
            }
        ],
        "assignees": [
            {
                "referenced_actor_type": "workspace-member",
                "referenced_actor_id": "wm_01abc123def456",
            }
        ],
        "created_by_actor": {"id": "actor_01abc", "type": "api-token"},
        "created_at": "2024-03-15T10:00:00.000Z",
    },
}

MOCK_TASK_DELETE: dict[str, Any] = {}

# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------

MOCK_WEBHOOK: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "webhook_id": "wh_01abc123def456",
    },
    "target_url": "https://example.com/webhooks/attio",
    "subscriptions": [
        {"event_type": "record.created", "filter": None},
        {"event_type": "record.updated", "filter": {"$object": "people"}},
    ],
    "status": "active",
    "secret": None,
    "created_at": "2024-02-20T10:00:00.000Z",
}

MOCK_WEBHOOK_2: dict[str, Any] = {
    "id": {
        "workspace_id": "ws_01abc123def456",
        "webhook_id": "wh_02xyz789ghi012",
    },
    "target_url": "https://example.com/webhooks/attio-tasks",
    "subscriptions": [
        {"event_type": "task.created", "filter": None},
    ],
    "status": "paused",
    "secret": None,
    "created_at": "2024-03-05T15:00:00.000Z",
}

MOCK_WEBHOOKS_LIST: dict[str, Any] = {
    "data": [MOCK_WEBHOOK, MOCK_WEBHOOK_2],
}

MOCK_WEBHOOK_SINGLE: dict[str, Any] = {
    "data": MOCK_WEBHOOK,
}

MOCK_WEBHOOK_CREATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "webhook_id": "wh_03new456abc789",
        },
        "target_url": "https://example.com/webhooks/new",
        "subscriptions": [
            {"event_type": "note.created", "filter": None},
        ],
        "status": "active",
        "secret": "whsec_test_secret_12345",
        "created_at": "2024-06-01T12:00:00.000Z",
    },
}

MOCK_WEBHOOK_UPDATED: dict[str, Any] = {
    "data": {
        "id": {
            "workspace_id": "ws_01abc123def456",
            "webhook_id": "wh_01abc123def456",
        },
        "target_url": "https://example.com/webhooks/updated",
        "subscriptions": [
            {"event_type": "record.created", "filter": None},
            {"event_type": "record.deleted", "filter": None},
        ],
        "status": "active",
        "secret": None,
        "created_at": "2024-02-20T10:00:00.000Z",
    },
}

MOCK_WEBHOOK_DELETE: dict[str, Any] = {}
