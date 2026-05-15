"""Comments resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper
from attio.models.comments import Comment
from attio.resources._base import AsyncResource, SyncResource


class _CommentsMixin:
    """Shared parameter/body construction logic for the Comments resource."""

    @staticmethod
    def _validate_target(
        thread_id: str | None,
        record: dict[str, str] | None,
        entry: dict[str, str] | None,
    ) -> None:
        """Validate that exactly one target is provided."""
        targets = sum(x is not None for x in (thread_id, record, entry))
        if targets == 0:
            raise ValueError(
                "Exactly one of thread_id, record, or entry must be provided."
            )
        if targets > 1:
            raise ValueError(
                "Exactly one of thread_id, record, or entry must be provided; "
                f"got {targets}."
            )

    @staticmethod
    def _build_create_body(
        *,
        thread_id: str | None = None,
        record: dict[str, str] | None = None,
        entry: dict[str, str] | None = None,
        format: str = "plaintext",
        content: str,
        author: dict[str, str],
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "format": format,
            "content": content,
            "author": author,
        }
        if thread_id is not None:
            data["thread_id"] = thread_id
        elif record is not None:
            data["record"] = record
        elif entry is not None:
            data["entry"] = entry
        return {"data": data}

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Comment:
        wrapper = DataWrapper[Comment].model_validate(raw)
        return wrapper.data


class CommentsResource(SyncResource, _CommentsMixin):
    """Synchronous Comments resource."""

    def create(
        self,
        *,
        thread_id: str | None = None,
        record: dict[str, str] | None = None,
        entry: dict[str, str] | None = None,
        format: str = "plaintext",
        content: str,
        author: dict[str, str],
    ) -> Comment:
        """Create a comment on a thread, record, or entry."""
        self._validate_target(thread_id, record, entry)
        body = self._build_create_body(
            thread_id=thread_id,
            record=record,
            entry=entry,
            format=format,
            content=content,
            author=author,
        )
        raw = self._http.request("POST", "/comments", json=body)
        return self._parse_single_response(raw)

    def get(self, comment_id: str) -> Comment:
        """Get a single comment by ID."""
        raw = self._http.request("GET", f"/comments/{comment_id}")
        return self._parse_single_response(raw)

    def delete(self, comment_id: str) -> None:
        """Delete a comment by ID."""
        self._http.request("DELETE", f"/comments/{comment_id}")


class AsyncCommentsResource(AsyncResource, _CommentsMixin):
    """Asynchronous Comments resource."""

    async def create(
        self,
        *,
        thread_id: str | None = None,
        record: dict[str, str] | None = None,
        entry: dict[str, str] | None = None,
        format: str = "plaintext",
        content: str,
        author: dict[str, str],
    ) -> Comment:
        """Create a comment on a thread, record, or entry."""
        self._validate_target(thread_id, record, entry)
        body = self._build_create_body(
            thread_id=thread_id,
            record=record,
            entry=entry,
            format=format,
            content=content,
            author=author,
        )
        raw = await self._http.request("POST", "/comments", json=body)
        return self._parse_single_response(raw)

    async def get(self, comment_id: str) -> Comment:
        """Get a single comment by ID."""
        raw = await self._http.request("GET", f"/comments/{comment_id}")
        return self._parse_single_response(raw)

    async def delete(self, comment_id: str) -> None:
        """Delete a comment by ID."""
        await self._http.request("DELETE", f"/comments/{comment_id}")
