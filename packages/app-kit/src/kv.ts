/**
 * Structural type for the Attio App SDK KV store (`import {kv} from "attio/server"`).
 *
 * Typed structurally on purpose: this package has zero dependencies and never
 * imports `attio/server`. Pass the real `kv` object in — anything with the
 * same shape (including an in-memory fake in tests) works.
 *
 * The Attio KV store holds STRINGS ONLY and supports per-key TTL.
 */

type MaybePromise<T> = T | Promise<T>;

export interface AttioKV {
  /** Returns `{value}` if the key exists, or null. */
  get(key: string): MaybePromise<{ value: string } | null | undefined>;
  /** Set a string value, optionally expiring after `ttlInSeconds`. */
  set(key: string, value: string, options?: { ttlInSeconds?: number }): MaybePromise<unknown>;
  /** Remove a key. */
  delete(key: string): MaybePromise<unknown>;
}
