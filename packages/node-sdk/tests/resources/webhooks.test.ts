import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockWebhook } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('WebhooksResource', () => {
  it('list() → GET /webhooks', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/webhooks`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockWebhook] });
      }),
    );
    const result = await client.webhooks.list();
    expect(url).toBe('/v2/webhooks');
    expect(result.data).toHaveLength(1);
  });

  it('get() → GET /webhooks/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/webhooks/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockWebhook });
      }),
    );
    const result = await client.webhooks.get('wh_01abc');
    expect(url).toBe('/v2/webhooks/wh_01abc');
    expect(result.data.target_url).toBe('https://example.com/webhook');
  });

  it('create() → POST /webhooks with body', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/webhooks`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockWebhook });
      }),
    );
    await client.webhooks.create({
      data: {
        target_url: 'https://example.com/webhook',
        subscriptions: [{ event_type: 'record.created' }],
      },
    });
    expect(method).toBe('POST');
    expect(body).toHaveProperty('data.target_url', 'https://example.com/webhook');
  });

  it('update() → PUT /webhooks/:id with body', async () => {
    let method = '';
    let url = '';
    server.use(
      http.put(`${BASE}/webhooks/:id`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockWebhook });
      }),
    );
    await client.webhooks.update('wh_01abc', {
      data: { target_url: 'https://example.com/new-webhook' },
    });
    expect(method).toBe('PUT');
    expect(url).toBe('/v2/webhooks/wh_01abc');
  });

  it('delete() → DELETE /webhooks/:id', async () => {
    let method = '';
    server.use(
      http.delete(`${BASE}/webhooks/:id`, ({ request }) => {
        method = request.method;
        return HttpResponse.json({});
      }),
    );
    await client.webhooks.delete('wh_01abc');
    expect(method).toBe('DELETE');
  });
});
