import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
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
});
