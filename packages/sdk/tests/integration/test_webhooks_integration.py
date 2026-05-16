"""Integration tests for Webhooks resource."""

from __future__ import annotations

from tests.integration.conftest import my_vcr


class TestWebhooksIntegration:
    @my_vcr.use_cassette("webhooks_list.yaml")
    def test_list_webhooks(self, client):
        result = client.webhooks.list()
        assert hasattr(result, "data")
