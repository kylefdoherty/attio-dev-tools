import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateCursor } from '../pagination.js';
import type { GetTranscriptParams, TranscriptResponse, TranscriptSegment } from '../types.js';

export class TranscriptsResource {
  constructor(private client: HttpClient) {}

  /**
   * Get one page of the transcript for a call recording. (beta)
   *
   * Cursor-paginated: segments are in `data.transcript`; pass `cursor` from
   * `pagination.next_cursor` to fetch the next page, or use {@link segments}
   * to iterate automatically.
   */
  async get(
    meetingId: string,
    callRecordingId: string,
    params?: GetTranscriptParams,
  ): Promise<TranscriptResponse> {
    const queryParams: Record<string, string> = {};
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request(
      'GET',
      `/meetings/${meetingId}/call_recordings/${callRecordingId}/transcript`,
      { params: queryParams },
    );
  }

  /**
   * Auto-paginating iterator that yields individual transcript segments. (beta)
   * Wraps get() and automatically follows `pagination.next_cursor`.
   *
   * @example
   * ```ts
   * for await (const segment of client.transcripts.segments(meetingId, recordingId)) {
   *   console.log(`${segment.speaker.name}: ${segment.speech}`);
   * }
   * ```
   */
  segments(
    meetingId: string,
    callRecordingId: string,
    options?: PaginateOptions,
  ): AsyncIterable<TranscriptSegment> {
    return paginateCursor(async (cursor) => {
      const page = await this.get(meetingId, callRecordingId, { cursor });
      return { data: page.data.transcript, pagination: page.pagination };
    }, options);
  }
}
