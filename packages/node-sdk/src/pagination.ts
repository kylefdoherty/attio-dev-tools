/**
 * Options for configuring auto-pagination behavior.
 */
export interface PaginateOptions {
  /** Maximum number of items to yield in total. Defaults to Infinity (all items). */
  maxItems?: number;
  /** Number of items to fetch per page. Defaults to the API default (typically 25). */
  pageSize?: number;
}

// ---------------------------------------------------------------------------
// Offset-based pagination (records.query, entries.query, records.list, entries.list)
// ---------------------------------------------------------------------------

/**
 * Creates an async iterable that auto-paginates through offset-based endpoints.
 *
 * The caller provides a function that fetches one page given limit and offset.
 * The iterable yields individual items until the API returns fewer items than
 * the page size (indicating the last page) or maxItems is reached.
 *
 * @example
 * ```ts
 * const iterable = paginateOffset(
 *   (limit, offset) => client.records.query('people', { limit, offset }),
 *   { pageSize: 50 }
 * );
 * for await (const record of iterable) {
 *   console.log(record);
 * }
 * ```
 */
export function paginateOffset<T>(
  fetchPage: (limit: number, offset: number) => Promise<{ data: T[] }>,
  options?: PaginateOptions,
): AsyncIterable<T> {
  const pageSize = options?.pageSize ?? 25;
  const maxItems = options?.maxItems ?? Infinity;

  return {
    [Symbol.asyncIterator](): AsyncIterator<T> {
      let offset = 0;
      let yielded = 0;
      let done = false;
      let buffer: T[] = [];
      let bufferIndex = 0;

      return {
        async next(): Promise<IteratorResult<T>> {
          // Yield from buffer first
          if (bufferIndex < buffer.length) {
            if (yielded >= maxItems) {
              return { done: true, value: undefined };
            }
            yielded++;
            return { done: false, value: buffer[bufferIndex++] };
          }

          // If we've exhausted all pages, we're done
          if (done) {
            return { done: true, value: undefined };
          }

          // If we've yielded enough, we're done
          if (yielded >= maxItems) {
            return { done: true, value: undefined };
          }

          // Fetch the next page
          const result = await fetchPage(pageSize, offset);
          const items = result.data;
          offset += items.length;

          // If we got fewer items than pageSize, this is the last page
          if (items.length < pageSize) {
            done = true;
          }

          // If no items, we're done
          if (items.length === 0) {
            return { done: true, value: undefined };
          }

          // Load into buffer and yield first item
          buffer = items;
          bufferIndex = 1;
          yielded++;
          return { done: false, value: items[0] };
        },
      };
    },
  };
}

// ---------------------------------------------------------------------------
// Cursor-based pagination (views, files, meetings, call recordings, transcripts)
// ---------------------------------------------------------------------------

/**
 * Creates an async iterable that auto-paginates through cursor-based endpoints.
 *
 * The caller provides a function that fetches one page given an optional cursor.
 * The iterable yields individual items until there is no next_cursor or maxItems
 * is reached.
 *
 * @example
 * ```ts
 * const iterable = paginateCursor(
 *   (cursor) => client.files.list({ cursor, limit: 50 }),
 *   { pageSize: 50 }
 * );
 * for await (const file of iterable) {
 *   console.log(file);
 * }
 * ```
 */
export function paginateCursor<T>(
  fetchPage: (
    cursor?: string,
  ) => Promise<{ data: T[]; pagination: { next_cursor: string | null } }>,
  options?: PaginateOptions,
): AsyncIterable<T> {
  const maxItems = options?.maxItems ?? Infinity;

  return {
    [Symbol.asyncIterator](): AsyncIterator<T> {
      let cursor: string | undefined;
      let yielded = 0;
      let done = false;
      let buffer: T[] = [];
      let bufferIndex = 0;

      return {
        async next(): Promise<IteratorResult<T>> {
          // Yield from buffer first
          if (bufferIndex < buffer.length) {
            if (yielded >= maxItems) {
              return { done: true, value: undefined };
            }
            yielded++;
            return { done: false, value: buffer[bufferIndex++] };
          }

          // If we've exhausted all pages, we're done
          if (done) {
            return { done: true, value: undefined };
          }

          // If we've yielded enough, we're done
          if (yielded >= maxItems) {
            return { done: true, value: undefined };
          }

          // Fetch the next page
          const result = await fetchPage(cursor);
          const items = result.data;

          // Update cursor for next page
          if (result.pagination.next_cursor) {
            cursor = result.pagination.next_cursor;
          } else {
            done = true;
          }

          // If no items, we're done
          if (items.length === 0) {
            return { done: true, value: undefined };
          }

          // Load into buffer and yield first item
          buffer = items;
          bufferIndex = 1;
          yielded++;
          return { done: false, value: items[0] };
        },
      };
    },
  };
}

// ---------------------------------------------------------------------------
// Helpers to collect all items from an async iterable
// ---------------------------------------------------------------------------

/**
 * Collects all items from an async iterable into an array.
 *
 * @example
 * ```ts
 * const allRecords = await collectAll(client.records.queryAll('people'));
 * ```
 */
export async function collectAll<T>(iterable: AsyncIterable<T>): Promise<T[]> {
  const items: T[] = [];
  for await (const item of iterable) {
    items.push(item);
  }
  return items;
}
