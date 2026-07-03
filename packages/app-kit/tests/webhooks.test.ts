import { createHmac } from 'node:crypto';
import { describe, expect, it } from 'vitest';
import type { AttioKV } from '../src/kv.js';
import { idempotencyGuard, verifyAttioSignature } from '../src/webhooks.js';

const sign = (body: string, secret: string) =>
  createHmac('sha256', secret).update(body).digest('hex');

describe('verifyAttioSignature', () => {
  const secret = 'whsec_test_secret_123';
  const body = JSON.stringify({
    webhook_id: 'b0d0a58a-0000-4000-8000-000000000000',
    events: [{ event_type: 'record.updated', id: { record_id: 'r1' } }],
  });

  it('accepts a valid signature', async () => {
    expect(await verifyAttioSignature(body, sign(body, secret), secret)).toBe(true);
  });

  it('accepts uppercase hex and surrounding whitespace', async () => {
    const header = `  ${sign(body, secret).toUpperCase()}  `;
    expect(await verifyAttioSignature(body, header, secret)).toBe(true);
  });

  it('rejects a tampered body', async () => {
    const header = sign(body, secret);
    expect(await verifyAttioSignature(`${body} `, header, secret)).toBe(false);
  });

  it('rejects a signature made with the wrong secret', async () => {
    expect(await verifyAttioSignature(body, sign(body, 'other-secret'), secret)).toBe(false);
  });

  it('rejects empty/missing header or secret without throwing', async () => {
    expect(await verifyAttioSignature(body, '', secret)).toBe(false);
    expect(await verifyAttioSignature(body, sign(body, secret), '')).toBe(false);
  });

  it('rejects malformed headers (non-hex, wrong length)', async () => {
    expect(await verifyAttioSignature(body, 'not-hex-at-all', secret)).toBe(false);
    expect(await verifyAttioSignature(body, sign(body, secret).slice(0, 40), secret)).toBe(false);
    expect(await verifyAttioSignature(body, `${sign(body, secret)}00`, secret)).toBe(false);
  });

  it('handles unicode bodies (UTF-8 encoding of the raw body)', async () => {
    const unicodeBody = '{"name":"Ünïcode 🎉"}';
    expect(
      await verifyAttioSignature(unicodeBody, sign(unicodeBody, secret), secret),
    ).toBe(true);
  });

  it('handles the empty body', async () => {
    expect(await verifyAttioSignature('', sign('', secret), secret)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Idempotency guard
// ---------------------------------------------------------------------------

interface FakeKVEntry {
  value: string;
  ttlInSeconds?: number;
}

function fakeKV(): AttioKV & { entries: Map<string, FakeKVEntry> } {
  const entries = new Map<string, FakeKVEntry>();
  return {
    entries,
    async get(key) {
      const entry = entries.get(key);
      return entry ? { value: entry.value } : null;
    },
    async set(key, value, options) {
      entries.set(key, { value, ttlInSeconds: options?.ttlInSeconds });
    },
    async delete(key) {
      entries.delete(key);
    },
  };
}

describe('idempotencyGuard', () => {
  it('claims a fresh key, rejects the duplicate', async () => {
    const idem = idempotencyGuard(fakeKV());
    expect(await idem.claim('evt-1')).toBe(true);
    expect(await idem.claim('evt-1')).toBe(false);
    expect(await idem.claim('evt-2')).toBe(true);
  });

  it('stores under a prefixed key with the default 24h TTL', async () => {
    const kv = fakeKV();
    const idem = idempotencyGuard(kv);
    await idem.claim('evt-1');
    const entry = kv.entries.get('idempotency:evt-1');
    expect(entry).toBeDefined();
    expect(entry?.ttlInSeconds).toBe(24 * 60 * 60);
  });

  it('honors custom TTL and prefix', async () => {
    const kv = fakeKV();
    const idem = idempotencyGuard(kv, { ttlInSeconds: 60, prefix: 'wh:' });
    await idem.claim('k');
    expect(kv.entries.get('wh:k')?.ttlInSeconds).toBe(60);
  });

  it('seen() checks without claiming', async () => {
    const idem = idempotencyGuard(fakeKV());
    expect(await idem.seen('evt-1')).toBe(false);
    expect(await idem.claim('evt-1')).toBe(true);
    expect(await idem.seen('evt-1')).toBe(true);
  });

  it('release() lets a key be claimed again', async () => {
    const idem = idempotencyGuard(fakeKV());
    await idem.claim('evt-1');
    await idem.release('evt-1');
    expect(await idem.claim('evt-1')).toBe(true);
  });

  it('works with a synchronous (non-promise) kv', async () => {
    const entries = new Map<string, string>();
    const syncKv: AttioKV = {
      get: (key) => (entries.has(key) ? { value: entries.get(key) as string } : null),
      set: (key, value) => {
        entries.set(key, value);
      },
      delete: (key) => {
        entries.delete(key);
      },
    };
    const idem = idempotencyGuard(syncKv);
    expect(await idem.claim('a')).toBe(true);
    expect(await idem.claim('a')).toBe(false);
  });
});
