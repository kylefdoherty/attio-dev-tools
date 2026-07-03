"""Files resource implementation (sync and async)."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, Union

from attio.models._base import DataWrapper, PaginatedResponse
from attio.models.files import AttioFile, DownloadUrl
from attio.resources._base import AsyncResource, SyncResource

if TYPE_CHECKING:
    from attio._pagination import AsyncCursorIterator, CursorIterator


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
            "object": object,
            "record_id": record_id,
            "file_type": "folder",
            "name": name,
        }
        if parent_folder_id is not None:
            body["parent_folder_id"] = parent_folder_id
        return body

    @staticmethod
    def _build_connect_body(
        *,
        object: str,
        record_id: str,
        storage_provider: str,
        external_provider_file_id: str,
        file_type: str = "connected-file",
        microsoft_drive_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "object": object,
            "record_id": record_id,
            "storage_provider": storage_provider,
            "external_provider_file_id": external_provider_file_id,
            "file_type": file_type,
        }
        if microsoft_drive_id is not None:
            body["microsoft_drive_id"] = microsoft_drive_id
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
        """Create a new native folder on a record. (beta)"""
        body = self._build_create_folder_body(
            name=name,
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        raw = self._http.request("POST", "/files", json=body)
        return self._parse_single_response(raw)

    def connect(
        self,
        *,
        object: str,
        record_id: str,
        storage_provider: str,
        external_provider_file_id: str,
        file_type: str = "connected-file",
        microsoft_drive_id: str | None = None,
    ) -> AttioFile:
        """Connect an external file or folder to a record. (beta)

        ``storage_provider`` is one of ``"dropbox"``, ``"box"``,
        ``"google-drive"``, or ``"microsoft-onedrive"``; ``file_type`` is
        ``"connected-file"`` or ``"connected-folder"``. ``microsoft_drive_id``
        is only used with ``"microsoft-onedrive"``.
        """
        body = self._build_connect_body(
            object=object,
            record_id=record_id,
            storage_provider=storage_provider,
            external_provider_file_id=external_provider_file_id,
            file_type=file_type,
            microsoft_drive_id=microsoft_drive_id,
        )
        raw = self._http.request("POST", "/files", json=body)
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
        """Upload a file (multipart, max 50MB). (beta)"""
        data = self._build_upload_data(
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        raw = self._http.request_multipart(
            "POST",
            "/files/upload",
            data=data,
            files={"file": (filename, file)},
        )
        return self._parse_single_response(raw)

    def download(self, file_id: str) -> DownloadUrl:
        """Get a short-lived signed download URL for a file. (beta)

        The API responds with a 302 redirect to a signed URL; this method
        returns that URL without following the redirect or downloading the
        file contents.
        """
        url = self._http.request_redirect_url("GET", f"/files/{file_id}/download")
        return DownloadUrl(url=url)

    def delete(self, file_id: str) -> None:
        """Delete a file. (beta)"""
        self._http.request("DELETE", f"/files/{file_id}")

    def list_all(
        self,
        *,
        object: str,
        record_id: str,
        storage_provider: str | None = None,
        parent_folder_id: str | None = None,
        limit: int | None = None,
    ) -> CursorIterator[AttioFile]:
        """Auto-paginate all files for a record. Returns an iterator over all files."""
        from attio._pagination import CursorIterator

        def fetch_page(cursor: str | None) -> PaginatedResponse[AttioFile]:
            return self.list(
                object=object,
                record_id=record_id,
                storage_provider=storage_provider,
                parent_folder_id=parent_folder_id,
                limit=limit,
                cursor=cursor,
            )

        return CursorIterator(fetch_page=fetch_page)


# --- GENERATED ASYNC CODE BELOW --- #


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
        """Create a new native folder on a record. (beta)"""
        body = self._build_create_folder_body(
            name=name,
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        raw = await self._http.request("POST", "/files", json=body)
        return self._parse_single_response(raw)

    async def connect(
        self,
        *,
        object: str,
        record_id: str,
        storage_provider: str,
        external_provider_file_id: str,
        file_type: str = "connected-file",
        microsoft_drive_id: str | None = None,
    ) -> AttioFile:
        """Connect an external file or folder to a record. (beta)

        ``storage_provider`` is one of ``"dropbox"``, ``"box"``,
        ``"google-drive"``, or ``"microsoft-onedrive"``; ``file_type`` is
        ``"connected-file"`` or ``"connected-folder"``. ``microsoft_drive_id``
        is only used with ``"microsoft-onedrive"``.
        """
        body = self._build_connect_body(
            object=object,
            record_id=record_id,
            storage_provider=storage_provider,
            external_provider_file_id=external_provider_file_id,
            file_type=file_type,
            microsoft_drive_id=microsoft_drive_id,
        )
        raw = await self._http.request("POST", "/files", json=body)
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
        """Upload a file (multipart, max 50MB). (beta)"""
        data = self._build_upload_data(
            object=object,
            record_id=record_id,
            parent_folder_id=parent_folder_id,
        )
        raw = await self._http.request_multipart(
            "POST",
            "/files/upload",
            data=data,
            files={"file": (filename, file)},
        )
        return self._parse_single_response(raw)

    async def download(self, file_id: str) -> DownloadUrl:
        """Get a short-lived signed download URL for a file. (beta)

        The API responds with a 302 redirect to a signed URL; this method
        returns that URL without following the redirect or downloading the
        file contents.
        """
        url = await self._http.request_redirect_url("GET", f"/files/{file_id}/download")
        return DownloadUrl(url=url)

    async def delete(self, file_id: str) -> None:
        """Delete a file. (beta)"""
        await self._http.request("DELETE", f"/files/{file_id}")

    def list_all(
        self,
        *,
        object: str,
        record_id: str,
        storage_provider: str | None = None,
        parent_folder_id: str | None = None,
        limit: int | None = None,
    ) -> AsyncCursorIterator[AttioFile]:
        """Auto-paginate all files for a record. Returns an async iterator over all files."""
        from attio._pagination import AsyncCursorIterator

        async def fetch_page(cursor: str | None) -> PaginatedResponse[AttioFile]:
            return await self.list(
                object=object,
                record_id=record_id,
                storage_provider=storage_provider,
                parent_folder_id=parent_folder_id,
                limit=limit,
                cursor=cursor,
            )

        return AsyncCursorIterator(fetch_page=fetch_page)
