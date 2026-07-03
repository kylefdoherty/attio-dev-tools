import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, RateLimitError, collectAll } from '../../src/index.js';
import { server, mockCallRecording } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('CallRecordingsResource', () => {
  it('list() → GET /meetings/:id/call_recordings', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/meetings/:meetingId/call_recordings`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({
          data: [mockCallRecording],
          pagination: { next_cursor: null },
        });
      }),
    );
    const result = await client.callRecordings.list('meeting_01abc');
    expect(url).toBe('/v2/meetings/meeting_01abc/call_recordings');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].status).toBe('completed');
    expect(result.pagination.next_cursor).toBeNull();
  });

  it('list() passes query params', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(`${BASE}/meetings/:meetingId/call_recordings`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
      }),
    );
    await client.callRecordings.list('meeting_01abc', { limit: 5, cursor: 'cur_abc' });
    expect(searchParams.get('limit')).toBe('5');
    expect(searchParams.get('cursor')).toBe('cur_abc');
  });

  it('get() → GET /meetings/:id/call_recordings/:crId', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/meetings/:meetingId/call_recordings/:crId`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockCallRecording });
      }),
    );
    const result = await client.callRecordings.get('meeting_01abc', 'cr_01abc');
    expect(url).toBe('/v2/meetings/meeting_01abc/call_recordings/cr_01abc');
    expect(result.data.id.call_recording_id).toBe('cr_01abc');
  });

  it('create() → POST /meetings/:id/call_recordings with body', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/meetings/:meetingId/call_recordings`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: { ...mockCallRecording, status: 'processing' } });
      }),
    );
    const result = await client.callRecordings.create('meeting_01abc', {
      data: { video_url: 'https://example.com/recording.mp4' },
    });
    expect(method).toBe('POST');
    expect(url).toBe('/v2/meetings/meeting_01abc/call_recordings');
    expect(body).toEqual({ data: { video_url: 'https://example.com/recording.mp4' } });
    expect(result.data.status).toBe('processing');
  });

  it('create() with invalid video URL throws AttioError', async () => {
    server.use(
      http.post(`${BASE}/meetings/:meetingId/call_recordings`, () =>
        HttpResponse.json(
          { code: 'VALIDATION_ERROR', message: 'video_url must use https' },
          { status: 400 },
        ),
      ),
    );
    await expect(
      client.callRecordings.create('meeting_01abc', {
        data: { video_url: 'http://example.com/recording.mp4' },
      }),
    ).rejects.toThrow(AttioError);
  });

  it('create() surfaces RateLimitError when the 1 req/s limit is exhausted', async () => {
    server.use(
      http.post(`${BASE}/meetings/:meetingId/call_recordings`, () =>
        HttpResponse.json(
          { message: 'Too many requests' },
          { status: 429, headers: { 'Retry-After': '1' } },
        ),
      ),
    );
    await expect(
      client.callRecordings.create('meeting_01abc', {
        data: { video_url: 'https://example.com/recording.mp4' },
      }),
    ).rejects.toThrow(RateLimitError);
  });

  it('delete() → DELETE /meetings/:id/call_recordings/:crId', async () => {
    let method = '';
    let url = '';
    server.use(
      http.delete(`${BASE}/meetings/:meetingId/call_recordings/:crId`, ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        return new HttpResponse(null, { status: 204 });
      }),
    );
    await client.callRecordings.delete('meeting_01abc', 'cr_01abc');
    expect(method).toBe('DELETE');
    expect(url).toBe('/v2/meetings/meeting_01abc/call_recordings/cr_01abc');
  });

  it('delete() on non-existent recording throws AttioError', async () => {
    server.use(
      http.delete(`${BASE}/meetings/:meetingId/call_recordings/:crId`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.callRecordings.delete('meeting_01abc', 'nonexistent')).rejects.toThrow(
      AttioError,
    );
  });
});

describe('CallRecordingsResource — listAll()', () => {
  it('iterates through multiple cursor pages', async () => {
    const rec = (id: string) => ({
      ...mockCallRecording,
      id: { ...mockCallRecording.id, call_recording_id: id },
    });

    let callCount = 0;
    server.use(
      http.get(`${BASE}/meetings/:meetingId/call_recordings`, ({ request }) => {
        callCount++;
        const cursor = new URL(request.url).searchParams.get('cursor');
        if (cursor === null) {
          return HttpResponse.json({
            data: [rec('cr_a'), rec('cr_b')],
            pagination: { next_cursor: 'cur_2' },
          });
        }
        return HttpResponse.json({ data: [rec('cr_c')], pagination: { next_cursor: null } });
      }),
    );

    const recordings = await collectAll(client.callRecordings.listAll('meeting_01abc'));

    expect(recordings).toHaveLength(3);
    expect(recordings[2].id.call_recording_id).toBe('cr_c');
    expect(callCount).toBe(2);
  });
});
