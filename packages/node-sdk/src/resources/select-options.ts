import type { HttpClient } from '../client.js';
import type {
  CreateSelectOptionParams,
  CreateStatusParams,
  ListResponse,
  SelectOption,
  StatusOption,
  UpdateStatusParams,
} from '../types.js';

type Target = 'objects' | 'lists';

export class SelectOptionsResource {
  constructor(private client: HttpClient) {}

  /** List select options for an attribute. */
  async list(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
  ): Promise<ListResponse<SelectOption>> {
    return this.client.request(
      'GET',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}/options`,
    );
  }

  /** Create a select option on an attribute. */
  async create(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
    params: CreateSelectOptionParams,
  ): Promise<{ data: SelectOption }> {
    return this.client.request(
      'POST',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}/options`,
      { body: { data: params } },
    );
  }

  /** Update a select option. */
  async update(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
    optionId: string,
    params: { title?: string; is_archived?: boolean },
  ): Promise<{ data: SelectOption }> {
    return this.client.request(
      'PATCH',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}/options/${optionId}`,
      { body: { data: params } },
    );
  }

  /** List statuses for a status attribute. */
  async listStatuses(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
  ): Promise<ListResponse<StatusOption>> {
    return this.client.request(
      'GET',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}/statuses`,
    );
  }

  /** Create a status on a status attribute. */
  async createStatus(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
    params: CreateStatusParams,
  ): Promise<{ data: StatusOption }> {
    return this.client.request(
      'POST',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}/statuses`,
      { body: { data: params } },
    );
  }

  /** Update a status. */
  async updateStatus(
    target: Target,
    targetIdOrSlug: string,
    attributeIdOrSlug: string,
    statusId: string,
    params: UpdateStatusParams,
  ): Promise<{ data: StatusOption }> {
    return this.client.request(
      'PATCH',
      `/${target}/${targetIdOrSlug}/attributes/${attributeIdOrSlug}/statuses/${statusId}`,
      { body: { data: params } },
    );
  }
}
