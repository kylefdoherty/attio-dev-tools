import type { HttpClient } from '../client.js';
import type { AttioTranscript, ListTranscriptParams } from '../types.js';

export class TranscriptsResource {
  constructor(private client: HttpClient) {}

  /** Get the transcript for a call recording. */
  async get(
    meetingId: string,
    callRecordingId: string,
    params?: ListTranscriptParams,
  ): Promise<AttioTranscript> {
    const queryParams: Record<string, string> = {};
    if (params?.limit != null) queryParams.limit = String(params.limit);
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request(
      'GET',
      `/meetings/${meetingId}/call_recordings/${callRecordingId}/transcript`,
      { params: queryParams },
    );
  }
}
