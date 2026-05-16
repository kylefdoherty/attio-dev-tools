import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockFile, mockFolder } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('FilesResource', () => {
  it('list() → GET /files', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/files`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockFile], pagination: { next_cursor: null } });
      }),
    );
    const result = await client.files.list();
    expect(url).toBe('/v2/files');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].name).toBe('report.pdf');
    expect(result.pagination.next_cursor).toBeNull();
  });

  it('list() passes query params', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(`${BASE}/files`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
      }),
    );
    await client.files.list({
      object: 'deals',
      record_id: 'rec_01abc',
      limit: 10,
      cursor: 'cur_abc',
    });
    expect(searchParams.get('object')).toBe('deals');
    expect(searchParams.get('record_id')).toBe('rec_01abc');
    expect(searchParams.get('limit')).toBe('10');
    expect(searchParams.get('cursor')).toBe('cur_abc');
  });

  it('get() → GET /files/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/files/:fileId`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockFile });
      }),
    );
    const result = await client.files.get('file_01abc');
    expect(url).toBe('/v2/files/file_01abc');
    expect(result.data.name).toBe('report.pdf');
  });

  it('createFolder() → POST /files with body', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/files`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockFolder });
      }),
    );
    await client.files.createFolder({
      data: {
        name: 'Documents',
        parent_record: { object: 'deals', record_id: 'rec_01abc' },
      },
    });
    expect(method).toBe('POST');
    expect(body).toHaveProperty('data.name', 'Documents');
  });

  it('upload() -> POST /files/upload with multipart/form-data', async () => {
    let contentType = '';
    let url = '';
    server.use(
      http.post(`${BASE}/files/upload`, async ({ request }) => {
        contentType = request.headers.get('content-type') ?? '';
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockFile });
      }),
    );
    const result = await client.files.upload({
      file: new Blob(['test file content'], { type: 'text/plain' }),
      parent_record_object: 'deals',
      parent_record_record_id: 'rec_01abc',
    });
    expect(url).toBe('/v2/files/upload');
    expect(contentType).toContain('multipart/form-data');
    expect(result.data.name).toBe('report.pdf');
  });

  it('download() → GET /files/:id/download', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/files/:fileId/download`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: { url: 'https://storage.example.com/file.pdf' } });
      }),
    );
    const result = await client.files.download('file_01abc');
    expect(url).toBe('/v2/files/file_01abc/download');
    expect(result.data.url).toContain('storage.example.com');
  });

  it('delete() → DELETE /files/:id', async () => {
    let method = '';
    let url = '';
    server.use(
      http.delete(`${BASE}/files/:fileId`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return HttpResponse.json({});
      }),
    );
    await client.files.delete('file_01abc');
    expect(method).toBe('DELETE');
    expect(url).toBe('/v2/files/file_01abc');
  });
});
