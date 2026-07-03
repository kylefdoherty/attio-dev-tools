import { createHmac, createHash } from 'node:crypto';
import { describe, expect, it } from 'vitest';
import {
  bytesToHex,
  hmacSha256,
  hmacSha256Hex,
  sha256,
  timingSafeEqualString,
  utf8,
} from '../src/sha256.js';

const hex = (bytes: Uint8Array) => bytesToHex(bytes);

describe('sha256 (pure TS)', () => {
  // FIPS 180-4 / NIST test vectors
  it('hashes the empty string', () => {
    expect(hex(sha256(utf8('')))).toBe(
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    );
  });

  it('hashes "abc"', () => {
    expect(hex(sha256(utf8('abc')))).toBe(
      'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
    );
  });

  it('hashes the two-block NIST vector', () => {
    expect(hex(sha256(utf8('abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq')))).toBe(
      '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1',
    );
  });

  it('hashes one million "a"s', () => {
    const million = new Uint8Array(1_000_000).fill(0x61);
    expect(hex(sha256(million))).toBe(
      'cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0',
    );
  });

  it('handles messages at block-boundary lengths (55, 56, 63, 64, 65 bytes)', () => {
    for (const len of [55, 56, 63, 64, 65, 119, 120]) {
      const message = new Uint8Array(len).fill(0x41);
      const expected = createHash('sha256').update(message).digest('hex');
      expect(hex(sha256(message)), `length ${len}`).toBe(expected);
    }
  });

  it('handles arbitrary binary input (all byte values)', () => {
    const message = new Uint8Array(256);
    for (let i = 0; i < 256; i++) message[i] = i;
    const expected = createHash('sha256').update(message).digest('hex');
    expect(hex(sha256(message))).toBe(expected);
  });

  it('matches node:crypto on random inputs', () => {
    for (let trial = 0; trial < 25; trial++) {
      const len = Math.floor(Math.random() * 300);
      const message = new Uint8Array(len);
      for (let i = 0; i < len; i++) message[i] = Math.floor(Math.random() * 256);
      const expected = createHash('sha256').update(message).digest('hex');
      expect(hex(sha256(message))).toBe(expected);
    }
  });
});

describe('hmacSha256 (pure TS) — RFC 4231 vectors', () => {
  it('test case 1', () => {
    const key = new Uint8Array(20).fill(0x0b);
    expect(hex(hmacSha256(key, utf8('Hi There')))).toBe(
      'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7',
    );
  });

  it('test case 2 (short key "Jefe")', () => {
    expect(hex(hmacSha256(utf8('Jefe'), utf8('what do ya want for nothing?')))).toBe(
      '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843',
    );
  });

  it('test case 3 (0xaa key, 0xdd data)', () => {
    const key = new Uint8Array(20).fill(0xaa);
    const data = new Uint8Array(50).fill(0xdd);
    expect(hex(hmacSha256(key, data))).toBe(
      '773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe',
    );
  });

  it('test case 4 (incrementing key, 0xcd data)', () => {
    const key = new Uint8Array(25);
    for (let i = 0; i < 25; i++) key[i] = i + 1;
    const data = new Uint8Array(50).fill(0xcd);
    expect(hex(hmacSha256(key, data))).toBe(
      '82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b',
    );
  });

  it('test case 6 (key larger than block size — hashed first)', () => {
    const key = new Uint8Array(131).fill(0xaa);
    expect(hex(hmacSha256(key, utf8('Test Using Larger Than Block-Size Key - Hash Key First')))).toBe(
      '60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54',
    );
  });

  it('test case 7 (large key and large data)', () => {
    const key = new Uint8Array(131).fill(0xaa);
    const message = utf8(
      'This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm.',
    );
    expect(hex(hmacSha256(key, message))).toBe(
      '9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2',
    );
  });

  it('exact block-size key (64 bytes) is used as-is', () => {
    const key = new Uint8Array(64).fill(0x7f);
    const expected = createHmac('sha256', key).update('boundary').digest('hex');
    expect(hex(hmacSha256(key, utf8('boundary')))).toBe(expected);
  });

  it('matches node:crypto for unicode secrets and bodies', () => {
    const secret = 'wébhook-secrèt-日本語';
    const body = '{"events":[{"emoji":"🎉","text":"héllo"}]}';
    const expected = createHmac('sha256', secret).update(body).digest('hex');
    expect(hex(hmacSha256(utf8(secret), utf8(body)))).toBe(expected);
  });
});

describe('hmacSha256Hex (runtime dispatch)', () => {
  it('produces the same digest as node:crypto (WebCrypto path in Node)', async () => {
    const expected = createHmac('sha256', 'secret').update('payload').digest('hex');
    expect(await hmacSha256Hex('secret', 'payload')).toBe(expected);
  });

  it('WebCrypto path and pure path agree', async () => {
    const viaDispatch = await hmacSha256Hex('key-123', 'body-456');
    const viaPure = hex(hmacSha256(utf8('key-123'), utf8('body-456')));
    expect(viaDispatch).toBe(viaPure);
  });
});

describe('timingSafeEqualString', () => {
  it('returns true for equal strings', () => {
    expect(timingSafeEqualString('abcdef012345', 'abcdef012345')).toBe(true);
  });

  it('returns false for different strings of equal length', () => {
    expect(timingSafeEqualString('abcdef012345', 'abcdef012346')).toBe(false);
  });

  it('returns false for different lengths', () => {
    expect(timingSafeEqualString('abc', 'abcd')).toBe(false);
    expect(timingSafeEqualString('abcd', 'abc')).toBe(false);
  });

  it('handles empty strings', () => {
    expect(timingSafeEqualString('', '')).toBe(true);
    expect(timingSafeEqualString('a', '')).toBe(false);
    expect(timingSafeEqualString('', 'a')).toBe(false);
  });
});
