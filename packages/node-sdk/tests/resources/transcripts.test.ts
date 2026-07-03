import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, collectAll } from '../../src/index.js';
import { server, mockTranscript, mockTranscriptSegment } from '../handlers.js';

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
            data: mockTranscript,
            pagination: { next_cursor: null },
          });
        },
      ),
    );
    const result = await client.transcripts.get('meeting_01abc', 'cr_01abc');
    expect(url).toBe('/v2/meetings/meeting_01abc/call_recordings/cr_01abc/transcript');
    expect(result.data.id.call_recording_id).toBe('cr_01abc');
    expect(result.data.transcript).toHaveLength(1);
    expect(result.data.transcript[0].speech).toBe('Hello, welcome to the meeting.');
    expect(result.pagination.next_cursor).toBeNull();
  });

  it('get() passes cursor query param', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(
        `${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`,
        ({ request }) => {
          searchParams = new URL(request.url).searchParams;
          return HttpResponse.json({
            data: { ...mockTranscript, transcript: [] },
            pagination: { next_cursor: null },
          });
        },
      ),
    );
    await client.transcripts.get('meeting_01abc', 'cr_01abc', { cursor: 'cur_abc' });
    expect(searchParams.get('cursor')).toBe('cur_abc');
  });

  it('get() on a recording without a transcript throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.transcripts.get('meeting_01abc', 'nonexistent')).rejects.toThrow(
      AttioError,
    );
  });
});

describe('TranscriptsResource — segments()', () => {
  it('iterates through multiple cursor pages of segments', async () => {
    const segment = (speech: string) => ({ ...mockTranscriptSegment, speech });

    let callCount = 0;
    server.use(
      http.get(
        `${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`,
        ({ request }) => {
          callCount++;
          const cursor = new URL(request.url).searchParams.get('cursor');
          if (cursor === null) {
            return HttpResponse.json({
              data: { ...mockTranscript, transcript: [segment('Hello,'), segment('world.')] },
              pagination: { next_cursor: 'cur_2' },
            });
          }
          return HttpResponse.json({
            data: { ...mockTranscript, transcript: [segment('Goodbye.')] },
            pagination: { next_cursor: null },
          });
        },
      ),
    );

    const segments = await collectAll(client.transcripts.segments('meeting_01abc', 'cr_01abc'));

    expect(segments).toHaveLength(3);
    expect(segments[0].speech).toBe('Hello,');
    expect(segments[2].speech).toBe('Goodbye.');
    expect(callCount).toBe(2);
  });

  it('respects maxItems', async () => {
    server.use(
      http.get(`${BASE}/meetings/:meetingId/call_recordings/:crId/transcript`, () =>
        HttpResponse.json({
          data: {
            ...mockTranscript,
            transcript: Array.from({ length: 5 }, (_, i) => ({
              ...mockTranscriptSegment,
              speech: `Segment ${i}`,
            })),
          },
          pagination: { next_cursor: 'cur_more' },
        }),
      ),
    );

    const segments = await collectAll(
      client.transcripts.segments('meeting_01abc', 'cr_01abc', { maxItems: 3 }),
    );

    expect(segments).toHaveLength(3);
  });
});
