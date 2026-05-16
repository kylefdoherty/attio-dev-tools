import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockAttribute } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('AttributesResource', () => {
  it('list(objects, slug) -> GET /objects/:slug/attributes', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/:target/:targetId/attributes`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockAttribute] });
      }),
    );
    const result = await client.attributes.list('objects', 'deals');
    expect(url).toBe('/v2/objects/deals/attributes');
    expect(result.data).toHaveLength(1);
  });

  it('list(lists, slug) -> GET /lists/:slug/attributes', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/:target/:targetId/attributes`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockAttribute] });
      }),
    );
    await client.attributes.list('lists', 'pipeline');
    expect(url).toBe('/v2/lists/pipeline/attributes');
  });

  it('get(target, targetSlug, attrSlug) -> GET /:target/:slug/attributes/:attr', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/:target/:targetId/attributes/:attr`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockAttribute });
      }),
    );
    const result = await client.attributes.get('objects', 'deals', 'name');
    expect(url).toBe('/v2/objects/deals/attributes/name');
    expect(result.data.api_slug).toBe('name');
  });

  it('create(target, targetSlug, params) -> POST /:target/:slug/attributes', async () => {
    let url = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/:target/:targetId/attributes`, async ({ request }) => {
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockAttribute });
      }),
    );
    await client.attributes.create('objects', 'deals', {
      title: 'Name',
      api_slug: 'name',
      type: 'text',
    });
    expect(url).toBe('/v2/objects/deals/attributes');
    expect(body).toEqual({ data: { title: 'Name', api_slug: 'name', type: 'text' } });
  });

  it('update() -> PATCH /:target/:slug/attributes/:attr with { data: params }', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.patch(`${BASE}/:target/:targetId/attributes/:attr`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockAttribute });
      }),
    );
    await client.attributes.update('objects', 'deals', 'name', { title: 'Full Name' });
    expect(method).toBe('PATCH');
    expect(url).toBe('/v2/objects/deals/attributes/name');
    expect(body).toEqual({ data: { title: 'Full Name' } });
  });
});
