/**
 * A `fetch` wrapper with retries tuned for the Attio REST API.
 *
 * Retries on:
 * - HTTP 429 — honoring the `Retry-After` header. Attio sends `Retry-After`
 *   as an HTTP-date (usually the next second), NOT a number of seconds; both
 *   forms are parsed.
 * - HTTP 5xx — exponential backoff with jitter.
 * - Network errors (fetch rejecting with e.g. TypeError) — same backoff.
 *
 * Never retries other 4xx, and never retries an aborted request. On retry
 * exhaustion the last Response is returned (fetch semantics: HTTP status is
 * not an exception) or the last network error is rethrown.
 *
 * Uses only web-standard APIs (fetch, setTimeout) so it runs in the Attio
 * server sandbox, Node 18+, and browsers.
 */

export interface RetryFetchOptions {
  /** Maximum number of retries after the initial attempt. Default 3. */
  maxRetries?: number;
  /** Base delay for exponential backoff in ms. Default 1000. */
  baseDelayMs?: number;
  /** Upper bound on any single delay (including Retry-After) in ms. Default 30000. */
  maxDelayMs?: number;
  /**
   * Give up (returning/throwing the last result) once sleeping again would
   * exceed this total elapsed time in ms. Default 25000 — Attio server
   * functions have a hard 30s timeout, so leave headroom.
   */
  maxElapsedMs?: number;
  /** Apply equal jitter (delay * [0.5, 1.0)) to backoff delays. Default true. */
  jitter?: boolean;
  /** Decide which HTTP statuses to retry. Default: 429 and 5xx. */
  retryOnStatus?: (status: number) => boolean;
  /** Underlying fetch. Default: globalThis.fetch. */
  fetch?: typeof fetch;
  /** Observe retries (logging/metrics). */
  onRetry?: (info: { attempt: number; delayMs: number; status?: number; error?: unknown }) => void;
  /** Injectable clock/sleep/random for deterministic tests. */
  now?: () => number;
  sleep?: (ms: number) => Promise<void>;
  random?: () => number;
}

const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_BASE_DELAY_MS = 1000;
const DEFAULT_MAX_DELAY_MS = 30_000;
const DEFAULT_MAX_ELAPSED_MS = 25_000;

function defaultSleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function defaultRetryOnStatus(status: number): boolean {
  return status === 429 || (status >= 500 && status <= 599);
}

/**
 * Parse a `Retry-After` header value into a delay in milliseconds.
 *
 * Accepts both forms from RFC 9110: delay-seconds (`"2"`, `"1.5"`) and an
 * HTTP-date (`"Wed, 01 Jul 2026 12:00:01 GMT"`). Attio uses the HTTP-date
 * form. Returns null if the value is missing or unparseable; past dates
 * clamp to 0.
 */
export function parseRetryAfter(value: string | null | undefined, now = Date.now()): number | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (/^\d+(\.\d+)?$/.test(trimmed)) {
    return Number(trimmed) * 1000;
  }
  // A bare (signed) number that didn't match above is invalid delay-seconds —
  // don't let Date.parse misread it as a year.
  if (/^[+-]?\d+(\.\d+)?$/.test(trimmed)) {
    return null;
  }
  const dateMs = Date.parse(trimmed);
  if (!Number.isNaN(dateMs)) {
    return Math.max(0, dateMs - now);
  }
  return null;
}

function isAbortError(error: unknown): boolean {
  return (
    typeof error === 'object' &&
    error !== null &&
    (error as { name?: string }).name === 'AbortError'
  );
}

/**
 * `fetch` with Attio-appropriate retries. See module docs for behavior.
 *
 * If `input` is a `Request` it is cloned per attempt so bodies can be
 * re-sent on retry.
 */
export async function retryFetch(
  input: string | URL | Request,
  init?: RequestInit,
  options: RetryFetchOptions = {},
): Promise<Response> {
  const {
    maxRetries = DEFAULT_MAX_RETRIES,
    baseDelayMs = DEFAULT_BASE_DELAY_MS,
    maxDelayMs = DEFAULT_MAX_DELAY_MS,
    maxElapsedMs = DEFAULT_MAX_ELAPSED_MS,
    jitter = true,
    retryOnStatus = defaultRetryOnStatus,
    onRetry,
    now = Date.now,
    sleep = defaultSleep,
    random = Math.random,
  } = options;
  const doFetch = options.fetch ?? globalThis.fetch;

  const backoff = (attempt: number): number => {
    const exp = Math.min(maxDelayMs, baseDelayMs * 2 ** attempt);
    return jitter ? Math.round(exp * (0.5 + random() * 0.5)) : exp;
  };

  const start = now();

  for (let attempt = 0; ; attempt++) {
    let response: Response | undefined;
    let networkError: unknown;

    try {
      // Clone Request inputs so a consumed body doesn't break retries.
      const attemptInput = input instanceof Request ? input.clone() : input;
      response = await doFetch(attemptInput, init);
    } catch (error) {
      if (isAbortError(error) || init?.signal?.aborted) throw error;
      networkError = error;
    }

    if (response && !retryOnStatus(response.status)) {
      return response;
    }
    if (attempt >= maxRetries) {
      if (response) return response;
      throw networkError;
    }

    let delayMs: number;
    if (response?.status === 429) {
      const retryAfter = parseRetryAfter(response.headers.get('retry-after'), now());
      delayMs = retryAfter !== null ? Math.min(retryAfter, maxDelayMs) : backoff(attempt);
    } else {
      delayMs = backoff(attempt);
    }

    if (now() - start + delayMs > maxElapsedMs) {
      if (response) return response;
      throw networkError;
    }

    if (response) {
      // Free the connection: discard the retryable response's body.
      // Fire-and-forget — cancel() can stall on tee'd/cloned bodies in some
      // fetch implementations, and we must not block the retry on it.
      try {
        response.body?.cancel().catch(() => {});
      } catch {
        // Some fetch implementations disallow cancel after buffering; ignore.
      }
    }

    onRetry?.({ attempt, delayMs, status: response?.status, error: networkError });
    await sleep(delayMs);
  }
}

/**
 * Create a `fetch`-compatible function with retry options baked in — handy
 * for passing to code that expects plain `fetch`.
 */
export function createRetryFetch(
  options: RetryFetchOptions = {},
): (input: string | URL | Request, init?: RequestInit) => Promise<Response> {
  return (input, init) => retryFetch(input, init, options);
}
