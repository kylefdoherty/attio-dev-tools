import { describe, it, expect } from 'vitest';
import { AttioError, RateLimitError, ScopeError } from '../src/errors.js';

describe('AttioError', () => {
  it('sets name, status, and body', () => {
    const err = new AttioError('Something failed', 400, { detail: 'bad' });
    expect(err.name).toBe('AttioError');
    expect(err.message).toBe('Something failed');
    expect(err.status).toBe(400);
    expect(err.body).toEqual({ detail: 'bad' });
  });

  it('extracts code from body', () => {
    const err = new AttioError('err', 422, { code: 'invalid_field', message: 'err' });
    expect(err.code).toBe('invalid_field');
  });

  it('code is undefined when body has no code', () => {
    const err = new AttioError('err', 400, { message: 'err' });
    expect(err.code).toBeUndefined();
  });

  it('code is undefined when body is not an object', () => {
    const err = new AttioError('err', 400, 'raw text');
    expect(err.code).toBeUndefined();
  });

  it('is an instance of Error', () => {
    const err = new AttioError('err', 500);
    expect(err).toBeInstanceOf(Error);
  });
});

describe('RateLimitError', () => {
  it('sets retryAfter and status 429', () => {
    const err = new RateLimitError(30);
    expect(err.retryAfter).toBe(30);
    expect(err.status).toBe(429);
    expect(err.name).toBe('RateLimitError');
  });

  it('is an instance of AttioError', () => {
    const err = new RateLimitError(10);
    expect(err).toBeInstanceOf(AttioError);
    expect(err).toBeInstanceOf(Error);
  });

  it('includes retryAfter in message', () => {
    const err = new RateLimitError(5);
    expect(err.message).toContain('5');
  });
});

describe('ScopeError', () => {
  it('sets status 403', () => {
    const err = new ScopeError('Forbidden: missing scope');
    expect(err.status).toBe(403);
    expect(err.name).toBe('ScopeError');
    expect(err.message).toBe('Forbidden: missing scope');
  });

  it('is an instance of AttioError', () => {
    const err = new ScopeError('msg');
    expect(err).toBeInstanceOf(AttioError);
    expect(err).toBeInstanceOf(Error);
  });

  it('stores body', () => {
    const err = new ScopeError('msg', { scopes: ['record:read'] });
    expect(err.body).toEqual({ scopes: ['record:read'] });
  });
});
