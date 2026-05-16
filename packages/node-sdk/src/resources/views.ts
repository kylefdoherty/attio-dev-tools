import type { HttpClient } from '../client.js';
import type { AttioView, ListViewsParams, PaginatedResponse } from '../types.js';

type Target = 'objects' | 'lists';

export class ViewsResource {
  constructor(private client: HttpClient) {}

  /** List saved views on an object or list. */
  async list(
    target: Target,
    targetIdOrSlug: string,
    params?: ListViewsParams,
  ): Promise<PaginatedResponse<AttioView>> {
    const queryParams: Record<string, string> = {};
    if (params?.show_archived != null) queryParams.show_archived = String(params.show_archived);
    if (params?.limit != null) queryParams.limit = String(params.limit);
    if (params?.cursor) queryParams.cursor = params.cursor;
    return this.client.request('GET', `/${target}/${targetIdOrSlug}/views`, {
      params: queryParams,
    });
  }
}
