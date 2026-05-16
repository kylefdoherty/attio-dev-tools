"""Integration tests for Notes resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestNotesIntegration:
    @my_vcr.use_cassette("notes_list.yaml")
    def test_list_notes(self, client):
        result = client.notes.list()
        assert hasattr(result, "data")
