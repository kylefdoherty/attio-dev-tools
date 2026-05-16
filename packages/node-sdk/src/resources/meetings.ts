import type { HttpClient } from '../client.js';
import type { AttioMeeting, ListMeetingsParams, PaginatedResponse } from '../types.js';

export class MeetingsResource {
  constructor(private client: HttpClient) {}

  /** List meetings, optionally filtered by linked record, participant, or date range. */
  async list(params?: ListMeetingsParams): Promise<PaginatedResponse<AttioMeeting>> {
    const queryParams: Record<string, string> = {};
    if (params?.linked_record_id) queryParams.linked_record_id = params.linked_record_id;
    if (params?.linked_object) queryParams.linked_object = params.linked_object;
    if (params?.participant_email) queryParams.participant_email = params.participant_email;
    if (params?.start_date) queryParams.start_date = params.start_date;
    if (params?.end_date) queryParams.end_date = params.end_date;
    if (params?.timezone) queryParams.timezone = params.timezone;
    if (params?.limit != null) queryParams.limit = String(params.limit);
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request('GET', '/meetings', { params: queryParams });
  }

  /** Get a single meeting by ID. */
  async get(meetingId: string): Promise<{ data: AttioMeeting }> {
    return this.client.request('GET', `/meetings/${meetingId}`);
  }
}
