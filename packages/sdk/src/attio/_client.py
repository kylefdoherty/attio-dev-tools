"""Attio client classes (sync and async)."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from attio._config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    ClientConfig,
)
from attio._http import AsyncHttpTransport, HttpTransport
from attio.resources.attributes import AsyncAttributesResource, AttributesResource
from attio.resources.call_recordings import (
    AsyncCallRecordingsResource,
    CallRecordingsResource,
)
from attio.resources.comments import AsyncCommentsResource, CommentsResource
from attio.resources.files import AsyncFilesResource, FilesResource
from attio.resources.lists import AsyncListsResource, ListsResource
from attio.resources.meetings import AsyncMeetingsResource, MeetingsResource
from attio.resources.notes import AsyncNotesResource, NotesResource
from attio.resources.objects import AsyncObjectsResource, ObjectsResource
from attio.resources.records import AsyncRecordsResource, RecordsResource
from attio.resources.select_options import (
    AsyncSelectOptionsResource,
    SelectOptionsResource,
)
from attio.resources.self_resource import AsyncSelfResource, SelfResource
from attio.resources.statuses import AsyncStatusesResource, StatusesResource
from attio.resources.tasks import AsyncTasksResource, TasksResource
from attio.resources.threads import AsyncThreadsResource, ThreadsResource
from attio.resources.transcripts import AsyncTranscriptsResource, TranscriptsResource
from attio.resources.views import AsyncViewsResource, ViewsResource
from attio.resources.webhooks import AsyncWebhooksResource, WebhooksResource
from attio.resources.workspace_members import (
    AsyncWorkspaceMembersResource,
    WorkspaceMembersResource,
)


class AttioClient:
    """Synchronous client for the Attio API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._config = ClientConfig(
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        self._http = HttpTransport(self._config)

    @property
    def http(self) -> HttpTransport:
        """Access the underlying HTTP transport for custom requests."""
        return self._http

    @cached_property
    def objects(self) -> ObjectsResource:
        """Access the Objects resource."""
        return ObjectsResource(self._http)

    @cached_property
    def lists(self) -> ListsResource:
        """Access the Lists resource."""
        return ListsResource(self._http)

    @cached_property
    def workspace_members(self) -> WorkspaceMembersResource:
        """Access the Workspace Members resource."""
        return WorkspaceMembersResource(self._http)

    @cached_property
    def self_(self) -> SelfResource:
        """Access the Self resource."""
        return SelfResource(self._http)

    @cached_property
    def attributes(self) -> AttributesResource:
        """Access the Attributes resource."""
        return AttributesResource(self._http)

    @cached_property
    def select_options(self) -> SelectOptionsResource:
        """Access the Select Options resource."""
        return SelectOptionsResource(self._http)

    @cached_property
    def statuses(self) -> StatusesResource:
        """Access the Statuses resource."""
        return StatusesResource(self._http)

    @cached_property
    def views(self) -> ViewsResource:
        """Access the Views resource."""
        return ViewsResource(self._http)

    @cached_property
    def notes(self) -> NotesResource:
        """Access the Notes resource."""
        return NotesResource(self._http)

    @cached_property
    def tasks(self) -> TasksResource:
        """Access the Tasks resource."""
        return TasksResource(self._http)

    @cached_property
    def records(self) -> RecordsResource:
        """Access the Records resource."""
        return RecordsResource(self._http)

    @cached_property
    def webhooks(self) -> WebhooksResource:
        """Access the Webhooks resource."""
        return WebhooksResource(self._http)

    @cached_property
    def comments(self) -> CommentsResource:
        """Access the Comments resource."""
        return CommentsResource(self._http)

    @cached_property
    def threads(self) -> ThreadsResource:
        """Access the Threads resource."""
        return ThreadsResource(self._http)

    @cached_property
    def files(self) -> FilesResource:
        """Access the Files resource."""
        return FilesResource(self._http)

    @cached_property
    def meetings(self) -> MeetingsResource:
        """Access the Meetings resource."""
        return MeetingsResource(self._http)

    @cached_property
    def call_recordings(self) -> CallRecordingsResource:
        """Access the Call Recordings resource."""
        return CallRecordingsResource(self._http)

    @cached_property
    def transcripts(self) -> TranscriptsResource:
        """Access the Transcripts resource."""
        return TranscriptsResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._http.close()

    def __enter__(self) -> AttioClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAttioClient:
    """Asynchronous client for the Attio API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._config = ClientConfig(
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        self._http = AsyncHttpTransport(self._config)

    @property
    def http(self) -> AsyncHttpTransport:
        """Access the underlying async HTTP transport for custom requests."""
        return self._http

    @cached_property
    def objects(self) -> AsyncObjectsResource:
        """Access the Objects resource."""
        return AsyncObjectsResource(self._http)

    @cached_property
    def lists(self) -> AsyncListsResource:
        """Access the Lists resource."""
        return AsyncListsResource(self._http)

    @cached_property
    def workspace_members(self) -> AsyncWorkspaceMembersResource:
        """Access the Workspace Members resource."""
        return AsyncWorkspaceMembersResource(self._http)

    @cached_property
    def self_(self) -> AsyncSelfResource:
        """Access the Self resource."""
        return AsyncSelfResource(self._http)

    @cached_property
    def attributes(self) -> AsyncAttributesResource:
        """Access the Attributes resource."""
        return AsyncAttributesResource(self._http)

    @cached_property
    def select_options(self) -> AsyncSelectOptionsResource:
        """Access the Select Options resource."""
        return AsyncSelectOptionsResource(self._http)

    @cached_property
    def statuses(self) -> AsyncStatusesResource:
        """Access the Statuses resource."""
        return AsyncStatusesResource(self._http)

    @cached_property
    def views(self) -> AsyncViewsResource:
        """Access the Views resource."""
        return AsyncViewsResource(self._http)

    @cached_property
    def notes(self) -> AsyncNotesResource:
        """Access the Notes resource."""
        return AsyncNotesResource(self._http)

    @cached_property
    def tasks(self) -> AsyncTasksResource:
        """Access the Tasks resource."""
        return AsyncTasksResource(self._http)

    @cached_property
    def records(self) -> AsyncRecordsResource:
        """Access the Records resource."""
        return AsyncRecordsResource(self._http)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResource:
        """Access the Webhooks resource."""
        return AsyncWebhooksResource(self._http)

    @cached_property
    def comments(self) -> AsyncCommentsResource:
        """Access the Comments resource."""
        return AsyncCommentsResource(self._http)

    @cached_property
    def threads(self) -> AsyncThreadsResource:
        """Access the Threads resource."""
        return AsyncThreadsResource(self._http)

    @cached_property
    def files(self) -> AsyncFilesResource:
        """Access the Files resource."""
        return AsyncFilesResource(self._http)

    @cached_property
    def meetings(self) -> AsyncMeetingsResource:
        """Access the Meetings resource."""
        return AsyncMeetingsResource(self._http)

    @cached_property
    def call_recordings(self) -> AsyncCallRecordingsResource:
        """Access the Call Recordings resource."""
        return AsyncCallRecordingsResource(self._http)

    @cached_property
    def transcripts(self) -> AsyncTranscriptsResource:
        """Access the Transcripts resource."""
        return AsyncTranscriptsResource(self._http)

    async def close(self) -> None:
        """Close the underlying async HTTP client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> AsyncAttioClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
