import type { HttpClient } from '../client.js';
import type { AttioList, CreateListParams, ListResponse, UpdateListParams } from '../types.js';

export class ListsResource {
  constructor(private client: HttpClient) {}

  /** List all lists in the workspace. */
  async list(): Promise<ListResponse<AttioList>> {
    return this.client.request('GET', '/lists');
  }

  /** Get a single list by slug or ID. */
  async get(listIdOrSlug: string): Promise<{ data: AttioList }> {
    return this.client.request('GET', `/lists/${listIdOrSlug}`);
  }

  /** Create a new list. */
  async create(params: CreateListParams): Promise<{ data: AttioList }> {
    return this.client.request('POST', '/lists', {
      body: { data: params },
    });
  }

  /** Update a list. */
  async update(listIdOrSlug: string, params: UpdateListParams): Promise<{ data: AttioList }> {
    return this.client.request('PATCH', `/lists/${listIdOrSlug}`, {
      body: { data: params },
    });
  }
}
