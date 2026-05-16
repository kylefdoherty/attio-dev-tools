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
  filter?: Record<string, unknown>;
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
  filter?: Record<string, unknown>;
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

export interface AttioFile {
  id: { file_id: string };
  name: string;
  type: 'file' | 'folder';
  mime_type: string | null;
  size: number | null;
  parent_record: {
    object: string;
    record_id: string;
  };
  parent_folder_id: string | null;
  storage_provider: string | null;
  created_by_actor: ActorReference;
  created_at: string;
}

export interface ListFilesParams {
  object?: string;
  record_id?: string;
  parent_folder_id?: string;
  storage_provider?: string;
  limit?: number;
  cursor?: string;
}

export interface CreateFolderParams {
  data: {
    name: string;
    parent_record: {
      object: string;
      record_id: string;
    };
    parent_folder_id?: string;
    storage_provider?: string;
  };
}

export interface UploadFileParams {
  file: Blob | Buffer;
  parent_record_object: string;
  parent_record_record_id: string;
  parent_folder_id?: string;
  storage_provider?: string;
}

// ---------------------------------------------------------------------------
// Meetings
// ---------------------------------------------------------------------------

export interface AttioMeeting {
  id: { meeting_id: string };
  title: string;
  description: string | null;
  is_all_day: boolean;
  start: {
    date: string;
    time: string | null;
    timezone: string | null;
  };
  end: {
    date: string;
    time: string | null;
    timezone: string | null;
  };
  participants: Array<{
    email_address: string;
    is_organizer: boolean;
    response_status: string | null;
  }>;
  linked_records: Array<{
    target_object: string;
    target_record_id: string;
  }>;
  created_at: string;
}

export interface ListMeetingsParams {
  linked_record_id?: string;
  linked_object?: string;
  participant_email?: string;
  start_date?: string;
  end_date?: string;
  timezone?: string;
  limit?: number;
  cursor?: string;
}

// ---------------------------------------------------------------------------
// Call Recordings
// ---------------------------------------------------------------------------

export interface AttioCallRecording {
  id: { call_recording_id: string };
  status: string;
  web_url: string | null;
  actor: ActorReference | null;
  created_at: string;
}

export interface ListCallRecordingsParams {
  limit?: number;
  cursor?: string;
}

// ---------------------------------------------------------------------------
// Transcripts
// ---------------------------------------------------------------------------

export interface TranscriptSegment {
  speech: string;
  start_time: number;
  end_time: number;
  speaker: {
    name: string | null;
    email_address: string | null;
  } | null;
}

export interface AttioTranscript {
  data: TranscriptSegment[];
  pagination: {
    next_cursor: string | null;
  };
}

export interface ListTranscriptParams {
  limit?: number;
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

export interface GlobalSearchParams {
  query: string;
  objects?: string[];
  limit?: number;
}

export interface GlobalSearchResult {
  record_id: string;
  object_id: string;
  object_slug: string;
  record_text: string;
  record_image: string | null;
  [key: string]: unknown;
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
}
