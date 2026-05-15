"""Base Pydantic models for the Attio SDK."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AttioModel(BaseModel):
    """Base model with shared configuration for all Attio models."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        frozen=False,
    )


class DataWrapper(AttioModel, Generic[T]):
    """Wrapper for ``{"data": T}`` responses."""

    data: T


class ListResponse(AttioModel, Generic[T]):
    """Wrapper for ``{"data": [T]}`` responses."""

    data: list[T]


class Pagination(AttioModel):
    """Cursor pagination metadata."""

    next_cursor: str | None = None


class PaginatedResponse(AttioModel, Generic[T]):
    """Wrapper for ``{"data": [T], "pagination": {...}}`` responses."""

    data: list[T]
    pagination: Pagination
