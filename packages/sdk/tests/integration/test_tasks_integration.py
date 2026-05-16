"""Integration tests for Tasks resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestTasksIntegration:
    @my_vcr.use_cassette("tasks_list.yaml")
    def test_list_tasks(self, client):
        result = client.tasks.list()
        assert hasattr(result, "data")
