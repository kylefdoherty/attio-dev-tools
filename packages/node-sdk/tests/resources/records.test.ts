import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, collectAll } from '../../src/index.js';
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
      request_as: { type: 'workspace' },
      limit: 10,
    });
    expect(url).toBe('/v2/objects/records/search');
    expect(body).toEqual({
      query: 'Jane',
      objects: ['people'],
      request_as: { type: 'workspace' },
      limit: 10,
    });
    expect(result.data).toHaveLength(1);
    expect(result.data[0].record_text).toBe('Jane Doe');
    expect(result.data[0].object_slug).toBe('people');
    expect(result.data[0].id.record_id).toBe('rec_01abc');
  });

  it('globalSearch() supports workspace-member impersonation', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/records/search`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: [] });
      }),
    );
    await client.records.globalSearch({
      query: 'Jane',
      objects: ['people'],
      request_as: { type: 'workspace-member', email_address: 'alice@acme.com' },
    });
    expect(body).toMatchObject({
      request_as: { type: 'workspace-member', email_address: 'alice@acme.com' },
    });
  });

  it('query() rejects filter combined with filter_view_id', async () => {
    await expect(
      client.records.query('people', {
        filter: { name: { $contains: 'Jane' } },
        filter_view_id: 'view_01abc',
      }),
    ).rejects.toThrow(TypeError);
  });

  it('query() accepts filter_view_id on its own', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: [mockRecord] });
      }),
    );
    await client.records.query('people', { filter_view_id: 'view_01abc', limit: 5 });
    expect(body).toEqual({ filter_view_id: 'view_01abc', limit: 5 });
  });

  // -------------------------------------------------------------------------
  // Error scenarios
  // -------------------------------------------------------------------------

  it('query() propagates API errors', async () => {
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, () =>
        HttpResponse.json({ message: 'Invalid filter' }, { status: 400 }),
      ),
    );
    await expect(client.records.query('people', { filter: { bad: true } })).rejects.toThrow(
      AttioError,
    );
  });

  it('get() with non-existent ID throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/objects/:objId/records/:recId`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.records.get('people', 'nonexistent')).rejects.toThrow(AttioError);
  });

  it('create() with invalid data throws AttioError', async () => {
    server.use(
      http.post(`${BASE}/objects/:objId/records`, () =>
        HttpResponse.json({ message: 'Validation failed', code: 'invalid_params' }, { status: 422 }),
      ),
    );
    try {
      await client.records.create('people', { data: { values: {} } });
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(AttioError);
      expect((e as AttioError).status).toBe(422);
    }
  });

  it('delete() on non-existent record throws AttioError', async () => {
    server.use(
      http.delete(`${BASE}/objects/:objId/records/:recId`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.records.delete('people', 'nonexistent')).rejects.toThrow(AttioError);
  });
});

// ---------------------------------------------------------------------------
// Auto-pagination: queryAll / listAll
// ---------------------------------------------------------------------------

describe('RecordsResource — queryAll()', () => {
  it('iterates through multiple pages of query results', async () => {
    const page1 = Array.from({ length: 3 }, (_, i) => ({
      ...mockRecord,
      id: { ...mockRecord.id, record_id: `rec_p1_${i}` },
    }));
    const page2 = Array.from({ length: 3 }, (_, i) => ({
      ...mockRecord,
      id: { ...mockRecord.id, record_id: `rec_p2_${i}` },
    }));
    const page3 = [{ ...mockRecord, id: { ...mockRecord.id, record_id: 'rec_p3_0' } }];

    let callCount = 0;
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, async ({ request }) => {
        callCount++;
        const body = (await request.json()) as { limit?: number; offset?: number };
        if (body.offset === 0 || body.offset === undefined) return HttpResponse.json({ data: page1 });
        if (body.offset === 3) return HttpResponse.json({ data: page2 });
        if (body.offset === 6) return HttpResponse.json({ data: page3 });
        return HttpResponse.json({ data: [] });
      }),
    );

    const records = await collectAll(client.records.queryAll('people', undefined, { pageSize: 3 }));

    expect(records).toHaveLength(7);
    expect(records[0].id.record_id).toBe('rec_p1_0');
    expect(records[6].id.record_id).toBe('rec_p3_0');
    expect(callCount).toBe(3);
  });

  it('passes filter and sort params through to query()', async () => {
    let capturedBody: unknown;
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({ data: [] });
      }),
    );

    await collectAll(
      client.records.queryAll(
        'people',
        { filter: { name: { $contains: 'Jane' } }, sorts: [{ attribute: 'name', direction: 'asc' }] },
        { pageSize: 10 },
      ),
    );

    expect(capturedBody).toMatchObject({
      filter: { name: { $contains: 'Jane' } },
      sorts: [{ attribute: 'name', direction: 'asc' }],
      limit: 10,
      offset: 0,
    });
  });

  it('respects maxItems', async () => {
    const page = Array.from({ length: 5 }, (_, i) => ({
      ...mockRecord,
      id: { ...mockRecord.id, record_id: `rec_${i}` },
    }));
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, () =>
        HttpResponse.json({ data: page }),
      ),
    );

    const records = await collectAll(
      client.records.queryAll('people', undefined, { pageSize: 5, maxItems: 3 }),
    );

    expect(records).toHaveLength(3);
  });

  it('works with for-await-of and early break', async () => {
    const page = Array.from({ length: 10 }, (_, i) => ({
      ...mockRecord,
      id: { ...mockRecord.id, record_id: `rec_${i}` },
    }));
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, () =>
        HttpResponse.json({ data: page }),
      ),
    );

    const records = [];
    for await (const record of client.records.queryAll('people', undefined, { pageSize: 10 })) {
      records.push(record);
      if (records.length === 4) break;
    }

    expect(records).toHaveLength(4);
  });

  it('returns empty when no results', async () => {
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, () =>
        HttpResponse.json({ data: [] }),
      ),
    );

    const records = await collectAll(client.records.queryAll('people'));

    expect(records).toEqual([]);
  });

  it('propagates API errors during pagination', async () => {
    let callCount = 0;
    server.use(
      http.post(`${BASE}/objects/:objId/records/query`, () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({
            data: [mockRecord, mockRecord],
          });
        }
        return HttpResponse.json({ message: 'Server error' }, { status: 500 });
      }),
    );

    await expect(
      collectAll(client.records.queryAll('people', undefined, { pageSize: 2 })),
    ).rejects.toThrow(AttioError);
  });
});

describe('RecordsResource — listAll()', () => {
  it('iterates through multiple pages', async () => {
    const page1 = [
      { ...mockRecord, id: { ...mockRecord.id, record_id: 'rec_a' } },
      { ...mockRecord, id: { ...mockRecord.id, record_id: 'rec_b' } },
    ];
    const page2 = [{ ...mockRecord, id: { ...mockRecord.id, record_id: 'rec_c' } }];

    let callCount = 0;
    server.use(
      http.get(`${BASE}/objects/:objId/records`, ({ request }) => {
        callCount++;
        const offset = new URL(request.url).searchParams.get('offset');
        if (offset === '0' || offset === null) return HttpResponse.json({ data: page1 });
        return HttpResponse.json({ data: page2 });
      }),
    );

    const records = await collectAll(client.records.listAll('people', { pageSize: 2 }));

    expect(records).toHaveLength(3);
    expect(records[0].id.record_id).toBe('rec_a');
    expect(records[2].id.record_id).toBe('rec_c');
    expect(callCount).toBe(2);
  });

  it('sends limit as query param', async () => {
    let capturedSearchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/objects/:objId/records`, ({ request }) => {
        capturedSearchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );

    await collectAll(client.records.listAll('people', { pageSize: 15 }));

    expect(capturedSearchParams?.get('limit')).toBe('15');
  });
});
