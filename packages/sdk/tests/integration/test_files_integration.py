"""Integration tests for Files resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestFilesIntegration:
    @my_vcr.use_cassette("files_list.yaml")
    def test_list_files(self, client):
        """Query companies to get a record_id, then list files for that record."""
        companies = client.records.query("companies", limit=1)
        assert len(companies.data) > 0, "Need at least one company record"

        record_id = companies.data[0].id.record_id
        result = client.files.list(object="companies", record_id=record_id)

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert hasattr(result, "pagination")

        # Files may be empty -- that's fine, just verify the shape
        if len(result.data) > 0:
            f = result.data[0]
            assert hasattr(f.id, "file_id")
            assert isinstance(f.name, str)
            assert isinstance(f.file_type, str)
