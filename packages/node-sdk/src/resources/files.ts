import type { HttpClient } from '../client.js';
import type {
  AttioFile,
  CreateFolderParams,
  ListFilesParams,
  PaginatedResponse,
  UploadFileParams,
} from '../types.js';

export class FilesResource {
  constructor(private client: HttpClient) {}

  /** List files, optionally filtered by object, record, folder, or storage provider. */
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

  /** Get a single file by ID. */
  async get(fileId: string): Promise<{ data: AttioFile }> {
    return this.client.request('GET', `/files/${fileId}`);
  }

  /** Create a folder. */
  async createFolder(params: CreateFolderParams): Promise<{ data: AttioFile }> {
    return this.client.request('POST', '/files', { body: params });
  }

  /**
   * Upload a file. Uses multipart/form-data via the HttpClient.requestFormData method.
   * Requires Node 18+ (FormData and Blob are globally available).
   */
  async upload(params: UploadFileParams): Promise<{ data: AttioFile }> {
    const formData = new FormData();

    if (params.file instanceof Blob) {
      formData.append('file', params.file);
    } else {
      // Buffer -> Blob for Node 18+
      formData.append('file', new Blob([params.file as unknown as BlobPart]));
    }

    formData.append('object', params.parent_record_object);
    formData.append('record_id', params.parent_record_record_id);
    if (params.parent_folder_id) {
      formData.append('parent_folder_id', params.parent_folder_id);
    }

    return this.client.requestFormData('/files/upload', formData);
  }

  /** Download a file. Returns the download URL or response. */
  async download(fileId: string): Promise<{ data: { url: string } }> {
    return this.client.request('GET', `/files/${fileId}/download`);
  }

  /** Delete a file or folder. */
  async delete(fileId: string): Promise<void> {
    await this.client.request('DELETE', `/files/${fileId}`);
  }
}
