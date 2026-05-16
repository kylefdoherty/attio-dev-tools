import { describe, it, expect, vi } from 'vitest';
import { paginateOffset, paginateCursor, collectAll } from '../src/pagination.js';

// ---------------------------------------------------------------------------
// paginateOffset
// ---------------------------------------------------------------------------

describe('paginateOffset', () => {
  it('iterates through multiple pages until a short page', async () => {
    const pages = [
      { data: [{ id: 1 }, { id: 2 }] },
      { data: [{ id: 3 }, { id: 4 }] },
      { data: [{ id: 5 }] }, // short page signals end
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async (_limit: number, _offset: number) => pages[callIndex++]);

    const items = await collectAll(paginateOffset(fetchPage, { pageSize: 2 }));

    expect(items).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }, { id: 5 }]);
    expect(fetchPage).toHaveBeenCalledTimes(3);
    expect(fetchPage).toHaveBeenNthCalledWith(1, 2, 0);
    expect(fetchPage).toHaveBeenNthCalledWith(2, 2, 2);
    expect(fetchPage).toHaveBeenNthCalledWith(3, 2, 4);
  });

  it('stops when an empty page is returned', async () => {
    const pages = [
      { data: [{ id: 1 }, { id: 2 }] },
      { data: [] as { id: number }[] },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async () => pages[callIndex++]);

    const items = await collectAll(paginateOffset(fetchPage, { pageSize: 2 }));

    expect(items).toEqual([{ id: 1 }, { id: 2 }]);
    expect(fetchPage).toHaveBeenCalledTimes(2);
  });

  it('returns empty array when first page is empty', async () => {
    const fetchPage = vi.fn(async () => ({ data: [] as { id: number }[] }));

    const items = await collectAll(paginateOffset(fetchPage, { pageSize: 10 }));

    expect(items).toEqual([]);
    expect(fetchPage).toHaveBeenCalledTimes(1);
  });

  it('respects maxItems limit', async () => {
    const pages = [
      { data: [{ id: 1 }, { id: 2 }, { id: 3 }] },
      { data: [{ id: 4 }, { id: 5 }, { id: 6 }] },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async () => pages[callIndex++]);

    const items = await collectAll(paginateOffset(fetchPage, { pageSize: 3, maxItems: 4 }));

    expect(items).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }]);
    // Fetches 2 pages: first yields 3 items, second fetches to get the 4th
    expect(fetchPage).toHaveBeenCalledTimes(2);
  });

  it('maxItems=0 yields nothing', async () => {
    const fetchPage = vi.fn(async () => ({ data: [{ id: 1 }] }));

    const items = await collectAll(paginateOffset(fetchPage, { maxItems: 0 }));

    expect(items).toEqual([]);
    // Should not even fetch a page since maxItems is 0
    expect(fetchPage).toHaveBeenCalledTimes(0);
  });

  it('uses default pageSize of 25 when not specified', async () => {
    const fetchPage = vi.fn(async () => ({ data: [] as { id: number }[] }));

    await collectAll(paginateOffset(fetchPage));

    expect(fetchPage).toHaveBeenCalledWith(25, 0);
  });

  it('handles a single page that fills pageSize exactly', async () => {
    const pages = [
      { data: [{ id: 1 }, { id: 2 }] },
      { data: [] as { id: number }[] },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async () => pages[callIndex++]);

    const items = await collectAll(paginateOffset(fetchPage, { pageSize: 2 }));

    expect(items).toEqual([{ id: 1 }, { id: 2 }]);
    // Must fetch a second page to know there are no more items
    expect(fetchPage).toHaveBeenCalledTimes(2);
  });

  it('works with for-await-of', async () => {
    const pages = [
      { data: ['a', 'b'] },
      { data: ['c'] },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async () => pages[callIndex++]);

    const items: string[] = [];
    for await (const item of paginateOffset(fetchPage, { pageSize: 2 })) {
      items.push(item);
    }

    expect(items).toEqual(['a', 'b', 'c']);
  });

  it('can be broken out of early', async () => {
    const fetchPage = vi.fn(async () => ({
      data: [{ id: 1 }, { id: 2 }, { id: 3 }],
    }));

    const items: { id: number }[] = [];
    for await (const item of paginateOffset(fetchPage, { pageSize: 3 })) {
      items.push(item);
      if (items.length === 2) break;
    }

    expect(items).toEqual([{ id: 1 }, { id: 2 }]);
    // Only fetched one page before breaking
    expect(fetchPage).toHaveBeenCalledTimes(1);
  });

  it('propagates errors from fetchPage', async () => {
    const fetchPage = vi.fn(async () => {
      throw new Error('API error');
    });

    await expect(collectAll(paginateOffset(fetchPage))).rejects.toThrow('API error');
  });
});

// ---------------------------------------------------------------------------
// paginateCursor
// ---------------------------------------------------------------------------

describe('paginateCursor', () => {
  it('iterates through multiple pages using cursors', async () => {
    const pages = [
      { data: [{ id: 1 }], pagination: { next_cursor: 'cursor_2' } },
      { data: [{ id: 2 }], pagination: { next_cursor: 'cursor_3' } },
      { data: [{ id: 3 }], pagination: { next_cursor: null } },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async (_cursor?: string) => pages[callIndex++]);

    const items = await collectAll(paginateCursor(fetchPage));

    expect(items).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);
    expect(fetchPage).toHaveBeenCalledTimes(3);
    expect(fetchPage).toHaveBeenNthCalledWith(1, undefined);
    expect(fetchPage).toHaveBeenNthCalledWith(2, 'cursor_2');
    expect(fetchPage).toHaveBeenNthCalledWith(3, 'cursor_3');
  });

  it('stops when next_cursor is null on first page', async () => {
    const fetchPage = vi.fn(async () => ({
      data: [{ id: 1 }],
      pagination: { next_cursor: null },
    }));

    const items = await collectAll(paginateCursor(fetchPage));

    expect(items).toEqual([{ id: 1 }]);
    expect(fetchPage).toHaveBeenCalledTimes(1);
  });

  it('returns empty array when first page has no data', async () => {
    const fetchPage = vi.fn(async () => ({
      data: [] as { id: number }[],
      pagination: { next_cursor: null },
    }));

    const items = await collectAll(paginateCursor(fetchPage));

    expect(items).toEqual([]);
    expect(fetchPage).toHaveBeenCalledTimes(1);
  });

  it('respects maxItems limit', async () => {
    const pages = [
      { data: [{ id: 1 }, { id: 2 }], pagination: { next_cursor: 'c2' } },
      { data: [{ id: 3 }, { id: 4 }], pagination: { next_cursor: null } },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async () => pages[callIndex++]);

    const items = await collectAll(paginateCursor(fetchPage, { maxItems: 3 }));

    expect(items).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);
  });

  it('maxItems=0 yields nothing', async () => {
    const fetchPage = vi.fn(async () => ({
      data: [{ id: 1 }],
      pagination: { next_cursor: null },
    }));

    const items = await collectAll(paginateCursor(fetchPage, { maxItems: 0 }));

    expect(items).toEqual([]);
    expect(fetchPage).toHaveBeenCalledTimes(0);
  });

  it('works with for-await-of', async () => {
    const pages = [
      { data: ['a', 'b'], pagination: { next_cursor: 'c2' } },
      { data: ['c'], pagination: { next_cursor: null } },
    ];
    let callIndex = 0;
    const fetchPage = vi.fn(async () => pages[callIndex++]);

    const items: string[] = [];
    for await (const item of paginateCursor(fetchPage)) {
      items.push(item);
    }

    expect(items).toEqual(['a', 'b', 'c']);
  });

  it('can be broken out of early', async () => {
    const fetchPage = vi.fn(async () => ({
      data: [{ id: 1 }, { id: 2 }, { id: 3 }],
      pagination: { next_cursor: 'more' },
    }));

    const items: { id: number }[] = [];
    for await (const item of paginateCursor(fetchPage)) {
      items.push(item);
      if (items.length === 2) break;
    }

    expect(items).toEqual([{ id: 1 }, { id: 2 }]);
    expect(fetchPage).toHaveBeenCalledTimes(1);
  });

  it('propagates errors from fetchPage', async () => {
    const fetchPage = vi.fn(async () => {
      throw new Error('Cursor error');
    });

    await expect(collectAll(paginateCursor(fetchPage))).rejects.toThrow('Cursor error');
  });
});

// ---------------------------------------------------------------------------
// collectAll
// ---------------------------------------------------------------------------

describe('collectAll', () => {
  it('collects items from an async iterable', async () => {
    async function* gen() {
      yield 1;
      yield 2;
      yield 3;
    }
    const result = await collectAll(gen());
    expect(result).toEqual([1, 2, 3]);
  });

  it('returns empty array for empty iterable', async () => {
    async function* gen() {
      // empty
    }
    const result = await collectAll(gen());
    expect(result).toEqual([]);
  });
});
