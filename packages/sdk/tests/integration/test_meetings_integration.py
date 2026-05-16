"""Integration tests for Meetings resource."""

from __future__ import annotations

from datetime import datetime

from tests.integration.conftest import my_vcr


class TestMeetingsIntegration:
    @my_vcr.use_cassette("meetings_list.yaml")
    def test_list_meetings(self, client):
        """List meetings -- may be empty if workspace has no meetings."""
        result = client.meetings.list()

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert hasattr(result, "pagination")

        if len(result.data) > 0:
            meeting = result.data[0]
            assert hasattr(meeting.id, "meeting_id")
            assert isinstance(meeting.id.meeting_id, str)
            assert isinstance(meeting.participants, list)
            assert isinstance(meeting.created_at, datetime)
