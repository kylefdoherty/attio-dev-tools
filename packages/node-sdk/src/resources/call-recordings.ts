import type { HttpClient } from '../client.js';
import type { AttioCallRecording, ListCallRecordingsParams, PaginatedResponse } from '../types.js';

export class CallRecordingsResource {
  constructor(private client: HttpClient) {}

  /** List call recordings for a meeting. */
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

  /** Get a single call recording by ID. */
  async get(
    meetingId: string,
    callRecordingId: string,
  ): Promise<{ data: AttioCallRecording }> {
    return this.client.request(
      'GET',
      `/meetings/${meetingId}/call_recordings/${callRecordingId}`,
    );
  }
}
