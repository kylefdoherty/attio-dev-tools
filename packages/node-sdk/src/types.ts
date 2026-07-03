// ---------------------------------------------------------------------------
// Common
// ---------------------------------------------------------------------------

export interface ListResponse<T> {
  data: T[];
}

// ---------------------------------------------------------------------------
// Objects
// ---------------------------------------------------------------------------

export interface AttioObject {
  id: { workspace_id: string; object_id: string };
  api_slug: string;
  singular_noun: string;
  plural_noun: string;
  description: string | null;
  created_at: string;
}

export interface CreateObjectParams {
  api_slug: string;
  singular_noun: string;
  plural_noun: string;
}

export interface UpdateObjectParams {
  singular_noun?: string;
  plural_noun?: string;
  description?: string;
}

// ---------------------------------------------------------------------------
// Attributes
// ---------------------------------------------------------------------------

export type AttributeType =
  | 'text'
  | 'number'
  | 'currency'
  | 'date'
  | 'checkbox'
  | 'select'
  | 'status'
  | 'rating'
  | 'email-address'
  | 'phone-number'
  | 'domain'
  | 'location'
  | 'record-reference'
  | 'interaction'
  | 'personal-name'
  | 'timestamp'
  | 'actor-reference';

export interface AttioAttribute {
  id: { attribute_id: string };
  api_slug: string;
  title: string;
  type: AttributeType;
  description: string | null;
  is_required: boolean;
  is_unique: boolean;
  is_multiselect: boolean;
  is_archived: boolean;
  is_system_attribute: boolean;
  config: Record<string, unknown>;
  created_at: string;
}

export interface CreateAttributeParams {
  title: string;
  api_slug: string;
  type: AttributeType;
  description?: string;
  is_required?: boolean;
  is_unique?: boolean;
  is_multiselect?: boolean;
  config?: Record<string, unknown>;
}

export interface UpdateAttributeParams {
  title?: string;
  description?: string;
  is_required?: boolean;
  is_unique?: boolean;
  is_multiselect?: boolean;
  is_archived?: boolean;
}

// ---------------------------------------------------------------------------
// Select Options & Statuses
// ---------------------------------------------------------------------------

export interface SelectOption {
  id: {
    workspace_id: string;
    object_id: string;
    attribute_id: string;
    option_id: string;
  };
  title: string;
  is_archived: boolean;
}

export interface CreateSelectOptionParams {
  title: string;
}

export interface StatusOption {
  id: {
    workspace_id: string;
    object_id: string;
    attribute_id: string;
    status_id: string;
  };
  title: string;
  is_archived: boolean;
  celebration_enabled: boolean;
  target_time_in_status: string | null;
}

export interface CreateStatusParams {
  title: string;
  celebration_enabled?: boolean;
  target_time_in_status?: string | null;
}

export interface UpdateStatusParams {
  title?: string;
  celebration_enabled?: boolean;
  target_time_in_status?: string | null;
}

// ---------------------------------------------------------------------------
// Records
// ---------------------------------------------------------------------------

export interface AttioRecord {
  id: { workspace_id: string; record_id: string; object_id: string };
  values: Record<string, AttributeValue[]>;
  created_at: string;
  web_url: string;
}

export interface AttributeValue {
  active_from: string;
  active_until: string | null;
  created_by_actor: ActorReference;
  attribute_type: string;
  [key: string]: unknown;
}

export interface ActorReference {
  type: string;
  id: string;
}

export interface RecordQueryParams {
  /** Attribute filter. Mutually exclusive with `filter_view_id`. */
  filter?: Record<string, unknown>;
  /**
   * Reuse the filter of a saved view (see `client.views.list()`).
   * Mutually exclusive with `filter` — the view's sorts and columns are ignored.
   */
  filter_view_id?: string;
  sorts?: Array<{ attribute: string; direction: 'asc' | 'desc' }>;
  limit?: number;
  offset?: number;
}

export interface CreateRecordParams {
  data: {
    values: Record<string, unknown>;
  };
}

export interface UpdateRecordParams {
  data: {
    values: Record<string, unknown>;
  };
}

export interface UpsertRecordParams {
  data: {
    matching_attribute: string;
    values: Record<string, unknown>;
  };
}

// ---------------------------------------------------------------------------
// Lists
// ---------------------------------------------------------------------------

export interface AttioList {
  id: { workspace_id: string; list_id: string };
  api_slug: string;
  name: string;
  parent_object: string;
  workspace_access: string;
  workspace_member_access: string;
  created_by_actor: ActorReference;
  created_at: string;
}

export interface CreateListParams {
  name: string;
  parent_object: string;
  api_slug?: string;
  workspace_access?: string;
}

export interface UpdateListParams {
  name?: string;
  api_slug?: string;
  workspace_access?: string;
  workspace_member_access?: string;
}

// ---------------------------------------------------------------------------
// Views
// ---------------------------------------------------------------------------

export interface AttioView {
  id: {
    workspace_id: string;
    view_id: string;
    object_id?: string;
    list_id?: string;
  };
  title: string;
  created_at: string;
}

export interface ListViewsParams {
  show_archived?: boolean;
  limit?: number;
  cursor?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    next_cursor: string | null;
  };
}

// ---------------------------------------------------------------------------
// Entries
// ---------------------------------------------------------------------------

export interface AttioEntry {
  id: { workspace_id: string; entry_id: string; list_id: string };
  parent_object: string;
  parent_record_id: string;
  entry_values: Record<string, AttributeValue[]>;
  created_at: string;
}

export interface EntryQueryParams {
  /** Attribute filter. Mutually exclusive with `filter_view_id`. */
  filter?: Record<string, unknown>;
  /**
   * Reuse the filter of a saved view (see `client.views.list()`).
   * Mutually exclusive with `filter` — the view's sorts and columns are ignored.
   */
  filter_view_id?: string;
  sorts?: Array<{ attribute: string; direction: 'asc' | 'desc' }>;
  limit?: number;
  offset?: number;
}

export interface CreateEntryParams {
  data: {
    parent_record_id: string;
    values?: Record<string, unknown>;
  };
}

export interface UpdateEntryParams {
  data: {
    values: Record<string, unknown>;
  };
}

export interface UpsertEntryParams {
  data: {
    parent_record_id: string;
    values?: Record<string, unknown>;
  };
}

// ---------------------------------------------------------------------------
// Notes
// ---------------------------------------------------------------------------

export interface AttioNote {
  id: { workspace_id: string; note_id: string };
  parent_object: string;
  parent_record_id: string;
  title: string;
  content_plaintext: string;
  content_markdown: string | null;
  meeting_id: string | null;
  tags: string[];
  created_by_actor: ActorReference;
  created_at: string;
}

export interface CreateNoteParams {
  data: {
    parent_object: string;
    parent_record_id: string;
    title: string;
    format: 'plaintext' | 'markdown';
    content: string;
    created_at?: string;
    meeting_id?: string;
  };
}

// ---------------------------------------------------------------------------
// Tasks
// ---------------------------------------------------------------------------

export interface AttioTask {
  id: { workspace_id: string; task_id: string };
  content_plaintext: string;
  is_completed: boolean;
  completed_at: string | null;
  deadline_at: string | null;
  linked_records: Array<{
    target_object_id: string;
    target_record_id: string;
  }>;
  assignees: Array<{
    referenced_actor_type: string;
    referenced_actor_id: string;
  }>;
  created_by_actor: ActorReference;
  created_at: string;
}

export interface CreateTaskParams {
  data: {
    content: string;
    format: 'plaintext';
    deadline_at?: string;
    is_completed?: boolean;
    linked_records?: Array<{
      target_object_id: string;
      target_record_id: string;
    }>;
    assignees?: Array<{
      referenced_actor_type: string;
      referenced_actor_id: string;
    }>;
  };
}

export interface UpdateTaskParams {
  data: {
    content?: string;
    format?: 'plaintext';
    deadline_at?: string | null;
    is_completed?: boolean;
    linked_records?: Array<{
      target_object_id: string;
      target_record_id: string;
    }>;
    assignees?: Array<{
      referenced_actor_type: string;
      referenced_actor_id: string;
    }>;
  };
}

// ---------------------------------------------------------------------------
// Webhooks
// ---------------------------------------------------------------------------

export interface AttioWebhook {
  id: { webhook_id: string };
  target_url: string;
  subscriptions: Array<{
    event_type: string;
    filter?: Record<string, unknown>;
  }>;
  status: string;
  created_at: string;
}

export interface CreateWebhookParams {
  data: {
    target_url: string;
    subscriptions: Array<{
      event_type: string;
      filter?: Record<string, unknown>;
    }>;
  };
}

export interface UpdateWebhookParams {
  data: {
    target_url?: string;
    subscriptions?: Array<{
      event_type: string;
      filter?: Record<string, unknown>;
    }>;
  };
}

// ---------------------------------------------------------------------------
// Workspace Members
// ---------------------------------------------------------------------------

export interface WorkspaceMember {
  id: { workspace_member_id: string };
  first_name: string;
  last_name: string;
  email_address: string;
  avatar_url: string | null;
  access_level: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Comments & Threads
// ---------------------------------------------------------------------------

export interface AttioComment {
  id: { comment_id: string };
  thread_id: string;
  content_plaintext: string;
  author: { type: string; id: string };
  created_by_actor: ActorReference;
  created_at: string;
  resolved_at: string | null;
  resolved_by: ActorReference | null;
  record: { object: string; record_id: string } | null;
  entry: { list: string; entry_id: string } | null;
}

/** Reply to an existing thread. */
export interface CreateCommentOnThread {
  data: {
    thread_id: string;
    format: 'plaintext';
    content: string;
    author: { type: 'workspace-member'; id: string };
    created_at?: string;
  };
}

/** Comment on a record. */
export interface CreateCommentOnRecord {
  data: {
    record: { object: string; record_id: string };
    format: 'plaintext';
    content: string;
    author: { type: 'workspace-member'; id: string };
    created_at?: string;
  };
}

/** Comment on a list entry. */
export interface CreateCommentOnEntry {
  data: {
    entry: { list: string; entry_id: string };
    format: 'plaintext';
    content: string;
    author: { type: 'workspace-member'; id: string };
    created_at?: string;
  };
}

export type CreateCommentParams =
  | CreateCommentOnThread
  | CreateCommentOnRecord
  | CreateCommentOnEntry;

export interface ListThreadsParams {
  record_id?: string;
  object?: string;
  entry_id?: string;
  list?: string;
}

export interface AttioThread {
  id: { thread_id: string };
  record_id: string;
  record: { object: string; record_id: string } | null;
  entry: { list: string; entry_id: string } | null;
  comments: AttioComment[];
  created_at: string;
}

// ---------------------------------------------------------------------------
// Files
// ---------------------------------------------------------------------------

export type FileStorageProvider =
  | 'attio'
  | 'dropbox'
  | 'box'
  | 'google-drive'
  | 'microsoft-onedrive';

export type FileEntryType = 'file' | 'folder' | 'connected-file' | 'connected-folder';

/**
 * A file entry attached to a record. (beta)
 *
 * Depending on `file_type`, some fields are only present on certain variants:
 * native files carry `content_type`/`content_size`, connected entries carry
 * `external_provider_file_id`/`microsoft_drive_id`.
 */
export interface AttioFile {
  id: { workspace_id: string; file_id: string };
  object_id: string;
  object_slug: string;
  record_id: string;
  storage_provider: FileStorageProvider;
  file_type: FileEntryType;
  /** File or folder name. Present on native `file`/`folder` entries. */
  name?: string;
  /** MIME type. Present on native `file` entries. */
  content_type?: string | null;
  /** Size in bytes. Present on native `file` entries. */
  content_size?: number | null;
  parent_folder_id?: string | null;
  /** The file/folder ID in the external provider. Present on connected entries. */
  external_provider_file_id?: string;
  /** Microsoft drive ID. Only populated for `microsoft-onedrive` entries. */
  microsoft_drive_id?: string | null;
  created_by_actor: ActorReference;
  created_at: string;
}

export interface ListFilesParams {
  object?: string;
  record_id?: string;
  parent_folder_id?: string;
  storage_provider?: FileStorageProvider;
  limit?: number;
  cursor?: string;
}

/** Parameters for creating a native Attio folder. (beta) */
export interface CreateFolderParams {
  /** The object slug or ID. */
  object: string;
  /** The ID of the record to create the folder on. */
  record_id: string;
  /** The folder name. */
  name: string;
  /** Optional parent folder ID. Omit to create a top-level folder. */
  parent_folder_id?: string;
}

/** Parameters for linking a file or folder from an external storage provider. (beta) */
export interface CreateConnectedFileParams {
  /** The object slug or ID. */
  object: string;
  /** The ID of the record to create the file entry on. */
  record_id: string;
  file_type: 'connected-file' | 'connected-folder';
  storage_provider: Exclude<FileStorageProvider, 'attio'>;
  /** The ID of the file or folder in the external storage provider. */
  external_provider_file_id: string;
  /** Microsoft drive ID. Only used when `storage_provider` is `microsoft-onedrive`. */
  microsoft_drive_id?: string | null;
}

/** Parameters for uploading a file to native Attio storage. (beta) Max file size is 50 MB. */
export interface UploadFileParams {
  /** The file contents. Buffers are wrapped in a Blob automatically (Node 18+). */
  file: Blob | Buffer;
  /** The object slug or ID. */
  object: string;
  /** The ID of the record to upload the file to. */
  record_id: string;
  /** Filename sent in the multipart form data (e.g. `report.pdf`). */
  filename?: string;
  /** Optional parent folder ID. Omit to upload to the root folder. */
  parent_folder_id?: string;
}

// ---------------------------------------------------------------------------
// Meetings
// ---------------------------------------------------------------------------

/** A point in time for a non-all-day meeting. */
export interface MeetingDateTime {
  datetime: string;
  timezone: string | null;
}

/** A calendar date for an all-day meeting. */
export interface MeetingDate {
  date: string;
}

export type MeetingParticipantStatus = 'accepted' | 'tentative' | 'declined' | 'pending';

export interface MeetingParticipant {
  /** The normalized email address of the participant, if available. */
  email_address: string | null;
  is_organizer: boolean;
  status: MeetingParticipantStatus;
}

/** A meeting synced or created in Attio. (beta) */
export interface AttioMeeting {
  id: { workspace_id: string; meeting_id: string };
  title: string;
  description: string;
  is_all_day: boolean;
  /** Non-all-day meetings return `{ datetime, timezone }`; all-day meetings return `{ date }`. */
  start: MeetingDateTime | MeetingDate;
  /** Exclusive end (RFC 5545): the meeting ends before this time, not at it. */
  end: MeetingDateTime | MeetingDate;
  participants: MeetingParticipant[];
  linked_records: Array<{
    object_slug: string;
    object_id: string;
    record_id: string;
  }>;
  created_at: string;
  created_by_actor: ActorReference;
}

/** Query parameters for `client.meetings.list()`. (beta) */
export interface ListMeetingsParams {
  /** Object slug or ID to filter by. Must be provided together with `linked_record_id`. */
  linked_object?: string;
  /** Record ID to filter by. Must be provided together with `linked_object`. */
  linked_record_id?: string;
  /**
   * One or more participant emails. Meetings that include at least one of the
   * provided emails as a participant are returned. Arrays are joined with commas.
   */
  participants?: string | string[];
  /** Sort order. Defaults to `start_asc`. */
  sort?: 'start_asc' | 'start_desc';
  /** Only meetings ending at or after this timestamp (inclusive). */
  ends_from?: string;
  /** Only meetings starting before this timestamp (exclusive). */
  starts_before?: string;
  /** IANA timezone for `ends_from`/`starts_before` when filtering all-day meetings. Defaults to UTC. */
  timezone?: string;
  /** Max meetings per page (1-200, default 50). */
  limit?: number;
  cursor?: string;
}

/** External reference used to consistently identify and de-duplicate meetings. */
export type MeetingExternalRef =
  | string
  | {
      ical_uid: string;
      provider: 'google' | 'microsoft';
      /** Required for recurring event exceptions, optional otherwise. */
      original_start_time?: string;
      is_recurring: boolean;
    };

/**
 * Parameters for `client.meetings.create()` (find-or-create). (alpha)
 *
 * When `is_all_day` is true, `start`/`end` must use `{ date }`; otherwise
 * `{ datetime, timezone? }`. `end` is exclusive (RFC 5545).
 */
export interface CreateMeetingParams {
  data: {
    title: string;
    description: string;
    start: { datetime: string; timezone?: string | null } | { date: string };
    end: { datetime: string; timezone?: string | null } | { date: string };
    is_all_day: boolean;
    /** Person and company records are auto-created/linked from participant emails. */
    participants: Array<{
      email_address: string;
      is_organizer: boolean;
      status: MeetingParticipantStatus;
    }>;
    /** Records to link. Participants' companies are also linked asynchronously. */
    linked_records?: Array<{
      object: string;
      record_id: string;
    }>;
    external_ref: MeetingExternalRef;
  };
}

// ---------------------------------------------------------------------------
// Call Recordings
// ---------------------------------------------------------------------------

export type CallRecordingStatus = 'processing' | 'completed' | 'failed';

/** A call recording attached to a meeting. (beta) */
export interface AttioCallRecording {
  id: { workspace_id: string; meeting_id: string; call_recording_id: string };
  /** `processing` on creation, transitions to `completed` or `failed`. */
  status: CallRecordingStatus;
  /** Link to the call recording in the Attio web application. */
  web_url: string;
  created_by_actor: ActorReference;
  created_at: string;
}

export interface ListCallRecordingsParams {
  limit?: number;
  cursor?: string;
}

/** Parameters for `client.callRecordings.create()`. (alpha) */
export interface CreateCallRecordingParams {
  data: {
    /**
     * Publicly accessible HTTPS URL to a `.mp4` video (max 500MB). Attio
     * downloads the video asynchronously and verifies the URL with a HEAD
     * request that must return a `Content-Length` header.
     */
    video_url: string;
  };
}

// ---------------------------------------------------------------------------
// Transcripts
// ---------------------------------------------------------------------------

export interface TranscriptSegment {
  speech: string;
  /** Start of this segment in seconds, measured from the start of the recording. */
  start_time: number;
  /** End of this segment in seconds, measured from the start of the recording. */
  end_time: number;
  speaker: { name: string };
}

/** A page of transcript for a call recording. (beta) */
export interface AttioTranscript {
  id: { workspace_id: string; meeting_id: string; call_recording_id: string };
  transcript: TranscriptSegment[];
}

export interface TranscriptResponse {
  data: AttioTranscript;
  pagination: {
    next_cursor: string | null;
  };
}

export interface GetTranscriptParams {
  cursor?: string;
}

// ---------------------------------------------------------------------------
// Self
// ---------------------------------------------------------------------------

export interface AttioSelfInfo {
  scope: string;
  workspace_id: string;
  workspace_name: string;
  workspace_slug: string;
  workspace_logo_url: string | null;
  authorized_by_workspace_member_id: string;
}

// ---------------------------------------------------------------------------
// Global Record Search
// ---------------------------------------------------------------------------

/**
 * The context in which to perform a search. Use `{ type: 'workspace' }` for
 * all results, or a workspace member to limit results to what that person can see.
 */
export type SearchRequestAs =
  | { type: 'workspace' }
  | { type: 'workspace-member'; workspace_member_id: string }
  | { type: 'workspace-member'; email_address: string };

/** Parameters for `client.records.globalSearch()`. (beta) */
export interface GlobalSearchParams {
  /** Query string (max 256 chars). An empty string returns a default set of results. */
  query: string;
  /** Object slugs or IDs to search. At least one object must be specified. */
  objects: string[];
  /** The context in which to perform the search. */
  request_as: SearchRequestAs;
  /** Max results to return (1-25, default 25). */
  limit?: number;
}

export interface GlobalSearchResult {
  id: { workspace_id: string; object_id: string; record_id: string };
  /** Human-readable label for the record. */
  record_text: string;
  record_image: string | null;
  object_slug: string;
  [key: string]: unknown;
}

// ---------------------------------------------------------------------------
// SQL
// ---------------------------------------------------------------------------

/** Response from `client.sql.query()`. (beta) */
export interface SqlQueryResponse {
  data: {
    /** One object per result row, keyed by the columns selected in the query. */
    rows: Array<Record<string, unknown>>;
  };
}

// ---------------------------------------------------------------------------
// Client Options
// ---------------------------------------------------------------------------

export interface AttioClientOptions {
  apiKey: string;
  baseUrl?: string;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
}

export interface RequestOptions {
  body?: unknown;
  params?: Record<string, string>;
  allowNotFound?: boolean;
  /**
   * Set to 'manual' for endpoints that respond with a redirect (e.g. file
   * downloads). Instead of following the redirect, the request resolves with
   * `{ url }` containing the Location header.
   */
  redirect?: 'manual';
}
