import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockTranscriptSegment } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('TranscriptsResource', () => {
  it('get() → GET /meetings/:id/call_recordings/:crId/transcript', async () => {
    let url = '';
    server.use(
      http.get(
        `${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`,
        ({ request }) => {
          url = new URL(request.url).pathname;
          return HttpResponse.json({
            data: [mockTranscriptSegment],
            pagination: { next_cursor: null },
          });
        },
      ),
    );
    const result = await client.transcripts.get('meeting_01abc', 'cr_01abc');
    expect(url).toBe('/v2/meetings/meeting_01abc/call_recordings/cr_01abc/transcript');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].speech).toBe('Hello, welcome to the meeting.');
    expect(result.pagination.next_cursor).toBeNull();
  });

  it('get() passes query params', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(
        `${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`,
        ({ request }) => {
          searchParams = new URL(request.url).searchParams;
          return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
        },
      ),
    );
    await client.transcripts.get('meeting_01abc', 'cr_01abc', {
      limit: 50,
      cursor: 'cur_abc',
    });
    expect(searchParams.get('limit')).toBe('50');
    expect(searchParams.get('cursor')).toBe('cur_abc');
  });
});
