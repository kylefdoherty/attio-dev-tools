import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockNote } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('NotesResource', () => {
  it('list() → GET /notes', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/notes`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockNote] });
      }),
    );
    const result = await client.notes.list();
    expect(url).toBe('/v2/notes');
    expect(result.data).toHaveLength(1);
  });

  it('list() with filters as query params', async () => {
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/notes`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [mockNote] });
      }),
    );
    await client.notes.list({ parent_object: 'people', parent_record_id: 'rec_01abc' });
    expect(searchParams?.get('parent_object')).toBe('people');
    expect(searchParams?.get('parent_record_id')).toBe('rec_01abc');
  });

  it('get() → GET /notes/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/notes/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockNote });
      }),
    );
    const result = await client.notes.get('note_01abc');
    expect(url).toBe('/v2/notes/note_01abc');
    expect(result.data.title).toBe('Test Note');
  });

  it('create() → POST /notes with body', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/notes`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockNote });
      }),
    );
    await client.notes.create({
      data: {
        parent_object: 'people',
        parent_record_id: 'rec_01abc',
        title: 'Test',
        format: 'plaintext',
        content: 'Hello',
      },
    });
    expect(method).toBe('POST');
    expect(body).toHaveProperty('data.title', 'Test');
  });

  it('delete() → DELETE /notes/:id', async () => {
    let method = '';
    let url = '';
    server.use(
      http.delete(`${BASE}/notes/:id`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({});
      }),
    );
    await client.notes.delete('note_01abc');
    expect(method).toBe('DELETE');
    expect(url).toBe('/v2/notes/note_01abc');
  });
});
