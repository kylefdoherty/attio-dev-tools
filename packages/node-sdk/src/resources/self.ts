import type { HttpClient } from '../client.js';
import type { AttioSelfInfo } from '../types.js';

export class SelfResource {
  constructor(private client: HttpClient) {}

  /** Get information about the current API token and workspace. */
  async get(): Promise<{ data: AttioSelfInfo }> {
    return this.client.request('GET', '/self');
  }
}
