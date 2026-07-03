// attio-app-kit — sandbox-safe helpers for Attio App SDK apps.
// Web-standard APIs only: works in the Attio server sandbox, Node 18+, browsers.

// Minimal typed API client
export {
  type AttioApi,
  AttioApiError,
  type AttioApiOptions,
  attioApi,
  type QueryParams,
  type RequestOptions,
} from './attio-api.js';
// KV helpers
export type { AttioKV } from './kv.js';
export { type KvJson, kvJson } from './kv-json.js';
// Rate limiting for bulk write loops
export { createRateLimiter, type RateLimiter, type RateLimiterOptions } from './rate-limit.js';
// retryFetch — rate-limit-aware fetch retries
export {
  createRetryFetch,
  parseRetryAfter,
  type RetryFetchOptions,
  retryFetch,
} from './retry-fetch.js';
// Low-level crypto primitives (pure TS, WebCrypto fast path)
export {
  bytesToHex,
  hmacSha256,
  hmacSha256Hex,
  sha256,
  timingSafeEqualString,
  utf8,
} from './sha256.js';
// Attribute value builders + payload helpers
export {
  type ActorRefByEmailWrite,
  type ActorRefWrite,
  actorRef,
  actorRefByEmail,
  assertBody,
  type CheckboxWrite,
  type CurrencyWrite,
  checkbox,
  currency,
  type DateWrite,
  type DomainWrite,
  date,
  domain,
  type EmailAddressWrite,
  emailAddress,
  entryBody,
  type LocationInput,
  type LocationWrite,
  location,
  type NumberWrite,
  number,
  type PersonalNameWrite,
  type PhoneNumberWrite,
  personalName,
  phoneNumber,
  type RatingWrite,
  type RecordRefWrite,
  rating,
  recordBody,
  recordRef,
  recordRefByUnique,
  type SelectWrite,
  type StatusWrite,
  select,
  status,
  type TextWrite,
  type TimestampWrite,
  text,
  timestamp,
  type ValuesInput,
  v,
} from './values.js';
// Webhook signature verification + idempotency
export {
  type IdempotencyGuard,
  type IdempotencyGuardOptions,
  idempotencyGuard,
  verifyAttioSignature,
} from './webhooks.js';
