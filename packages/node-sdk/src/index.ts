import { HttpClient } from './client.js';
import { AttributesResource } from './resources/attributes.js';
import { CallRecordingsResource } from './resources/call-recordings.js';
import { CommentsResource } from './resources/comments.js';
import { EntriesResource } from './resources/entries.js';
import { FilesResource } from './resources/files.js';
import { ListsResource } from './resources/lists.js';
import { MeetingsResource } from './resources/meetings.js';
import { NotesResource } from './resources/notes.js';
import { ObjectsResource } from './resources/objects.js';
import { RecordsResource } from './resources/records.js';
import { SelectOptionsResource } from './resources/select-options.js';
import { SelfResource } from './resources/self.js';
import { TasksResource } from './resources/tasks.js';
import { TranscriptsResource } from './resources/transcripts.js';
import { ViewsResource } from './resources/views.js';
import { WebhooksResource } from './resources/webhooks.js';
import { WorkspaceMembersResource } from './resources/workspace-members.js';
import type { AttioClientOptions } from './types.js';

export class AttioClient {
  /** Manage objects (People, Companies, Deals, custom objects, etc.). */
  readonly objects: ObjectsResource;

  /** Manage attributes on objects and lists. */
  readonly attributes: AttributesResource;

  /** Query, create, update, and delete records. */
  readonly records: RecordsResource;

  /** Manage lists (pipelines, workflows, etc.). */
  readonly lists: ListsResource;

  /** Manage list entries. */
  readonly entries: EntriesResource;

  /** Create and manage notes on records. */
  readonly notes: NotesResource;

  /** Create and manage tasks. */
  readonly tasks: TasksResource;

  /** Manage webhook subscriptions. */
  readonly webhooks: WebhooksResource;

  /** List and get workspace members. */
  readonly workspaceMembers: WorkspaceMembersResource;

  /** Manage select options and statuses on attributes. */
  readonly selectOptions: SelectOptionsResource;

  /** List saved views on objects and lists. */
  readonly views: ViewsResource;

  /** Manage comments and threads on records. */
  readonly comments: CommentsResource;

  /** Manage files and folders attached to records. */
  readonly files: FilesResource;

  /** List and get meetings. */
  readonly meetings: MeetingsResource;

  /** List and get call recordings on meetings. */
  readonly callRecordings: CallRecordingsResource;

  /** Get transcripts for call recordings. */
  readonly transcripts: TranscriptsResource;

  /** Get information about the current API token and workspace. */
  readonly self: SelfResource;

  /** Low-level HTTP client for custom requests. */
  readonly http: HttpClient;

  constructor(options: AttioClientOptions) {
    this.http = new HttpClient(options);
    this.objects = new ObjectsResource(this.http);
    this.attributes = new AttributesResource(this.http);
    this.records = new RecordsResource(this.http);
    this.lists = new ListsResource(this.http);
    this.entries = new EntriesResource(this.http);
    this.notes = new NotesResource(this.http);
    this.tasks = new TasksResource(this.http);
    this.webhooks = new WebhooksResource(this.http);
    this.workspaceMembers = new WorkspaceMembersResource(this.http);
    this.selectOptions = new SelectOptionsResource(this.http);
    this.views = new ViewsResource(this.http);
    this.comments = new CommentsResource(this.http);
    this.files = new FilesResource(this.http);
    this.meetings = new MeetingsResource(this.http);
    this.callRecordings = new CallRecordingsResource(this.http);
    this.transcripts = new TranscriptsResource(this.http);
    this.self = new SelfResource(this.http);
  }
}

// Re-export everything
export { HttpClient } from './client.js';
export { AttioError, RateLimitError, ScopeError } from './errors.js';
export type { PaginateOptions } from './pagination.js';
export { collectAll, paginateCursor, paginateOffset } from './pagination.js';
export type * from './types.js';
export { verifyWebhookSignature, WebhookEventType } from './webhook-utils.js';
