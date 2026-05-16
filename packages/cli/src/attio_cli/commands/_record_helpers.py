"""Shared helpers for record-based commands (people, companies, deals, records).

Contains record-to-dict flattening logic, column definitions, and dynamic
attribute-based column discovery for custom objects.
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

# ---------------------------------------------------------------------------
# Dynamic attribute-based column discovery
# ---------------------------------------------------------------------------

# Mapping from standard object slugs to their pre-built column definitions.
_STANDARD_OBJECT_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "people": PEOPLE_COLUMNS,
    "companies": COMPANIES_COLUMNS,
    "deals": DEALS_COLUMNS,
}

# Attribute types that render well as table columns. Types like
# record-reference or interaction produce opaque IDs that aren't useful
# in a compact table view.
_DISPLAYABLE_ATTR_TYPES: set[str] = {
    "text",
    "number",
    "checkbox",
    "currency",
    "date",
    "timestamp",
    "email",
    "phone",
    "domain",
    "select",
    "status",
    "rating",
    "personal-name",
    "location",
}

# Maximum number of attribute columns to include in dynamic tables (beyond ID
# and Created, which are always shown).
_MAX_DYNAMIC_COLUMNS = 6

# Per-session cache: object_slug -> list[column_def].  Avoids re-fetching
# attribute metadata for the same object within a single CLI invocation.
_attribute_column_cache: dict[str, list[dict[str, Any]]] = {}


def _make_accessor(slug: str) -> Callable[[dict[str, Any]], str]:
    """Build an accessor function that reads *slug* from the flattened dict."""
    def _accessor(r: dict[str, Any], _slug: str = slug) -> str:
        return str(r.get(_slug, ""))
    return _accessor


def _build_columns_from_attributes(attributes: list[Any]) -> list[dict[str, Any]]:
    """Convert a list of Attribute models into column definitions.

    Filters to displayable types, excludes archived attributes, and caps at
    ``_MAX_DYNAMIC_COLUMNS`` attribute columns.  ID and Created are always
    prepended/appended.
    """
    cols: list[dict[str, Any]] = [
        {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
    ]

    attr_cols: list[dict[str, Any]] = []
    for attr in attributes:
        if getattr(attr, "is_archived", False):
            continue
        attr_type = getattr(attr, "type", "")
        if attr_type not in _DISPLAYABLE_ATTR_TYPES:
            continue
        slug = getattr(attr, "api_slug", "")
        title = getattr(attr, "title", slug)
        if not slug:
            continue
        attr_cols.append({
            "header": title,
            "accessor": _make_accessor(slug),
        })

    cols.extend(attr_cols[:_MAX_DYNAMIC_COLUMNS])
    cols.append({
        "header": "Created",
        "accessor": lambda r: r.get("created_at", "")[:10] if r.get("created_at") else "",
    })
    return cols


def get_columns_for_object(
    object_slug: str,
    client: Any | None = None,
) -> list[dict[str, Any]]:
    """Return display columns for *object_slug*.

    For standard objects (people, companies, deals) this returns the
    pre-built column definitions -- output is identical to the hardcoded
    versions.  For custom or unknown objects it fetches attribute metadata
    from the API and builds columns dynamically, falling back to
    ``GENERIC_COLUMNS`` if the fetch fails or no client is provided.

    Results are cached per object slug for the lifetime of the process.
    """
    # Fast path: standard objects
    if object_slug in _STANDARD_OBJECT_COLUMNS:
        return _STANDARD_OBJECT_COLUMNS[object_slug]

    # Check cache
    if object_slug in _attribute_column_cache:
        return _attribute_column_cache[object_slug]

    # No client -> fall back to generic
    if client is None:
        return GENERIC_COLUMNS

    # Fetch attribute metadata
    try:
        result = client.attributes.list("objects", object_slug)
        attributes = result.data
        if not isinstance(attributes, list) or not attributes:
            return GENERIC_COLUMNS
        columns = _build_columns_from_attributes(attributes)
        _attribute_column_cache[object_slug] = columns
        return columns
    except Exception:
        # Network or permission error -- degrade gracefully
        return GENERIC_COLUMNS


def clear_attribute_cache() -> None:
    """Clear the cached attribute columns.  Useful for testing."""
    _attribute_column_cache.clear()


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
