"""Tests for the files commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from attio_cli.commands.files import app as files_app

runner = CliRunner()

# Create a test app with the files command group registered.
app = typer.Typer()
app.add_typer(files_app, name="files")


@app.callback()
def _main(ctx: typer.Context, json_output: bool = typer.Option(False, "--json")) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output


def _make_mock_file(file_id="file_123", name="report.pdf", file_type="file"):
    """Create a mock AttioFile model."""
    f = MagicMock()
    f.id = MagicMock()
    f.id.file_id = file_id
    f.name = name
    f.file_type = file_type
    f.content_type = "application/pdf"
    f.content_size = 1024
    f.object_id = "obj_people"
    f.object_slug = "people"
    f.record_id = "rec_123"
    f.storage_provider = "attio"
    f.parent_folder_id = None
    f.created_at = "2026-01-01T00:00:00Z"
    return f


class TestFilesList:
    """Test the files list command."""

    def test_list_json(self):
        """files list --json should return files for a record."""
        mock_response = MagicMock()
        mock_response.data = [
            _make_mock_file("file_1", "doc.pdf"),
            _make_mock_file("file_2", "image.png", "file"),
        ]

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app, ["--json", "files", "list", "--object", "people", "--record", "rec_123"]
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert parsed["data"][0]["name"] == "doc.pdf"

    def test_list_with_filters(self):
        """files list with optional filters should pass them to the SDK."""
        mock_response = MagicMock()
        mock_response.data = [_make_mock_file()]

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.list.return_value = mock_response
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "files", "list",
                    "--object", "people",
                    "--record", "rec_123",
                    "--storage-provider", "google_drive",
                    "--parent-folder", "folder_1",
                ],
            )
            assert result.exit_code == 0
            mock_client.files.list.assert_called_once_with(
                object="people",
                record_id="rec_123",
                storage_provider="google_drive",
                parent_folder_id="folder_1",
                limit=None,
                cursor=None,
            )


class TestFilesListAll:
    """Test the files list --all command."""

    def test_list_all_cursor(self):
        """files list --all should paginate through all cursor pages."""
        mock_file1 = _make_mock_file("file_1", "doc1.pdf")
        mock_file2 = _make_mock_file("file_2", "doc2.pdf")

        # First page has next_cursor, second page does not
        mock_response1 = MagicMock()
        mock_response1.data = [mock_file1]
        mock_response1.pagination = MagicMock()
        mock_response1.pagination.next_cursor = "cursor_2"

        mock_response2 = MagicMock()
        mock_response2.data = [mock_file2]
        mock_response2.pagination = MagicMock()
        mock_response2.pagination.next_cursor = None

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.list.side_effect = [mock_response1, mock_response2]
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                ["--json", "files", "list", "--object", "people", "--record", "rec_123", "--all"],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert len(parsed["data"]) == 2
            assert mock_client.files.list.call_count == 2


class TestFilesGet:
    """Test the files get command."""

    def test_get_by_id(self):
        """files get should return a file by ID."""
        mock_file = _make_mock_file()

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.get.return_value = mock_file
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "files", "get", "file_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["id"] == "file_123"
            assert parsed["data"]["name"] == "report.pdf"


class TestFilesUpload:
    """Test the files upload command."""

    def test_upload(self, tmp_path):
        """files upload should read file from disk and call upload."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        mock_file = _make_mock_file(name="test.txt")

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.upload.return_value = mock_file
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "files", "upload",
                    "--file", str(test_file),
                    "--object", "people",
                    "--record", "rec_123",
                ],
            )
            assert result.exit_code == 0
            mock_client.files.upload.assert_called_once()
            call_kwargs = mock_client.files.upload.call_args[1]
            assert call_kwargs["filename"] == "test.txt"
            assert call_kwargs["object"] == "people"
            assert call_kwargs["record_id"] == "rec_123"


class TestFilesDownload:
    """Test the files download command."""

    def test_download(self):
        """files download should return a download URL."""
        mock_url = MagicMock()
        mock_url.url = "https://example.com/download/file_123"

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.download.return_value = mock_url
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "files", "download", "file_123"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["url"] == "https://example.com/download/file_123"


class TestFilesCreateFolder:
    """Test the files create-folder command."""

    def test_create_folder(self):
        """files create-folder should create a folder."""
        mock_folder = _make_mock_file(file_id="folder_1", name="Documents", file_type="folder")

        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.create_folder.return_value = mock_folder
            mock_gc.return_value = mock_client

            result = runner.invoke(
                app,
                [
                    "--json", "files", "create-folder",
                    "--name", "Documents",
                    "--object", "people",
                    "--record", "rec_123",
                ],
            )
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["data"]["name"] == "Documents"
            assert parsed["data"]["file_type"] == "folder"


class TestFilesDelete:
    """Test the files delete command."""

    def test_delete_with_yes(self):
        """files delete --yes should skip confirmation."""
        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "files", "delete", "file_123", "--yes"])
            assert result.exit_code == 0
            mock_client.files.delete.assert_called_once_with("file_123")

    def test_delete_calls_sdk(self):
        """files delete should call the SDK delete method."""
        with patch("attio_cli.commands.files.get_client") as mock_gc:
            mock_client = MagicMock()
            mock_client.files.delete.return_value = None
            mock_gc.return_value = mock_client

            result = runner.invoke(app, ["--json", "files", "delete", "file_456", "--yes"])
            assert result.exit_code == 0
            parsed = json.loads(result.output)
            assert parsed["status"] == "success"
