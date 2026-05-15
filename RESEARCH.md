# Attio Python SDK -- Research & Architecture Plan

> Generated 2026-05-15. This document serves as the blueprint for building the `attio` Python SDK.

---

## Table of Contents

1. [Complete API Map](#1-complete-api-map)
2. [SDK Architecture Proposal](#2-sdk-architecture-proposal)
3. [Testing Strategy](#3-testing-strategy)
4. [Dependency Recommendations](#4-dependency-recommendations)
5. [Comparison with attio-node](#5-comparison-with-attio-node)

---

## 1. Complete API Map

### 1.1 API Fundamentals

| Property | Value |
|---|---|
| Base URL | `https://api.attio.com/v2` |
| Protocol | REST over HTTPS, JSON request/response bodies |
| Authentication | Bearer token (`Authorization: Bearer <token>`) -- supports both API keys and OAuth 2.0 access tokens |
| Rate Limits (reads) | 100 requests/second |
| Rate Limits (writes) | 25 requests/second |
| Rate Limit Response | HTTP 429 with `Retry-After` header (date when limit resets, usually next second) |
| Score-Based Limits | List records/entries queries have complexity scoring with a 10-second sliding window |
| Pagination (type A) | Limit/offset -- `limit` + `offset` query params; default varies by endpoint |
| Pagination (type B) | Cursor-based -- `limit` + `cursor` query params; response has `pagination.next_cursor` |
| OpenAPI Spec URLs | `https://api.attio.com/openapi/api`, `https://api.attio.com/openapi/standard-objects`, `https://api.attio.com/openapi/webhooks` |

### 1.2 Authentication Details

- **API Key**: Generated in Attio Settings -> Developers -> API Keys. Scopes set at generation time, modifiable afterward.
- **OAuth 2.0**: Authorization code grant flow. Endpoints: authorize, token exchange, introspect.
- **Header**: `Authorization: Bearer <access_token>`
- **Alternative**: HTTP Basic Auth (username=token, password blank) -- not recommended.
- **Scopes**: Space-separated. Each endpoint documents required scopes. Both API key and OAuth tokens use the same scope system.

### 1.3 Error Response Format

All errors return JSON:
```json
{
  "status_code": 400,
  "type": "invalid_request_error",
  "code": "validation_type",
  "message": "Human-readable error description"
}
```

Known error codes: `validation_type`, `not_found`, `slug_conflict`, `quota_exceeded`, `rate_limit_exceeded`.

Known error types: `invalid_request_error`, `rate_limit_error`.

### 1.4 Response Envelope Patterns

| Pattern | Shape | Used By |
|---|---|---|
| Single item | `{ "data": T }` | get, create, update, upsert |
| List (offset) | `{ "data": T[] }` | list records, list entries, query, search, list objects, etc. |
| List (cursor) | `{ "data": T[], "pagination": { "next_cursor": string \| null } }` | list views, list files, list meetings, list call recordings, transcripts |
| Void | Empty body or `{}` | delete operations |

### 1.5 Attribute Types (Complete)

| Type | Value Fields | Writable via API |
|---|---|---|
| `text` | `value: string` | Yes |
| `number` | `value: number` | Yes |
| `checkbox` | `value: boolean` | Yes |
| `currency` | `currency_value: number`, `currency_code: string` | Yes |
| `date` | `value: string` (ISO 8601 date) | Yes |
| `timestamp` | `value: string` (ISO 8601 datetime) | Yes |
| `rating` | `value: number` | Yes |
| `status` | `status: { title: string }` or `{ status_id: string }` | Yes |
| `select` | `option: { title: string }` or `{ option_id: string }` | Yes |
| `record-reference` | `target_object: string`, `target_record_id: string` | Yes |
| `actor-reference` | `referenced_actor_type: string`, `referenced_actor_id: string` | Read-only (system) |
| `location` | `line_1`, `line_2`, `line_3`, `line_4`, `locality`, `region`, `postcode`, `country_code`, `latitude`, `longitude` | Yes |
| `domain` | `domain: string` | Yes |
| `email-address` | `email_address: string` | Yes (on records, not as custom attribute type) |
| `phone-number` | `original_phone_number: string`, `country_code: string` | Yes |
| `interaction` | `interaction_type: string`, `interacted_at: string` | Read-only (system) |
| `personal-name` | `first_name: string`, `last_name: string`, `full_name: string` | Yes |

### 1.6 Complete Endpoint Reference

#### 1.6.1 Objects

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/objects` | `objects.list()` | List all objects | `object_configuration:read` |
| GET | `/v2/objects/{object}` | `objects.get(slug)` | Get single object | `object_configuration:read` |
| POST | `/v2/objects` | `objects.create(data)` | Create custom object | `object_configuration:read-write` |
| PUT | `/v2/objects/{object}` | `objects.update(slug, data)` | Update object | `object_configuration:read-write` |

**Object response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid"
    },
    "api_slug": "string | None",
    "singular_noun": "string | None",
    "plural_noun": "string | None",
    "created_at": "ISO 8601 timestamp"
}
```

#### 1.6.2 Attributes

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/{target}/{id}/attributes` | `attributes.list(target, id)` | List attributes on object/list | `object_configuration:read` or `list_configuration:read` |
| GET | `/v2/{target}/{id}/attributes/{attr}` | `attributes.get(target, id, attr)` | Get single attribute | same |
| POST | `/v2/{target}/{id}/attributes` | `attributes.create(target, id, data)` | Create attribute | `*_configuration:read-write` |
| PATCH | `/v2/{target}/{id}/attributes/{attr}` | `attributes.update(target, id, attr, data)` | Update attribute | `*_configuration:read-write` |

**Query params for list:** `limit`, `offset`, `show_archived`

**Attribute response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid",
        "attribute_id": "uuid"
    },
    "title": "string",
    "description": "string | None",
    "api_slug": "string",
    "type": "text | number | checkbox | ...",  # see attribute types above
    "is_system_attribute": "bool",
    "is_writable": "bool",
    "is_required": "bool",
    "is_unique": "bool",
    "is_multiselect": "bool",
    "is_default_value_enabled": "bool",
    "is_archived": "bool",
    "default_value": "dict | None",
    "relationship": "dict | None",
    "created_at": "ISO 8601 timestamp",
    "config": {
        "currency": {"default_currency_code": "str | None", "display_type": "str | None"},
        "record_reference": {"allowed_object_ids": "list | None"}
    }
}
```

**Create attribute request body:**
```python
{
    "data": {
        "title": "string",           # required
        "description": "string|null", # required
        "api_slug": "string",         # required
        "type": "string",             # required -- see attribute types
        "is_required": "bool",        # required
        "is_unique": "bool",          # required
        "is_multiselect": "bool",     # required
        "default_value": "dict|null", # optional
        "relationship": "dict|null",  # optional
        "config": "dict"              # required
    }
}
```

#### 1.6.3 Select Options

| Method | Path | SDK Method | Description |
|---|---|---|---|
| GET | `/v2/{target}/{id}/attributes/{attr}/options` | `select_options.list(target, id, attr)` | List select options |
| POST | `/v2/{target}/{id}/attributes/{attr}/options` | `select_options.create(target, id, attr, data)` | Create select option |
| PATCH | `/v2/{target}/{id}/attributes/{attr}/options/{option_id}` | `select_options.update(target, id, attr, option_id, data)` | Update select option |

**Query params for list:** `show_archived`

**Select option response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid",
        "attribute_id": "uuid",
        "option_id": "uuid"
    },
    "title": "string",
    "is_archived": "bool"
}
```

#### 1.6.4 Statuses

| Method | Path | SDK Method | Description |
|---|---|---|---|
| GET | `/v2/{target}/{id}/attributes/{attr}/statuses` | `statuses.list(target, id, attr)` | List statuses |
| POST | `/v2/{target}/{id}/attributes/{attr}/statuses` | `statuses.create(target, id, attr, data)` | Create status |
| PATCH | `/v2/{target}/{id}/attributes/{attr}/statuses/{status_id}` | `statuses.update(target, id, attr, status_id, data)` | Update status |

**Query params for list:** `show_archived`

**Status response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid",
        "attribute_id": "uuid",
        "status_id": "uuid"
    },
    "title": "string",
    "is_archived": "bool",
    "celebration_enabled": "bool",
    "target_time_in_status": "string | None"  # ISO 8601 duration
}
```

#### 1.6.5 Records (Generic)

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/objects/{object}/records` | `records.list(object, *, limit, offset)` | List records | `record_permission:read`, `object_configuration:read` |
| POST | `/v2/objects/{object}/records/query` | `records.query(object, *, filter, sorts, limit, offset)` | Query with filters | same |
| POST | `/v2/objects/{object}/records` | `records.create(object, data)` | Create record | `record_permission:read-write`, `object_configuration:read` |
| GET | `/v2/objects/{object}/records/{record_id}` | `records.get(object, record_id)` | Get single record | `record_permission:read`, `object_configuration:read` |
| PUT | `/v2/objects/{object}/records/{record_id}` | `records.update(object, record_id, data)` | Update (overwrite multiselect) | `record_permission:read-write`, `object_configuration:read` |
| PATCH | `/v2/objects/{object}/records/{record_id}` | `records.append(object, record_id, data)` | Update (append multiselect) | same |
| DELETE | `/v2/objects/{object}/records/{record_id}` | `records.delete(object, record_id)` | Delete record | same |
| PUT | `/v2/objects/{object}/records` | `records.upsert(object, data)` | Upsert by matching attribute | same |
| GET | `/v2/objects/{object}/records/{record_id}/attributes/{attribute}/values` | `records.get_attribute_values(object, record_id, attribute)` | Get attribute values | `record_permission:read`, `object_configuration:read` |
| GET | `/v2/objects/{object}/records/{record_id}/entries` | `records.list_entries(object, record_id)` | List entries for record | `record_permission:read`, `object_configuration:read`, `list_entry:read` |
| POST | `/v2/objects/records/search` | `records.global_search(query, objects, ...)` | Global record search | `record_permission:read`, `object_configuration:read` |

**Record response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid",
        "record_id": "uuid"
    },
    "created_at": "ISO 8601 timestamp",
    "web_url": "https://app.attio.com/...",
    "values": {
        "<attribute_slug>": [
            {
                "active_from": "ISO 8601 timestamp",
                "active_until": "ISO 8601 timestamp | None",
                "created_by_actor": {
                    "id": "string | None",
                    "type": "api-token | workspace-member | system | app"
                },
                "attribute_type": "text | number | ...",
                # ... type-specific fields (see attribute types)
            }
        ]
    }
}
```

**Create/Update record request body:**
```python
{
    "data": {
        "values": {
            "<attribute_slug_or_id>": "<value_or_array>"
        }
    }
}
```

**Upsert record request body:**
```python
{
    "data": {
        "matching_attribute": "email_addresses",
        "values": { ... }
    }
}
```

**Query request body:**
```python
{
    "filter": {"name": {"$contains": "test"}},  # or shorthand: {"name": "test"}
    "sorts": [{"attribute": "created_at", "direction": "desc"}],
    "limit": 500,  # default 500
    "offset": 0    # default 0
}
```

**Global search request body:**
```python
{
    "query": "Jane",              # max 256 chars
    "objects": ["people"],        # min 1 item, slugs or UUIDs
    "request_as": { ... },        # workspace-wide or member-specific
    "limit": 25                   # 1-25, default 25
}
```

**Global search result shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid",
        "record_id": "uuid"
    },
    "record_text": "Jane Doe",
    "record_image": "url | None",
    "object_slug": "people",
    # additional type-specific fields (email_addresses, domains, etc.)
}
```

**Record attribute values query params:** `show_historic`, `limit`, `offset`

**Record entries query params:** `limit` (default 100, max 1000), `offset` (default 0)

**Record entries response shape (different from list entries):**
```python
{
    "list_id": "uuid",
    "list_api_slug": "string",
    "entry_id": "uuid",
    "created_at": "ISO 8601 timestamp"
}
```

#### 1.6.6 Standard Object Convenience Endpoints (People, Companies, Deals, Users, Workspaces)

These are type-safe wrappers around the generic record endpoints with object-specific paths. They share the same request/response shapes as generic records but use fixed paths:

**People** (`/v2/objects/people/records/...`):

| Method | Path | SDK Method |
|---|---|---|
| GET | `/v2/objects/people/records` | `people.list(...)` |
| POST | `/v2/objects/people/records/query` | `people.query(...)` |
| POST | `/v2/objects/people/records` | `people.create(...)` |
| GET | `/v2/objects/people/records/{record_id}` | `people.get(...)` |
| PUT | `/v2/objects/people/records/{record_id}` | `people.update(...)` |
| PATCH | `/v2/objects/people/records/{record_id}` | `people.append(...)` |
| DELETE | `/v2/objects/people/records/{record_id}` | `people.delete(...)` |
| PUT | `/v2/objects/people/records` | `people.upsert(...)` |
| GET | `/v2/objects/people/records/{record_id}/attributes/{attribute}/values` | `people.get_attribute_values(...)` |
| GET | `/v2/objects/people/records/{record_id}/entries` | `people.list_entries(...)` |

**Companies** (`/v2/objects/companies/records/...`): Same pattern as People.

**Deals** (`/v2/objects/deals/records/...`): Same pattern as People.

**Users** (`/v2/objects/users/records/...`): Same pattern as People.

**Workspaces** (`/v2/objects/workspaces/records/...`): Same pattern as People.

> **Note for SDK design**: These standard object endpoints are functionally identical to calling `records.*` with the specific object slug. In the Python SDK, we can provide convenience sub-clients that delegate to the records resource with a fixed slug, rather than duplicating logic. This gives users type-safe access like `client.people.create(...)` while keeping implementation DRY.

**Known standard object attributes:**

People: `email_addresses`, `name` (personal-name), `description`, `job_title`, `phone_numbers`, `primary_location`, `linkedin`, `twitter`, `facebook`, `instagram`, `angellist`, `twitter_follower_count`, `company` (record-reference), `avatar_url` (read-only)

Companies: `domains`, `name`, `description`, `primary_location`, `twitter`, `linkedin`, `facebook`, `instagram`, `angellist`, `categories`, `estimated_arr_usd`, `employee_range`, `foundation_date`, `twitter_follower_count`, `team` (record-reference to people)

Deals: `name`, `stage` (status), `owner`, `value`, associated people/company references

Users: `person` (record-reference), `primary_email_address`, `user_id`, `workspace` (record-reference), `avatar_url` (read-only)

Workspaces: `workspace_id`, `name`, `users` (record-reference), `company` (record-reference), `avatar_url`

#### 1.6.7 Lists

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/lists` | `lists.list()` | List all lists | `list_configuration:read` |
| GET | `/v2/lists/{list}` | `lists.get(list)` | Get single list | `list_configuration:read` |
| POST | `/v2/lists` | `lists.create(data)` | Create list | `list_configuration:read-write` |
| PATCH | `/v2/lists/{list}` | `lists.update(list, data)` | Update list | `list_configuration:read-write` |

**List response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "list_id": "uuid"
    },
    "api_slug": "string",
    "name": "string",
    "parent_object": ["string"],  # array of object slugs
    "workspace_access": "full-access | read-and-write | read-only | None",
    "workspace_member_access": [
        {"workspace_member_id": "uuid", "level": "full-access | read-and-write | read-only"}
    ],
    "created_by_actor": {"id": "string | None", "type": "api-token | workspace-member | system | app"},
    "created_at": "ISO 8601 timestamp"
}
```

**Create list request body:**
```python
{
    "data": {
        "name": "string",                   # required
        "api_slug": "string",               # required
        "parent_object": "string",           # required -- UUID or slug
        "workspace_access": "string | None", # required
        "workspace_member_access": [...]     # optional
    }
}
```

#### 1.6.8 Entries (List Entries)

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/lists/{list}/entries` | `entries.list(list, *, limit, offset)` | List entries | `list_entry:read`, `list_configuration:read` |
| POST | `/v2/lists/{list}/entries/query` | `entries.query(list, *, filter, sorts, limit, offset)` | Query with filters | same |
| GET | `/v2/lists/{list}/entries/{entry_id}` | `entries.get(list, entry_id)` | Get single entry | same |
| POST | `/v2/lists/{list}/entries` | `entries.create(list, data)` | Create entry | `list_entry:read-write`, `list_configuration:read` |
| PUT | `/v2/lists/{list}/entries/{entry_id}` | `entries.update(list, entry_id, data)` | Update (overwrite) | same |
| PATCH | `/v2/lists/{list}/entries/{entry_id}` | `entries.append(list, entry_id, data)` | Update (append) | same |
| DELETE | `/v2/lists/{list}/entries/{entry_id}` | `entries.delete(list, entry_id)` | Delete entry | same |
| PUT | `/v2/lists/{list}/entries` | `entries.upsert(list, data)` | Upsert by parent | same |
| GET | `/v2/lists/{list}/entries/{entry_id}/attributes/{attribute}/values` | `entries.get_attribute_values(list, entry_id, attribute)` | Get attribute values | `list_entry:read`, `list_configuration:read` |

**Entry response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "list_id": "uuid",
        "entry_id": "uuid"
    },
    "parent_record_id": "uuid",
    "parent_object": "string",
    "created_at": "ISO 8601 timestamp",
    "entry_values": {
        "<attribute_slug>": [
            {
                "active_from": "...",
                "active_until": "...",
                "created_by_actor": { ... },
                "attribute_type": "...",
                # type-specific fields
            }
        ]
    }
}
```

**Create entry request body:**
```python
{
    "data": {
        "parent_record_id": "uuid",     # required
        "parent_object": "string",       # required (UUID or slug)
        "entry_values": { ... }          # required
    }
}
```

**Entry attribute values query params:** `show_historic`, `limit`, `offset`

#### 1.6.9 Notes

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/notes` | `notes.list(*, parent_object, parent_record_id)` | List notes | `note:read`, `object_configuration:read`, `record_permission:read` |
| GET | `/v2/notes/{note_id}` | `notes.get(note_id)` | Get single note | same |
| POST | `/v2/notes` | `notes.create(data)` | Create note | `note:read-write`, `object_configuration:read`, `record_permission:read` |
| DELETE | `/v2/notes/{note_id}` | `notes.delete(note_id)` | Delete note | `note:read-write` |

**List query params:** `parent_object`, `parent_record_id`

**Note response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "note_id": "uuid"
    },
    "parent_object": "string",
    "parent_record_id": "uuid",
    "title": "string",
    "meeting_id": "uuid | None",
    "content_plaintext": "string",
    "content_markdown": "string",
    "tags": [
        {
            "type": "workspace-member | record",
            "workspace_member_id": "uuid",  # if type=workspace-member
            "object": "string",              # if type=record
            "record_id": "uuid"              # if type=record
        }
    ],
    "created_by_actor": {"id": "string | None", "type": "..."},
    "created_at": "ISO 8601 timestamp"
}
```

**Create note request body:**
```python
{
    "data": {
        "parent_object": "string",       # required
        "parent_record_id": "uuid",      # required
        "title": "string",               # required
        "format": "plaintext | markdown", # required
        "content": "string",             # required
        "created_at": "string",          # optional, ISO 8601
        "meeting_id": "uuid | None"      # optional
    }
}
```

#### 1.6.10 Tasks

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/tasks` | `tasks.list(*, linked_object, linked_record_id, is_completed, assignee)` | List tasks | `task:read`, `object_configuration:read`, `record_permission:read`, `user_management:read` |
| GET | `/v2/tasks/{task_id}` | `tasks.get(task_id)` | Get single task | same |
| POST | `/v2/tasks` | `tasks.create(data)` | Create task | `task:read-write`, ... |
| PUT | `/v2/tasks/{task_id}` | `tasks.update(task_id, data)` | Update task | same |
| DELETE | `/v2/tasks/{task_id}` | `tasks.delete(task_id)` | Delete task | same |

**List query params:** `linked_object`, `linked_record_id`, `is_completed`, `assignee`

**Task response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "task_id": "uuid"
    },
    "content_plaintext": "string",
    "deadline_at": "ISO 8601 | None",
    "is_completed": "bool",
    "completed_at": "ISO 8601 | None",
    "linked_records": [
        {"target_object_id": "string", "target_record_id": "uuid"}
    ],
    "assignees": [
        {"referenced_actor_type": "string", "referenced_actor_id": "uuid"}
    ],
    "created_by_actor": {"id": "string | None", "type": "..."},
    "created_at": "ISO 8601 timestamp"
}
```

**Create task request body:**
```python
{
    "data": {
        "content": "string",             # required, max 2000 chars
        "format": "plaintext",           # required
        "deadline_at": "ISO 8601 | None",# optional
        "is_completed": "bool",          # optional
        "linked_records": [...],         # optional -- record refs or matching attrs
        "assignees": [...]               # optional -- workspace member refs or emails
    }
}
```

#### 1.6.11 Webhooks

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/webhooks` | `webhooks.list()` | List webhooks | `webhook:read` |
| GET | `/v2/webhooks/{webhook_id}` | `webhooks.get(webhook_id)` | Get single webhook | `webhook:read` |
| POST | `/v2/webhooks` | `webhooks.create(data)` | Create webhook | `webhook:read-write` |
| PUT | `/v2/webhooks/{webhook_id}` | `webhooks.update(webhook_id, data)` | Update webhook | `webhook:read-write` |
| DELETE | `/v2/webhooks/{webhook_id}` | `webhooks.delete(webhook_id)` | Delete webhook | `webhook:read-write` |

**Webhook response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "webhook_id": "uuid"
    },
    "target_url": "https://...",
    "subscriptions": [
        {"event_type": "record.created", "filter": "dict | None"}
    ],
    "status": "active | degraded | inactive",
    "secret": "string",  # only returned on create
    "created_at": "ISO 8601 timestamp"
}
```

**All webhook event types:**
```
record.created, record.updated, record.deleted, record.merged,
list-entry.created, list-entry.updated, list-entry.deleted,
list.created, list.updated, list.deleted,
task.created, task.updated, task.deleted,
note.created, note.updated, note.deleted, note-content.updated,
comment.created, comment.deleted, comment.resolved, comment.unresolved,
object-attribute.created, object-attribute.updated,
list-attribute.created, list-attribute.updated,
workspace-member.created,
call-recording.created
```

**Webhook signature verification:**
- Header: `Attio-Signature` (also `X-Attio-Signature` for legacy)
- Algorithm: HMAC-SHA256 of raw request body using webhook secret
- Encoding: Hexadecimal
- Retry behavior: Up to 10 retries with exponential backoff over ~3 days
- Timeout: 5 seconds
- Deduplication: `Idempotency-Key` header

#### 1.6.12 Workspace Members

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/workspace_members` | `workspace_members.list()` | List all members | `user_management:read` |
| GET | `/v2/workspace_members/{member_id}` | `workspace_members.get(member_id)` | Get single member | `user_management:read` |

**Workspace member response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "workspace_member_id": "uuid"
    },
    "first_name": "string",
    "last_name": "string",
    "email_address": "string",
    "avatar_url": "string | None",
    "access_level": "string",
    "created_at": "ISO 8601 timestamp"
}
```

#### 1.6.13 Views

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/objects/{object}/views` | `views.list_for_object(object, *, show_archived, limit, cursor)` | List views for object | `object_configuration:read` |
| GET | `/v2/lists/{list}/views` | `views.list_for_list(list, *, show_archived, limit, cursor)` | List views for list | `list_configuration:read` |

**Pagination:** Cursor-based

**Query params:** `show_archived` (bool), `limit` (1-1000, default 500), `cursor` (string)

**View response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "object_id": "uuid",  # or list_id for list views
        "view_id": "uuid"
    },
    "title": "string",
    "created_at": "ISO 8601 timestamp"
}
```

#### 1.6.14 Comments

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| POST | `/v2/comments` | `comments.create(data)` | Create comment (on thread, record, or entry) | `comment:read-write`, plus context scopes |
| GET | `/v2/comments/{comment_id}` | `comments.get(comment_id)` | Get single comment | `comment:read` |
| DELETE | `/v2/comments/{comment_id}` | `comments.delete(comment_id)` | Delete comment | `comment:read-write` |

**Comment response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "comment_id": "uuid"
    },
    "thread_id": "uuid",
    "content_plaintext": "string",
    "entry": {"entry_id": "uuid", "list_id": "uuid"} | None,
    "record": {"record_id": "uuid", "object_id": "uuid"},
    "resolved_at": "ISO 8601 | None",
    "resolved_by": {"type": "string", "id": "string"} | None,
    "created_at": "ISO 8601 timestamp",
    "author": {"type": "workspace-member", "id": "uuid"}
}
```

**Create comment -- three variants (mutually exclusive):**

On thread:
```python
{"data": {"thread_id": "uuid", "format": "plaintext", "content": "...", "author": {"type": "workspace-member", "id": "uuid"}, "created_at": "..."}}
```

On record:
```python
{"data": {"record": {"object": "slug", "record_id": "uuid"}, "format": "plaintext", "content": "...", "author": {"type": "workspace-member", "id": "uuid"}}}
```

On entry:
```python
{"data": {"entry": {"list": "slug", "entry_id": "uuid"}, "format": "plaintext", "content": "...", "author": {"type": "workspace-member", "id": "uuid"}}}
```

#### 1.6.15 Threads

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/threads` | `threads.list(*, record_id, object, entry_id, list, limit, offset)` | List threads | `comment:read`, plus context scopes |
| GET | `/v2/threads/{thread_id}` | `threads.get(thread_id)` | Get single thread | `comment:read` |

**Query params:** `record_id`, `object` (required with record_id), `entry_id`, `list` (required with entry_id), `limit` (default 10, max 50), `offset` (default 0)

**Thread response shape:**
```python
{
    "id": {
        "workspace_id": "uuid",
        "thread_id": "uuid"
    },
    "comments": [<Comment>],  # nested comment objects
    "created_at": "ISO 8601 timestamp"
}
```

#### 1.6.16 Files

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/files` | `files.list(*, object, record_id, storage_provider, parent_folder_id, limit, cursor)` | List files | `file:read`, `object_configuration:read`, `record_permission:read` |
| GET | `/v2/files/{file_id}` | `files.get(file_id)` | Get single file | same |
| POST | `/v2/files` | `files.create_folder(data)` | Create folder | `file:read-write`, ... |
| POST | `/v2/files/upload` | `files.upload(file, object, record_id, ...)` | Upload file (multipart/form-data) | `file:read-write`, ... |
| GET | `/v2/files/{file_id}/download` | `files.download(file_id)` | Get download URL | same |
| DELETE | `/v2/files/{file_id}` | `files.delete(file_id)` | Delete file/folder | `file:read-write`, ... |

**Pagination:** Cursor-based. `limit` (1-200, default 50), `cursor`.

**Query params for list:** `object` (required), `record_id` (required), `storage_provider`, `parent_folder_id`, `limit`, `cursor`

**File response shape (discriminated union by `file_type`):**
```python
# file_type = "file"
{
    "id": {"workspace_id": "uuid", "file_id": "uuid"},
    "object_id": "uuid",
    "object_slug": "string",
    "record_id": "uuid",
    "storage_provider": "attio | dropbox | box | google-drive | microsoft-onedrive",
    "created_by_actor": {"id": "string | None", "type": "..."},
    "created_at": "ISO 8601",
    "file_type": "file",
    "name": "string",
    "content_type": "string | None",
    "content_size": "int | None",
    "parent_folder_id": "uuid | None"
}

# file_type = "folder"
# Same but without content_type and content_size

# file_type = "connected-file"
# Includes external_provider_file_id, microsoft_drive_id

# file_type = "connected-folder"
# Similar to connected-file
```

**Upload file:**
- Content-Type: `multipart/form-data`
- Max size: 50 MB
- Fields: `file` (binary), `object` (string), `record_id` (uuid), `parent_folder_id` (optional)
- Response: 201 Created

#### 1.6.17 Meetings

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/meetings` | `meetings.list(*, limit, cursor, linked_object, linked_record_id, participants, sort, ends_from, starts_before, timezone)` | List meetings | `meeting:read`, `record_permission:read` |
| GET | `/v2/meetings/{meeting_id}` | `meetings.get(meeting_id)` | Get single meeting | same |

**Pagination:** Cursor-based. `limit` (1-200, default 50), `cursor`.

**Query params:** `linked_object`, `linked_record_id`, `participants` (comma-separated emails), `sort` (start_asc|start_desc), `ends_from`, `starts_before`, `timezone` (default UTC)

**Meeting response shape:**
```python
{
    "id": {"workspace_id": "uuid", "meeting_id": "uuid"},
    "title": "string",
    "description": "string",
    "is_all_day": "bool",
    "start": {"datetime": "ISO 8601", "date": "YYYY-MM-DD", "timezone": "string"},
    "end": {"datetime": "ISO 8601", "date": "YYYY-MM-DD", "timezone": "string"},
    "participants": [
        {"status": "string", "is_organizer": "bool", "email_address": "string"}
    ],
    "linked_records": [
        {"object_slug": "string", "object_id": "uuid", "record_id": "uuid"}
    ],
    "created_at": "ISO 8601",
    "created_by_actor": {"id": "string", "type": "string"}
}
```

#### 1.6.18 Call Recordings

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/meetings/{meeting_id}/call_recordings` | `call_recordings.list(meeting_id, *, limit, cursor)` | List call recordings | `meeting:read` |
| GET | `/v2/meetings/{meeting_id}/call_recordings/{recording_id}` | `call_recordings.get(meeting_id, recording_id)` | Get single recording | same |

**Pagination:** Cursor-based.

**Call recording response shape:**
```python
{
    "id": {"workspace_id": "uuid", "call_recording_id": "uuid"},
    "status": "string",
    "web_url": "string | None",
    "actor": {"type": "string", "id": "string"} | None,
    "created_at": "ISO 8601"
}
```

#### 1.6.19 Transcripts

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/meetings/{meeting_id}/call_recordings/{recording_id}/transcript` | `transcripts.get(meeting_id, recording_id, *, limit, cursor)` | Get transcript | `meeting:read` |

**Pagination:** Cursor-based.

**Transcript response shape:**
```python
{
    "data": [
        {
            "speech": "string",
            "start_time": "float",
            "end_time": "float",
            "speaker": {
                "name": "string | None",
                "email_address": "string | None"
            } | None
        }
    ],
    "pagination": {"next_cursor": "string | None"}
}
```

#### 1.6.20 Self / Identify (Meta)

| Method | Path | SDK Method | Description | Scopes |
|---|---|---|---|---|
| GET | `/v2/self` | `self.identify()` | Get token/workspace info | None required |

**Response shape (active token):**
```python
{
    "active": True,
    "scope": "space-separated scopes string",
    "client_id": "string",
    "token_type": "Bearer",
    "exp": "int | None",  # unix timestamp
    "iat": "int",          # unix timestamp
    "sub": "uuid",         # workspace_id
    "aud": "string",
    "iss": "attio.com",
    "authorized_by_workspace_member_id": "uuid",
    "workspace_id": "uuid",
    "workspace_name": "string",
    "workspace_slug": "string",
    "workspace_logo_url": "string | None"
}
```

### 1.7 Filtering & Sorting Reference

**Filter operators:**
- `$eq` -- equality (all types)
- `$contains` -- case-insensitive substring (strings, domains, emails, names, phones)
- `$starts_with` -- prefix match (same types as $contains)
- `$ends_with` -- suffix match (same types as $contains)
- `$lt`, `$lte`, `$gt`, `$gte` -- comparison (numbers, dates, currency, ratings)
- `$in` -- set membership (record references, text)
- `$not_empty` -- existence check (select types)

**Logical operators:** `$and`, `$or`, `$not`

**Shorthand:** `{"name": "John"}` is equivalent to `{"name": {"full_name": {"$eq": "John"}}}`

**Path filtering:** For record references, use `path` arrays to traverse relationships.

**Sort format:**
```python
{
    "direction": "asc | desc",
    "attribute": "slug_or_id",
    "field": "sub_field"  # optional, e.g. "last_name" for personal-name
}
```

---

## 2. SDK Architecture Proposal

### 2.1 Monorepo Structure

```
attio-python/
  pyproject.toml              # Workspace root (hatch / uv workspaces)
  RESEARCH.md                 # This file
  CLAUDE.md                   # Instructions for Claude
  packages/
    sdk/
      pyproject.toml           # Published as "attio" on PyPI
      src/
        attio/
          __init__.py           # AttioClient, async_client
          _client.py            # Sync + Async client classes
          _http.py              # Low-level HTTP transport (httpx wrapper)
          _config.py            # Configuration, defaults, constants
          _exceptions.py        # Error hierarchy
          _types.py             # Shared type aliases, enums
          _pagination.py        # Pagination helpers / iterators
          _compat.py            # Python version compat helpers
          models/
            __init__.py
            _base.py            # Base model config
            objects.py
            attributes.py
            records.py
            lists.py
            entries.py
            notes.py
            tasks.py
            webhooks.py
            workspace_members.py
            comments.py
            threads.py
            files.py
            meetings.py
            call_recordings.py
            transcripts.py
            self_info.py
            select_options.py
            common.py           # ActorReference, AttributeValue, etc.
          resources/
            __init__.py
            _base.py            # BaseResource with http reference
            objects.py
            attributes.py
            records.py
            lists.py
            entries.py
            notes.py
            tasks.py
            webhooks.py
            workspace_members.py
            select_options.py
            statuses.py
            views.py
            comments.py
            threads.py
            files.py
            meetings.py
            call_recordings.py
            transcripts.py
            self_resource.py
            # Standard object convenience resources
            people.py
            companies.py
            deals.py
            users.py
            workspaces.py
          webhook_utils.py      # Signature verification
          py.typed              # PEP 561 marker
      tests/
        __init__.py
        conftest.py             # Shared fixtures, respx setup
        fixtures/               # Recorded/static response fixtures
          objects.py
          records.py
          ...
        test_client.py
        test_exceptions.py
        test_pagination.py
        test_webhook_utils.py
        resources/
          test_objects.py
          test_records.py
          test_lists.py
          test_entries.py
          test_notes.py
          test_tasks.py
          test_webhooks.py
          test_workspace_members.py
          test_select_options.py
          test_views.py
          test_comments.py
          test_threads.py
          test_files.py
          test_meetings.py
          test_call_recordings.py
          test_transcripts.py
          test_self.py
          test_people.py
          test_companies.py
    cli/
      pyproject.toml           # Published as "attio-cli" on PyPI (future)
      src/
        attio_cli/
          __init__.py
          main.py
```

### 2.2 Client Class Design

```python
from attio import AttioClient

# Sync client (default)
client = AttioClient(
    api_key="sk_...",
    base_url="https://api.attio.com/v2",  # default
    max_retries=3,                         # default
    retry_delay=1.0,                       # seconds, default
    timeout=30.0,                          # seconds, default
)

# All resources available as properties
client.objects.list()
client.records.query("people", filter={"name": {"$contains": "Jane"}})
client.people.create(values={"name": [{"first_name": "Jane"}]})

# Async client
from attio import AsyncAttioClient

async_client = AsyncAttioClient(api_key="sk_...")
await async_client.records.list("people")

# Context manager support
async with AsyncAttioClient(api_key="sk_...") as client:
    await client.records.list("people")

with AttioClient(api_key="sk_...") as client:
    client.records.list("people")
```

**Design decisions:**
- Separate `AttioClient` and `AsyncAttioClient` classes (not a unified class) -- this is the standard pattern in modern Python SDKs (Stripe, OpenAI, Anthropic) and avoids confusing await/non-await method signatures.
- Resources are lazy-initialized properties on the client.
- The low-level HTTP client is accessible as `client.http` for custom requests.
- Both clients support context manager protocol for clean resource cleanup.

### 2.3 Resource Class Design

```python
# Base resource pattern
class BaseResource:
    def __init__(self, http: HttpTransport):
        self._http = http

class AsyncBaseResource:
    def __init__(self, http: AsyncHttpTransport):
        self._http = http

# Example: Records resource
class RecordsResource(BaseResource):
    def list(
        self,
        object: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        ...

    def query(
        self,
        object: str,
        *,
        filter: dict[str, Any] | None = None,
        filter_view_id: str | None = None,
        sorts: list[Sort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Record]:
        ...

    def get(self, object: str, record_id: str) -> Record:
        ...

    def create(self, object: str, *, values: dict[str, Any]) -> Record:
        ...

    def update(self, object: str, record_id: str, *, values: dict[str, Any]) -> Record:
        ...

    def append(self, object: str, record_id: str, *, values: dict[str, Any]) -> Record:
        ...

    def delete(self, object: str, record_id: str) -> None:
        ...

    def upsert(
        self,
        object: str,
        *,
        matching_attribute: str,
        values: dict[str, Any],
    ) -> Record:
        ...

    def get_attribute_values(
        self,
        object: str,
        record_id: str,
        attribute: str,
        *,
        show_historic: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[AttributeValue]:
        ...

    def list_entries(
        self,
        object: str,
        record_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[RecordEntry]:
        ...

    def global_search(
        self,
        *,
        query: str,
        objects: list[str],
        limit: int | None = None,
    ) -> ListResponse[GlobalSearchResult]:
        ...
```

**Design patterns:**
- Keyword-only arguments after the first positional path identifier -- this prevents parameter ordering mistakes.
- Return Pydantic models, not raw dicts -- users get autocomplete, type safety, and serialization.
- The `data: { values: ... }` envelope is handled internally -- users pass `values` directly.
- Standard object resources (PeopleResource, CompaniesResource, etc.) inherit from a base that delegates to the records resource with a fixed object slug.

### 2.4 Type/Model Approach: Pydantic v2

**Recommendation: Pydantic v2**

Rationale:
1. **Validation at deserialization**: Catches API response changes immediately instead of silently passing bad data.
2. **IDE autocomplete**: Full attribute access with type hints on response objects.
3. **Serialization**: `model_dump()` for converting back to dicts when needed.
4. **JSON Schema**: Can generate OpenAPI-compatible schemas for documentation.
5. **Performance**: Pydantic v2 uses Rust-based validation, making it fast.
6. **Ecosystem**: Standard in modern Python -- OpenAI SDK, Anthropic SDK, Stripe SDK all use Pydantic.

**Why not TypedDict**: No runtime validation, no serialization helpers, worse IDE support.
**Why not dataclass**: No built-in validation, no serialization, would need manual `from_dict` methods.

**Model design:**

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class AttioModel(BaseModel):
    """Base model with shared config."""
    model_config = ConfigDict(
        populate_by_name=True,     # Allow both field name and alias
        extra="allow",             # Forward compat -- don't break on new fields
        frozen=False,              # Mutable by default for flexibility
    )

class ObjectId(AttioModel):
    workspace_id: str
    object_id: str

class RecordId(AttioModel):
    workspace_id: str
    object_id: str
    record_id: str

class ActorReference(AttioModel):
    id: str | None
    type: str  # "api-token" | "workspace-member" | "system" | "app"

class AttributeValue(AttioModel):
    active_from: datetime
    active_until: datetime | None
    created_by_actor: ActorReference
    attribute_type: str
    # Additional fields vary by type -- captured by extra="allow"

class Record(AttioModel):
    id: RecordId
    created_at: datetime
    web_url: str
    values: dict[str, list[AttributeValue]]

class ListResponse(AttioModel, Generic[T]):
    data: list[T]

class PaginatedResponse(AttioModel, Generic[T]):
    data: list[T]
    pagination: Pagination

class Pagination(AttioModel):
    next_cursor: str | None
```

**Key design choice -- `extra="allow"`**: The Attio API may add new fields at any time. By allowing extra fields, the SDK gracefully handles API additions without breaking. Users can access new fields via `model.model_extra` or by updating the SDK.

### 2.5 Error Handling Strategy

```python
class AttioError(Exception):
    """Base exception for all Attio API errors."""
    def __init__(self, message: str, status_code: int = 0, code: str | None = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.body = body

class AttioAPIError(AttioError):
    """Raised for non-2xx responses from the Attio API."""
    pass

class RateLimitError(AttioAPIError):
    """Raised when 429 and all retries exhausted."""
    def __init__(self, retry_after: float, body: Any = None):
        super().__init__(f"Rate limited. Retry after {retry_after}s", 429, "rate_limit_exceeded", body)
        self.retry_after = retry_after

class AuthenticationError(AttioAPIError):
    """Raised for 401 Unauthorized."""
    pass

class PermissionError(AttioAPIError):
    """Raised for 403 Forbidden (missing scopes)."""
    pass

class NotFoundError(AttioAPIError):
    """Raised for 404 Not Found."""
    pass

class ConflictError(AttioAPIError):
    """Raised for 409 Conflict (e.g., slug_conflict, unique attribute conflict)."""
    pass

class ValidationError(AttioAPIError):
    """Raised for 400 Bad Request with validation errors."""
    pass

class AttioConnectionError(AttioError):
    """Raised for network/connection failures."""
    pass

class AttioTimeoutError(AttioError):
    """Raised when request times out."""
    pass
```

**Compared to attio-node**: The node SDK has just 3 error classes (AttioError, RateLimitError, ScopeError). We add more granularity for Python idioms -- users can catch specific errors or the base class. This matches the Anthropic Python SDK pattern.

### 2.6 Async Support Approach

**Recommendation: Sync + Async via separate client classes.**

```python
# Sync (default -- most users)
from attio import AttioClient
client = AttioClient(api_key="sk_...")
records = client.records.list("people")

# Async
from attio import AsyncAttioClient
client = AsyncAttioClient(api_key="sk_...")
records = await client.records.list("people")
```

**Implementation strategy:**
- Use httpx, which natively supports both `httpx.Client` (sync) and `httpx.AsyncClient` (async).
- Each resource class has a sync and async variant. Use a code generation approach or a base class pattern to avoid duplicating logic.
- The recommended approach is to write the async version as the "source of truth" and generate sync wrappers, OR use the pattern from the Anthropic SDK where both sync and async resource classes inherit from a shared base that defines the interface.

**Simpler alternative (recommended for v1):** Write resource logic once with the async transport, then have the sync transport call `anyio.from_thread.run_sync()` or simply use httpx's sync client directly. The cleanest approach is:
- `_http.py` defines `HttpTransport` (sync, uses `httpx.Client`) and `AsyncHttpTransport` (async, uses `httpx.AsyncClient`)
- Resource methods are defined twice (sync + async) but share all parameter construction and response parsing logic via private helper methods.

### 2.7 Pagination Handling

```python
# Option 1: Manual iteration (always available)
response = client.records.list("people", limit=100)
for record in response.data:
    process(record)

# Option 2: Auto-pagination iterator (cursor-based endpoints)
for meeting in client.meetings.list_all(limit=50):
    process(meeting)

# Option 3: Auto-pagination async iterator
async for meeting in async_client.meetings.list_all(limit=50):
    process(meeting)
```

**Implementation:**
- Methods like `list()` return a single page (ListResponse or PaginatedResponse).
- Methods like `list_all()` (or `iter_all()`) return a generator/async generator that automatically fetches next pages.
- For offset-based pagination: increment offset by page size until `len(response.data) < limit`.
- For cursor-based pagination: pass `next_cursor` until it is `None`.

```python
class PaginationIterator(Generic[T]):
    """Synchronous auto-paginator for cursor-based endpoints."""
    def __iter__(self):
        cursor = None
        while True:
            response = self._fetch(cursor=cursor)
            yield from response.data
            cursor = response.pagination.next_cursor
            if cursor is None:
                break
```

### 2.8 Rate Limit / Retry Strategy

Mirror the attio-node SDK approach with Python idioms:

```python
# Defaults
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
TIMEOUT = 30.0     # seconds

# Retry logic:
# 1. On 429: Read Retry-After header, sleep, retry
# 2. On network error: Exponential backoff (delay * 2^attempt)
# 3. On timeout: No retry (raise immediately)
# 4. On 5xx: Retry with backoff (server errors can be transient)
# 5. On 4xx (except 429): No retry (client error, won't help)
```

Use `tenacity` or hand-roll a simple retry loop (hand-roll is preferred to minimize dependencies, matching attio-node's approach).

### 2.9 Webhook Signature Verification

```python
import hmac
import hashlib

def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """Verify Attio webhook HMAC-SHA256 signature."""
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## 3. Testing Strategy

### 3.1 Recommended Library Stack

| Library | Purpose | Rationale |
|---|---|---|
| **pytest** | Test runner | Industry standard, best plugin ecosystem |
| **respx** | HTTP mocking for httpx | Purpose-built for httpx. Pattern matching, side effects, both sync/async support |
| **pytest-asyncio** | Async test support | Required for testing async client |
| **coverage / pytest-cov** | Code coverage | Track test completeness |
| **VCR.py (optional)** | Response recording | Record real API responses for high-fidelity fixtures |

**Why respx over alternatives:**
- `responses` only works with `requests`, not `httpx`.
- `pytest-httpx` is simpler but `respx` has richer pattern matching (URL patterns, header matching, response side effects).
- `respx` supports both sync and async httpx clients natively.
- `respx` is the closest equivalent to `msw` (used by attio-node) in the Python ecosystem.

**Why VCR.py as optional complement:**
- The user specifically wants testing based on ACTUAL API responses.
- VCR.py records real HTTP interactions to YAML/JSON cassette files.
- First run hits the real API and records responses; subsequent runs replay from cassettes.
- This ensures response shapes exactly match what the API returns.
- Can be used alongside respx: respx for unit tests, VCR.py for integration/fixture generation.

### 3.2 Test Structure

```
tests/
  conftest.py                  # respx setup, shared client fixtures
  fixtures/
    __init__.py
    factory.py                 # Mock data factories (mirrors attio-node handlers.ts)
    cassettes/                 # VCR.py recorded responses (gitignored sensitive data)
      objects_list.yaml
      records_query.yaml
      ...
  test_client.py               # HTTP client: auth, retries, rate limiting, timeouts
  test_exceptions.py           # Error parsing and hierarchy
  test_pagination.py           # Auto-pagination iterators
  test_webhook_utils.py        # Signature verification
  resources/
    test_objects.py
    test_attributes.py
    test_records.py
    test_lists.py
    test_entries.py
    test_notes.py
    test_tasks.py
    test_webhooks.py
    test_workspace_members.py
    test_select_options.py
    test_statuses.py
    test_views.py
    test_comments.py
    test_threads.py
    test_files.py
    test_meetings.py
    test_call_recordings.py
    test_transcripts.py
    test_self.py
    test_people.py
    test_companies.py
    test_deals.py
```

### 3.3 Mock Data Factory (fixtures/factory.py)

Port the attio-node `handlers.ts` mock data to Python. This provides realistic response shapes:

```python
MOCK_OBJECT = {
    "id": {"workspace_id": "ws_01abc", "object_id": "obj_01abc"},
    "api_slug": "deals",
    "singular_noun": "Deal",
    "plural_noun": "Deals",
    "created_at": "2024-01-01T00:00:00.000Z",
}

MOCK_RECORD = {
    "id": {"workspace_id": "ws_01abc", "object_id": "obj_01abc", "record_id": "rec_01abc"},
    "created_at": "2024-01-01T00:00:00.000Z",
    "web_url": "https://app.attio.com/people/rec_01abc",
    "values": {},
}

# ... one for each resource type (mirroring handlers.ts)
```

### 3.4 Test Patterns

**Unit test pattern (per resource method):**

```python
import respx
from httpx import Response

@respx.mock
def test_records_list():
    route = respx.get("https://api.attio.com/v2/objects/people/records").mock(
        return_value=Response(200, json={"data": [MOCK_RECORD]})
    )
    client = AttioClient(api_key="test-key")
    result = client.records.list("people")

    assert route.called
    assert len(result.data) == 1
    assert result.data[0].id.record_id == "rec_01abc"

@respx.mock
async def test_records_list_async():
    route = respx.get("https://api.attio.com/v2/objects/people/records").mock(
        return_value=Response(200, json={"data": [MOCK_RECORD]})
    )
    client = AsyncAttioClient(api_key="test-key")
    result = await client.records.list("people")

    assert route.called
    assert len(result.data) == 1
```

**For each resource method, verify:**
1. Correct HTTP method used
2. Correct URL path constructed
3. Query parameters properly encoded
4. Request body properly serialized
5. Response properly deserialized into Pydantic model
6. Error responses properly mapped to exception types

**Client-level tests:**
1. Authentication header present
2. Rate limit retry (429 -> retry -> success)
3. Rate limit exhaustion (429 -> all retries -> RateLimitError)
4. Network error retry with exponential backoff
5. Timeout handling
6. 403 -> PermissionError
7. 404 -> NotFoundError
8. 400 -> ValidationError
9. 409 -> ConflictError
10. Non-JSON error bodies handled gracefully

**Pagination tests:**
1. Single page (next_cursor is None)
2. Multi-page iteration
3. Empty result set
4. Offset-based iteration

### 3.5 Response Fixture Strategy

**Three-tier approach:**

1. **Static fixtures (primary)**: Python dicts mirroring real response shapes, committed to repo. Used for all unit tests. Based on the attio-node mock data + enriched with actual field names from API docs.

2. **VCR.py cassettes (secondary)**: Recorded from real API calls. Used for integration validation. These cassettes are:
   - Generated by running a "record" test suite against a test Attio workspace.
   - Stored in `tests/fixtures/cassettes/`.
   - Sensitive data (API keys, real record IDs) scrubbed via VCR.py's `before_record_request` / `before_record_response` hooks.
   - Can be regenerated at any time by running tests with `--vcr-record=all`.

3. **Live integration tests (optional, CI-gated)**: Run against a real Attio workspace with `ATTIO_API_KEY` env var. Skipped by default, enabled via `pytest -m integration`.

### 3.6 Coverage Strategy

Target: **95%+ line coverage** for the SDK package.

- Every resource method tested (sync + async variants)
- Every error path tested
- Every pagination mode tested
- Webhook signature verification tested (valid, invalid, tampered)
- Edge cases: empty responses, missing fields, extra fields, None values

---

## 4. Dependency Recommendations

### 4.1 Runtime Dependencies

| Dependency | Version | Purpose | Rationale |
|---|---|---|---|
| **httpx** | `>=0.27,<1.0` | HTTP client | Sync + async in one library, HTTP/2 support, modern API. Used by Anthropic SDK, OpenAI SDK. Superior to `requests` (no async) and `aiohttp` (no sync). |
| **pydantic** | `>=2.0,<3.0` | Data models & validation | Industry standard for Python API SDKs. Runtime validation, serialization, IDE autocomplete. |

**Total: 2 runtime dependencies** (plus their transitive deps: `anyio`, `httpcore`, `certifi`, `idna`, `sniffio`, `annotated-types`, `pydantic-core`, `typing-extensions`).

### 4.2 Development Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| **pytest** | `>=8.0` | Test runner |
| **pytest-asyncio** | `>=0.24` | Async test support |
| **respx** | `>=0.22` | httpx mocking |
| **pytest-cov** | `>=6.0` | Coverage reporting |
| **vcrpy** | `>=7.0` | HTTP recording (optional) |
| **ruff** | `>=0.8` | Linting + formatting (replaces flake8, black, isort) |
| **mypy** | `>=1.14` | Static type checking |
| **hatch** | `>=1.14` | Build system + workspace management |

### 4.3 Why httpx over requests

| Feature | httpx | requests |
|---|---|---|
| Async support | Native (`AsyncClient`) | Requires `aiohttp` (different API) |
| HTTP/2 | Yes | No |
| Timeout handling | Granular (connect, read, write, pool) | Single timeout |
| Type hints | Full | Partial |
| Modern Python | Designed for 3.8+ | Legacy, 2012-era |
| Context manager | Yes (proper resource cleanup) | Not standard |

### 4.4 Build System: Hatch

**Why Hatch:**
- Native monorepo/workspace support via `hatch-workspace` plugin.
- PEP 621 compliant (`pyproject.toml` only, no `setup.py`).
- Environment management (dev, test, lint environments).
- Version management built-in.
- Used by many modern Python projects.

**Alternative: uv** -- faster but less mature for workspaces. Could switch later.

### 4.5 Python Version Support

- **Minimum: Python 3.10** -- for `X | Y` union syntax, `match` statements, improved type hints.
- **Tested on: 3.10, 3.11, 3.12, 3.13**

---

## 5. Comparison with attio-node

### 5.1 What to Keep the Same

| Aspect | attio-node Approach | Python SDK Approach |
|---|---|---|
| Resource-per-file | One file per API resource | Same -- one module per resource |
| Client composition | Resources as properties on client | Same pattern |
| Error hierarchy | Base + RateLimit + Scope | Extended (more granular, Python idiom) |
| Retry logic | Built-in, exponential backoff | Same behavior, hand-rolled |
| Rate limit handling | Auto-retry on 429 with Retry-After | Same |
| Mock data for tests | Centralized mock factories | Same pattern, ported to Python |
| Test per resource | One test file per resource | Same |
| Response envelope unwrap | Not unwrapped (returns `{data: T}`) | **Unwrap** -- return `T` directly (see below) |

### 5.2 What to Do Differently (Python Idioms)

| Aspect | attio-node | Python SDK | Rationale |
|---|---|---|---|
| **Naming** | camelCase methods | snake_case methods | PEP 8 convention |
| **Response unwrap** | Returns `{ data: T }` envelope | Returns `T` directly (the model) | Pythonic -- less boilerplate for users. `result.id` instead of `result.data.id` |
| **List responses** | Returns `{ data: T[] }` | Returns `ListResponse[T]` with `.data` property | Need to preserve pagination metadata |
| **Parameter style** | Object params (`{ data: { values: ... } }`) | Keyword args (`values={...}`) | Pythonic -- no need for nested dict construction |
| **Type models** | TypeScript interfaces (compile-time only) | Pydantic models (runtime validation) | Python lacks TS-style structural typing; Pydantic provides runtime safety |
| **Async** | All methods are async | Sync (default) + Async variant | Python users often want sync; provide both |
| **HTTP client** | Raw `fetch()` | `httpx` | Python has no built-in `fetch`; httpx is the modern standard |
| **Testing** | `msw` (Mock Service Worker) | `respx` | Equivalent approach for httpx mocking |
| **Attribute paths** | `attributes.get(attrId)` on a flat endpoint | `attributes.get(target, id, attr)` on nested endpoint | Docs show nested paths; match the actual API |
| **Comments + Threads** | Combined in `CommentsResource` | Separate `CommentsResource` and `ThreadsResource` | Cleaner separation of concerns |
| **Select + Status** | Combined in `SelectOptionsResource` | Separate `SelectOptionsResource` and `StatusesResource` | Different response shapes, clearer API |
| **Standard objects** | Not provided (use generic records) | Provide convenience wrappers (`client.people`, `client.companies`) | Docs have dedicated endpoints; improves DX |
| **Webhook event types** | `const` object enum | Python `StrEnum` | Python 3.11+ has native StrEnum |
| **Context manager** | Not supported | `with` / `async with` | Proper resource cleanup (httpx client lifecycle) |
| **File upload** | Throws "not supported" | Actually implement multipart upload | httpx natively supports multipart |

### 5.3 API Coverage Comparison

| Resource | attio-node | Python SDK (proposed) |
|---|---|---|
| Objects | list, get, create, update | Same |
| Attributes | list, get, create, update | Same (but with target/id in path) |
| Records | list, query, search, get, create, update, append, delete, upsert, getAttributeValues, listEntries, globalSearch | Same |
| Lists | list, get, create, update | Same |
| Entries | list, query, get, create, update, append, delete, upsert, getAttributeValues | Same |
| Notes | list, get, create, delete | Same |
| Tasks | list, get, create, update, delete | Same |
| Webhooks | list, get, create, update, delete | Same |
| Workspace Members | list, get | Same |
| Select Options | list, create, update | Same (separate resource) |
| Statuses | list, create, update | Same (separate resource) |
| Views | list (object/list) | Same (split into list_for_object, list_for_list) |
| Comments | create, get, delete | Same |
| Threads | get, list | Same (separate resource) |
| Files | list, get, createFolder, upload (broken), download, delete | Same (with working upload) |
| Meetings | list, get | Same |
| Call Recordings | list, get | Same |
| Transcripts | get | Same |
| Self | get | identify() |
| **People** | Not separate | **NEW** -- convenience wrapper |
| **Companies** | Not separate | **NEW** -- convenience wrapper |
| **Deals** | Not separate | **NEW** -- convenience wrapper |
| **Users** | Not separate | **NEW** -- convenience wrapper |
| **Workspaces** | Not separate | **NEW** -- convenience wrapper |
| Webhook Utils | verifyWebhookSignature | verify_webhook_signature |

### 5.4 Node SDK Issues to Fix in Python

1. **File upload is broken**: Node SDK throws an error because HttpClient only sends JSON. Python SDK will use httpx's native multipart support.
2. **Select options path is wrong in node**: Node SDK uses `/attributes/{attr}/select-options` but the actual API path is `/{target}/{id}/attributes/{attr}/options`. Python SDK will use the correct documented path.
3. **Attribute get path is potentially wrong**: Node SDK uses `/attributes/{id}` but docs show `/{target}/{id}/attributes/{attr}`. Need to verify against actual API. If both work, support both.
4. **Entry response field name**: The API docs show `entry_values` not `values` for entry responses. The node SDK types use `values`. Python SDK should match the actual API response field name.
5. **Missing `completed_at` on tasks**: Node SDK types lack `completed_at` field that the API returns. Python SDK will include it.
6. **Missing `workspace_id` in id objects**: Some node SDK types omit `workspace_id` from id objects. Python SDK will include all fields returned by the API.

---

## Appendix A: OpenAPI Spec URLs

For automated code generation or validation:

- **Core API**: `https://api.attio.com/openapi/api`
- **Standard Objects**: `https://api.attio.com/openapi/standard-objects`
- **Webhooks**: `https://api.attio.com/openapi/webhooks`

## Appendix B: Attio API Scopes (Complete)

Based on endpoint requirements:

| Scope | Endpoints |
|---|---|
| `object_configuration:read` | Objects (list/get), Attributes (list/get), Records (all), Entries (context) |
| `object_configuration:read-write` | Objects (create/update), Attributes (create/update) |
| `record_permission:read` | Records (list/get/query/search), Meetings |
| `record_permission:read-write` | Records (create/update/delete/upsert) |
| `list_configuration:read` | Lists (list/get), Entries (context), Attributes on lists |
| `list_configuration:read-write` | Lists (create/update) |
| `list_entry:read` | Entries (list/get/query), Record entries |
| `list_entry:read-write` | Entries (create/update/delete/upsert) |
| `note:read` | Notes (list/get) |
| `note:read-write` | Notes (create/delete) |
| `task:read` | Tasks (list/get) |
| `task:read-write` | Tasks (create/update/delete) |
| `webhook:read` | Webhooks (list/get) |
| `webhook:read-write` | Webhooks (create/update/delete) |
| `user_management:read` | Workspace Members (list/get), Tasks |
| `comment:read` | Comments (get), Threads (list/get) |
| `comment:read-write` | Comments (create/delete) |
| `file:read` | Files (list/get/download) |
| `file:read-write` | Files (create/upload/delete) |
| `meeting:read` | Meetings (list/get), Call Recordings, Transcripts |

## Appendix C: Webhook Event Type Enum

```python
from enum import StrEnum

class WebhookEventType(StrEnum):
    # Records
    RECORD_CREATED = "record.created"
    RECORD_UPDATED = "record.updated"
    RECORD_DELETED = "record.deleted"
    RECORD_MERGED = "record.merged"

    # List Entries
    LIST_ENTRY_CREATED = "list-entry.created"
    LIST_ENTRY_UPDATED = "list-entry.updated"
    LIST_ENTRY_DELETED = "list-entry.deleted"

    # Lists
    LIST_CREATED = "list.created"
    LIST_UPDATED = "list.updated"
    LIST_DELETED = "list.deleted"

    # Tasks
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"

    # Notes
    NOTE_CREATED = "note.created"
    NOTE_UPDATED = "note.updated"
    NOTE_DELETED = "note.deleted"
    NOTE_CONTENT_UPDATED = "note-content.updated"

    # Comments
    COMMENT_CREATED = "comment.created"
    COMMENT_DELETED = "comment.deleted"
    COMMENT_RESOLVED = "comment.resolved"
    COMMENT_UNRESOLVED = "comment.unresolved"

    # Object Attributes
    OBJECT_ATTRIBUTE_CREATED = "object-attribute.created"
    OBJECT_ATTRIBUTE_UPDATED = "object-attribute.updated"

    # List Attributes
    LIST_ATTRIBUTE_CREATED = "list-attribute.created"
    LIST_ATTRIBUTE_UPDATED = "list-attribute.updated"

    # Workspace Members
    WORKSPACE_MEMBER_CREATED = "workspace-member.created"

    # Call Recordings
    CALL_RECORDING_CREATED = "call-recording.created"
```
