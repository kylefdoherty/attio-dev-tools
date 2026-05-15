"""Tests for the Files resource (sync and async)."""

from __future__ import annotations

import io

import httpx
import pytest
import respx

from attio import AsyncAttioClient, AttioClient
from attio.models._base import PaginatedResponse
from attio.models.files import AttioFile, DownloadUrl

from tests.fixtures.factory import (
    MOCK_FILE_DELETE,
    MOCK_FILE_DOWNLOAD,
    MOCK_FILE_FOLDER_CREATED,
    MOCK_FILE_SINGLE,
    MOCK_FILE_UPLOADED,
    MOCK_FILES_LIST,
    MOCK_NOT_FOUND_ERROR,
)

BASE_URL = "https://api.attio.com/v2"
TEST_KEY = "test_key_files"


def _sync_client() -> AttioClient:
    return AttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


def _async_client() -> AsyncAttioClient:
    return AsyncAttioClient(api_key=TEST_KEY, base_url=BASE_URL, retry_delay=0.0)


# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


class TestFilesResourceSync:
    @respx.mock
    def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/files").mock(
            return_value=httpx.Response(200, json=MOCK_FILES_LIST)
        )
        client = _sync_client()
        result = client.files.list(object="people", record_id="rec_01abc123def456")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], AttioFile)
        assert result.data[0].name == "proposal.pdf"
        assert result.data[0].id.file_id == "file_01abc123def456"
        assert result.data[0].file_type == "file"
        assert result.data[1].file_type == "folder"
        assert result.pagination.next_cursor is None
        client.close()

    @respx.mock
    def test_list_with_params(self) -> None:
        route = respx.get(f"{BASE_URL}/files").mock(
            return_value=httpx.Response(200, json=MOCK_FILES_LIST)
        )
        client = _sync_client()
        client.files.list(
            object="people",
            record_id="rec_01abc",
            storage_provider="attio",
            parent_folder_id="folder_01",
            limit=10,
            cursor="cursor_abc",
        )

        assert route.called
        request = route.calls[0].request
        assert "object=people" in str(request.url)
        assert "record_id=rec_01abc" in str(request.url)
        assert "storage_provider=attio" in str(request.url)
        assert "parent_folder_id=folder_01" in str(request.url)
        assert "limit=10" in str(request.url)
        assert "cursor=cursor_abc" in str(request.url)
        client.close()

    @respx.mock
    def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/files/file_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_SINGLE)
        )
        client = _sync_client()
        result = client.files.get("file_01abc123def456")

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.name == "proposal.pdf"
        assert result.content_type == "application/pdf"
        assert result.content_size == 102400
        client.close()

    @respx.mock
    def test_create_folder(self) -> None:
        route = respx.post(f"{BASE_URL}/files/folders").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_FOLDER_CREATED)
        )
        client = _sync_client()
        result = client.files.create_folder(
            name="New Folder",
            object="people",
            record_id="rec_01abc123def456",
        )

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.file_type == "folder"
        assert result.name == "New Folder"

        # Verify request body
        import json

        request = route.calls[0].request
        body = json.loads(request.content)
        assert body == {
            "data": {
                "name": "New Folder",
                "object": "people",
                "record_id": "rec_01abc123def456",
            }
        }
        client.close()

    @respx.mock
    def test_upload_bytes(self) -> None:
        route = respx.post(f"{BASE_URL}/files").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_UPLOADED)
        )
        client = _sync_client()
        result = client.files.upload(
            file=b"file content here",
            filename="report.csv",
            object="people",
            record_id="rec_01abc123def456",
        )

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.name == "report.csv"
        assert result.file_type == "file"
        client.close()

    @respx.mock
    def test_upload_file_object(self) -> None:
        route = respx.post(f"{BASE_URL}/files").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_UPLOADED)
        )
        client = _sync_client()
        file_obj = io.BytesIO(b"file content from io")
        result = client.files.upload(
            file=file_obj,
            filename="report.csv",
            object="people",
            record_id="rec_01abc123def456",
        )

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.name == "report.csv"
        client.close()

    @respx.mock
    def test_download(self) -> None:
        route = respx.get(f"{BASE_URL}/files/file_01abc123def456/download").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_DOWNLOAD)
        )
        client = _sync_client()
        result = client.files.download("file_01abc123def456")

        assert route.called
        assert isinstance(result, DownloadUrl)
        assert "storage.attio.com" in result.url
        client.close()

    @respx.mock
    def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/files/file_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_DELETE)
        )
        client = _sync_client()
        result = client.files.delete("file_01abc123def456")

        assert route.called
        assert result is None
        client.close()

    @respx.mock
    def test_get_not_found(self) -> None:
        from attio._exceptions import NotFoundError

        respx.get(f"{BASE_URL}/files/nonexistent").mock(
            return_value=httpx.Response(404, json=MOCK_NOT_FOUND_ERROR)
        )
        client = _sync_client()
        with pytest.raises(NotFoundError) as exc_info:
            client.files.get("nonexistent")
        assert exc_info.value.status_code == 404
        client.close()


# ---------------------------------------------------------------------------
# Async tests
# ---------------------------------------------------------------------------


class TestFilesResourceAsync:
    @respx.mock
    async def test_list(self) -> None:
        route = respx.get(f"{BASE_URL}/files").mock(
            return_value=httpx.Response(200, json=MOCK_FILES_LIST)
        )
        client = _async_client()
        result = await client.files.list(object="people", record_id="rec_01abc123def456")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert isinstance(result.data[0], AttioFile)
        assert result.data[0].name == "proposal.pdf"
        await client.close()

    @respx.mock
    async def test_get(self) -> None:
        route = respx.get(f"{BASE_URL}/files/file_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_SINGLE)
        )
        client = _async_client()
        result = await client.files.get("file_01abc123def456")

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.name == "proposal.pdf"
        await client.close()

    @respx.mock
    async def test_create_folder(self) -> None:
        route = respx.post(f"{BASE_URL}/files/folders").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_FOLDER_CREATED)
        )
        client = _async_client()
        result = await client.files.create_folder(
            name="New Folder",
            object="people",
            record_id="rec_01abc123def456",
        )

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.file_type == "folder"
        await client.close()

    @respx.mock
    async def test_upload(self) -> None:
        route = respx.post(f"{BASE_URL}/files").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_UPLOADED)
        )
        client = _async_client()
        result = await client.files.upload(
            file=b"async file content",
            filename="report.csv",
            object="people",
            record_id="rec_01abc123def456",
        )

        assert route.called
        assert isinstance(result, AttioFile)
        assert result.name == "report.csv"
        await client.close()

    @respx.mock
    async def test_download(self) -> None:
        route = respx.get(f"{BASE_URL}/files/file_01abc123def456/download").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_DOWNLOAD)
        )
        client = _async_client()
        result = await client.files.download("file_01abc123def456")

        assert route.called
        assert isinstance(result, DownloadUrl)
        assert "storage.attio.com" in result.url
        await client.close()

    @respx.mock
    async def test_delete(self) -> None:
        route = respx.delete(f"{BASE_URL}/files/file_01abc123def456").mock(
            return_value=httpx.Response(200, json=MOCK_FILE_DELETE)
        )
        client = _async_client()
        result = await client.files.delete("file_01abc123def456")

        assert route.called
        assert result is None
        await client.close()
