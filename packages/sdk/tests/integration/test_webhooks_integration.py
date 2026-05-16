"""Integration tests for Webhooks resource."""

from __future__ import annotations

from datetime import datetime

from tests.integration.conftest import my_vcr


class TestWebhooksIntegration:
    @my_vcr.use_cassette("webhooks_list.yaml")
    def test_list_webhooks(self, client):
        result = client.webhooks.list()
        assert hasattr(result, "data")
        assert isinstance(result.data, list)

    @my_vcr.use_cassette("webhooks_create_get_delete.yaml")
    def test_create_get_delete_webhook(self, client):
        """Full lifecycle: create a webhook, get it, delete it."""
        # Step 1: Create a webhook (filter must be explicitly present, even as None)
        webhook = client.webhooks.create(
            target_url="https://example.com/test-webhook",
            subscriptions=[{"event_type": "record.created", "filter": None}],
        )
        assert hasattr(webhook, "id")
        assert hasattr(webhook.id, "webhook_id")
        assert isinstance(webhook.id.webhook_id, str)
        assert len(webhook.id.webhook_id) > 0
        assert webhook.target_url == "https://example.com/test-webhook"
        assert isinstance(webhook.subscriptions, list)
        assert len(webhook.subscriptions) > 0
        assert webhook.subscriptions[0].event_type == "record.created"
        assert isinstance(webhook.status, str)
        assert isinstance(webhook.created_at, datetime)

        webhook_id = webhook.id.webhook_id

        # Step 2: Get the webhook by ID
        fetched = client.webhooks.get(webhook_id)
        assert fetched.id.webhook_id == webhook_id
        assert fetched.target_url == "https://example.com/test-webhook"
        assert isinstance(fetched.subscriptions, list)
        assert isinstance(fetched.status, str)
        assert isinstance(fetched.created_at, datetime)

        # Step 3: Delete the webhook
        result = client.webhooks.delete(webhook_id)
        assert result is None
