"""Auto-expand simplified values into Attio's array-of-dicts format."""
from __future__ import annotations

import sys
from typing import Any

KEY_ALIASES: dict[str, str] = {
    "email": "email_addresses",
    "phone": "phone_numbers",
    "domain": "domains",
}


def fetch_attribute_map(client: Any, target: str, target_id: str) -> dict[str, str]:
    """Fetch attribute slug -> type mapping. Returns empty dict on failure."""
    try:
        result = client.attributes.list(target, target_id)
        return {attr.api_slug: attr.type for attr in result.data}
    except Exception:
        return {}


def expand_value(value: Any, attr_type: str | None) -> Any:
    """Expand a single value based on its attribute type."""
    if isinstance(value, list):
        return value  # already in full format

    if attr_type is None:
        return [{"value": value}]

    match attr_type:
        case "personal-name" if isinstance(value, str):
            parts = value.split(" ", 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ""
            return [{"first_name": first, "last_name": last}]
        case "email-address":
            return [{"email_address": value}]
        case "phone-number":
            return [{"original_phone_number": str(value)}]
        case "domain":
            return [{"domain": value}]
        case "currency" if isinstance(value, (int, float)):
            return [{"currency_value": value}]
        case "select":
            return [{"option": value}]
        case "status":
            return [{"status": value}]
        case "record-reference" | "location":
            return value  # pass through complex types
        case _:
            return [{"value": value}]


def expand_values(client: Any, object_slug: str, values: dict[str, Any], target: str = "objects") -> dict[str, Any]:
    """Expand simplified values dict into Attio's full format."""
    attr_map = fetch_attribute_map(client, target, object_slug)
    result = {}
    for key, value in values.items():
        resolved_key = KEY_ALIASES.get(key, key)
        attr_type = attr_map.get(resolved_key)
        result[resolved_key] = expand_value(value, attr_type)
    return result


def expand_entry_values(client: Any, list_slug: str, values: dict[str, Any]) -> dict[str, Any]:
    """Expand simplified entry values using list attribute types."""
    return expand_values(client, list_slug, values, target="lists")
