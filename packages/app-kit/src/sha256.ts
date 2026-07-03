/**
 * Pure-TypeScript SHA-256 and HMAC-SHA256.
 *
 * The Attio App SDK server sandbox does not document WebCrypto (`crypto.subtle`)
 * among its available globals, and there is no `node:crypto`. This module
 * implements SHA-256 (FIPS 180-4) and HMAC (RFC 2104) using only standard
 * JavaScript, and opportunistically uses WebCrypto when it is detected at
 * runtime (Node 18+, browsers, workers).
 *
 * Verified against FIPS 180-4 / RFC 4231 test vectors in tests/sha256.test.ts.
 */

// SHA-256 round constants (first 32 bits of the fractional parts of the cube
// roots of the first 64 primes).
const K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

// Initial hash values (first 32 bits of the fractional parts of the square
// roots of the first 8 primes).
const H_INIT = new Uint32Array([
  0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]);

function rotr(x: number, n: number): number {
  return ((x >>> n) | (x << (32 - n))) >>> 0;
}

/**
 * Compute the SHA-256 digest of `data`.
 */
export function sha256(data: Uint8Array): Uint8Array {
  const len = data.length;
  // Message + 0x80 + zero padding + 64-bit big-endian bit length, padded to a
  // multiple of 64 bytes.
  const paddedLen = Math.ceil((len + 9) / 64) * 64;
  const padded = new Uint8Array(paddedLen);
  padded.set(data);
  padded[len] = 0x80;
  const view = new DataView(padded.buffer);
  const bitLen = len * 8; // exact for any realistic payload (< 2^53)
  view.setUint32(paddedLen - 8, Math.floor(bitLen / 0x100000000), false);
  view.setUint32(paddedLen - 4, bitLen >>> 0, false);

  const h = new Uint32Array(H_INIT);
  const w = new Uint32Array(64);

  for (let offset = 0; offset < paddedLen; offset += 64) {
    for (let i = 0; i < 16; i++) {
      w[i] = view.getUint32(offset + i * 4, false);
    }
    for (let i = 16; i < 64; i++) {
      const w15 = w[i - 15];
      const w2 = w[i - 2];
      const s0 = (rotr(w15, 7) ^ rotr(w15, 18) ^ (w15 >>> 3)) >>> 0;
      const s1 = (rotr(w2, 17) ^ rotr(w2, 19) ^ (w2 >>> 10)) >>> 0;
      w[i] = w[i - 16] + s0 + w[i - 7] + s1; // Uint32Array store wraps mod 2^32
    }

    let a = h[0];
    let b = h[1];
    let c = h[2];
    let d = h[3];
    let e = h[4];
    let f = h[5];
    let g = h[6];
    let hh = h[7];

    for (let i = 0; i < 64; i++) {
      const S1 = (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) >>> 0;
      const ch = ((e & f) ^ (~e & g)) >>> 0;
      const temp1 = (hh + S1 + ch + K[i] + w[i]) >>> 0;
      const S0 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) >>> 0;
      const maj = ((a & b) ^ (a & c) ^ (b & c)) >>> 0;
      const temp2 = (S0 + maj) >>> 0;
      hh = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }

    h[0] += a;
    h[1] += b;
    h[2] += c;
    h[3] += d;
    h[4] += e;
    h[5] += f;
    h[6] += g;
    h[7] += hh;
  }

  const out = new Uint8Array(32);
  const outView = new DataView(out.buffer);
  for (let i = 0; i < 8; i++) {
    outView.setUint32(i * 4, h[i], false);
  }
  return out;
}

/**
 * Compute HMAC-SHA256 of `message` with `key` (RFC 2104), pure TypeScript.
 */
export function hmacSha256(key: Uint8Array, message: Uint8Array): Uint8Array {
  const BLOCK_SIZE = 64;
  let normalizedKey = key;
  if (normalizedKey.length > BLOCK_SIZE) {
    normalizedKey = sha256(normalizedKey);
  }
  const ipad = new Uint8Array(BLOCK_SIZE + message.length);
  const opad = new Uint8Array(BLOCK_SIZE + 32);
  for (let i = 0; i < BLOCK_SIZE; i++) {
    const k = i < normalizedKey.length ? normalizedKey[i] : 0;
    ipad[i] = k ^ 0x36;
    opad[i] = k ^ 0x5c;
  }
  ipad.set(message, BLOCK_SIZE);
  opad.set(sha256(ipad), BLOCK_SIZE);
  return sha256(opad);
}

/** Encode a string as UTF-8 bytes. */
export function utf8(input: string): Uint8Array {
  return new TextEncoder().encode(input);
}

/** Lowercase hex encoding of a byte array. */
export function bytesToHex(bytes: Uint8Array): string {
  let hex = '';
  for (let i = 0; i < bytes.length; i++) {
    hex += bytes[i].toString(16).padStart(2, '0');
  }
  return hex;
}

// ---------------------------------------------------------------------------
// WebCrypto fast path (used when detected at runtime)
// ---------------------------------------------------------------------------

/**
 * Minimal structural type for `crypto.subtle` so this module compiles without
 * DOM or Node type libs.
 */
interface MinimalSubtle {
  importKey(
    format: string,
    keyData: Uint8Array,
    algorithm: { name: string; hash: string },
    extractable: boolean,
    keyUsages: string[],
  ): Promise<unknown>;
  sign(algorithm: string, key: unknown, data: Uint8Array): Promise<ArrayBuffer>;
}

function detectSubtle(): MinimalSubtle | null {
  const g = globalThis as { crypto?: { subtle?: MinimalSubtle } };
  const subtle = g.crypto?.subtle;
  if (subtle && typeof subtle.importKey === 'function' && typeof subtle.sign === 'function') {
    return subtle;
  }
  return null;
}

/**
 * Hex HMAC-SHA256 of `message` keyed by `secret` (both UTF-8 strings).
 *
 * Uses WebCrypto (`crypto.subtle`) when available at runtime; otherwise falls
 * back to the pure-TypeScript implementation. The Attio server sandbox does
 * not document WebCrypto, so the fallback is the expected path there.
 */
export async function hmacSha256Hex(secret: string, message: string): Promise<string> {
  const subtle = detectSubtle();
  if (subtle) {
    try {
      const key = await subtle.importKey(
        'raw',
        utf8(secret),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign'],
      );
      const signature = await subtle.sign('HMAC', key, utf8(message));
      return bytesToHex(new Uint8Array(signature));
    } catch {
      // Some sandboxes expose a crippled subtle — fall through to pure TS.
    }
  }
  return bytesToHex(hmacSha256(utf8(secret), utf8(message)));
}

/**
 * Constant-time string comparison. Always walks the full length of `a` and
 * folds any length mismatch into the result, so timing does not reveal how
 * many leading characters matched.
 */
export function timingSafeEqualString(a: string, b: string): boolean {
  const aBytes = utf8(a);
  const bBytes = utf8(b);
  let diff = aBytes.length ^ bBytes.length;
  const bLen = bBytes.length || 1;
  for (let i = 0; i < aBytes.length; i++) {
    diff |= aBytes[i] ^ (bBytes[i % bLen] ?? 0);
  }
  return diff === 0;
}
