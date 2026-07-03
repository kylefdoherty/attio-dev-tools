import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateCursor } from '../pagination.js';
import type {
  AttioFile,
  CreateConnectedFileParams,
  CreateFolderParams,
  ListFilesParams,
  PaginatedResponse,
  UploadFileParams,
} from '../types.js';

export class FilesResource {
  constructor(private client: HttpClient) {}

  /**
   * List files, optionally filtered by object, record, folder, or storage provider. (beta)
   *
   * Cursor-paginated: pass `cursor` from `pagination.next_cursor` to fetch the
   * next page, or use {@link listAll} to iterate automatically.
   */
  async list(params?: ListFilesParams): Promise<PaginatedResponse<AttioFile>> {
    const queryParams: Record<string, string> = {};
    if (params?.object) queryParams.object = params.object;
    if (params?.record_id) queryParams.record_id = params.record_id;
    if (params?.parent_folder_id) queryParams.parent_folder_id = params.parent_folder_id;
    if (params?.storage_provider) queryParams.storage_provider = params.storage_provider;
    if (params?.limit != null) queryParams.limit = String(params.limit);
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request('GET', '/files', { params: queryParams });
  }

  /** Get a single file by ID. (beta) */
  async get(fileId: string): Promise<{ data: AttioFile }> {
    return this.client.request('GET', `/files/${fileId}`);
  }

  /** Create a native Attio folder on a record. (beta) */
  async createFolder(params: CreateFolderParams): Promise<{ data: AttioFile }> {
    return this.client.request('POST', '/files', {
      body: { ...params, file_type: 'folder' },
    });
  }

  /**
   * Link a file or folder from an external storage provider
   * (Dropbox, Box, Google Drive, or Microsoft OneDrive) to a record. (beta)
   */
  async createConnected(params: CreateConnectedFileParams): Promise<{ data: AttioFile }> {
    return this.client.request('POST', '/files', { body: params });
  }

  /**
   * Upload a file (max 50 MB) to native Attio storage for a record. (beta)
   *
   * Sends multipart/form-data via HttpClient.requestFormData.
   * Requires Node 18+ (FormData and Blob are globally available).
   */
  async upload(params: UploadFileParams): Promise<{ data: AttioFile }> {
    const formData = new FormData();

    const blob =
      params.file instanceof Blob
        ? params.file
        : // Buffer -> Blob for Node 18+
          new Blob([params.file as unknown as BlobPart]);

    if (params.filename) {
      formData.append('file', blob, params.filename);
    } else {
      formData.append('file', blob);
    }

    formData.append('object', params.object);
    formData.append('record_id', params.record_id);
    if (params.parent_folder_id) {
      formData.append('parent_folder_id', params.parent_folder_id);
    }

    return this.client.requestFormData('/files/upload', formData);
  }

  /**
   * Get a signed download URL for a file. (beta)
   *
   * The API responds with a 302 redirect to a signed URL. The SDK does not
   * follow the redirect; it returns the signed URL so you can fetch it
   * however you like (the URL is short-lived).
   */
  async download(fileId: string): Promise<{ url: string }> {
    return this.client.request('GET', `/files/${fileId}/download`, { redirect: 'manual' });
  }

  /** Delete a file or folder. (beta) */
  async delete(fileId: string): Promise<void> {
    await this.client.request('DELETE', `/files/${fileId}`);
  }

  /**
   * Auto-paginating list that yields individual files. (beta)
   * Wraps list() and automatically follows `pagination.next_cursor`.
   *
   * @example
   * ```ts
   * for await (const file of client.files.listAll({ object: 'deals', record_id: recordId })) {
   *   console.log(file.name);
   * }
   * ```
   */
  listAll(
    params?: Omit<ListFilesParams, 'limit' | 'cursor'>,
    options?: PaginateOptions,
  ): AsyncIterable<AttioFile> {
    return paginateCursor(
      (cursor) => this.list({ ...params, limit: options?.pageSize, cursor }),
      options,
    );
  }
}
