import { type RetryFetchOptions, retryFetch } from './retry-fetch.js';

/**
 * Minimal typed client for `api.attio.com/v2` from Attio server functions.
 *
 * Deliberately NOT a full SDK (that's `attio-node`) — this is a tiny,
 * sandbox-safe wrapper that adds auth, JSON handling, typed errors, and
 * rate-limit-aware retries on top of `fetch`.
 *
 * ```ts
 * import {ATTIO_API_TOKEN} from "attio/server";
 * import {attioApi} from "attio-app-kit";
 *
 * const api = attioApi(ATTIO_API_TOKEN);
 * const {data} = await api.post<{data: unknown[]}>("/objects/people/records/query", {
 *   filter: {name: {$contains: "Jane"}},
 *   limit: 10,
 * });
 * ```
 */

export type QueryParams = Record<string, string | number | boolean | undefined>;

export interface AttioApiOptions {
  /** Base URL. Default "https://api.attio.com/v2". */
  baseUrl?: string;
  /** Underlying fetch (before retries). Default: globalThis.fetch. */
  fetch?: typeof fetch;
  /** Retry tuning passed through to retryFetch. */
  retry?: RetryFetchOptions;
}

export interface RequestOptions {
  query?: QueryParams;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

/** Error thrown for non-2xx Attio API responses. */
export class AttioApiError extends Error {
  /** HTTP status code. */
  readonly status: number;
  /** Attio error code (e.g. "validation_type"), when present. */
  readonly code?: string;
  /** Attio error type (e.g. "invalid_request_error", "rate_limit_error"). */
  readonly type?: string;
  /** Parsed response body (JSON if possible, else raw text). */
  readonly body: unknown;
  readonly method: string;
  readonly path: string;

  constructor(input: {
    status: number;
    method: string;
    path: string;
    body: unknown;
  }) {
    const { status, method, path, body } = input;
    const parsed = (typeof body === 'object' && body !== null ? body : {}) as {
      message?: unknown;
      code?: unknown;
      type?: unknown;
    };
    const message =
      typeof parsed.message === 'string' && parsed.message
        ? parsed.message
        : `Attio API error ${status} on ${method} ${path}`;
    super(message);
    this.name = 'AttioApiError';
    this.status = status;
    this.method = method;
    this.path = path;
    this.body = body;
    if (typeof parsed.code === 'string') this.code = parsed.code;
    if (typeof parsed.type === 'string') this.type = parsed.type;
  }
}

export interface AttioApi {
  get<T = unknown>(path: string, options?: RequestOptions): Promise<T>;
  post<T = unknown>(path: string, body?: unknown, options?: RequestOptions): Promise<T>;
  put<T = unknown>(path: string, body?: unknown, options?: RequestOptions): Promise<T>;
  patch<T = unknown>(path: string, body?: unknown, options?: RequestOptions): Promise<T>;
  del<T = unknown>(path: string, options?: RequestOptions): Promise<T>;
  /** Escape hatch for custom methods. */
  request<T = unknown>(
    method: string,
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T>;
}

const DEFAULT_BASE_URL = 'https://api.attio.com/v2';

function buildUrl(baseUrl: string, path: string, query?: QueryParams): string {
  const url = /^https?:\/\//.test(path)
    ? path
    : `${baseUrl.replace(/\/+$/, '')}/${path.replace(/^\/+/, '')}`;
  if (!query) return url;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${url}${url.includes('?') ? '&' : '?'}${qs}` : url;
}

/**
 * Create a minimal Attio API client. See module docs for usage.
 */
export function attioApi(token: string, options: AttioApiOptions = {}): AttioApi {
  if (!token) throw new RangeError('attioApi requires an API token');
  const baseUrl = options.baseUrl ?? DEFAULT_BASE_URL;
  const retryOptions: RetryFetchOptions = {
    ...options.retry,
    fetch: options.retry?.fetch ?? options.fetch,
  };

  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
    requestOptions: RequestOptions = {},
  ): Promise<T> {
    const url = buildUrl(baseUrl, path, requestOptions.query);
    const headers: Record<string, string> = {
      authorization: `Bearer ${token}`,
      accept: 'application/json',
      ...requestOptions.headers,
    };
    const init: RequestInit = { method, headers, signal: requestOptions.signal };
    if (body !== undefined) {
      headers['content-type'] = 'application/json';
      init.body = JSON.stringify(body);
    }

    const response = await retryFetch(url, init, retryOptions);
    const raw = await response.text();
    let parsed: unknown;
    if (raw) {
      try {
        parsed = JSON.parse(raw);
      } catch {
        parsed = raw;
      }
    }

    if (!response.ok) {
      throw new AttioApiError({ status: response.status, method, path, body: parsed });
    }
    return parsed as T;
  }

  return {
    request,
    get: (path, opts) => request('GET', path, undefined, opts),
    post: (path, body, opts) => request('POST', path, body, opts),
    put: (path, body, opts) => request('PUT', path, body, opts),
    patch: (path, body, opts) => request('PATCH', path, body, opts),
    del: (path, opts) => request('DELETE', path, undefined, opts),
  };
}
