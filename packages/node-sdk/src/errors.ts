/**
 * Base error for all Attio API errors.
 */
export class AttioError extends Error {
  status: number;
  code?: string;
  body?: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = 'AttioError';
    this.status = status;
    this.body = body;
    if (body && typeof body === 'object' && 'code' in body) {
      this.code = (body as { code: string }).code;
    }
  }
}

/**
 * Thrown when the API returns 429 Too Many Requests and all retries are exhausted.
 */
export class RateLimitError extends AttioError {
  retryAfter: number;

  constructor(retryAfter: number, body?: unknown) {
    super(`Rate limited. Retry after ${retryAfter}s`, 429, body);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }
}

/**
 * Thrown when the API returns 403 due to missing scopes.
 */
export class ScopeError extends AttioError {
  constructor(message: string, body?: unknown) {
    super(message, 403, body);
    this.name = 'ScopeError';
  }
}
