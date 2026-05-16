import type { HttpClient } from '../client.js';
import type { AttioTask, CreateTaskParams, ListResponse, UpdateTaskParams } from '../types.js';

export class TasksResource {
  constructor(private client: HttpClient) {}

  /** List tasks. */
  async list(params?: {
    linked_object?: string;
    linked_record_id?: string;
    is_completed?: boolean;
    assignee?: string;
  }): Promise<ListResponse<AttioTask>> {
    const queryParams: Record<string, string> = {};
    if (params?.linked_object) queryParams.linked_object = params.linked_object;
    if (params?.linked_record_id) queryParams.linked_record_id = params.linked_record_id;
    if (params?.is_completed !== undefined) queryParams.is_completed = String(params.is_completed);
    if (params?.assignee) queryParams.assignee = params.assignee;
    return this.client.request('GET', '/tasks', { params: queryParams });
  }

  /** Get a single task. */
  async get(taskId: string): Promise<{ data: AttioTask }> {
    return this.client.request('GET', `/tasks/${taskId}`);
  }

  /** Create a task. */
  async create(params: CreateTaskParams): Promise<{ data: AttioTask }> {
    return this.client.request('POST', '/tasks', { body: params });
  }

  /** Update a task. */
  async update(taskId: string, params: UpdateTaskParams): Promise<{ data: AttioTask }> {
    return this.client.request('PUT', `/tasks/${taskId}`, { body: params });
  }

  /** Delete a task. */
  async delete(taskId: string): Promise<void> {
    await this.client.request('DELETE', `/tasks/${taskId}`);
  }
}
