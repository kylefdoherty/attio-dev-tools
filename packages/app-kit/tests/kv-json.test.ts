import { describe, expect, it } from 'vitest';
import type { AttioKV } from '../src/kv.js';
import { kvJson } from '../src/kv-json.js';

function fakeKV(): AttioKV & { raw: Map<string, string>; lastSetOptions?: { ttlInSeconds?: number } } {
  const raw = new Map<string, string>();
  const store: AttioKV & { raw: Map<string, string>; lastSetOptions?: { ttlInSeconds?: number } } = {
    raw,
    async get(key) {
      return raw.has(key) ? { value: raw.get(key) as string } : null;
    },
    async set(key, value, options) {
      store.lastSetOptions = options;
      raw.set(key, value);
    },
    async delete(key) {
      raw.delete(key);
    },
  };
  return store;
}

describe('kvJson', () => {
  it('round-trips objects, arrays, strings, numbers, booleans', async () => {
    const store = kvJson(fakeKV());
    const cases: unknown[] = [
      { a: 1, b: { nested: ['x', 'y'] } },
      [1, 2, 3],
      'plain string',
      42.5,
      true,
      false,
      0,
      '',
    ];
    for (const [i, value] of cases.entries()) {
      await store.set(`k${i}`, value);
      expect(await store.get(`k${i}`)).toEqual(value);
    }
  });

  it('stores JSON strings in the underlying KV', async () => {
    const kv = fakeKV();
    const store = kvJson(kv);
    await store.set('key', { cursor: 'abc' });
    expect(kv.raw.get('key')).toBe('{"cursor":"abc"}');
  });

  it('returns null for missing keys', async () => {
    const store = kvJson(fakeKV());
    expect(await store.get('nope')).toBeNull();
  });

  it('returns null for corrupt (non-JSON) stored values', async () => {
    const kv = fakeKV();
    kv.raw.set('bad', 'not json {');
    const store = kvJson(kv);
    expect(await store.get('bad')).toBeNull();
  });

  it('passes ttlInSeconds through to the KV', async () => {
    const kv = fakeKV();
    const store = kvJson(kv);
    await store.set('key', 1, { ttlInSeconds: 300 });
    expect(kv.lastSetOptions).toEqual({ ttlInSeconds: 300 });
  });

  it('omits options entirely when no TTL is given', async () => {
    const kv = fakeKV();
    const store = kvJson(kv);
    await store.set('key', 1);
    expect(kv.lastSetOptions).toBeUndefined();
  });

  it('deletes keys', async () => {
    const kv = fakeKV();
    const store = kvJson(kv);
    await store.set('key', 'v');
    await store.delete('key');
    expect(await store.get('key')).toBeNull();
    expect(kv.raw.has('key')).toBe(false);
  });

  it('throws on non-serializable values (undefined)', async () => {
    const store = kvJson(fakeKV());
    await expect(store.set('key', undefined)).rejects.toThrow(/not JSON-serializable/);
  });

  it('note: stored null round-trips to null (indistinguishable from missing)', async () => {
    const store = kvJson(fakeKV());
    await store.set('key', null);
    expect(await store.get('key')).toBeNull();
  });

  it('supports typed reads', async () => {
    const store = kvJson(fakeKV());
    await store.set('state', { cursor: 'c1', page: 2 });
    const state = await store.get<{ cursor: string; page: number }>('state');
    expect(state?.cursor).toBe('c1');
    expect(state?.page).toBe(2);
  });
});
