import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, collectAll } from '../../src/index.js';
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
      linked_object: 'deals',
      linked_record_id: 'rec_01abc',
      participants: 'jane@example.com',
      sort: 'start_desc',
      ends_from: '2024-01-01T00:00:00Z',
      starts_before: '2024-12-31T00:00:00Z',
      timezone: 'America/New_York',
      limit: 25,
      cursor: 'cur_xyz',
    });
    expect(searchParams.get('linked_object')).toBe('deals');
    expect(searchParams.get('linked_record_id')).toBe('rec_01abc');
    expect(searchParams.get('participants')).toBe('jane@example.com');
    expect(searchParams.get('sort')).toBe('start_desc');
    expect(searchParams.get('ends_from')).toBe('2024-01-01T00:00:00Z');
    expect(searchParams.get('starts_before')).toBe('2024-12-31T00:00:00Z');
    expect(searchParams.get('timezone')).toBe('America/New_York');
    expect(searchParams.get('limit')).toBe('25');
    expect(searchParams.get('cursor')).toBe('cur_xyz');
  });

  it('list() joins participants array with commas', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(`${BASE}/meetings`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
      }),
    );
    await client.meetings.list({ participants: ['jane@example.com', 'john@example.com'] });
    expect(searchParams.get('participants')).toBe('jane@example.com,john@example.com');
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

  it('get() with non-existent ID throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/meetings/:meetingId`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    await expect(client.meetings.get('nonexistent')).rejects.toThrow(AttioError);
  });

  it('create() → POST /meetings with body (find-or-create)', async () => {
    let method = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/meetings`, async ({ request }) => {
        method = request.method;
        body = await request.json();
        return HttpResponse.json({ data: mockMeeting });
      }),
    );
    const params = {
      data: {
        title: 'Quarterly Review',
        description: 'Q1 business review',
        start: { datetime: '2024-03-15T14:00:00Z', timezone: 'America/New_York' },
        end: { datetime: '2024-03-15T15:00:00Z', timezone: 'America/New_York' },
        is_all_day: false,
        participants: [
          { email_address: 'jane@example.com', is_organizer: true, status: 'accepted' as const },
        ],
        linked_records: [{ object: 'deals', record_id: 'rec_01abc' }],
        external_ref: 'external_meeting_12345',
      },
    };
    const result = await client.meetings.create(params);
    expect(method).toBe('POST');
    expect(body).toEqual(params);
    expect(result.data.id.meeting_id).toBe('meeting_01abc');
  });

  it('create() with invalid data throws AttioError', async () => {
    server.use(
      http.post(`${BASE}/meetings`, () =>
        HttpResponse.json(
          { code: 'VALIDATION_ERROR', message: 'Body payload validation error.' },
          { status: 400 },
        ),
      ),
    );
    await expect(
      client.meetings.create({
        data: {
          title: 'Bad',
          description: '',
          start: { date: '2024-03-15' },
          end: { date: '2024-03-15' },
          is_all_day: true,
          participants: [],
          external_ref: 'ref_1',
        },
      }),
    ).rejects.toThrow(AttioError);
  });
});

describe('MeetingsResource — listAll()', () => {
  it('iterates through multiple cursor pages', async () => {
    const page1 = [
      { ...mockMeeting, title: 'Meeting 1' },
      { ...mockMeeting, title: 'Meeting 2' },
    ];
    const page2 = [{ ...mockMeeting, title: 'Meeting 3' }];

    let callCount = 0;
    server.use(
      http.get(`${BASE}/meetings`, ({ request }) => {
        callCount++;
        const cursor = new URL(request.url).searchParams.get('cursor');
        if (cursor === null) {
          return HttpResponse.json({ data: page1, pagination: { next_cursor: 'cur_2' } });
        }
        return HttpResponse.json({ data: page2, pagination: { next_cursor: null } });
      }),
    );

    const meetings = await collectAll(client.meetings.listAll());

    expect(meetings).toHaveLength(3);
    expect(meetings[0].title).toBe('Meeting 1');
    expect(meetings[2].title).toBe('Meeting 3');
    expect(callCount).toBe(2);
  });

  it('passes filter params and pageSize through to list()', async () => {
    let searchParams = new URLSearchParams();
    server.use(
      http.get(`${BASE}/meetings`, ({ request }) => {
        searchParams = new URL(request.url).searchParams;
        return HttpResponse.json({ data: [], pagination: { next_cursor: null } });
      }),
    );

    await collectAll(
      client.meetings.listAll({ linked_object: 'deals', linked_record_id: 'rec_01abc' }, {
        pageSize: 100,
      }),
    );

    expect(searchParams.get('linked_object')).toBe('deals');
    expect(searchParams.get('linked_record_id')).toBe('rec_01abc');
    expect(searchParams.get('limit')).toBe('100');
  });
});
