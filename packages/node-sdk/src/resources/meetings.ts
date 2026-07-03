import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateCursor } from '../pagination.js';
import type {
  AttioMeeting,
  CreateMeetingParams,
  ListMeetingsParams,
  PaginatedResponse,
} from '../types.js';

export class MeetingsResource {
  constructor(private client: HttpClient) {}

  /**
   * List meetings, optionally filtered by linked record, participants, or time range. (beta)
   *
   * Cursor-paginated: pass `cursor` from `pagination.next_cursor` to fetch the
   * next page, or use {@link listAll} to iterate automatically.
   */
  async list(params?: ListMeetingsParams): Promise<PaginatedResponse<AttioMeeting>> {
    const queryParams: Record<string, string> = {};
    if (params?.linked_object) queryParams.linked_object = params.linked_object;
    if (params?.linked_record_id) queryParams.linked_record_id = params.linked_record_id;
    if (params?.participants) {
      queryParams.participants = Array.isArray(params.participants)
        ? params.participants.join(',')
        : params.participants;
    }
    if (params?.sort) queryParams.sort = params.sort;
    if (params?.ends_from) queryParams.ends_from = params.ends_from;
    if (params?.starts_before) queryParams.starts_before = params.starts_before;
    if (params?.timezone) queryParams.timezone = params.timezone;
    if (params?.limit != null) queryParams.limit = String(params.limit);
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request('GET', '/meetings', { params: queryParams });
  }

  /** Get a single meeting by ID. (beta) */
  async get(meetingId: string): Promise<{ data: AttioMeeting }> {
    return this.client.request('GET', `/meetings/${meetingId}`);
  }

  /**
   * Find or create a meeting, matched by `external_ref`. (alpha)
   *
   * Person and company records are automatically created and linked from
   * participant emails (company linking is asynchronous).
   *
   * **Alpha:** this endpoint may be subject to breaking changes as Attio
   * gathers feedback. There are no meeting update or delete endpoints.
   */
  async create(params: CreateMeetingParams): Promise<{ data: AttioMeeting }> {
    return this.client.request('POST', '/meetings', { body: params });
  }

  /**
   * Auto-paginating list that yields individual meetings. (beta)
   * Wraps list() and automatically follows `pagination.next_cursor`.
   *
   * @example
   * ```ts
   * for await (const meeting of client.meetings.listAll({ participants: 'jane@acme.com' })) {
   *   console.log(meeting.title);
   * }
   * ```
   */
  listAll(
    params?: Omit<ListMeetingsParams, 'limit' | 'cursor'>,
    options?: PaginateOptions,
  ): AsyncIterable<AttioMeeting> {
    return paginateCursor(
      (cursor) => this.list({ ...params, limit: options?.pageSize, cursor }),
      options,
    );
  }
}
