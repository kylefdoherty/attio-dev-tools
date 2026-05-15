"""Shared helpers for record-based commands (people, companies, deals, records).

Contains record-to-dict flattening logic and column definitions.
"""

from __future__ import annotations

import json
from typing import Any, Callable


def record_to_dict(record: Any) -> dict[str, Any]:
    """Flatten a Record model into a simple dict for display.

    Extracts commonly-used fields from the nested values structure.
    """
    result: dict[str, Any] = {}

    # ID
    if hasattr(record, "id"):
        rid = record.id
        result["record_id"] = getattr(rid, "record_id", str(rid))
        result["object_id"] = getattr(rid, "object_id", "")

    # Timestamps
    result["created_at"] = str(getattr(record, "created_at", ""))
    result["web_url"] = getattr(record, "web_url", "")

    # Flatten values
    values = getattr(record, "values", {})
    if isinstance(values, dict):
        for attr_slug, val_list in values.items():
            result[attr_slug] = _extract_display_value(attr_slug, val_list)

    return result


def _extract_display_value(attr_slug: str, val_list: Any) -> str:
    """Extract a human-readable value from an attribute value list."""
    if not val_list or not isinstance(val_list, list):
        return ""

    first = val_list[0]
    if hasattr(first, "model_dump"):
        first = first.model_dump(mode="json")

    if not isinstance(first, dict):
        return str(first)

    # Personal name
    if "first_name" in first or "last_name" in first:
        parts = [first.get("first_name", ""), first.get("last_name", "")]
        return " ".join(p for p in parts if p).strip()

    # Email
    if "email_address" in first:
        return first["email_address"]

    # Phone
    if "phone_number" in first:
        return first["phone_number"]

    # Domain
    if "domain" in first:
        return first["domain"]

    # Status
    if "status" in first and isinstance(first["status"], dict):
        return first["status"].get("title", "")

    # Currency
    if "currency_value" in first:
        return str(first["currency_value"])

    # Generic value field
    if "value" in first:
        return str(first["value"])

    # Fallback
    return str(first.get("attribute_type", ""))


# Column definitions for standard record objects

PEOPLE_COLUMNS = [
    {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
    {"header": "Name", "accessor": lambda r: r.get("name", "")},
    {"header": "Email", "accessor": lambda r: r.get("email_addresses", ""), "no_wrap": True},
    {"header": "Phone", "accessor": lambda r: r.get("phone_numbers", "")},
    {"header": "Created", "accessor": lambda r: r.get("created_at", "")[:10] if r.get("created_at") else ""},
]

COMPANIES_COLUMNS = [
    {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
    {"header": "Name", "accessor": lambda r: r.get("name", "")},
    {"header": "Domain", "accessor": lambda r: r.get("domains", r.get("primary_domain", ""))},
    {"header": "Created", "accessor": lambda r: r.get("created_at", "")[:10] if r.get("created_at") else ""},
]

DEALS_COLUMNS = [
    {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
    {"header": "Name", "accessor": lambda r: r.get("name", r.get("deal_name", ""))},
    {"header": "Stage", "accessor": lambda r: r.get("stage", "")},
    {"header": "Value", "accessor": lambda r: r.get("value", r.get("deal_value", ""))},
    {"header": "Created", "accessor": lambda r: r.get("created_at", "")[:10] if r.get("created_at") else ""},
]

GENERIC_COLUMNS = [
    {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
    {"header": "Name", "accessor": lambda r: r.get("name", "")},
    {"header": "Created", "accessor": lambda r: r.get("created_at", "")[:10] if r.get("created_at") else ""},
    {"header": "URL", "accessor": lambda r: r.get("web_url", "")},
]


def collect_cursor_pages(fetch_page_fn: Callable[..., Any]) -> list[Any]:
    """Collect all items from a cursor-paginated endpoint."""
    all_items: list[Any] = []
    cursor = None
    while True:
        result = fetch_page_fn(cursor)
        all_items.extend(result.data)
        if not hasattr(result, 'pagination') or result.pagination is None or result.pagination.next_cursor is None:
            break
        cursor = result.pagination.next_cursor
    return all_items


def collect_offset_pages(fetch_page_fn: Callable[..., Any], page_size: int = 500) -> list[Any]:
    """Collect all items from an offset-paginated endpoint."""
    all_items: list[Any] = []
    offset = 0
    while True:
        result = fetch_page_fn(offset, page_size)
        all_items.extend(result.data)
        if len(result.data) < page_size:
            break
        offset += len(result.data)
    return all_items


def parse_json_option(value: str | None) -> dict[str, Any] | None:
    """Parse a JSON string option, returning None if empty."""
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON: {e}")


def parse_sorts(sort: str | None, direction: str = "asc") -> list[dict[str, str]] | None:
    """Parse sort options into the SDK Sort format."""
    if not sort:
        return None
    return [{"attribute": sort, "direction": direction}]


VALUE_COLUMNS: list[dict[str, Any]] = [
    {"header": "Type", "accessor": lambda v: str(v.get("attribute_type", ""))},
    {"header": "Active From", "accessor": lambda v: str(v.get("active_from", ""))},
    {"header": "Active Until", "accessor": lambda v: str(v.get("active_until", ""))},
    {
        "header": "Data",
        "accessor": lambda v: json.dumps(
            {
                k: v2
                for k, v2 in v.items()
                if k not in ("attribute_type", "active_from", "active_until", "created_by_actor")
            },
            default=str,
        ),
    },
]


ENTRY_LIST_COLUMNS: list[dict[str, Any]] = [
    {"header": "Entry ID", "accessor": lambda e: e["entry_id"]},
    {"header": "List", "accessor": lambda e: e["list_slug"]},
    {"header": "Created", "accessor": lambda e: e["created_at"]},
]


def entry_to_dict(entry: Any) -> dict[str, Any]:
    """Convert an Entry model (with entry_values) to a simple dict for display."""
    result: dict[str, Any] = {}
    if hasattr(entry, "id"):
        eid = entry.id
        result["entry_id"] = getattr(eid, "entry_id", str(eid))
        result["list_id"] = getattr(eid, "list_id", "")
    result["parent_record_id"] = getattr(entry, "parent_record_id", "")
    result["parent_object"] = getattr(entry, "parent_object", "")
    result["created_at"] = str(getattr(entry, "created_at", ""))

    # Flatten entry_values
    entry_values = getattr(entry, "entry_values", {})
    if isinstance(entry_values, dict):
        for k, v in entry_values.items():
            if v and isinstance(v, list):
                first = v[0]
                if hasattr(first, "model_dump"):
                    first = first.model_dump(mode="json")
                result[k] = str(first) if first else ""
            else:
                result[k] = str(v)

    return result
