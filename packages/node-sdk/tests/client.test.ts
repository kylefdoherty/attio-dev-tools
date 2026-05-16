import { describe, it, expect, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { HttpClient } from '../src/client.js';
import { AttioError, RateLimitError, ScopeError } from '../src/errors.js';
import { server } from './handlers.js';

const BASE = 'https://api.attio.com/v2';

function createClient(overrides?: Partial<ConstructorParameters<typeof HttpClient>[0]>) {
  return new HttpClient({
    apiKey: 'test-key',
    maxRetries: 0,
    retryDelay: 1,
    timeout: 5000,
    ...overrides,
  });
}

// ---------------------------------------------------------------------------
// Success paths
// ---------------------------------------------------------------------------

describe('HttpClient — success', () => {
  it('GET request returns parsed JSON', async () => {
    server.use(
      http.get(`${BASE}/objects`, () => HttpResponse.json({ data: [{ id: '1' }] })),
    );
    const client = createClient();
    const result = await client.request('GET', '/objects');
    expect(result).toEqual({ data: [{ id: '1' }] });
  });

  it('POST request sends body as JSON', async () => {
    let captured: unknown;
    server.use(
      http.post(`${BASE}/objects`, async ({ request }) => {
        captured = await request.json();
        return HttpResponse.json({ data: { id: '1' } });
      }),
    );
    const client = createClient();
    await client.request('POST', '/objects', { body: { data: { name: 'Deals' } } });
    expect(captured).toEqual({ data: { name: 'Deals' } });
  });

  it('query params are properly encoded in URL', async () => {
    let capturedUrl = '';
    server.use(
      http.get(`${BASE}/tasks`, ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient();
    await client.request('GET', '/tasks', { params: { is_completed: 'true', assignee: 'me' } });
    const url = new URL(capturedUrl);
    expect(url.searchParams.get('is_completed')).toBe('true');
    expect(url.searchParams.get('assignee')).toBe('me');
  });

  it('custom baseUrl is used (trailing slash stripped)', async () => {
    let capturedUrl = '';
    server.use(
      http.get('https://custom.api.com/v3/objects', ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient({ baseUrl: 'https://custom.api.com/v3/' });
    await client.request('GET', '/objects');
    expect(capturedUrl).toContain('https://custom.api.com/v3/objects');
  });

  it('request headers include Authorization', async () => {
    let authHeader = '';
    server.use(
      http.get(`${BASE}/objects`, ({ request }) => {
        authHeader = request.headers.get('authorization') ?? '';
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient();
    await client.request('GET', '/objects');
    expect(authHeader).toBe('Bearer test-key');
  });

  it('GET request does not send Content-Type header', async () => {
    let contentType: string | null = null;
    server.use(
      http.get(`${BASE}/objects`, ({ request }) => {
        contentType = request.headers.get('content-type');
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient();
    await client.request('GET', '/objects');
    expect(contentType).toBeNull();
  });

  it('POST request sends Content-Type: application/json', async () => {
    let contentType = '';
    server.use(
      http.post(`${BASE}/objects`, ({ request }) => {
        contentType = request.headers.get('content-type') ?? '';
        return HttpResponse.json({ data: {} });
      }),
    );
    const client = createClient();
    await client.request('POST', '/objects', { body: { data: {} } });
    expect(contentType).toBe('application/json');
  });
});

// ---------------------------------------------------------------------------
// Rate limiting
// ---------------------------------------------------------------------------

describe('HttpClient — rate limiting', () => {
  it('429 triggers retry and succeeds on next attempt', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/objects`, () => {
        attempts++;
        if (attempts === 1) {
          return new HttpResponse(null, {
            status: 429,
            headers: { 'retry-after': '0' },
          });
        }
        return HttpResponse.json({ data: [{ id: '1' }] });
      }),
    );
    const client = createClient({ maxRetries: 2, retryDelay: 1 });
    const result = await client.request('GET', '/objects');
    expect(result).toEqual({ data: [{ id: '1' }] });
    expect(attempts).toBe(2);
  });

  it('all retries exhausted on 429 throws RateLimitError', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        new HttpResponse(JSON.stringify({ message: 'slow down' }), {
          status: 429,
          headers: { 'retry-after': '0' },
        }),
      ),
    );
    const client = createClient({ maxRetries: 1, retryDelay: 1 });
    await expect(client.request('GET', '/objects')).rejects.toThrow(RateLimitError);
  });

  it('RateLimitError contains retryAfter value', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        new HttpResponse(null, {
          status: 429,
          headers: { 'retry-after': '42' },
        }),
      ),
    );
    const client = createClient({ maxRetries: 0 });
    try {
      await client.request('GET', '/objects');
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(RateLimitError);
      expect((e as RateLimitError).retryAfter).toBe(42);
    }
  });
});

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

describe('HttpClient — error handling', () => {
  it('403 throws ScopeError with parsed message', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        HttpResponse.json({ message: 'Missing scope: record:read' }, { status: 403 }),
      ),
    );
    const client = createClient();
    await expect(client.request('GET', '/objects')).rejects.toThrow(ScopeError);
    try {
      await client.request('GET', '/objects');
    } catch (e) {
      expect((e as ScopeError).message).toContain('Missing scope: record:read');
      expect((e as ScopeError).status).toBe(403);
    }
  });

  it('404 with allowNotFound returns null', async () => {
    server.use(
      http.get(`${BASE}/objects/missing`, () =>
        new HttpResponse(null, { status: 404 }),
      ),
    );
    const client = createClient();
    const result = await client.request('GET', '/objects/missing', { allowNotFound: true });
    expect(result).toBeNull();
  });

  it('404 without allowNotFound throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/objects/missing`, () =>
        HttpResponse.json({ message: 'Not found' }, { status: 404 }),
      ),
    );
    const client = createClient();
    await expect(client.request('GET', '/objects/missing')).rejects.toThrow(AttioError);
  });

  it('400 throws AttioError with status and parsed body', async () => {
    server.use(
      http.post(`${BASE}/objects`, () =>
        HttpResponse.json({ message: 'Bad request', code: 'invalid_params' }, { status: 400 }),
      ),
    );
    const client = createClient();
    try {
      await client.request('POST', '/objects', { body: {} });
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(AttioError);
      const err = e as AttioError;
      expect(err.status).toBe(400);
      expect(err.code).toBe('invalid_params');
      expect(err.body).toEqual({ message: 'Bad request', code: 'invalid_params' });
    }
  });

  it('500 throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        HttpResponse.json({ message: 'Internal error' }, { status: 500 }),
      ),
    );
    const client = createClient();
    await expect(client.request('GET', '/objects')).rejects.toThrow(AttioError);
  });

  it('non-JSON error body falls back to raw text', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        new HttpResponse('plain text error', {
          status: 502,
          headers: { 'content-type': 'text/plain' },
        }),
      ),
    );
    const client = createClient();
    try {
      await client.request('GET', '/objects');
      expect.unreachable();
    } catch (e) {
      expect((e as AttioError).message).toContain('plain text error');
    }
  });

  it('error body with message field is extracted', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        HttpResponse.json({ message: 'Detailed error msg' }, { status: 422 }),
      ),
    );
    const client = createClient();
    try {
      await client.request('GET', '/objects');
      expect.unreachable();
    } catch (e) {
      expect((e as AttioError).message).toContain('Detailed error msg');
    }
  });

  it('error body with code field is set on AttioError.code', async () => {
    server.use(
      http.get(`${BASE}/objects`, () =>
        HttpResponse.json({ message: 'err', code: 'validation_error' }, { status: 400 }),
      ),
    );
    const client = createClient();
    try {
      await client.request('GET', '/objects');
      expect.unreachable();
    } catch (e) {
      expect((e as AttioError).code).toBe('validation_error');
    }
  });
});

// ---------------------------------------------------------------------------
// Retry & timeout
// ---------------------------------------------------------------------------

describe('HttpClient — retry & timeout', () => {
  it('network error retries with exponential backoff then succeeds', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/objects`, () => {
        attempts++;
        if (attempts < 3) {
          return HttpResponse.error();
        }
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient({ maxRetries: 3, retryDelay: 1 });
    const result = await client.request('GET', '/objects');
    expect(result).toEqual({ data: [] });
    expect(attempts).toBe(3);
  });

  it('network errors exhausted throws AttioError', async () => {
    server.use(
      http.get(`${BASE}/objects`, () => HttpResponse.error()),
    );
    const client = createClient({ maxRetries: 1, retryDelay: 1 });
    await expect(client.request('GET', '/objects')).rejects.toThrow(AttioError);
  });

  it('timeout fires → throws AttioError with timeout message', async () => {
    server.use(
      http.get(`${BASE}/objects`, async () => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient({ timeout: 50 });
    try {
      await client.request('GET', '/objects');
      expect.unreachable();
    } catch (e) {
      expect(e).toBeInstanceOf(AttioError);
      expect((e as AttioError).message).toContain('timed out');
    }
  });

  it('maxRetries=0 means no retries', async () => {
    let attempts = 0;
    server.use(
      http.get(`${BASE}/objects`, () => {
        attempts++;
        return HttpResponse.error();
      }),
    );
    const client = createClient({ maxRetries: 0 });
    await expect(client.request('GET', '/objects')).rejects.toThrow();
    expect(attempts).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------

describe('HttpClient — edge cases', () => {
  it('empty response body on DELETE returns undefined', async () => {
    server.use(
      http.delete(`${BASE}/objects/123`, () => new HttpResponse(null, { status: 200 })),
    );
    const client = createClient();
    const result = await client.request('DELETE', '/objects/123');
    expect(result).toBeUndefined();
  });

  it('204 No Content returns undefined', async () => {
    server.use(
      http.delete(`${BASE}/objects/456`, () => new HttpResponse(null, { status: 204 })),
    );
    const client = createClient();
    const result = await client.request('DELETE', '/objects/456');
    expect(result).toBeUndefined();
  });

  it('baseUrl with multiple trailing slashes', async () => {
    let capturedUrl = '';
    server.use(
      http.get('https://api.attio.com/v2/objects', ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json({ data: [] });
      }),
    );
    const client = createClient({ baseUrl: 'https://api.attio.com/v2///' });
    await client.request('GET', '/objects');
    expect(new URL(capturedUrl).pathname).toBe('/v2/objects');
  });
});
