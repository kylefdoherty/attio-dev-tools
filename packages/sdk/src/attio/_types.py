"""Shared type aliases for the Attio SDK."""

from __future__ import annotations

from typing import Any, TypeAlias

JsonDict: TypeAlias = dict[str, Any]
PathParam: TypeAlias = str  # object slug or UUID
