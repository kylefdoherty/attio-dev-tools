import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockMeeting } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('MeetingsResource', () => {
  it('list() → GET /meetings', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/meetings`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockMeeting], pagination: { next_cursor: null } });
      }),
    );
    const result = await client.meetings.list();
    expect(url).toBe('/v2/meetings');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].title).toBe('Quarterly Review');
    expect(result.pagination.next_cursor).toBeNull();
  });

  it('list() passes query params', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(`${BASE}/meetings`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
      }),
    );
    await client.meetings.list({
      linked_record_id: 'rec_01abc',
      linked_object: 'deals',
      participant_email: 'jane@example.com',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      timezone: 'America/New_York',
      limit: 25,
      cursor: 'cur_xyz',
    });
    expect(searchParams.get('linked_record_id')).toBe('rec_01abc');
    expect(searchParams.get('linked_object')).toBe('deals');
    expect(searchParams.get('participant_email')).toBe('jane@example.com');
    expect(searchParams.get('start_date')).toBe('2024-01-01');
    expect(searchParams.get('end_date')).toBe('2024-12-31');
    expect(searchParams.get('timezone')).toBe('America/New_York');
    expect(searchParams.get('limit')).toBe('25');
    expect(searchParams.get('cursor')).toBe('cur_xyz');
  });

  it('get() → GET /meetings/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/meetings/:meetingId`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockMeeting });
      }),
    );
    const result = await client.meetings.get('meeting_01abc');
    expect(url).toBe('/v2/meetings/meeting_01abc');
    expect(result.data.title).toBe('Quarterly Review');
    expect(result.data.participants).toHaveLength(1);
  });
});
