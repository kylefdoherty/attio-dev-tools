import type { HttpClient } from '../client.js';
import { type PaginateOptions, paginateCursor } from '../pagination.js';
import type { AttioView, ListViewsParams, PaginatedResponse } from '../types.js';

type Target = 'objects' | 'lists';

export class ViewsResource {
  constructor(private client: HttpClient) {}

  /**
   * List saved views on an object or list.
   *
   * Use a view's `id.view_id` as `filter_view_id` when querying records or
   * entries to reuse the view's saved filter.
   *
   * Cursor-paginated: pass `cursor` from `pagination.next_cursor` to fetch the
   * next page, or use {@link listAll} to iterate automatically.
   */
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

  /**
   * Auto-paginating list that yields individual views.
   * Wraps list() and automatically follows `pagination.next_cursor`.
   *
   * @example
   * ```ts
   * for await (const view of client.views.listAll('objects', 'deals')) {
   *   console.log(view.title);
   * }
   * ```
   */
  listAll(
    target: Target,
    targetIdOrSlug: string,
    params?: Omit<ListViewsParams, 'limit' | 'cursor'>,
    options?: PaginateOptions,
  ): AsyncIterable<AttioView> {
    return paginateCursor(
      (cursor) =>
        this.list(target, targetIdOrSlug, { ...params, limit: options?.pageSize, cursor }),
      options,
    );
  }
}
