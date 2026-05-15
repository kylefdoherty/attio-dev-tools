"""Resource classes for the Attio SDK."""

from attio.resources.attributes import AsyncAttributesResource, AttributesResource
from attio.resources.call_recordings import (
    AsyncCallRecordingsResource,
    CallRecordingsResource,
)
from attio.resources.comments import AsyncCommentsResource, CommentsResource
from attio.resources.companies import AsyncCompaniesResource, CompaniesResource
from attio.resources.deals import AsyncDealsResource, DealsResource
from attio.resources.entries import AsyncEntriesResource, EntriesResource
from attio.resources.files import AsyncFilesResource, FilesResource
from attio.resources.lists import AsyncListsResource, ListsResource
from attio.resources.meetings import AsyncMeetingsResource, MeetingsResource
from attio.resources.notes import AsyncNotesResource, NotesResource
from attio.resources.objects import AsyncObjectsResource, ObjectsResource
from attio.resources.people import AsyncPeopleResource, PeopleResource
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
from attio.resources.users import AsyncUsersResource, UsersResource
from attio.resources.views import AsyncViewsResource, ViewsResource
from attio.resources.webhooks import AsyncWebhooksResource, WebhooksResource
from attio.resources.workspace_members import (
    AsyncWorkspaceMembersResource,
    WorkspaceMembersResource,
)
from attio.resources.workspaces_resource import (
    AsyncWorkspacesResource,
    WorkspacesResource,
)

__all__ = [
    "AsyncAttributesResource",
    "AsyncCallRecordingsResource",
    "AsyncCommentsResource",
    "AsyncCompaniesResource",
    "AsyncDealsResource",
    "AsyncEntriesResource",
    "AsyncFilesResource",
    "AsyncListsResource",
    "AsyncMeetingsResource",
    "AsyncNotesResource",
    "AsyncObjectsResource",
    "AsyncPeopleResource",
    "AsyncRecordsResource",
    "AsyncSelectOptionsResource",
    "AsyncSelfResource",
    "AsyncStatusesResource",
    "AsyncTasksResource",
    "AsyncThreadsResource",
    "AsyncTranscriptsResource",
    "AsyncUsersResource",
    "AsyncViewsResource",
    "AsyncWebhooksResource",
    "AsyncWorkspaceMembersResource",
    "AsyncWorkspacesResource",
    "AttributesResource",
    "CallRecordingsResource",
    "CommentsResource",
    "CompaniesResource",
    "DealsResource",
    "EntriesResource",
    "FilesResource",
    "ListsResource",
    "MeetingsResource",
    "NotesResource",
    "ObjectsResource",
    "PeopleResource",
    "RecordsResource",
    "SelectOptionsResource",
    "SelfResource",
    "StatusesResource",
    "TasksResource",
    "ThreadsResource",
    "TranscriptsResource",
    "UsersResource",
    "ViewsResource",
    "WebhooksResource",
    "WorkspaceMembersResource",
    "WorkspacesResource",
]
