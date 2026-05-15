"""Tests for the _values module (simplified value expansion)."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from attio_cli._values import expand_value, expand_values, expand_entry_values, KEY_ALIASES


class TestExpandValue:
    def test_text(self):
        assert expand_value("hello", "text") == [{"value": "hello"}]

    def test_number(self):
        assert expand_value(42, "number") == [{"value": 42}]

    def test_checkbox(self):
        assert expand_value(True, "checkbox") == [{"value": True}]

    def test_personal_name(self):
        assert expand_value("Jane Doe", "personal-name") == [{"first_name": "Jane", "last_name": "Doe"}]

    def test_personal_name_single(self):
        assert expand_value("Madonna", "personal-name") == [{"first_name": "Madonna", "last_name": ""}]

    def test_personal_name_multiple_spaces(self):
        assert expand_value("Mary Jane Watson", "personal-name") == [{"first_name": "Mary", "last_name": "Jane Watson"}]

    def test_email(self):
        assert expand_value("j@x.com", "email-address") == [{"email_address": "j@x.com"}]

    def test_phone(self):
        assert expand_value("+1234", "phone-number") == [{"original_phone_number": "+1234"}]

    def test_domain(self):
        assert expand_value("acme.com", "domain") == [{"domain": "acme.com"}]

    def test_currency(self):
        assert expand_value(1000, "currency") == [{"currency_value": 1000}]

    def test_select(self):
        assert expand_value("high", "select") == [{"option": "high"}]

    def test_status(self):
        assert expand_value("active", "status") == [{"status": "active"}]

    def test_record_reference_passthrough(self):
        val = {"target_object": "companies", "target_record_id": "abc"}
        assert expand_value(val, "record-reference") == val

    def test_location_passthrough(self):
        val = {"line_1": "123 Main St"}
        assert expand_value(val, "location") == val

    def test_list_passthrough(self):
        val = [{"value": "already wrapped"}]
        assert expand_value(val, "text") == val

    def test_none_type_fallback(self):
        assert expand_value("test", None) == [{"value": "test"}]

    def test_unknown_type_fallback(self):
        assert expand_value("test", "some-future-type") == [{"value": "test"}]


class TestKeyAliases:
    def test_email_alias(self):
        assert KEY_ALIASES["email"] == "email_addresses"

    def test_phone_alias(self):
        assert KEY_ALIASES["phone"] == "phone_numbers"

    def test_domain_alias(self):
        assert KEY_ALIASES["domain"] == "domains"


class TestExpandValues:
    def test_full_expansion(self):
        mock_client = MagicMock()
        mock_attr = MagicMock()
        mock_attr.api_slug = "name"
        mock_attr.type = "personal-name"
        mock_attr2 = MagicMock()
        mock_attr2.api_slug = "email_addresses"
        mock_attr2.type = "email-address"
        mock_attr3 = MagicMock()
        mock_attr3.api_slug = "job_title"
        mock_attr3.type = "text"
        mock_result = MagicMock()
        mock_result.data = [mock_attr, mock_attr2, mock_attr3]
        mock_client.attributes.list.return_value = mock_result

        values = {"name": "Jane Doe", "email": "jane@acme.com", "job_title": "CTO"}
        result = expand_values(mock_client, "people", values)

        assert result["name"] == [{"first_name": "Jane", "last_name": "Doe"}]
        assert result["email_addresses"] == [{"email_address": "jane@acme.com"}]
        assert result["job_title"] == [{"value": "CTO"}]

    def test_attribute_lookup_failure(self):
        mock_client = MagicMock()
        mock_client.attributes.list.side_effect = Exception("API error")

        values = {"name": "Jane", "title": "CTO"}
        result = expand_values(mock_client, "people", values)
        # Falls back to wrapping with [{"value": ...}]
        assert result["name"] == [{"value": "Jane"}]
        assert result["title"] == [{"value": "CTO"}]

    def test_mixed_simplified_and_full(self):
        mock_client = MagicMock()
        mock_attr = MagicMock()
        mock_attr.api_slug = "name"
        mock_attr.type = "personal-name"
        mock_result = MagicMock()
        mock_result.data = [mock_attr]
        mock_client.attributes.list.return_value = mock_result

        values = {
            "name": "Jane Doe",  # simplified
            "custom": [{"value": "already wrapped"}],  # full format
        }
        result = expand_values(mock_client, "people", values)
        assert result["name"] == [{"first_name": "Jane", "last_name": "Doe"}]
        assert result["custom"] == [{"value": "already wrapped"}]

    def test_uses_correct_target(self):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_client.attributes.list.return_value = mock_result

        expand_values(mock_client, "people", {"x": "y"}, target="objects")
        mock_client.attributes.list.assert_called_once_with("objects", "people")


class TestExpandEntryValues:
    def test_uses_lists_target(self):
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_client.attributes.list.return_value = mock_result

        expand_entry_values(mock_client, "my_pipeline", {"stage": "Active"})
        mock_client.attributes.list.assert_called_once_with("lists", "my_pipeline")
