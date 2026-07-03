import { describe, expect, it } from 'vitest';
import { AttioApiError, attioApi } from '../src/attio-api.js';

interface Captured {
  url: string;
  method: string;
  headers: Headers;
  body: string | null;
}

function captureFetch(
  responder: (captured: Captured, call: number) => Response,
): { fetch: typeof fetch; requests: Captured[] } {
  const requests: Captured[] = [];
  const fetchImpl = (async (input: string | URL | Request, init?: RequestInit) => {
    const captured: Captured = {
      url: String(input),
      method: init?.method ?? 'GET',
      headers: new Headers(init?.headers),
      body: typeof init?.body === 'string' ? init.body : null,
    };
    requests.push(captured);
    return responder(captured, requests.length);
  }) as typeof fetch;
  return { fetch: fetchImpl, requests };
}

const ok = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  });

describe('attioApi', () => {
  it('requires a token', () => {
    expect(() => attioApi('')).toThrow(RangeError);
  });

  it('sends bearer auth and JSON headers to the default base URL', async () => {
    const { fetch, requests } = captureFetch(() => ok({ data: [] }));
    const api = attioApi('tok_123', { fetch });
    await api.get('/objects');
    expect(requests[0].url).toBe('https://api.attio.com/v2/objects');
    expect(requests[0].headers.get('authorization')).toBe('Bearer tok_123');
    expect(requests[0].headers.get('accept')).toBe('application/json');
    expect(requests[0].headers.get('content-type')).toBeNull(); // no body on GET
  });

  it('normalizes leading/trailing slashes', async () => {
    const { fetch, requests } = captureFetch(() => ok({}));
    const api = attioApi('t', { fetch, baseUrl: 'https://api.attio.com/v2/' });
    await api.get('objects/people');
    expect(requests[0].url).toBe('https://api.attio.com/v2/objects/people');
  });

  it('serializes JSON bodies on POST/PUT/PATCH', async () => {
    const { fetch, requests } = captureFetch(() => ok({}));
    const api = attioApi('t', { fetch });
    await api.post('/objects/people/records', { data: { values: { name: 'Jane' } } });
    expect(requests[0].method).toBe('POST');
    expect(requests[0].headers.get('content-type')).toBe('application/json');
    expect(JSON.parse(requests[0].body ?? '')).toEqual({ data: { values: { name: 'Jane' } } });
  });

  it('appends query params, skipping undefined', async () => {
    const { fetch, requests } = captureFetch(() => ok({}));
    const api = attioApi('t', { fetch });
    await api.put(
      '/objects/people/records',
      {},
      { query: { matching_attribute: 'email_addresses', skip: undefined, limit: 5 } },
    );
    const url = new URL(requests[0].url);
    expect(url.searchParams.get('matching_attribute')).toBe('email_addresses');
    expect(url.searchParams.get('limit')).toBe('5');
    expect(url.searchParams.has('skip')).toBe(false);
  });

  it('returns parsed JSON', async () => {
    const { fetch } = captureFetch(() => ok({ data: { id: 'r1' } }));
    const api = attioApi('t', { fetch });
    const result = await api.get<{ data: { id: string } }>('/x');
    expect(result.data.id).toBe('r1');
  });

  it('returns undefined for empty bodies (204)', async () => {
    const { fetch } = captureFetch(() => new Response(null, { status: 204 }));
    const api = attioApi('t', { fetch });
    expect(await api.del('/objects/people/records/r1')).toBeUndefined();
  });

  it('throws AttioApiError with status/code/type/message from the body', async () => {
    const { fetch } = captureFetch(() =>
      ok(
        {
          status_code: 400,
          type: 'invalid_request_error',
          code: 'validation_type',
          message: 'The value was not valid',
        },
        400,
      ),
    );
    const api = attioApi('t', { fetch });
    const error = await api.post('/objects/people/records', {}).catch((e) => e);
    expect(error).toBeInstanceOf(AttioApiError);
    expect(error.status).toBe(400);
    expect(error.code).toBe('validation_type');
    expect(error.type).toBe('invalid_request_error');
    expect(error.message).toBe('The value was not valid');
    expect(error.method).toBe('POST');
    expect(error.path).toBe('/objects/people/records');
  });

  it('handles non-JSON error bodies', async () => {
    const { fetch } = captureFetch(() => new Response('Bad Gateway', { status: 502 }));
    const api = attioApi('t', { fetch, retry: { maxRetries: 0 } });
    const error = await api.get('/self').catch((e) => e);
    expect(error).toBeInstanceOf(AttioApiError);
    expect(error.status).toBe(502);
    expect(error.body).toBe('Bad Gateway');
    expect(error.message).toContain('502');
  });

  it('retries 429 (HTTP-date Retry-After) before succeeding', async () => {
    const slept: number[] = [];
    let virtualNow = 0;
    const { fetch, requests } = captureFetch((_captured, call) =>
      call === 1
        ? ok({ type: 'rate_limit_error' }, 429) // no header: falls back to backoff
        : ok({ data: [] }),
    );
    const api = attioApi('t', {
      fetch,
      retry: {
        jitter: false,
        baseDelayMs: 100,
        now: () => virtualNow,
        sleep: async (ms) => {
          slept.push(ms);
          virtualNow += ms;
        },
      },
    });
    const result = await api.get<{ data: unknown[] }>('/objects');
    expect(result.data).toEqual([]);
    expect(requests).toHaveLength(2);
    expect(slept).toEqual([100]);
  });

  it('does not retry 4xx', async () => {
    const { fetch, requests } = captureFetch(() => ok({ message: 'nope' }, 404));
    const api = attioApi('t', { fetch });
    await expect(api.get('/objects/nope')).rejects.toThrow('nope');
    expect(requests).toHaveLength(1);
  });

  it('exposes request() for custom verbs', async () => {
    const { fetch, requests } = captureFetch(() => ok({}));
    const api = attioApi('t', { fetch });
    await api.request('HEAD', '/self');
    expect(requests[0].method).toBe('HEAD');
  });

  it('allows extra headers per request', async () => {
    const { fetch, requests } = captureFetch(() => ok({}));
    const api = attioApi('t', { fetch });
    await api.get('/self', { headers: { 'x-custom': 'yes' } });
    expect(requests[0].headers.get('x-custom')).toBe('yes');
    expect(requests[0].headers.get('authorization')).toBe('Bearer t');
  });
});
