import type { HttpClient } from '../client.js';
import type {
  AttioComment,
  AttioThread,
  CreateCommentParams,
  ListResponse,
  ListThreadsParams,
} from '../types.js';

export class CommentsResource {
  constructor(private client: HttpClient) {}

  /** Create a comment on a thread, record, or entry. */
  async create(params: CreateCommentParams): Promise<{ data: AttioComment }> {
    return this.client.request('POST', '/comments', { body: params });
  }

  /** Get a single comment. */
  async get(commentId: string): Promise<{ data: AttioComment }> {
    return this.client.request('GET', `/comments/${commentId}`);
  }

  /** Delete a comment. */
  async delete(commentId: string): Promise<void> {
    await this.client.request('DELETE', `/comments/${commentId}`);
  }

  /** Get a thread. */
  async getThread(threadId: string): Promise<{ data: AttioThread }> {
    return this.client.request('GET', `/threads/${threadId}`);
  }

  /** List threads for a record or entry. */
  async listThreads(params: ListThreadsParams): Promise<ListResponse<AttioThread>> {
    const queryParams: Record<string, string> = {};
    if (params.record_id) queryParams.record_id = params.record_id;
    if (params.object) queryParams.object = params.object;
    if (params.entry_id) queryParams.entry_id = params.entry_id;
    if (params.list) queryParams.list = params.list;
    return this.client.request('GET', '/threads', { params: queryParams });
  }
}
