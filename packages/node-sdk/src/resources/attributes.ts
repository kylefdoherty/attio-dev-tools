import type { HttpClient } from '../client.js';
import type {
  AttioAttribute,
  CreateAttributeParams,
  ListResponse,
  UpdateAttributeParams,
} from '../types.js';

type Target = 'objects' | 'lists';

export class AttributesResource {
  constructor(private client: HttpClient) {}

  /** List all attributes on an object or list. */
  async list(target: Target, targetIdOrSlug: string): Promise<ListResponse<AttioAttribute>> {
    return this.client.request('GET', `/${target}/${targetIdOrSlug}/attributes`);
  }

  /** Get a single attribute by slug or ID. */
  async get(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
  ): Promise<{ data: AttioAttribute }> {
    return this.client.request(
      'GET',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}`,
    );
  }

  /** Create a new attribute on an object or list. */
  async create(
    target: Target,
    targetIdOrSlug: string,
    params: CreateAttributeParams,
  ): Promise<{ data: AttioAttribute }> {
    return this.client.request('POST', `/${target}/${targetIdOrSlug}/attributes`, {
      body: { data: params },
    });
  }

  /** Update an attribute. */
  async update(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
    params: UpdateAttributeParams,
  ): Promise<{ data: AttioAttribute }> {
    return this.client.request(
      'PATCH',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}`,
      { body: { data: params } },
    );
  }
}
