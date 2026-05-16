import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockRecord, mockEntry, mockGlobalSearchResult } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('RecordsResource', () => {
  it('list() → GET /objects/:slug/records', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/objects/:objId/records`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockRecord] });
      }),
    );
    const result = await client.records.list('people');
    expect(url).toBe('/v2/objects/people/records');
    expect(result.data).toHaveLength(1);
  });

  it('list() with limit and offset as query params', async () => {
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/objects/:objId/records`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.records.list('people', { limit: 10, offset: 20 });
    expect(searchParams?.get('limit')).toBe('10');
    expect(searchParams?.get('offset')).toBe('20');
  });

  it('query() → POST /objects/:slug/records/query with body', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: [mockRecord] });
      }),
    );
    const filter = { name: { $contains: 'test' } };
    await client.records.query('people', { filter, limit: 5 });
    expect(method).toBe('POST');
    expect(body).toEqual({ filter, limit: 5 });
  });

  it('query() with no params sends empty body', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.records.query('people');
    expect(body).toEqual({});
  });

  it('search() → POST /objects/:slug/records/search', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/:objId/records/search`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: [mockRecord] });
      }),
    );
    await client.records.search('people', { query: 'Jane', limit: 5 });
    expect(body).toEqual({ query: 'Jane', limit: 5 });
  });

  it('get() → GET /objects/:slug/records/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/objects/:objId/records/:recId`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockRecord });
      }),
    );
    const result = await client.records.get('people', 'rec_01abc');
    expect(url).toBe('/v2/objects/people/records/rec_01abc');
    expect(result.data.id.record_id).toBe('rec_01abc');
  });

  it('create() → POST /objects/:slug/records', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/:objId/records`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockRecord });
      }),
    );
    await client.records.create('people', { data: { values: { name: [{ value: 'Jane' }] } } });
    expect(method).toBe('POST');
    expect(body).toEqual({ data: { values: { name: [{ value: 'Jane' }] } } });
  });

  it('update() → PUT /objects/:slug/records/:id', async () => {
    let method = '';
    let url = '';
    server.use(
      http.put(`${BASE}/objects/:objId/records/:recId`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockRecord });
      }),
    );
    await client.records.update('people', 'rec_01abc', { data: { values: {} } });
    expect(method).toBe('PUT');
    expect(url).toBe('/v2/objects/people/records/rec_01abc');
  });

  it('append() → PATCH /objects/:slug/records/:id', async () => {
    let method = '';
    server.use(
      http.patch(`${BASE}/objects/:objId/records/:recId`, async ({ request }) => {
        method = request.method;
        return HttpResponse.json({ data: mockRecord });
      }),
    );
    await client.records.append('people', 'rec_01abc', { data: { values: {} } });
    expect(method).toBe('PATCH');
  });

  it('delete() → DELETE /objects/:slug/records/:id', async () => {
    let method = '';
    let url = '';
    server.use(
      http.delete(`${BASE}/objects/:objId/records/:recId`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({});
      }),
    );
    await client.records.delete('people', 'rec_01abc');
    expect(method).toBe('DELETE');
    expect(url).toBe('/v2/objects/people/records/rec_01abc');
  });

  it('upsert() → PUT /objects/:slug/records (upsert)', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.put(`${BASE}/objects/:objId/records`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockRecord });
      }),
    );
    await client.records.upsert('people', {
      data: { matching_attribute: 'email', values: { email: [{ value: 'j@example.com' }] } },
    });
    expect(method).toBe('PUT');
    expect(url).toBe('/v2/objects/people/records');
    expect(body).toHaveProperty('data.matching_attribute', 'email');
  });

  it('getAttributeValues() -> GET /objects/:obj/records/:rec/attributes/:attr/values', async () => {
    let url = '';
    let searchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/objects/:objId/records/:recId/attributes/:attrId/values`, ({ request }) => {
        url = new URL(request.url).pathname;
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.records.getAttributeValues('people', 'rec_01abc', 'email', {
      showHistoric: true,
    });
    expect(url).toBe('/v2/objects/people/records/rec_01abc/attributes/email/values');
    expect(searchParams?.get('show_historic')).toBe('true');
  });

  it('listEntries() → GET /objects/:slug/records/:id/entries', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/objects/:objId/records/:recId/entries`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockEntry] });
      }),
    );
    const result = await client.records.listEntries('people', 'rec_01abc');
    expect(url).toBe('/v2/objects/people/records/rec_01abc/entries');
    expect(result.data).toHaveLength(1);
  });

  it('globalSearch() → POST /objects/records/search', async () => {
    let url = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/records/search`, async ({ request }) => {
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: [mockGlobalSearchResult] });
      }),
    );
    const result = await client.records.globalSearch({
      query: 'Jane',
      objects: ['people'],
      limit: 10,
    });
    expect(url).toBe('/v2/objects/records/search');
    expect(body).toEqual({ query: 'Jane', objects: ['people'], limit: 10 });
    expect(result.data).toHaveLength(1);
    expect(result.data[0].record_text).toBe('Jane Doe');
    expect(result.data[0].object_slug).toBe('people');
  });
});
