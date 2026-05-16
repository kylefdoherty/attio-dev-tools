import type { HttpClient } from '../client.js';
import type {
  UpsertRecordParams,
  AttioEntry,
  AttioRecord,
  AttributeValue,
  CreateRecordParams,
  GlobalSearchParams,
  GlobalSearchResult,
  ListResponse,
  RecordQueryParams,
  UpdateRecordParams,
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

  /** Query records with filters and sorting. */
  async query(
    objectIdOrSlug: string,
    params?: RecordQueryParams,
  ): Promise<ListResponse<AttioRecord>> {
    return this.client.request('POST', `/objects/${objectIdOrSlug}/records/query`, {
      body: params ?? {},
    });
  }

  /** Search records by text. */
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
  ): Promise<{ data: AttioRecord}> {
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

  /** Search across all object records globally. */
  async globalSearch(params: GlobalSearchParams): Promise<ListResponse<GlobalSearchResult>> {
    return this.client.request('POST', '/objects/records/search', {
      body: params,
    });
  }
}
