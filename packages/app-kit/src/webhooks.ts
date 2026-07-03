import type { AttioKV } from './kv.js';
import { hmacSha256Hex, timingSafeEqualString } from './sha256.js';

/**
 * Attio webhook helpers: signature verification and idempotency.
 *
 * Attio signs webhook deliveries with `Attio-Signature` (and a duplicate
 * `X-Attio-Signature`): a lowercase hex HMAC-SHA256 of the RAW request body
 * using the webhook secret (shown once, at webhook creation). Delivery is
 * at-least-once; the `Idempotency-Key` header dedupes retries.
 *
 * App Store code review REQUIRES signature verification on incoming webhooks.
 */

/**
 * Verify an Attio webhook signature.
 *
 * ```ts
 * // src/webhooks/attio.webhook.ts
 * export default async function handler(req: Request): Promise<Response> {
 *   const rawBody = await req.text(); // verify the RAW body, before JSON.parse
 *   const ok = await verifyAttioSignature(
 *     rawBody,
 *     req.headers.get("attio-signature") ?? "",
 *     secret,
 *   );
 *   if (!ok) return new Response("invalid signature", {status: 401});
 *   const payload = JSON.parse(rawBody);
 *   // ...
 *   return new Response(null, {status: 200});
 * }
 * ```
 *
 * Comparison is constant-time. Returns false (never throws) on a missing or
 * malformed header or empty secret.
 */
export async function verifyAttioSignature(
  rawBody: string,
  signatureHeader: string,
  secret: string,
): Promise<boolean> {
  if (!signatureHeader || !secret) return false;
  const received = signatureHeader.trim().toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(received)) return false;
  const expected = await hmacSha256Hex(secret, rawBody);
  return timingSafeEqualString(expected, received);
}

export interface IdempotencyGuardOptions {
  /** How long to remember seen keys. Default 86400 (24h — Attio retries span ~3 days, tune to taste). */
  ttlInSeconds?: number;
  /** KV key prefix. Default "idempotency:". */
  prefix?: string;
}

export interface IdempotencyGuard {
  /**
   * Atomically-ish claim a key: returns true the first time a key is seen
   * (and records it with the TTL), false for duplicates.
   */
  claim(key: string): Promise<boolean>;
  /** Check without claiming. */
  seen(key: string): Promise<boolean>;
  /** Forget a key — e.g. to allow a retry after your handler failed midway. */
  release(key: string): Promise<void>;
}

/**
 * Dedup webhook deliveries by `Idempotency-Key` using the Attio KV store.
 *
 * Pass the `kv` object from `attio/server` (typed structurally — this package
 * never imports the Attio SDK).
 *
 * ```ts
 * import {kv} from "attio/server";
 * const idem = idempotencyGuard(kv, {ttlInSeconds: 3 * 24 * 3600});
 *
 * const key = req.headers.get("idempotency-key");
 * if (key && !(await idem.claim(key))) {
 *   return new Response(null, {status: 200}); // duplicate delivery — ack and skip
 * }
 * ```
 *
 * Note: the Attio KV store has no compare-and-set, so `claim` is
 * check-then-set. Two truly concurrent deliveries of the same key can both
 * claim it — acceptable for webhook dedup (the goal is suppressing Attio's
 * retry redeliveries, which arrive seconds-to-minutes apart).
 */
export function idempotencyGuard(
  kv: AttioKV,
  options: IdempotencyGuardOptions = {},
): IdempotencyGuard {
  const ttlInSeconds = options.ttlInSeconds ?? 24 * 60 * 60;
  const prefix = options.prefix ?? 'idempotency:';

  return {
    async claim(key: string): Promise<boolean> {
      const kvKey = prefix + key;
      const existing = await kv.get(kvKey);
      if (existing != null) return false;
      await kv.set(kvKey, new Date().toISOString(), { ttlInSeconds });
      return true;
    },

    async seen(key: string): Promise<boolean> {
      return (await kv.get(prefix + key)) != null;
    },

    async release(key: string): Promise<void> {
      await kv.delete(prefix + key);
    },
  };
}
