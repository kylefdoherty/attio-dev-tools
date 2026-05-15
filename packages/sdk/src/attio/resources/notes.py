"""Notes resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.notes import Note
from attio.resources._base import AsyncResource, SyncResource


class _NotesMixin:
    """Shared parameter/body construction logic for the Notes resource."""

    @staticmethod
    def _build_query_params(
        *,
        parent_object: str | None = None,
        parent_record_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | None:
        params: dict[str, Any] = {}
        if parent_object is not None:
            params["parent_object"] = parent_object
        if parent_record_id is not None:
            params["parent_record_id"] = parent_record_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return params or None

    @staticmethod
    def _build_create_body(
        *,
        parent_object: str,
        parent_record_id: str,
        title: str,
        format: str = "plaintext",
        content: str,
    ) -> dict[str, Any]:
        return {
            "data": {
                "parent_object": parent_object,
                "parent_record_id": parent_record_id,
                "title": title,
                "format": format,
                "content": content,
            }
        }

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Note]:
        return ListResponse[Note].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Note:
        wrapper = DataWrapper[Note].model_validate(raw)
        return wrapper.data


class NotesResource(SyncResource, _NotesMixin):
    """Synchronous Notes resource."""

    def list(
        self,
        *,
        parent_object: str | None = None,
        parent_record_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Note]:
        """List notes, optionally filtered by parent object and record."""
        params = self._build_query_params(
            parent_object=parent_object,
            parent_record_id=parent_record_id,
            limit=limit,
            offset=offset,
        )
        raw = self._http.request("GET", "/notes", params=params)
        return self._parse_list_response(raw)

    def get(self, note_id: str) -> Note:
        """Get a single note by ID."""
        raw = self._http.request("GET", f"/notes/{note_id}")
        return self._parse_single_response(raw)

    def create(
        self,
        *,
        parent_object: str,
        parent_record_id: str,
        title: str,
        format: str = "plaintext",
        content: str,
    ) -> Note:
        """Create a new note."""
        body = self._build_create_body(
            parent_object=parent_object,
            parent_record_id=parent_record_id,
            title=title,
            format=format,
            content=content,
        )
        raw = self._http.request("POST", "/notes", json=body)
        return self._parse_single_response(raw)

    def delete(self, note_id: str) -> None:
        """Delete a note by ID."""
        self._http.request("DELETE", f"/notes/{note_id}")


class AsyncNotesResource(AsyncResource, _NotesMixin):
    """Asynchronous Notes resource."""

    async def list(
        self,
        *,
        parent_object: str | None = None,
        parent_record_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Note]:
        """List notes, optionally filtered by parent object and record."""
        params = self._build_query_params(
            parent_object=parent_object,
            parent_record_id=parent_record_id,
            limit=limit,
            offset=offset,
        )
        raw = await self._http.request("GET", "/notes", params=params)
        return self._parse_list_response(raw)

    async def get(self, note_id: str) -> Note:
        """Get a single note by ID."""
        raw = await self._http.request("GET", f"/notes/{note_id}")
        return self._parse_single_response(raw)

    async def create(
        self,
        *,
        parent_object: str,
        parent_record_id: str,
        title: str,
        format: str = "plaintext",
        content: str,
    ) -> Note:
        """Create a new note."""
        body = self._build_create_body(
            parent_object=parent_object,
            parent_record_id=parent_record_id,
            title=title,
            format=format,
            content=content,
        )
        raw = await self._http.request("POST", "/notes", json=body)
        return self._parse_single_response(raw)

    async def delete(self, note_id: str) -> None:
        """Delete a note by ID."""
        await self._http.request("DELETE", f"/notes/{note_id}")
