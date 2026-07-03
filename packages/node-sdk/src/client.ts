import { AttioError, RateLimitError, ScopeError } from './errors.js';
import type { AttioClientOptions, RequestOptions } from './types.js';

const DEFAULT_BASE_URL = 'https://api.attio.com/v2';
const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_RETRY_DELAY = 1000;
const DEFAULT_TIMEOUT = 30000;

export class HttpClient {
  private apiKey: string;
  private baseUrl: string;
  private maxRetries: number;
  private retryDelay: number;
  private timeout: number;

  constructor(options: AttioClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, '');
    this.maxRetries = options.maxRetries ?? DEFAULT_MAX_RETRIES;
    this.retryDelay = options.retryDelay ?? DEFAULT_RETRY_DELAY;
    this.timeout = options.timeout ?? DEFAULT_TIMEOUT;
  }

  async request<T>(method: string, path: string, options?: RequestOptions): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    if (options?.params) {
      for (const [key, value] of Object.entries(options.params)) {
        url.searchParams.set(key, value);
      }
    }

    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      try {
        const headers: Record<string, string> = {
          Authorization: `Bearer ${this.apiKey}`,
        };
        if (options?.body !== undefined) {
          headers['Content-Type'] = 'application/json';
        }
        const fetchOptions: RequestInit = {
          method,
          headers,
          signal: controller.signal,
        };

        if (options?.body !== undefined) {
          fetchOptions.body = JSON.stringify(options.body);
        }

        if (options?.redirect) {
          fetchOptions.redirect = options.redirect;
        }

        const res = await fetch(url.toString(), fetchOptions);

        // Handle rate limiting (429) — retry with Retry-After
        if (res.status === 429) {
          const retryAfterHeader = res.headers.get('retry-after');
          const retryAfterSec =
            retryAfterHeader != null ? parseFloat(retryAfterHeader) : this.retryDelay / 1000;
          if (attempt < this.maxRetries) {
            await this.sleep(retryAfterSec * 1000);
            continue;
          }
          const body = await this.parseBody(res);
          throw new RateLimitError(retryAfterSec, body);
        }

        // Handle retryable server errors (5xx) — retry with exponential backoff
        if (res.status >= 500) {
          if (attempt < this.maxRetries) {
            await this.sleep(this.retryDelay * 2 ** attempt);
            continue;
          }
          const body = await this.parseBody(res);
          throw new AttioError(
            `Attio API ${method} ${path} ${res.status}: ${this.extractMessage(body)}`,
            res.status,
            body,
          );
        }

        // Handle manual redirects (e.g. signed file download URLs) — resolve
        // with the Location header instead of following the redirect
        if (options?.redirect === 'manual' && res.status >= 300 && res.status < 400) {
          const location = res.headers.get('location');
          if (!location) {
            throw new AttioError(
              `Attio API ${method} ${path} ${res.status}: redirect response missing Location header`,
              res.status,
            );
          }
          return { url: location } as T;
        }

        // Handle scope errors
        if (res.status === 403) {
          const body = await this.parseBody(res);
          throw new ScopeError(
            `Forbidden: missing required API scope. ${this.extractMessage(body)}`,
            body,
          );
        }

        // Handle not found (optionally return null)
        if (res.status === 404 && options?.allowNotFound) {
          return null as T;
        }

        // Handle other non-retryable errors (4xx)
        if (!res.ok) {
          const body = await this.parseBody(res);
          throw new AttioError(
            `Attio API ${method} ${path} ${res.status}: ${this.extractMessage(body)}`,
            res.status,
            body,
          );
        }

        // Success — handle empty bodies (e.g., 204 No Content or empty 200)
        const text = await res.text();
        if (!text) return undefined as T;
        return JSON.parse(text) as T;
      } catch (error) {
        if (error instanceof AttioError) throw error;

        lastError = error as Error;

        // Don't retry on abort (timeout)
        if ((error as Error).name === 'AbortError') {
          throw new AttioError(`Request timed out after ${this.timeout}ms: ${method} ${path}`, 0);
        }

        // Retry on network errors
        if (attempt < this.maxRetries) {
          await this.sleep(this.retryDelay * 2 ** attempt);
        }
      } finally {
        clearTimeout(timeoutId);
      }
    }

    throw new AttioError(
      lastError?.message ?? `Request failed after ${this.maxRetries} retries`,
      0,
    );
  }

  async requestFormData<T>(path: string, formData: FormData): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      try {
        const res = await fetch(url.toString(), {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            // Do NOT set Content-Type — fetch sets it automatically with boundary for FormData
          },
          body: formData,
          signal: controller.signal,
        });

        // Handle rate limiting (429) — retry with Retry-After
        if (res.status === 429) {
          const retryAfterHeader = res.headers.get('retry-after');
          const retryAfterSec =
            retryAfterHeader != null ? parseFloat(retryAfterHeader) : this.retryDelay / 1000;
          if (attempt < this.maxRetries) {
            await this.sleep(retryAfterSec * 1000);
            continue;
          }
          const body = await this.parseBody(res);
          throw new RateLimitError(retryAfterSec, body);
        }

        // Handle retryable server errors (5xx) — retry with exponential backoff
        if (res.status >= 500) {
          if (attempt < this.maxRetries) {
            await this.sleep(this.retryDelay * 2 ** attempt);
            continue;
          }
          const body = await this.parseBody(res);
          throw new AttioError(
            `Attio API POST ${path} ${res.status}: ${this.extractMessage(body)}`,
            res.status,
            body,
          );
        }

        // Handle scope errors
        if (res.status === 403) {
          const body = await this.parseBody(res);
          throw new ScopeError(
            `Forbidden: missing required API scope. ${this.extractMessage(body)}`,
            body,
          );
        }

        // Handle other non-retryable errors (4xx)
        if (!res.ok) {
          const body = await this.parseBody(res);
          throw new AttioError(
            `Attio API POST ${path} ${res.status}: ${this.extractMessage(body)}`,
            res.status,
            body,
          );
        }

        return (await res.json()) as T;
      } catch (error) {
        if (error instanceof AttioError) throw error;

        lastError = error as Error;

        if ((error as Error).name === 'AbortError') {
          throw new AttioError(`Request timed out after ${this.timeout}ms: POST ${path}`, 0);
        }

        if (attempt < this.maxRetries) {
          await this.sleep(this.retryDelay * 2 ** attempt);
        }
      } finally {
        clearTimeout(timeoutId);
      }
    }

    throw new AttioError(
      lastError?.message ?? `Request failed after ${this.maxRetries} retries`,
      0,
    );
  }

  private async parseBody(res: Response): Promise<unknown> {
    const text = await res.text();
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }

  private extractMessage(body: unknown): string {
    if (typeof body === 'string') return body;
    if (body && typeof body === 'object') {
      const obj = body as Record<string, unknown>;
      if (typeof obj.message === 'string') return obj.message;
      if (typeof obj.error === 'string') return obj.error;
    }
    return JSON.stringify(body);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
