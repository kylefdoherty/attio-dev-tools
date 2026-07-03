import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateOffset } from '../pagination.js';
import type {
  AttioEntry,
  AttributeValue,
  CreateEntryParams,
  EntryQueryParams,
  ListResponse,
  UpdateEntryParams,
  UpsertEntryParams,
} from '../types.js';

export class EntriesResource {
  constructor(private client: HttpClient) {}

  /** List entries in a list. */
  async list(
    listIdOrSlug: string,
    params?: { limit?: number; offset?: number },
  ): Promise<ListResponse<AttioEntry>> {
    const queryParams: Record<string, string> = {};
    if (params?.limit) queryParams.limit = String(params.limit);
    if (params?.offset) queryParams.offset = String(params.offset);
    return this.client.request('GET', `/lists/${listIdOrSlug}/entries`, { params: queryParams });
  }

  /**
   * Query entries with filters.
   *
   * `filter` and `filter_view_id` are mutually exclusive — provide at most one.
   */
  async query(listIdOrSlug: string, params?: EntryQueryParams): Promise<ListResponse<AttioEntry>> {
    if (params?.filter !== undefined && params?.filter_view_id !== undefined) {
      throw new TypeError(
        '`filter` and `filter_view_id` are mutually exclusive — provide at most one.',
      );
    }
    return this.client.request('POST', `/lists/${listIdOrSlug}/entries/query`, {
      body: params ?? {},
    });
  }

  /** Get a single entry. */
  async get(listIdOrSlug: string, entryId: string): Promise<{ data: AttioEntry }> {
    return this.client.request('GET', `/lists/${listIdOrSlug}/entries/${entryId}`);
  }

  /** Create a new entry in a list. */
  async create(listIdOrSlug: string, params: CreateEntryParams): Promise<{ data: AttioEntry }> {
    return this.client.request('POST', `/lists/${listIdOrSlug}/entries`, { body: params });
  }

  /** Update an entry (overwrite multiselect values). */
  async update(
    listIdOrSlug: string,
    entryId: string,
    params: UpdateEntryParams,
  ): Promise<{ data: AttioEntry }> {
    return this.client.request('PUT', `/lists/${listIdOrSlug}/entries/${entryId}`, {
      body: params,
    });
  }

  /** Update an entry (append to multiselect values). */
  async append(
    listIdOrSlug: string,
    entryId: string,
    params: UpdateEntryParams,
  ): Promise<{ data: AttioEntry }> {
    return this.client.request('PATCH', `/lists/${listIdOrSlug}/entries/${entryId}`, {
      body: params,
    });
  }

  /** Delete an entry. */
  async delete(listIdOrSlug: string, entryId: string): Promise<void> {
    await this.client.request('DELETE', `/lists/${listIdOrSlug}/entries/${entryId}`);
  }

  /** Upsert an entry by parent record (create or update). */
  async upsert(listIdOrSlug: string, params: UpsertEntryParams): Promise<{ data: AttioEntry }> {
    return this.client.request('PUT', `/lists/${listIdOrSlug}/entries`, { body: params });
  }

  /** Get attribute values for a specific entry. */
  async getAttributeValues(
    listIdOrSlug: string,
    entryId: string,
    attributeIdOrSlug: string,
    options?: { showHistoric?: boolean },
  ): Promise<ListResponse<AttributeValue>> {
    const params: Record<string, string> = {};
    if (options?.showHistoric) params.show_historic = 'true';
    return this.client.request(
      'GET',
      `/lists/${listIdOrSlug}/entries/${entryId}/attributes/${attributeIdOrSlug}/values`,
      { params },
    );
  }

  /**
   * Auto-paginating query that yields individual entries.
   * Wraps query() and automatically fetches subsequent pages.
   *
   * @example
   * ```ts
   * for await (const entry of client.entries.queryAll('pipeline', {
   *   filter: { status: { $eq: 'active' } },
   * })) {
   *   console.log(entry.id.entry_id);
   * }
   * ```
   */
  queryAll(
    listIdOrSlug: string,
    params?: Omit<EntryQueryParams, 'limit' | 'offset'>,
    options?: PaginateOptions,
  ): AsyncIterable<AttioEntry> {
    return paginateOffset(
      (limit, offset) => this.query(listIdOrSlug, { ...params, limit, offset }),
      options,
    );
  }

  /**
   * Auto-paginating list that yields individual entries.
   * Wraps list() and automatically fetches subsequent pages.
   *
   * @example
   * ```ts
   * for await (const entry of client.entries.listAll('pipeline')) {
   *   console.log(entry.id.entry_id);
   * }
   * ```
   */
  listAll(listIdOrSlug: string, options?: PaginateOptions): AsyncIterable<AttioEntry> {
    return paginateOffset((limit, offset) => this.list(listIdOrSlug, { limit, offset }), options);
  }
}
