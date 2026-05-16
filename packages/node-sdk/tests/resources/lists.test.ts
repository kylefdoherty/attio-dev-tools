import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockList } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('ListsResource', () => {
  it('list() → GET /lists', async () => {
    let method = '';
    server.use(
      http.get(`${BASE}/lists`, ({ request }) => {
        method = request.method;
        return HttpResponse.json({ data: [mockList] });
      }),
    );
    const result = await client.lists.list();
    expect(method).toBe('GET');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].api_slug).toBe('pipeline');
  });

  it('get(slug) → GET /lists/:slug', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/lists/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockList });
      }),
    );
    const result = await client.lists.get('pipeline');
    expect(url).toBe('/v2/lists/pipeline');
    expect(result.data.name).toBe('Pipeline');
  });

  it('create() → POST /lists with { data: params }', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/lists`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: mockList });
      }),
    );
    await client.lists.create({ name: 'Pipeline', parent_object: 'deals' });
    expect(body).toEqual({ data: { name: 'Pipeline', parent_object: 'deals' } });
  });

  it('update() → PATCH /lists/:slug with { data: params }', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.patch(`${BASE}/lists/:id`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockList });
      }),
    );
    await client.lists.update('pipeline', { name: 'Sales Pipeline' });
    expect(method).toBe('PATCH');
    expect(url).toBe('/v2/lists/pipeline');
    expect(body).toEqual({ data: { name: 'Sales Pipeline' } });
  });
});
