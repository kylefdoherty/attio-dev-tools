"""Tasks resource implementation (sync and async)."""

from __future__ import annotations

from typing import Any

from attio.models._base import DataWrapper, ListResponse
from attio.models.tasks import Task
from attio.resources._base import AsyncResource, SyncResource


class _TasksMixin:
    """Shared parameter/body construction logic for the Tasks resource."""

    @staticmethod
    def _build_query_params(
        *,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        is_completed: bool | None = None,
        assignee: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | None:
        params: dict[str, Any] = {}
        if linked_object is not None:
            params["linked_object"] = linked_object
        if linked_record_id is not None:
            params["linked_record_id"] = linked_record_id
        if is_completed is not None:
            params["is_completed"] = is_completed
        if assignee is not None:
            params["assignee"] = assignee
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return params or None

    @staticmethod
    def _build_create_body(
        *,
        content: str,
        format: str = "plaintext",
        deadline_at: str | None = None,
        is_completed: bool = False,
        linked_records: list[dict[str, Any]] | None = None,
        assignees: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "content": content,
            "format": format,
            "is_completed": is_completed,
        }
        if deadline_at is not None:
            data["deadline_at"] = deadline_at
        if linked_records is not None:
            data["linked_records"] = linked_records
        if assignees is not None:
            data["assignees"] = assignees
        return {"data": data}

    @staticmethod
    def _build_update_body(
        *,
        content: str | None = None,
        format: str | None = None,
        deadline_at: str | None = None,
        is_completed: bool | None = None,
        linked_records: list[dict[str, Any]] | None = None,
        assignees: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if content is not None:
            data["content"] = content
        if format is not None:
            data["format"] = format
        if deadline_at is not None:
            data["deadline_at"] = deadline_at
        if is_completed is not None:
            data["is_completed"] = is_completed
        if linked_records is not None:
            data["linked_records"] = linked_records
        if assignees is not None:
            data["assignees"] = assignees
        return {"data": data}

    @staticmethod
    def _parse_list_response(raw: dict[str, Any]) -> ListResponse[Task]:
        return ListResponse[Task].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> Task:
        wrapper = DataWrapper[Task].model_validate(raw)
        return wrapper.data


class TasksResource(SyncResource, _TasksMixin):
    """Synchronous Tasks resource."""

    def list(
        self,
        *,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        is_completed: bool | None = None,
        assignee: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Task]:
        """List tasks, optionally filtered."""
        params = self._build_query_params(
            linked_object=linked_object,
            linked_record_id=linked_record_id,
            is_completed=is_completed,
            assignee=assignee,
            limit=limit,
            offset=offset,
        )
        raw = self._http.request("GET", "/tasks", params=params)
        return self._parse_list_response(raw)

    def get(self, task_id: str) -> Task:
        """Get a single task by ID."""
        raw = self._http.request("GET", f"/tasks/{task_id}")
        return self._parse_single_response(raw)

    def create(
        self,
        *,
        content: str,
        format: str = "plaintext",
        deadline_at: str | None = None,
        is_completed: bool = False,
        linked_records: list[dict[str, Any]] | None = None,
        assignees: list[dict[str, Any]] | None = None,
    ) -> Task:
        """Create a new task."""
        body = self._build_create_body(
            content=content,
            format=format,
            deadline_at=deadline_at,
            is_completed=is_completed,
            linked_records=linked_records,
            assignees=assignees,
        )
        raw = self._http.request("POST", "/tasks", json=body)
        return self._parse_single_response(raw)

    def update(
        self,
        task_id: str,
        *,
        content: str | None = None,
        format: str | None = None,
        deadline_at: str | None = None,
        is_completed: bool | None = None,
        linked_records: list[dict[str, Any]] | None = None,
        assignees: list[dict[str, Any]] | None = None,
    ) -> Task:
        """Update an existing task."""
        body = self._build_update_body(
            content=content,
            format=format,
            deadline_at=deadline_at,
            is_completed=is_completed,
            linked_records=linked_records,
            assignees=assignees,
        )
        raw = self._http.request("PATCH", f"/tasks/{task_id}", json=body)
        return self._parse_single_response(raw)

    def delete(self, task_id: str) -> None:
        """Delete a task by ID."""
        self._http.request("DELETE", f"/tasks/{task_id}")


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncTasksResource(AsyncResource, _TasksMixin):
    """Asynchronous Tasks resource."""

    async def list(
        self,
        *,
        linked_object: str | None = None,
        linked_record_id: str | None = None,
        is_completed: bool | None = None,
        assignee: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[Task]:
        """List tasks, optionally filtered."""
        params = self._build_query_params(
            linked_object=linked_object,
            linked_record_id=linked_record_id,
            is_completed=is_completed,
            assignee=assignee,
            limit=limit,
            offset=offset,
        )
        raw = await self._http.request("GET", "/tasks", params=params)
        return self._parse_list_response(raw)

    async def get(self, task_id: str) -> Task:
        """Get a single task by ID."""
        raw = await self._http.request("GET", f"/tasks/{task_id}")
        return self._parse_single_response(raw)

    async def create(
        self,
        *,
        content: str,
        format: str = "plaintext",
        deadline_at: str | None = None,
        is_completed: bool = False,
        linked_records: list[dict[str, Any]] | None = None,
        assignees: list[dict[str, Any]] | None = None,
    ) -> Task:
        """Create a new task."""
        body = self._build_create_body(
            content=content,
            format=format,
            deadline_at=deadline_at,
            is_completed=is_completed,
            linked_records=linked_records,
            assignees=assignees,
        )
        raw = await self._http.request("POST", "/tasks", json=body)
        return self._parse_single_response(raw)

    async def update(
        self,
        task_id: str,
        *,
        content: str | None = None,
        format: str | None = None,
        deadline_at: str | None = None,
        is_completed: bool | None = None,
        linked_records: list[dict[str, Any]] | None = None,
        assignees: list[dict[str, Any]] | None = None,
    ) -> Task:
        """Update an existing task."""
        body = self._build_update_body(
            content=content,
            format=format,
            deadline_at=deadline_at,
            is_completed=is_completed,
            linked_records=linked_records,
            assignees=assignees,
        )
        raw = await self._http.request("PATCH", f"/tasks/{task_id}", json=body)
        return self._parse_single_response(raw)

    async def delete(self, task_id: str) -> None:
        """Delete a task by ID."""
        await self._http.request("DELETE", f"/tasks/{task_id}")
