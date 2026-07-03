import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, collectAll } from '../../src/index.js';
import { server, mockConnectedFile, mockFile, mockFolder } from '../handlers.js';

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
      storage_provider: 'attio',
      limit: 10,
      cursor: 'cur_abc',
    });
    expect(searchParams.get('object')).toBe('deals');
    expect(searchParams.get('record_id')).toBe('rec_01abc');
    expect(searchParams.get('storage_provider')).toBe('attio');
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

  it('createFolder() → POST /files with file_type folder', async () => {
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
      object: 'deals',
      record_id: 'rec_01abc',
      name: 'Documents',
    });
    expect(method).toBe('POST');
    expect(body).toEqual({
      object: 'deals',
      record_id: 'rec_01abc',
      name: 'Documents',
      file_type: 'folder',
    });
  });

  it('createConnected() → POST /files with connected entry body', async () => {
    let body: unknown;
    server.use(
      http.post(`${BASE}/files`, async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ data: mockConnectedFile });
      }),
    );
    const result = await client.files.createConnected({
      object: 'deals',
      record_id: 'rec_01abc',
      file_type: 'connected-file',
      storage_provider: 'google-drive',
      external_provider_file_id: 'gdrive_file_123',
    });
    expect(body).toEqual({
      object: 'deals',
      record_id: 'rec_01abc',
      file_type: 'connected-file',
      storage_provider: 'google-drive',
      external_provider_file_id: 'gdrive_file_123',
    });
    expect(result.data.file_type).toBe('connected-file');
  });

  it('upload() -> POST /files/upload with multipart/form-data fields', async () => {
    let contentType = '';
    let url = '';
    let formData: FormData | undefined;
    server.use(
      http.post(`${BASE}/files/upload`, async ({ request }) => {
        contentType = request.headers.get('content-type') ?? '';
        url = new URL(request.url).pathname;
        formData = await request.formData();
        return HttpResponse.json({ data: mockFile });
      }),
    );
    const result = await client.files.upload({
      file: new Blob(['test file content'], { type: 'text/plain' }),
      object: 'deals',
      record_id: 'rec_01abc',
      filename: 'notes.txt',
    });
    expect(url).toBe('/v2/files/upload');
    expect(contentType).toContain('multipart/form-data');
    expect(formData?.get('object')).toBe('deals');
    expect(formData?.get('record_id')).toBe('rec_01abc');
    expect((formData?.get('file') as File).name).toBe('notes.txt');
    expect(result.data.name).toBe('report.pdf');
  });

  it('upload() accepts a Buffer', async () => {
    let formData: FormData | undefined;
    server.use(
      http.post(`${BASE}/files/upload`, async ({ request }) => {
        formData = await request.formData();
        return HttpResponse.json({ data: mockFile });
      }),
    );
    await client.files.upload({
      file: Buffer.from('binary content'),
      object: 'deals',
      record_id: 'rec_01abc',
    });
    const file = formData?.get('file') as File;
    expect(await file.text()).toBe('binary content');
  });

  it('download() → GET /files/:id/download resolves 302 with the signed URL', async () => {
    let url = '';
    server.use(
      http.get(
        `${BASE}/files/:fileId/download`,
        ({ request }) => {
          url = new URL(request.url).pathname;
          return new HttpResponse(null, {
            status: 302,
            headers: { Location: 'https://storage.example.com/file.pdf?signature=abc' },
          });
        },
      ),
    );
    const result = await client.files.download('file_01abc');
    expect(url).toBe('/v2/files/file_01abc/download');
    expect(result.url).toBe('https://storage.example.com/file.pdf?signature=abc');
  });

  it('download() on non-existent file throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/files/:fileId/download`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.files.download('nonexistent')).rejects.toThrow(AttioError);
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

describe('FilesResource — listAll()', () => {
  it('iterates through multiple cursor pages', async () => {
    const file = (name: string) => ({ ...mockFile, name });

    let callCount = 0;
    server.use(
      http.get(`${BASE}/files`, ({ request }) => {
        callCount++;
        const cursor = new URL(request.url).searchParams.get('cursor');
        if (cursor === null) {
          return HttpResponse.json({
            data: [file('a.pdf'), file('b.pdf')],
            pagination: { next_cursor: 'cur_2' },
          });
        }
        return HttpResponse.json({ data: [file('c.pdf')], pagination: { next_cursor: null } });
      }),
    );

    const files = await collectAll(client.files.listAll({ object: 'deals' }));

    expect(files).toHaveLength(3);
    expect(files[2].name).toBe('c.pdf');
    expect(callCount).toBe(2);
  });
});
