import type { HttpClient } from '../client.js';
import type {
  AttioWebhook,
  CreateWebhookParams,
  ListResponse,
  UpdateWebhookParams,
} from '../types.js';

export class WebhooksResource {
  constructor(private client: HttpClient) {}

  /** List all webhooks. */
  async list(): Promise<ListResponse<AttioWebhook>> {
    return this.client.request('GET', '/webhooks');
  }

  /** Get a single webhook. */
  async get(webhookId: string): Promise<{ data: AttioWebhook }> {
    return this.client.request('GET', `/webhooks/${webhookId}`);
  }

  /** Create a webhook. */
  async create(params: CreateWebhookParams): Promise<{ data: AttioWebhook }> {
    return this.client.request('POST', '/webhooks', { body: params });
  }

  /** Update a webhook. */
  async update(webhookId: string, params: UpdateWebhookParams): Promise<{ data: AttioWebhook }> {
    return this.client.request('PUT', `/webhooks/${webhookId}`, {
      body: params,
    });
  }

  /** Delete a webhook. */
  async delete(webhookId: string): Promise<void> {
    await this.client.request('DELETE', `/webhooks/${webhookId}`);
  }
}
