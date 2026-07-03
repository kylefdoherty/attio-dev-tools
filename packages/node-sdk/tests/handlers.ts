import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const BASE = 'https://api.attio.com/v2';

// ---------------------------------------------------------------------------
// Mock data factories
// ---------------------------------------------------------------------------

export const mockObject = {
  id: { workspace_id: 'ws_01abc', object_id: 'obj_01abc' },
  api_slug: 'deals',
  singular_noun: 'Deal',
  plural_noun: 'Deals',
  description: null,
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockAttribute = {
  id: { attribute_id: 'attr_01abc' },
  api_slug: 'name',
  title: 'Name',
  type: 'text' as const,
  description: null,
  is_required: false,
  is_unique: false,
  is_multiselect: false,
  is_archived: false,
  is_system_attribute: false,
  config: {},
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockRecord = {
  id: { workspace_id: 'ws_01abc', record_id: 'rec_01abc', object_id: 'obj_01abc' },
  values: {},
  created_at: '2024-01-01T00:00:00.000Z',
  web_url: 'https://app.attio.com/people/rec_01abc',
};

export const mockList = {
  id: { workspace_id: 'ws_01abc', list_id: 'list_01abc' },
  api_slug: 'pipeline',
  name: 'Pipeline',
  parent_object: 'deals',
  workspace_access: 'full-access',
  workspace_member_access: 'full-access',
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockEntry = {
  id: { workspace_id: 'ws_01abc', entry_id: 'entry_01abc', list_id: 'list_01abc' },
  parent_object: 'deals',
  parent_record_id: 'rec_01abc',
  entry_values: {},
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockNote = {
  id: { workspace_id: 'ws_01abc', note_id: 'note_01abc' },
  parent_object: 'people',
  parent_record_id: 'rec_01abc',
  title: 'Test Note',
  content_plaintext: 'Hello world',
  content_markdown: null,
  meeting_id: null,
  tags: [],
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockTask = {
  id: { workspace_id: 'ws_01abc', task_id: 'task_01abc' },
  content_plaintext: 'Do something',
  is_completed: false,
  completed_at: null,
  deadline_at: null,
  linked_records: [],
  assignees: [],
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockWebhook = {
  id: { webhook_id: 'wh_01abc' },
  target_url: 'https://example.com/webhook',
  subscriptions: [{ event_type: 'record.created' }],
  status: 'active',
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockWorkspaceMember = {
  id: { workspace_member_id: 'wm_01abc' },
  first_name: 'Jane',
  last_name: 'Doe',
  email_address: 'jane@example.com',
  avatar_url: null,
  access_level: 'admin',
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockSelectOption = {
  id: {
    workspace_id: 'ws_01abc',
    object_id: 'obj_01abc',
    attribute_id: 'attr_01abc',
    option_id: 'opt_01abc',
  },
  title: 'Option A',
  is_archived: false,
};

export const mockStatus = {
  id: {
    workspace_id: 'ws_01abc',
    object_id: 'obj_01abc',
    attribute_id: 'attr_01abc',
    status_id: 'status_01abc',
  },
  title: 'In Progress',
  is_archived: false,
  celebration_enabled: false,
  target_time_in_status: null,
};

export const mockObjectView = {
  id: { workspace_id: 'ws_01abc', view_id: 'view_01abc', object_id: 'obj_01abc' },
  title: 'All People',
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockListView = {
  id: { workspace_id: 'ws_01abc', view_id: 'view_02abc', list_id: 'list_01abc' },
  title: 'Active Deals',
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockComment = {
  id: { comment_id: 'comment_01abc' },
  thread_id: 'thread_01abc',
  content_plaintext: 'Great update!',
  author: { type: 'workspace-member', id: 'wm_01abc' },
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
  resolved_at: null,
  resolved_by: null,
  record: { object: 'people', record_id: 'rec_01abc' },
  entry: null,
};

export const mockThread = {
  id: { thread_id: 'thread_01abc' },
  record_id: 'rec_01abc',
  record: { object: 'people', record_id: 'rec_01abc' },
  entry: null,
  comments: [mockComment],
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockFile = {
  id: { workspace_id: 'ws_01abc', file_id: 'file_01abc' },
  object_id: 'obj_01abc',
  object_slug: 'deals',
  record_id: 'rec_01abc',
  storage_provider: 'attio' as const,
  file_type: 'file' as const,
  name: 'report.pdf',
  content_type: 'application/pdf',
  content_size: 102400,
  parent_folder_id: null,
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockFolder = {
  id: { workspace_id: 'ws_01abc', file_id: 'file_02abc' },
  object_id: 'obj_01abc',
  object_slug: 'deals',
  record_id: 'rec_01abc',
  storage_provider: 'attio' as const,
  file_type: 'folder' as const,
  name: 'Documents',
  parent_folder_id: null,
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockConnectedFile = {
  id: { workspace_id: 'ws_01abc', file_id: 'file_03abc' },
  object_id: 'obj_01abc',
  object_slug: 'deals',
  record_id: 'rec_01abc',
  storage_provider: 'google-drive' as const,
  file_type: 'connected-file' as const,
  external_provider_file_id: 'gdrive_file_123',
  microsoft_drive_id: null,
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockMeeting = {
  id: { workspace_id: 'ws_01abc', meeting_id: 'meeting_01abc' },
  title: 'Quarterly Review',
  description: 'Q1 business review',
  is_all_day: false,
  start: { datetime: '2024-03-15T10:00:00.000-04:00', timezone: 'America/New_York' },
  end: { datetime: '2024-03-15T11:00:00.000-04:00', timezone: 'America/New_York' },
  participants: [
    { email_address: 'jane@example.com', is_organizer: true, status: 'accepted' as const },
  ],
  linked_records: [{ object_slug: 'deals', object_id: 'obj_01abc', record_id: 'rec_01abc' }],
  created_at: '2024-01-01T00:00:00.000Z',
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
};

export const mockCallRecording = {
  id: { workspace_id: 'ws_01abc', meeting_id: 'meeting_01abc', call_recording_id: 'cr_01abc' },
  status: 'completed' as const,
  web_url: 'https://app.attio.com/acme/calls/meeting_01abc/cr_01abc',
  created_by_actor: { type: 'workspace-member', id: 'wm_01abc' },
  created_at: '2024-01-01T00:00:00.000Z',
};

export const mockTranscriptSegment = {
  speech: 'Hello, welcome to the meeting.',
  start_time: 0,
  end_time: 3.5,
  speaker: { name: 'Jane Doe' },
};

export const mockTranscript = {
  id: { workspace_id: 'ws_01abc', meeting_id: 'meeting_01abc', call_recording_id: 'cr_01abc' },
  transcript: [mockTranscriptSegment],
};

export const mockSelfInfo = {
  scope: 'record_permission:read,object_configuration:read',
  workspace_id: 'ws_01abc',
  workspace_name: 'Acme Corp',
  workspace_slug: 'acme-corp',
  workspace_logo_url: null,
  authorized_by_workspace_member_id: 'wm_01abc',
};

export const mockGlobalSearchResult = {
  id: { workspace_id: 'ws_01abc', object_id: 'obj_01abc', record_id: 'rec_01abc' },
  record_text: 'Jane Doe',
  record_image: null,
  object_slug: 'people',
};

export const mockSqlRow = {
  record_id: 'rec_01abc',
  created_at: '2024-01-01T00:00:00.000Z',
  name: 'Acme Corp',
  domains: ['acme.com'],
};

// ---------------------------------------------------------------------------
// Default handlers -- each returns realistic mock data
// ---------------------------------------------------------------------------

export const handlers = [
  // Objects
  http.get(`${BASE}/objects`, () => HttpResponse.json({ data: [mockObject] })),
  http.get(`${BASE}/objects/:id`, () => HttpResponse.json({ data: mockObject })),
  http.post(`${BASE}/objects`, () => HttpResponse.json({ data: mockObject })),
  http.put(`${BASE}/objects/:id`, () => HttpResponse.json({ data: mockObject })),

  // Attributes (fixed: target/identifier prefix for get/create/update)
  http.get(`${BASE}/:target/:targetId/attributes/:attr`, () =>
    HttpResponse.json({ data: mockAttribute }),
  ),
  http.get(`${BASE}/:target/:targetId/attributes`, () =>
    HttpResponse.json({ data: [mockAttribute] }),
  ),
  http.post(`${BASE}/:target/:targetId/attributes`, () =>
    HttpResponse.json({ data: mockAttribute }),
  ),
  http.patch(`${BASE}/:target/:targetId/attributes/:attr`, () =>
    HttpResponse.json({ data: mockAttribute }),
  ),

  // Records
  http.get(`${BASE}/objects/:objId/records`, () => HttpResponse.json({ data: [mockRecord] })),
  http.post(`${BASE}/objects/:objId/records/query`, () =>
    HttpResponse.json({ data: [mockRecord] }),
  ),
  http.post(`${BASE}/objects/:objId/records/search`, () =>
    HttpResponse.json({ data: [mockRecord] }),
  ),
  http.get(`${BASE}/objects/:objId/records/:recId`, () =>
    HttpResponse.json({ data: mockRecord }),
  ),
  http.post(`${BASE}/objects/:objId/records`, () => HttpResponse.json({ data: mockRecord })),
  http.put(`${BASE}/objects/:objId/records/:recId`, () =>
    HttpResponse.json({ data: mockRecord }),
  ),
  http.patch(`${BASE}/objects/:objId/records/:recId`, () =>
    HttpResponse.json({ data: mockRecord }),
  ),
  http.delete(`${BASE}/objects/:objId/records/:recId`, () =>
    HttpResponse.json({}),
  ),
  // Fixed: attribute-values -> attributes/:attrId/values
  http.get(`${BASE}/objects/:objId/records/:recId/attributes/:attrId/values`, () =>
    HttpResponse.json({ data: [] }),
  ),
  http.get(`${BASE}/objects/:objId/records/:recId/entries`, () =>
    HttpResponse.json({ data: [mockEntry] }),
  ),

  // Lists
  http.get(`${BASE}/lists`, () => HttpResponse.json({ data: [mockList] })),
  http.get(`${BASE}/lists/:id`, () => HttpResponse.json({ data: mockList })),
  http.post(`${BASE}/lists`, () => HttpResponse.json({ data: mockList })),
  http.patch(`${BASE}/lists/:id`, () => HttpResponse.json({ data: mockList })),

  // Entries
  http.get(`${BASE}/lists/:listId/entries`, () => HttpResponse.json({ data: [mockEntry] })),
  http.post(`${BASE}/lists/:listId/entries/query`, () =>
    HttpResponse.json({ data: [mockEntry] }),
  ),
  http.get(`${BASE}/lists/:listId/entries/:entryId`, () =>
    HttpResponse.json({ data: mockEntry }),
  ),
  http.post(`${BASE}/lists/:listId/entries`, () => HttpResponse.json({ data: mockEntry })),
  http.put(`${BASE}/lists/:listId/entries/:entryId`, () =>
    HttpResponse.json({ data: mockEntry }),
  ),
  http.patch(`${BASE}/lists/:listId/entries/:entryId`, () =>
    HttpResponse.json({ data: mockEntry }),
  ),
  http.delete(`${BASE}/lists/:listId/entries/:entryId`, () => HttpResponse.json({})),
  // Fixed: attribute-values -> attributes/:attrId/values
  http.get(`${BASE}/lists/:listId/entries/:entryId/attributes/:attrId/values`, () =>
    HttpResponse.json({ data: [] }),
  ),

  // Notes
  http.get(`${BASE}/notes`, () => HttpResponse.json({ data: [mockNote] })),
  http.get(`${BASE}/notes/:id`, () => HttpResponse.json({ data: mockNote })),
  http.post(`${BASE}/notes`, () => HttpResponse.json({ data: mockNote })),
  http.delete(`${BASE}/notes/:id`, () => HttpResponse.json({})),

  // Tasks
  http.get(`${BASE}/tasks`, () => HttpResponse.json({ data: [mockTask] })),
  http.get(`${BASE}/tasks/:id`, () => HttpResponse.json({ data: mockTask })),
  http.post(`${BASE}/tasks`, () => HttpResponse.json({ data: mockTask })),
  http.put(`${BASE}/tasks/:id`, () => HttpResponse.json({ data: mockTask })),
  http.delete(`${BASE}/tasks/:id`, () => HttpResponse.json({})),

  // Webhooks
  http.get(`${BASE}/webhooks`, () => HttpResponse.json({ data: [mockWebhook] })),
  http.get(`${BASE}/webhooks/:id`, () => HttpResponse.json({ data: mockWebhook })),
  http.post(`${BASE}/webhooks`, () => HttpResponse.json({ data: mockWebhook })),
  http.put(`${BASE}/webhooks/:id`, () => HttpResponse.json({ data: mockWebhook })),
  http.delete(`${BASE}/webhooks/:id`, () => HttpResponse.json({})),

  // Workspace Members
  http.get(`${BASE}/workspace_members`, () =>
    HttpResponse.json({ data: [mockWorkspaceMember] }),
  ),
  http.get(`${BASE}/workspace_members/:id`, () =>
    HttpResponse.json({ data: mockWorkspaceMember }),
  ),

  // Select Options (fixed: target/identifier prefix, /options not /select-options, PATCH not PUT)
  http.get(`${BASE}/:target/:identifier/attributes/:attr/options`, () =>
    HttpResponse.json({ data: [mockSelectOption] }),
  ),
  http.post(`${BASE}/:target/:identifier/attributes/:attr/options`, () =>
    HttpResponse.json({ data: mockSelectOption }),
  ),
  http.patch(`${BASE}/:target/:identifier/attributes/:attr/options/:opt`, () =>
    HttpResponse.json({ data: mockSelectOption }),
  ),
  http.get(`${BASE}/:target/:identifier/attributes/:attr/statuses`, () =>
    HttpResponse.json({ data: [mockStatus] }),
  ),
  http.post(`${BASE}/:target/:identifier/attributes/:attr/statuses`, () =>
    HttpResponse.json({ data: mockStatus }),
  ),
  http.patch(`${BASE}/:target/:identifier/attributes/:attr/statuses/:status`, () =>
    HttpResponse.json({ data: mockStatus }),
  ),

  // Views
  http.get(`${BASE}/objects/:objectId/views`, () =>
    HttpResponse.json({ data: [mockObjectView], pagination: { next_cursor: null } }),
  ),
  http.get(`${BASE}/lists/:listId/views`, () =>
    HttpResponse.json({ data: [mockListView], pagination: { next_cursor: null } }),
  ),

  // Comments & Threads
  http.post(`${BASE}/comments`, () => HttpResponse.json({ data: mockComment })),
  http.get(`${BASE}/comments/:id`, () => HttpResponse.json({ data: mockComment })),
  http.delete(`${BASE}/comments/:id`, () => HttpResponse.json({})),
  http.get(`${BASE}/threads/:id`, () => HttpResponse.json({ data: mockThread })),
  http.get(`${BASE}/threads`, () =>
    HttpResponse.json({ data: [mockThread] }),
  ),

  // Files
  http.get(`${BASE}/files`, () =>
    HttpResponse.json({ data: [mockFile], pagination: { next_cursor: null } }),
  ),
  http.get(
    `${BASE}/files/:fileId/download`,
    () =>
      new HttpResponse(null, {
        status: 302,
        headers: { Location: 'https://storage.example.com/file.pdf?signature=abc' },
      }),
  ),
  http.get(`${BASE}/files/:fileId`, () => HttpResponse.json({ data: mockFile })),
  http.post(`${BASE}/files/upload`, () => HttpResponse.json({ data: mockFile })),
  http.post(`${BASE}/files`, () => HttpResponse.json({ data: mockFolder })),
  http.delete(`${BASE}/files/:fileId`, () => HttpResponse.json({})),

  // Meetings
  http.get(`${BASE}/meetings`, () =>
    HttpResponse.json({ data: [mockMeeting], pagination: { next_cursor: null } }),
  ),
  http.post(`${BASE}/meetings`, () => HttpResponse.json({ data: mockMeeting })),
  http.get(`${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`, () =>
    HttpResponse.json({ data: mockTranscript, pagination: { next_cursor: null } }),
  ),
  http.get(`${BASE}/meetings/:meetingId/call_recordings/:crId`, () =>
    HttpResponse.json({ data: mockCallRecording }),
  ),
  http.delete(`${BASE}/meetings/:meetingId/call_recordings/:crId`, () =>
    new HttpResponse(null, { status: 204 }),
  ),
  http.get(`${BASE}/meetings/:meetingId/call_recordings`, () =>
    HttpResponse.json({ data: [mockCallRecording], pagination: { next_cursor: null } }),
  ),
  http.post(`${BASE}/meetings/:meetingId/call_recordings`, () =>
    HttpResponse.json({ data: mockCallRecording }),
  ),
  http.get(`${BASE}/meetings/:meetingId`, () =>
    HttpResponse.json({ data: mockMeeting }),
  ),

  // Self
  http.get(`${BASE}/self`, () => HttpResponse.json({ data: mockSelfInfo })),

  // Global Record Search
  http.post(`${BASE}/objects/records/search`, () =>
    HttpResponse.json({ data: [mockGlobalSearchResult] }),
  ),

  // SQL
  http.post(`${BASE}/sql`, () => HttpResponse.json({ data: { rows: [mockSqlRow] } })),
];

export const server = setupServer(...handlers);
