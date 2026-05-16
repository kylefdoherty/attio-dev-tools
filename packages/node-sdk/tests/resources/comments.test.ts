import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockComment, mockThread } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('CommentsResource', () => {
  it('create() on thread → POST /comments with author and thread_id', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/comments`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockComment });
      }),
    );
    await client.comments.create({
      data: {
        thread_id: 'thread_01abc',
        format: 'plaintext',
        content: 'Hello',
        author: { type: 'workspace-member', id: 'wm_01abc' },
      },
    });
    expect(method).toBe('POST');
    expect(body).toHaveProperty('data.content', 'Hello');
    expect(body).toHaveProperty('data.author.type', 'workspace-member');
  });

  it('create() on record → POST /comments with record object', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/comments`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: mockComment });
      }),
    );
    await client.comments.create({
      data: {
        record: { object: 'people', record_id: 'rec_01abc' },
        format: 'plaintext',
        content: 'Note on record',
        author: { type: 'workspace-member', id: 'wm_01abc' },
      },
    });
    expect(body).toHaveProperty('data.record.object', 'people');
    expect(body).toHaveProperty('data.record.record_id', 'rec_01abc');
  });

  it('create() on entry → POST /comments with entry object', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/comments`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: mockComment });
      }),
    );
    await client.comments.create({
      data: {
        entry: { list: 'pipeline', entry_id: 'entry_01abc' },
        format: 'plaintext',
        content: 'Note on entry',
        author: { type: 'workspace-member', id: 'wm_01abc' },
      },
    });
    expect(body).toHaveProperty('data.entry.list', 'pipeline');
    expect(body).toHaveProperty('data.entry.entry_id', 'entry_01abc');
  });

  it('get() → GET /comments/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/comments/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockComment });
      }),
    );
    const result = await client.comments.get('comment_01abc');
    expect(url).toBe('/v2/comments/comment_01abc');
    expect(result.data.content_plaintext).toBe('Great update!');
    expect(result.data.resolved_at).toBeNull();
    expect(result.data.record).toEqual({ object: 'people', record_id: 'rec_01abc' });
  });

  it('delete() → DELETE /comments/:id', async () => {
    let method = '';
    let url = '';
    server.use(
      http.delete(`${BASE}/comments/:id`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({});
      }),
    );
    await client.comments.delete('comment_01abc');
    expect(method).toBe('DELETE');
    expect(url).toBe('/v2/comments/comment_01abc');
  });

  it('getThread() → GET /threads/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/threads/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockThread });
      }),
    );
    const result = await client.comments.getThread('thread_01abc');
    expect(url).toBe('/v2/threads/thread_01abc');
    expect(result.data.comments).toHaveLength(1);
  });

  it('listThreads() → GET /threads with query params', async () => {
    let url = '';
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/threads`, ({ request }) => {
        url = new URL(request.url).pathname;
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [mockThread] });
      }),
    );
    const result = await client.comments.listThreads({
      record_id: 'rec_01abc',
      object: 'people',
    });
    expect(url).toBe('/v2/threads');
    expect(searchParams?.get('record_id')).toBe('rec_01abc');
    expect(searchParams?.get('object')).toBe('people');
    expect(result.data).toHaveLength(1);
  });

  it('listThreads() with entry params', async () => {
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/threads`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [mockThread] });
      }),
    );
    await client.comments.listThreads({
      entry_id: 'entry_01abc',
      list: 'pipeline',
    });
    expect(searchParams?.get('entry_id')).toBe('entry_01abc');
    expect(searchParams?.get('list')).toBe('pipeline');
  });
});
