import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateCursor } from '../pagination.js';
import type {
  AttioCallRecording,
  CreateCallRecordingParams,
  ListCallRecordingsParams,
  PaginatedResponse,
} from '../types.js';

export class CallRecordingsResource {
  constructor(private client: HttpClient) {}

  /**
   * List call recordings for a meeting. (beta)
   *
   * Cursor-paginated: pass `cursor` from `pagination.next_cursor` to fetch the
   * next page, or use {@link listAll} to iterate automatically.
   */
  async list(
    meetingId: string,
    params?: ListCallRecordingsParams,
  ): Promise<PaginatedResponse<AttioCallRecording>> {
    const queryParams: Record<string, string> = {};
    if (params?.limit != null) queryParams.limit = String(params.limit);
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request('GET', `/meetings/${meetingId}/call_recordings`, {
      params: queryParams,
    });
  }

  /** Get a single call recording by ID. (beta) */
  async get(meetingId: string, callRecordingId: string): Promise<{ data: AttioCallRecording }> {
    return this.client.request('GET', `/meetings/${meetingId}/call_recordings/${callRecordingId}`);
  }

  /**
   * Create a call recording for a meeting from a publicly accessible video URL. (alpha)
   *
   * The video is downloaded asynchronously; the recording starts in
   * `processing` status and transitions to `completed` or `failed`.
   *
   * **Alpha:** this endpoint may be subject to breaking changes as Attio
   * gathers feedback. It is rate limited to 1 request per second.
   */
  async create(
    meetingId: string,
    params: CreateCallRecordingParams,
  ): Promise<{ data: AttioCallRecording }> {
    return this.client.request('POST', `/meetings/${meetingId}/call_recordings`, {
      body: params,
    });
  }

  /**
   * Delete a call recording and all associated data. (alpha)
   *
   * **Alpha:** this endpoint may be subject to breaking changes as Attio
   * gathers feedback.
   */
  async delete(meetingId: string, callRecordingId: string): Promise<void> {
    await this.client.request(
      'DELETE',
      `/meetings/${meetingId}/call_recordings/${callRecordingId}`,
    );
  }

  /**
   * Auto-paginating list that yields individual call recordings. (beta)
   * Wraps list() and automatically follows `pagination.next_cursor`.
   *
   * @example
   * ```ts
   * for await (const recording of client.callRecordings.listAll(meetingId)) {
   *   console.log(recording.status);
   * }
   * ```
   */
  listAll(meetingId: string, options?: PaginateOptions): AsyncIterable<AttioCallRecording> {
    return paginateCursor(
      (cursor) => this.list(meetingId, { limit: options?.pageSize, cursor }),
      options,
    );
  }
}
