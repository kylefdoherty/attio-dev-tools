import type { HttpClient } from '../client.js';
import type {
  AttioObject,
  CreateObjectParams,
  ListResponse,
  UpdateObjectParams,
} from '../types.js';

export class ObjectsResource {
  constructor(private client: HttpClient) {}

  /** List all objects in the workspace. */
  async list(): Promise<ListResponse<AttioObject>> {
    return this.client.request('GET', '/objects');
  }

  /** Get a single object by slug or ID. */
  async get(objectIdOrSlug: string): Promise<{ data: AttioObject }> {
    return this.client.request('GET', `/objects/${objectIdOrSlug}`);
  }

  /** Create a new custom object. */
  async create(params: CreateObjectParams): Promise<{ data: AttioObject }> {
    return this.client.request('POST', '/objects', {
      body: { data: params },
    });
  }

  /** Update an object. */
  async update(objectIdOrSlug: string, params: UpdateObjectParams): Promise<{ data: AttioObject }> {
    return this.client.request('PUT', `/objects/${objectIdOrSlug}`, {
      body: { data: params },
    });
  }
}
