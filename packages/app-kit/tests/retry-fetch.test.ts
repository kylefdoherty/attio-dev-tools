import { describe, expect, it, vi } from 'vitest';
import { createRetryFetch, parseRetryAfter, retryFetch } from '../src/retry-fetch.js';

// -- test helpers -----------------------------------------------------------

/** Response factory — a fresh Response per attempt (bodies are one-shot). */
function json(status: number, headers: Record<string, string> = {}): () => Response {
  return () =>
    new Response(JSON.stringify({ status }), {
      status,
      headers: { 'content-type': 'application/json', ...headers },
    });
}

/** Sequence of response factories/errors; records call count. */
function fetchSequence(steps: Array<(() => Response) | Error>): typeof fetch & { calls: number } {
  let i = 0;
  const fn = (async () => {
    const step = steps[Math.min(i, steps.length - 1)];
    i++;
    if (step instanceof Error) throw step;
    return step();
  }) as unknown as typeof fetch & { calls: number };
  Object.defineProperty(fn, 'calls', { get: () => i });
  return fn;
}

/** Deterministic clock: sleep() advances virtual time and records delays. */
function virtualClock() {
  let time = 0;
  const slept: number[] = [];
  return {
    now: () => time,
    sleep: async (ms: number) => {
      slept.push(ms);
      time += ms;
    },
    slept,
    advance: (ms: number) => {
      time += ms;
    },
    get time() {
      return time;
    },
  };
}

const noJitter = { jitter: false } as const;

// -- parseRetryAfter --------------------------------------------------------

describe('parseRetryAfter', () => {
  it('parses delay-seconds', () => {
    expect(parseRetryAfter('2', 0)).toBe(2000);
    expect(parseRetryAfter('0', 0)).toBe(0);
    expect(parseRetryAfter('1.5', 0)).toBe(1500);
    expect(parseRetryAfter(' 3 ', 0)).toBe(3000);
  });

  it('parses HTTP-dates (the form Attio actually sends)', () => {
    const now = Date.parse('Wed, 01 Jul 2026 12:00:00 GMT');
    expect(parseRetryAfter('Wed, 01 Jul 2026 12:00:01 GMT', now)).toBe(1000);
    expect(parseRetryAfter('Wed, 01 Jul 2026 12:00:30 GMT', now)).toBe(30000);
  });

  it('clamps past HTTP-dates to 0', () => {
    const now = Date.parse('Wed, 01 Jul 2026 12:00:00 GMT');
    expect(parseRetryAfter('Wed, 01 Jul 2026 11:59:00 GMT', now)).toBe(0);
  });

  it('returns null for missing or garbage values', () => {
    expect(parseRetryAfter(null)).toBeNull();
    expect(parseRetryAfter(undefined)).toBeNull();
    expect(parseRetryAfter('')).toBeNull();
    expect(parseRetryAfter('soon')).toBeNull();
    expect(parseRetryAfter('-5')).toBeNull(); // negative seconds are not valid RFC 9110
  });
});

// -- retryFetch -------------------------------------------------------------

describe('retryFetch', () => {
  it('returns immediately on success', async () => {
    const f = fetchSequence([json(200)]);
    const clock = virtualClock();
    const res = await retryFetch('https://api.attio.com/v2/self', undefined, {
      fetch: f,
      ...clock,
      ...noJitter,
    });
    expect(res.status).toBe(200);
    expect(f.calls).toBe(1);
    expect(clock.slept).toEqual([]);
  });

  it('retries 429 honoring an HTTP-date Retry-After', async () => {
    const clock = virtualClock();
    // virtual now() is 0 => epoch; Retry-After 2s after epoch
    const retryAt = new Date(2000).toUTCString();
    const f = fetchSequence([json(429, { 'retry-after': retryAt }), json(200)]);
    const res = await retryFetch('https://x', undefined, { fetch: f, ...clock, ...noJitter });
    expect(res.status).toBe(200);
    expect(f.calls).toBe(2);
    expect(clock.slept).toEqual([2000]);
  });

  it('retries 429 with numeric Retry-After seconds', async () => {
    const clock = virtualClock();
    const f = fetchSequence([json(429, { 'retry-after': '3' }), json(200)]);
    await retryFetch('https://x', undefined, { fetch: f, ...clock, ...noJitter });
    expect(clock.slept).toEqual([3000]);
  });

  it('falls back to backoff when 429 has no Retry-After', async () => {
    const clock = virtualClock();
    const f = fetchSequence([json(429), json(200)]);
    await retryFetch('https://x', undefined, {
      fetch: f,
      baseDelayMs: 500,
      ...clock,
      ...noJitter,
    });
    expect(clock.slept).toEqual([500]);
  });

  it('caps Retry-After at maxDelayMs', async () => {
    const clock = virtualClock();
    const farFuture = new Date(10 * 60_000).toUTCString();
    const f = fetchSequence([json(429, { 'retry-after': farFuture }), json(200)]);
    await retryFetch('https://x', undefined, {
      fetch: f,
      maxDelayMs: 5000,
      maxElapsedMs: 60_000,
      ...clock,
      ...noJitter,
    });
    expect(clock.slept).toEqual([5000]);
  });

  it('retries 5xx with exponential backoff (1s, 2s, 4s at defaults)', async () => {
    const clock = virtualClock();
    const f = fetchSequence([json(500), json(502), json(503), json(200)]);
    const res = await retryFetch('https://x', undefined, { fetch: f, ...clock, ...noJitter });
    expect(res.status).toBe(200);
    expect(f.calls).toBe(4);
    expect(clock.slept).toEqual([1000, 2000, 4000]);
  });

  it('applies equal jitter to backoff (delay in [0.5x, 1.0x))', async () => {
    const clock = virtualClock();
    const f = fetchSequence([json(500), json(200)]);
    await retryFetch('https://x', undefined, {
      fetch: f,
      baseDelayMs: 1000,
      random: () => 0.5, // => 1000 * (0.5 + 0.25) = 750
      ...clock,
    });
    expect(clock.slept).toEqual([750]);
  });

  it('does not retry non-429 4xx', async () => {
    const f = fetchSequence([json(400), json(200)]);
    const clock = virtualClock();
    const res = await retryFetch('https://x', undefined, { fetch: f, ...clock, ...noJitter });
    expect(res.status).toBe(400);
    expect(f.calls).toBe(1);
  });

  it('retries network errors and eventually rethrows', async () => {
    const boom = new TypeError('fetch failed');
    const f = fetchSequence([boom, boom, boom, boom]);
    const clock = virtualClock();
    await expect(
      retryFetch('https://x', undefined, { fetch: f, maxRetries: 3, ...clock, ...noJitter }),
    ).rejects.toBe(boom);
    expect(f.calls).toBe(4);
    expect(clock.slept).toEqual([1000, 2000, 4000]);
  });

  it('recovers when a network error is transient', async () => {
    const f = fetchSequence([new TypeError('fetch failed'), json(200)]);
    const clock = virtualClock();
    const res = await retryFetch('https://x', undefined, { fetch: f, ...clock, ...noJitter });
    expect(res.status).toBe(200);
  });

  it('does not retry AbortError', async () => {
    const abort = new DOMException('aborted', 'AbortError');
    const f = fetchSequence([abort, json(200)]);
    const clock = virtualClock();
    await expect(retryFetch('https://x', undefined, { fetch: f, ...clock })).rejects.toBe(abort);
    expect(f.calls).toBe(1);
  });

  it('returns the last response when retries are exhausted', async () => {
    const f = fetchSequence([json(500), json(500), json(500), json(500)]);
    const clock = virtualClock();
    const res = await retryFetch('https://x', undefined, {
      fetch: f,
      maxRetries: 3,
      ...clock,
      ...noJitter,
    });
    expect(res.status).toBe(500);
    expect(f.calls).toBe(4);
  });

  it('respects maxRetries: 0 (single attempt)', async () => {
    const f = fetchSequence([json(429, { 'retry-after': '1' }), json(200)]);
    const clock = virtualClock();
    const res = await retryFetch('https://x', undefined, {
      fetch: f,
      maxRetries: 0,
      ...clock,
      ...noJitter,
    });
    expect(res.status).toBe(429);
    expect(f.calls).toBe(1);
  });

  it('gives up early when the next sleep would exceed maxElapsedMs', async () => {
    const clock = virtualClock();
    const f = fetchSequence([json(500), json(500), json(200)]);
    const res = await retryFetch('https://x', undefined, {
      fetch: f,
      baseDelayMs: 1000,
      maxElapsedMs: 2500, // first retry (1000) ok; second (2000, total 3000) not
      maxRetries: 5,
      ...clock,
      ...noJitter,
    });
    expect(res.status).toBe(500);
    expect(f.calls).toBe(2);
    expect(clock.slept).toEqual([1000]);
  });

  it('clones Request inputs so bodies survive retries', async () => {
    const bodies: string[] = [];
    let call = 0;
    const f = (async (input: string | URL | Request) => {
      call++;
      bodies.push(await (input as Request).text());
      return call === 1 ? json(500)() : json(200)();
    }) as unknown as typeof fetch;

    const request = new Request('https://x', { method: 'POST', body: '{"a":1}' });
    const clock = virtualClock();
    const res = await retryFetch(request, undefined, { fetch: f, ...clock, ...noJitter });
    expect(res.status).toBe(200);
    expect(bodies).toEqual(['{"a":1}', '{"a":1}']);
  });

  it('invokes onRetry with attempt, delay, and status', async () => {
    const onRetry = vi.fn();
    const f = fetchSequence([json(429, { 'retry-after': '2' }), json(500), json(200)]);
    const clock = virtualClock();
    await retryFetch('https://x', undefined, { fetch: f, onRetry, ...clock, ...noJitter });
    expect(onRetry).toHaveBeenCalledTimes(2);
    expect(onRetry).toHaveBeenNthCalledWith(1, {
      attempt: 0,
      delayMs: 2000,
      status: 429,
      error: undefined,
    });
    expect(onRetry).toHaveBeenNthCalledWith(2, {
      attempt: 1,
      delayMs: 2000, // baseDelay 1000 * 2^1
      status: 500,
      error: undefined,
    });
  });

  it('honors a custom retryOnStatus predicate', async () => {
    const f = fetchSequence([json(503), json(200)]);
    const clock = virtualClock();
    const res = await retryFetch('https://x', undefined, {
      fetch: f,
      retryOnStatus: (s) => s === 429, // 503 no longer retryable
      ...clock,
    });
    expect(res.status).toBe(503);
    expect(f.calls).toBe(1);
  });

  it('createRetryFetch bakes options into a fetch-compatible function', async () => {
    const f = fetchSequence([json(500), json(200)]);
    const clock = virtualClock();
    const wrapped = createRetryFetch({ fetch: f, ...clock, ...noJitter });
    const res = await wrapped('https://x');
    expect(res.status).toBe(200);
    expect(f.calls).toBe(2);
  });
});
