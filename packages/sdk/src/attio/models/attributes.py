"""Models for the Attributes resource."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from attio.models._base import AttioModel


class AttributeId(AttioModel):
    """Identifier for an Attio attribute."""

    workspace_id: str
    object_id: str
    attribute_id: str


class AttributeConfig(AttioModel):
    """Configuration settings for an attribute."""

    currency: dict[str, Any] | None = None
    record_reference: dict[str, Any] | None = None


class Attribute(AttioModel):
    """Represents an Attio attribute on an object or list."""

    id: AttributeId
    title: str
    description: str | None = None
    api_slug: str
    type: str
    is_system_attribute: bool
    is_writable: bool
    is_required: bool
    is_unique: bool
    is_multiselect: bool
    is_default_value_enabled: bool
    is_archived: bool
    default_value: dict[str, Any] | None = None
    relationship: dict[str, Any] | None = None
    created_at: datetime
    config: AttributeConfig
