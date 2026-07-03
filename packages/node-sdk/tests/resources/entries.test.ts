import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, collectAll } from '../../src/index.js';
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

  it('query() rejects filter combined with filter_view_id', async () => {
    await expect(
      client.entries.query('pipeline', {
        filter: { stage: { $eq: 'active' } },
        filter_view_id: 'view_01abc',
      }),
    ).rejects.toThrow(TypeError);
  });

  it('query() accepts filter_view_id on its own', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: [mockEntry] });
      }),
    );
    await client.entries.query('pipeline', { filter_view_id: 'view_01abc' });
    expect(body).toEqual({ filter_view_id: 'view_01abc' });
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

  // -------------------------------------------------------------------------
  // Error scenarios
  // -------------------------------------------------------------------------

  it('query() propagates API errors', async () => {
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, () =>
        HttpResponse.json({ message: 'Invalid filter' }, { status: 400 }),
      ),
    );
    await expect(client.entries.query('pipeline', { filter: { bad: true } })).rejects.toThrow(
      AttioError,
    );
  });

  it('get() with non-existent ID throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/lists/:listId/entries/:entryId`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.entries.get('pipeline', 'nonexistent')).rejects.toThrow(AttioError);
  });

  it('create() with invalid data throws AttioError', async () => {
    server.use(
      http.post(`${BASE}/lists/:listId/entries`, () =>
        HttpResponse.json({ message: 'Validation failed', code: 'invalid_params' }, { status: 422 }),
      ),
    );
    try {
      await client.entries.create('pipeline', { data: { parent_record_id: 'bad' } });
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(AttioError);
      expect((e as AttioError).status).toBe(422);
    }
  });

  it('delete() on non-existent entry throws AttioError', async () => {
    server.use(
      http.delete(`${BASE}/lists/:listId/entries/:entryId`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.entries.delete('pipeline', 'nonexistent')).rejects.toThrow(AttioError);
  });
});

// ---------------------------------------------------------------------------
// Auto-pagination: queryAll / listAll
// ---------------------------------------------------------------------------

describe('EntriesResource — queryAll()', () => {
  it('iterates through multiple pages of query results', async () => {
    const page1 = Array.from({ length: 3 }, (_, i) => ({
      ...mockEntry,
      id: { ...mockEntry.id, entry_id: `entry_p1_${i}` },
    }));
    const page2 = Array.from({ length: 3 }, (_, i) => ({
      ...mockEntry,
      id: { ...mockEntry.id, entry_id: `entry_p2_${i}` },
    }));
    const page3 = [{ ...mockEntry, id: { ...mockEntry.id, entry_id: 'entry_p3_0' } }];

    let callCount = 0;
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, async ({ request }) => {
        callCount++;
        const body = (await request.json()) as { limit?: number; offset?: number };
        if (body.offset === 0 || body.offset === undefined) return HttpResponse.json({ data: page1 });
        if (body.offset === 3) return HttpResponse.json({ data: page2 });
        if (body.offset === 6) return HttpResponse.json({ data: page3 });
        return HttpResponse.json({ data: [] });
      }),
    );

    const entries = await collectAll(client.entries.queryAll('pipeline', undefined, { pageSize: 3 }));

    expect(entries).toHaveLength(7);
    expect(entries[0].id.entry_id).toBe('entry_p1_0');
    expect(entries[6].id.entry_id).toBe('entry_p3_0');
    expect(callCount).toBe(3);
  });

  it('passes filter and sort params through to query()', async () => {
    let capturedBody: unknown;
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({ data: [] });
      }),
    );

    await collectAll(
      client.entries.queryAll(
        'pipeline',
        { filter: { status: { $eq: 'active' } }, sorts: [{ attribute: 'created_at', direction: 'desc' }] },
        { pageSize: 10 },
      ),
    );

    expect(capturedBody).toMatchObject({
      filter: { status: { $eq: 'active' } },
      sorts: [{ attribute: 'created_at', direction: 'desc' }],
      limit: 10,
      offset: 0,
    });
  });

  it('respects maxItems', async () => {
    const page = Array.from({ length: 5 }, (_, i) => ({
      ...mockEntry,
      id: { ...mockEntry.id, entry_id: `entry_${i}` },
    }));
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, () =>
        HttpResponse.json({ data: page }),
      ),
    );

    const entries = await collectAll(
      client.entries.queryAll('pipeline', undefined, { pageSize: 5, maxItems: 3 }),
    );

    expect(entries).toHaveLength(3);
  });

  it('works with for-await-of and early break', async () => {
    const page = Array.from({ length: 10 }, (_, i) => ({
      ...mockEntry,
      id: { ...mockEntry.id, entry_id: `entry_${i}` },
    }));
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, () =>
        HttpResponse.json({ data: page }),
      ),
    );

    const entries = [];
    for await (const entry of client.entries.queryAll('pipeline', undefined, { pageSize: 10 })) {
      entries.push(entry);
      if (entries.length === 4) break;
    }

    expect(entries).toHaveLength(4);
  });

  it('returns empty when no results', async () => {
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, () =>
        HttpResponse.json({ data: [] }),
      ),
    );

    const entries = await collectAll(client.entries.queryAll('pipeline'));

    expect(entries).toEqual([]);
  });

  it('propagates API errors during pagination', async () => {
    let callCount = 0;
    server.use(
      http.post(`${BASE}/lists/:listId/entries/query`, () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({
            data: [mockEntry, mockEntry],
          });
        }
        return HttpResponse.json({ message: 'Server error' }, { status: 500 });
      }),
    );

    await expect(
      collectAll(client.entries.queryAll('pipeline', undefined, { pageSize: 2 })),
    ).rejects.toThrow(AttioError);
  });
});

describe('EntriesResource — listAll()', () => {
  it('iterates through multiple pages', async () => {
    const page1 = [
      { ...mockEntry, id: { ...mockEntry.id, entry_id: 'entry_a' } },
      { ...mockEntry, id: { ...mockEntry.id, entry_id: 'entry_b' } },
    ];
    const page2 = [{ ...mockEntry, id: { ...mockEntry.id, entry_id: 'entry_c' } }];

    let callCount = 0;
    server.use(
      http.get(`${BASE}/lists/:listId/entries`, ({ request }) => {
        callCount++;
        const offset = new URL(request.url).searchParams.get('offset');
        if (offset === '0' || offset === null) return HttpResponse.json({ data: page1 });
        return HttpResponse.json({ data: page2 });
      }),
    );

    const entries = await collectAll(client.entries.listAll('pipeline', { pageSize: 2 }));

    expect(entries).toHaveLength(3);
    expect(entries[0].id.entry_id).toBe('entry_a');
    expect(entries[2].id.entry_id).toBe('entry_c');
    expect(callCount).toBe(2);
  });

  it('sends limit as query param', async () => {
    let capturedSearchParams: URLSearchParams | undefined;
    server.use(
      http.get(`${BASE}/lists/:listId/entries`, ({ request }) => {
        capturedSearchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [] });
      }),
    );

    await collectAll(client.entries.listAll('pipeline', { pageSize: 15 }));

    expect(capturedSearchParams?.get('limit')).toBe('15');
  });
});
