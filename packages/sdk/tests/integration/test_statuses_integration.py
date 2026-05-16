"""Integration tests for Statuses resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestStatusesIntegration:
    @my_vcr.use_cassette("statuses_list_deals_stage.yaml")
    def test_list_statuses(self, client):
        """List statuses for the deals/stage attribute.

        Deals typically have a 'stage' status attribute in Attio.
        """
        result = client.statuses.list("objects", "deals", "stage")
        assert hasattr(result, "data")
        assert isinstance(result.data, list)
        assert len(result.data) > 0, "Expected at least one status on deals/stage"
        for status in result.data:
            # Verify shape of each Status object
            assert hasattr(status, "id")
            assert isinstance(status.id.workspace_id, str)
            assert isinstance(status.id.object_id, str)
            assert isinstance(status.id.attribute_id, str)
            assert isinstance(status.id.status_id, str)
            assert isinstance(status.title, str)
            assert isinstance(status.is_archived, bool)
            assert isinstance(status.celebration_enabled, bool)
            # target_time_in_status may be None or a string
            if status.target_time_in_status is not None:
                assert isinstance(status.target_time_in_status, str)
