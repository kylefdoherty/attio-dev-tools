import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockObjectView, mockListView } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('ViewsResource', () => {
  it('list(objects, slug) → GET /objects/:slug/views', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/objects/:objectId/views`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockObjectView], pagination: { next_cursor: null } });
      }),
    );
    const result = await client.views.list('objects', 'people');
    expect(url).toBe('/v2/objects/people/views');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].title).toBe('All People');
    expect(result.pagination.next_cursor).toBeNull();
  });

  it('list(lists, slug) → GET /lists/:slug/views', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/lists/:listId/views`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockListView], pagination: { next_cursor: null } });
      }),
    );
    const result = await client.views.list('lists', 'pipeline');
    expect(url).toBe('/v2/lists/pipeline/views');
    expect(result.data[0].title).toBe('Active Deals');
  });

  it('passes query params (show_archived, limit, cursor)', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(`${BASE}/objects/:objectId/views`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
      }),
    );
    await client.views.list('objects', 'people', {
      show_archived: true,
      limit: 10,
      cursor: 'abc123',
    });
    expect(searchParams.get('show_archived')).toBe('true');
    expect(searchParams.get('limit')).toBe('10');
    expect(searchParams.get('cursor')).toBe('abc123');
  });
});
