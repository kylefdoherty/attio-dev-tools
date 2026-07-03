import type { AttioKV } from './kv.js';

/**
 * JSON wrapper over Attio's string-only KV store.
 *
 * The Attio KV store (`import {kv} from "attio/server"`) stores strings only —
 * this wrapper handles JSON.stringify/parse and passes TTL through.
 *
 * ```ts
 * import {kv} from "attio/server";
 * const store = kvJson(kv);
 * await store.set("sync-state", {cursor: "abc"}, {ttlInSeconds: 3600});
 * const state = await store.get<{cursor: string}>("sync-state");
 * ```
 */

export interface KvJson {
  /**
   * Read and parse a JSON value. Returns null when the key is missing or the
   * stored string is not valid JSON (treat corrupt entries as cache misses).
   */
  get<T = unknown>(key: string): Promise<T | null>;
  /** JSON-encode and store a value, optionally with a TTL. */
  set<T>(key: string, value: T, options?: { ttlInSeconds?: number }): Promise<void>;
  /** Remove a key. */
  delete(key: string): Promise<void>;
}

export function kvJson(kv: AttioKV): KvJson {
  return {
    async get<T = unknown>(key: string): Promise<T | null> {
      const entry = await kv.get(key);
      if (entry == null) return null;
      try {
        return JSON.parse(entry.value) as T;
      } catch {
        return null;
      }
    },

    async set<T>(key: string, value: T, options?: { ttlInSeconds?: number }): Promise<void> {
      const encoded = JSON.stringify(value);
      if (encoded === undefined) {
        // JSON.stringify(undefined) and stringify(function) return undefined,
        // which would store the literal string "undefined" or crash the KV.
        throw new TypeError(`kvJson.set("${key}"): value is not JSON-serializable`);
      }
      if (options?.ttlInSeconds !== undefined) {
        await kv.set(key, encoded, { ttlInSeconds: options.ttlInSeconds });
      } else {
        await kv.set(key, encoded);
      }
    },

    async delete(key: string): Promise<void> {
      await kv.delete(key);
    },
  };
}
