/**
 * Cross-SDK HTTP retry spec validation tests.
 *
 * These tests validate that the Node SDK conforms to docs/http-retry-spec.md.
 * The Python SDK has a mirror test suite in packages/sdk/tests/test_http_retry_spec.py.
 * Both suites MUST cover the same scenarios.
 */

import { describe, it, expect, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { HttpClient } from '../src/client.js';
import { AttioError, RateLimitError } from '../src/errors.js';
import { server } from './handlers.js';

const BASE = 'https://api.attio.com/v2';

function createClient(overrides?: Partial<ConstructorParameters<typeof HttpClient>[0]>) {
  return new HttpClient({
    apiKey: 'test-key',
    maxRetries: 3,
    retryDelay: 10, // 10ms for fast tests
    timeout: 5000,
    ...overrides,
  });
}

// ---------------------------------------------------------------------------
// Spec scenario 1: retry_on_429_then_success
// ---------------------------------------------------------------------------

describe('Spec: retry on 429 then success', () => {
  it('first request returns 429, second returns 200 — verify 2 attempts and success', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        if (attempts === 1) {
          return new HttpResponse(JSON.stringify({ message: 'rate limited' }), {
            status: 429,
            headers: { 'retry-after': '0' },
          });
        }
        return HttpResponse.json({ data: 'ok' });
      }),
    );
    const client = createClient();
    const result = await client.request('GET', '/test');
    expect(result).toEqual({ data: 'ok' });
    expect(attempts).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 2: retry_on_5xx_then_success
// ---------------------------------------------------------------------------

describe('Spec: retry on 5xx then success', () => {
  it('first request returns 500, second returns 200 — verify 2 attempts and success', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        if (attempts === 1) {
          return HttpResponse.json({ message: 'server error' }, { status: 500 });
        }
        return HttpResponse.json({ data: 'ok' });
      }),
    );
    const client = createClient();
    const result = await client.request('GET', '/test');
    expect(result).toEqual({ data: 'ok' });
    expect(attempts).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 3: retry_on_network_error_then_success
// ---------------------------------------------------------------------------

describe('Spec: retry on network error then success', () => {
  it('first request raises network error, second returns 200 — verify 2 attempts', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        if (attempts === 1) {
          return HttpResponse.error();
        }
        return HttpResponse.json({ data: 'ok' });
      }),
    );
    const client = createClient();
    const result = await client.request('GET', '/test');
    expect(result).toEqual({ data: 'ok' });
    expect(attempts).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 4: 429_exhaustion_raises_rate_limit_error
// ---------------------------------------------------------------------------

describe('Spec: 429 exhaustion raises RateLimitError', () => {
  it('all attempts return 429 — verify RateLimitError', async () => {
    server.use(
      http.get(`${BASE}/test`, () =>
        new HttpResponse(JSON.stringify({ message: 'slow down' }), {
          status: 429,
          headers: { 'retry-after': '0' },
        }),
      ),
    );
    const client = createClient({ maxRetries: 1 });
    await expect(client.request('GET', '/test')).rejects.toThrow(RateLimitError);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 5: 5xx_exhaustion_raises_api_error
// ---------------------------------------------------------------------------

describe('Spec: 5xx exhaustion raises AttioError', () => {
  it('all attempts return 502 — verify AttioError with status 502', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        return HttpResponse.json({ message: 'bad gateway' }, { status: 502 });
      }),
    );
    const client = createClient({ maxRetries: 1 });
    try {
      await client.request('GET', '/test');
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(AttioError);
      expect((e as AttioError).status).toBe(502);
    }
    expect(attempts).toBe(2); // initial + 1 retry
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 6: network_error_exhaustion
// ---------------------------------------------------------------------------

describe('Spec: network error exhaustion', () => {
  it('all attempts raise network errors — verify AttioError', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        return HttpResponse.error();
      }),
    );
    const client = createClient({ maxRetries: 1 });
    await expect(client.request('GET', '/test')).rejects.toThrow(AttioError);
    expect(attempts).toBe(2); // initial + 1 retry
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 7: 4xx_no_retry
// ---------------------------------------------------------------------------

describe('Spec: 4xx no retry', () => {
  it('request returns 400 — exactly 1 attempt, AttioError raised', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        return HttpResponse.json(
          { message: 'bad request', code: 'validation_error' },
          { status: 400 },
        );
      }),
    );
    const client = createClient({ maxRetries: 3 });
    await expect(client.request('GET', '/test')).rejects.toThrow(AttioError);
    expect(attempts).toBe(1);
  });

  it('request returns 401 — exactly 1 attempt, AttioError raised', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        return HttpResponse.json({ message: 'unauthorized' }, { status: 401 });
      }),
    );
    const client = createClient({ maxRetries: 3 });
    await expect(client.request('GET', '/test')).rejects.toThrow(AttioError);
    expect(attempts).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 8: timeout_no_retry
// ---------------------------------------------------------------------------

describe('Spec: timeout no retry', () => {
  it('request times out — no retry, timeout error raised', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/test`, async () => {
        attempts++;
        await new Promise((resolve) => setTimeout(resolve, 500));
        return HttpResponse.json({ data: 'ok' });
      }),
    );
    const client = createClient({ maxRetries: 3, timeout: 50 });
    try {
      await client.request('GET', '/test');
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(AttioError);
      expect((e as AttioError).message).toContain('timed out');
    }
    // Only 1 attempt because timeout is not retried
    expect(attempts).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 9: retry_after_header_respected
// ---------------------------------------------------------------------------

describe('Spec: Retry-After header respected', () => {
  it('429 with Retry-After header — delay uses header value, not default backoff', async () => {
    let attempts = 0;
    const sleepCalls: number[] = [];
    const originalSetTimeout = globalThis.setTimeout;

    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        if (attempts === 1) {
          return new HttpResponse(JSON.stringify({ message: 'rate limited' }), {
            status: 429,
            headers: { 'retry-after': '0' }, // 0 seconds
          });
        }
        return HttpResponse.json({ data: 'ok' });
      }),
    );

    // Use a large retryDelay to prove we are NOT using it for 429
    const client = createClient({ retryDelay: 999_000 });
    // The test should complete quickly because retry-after is 0, not 999s
    const result = await client.request('GET', '/test');
    expect(result).toEqual({ data: 'ok' });
    expect(attempts).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// Spec scenario 10: 5xx_uses_exponential_backoff
// ---------------------------------------------------------------------------

describe('Spec: 5xx uses exponential backoff', () => {
  it('multiple 5xx retries use increasing delays', async () => {
    let attempts = 0;
    const timestamps: number[] = [];

    server.use(
      http.get(`${BASE}/test`, () => {
        attempts++;
        timestamps.push(Date.now());
        if (attempts <= 2) {
          return HttpResponse.json({ message: 'error' }, { status: 500 });
        }
        return HttpResponse.json({ data: 'ok' });
      }),
    );

    // retryDelay=50ms => delays should be 50ms (attempt 0), 100ms (attempt 1)
    const client = createClient({ retryDelay: 50, maxRetries: 3 });
    const result = await client.request('GET', '/test');
    expect(result).toEqual({ data: 'ok' });
    expect(attempts).toBe(3);

    // Verify second gap is roughly double the first gap
    // Allow generous margin for CI timing variance
    const gap1 = timestamps[1] - timestamps[0]; // ~50ms
    const gap2 = timestamps[2] - timestamps[1]; // ~100ms
    expect(gap2).toBeGreaterThan(gap1 * 1.3); // at least somewhat larger
  });
});
