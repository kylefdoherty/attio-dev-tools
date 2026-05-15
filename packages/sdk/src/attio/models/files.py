"""Models for the Files resource."""

from __future__ import annotations

from datetime import datetime

from attio.models._base import AttioModel
from attio.models.common import ActorReference


class FileId(AttioModel):
    """Unique identifier for a file."""

    workspace_id: str
    file_id: str


class AttioFile(AttioModel):
    """Represents a file or folder in Attio."""

    id: FileId
    object_id: str
    object_slug: str
    record_id: str
    storage_provider: str
    created_by_actor: ActorReference
    created_at: datetime
    file_type: str  # "file" | "folder" | "connected-file" | "connected-folder"
    name: str
    parent_folder_id: str | None = None
    content_type: str | None = None
    content_size: int | None = None


class DownloadUrl(AttioModel):
    """Download URL for a file."""

    url: str
