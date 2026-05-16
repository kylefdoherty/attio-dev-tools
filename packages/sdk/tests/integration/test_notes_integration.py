"""Integration tests for Notes resource."""

from __future__ import annotations

from datetime import datetime

import pytest

from tests.integration.conftest import my_vcr


class TestNotesIntegration:
    @my_vcr.use_cassette("notes_list.yaml")
    def test_list_notes(self, client):
        result = client.notes.list()
        assert hasattr(result, "data")
        assert isinstance(result.data, list)

    @my_vcr.use_cassette("notes_list_with_data.yaml")
    def test_list_notes_with_data(self, client):
        """If notes exist, verify note fields are properly typed."""
        result = client.notes.list()
        assert hasattr(result, "data")
        if len(result.data) == 0:
            pytest.skip("No notes in workspace to verify field structure")
        note = result.data[0]
        assert hasattr(note.id, "note_id")
        assert isinstance(note.id.note_id, str)
        assert len(note.id.note_id) > 0
        assert isinstance(note.title, str)
        assert isinstance(note.parent_object, str)
        assert len(note.parent_object) > 0
        assert isinstance(note.parent_record_id, str)
        assert len(note.parent_record_id) > 0
        assert isinstance(note.format, str)
        assert note.format in ("plaintext", "markdown")
        assert isinstance(note.created_at, datetime)

    @my_vcr.use_cassette("notes_get.yaml")
    def test_get_note(self, client):
        """Get a single note by ID. Discover the ID from a list call first."""
        list_result = client.notes.list()
        if len(list_result.data) == 0:
            pytest.skip("No notes in workspace to test get")
        note_id = list_result.data[0].id.note_id

        note = client.notes.get(note_id)
        assert note.id.note_id == note_id
        assert isinstance(note.title, str)
        assert isinstance(note.parent_object, str)
        assert isinstance(note.parent_record_id, str)
        assert isinstance(note.created_at, datetime)
