"""Integration tests for Comments resource."""

from __future__ import annotations

from datetime import datetime

from tests.integration.conftest import my_vcr


class TestCommentsIntegration:
    @my_vcr.use_cassette("comments_create_get_delete.yaml")
    def test_create_get_delete_comment(self, client):
        """Full lifecycle: create a comment on a company record, get it, delete it."""
        # Step 1: Query companies to get a record_id (people may be empty)
        companies = client.records.query("companies", limit=1)
        assert len(companies.data) > 0, "Need at least one company record for comment test"
        record_id = companies.data[0].id.record_id

        # Step 2: Get workspace member ID for the author field
        me = client.self_.identify()
        member_id = me.authorized_by_workspace_member_id

        # Step 3: Create a comment on that record
        comment = client.comments.create(
            record={"object": "companies", "record_id": record_id},
            content="Integration test comment - will be deleted",
            format="plaintext",
            author={"type": "workspace-member", "id": member_id},
        )
        assert hasattr(comment, "id")
        assert hasattr(comment.id, "comment_id")
        assert isinstance(comment.id.comment_id, str)
        assert len(comment.id.comment_id) > 0
        assert isinstance(comment.content_plaintext, str)
        assert "Integration test comment" in comment.content_plaintext
        assert isinstance(comment.thread_id, str)
        assert len(comment.thread_id) > 0
        assert isinstance(comment.created_at, datetime)

        comment_id = comment.id.comment_id

        # Step 4: Get the comment by ID
        fetched = client.comments.get(comment_id)
        assert fetched.id.comment_id == comment_id
        assert isinstance(fetched.content_plaintext, str)
        assert isinstance(fetched.thread_id, str)
        assert isinstance(fetched.created_at, datetime)

        # Step 5: Delete the comment
        result = client.comments.delete(comment_id)
        assert result is None
