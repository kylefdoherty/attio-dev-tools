# attio-app-kit

Sandbox-safe TypeScript helpers for building [Attio App SDK](https://docs.attio.com/sdk/overview) apps — the apps that run **inside** Attio (`npm create attio`): server functions, webhook handlers, and workflow blocks.

Zero runtime dependencies. Web-standard APIs only.

> **This project is not affiliated with, endorsed by, or associated with Attio.**

---

## Why this exists

The Attio app server runtime is **not Node.js**. It is a browser-like sandbox with only web globals: `fetch`, `Request`/`Response`/`Headers`, `URL`, `TextEncoder`/`TextDecoder`, timers, `console`, and standard JavaScript. There is no `node:crypto`, no `fs`, no `Buffer` — npm packages that touch Node built-ins break at import time.

That rules out most HTTP/retry/crypto utility libraries. This kit fills the gap with small, independently importable modules that use web-standard APIs exclusively, so the same code runs in the Attio sandbox, Node 18+, and browsers:

- **`retryFetch`** — fetch with Attio-aware retries (429 `Retry-After` is an HTTP-**date**, not seconds)
- **`createRateLimiter`** — token-bucket throttling for bulk write loops (Attio has no bulk endpoints; 25 writes/s limit)
- **`verifyAttioSignature`** — webhook HMAC verification (required for App Store review) with a pure-TS SHA-256 fallback, since the sandbox does not document WebCrypto
- **`idempotencyGuard`** / **`kvJson`** — dedup and JSON storage over Attio's string-only KV store
- **`v.*` value builders** — Attio's 17 attribute types have sharp write-form edge rules (atomic locations, all-3-field personal names, E.164 phones); the builders enforce them
- **`attioApi`** — a tiny typed client for `api.attio.com/v2` from server functions (deliberately minimal — the full SDK is [`attio-node`](../node-sdk), which targets Node)

This package never imports `attio/server` — anything it needs from the Attio SDK (like the `kv` store) is accepted as a parameter and typed structurally.

## Install

Not yet published. From this monorepo:

```bash
cd packages/app-kit && yarn install && yarn build
```

Requires TypeScript-side Node 18+ for building/testing; the built output runs anywhere web globals exist.

---

## retryFetch

Retries on 429 (honoring `Retry-After`), 5xx, and network errors, with exponential backoff + jitter. Never retries other 4xx or aborted requests. Attio sends `Retry-After` as an HTTP-date (usually the next second) — both the date and delta-seconds forms are parsed.

```ts
import {retryFetch, createRetryFetch} from "attio-app-kit";

const response = await retryFetch("https://api.example.com/things", {
  method: "POST",
  body: JSON.stringify(payload),
});

// Or bake options into a fetch-compatible function:
const fetchWithRetry = createRetryFetch({maxRetries: 5, baseDelayMs: 500});
```

Defaults: `maxRetries: 3`, `baseDelayMs: 1000` (backoff 1s/2s/4s), `maxDelayMs: 30000`, `maxElapsedMs: 25000` — Attio server functions have a hard 30s timeout, so retrying stops with headroom to spare. All configurable, plus `onRetry` for logging and `retryOnStatus` to customize what retries.

On retry exhaustion the last `Response` is returned (fetch semantics — HTTP status is not an exception); network errors rethrow.

## createRateLimiter

Attio enforces 100 reads/s and 25 writes/s, and has **no bulk endpoints** — bulk work is a loop of single requests that must self-throttle. Token bucket with optional concurrency cap; no background timers (safe to hold in a sandbox module).

```ts
import {createRateLimiter, attioApi, assertBody, v} from "attio-app-kit";

const limiter = createRateLimiter({requestsPerSecond: 20, maxConcurrent: 5});

await Promise.all(
  rows.map((row) =>
    limiter.run(() =>
      api.put("/objects/people/records", assertBody({
        email_addresses: [v.emailAddress(row.email)],
      }), {query: {matching_attribute: "email_addresses"}}),
    ),
  ),
);
```

`limiter.acquire()` is also exposed for manual loops. Stay at ~20/s for writes to leave room for retries and other integrations in the workspace (query complexity limits are shared across all tokens).

## Webhook signature verification

Attio signs deliveries with `Attio-Signature`: a hex HMAC-SHA256 of the **raw** request body using the webhook secret (shown once at creation). App Store code review requires verification.

```ts
// src/webhooks/attio.webhook.ts
import {verifyAttioSignature, idempotencyGuard} from "attio-app-kit";
import {kv} from "attio/server";

const idem = idempotencyGuard(kv, {ttlInSeconds: 3 * 24 * 3600});

export default async function handler(req: Request): Promise<Response> {
  const rawBody = await req.text(); // verify BEFORE JSON.parse
  const ok = await verifyAttioSignature(
    rawBody,
    req.headers.get("attio-signature") ?? "",
    secret,
  );
  if (!ok) return new Response("invalid signature", {status: 401});

  // Attio delivers at-least-once — dedup on Idempotency-Key:
  const key = req.headers.get("idempotency-key");
  if (key && !(await idem.claim(key))) {
    return new Response(null, {status: 200}); // duplicate — ack and skip
  }

  const payload = JSON.parse(rawBody);
  // ... respond 2xx within 5 seconds or the delivery counts as failed
  return new Response(null, {status: 200});
}
```

Comparison is constant-time; malformed headers return `false` rather than throwing.

**Crypto note:** Attio's documented sandbox globals do **not** include WebCrypto (`crypto.subtle`), so this module ships a pure-TypeScript SHA-256/HMAC (verified against FIPS 180-4 and RFC 4231 test vectors). When `crypto.subtle` *is* detected at runtime (Node 18+, browsers, or if Attio adds it), it is used automatically. The primitives (`sha256`, `hmacSha256`, `hmacSha256Hex`) are exported if you need them for other providers' webhooks.

`idempotencyGuard(kv)` accepts the KV store as a parameter (structural typing — no `attio/server` import). It is check-then-set: the Attio KV has no compare-and-set, so two *truly simultaneous* duplicate deliveries could both claim; that's fine for suppressing Attio's retry redeliveries, which arrive well apart.

## kvJson

The Attio KV store (`import {kv} from "attio/server"`) stores **strings only**. `kvJson` adds JSON encoding with TTL passthrough:

```ts
import {kvJson} from "attio-app-kit";
import {kv} from "attio/server";

const store = kvJson(kv);
await store.set("sync-state", {cursor: "abc", page: 2}, {ttlInSeconds: 3600});
const state = await store.get<{cursor: string; page: number}>("sync-state");
await store.delete("sync-state");
```

Missing keys and corrupt (non-JSON) values both read as `null` — treat them as cache misses. Storing `null` is legal but indistinguishable from a missing key on read.

## Value builders (`v.*`)

Typed builders for Attio's attribute write forms, enforcing each type's edge rules. 16 of the 17 attribute types are writable (`interaction` is system-managed/read-only, so it has no builder).

```ts
import {v, recordBody, assertBody, entryBody} from "attio-app-kit";

const body = recordBody({
  name: v.personalName({first: "Jane", last: "Doe"}), // all-3-fields rule handled
  email_addresses: [v.emailAddress("jane@acme.com")],
  company: v.recordRefByUnique({
    targetObject: "companies",
    matchingAttribute: "domains",
    value: "acme.com",
  }),
  stage: v.status("Qualified"),      // unknown titles ERROR — create statuses first
  deal_value: v.currency(15000),     // code is attribute-wide config, not per value
  priority: v.rating(4),             // integer 0–5 enforced
  kickoff: v.date("2026-07-03"),
  last_seen: v.timestamp(new Date()),
  tags: [v.select("Tier 1"), v.select("Partner")], // multiselect = array
  phone_numbers: [v.phoneNumber("+15551234567")],  // E.164 enforced
  owner: v.actorRefByEmail("kyle@example.com"),
  hq: v.location({locality: "Denver", region: "CO", countryCode: "US"}),
});

await api.post("/objects/people/records", body);
```

Rules the builders enforce for you:

| Builder | Edge rule |
|---|---|
| `v.personalName({first, last, full?})` | Object writes require **all three** fields — `full_name` is derived when omitted. `v.personalName("Doe, Jane")` passes the string form through. |
| `v.location({...})` | Object writes are **atomic** — every one of the 10 fields must be present; omitted fields are filled with `null` (which clears them — merge with existing values first if needed). |
| `v.status(...)` / `v.select(...)` | Unknown titles error server-side (never auto-created) — the JSDoc reminds you. |
| `v.phoneNumber(...)` | Requires E.164 (`+...`) or an explicit `countryCode`. |
| `v.recordRef(...)` | Target record must already exist — write parents before children. |
| `v.domain(...)` | Extracts the hostname from URLs (Attio stores domains, not URLs). |
| `v.rating(...)` | Integer 0–5. |

Payload helpers: `recordBody(values)` → `{data: {values}}` for create/update, `assertBody(values)` for upserts (the `matching_attribute` goes in the query string), `entryBody({parentObject, parentRecordId, entryValues})` for list entries.

## attioApi

A deliberately tiny typed client for calling `api.attio.com/v2` from server functions, with `retryFetch` baked in:

```ts
import {ATTIO_API_TOKEN} from "attio/server";
import {attioApi, AttioApiError} from "attio-app-kit";

const api = attioApi(ATTIO_API_TOKEN);

const {data} = await api.post<{data: AttioRecord[]}>(
  "/objects/people/records/query",
  {filter: {name: {$contains: "Jane"}}, limit: 10},
);

try {
  await api.del(`/objects/people/records/${recordId}`);
} catch (error) {
  if (error instanceof AttioApiError && error.status === 404) {
    // already gone
  } else {
    throw error;
  }
}
```

`get`/`post`/`put`/`patch`/`del` plus a `request()` escape hatch. Non-2xx responses throw `AttioApiError` with `status`, Attio's `code` and `type`, the parsed `body`, and the `method`/`path`. Rate limits and 5xx are retried automatically (tunable via the `retry` option).

This is **not** a full SDK — no resource methods, no pagination helpers. For that, use [`attio-node`](../node-sdk) in Node environments; `attioApi` exists because the full SDK doesn't need to be dragged into a 30-second sandbox function.

---

## Development

```bash
yarn install
yarn test          # vitest unit suite (HMAC test vectors, Retry-After parsing, builder rules, ...)
yarn typecheck     # tsc --noEmit
yarn check         # biome lint + format check
yarn build         # emit ESM + d.ts to dist/
```

## License

MIT
