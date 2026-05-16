import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockTask } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('TasksResource', () => {
  it('list() → GET /tasks', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/tasks`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockTask] });
      }),
    );
    const result = await client.tasks.list();
    expect(url).toBe('/v2/tasks');
    expect(result.data).toHaveLength(1);
  });

  it('list() with filter params', async () => {
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/tasks`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.tasks.list({
      linked_object: 'deals',
      linked_record_id: 'rec_01abc',
      is_completed: false,
      assignee: 'wm_01abc',
    });
    expect(searchParams?.get('linked_object')).toBe('deals');
    expect(searchParams?.get('linked_record_id')).toBe('rec_01abc');
    expect(searchParams?.get('is_completed')).toBe('false');
    expect(searchParams?.get('assignee')).toBe('wm_01abc');
  });

  it('get() → GET /tasks/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/tasks/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockTask });
      }),
    );
    await client.tasks.get('task_01abc');
    expect(url).toBe('/v2/tasks/task_01abc');
  });

  it('create() → POST /tasks with body', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/tasks`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockTask });
      }),
    );
    await client.tasks.create({
      data: { content: 'Do something', format: 'plaintext' },
    });
    expect(method).toBe('POST');
    expect(body).toHaveProperty('data.content', 'Do something');
  });

  it('update() → PUT /tasks/:id with body', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.put(`${BASE}/tasks/:id`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockTask });
      }),
    );
    await client.tasks.update('task_01abc', {
      data: { is_completed: true },
    });
    expect(method).toBe('PUT');
    expect(url).toBe('/v2/tasks/task_01abc');
    expect(body).toHaveProperty('data.is_completed', true);
  });

  it('delete() -> DELETE /tasks/:id', async () => {
    let method = '';
    server.use(
      http.delete(`${BASE}/tasks/:id`, ({ request }) => {
        method = request.method;
        return HttpResponse.json({});
      }),
    );
    await client.tasks.delete('task_01abc');
    expect(method).toBe('DELETE');
  });

  it('response includes completed_at', async () => {
    const result = await client.tasks.get('task_01abc');
    expect(result.data).toHaveProperty('completed_at');
  });

  it('completed task has completed_at set', async () => {
    server.use(
      http.get(`${BASE}/tasks/:id`, () =>
        HttpResponse.json({
          data: { ...mockTask, is_completed: true, completed_at: '2024-06-01T00:00:00.000Z' },
        }),
      ),
    );
    const result = await client.tasks.get('task_01abc');
    expect(result.data.completed_at).toBe('2024-06-01T00:00:00.000Z');
    expect(result.data.is_completed).toBe(true);
  });
});
