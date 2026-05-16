"""Integration tests for Call Recordings resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestCallRecordingsIntegration:
    @my_vcr.use_cassette("call_recordings_list.yaml")
    def test_list_call_recordings(self, client):
        """List meetings first; if any exist, list their call recordings."""
        meetings = client.meetings.list()

        if len(meetings.data) == 0:
            # No meetings in workspace -- verify the SDK method exists
            assert callable(getattr(client.call_recordings, "list", None))
            return

        meeting_id = meetings.data[0].id.meeting_id
        result = client.call_recordings.list(meeting_id)

        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert hasattr(result, "pagination")

        if len(result.data) > 0:
            rec = result.data[0]
            assert hasattr(rec.id, "call_recording_id")
            assert isinstance(rec.meeting_id, str)
            assert isinstance(rec.status, str)
