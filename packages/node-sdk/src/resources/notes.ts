import type { HttpClient } from '../client.js';
import type { AttioNote, CreateNoteParams, ListResponse } from '../types.js';

export class NotesResource {
  constructor(private client: HttpClient) {}

  /** List notes. Filter by parent_object and parent_record_id via params. */
  async list(params?: {
    parent_object?: string;
    parent_record_id?: string;
  }): Promise<ListResponse<AttioNote>> {
    const queryParams: Record<string, string> = {};
    if (params?.parent_object) queryParams.parent_object = params.parent_object;
    if (params?.parent_record_id) queryParams.parent_record_id = params.parent_record_id;
    return this.client.request('GET', '/notes', { params: queryParams });
  }

  /** Get a single note. */
  async get(noteId: string): Promise<{ data: AttioNote }> {
    return this.client.request('GET', `/notes/${noteId}`);
  }

  /** Create a note on a record. */
  async create(params: CreateNoteParams): Promise<{ data: AttioNote }> {
    return this.client.request('POST', '/notes', { body: params });
  }

  /** Delete a note. */
  async delete(noteId: string): Promise<void> {
    await this.client.request('DELETE', `/notes/${noteId}`);
  }
}
