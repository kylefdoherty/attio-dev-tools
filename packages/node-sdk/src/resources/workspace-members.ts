import type { HttpClient } from '../client.js';
import type { ListResponse, WorkspaceMember } from '../types.js';

export class WorkspaceMembersResource {
  constructor(private client: HttpClient) {}

  /** List all workspace members. */
  async list(): Promise<ListResponse<WorkspaceMember>> {
    return this.client.request('GET', '/workspace_members');
  }

  /** Get a single workspace member. */
  async get(memberId: string): Promise<{ data: WorkspaceMember }> {
    return this.client.request('GET', `/workspace_members/${memberId}`);
  }
}
