import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockEntry } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('EntriesResource', () => {
  it('list() → GET /lists/:slug/entries', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/lists/:listId/entries`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockEntry] });
      }),
    );
    const result = await client.entries.list('pipeline');
    expect(url).toBe('/v2/lists/pipeline/entries');
    expect(result.data).toHaveLength(1);
  });

  it('list() with limit and offset', async () => {
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/lists/:listId/entries`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.entries.list('pipeline', { limit: 5, offset: 10 });
    expect(searchParams?.get('limit')).toBe('5');
    expect(searchParams?.get('offset')).toBe('10');
  });

  it('query() → POST /lists/:slug/entries/query', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: [mockEntry] });
      }),
    );
    await client.entries.query('pipeline', { limit: 10 });
    expect(method).toBe('POST');
    expect(body).toEqual({ limit: 10 });
  });

  it('query() with no params sends empty body', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.entries.query('pipeline');
    expect(body).toEqual({});
  });

  it('get() → GET /lists/:slug/entries/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/lists/:listId/entries/:entryId`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockEntry });
      }),
    );
    await client.entries.get('pipeline', 'entry_01abc');
    expect(url).toBe('/v2/lists/pipeline/entries/entry_01abc');
  });

  it('create() → POST /lists/:slug/entries', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/lists/:listId/entries`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockEntry });
      }),
    );
    await client.entries.create('pipeline', {
      data: { parent_record_id: 'rec_01abc' },
    });
    expect(method).toBe('POST');
    expect(body).toEqual({ data: { parent_record_id: 'rec_01abc' } });
  });

  it('update() → PUT /lists/:slug/entries/:id', async () => {
    let method = '';
    server.use(
      http.put(`${BASE}/lists/:listId/entries/:entryId`, async ({ request }) => {
        method = request.method;
        return HttpResponse.json({ data: mockEntry });
      }),
    );
    await client.entries.update('pipeline', 'entry_01abc', { data: { values: {} } });
    expect(method).toBe('PUT');
  });

  it('append() → PATCH /lists/:slug/entries/:id', async () => {
    let method = '';
    server.use(
      http.patch(`${BASE}/lists/:listId/entries/:entryId`, async ({ request }) => {
        method = request.method;
        return HttpResponse.json({ data: mockEntry });
      }),
    );
    await client.entries.append('pipeline', 'entry_01abc', { data: { values: {} } });
    expect(method).toBe('PATCH');
  });

  it('delete() → DELETE /lists/:slug/entries/:id', async () => {
    let method = '';
    let url = '';
    server.use(
      http.delete(`${BASE}/lists/:listId/entries/:entryId`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({});
      }),
    );
    await client.entries.delete('pipeline', 'entry_01abc');
    expect(method).toBe('DELETE');
    expect(url).toBe('/v2/lists/pipeline/entries/entry_01abc');
  });

  it('upsert() → PUT /lists/:slug/entries (upsert)', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.put(`${BASE}/lists/:listId/entries`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockEntry });
      }),
    );
    await client.entries.upsert('pipeline', {
      data: { parent_record_id: 'rec_01abc' },
    });
    expect(method).toBe('PUT');
    expect(url).toBe('/v2/lists/pipeline/entries');
    expect(body).toEqual({ data: { parent_record_id: 'rec_01abc' } });
  });

  it('getAttributeValues() -> GET /lists/:list/entries/:entry/attributes/:attr/values', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/lists/:listId/entries/:entryId/attributes/:attrId/values`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.entries.getAttributeValues('pipeline', 'entry_01abc', 'status');
    expect(url).toBe('/v2/lists/pipeline/entries/entry_01abc/attributes/status/values');
  });

  it('getAttributeValues() with showHistoric', async () => {
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/lists/:listId/entries/:entryId/attributes/:attrId/values`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.entries.getAttributeValues('pipeline', 'entry_01abc', 'status', {
      showHistoric: true,
    });
    expect(searchParams?.get('show_historic')).toBe('true');
  });

  it('response includes entry_values (not values)', async () => {
    const result = await client.entries.get('pipeline', 'entry_01abc');
    expect(result.data).toHaveProperty('entry_values');
    expect(result.data).not.toHaveProperty('values');
  });
});
