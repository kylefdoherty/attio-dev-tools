"""Pydantic models for the Attio SDK."""

from attio.models._base import (
    AttioModel,
    DataWrapper,
    ListResponse,
    PaginatedResponse,
    Pagination,
)
from attio.models.attributes import Attribute, AttributeConfig, AttributeId
from attio.models.call_recordings import CallRecording, CallRecordingId
from attio.models.comments import Comment, CommentId
from attio.models.common import ActorReference, AttributeValue
from attio.models.entries import Entry, EntryId
from attio.models.files import AttioFile, DownloadUrl, FileId
from attio.models.lists import AttioList, ListId
from attio.models.meetings import Meeting, MeetingId, MeetingParticipant
from attio.models.notes import Note, NoteId
from attio.models.objects import Object, ObjectId
from attio.models.records import (
    GlobalSearchResult,
    Record,
    RecordEntry,
    RecordId,
    Sort,
)
from attio.models.select_options import (
    SelectOption,
    SelectOptionId,
    Status,
    StatusId,
)
from attio.models.self_info import SelfInfo
from attio.models.tasks import LinkedRecord, Task, TaskAssignee, TaskId
from attio.models.threads import Thread, ThreadId
from attio.models.transcripts import TranscriptSegment
from attio.models.views import View, ViewId
from attio.models.webhooks import Webhook, WebhookEventType, WebhookId, WebhookSubscription
from attio.models.workspace_members import WorkspaceMember, WorkspaceMemberId

__all__ = [
    "ActorReference",
    "AttioFile",
    "AttioList",
    "AttioModel",
    "Attribute",
    "AttributeConfig",
    "AttributeId",
    "AttributeValue",
    "CallRecording",
    "CallRecordingId",
    "Comment",
    "CommentId",
    "DataWrapper",
    "DownloadUrl",
    "Entry",
    "EntryId",
    "FileId",
    "GlobalSearchResult",
    "LinkedRecord",
    "ListId",
    "ListResponse",
    "Meeting",
    "MeetingId",
    "MeetingParticipant",
    "Note",
    "NoteId",
    "Object",
    "ObjectId",
    "PaginatedResponse",
    "Pagination",
    "Record",
    "RecordEntry",
    "RecordId",
    "SelectOption",
    "SelectOptionId",
    "SelfInfo",
    "Sort",
    "Status",
    "StatusId",
    "Task",
    "TaskAssignee",
    "TaskId",
    "Thread",
    "ThreadId",
    "TranscriptSegment",
    "View",
    "ViewId",
    "Webhook",
    "WebhookEventType",
    "WebhookId",
    "WebhookSubscription",
    "WorkspaceMember",
    "WorkspaceMemberId",
]
