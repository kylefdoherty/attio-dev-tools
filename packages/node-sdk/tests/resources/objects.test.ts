import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server } from '../handlers.js';
import { mockObject } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('ObjectsResource', () => {
  it('list() → GET /objects', async () => {
    let method = '';
    let url = '';
    server.use(
      http.get(`${BASE}/objects`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockObject] });
      }),
    );
    const result = await client.objects.list();
    expect(method).toBe('GET');
    expect(url).toBe('/v2/objects');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].api_slug).toBe('deals');
  });

  it('get(slug) → GET /objects/:slug', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/objects/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockObject });
      }),
    );
    const result = await client.objects.get('deals');
    expect(url).toBe('/v2/objects/deals');
    expect(result.data.api_slug).toBe('deals');
  });

  it('create() → POST /objects with { data: params }', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/objects`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockObject });
      }),
    );
    await client.objects.create({ api_slug: 'deals', singular_noun: 'Deal', plural_noun: 'Deals' });
    expect(method).toBe('POST');
    expect(body).toEqual({
      data: { api_slug: 'deals', singular_noun: 'Deal', plural_noun: 'Deals' },
    });
  });

  it('update() → PUT /objects/:slug with { data: params }', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.put(`${BASE}/objects/:id`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockObject });
      }),
    );
    await client.objects.update('deals', { description: 'Updated' });
    expect(method).toBe('PUT');
    expect(url).toBe('/v2/objects/deals');
    expect(body).toEqual({ data: { description: 'Updated' } });
  });
});
