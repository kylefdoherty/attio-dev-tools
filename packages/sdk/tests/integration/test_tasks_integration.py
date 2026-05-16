"""Integration tests for Tasks resource."""

from __future__ import annotations

from datetime import datetime

import pytest

from tests.integration.conftest import my_vcr


class TestTasksIntegration:
    @my_vcr.use_cassette("tasks_list.yaml")
    def test_list_tasks(self, client):
        result = client.tasks.list()
        assert hasattr(result, "data")
        assert isinstance(result.data, list)

    @my_vcr.use_cassette("tasks_list_with_data.yaml")
    def test_list_tasks_with_data(self, client):
        """If tasks exist, verify task fields are properly typed."""
        result = client.tasks.list()
        assert hasattr(result, "data")
        if len(result.data) == 0:
            pytest.skip("No tasks in workspace to verify field structure")
        task = result.data[0]
        assert hasattr(task.id, "task_id")
        assert isinstance(task.id.task_id, str)
        assert len(task.id.task_id) > 0
        assert isinstance(task.content_plaintext, str)
        assert isinstance(task.is_completed, bool)
        assert isinstance(task.format, str)
        assert isinstance(task.created_at, datetime)
        # completed_at should exist as an attribute (may be None)
        assert hasattr(task, "completed_at")
        if task.is_completed:
            assert task.completed_at is not None

    @my_vcr.use_cassette("tasks_get.yaml")
    def test_get_task(self, client):
        """Get a single task by ID. Discover the ID from a list call first."""
        list_result = client.tasks.list()
        if len(list_result.data) == 0:
            pytest.skip("No tasks in workspace to test get")
        task_id = list_result.data[0].id.task_id

        task = client.tasks.get(task_id)
        assert task.id.task_id == task_id
        assert isinstance(task.content_plaintext, str)
        assert isinstance(task.is_completed, bool)
        assert isinstance(task.created_at, datetime)
