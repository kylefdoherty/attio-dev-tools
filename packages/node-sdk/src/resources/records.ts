import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateOffset } from '../pagination.js';
import type {
  AttioEntry,
  AttioRecord,
  AttributeValue,
  CreateRecordParams,
  GlobalSearchParams,
  GlobalSearchResult,
  ListResponse,
  RecordQueryParams,
  UpdateRecordParams,
  UpsertRecordParams,
} from '../types.js';

export class RecordsResource {
  constructor(private client: HttpClient) {}

  /** List records on an object. */
  async list(
    objectIdOrSlug: string,
    params?: { limit?: number; offset?: number },
  ): Promise<ListResponse<AttioRecord>> {
    const queryParams: Record<string, string> = {};
    if (params?.limit) queryParams.limit = String(params.limit);
    if (params?.offset) queryParams.offset = String(params.offset);
    return this.client.request('GET', `/objects/${objectIdOrSlug}/records`, {
      params: queryParams,
    });
  }

  /**
   * Query records with filters and sorting.
   *
   * `filter` and `filter_view_id` are mutually exclusive — provide at most one.
   */
  async query(
    objectIdOrSlug: string,
    params?: RecordQueryParams,
  ): Promise<ListResponse<AttioRecord>> {
    if (params?.filter !== undefined && params?.filter_view_id !== undefined) {
      throw new TypeError(
        '`filter` and `filter_view_id` are mutually exclusive — provide at most one.',
      );
    }
    return this.client.request('POST', `/objects/${objectIdOrSlug}/records/query`, {
      body: params ?? {},
    });
  }

  /**
   * Search records by text on a single object.
   *
   * @deprecated This per-object endpoint is not part of the documented Attio
   * API. Use {@link globalSearch} (POST /objects/records/search) instead.
   */
  async search(
    objectIdOrSlug: string,
    params: { query: string; limit?: number },
  ): Promise<ListResponse<AttioRecord>> {
    return this.client.request('POST', `/objects/${objectIdOrSlug}/records/search`, {
      body: params,
    });
  }

  /** Get a single record by ID. */
  async get(objectIdOrSlug: string, recordId: string): Promise<{ data: AttioRecord }> {
    return this.client.request('GET', `/objects/${objectIdOrSlug}/records/${recordId}`);
  }

  /** Create a new record. */
  async create(objectIdOrSlug: string, params: CreateRecordParams): Promise<{ data: AttioRecord }> {
    return this.client.request('POST', `/objects/${objectIdOrSlug}/records`, { body: params });
  }

  /** Update a record (overwrite multiselect values). */
  async update(
    objectIdOrSlug: string,
    recordId: string,
    params: UpdateRecordParams,
  ): Promise<{ data: AttioRecord }> {
    return this.client.request('PUT', `/objects/${objectIdOrSlug}/records/${recordId}`, {
      body: params,
    });
  }

  /** Update a record (append to multiselect values). */
  async append(
    objectIdOrSlug: string,
    recordId: string,
    params: UpdateRecordParams,
  ): Promise<{ data: AttioRecord }> {
    return this.client.request('PATCH', `/objects/${objectIdOrSlug}/records/${recordId}`, {
      body: params,
    });
  }

  /** Delete a record. */
  async delete(objectIdOrSlug: string, recordId: string): Promise<void> {
    await this.client.request('DELETE', `/objects/${objectIdOrSlug}/records/${recordId}`);
  }

  /** Upsert a record by matching attribute (create or update). */
  async upsert(objectIdOrSlug: string, params: UpsertRecordParams): Promise<{ data: AttioRecord }> {
    return this.client.request('PUT', `/objects/${objectIdOrSlug}/records`, { body: params });
  }

  /** Get attribute values for a specific record and attribute. */
  async getAttributeValues(
    objectIdOrSlug: string,
    recordId: string,
    attributeIdOrSlug: string,
    options?: { showHistoric?: boolean },
  ): Promise<ListResponse<AttributeValue>> {
    const params: Record<string, string> = {};
    if (options?.showHistoric) params.show_historic = 'true';
    return this.client.request(
      'GET',
      `/objects/${objectIdOrSlug}/records/${recordId}/attributes/${attributeIdOrSlug}/values`,
      { params },
    );
  }

  /** List entries for a record (across all lists). */
  async listEntries(objectIdOrSlug: string, recordId: string): Promise<ListResponse<AttioEntry>> {
    return this.client.request('GET', `/objects/${objectIdOrSlug}/records/${recordId}/entries`);
  }

  /**
   * Fuzzy search for records across one or more objects. (beta)
   *
   * Matches names, domains, emails, phone numbers, and social handles on
   * people and companies, and labels on other records. Results are
   * eventually consistent (use query() when strong consistency matters).
   * `objects` and `request_as` are required by the API.
   */
  async globalSearch(params: GlobalSearchParams): Promise<ListResponse<GlobalSearchResult>> {
    return this.client.request('POST', '/objects/records/search', {
      body: params,
    });
  }

  /**
   * Auto-paginating query that yields individual records.
   * Wraps query() and automatically fetches subsequent pages.
   *
   * @example
   * ```ts
   * for await (const record of client.records.queryAll('people', {
   *   filter: { name: { $contains: 'Jane' } },
   * })) {
   *   console.log(record.id.record_id);
   * }
   * ```
   */
  queryAll(
    objectIdOrSlug: string,
    params?: Omit<RecordQueryParams, 'limit' | 'offset'>,
    options?: PaginateOptions,
  ): AsyncIterable<AttioRecord> {
    return paginateOffset(
      (limit, offset) => this.query(objectIdOrSlug, { ...params, limit, offset }),
      options,
    );
  }

  /**
   * Auto-paginating list that yields individual records.
   * Wraps list() and automatically fetches subsequent pages.
   *
   * @example
   * ```ts
   * for await (const record of client.records.listAll('people')) {
   *   console.log(record.id.record_id);
   * }
   * ```
   */
  listAll(objectIdOrSlug: string, options?: PaginateOptions): AsyncIterable<AttioRecord> {
    return paginateOffset((limit, offset) => this.list(objectIdOrSlug, { limit, offset }), options);
  }
}
