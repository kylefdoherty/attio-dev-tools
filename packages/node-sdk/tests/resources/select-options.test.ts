import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockSelectOption, mockStatus } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('SelectOptionsResource', () => {
  it('list() -> GET /:target/:slug/attributes/:attr/options', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/:target/:identifier/attributes/:attr/options`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockSelectOption] });
      }),
    );
    const result = await client.selectOptions.list('objects', 'deals', 'stage');
    expect(url).toBe('/v2/objects/deals/attributes/stage/options');
    expect(result.data).toHaveLength(1);
  });

  it('create() -> POST /:target/:slug/attributes/:attr/options with { data: params }', async () => {
    let url = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/:target/:identifier/attributes/:attr/options`, async ({ request }) => {
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockSelectOption });
      }),
    );
    await client.selectOptions.create('objects', 'deals', 'stage', { title: 'Option A' });
    expect(url).toBe('/v2/objects/deals/attributes/stage/options');
    expect(body).toEqual({ data: { title: 'Option A' } });
  });

  it('update() -> PATCH /:target/:slug/attributes/:attr/options/:optionId', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.patch(`${BASE}/:target/:identifier/attributes/:attr/options/:opt`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockSelectOption });
      }),
    );
    await client.selectOptions.update('objects', 'deals', 'stage', 'opt_01abc', { title: 'Renamed' });
    expect(method).toBe('PATCH');
    expect(url).toBe('/v2/objects/deals/attributes/stage/options/opt_01abc');
    expect(body).toEqual({ data: { title: 'Renamed' } });
  });

  it('listStatuses() -> GET /:target/:slug/attributes/:attr/statuses', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/:target/:identifier/attributes/:attr/statuses`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockStatus] });
      }),
    );
    const result = await client.selectOptions.listStatuses('objects', 'deals', 'deal_stage');
    expect(url).toBe('/v2/objects/deals/attributes/deal_stage/statuses');
    expect(result.data).toHaveLength(1);
  });

  it('createStatus() -> POST /:target/:slug/attributes/:attr/statuses with { data: params }', async () => {
    let url = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/:target/:identifier/attributes/:attr/statuses`, async ({ request }) => {
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: mockStatus });
      }),
    );
    await client.selectOptions.createStatus('objects', 'deals', 'deal_stage', {
      title: 'In Progress',
      celebration_enabled: false,
    });
    expect(url).toBe('/v2/objects/deals/attributes/deal_stage/statuses');
    expect(body).toEqual({
      data: { title: 'In Progress', celebration_enabled: false },
    });
  });

  it('updateStatus() -> PATCH /:target/:slug/attributes/:attr/statuses/:statusId', async () => {
    let method = '';
    let url = '';
    server.use(
      http.patch(`${BASE}/:target/:identifier/attributes/:attr/statuses/:status`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockStatus });
      }),
    );
    await client.selectOptions.updateStatus('objects', 'deals', 'deal_stage', 'status_01abc', { title: 'Done' });
    expect(method).toBe('PATCH');
    expect(url).toBe('/v2/objects/deals/attributes/deal_stage/statuses/status_01abc');
  });
});
