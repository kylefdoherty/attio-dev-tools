"""Files resource implementation (sync and async)."""

from __future__ import annotations

from typing import IO, Any, Union

from attio.models._base import DataWrapper, PaginatedResponse
from attio.models.files import AttioFile, DownloadUrl
from attio.resources._base import AsyncResource, SyncResource


class _FilesMixin:
    """Shared parameter/body construction logic for the Files resource."""

    @staticmethod
    def _build_list_params(
        *,
        object: str,
        record_id: str,
        storage_provider: str | None = None,
        parent_folder_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "object": object,
            "record_id": record_id,
        }
        if storage_provider is not None:
            params["storage_provider"] = storage_provider
        if parent_folder_id is not None:
            params["parent_folder_id"] = parent_folder_id
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        return params

    @staticmethod
    def _build_create_folder_body(
        *,
        name: str,
        object: str,
        record_id: str,
        parent_folder_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "data": {
                "name": name,
                "object": object,
                "record_id": record_id,
            }
        }
        if parent_folder_id is not None:
            body["data"]["parent_folder_id"] = parent_folder_id
        return body

    @staticmethod
    def _build_upload_data(
        *,
        object: str,
        record_id: str,
        parent_folder_id: str | None = None,
    ) -> dict[str, str]:
        data: dict[str, str] = {
            "object": object,
            "record_id": record_id,
        }
        if parent_folder_id is not None:
            data["parent_folder_id"] = parent_folder_id
        return data

    @staticmethod
    def _parse_paginated_response(raw: dict[str, Any]) -> PaginatedResponse[AttioFile]:
        return PaginatedResponse[AttioFile].model_validate(raw)

    @staticmethod
    def _parse_single_response(raw: dict[str, Any]) -> AttioFile:
        wrapper = DataWrapper[AttioFile].model_validate(raw)
        return wrapper.data

    @staticmethod
    def _parse_download_response(raw: dict[str, Any]) -> DownloadUrl:
        wrapper = DataWrapper[DownloadUrl].model_validate(raw)
        return wrapper.data


class FilesResource(SyncResource, _FilesMixin):
    """Synchronous Files resource."""

    def list(
        self,
        *,
        object: str,
        record_id: str,
        storage_provider: str | None = None,
        parent_folder_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[AttioFile]:
        """List files for a record."""
        params = self._build_list_params(
            object=object,
            record_id=record_id,
            storage_provider=storage_provider,
            parent_folder_id=parent_folder_id,
            limit=limit,
            cursor=cursor,
        )
        raw = self._http.request("GET", "/files", params=params)
        return self._parse_paginated_response(raw)

    def get(self, file_id: str) -> AttioFile:
        """Get a single file by ID."""
        raw = self._http.request("GET", f"/files/{file_id}")
        return self._parse_single_response(raw)

    def create_folder(
        self,
        *,
        name: str,
        object: str,
        record_id: str,
        parent_folder_id: str | None = None,
    ) -> AttioFile:
        """Create a new folder."""
        body = self._build_create_folder_body(
            name=name,
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        raw = self._http.request("POST", "/files/folders", json=body)
        return self._parse_single_response(raw)

    def upload(
        self,
        *,
        file: Union[bytes, IO[bytes]],
        filename: str,
        object: str,
        record_id: str,
        parent_folder_id: str | None = None,
    ) -> AttioFile:
        """Upload a file."""
        data = self._build_upload_data(
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        file_data = file if isinstance(file, bytes) else file
        raw = self._http.request_multipart(
            "POST",
            "/files",
            data=data,
            files={"file": (filename, file_data)},
        )
        return self._parse_single_response(raw)

    def download(self, file_id: str) -> DownloadUrl:
        """Get a download URL for a file."""
        raw = self._http.request("GET", f"/files/{file_id}/download")
        return self._parse_download_response(raw)

    def delete(self, file_id: str) -> None:
        """Delete a file."""
        self._http.request("DELETE", f"/files/{file_id}")


class AsyncFilesResource(AsyncResource, _FilesMixin):
    """Asynchronous Files resource."""

    async def list(
        self,
        *,
        object: str,
        record_id: str,
        storage_provider: str | None = None,
        parent_folder_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> PaginatedResponse[AttioFile]:
        """List files for a record."""
        params = self._build_list_params(
            object=object,
            record_id=record_id,
            storage_provider=storage_provider,
            parent_folder_id=parent_folder_id,
            limit=limit,
            cursor=cursor,
        )
        raw = await self._http.request("GET", "/files", params=params)
        return self._parse_paginated_response(raw)

    async def get(self, file_id: str) -> AttioFile:
        """Get a single file by ID."""
        raw = await self._http.request("GET", f"/files/{file_id}")
        return self._parse_single_response(raw)

    async def create_folder(
        self,
        *,
        name: str,
        object: str,
        record_id: str,
        parent_folder_id: str | None = None,
    ) -> AttioFile:
        """Create a new folder."""
        body = self._build_create_folder_body(
            name=name,
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        raw = await self._http.request("POST", "/files/folders", json=body)
        return self._parse_single_response(raw)

    async def upload(
        self,
        *,
        file: Union[bytes, IO[bytes]],
        filename: str,
        object: str,
        record_id: str,
        parent_folder_id: str | None = None,
    ) -> AttioFile:
        """Upload a file."""
        data = self._build_upload_data(
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        file_data = file if isinstance(file, bytes) else file
        raw = await self._http.request_multipart(
            "POST",
            "/files",
            data=data,
            files={"file": (filename, file_data)},
        )
        return self._parse_single_response(raw)

    async def download(self, file_id: str) -> DownloadUrl:
        """Get a download URL for a file."""
        raw = await self._http.request("GET", f"/files/{file_id}/download")
        return self._parse_download_response(raw)

    async def delete(self, file_id: str) -> None:
        """Delete a file."""
        await self._http.request("DELETE", f"/files/{file_id}")
