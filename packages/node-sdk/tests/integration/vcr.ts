/**
 * Lightweight VCR (Video Cassette Recorder) for integration tests.
 *
 * Records real HTTP interactions to YAML cassette files and replays them
 * in future test runs. This catches API contract changes that hand-crafted
 * MSW mocks cannot.
 *
 * Usage:
 *   - Record mode:  VCR_RECORD_MODE=all ATTIO_API_KEY=sk_... vitest run
 *   - Replay mode:  vitest run  (default, no API key needed)
 *
 * Cassettes are stored in tests/integration/cassettes/ and should be
 * committed to the repo.
 */

import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { afterEach, beforeEach } from 'vitest';
import YAML from 'yaml';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CassetteInteraction {
  request: {
    method: string;
    url: string;
    headers: Record<string, string>;
    body: string;
  };
  response: {
    status: number;
    statusText: string;
    headers: Record<string, string>;
    body: string;
  };
}

interface Cassette {
  version: 1;
  interactions: CassetteInteraction[];
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

export const CASSETTE_DIR = path.join(__dirname, 'cassettes');
export const RECORD_MODE = process.env.VCR_RECORD_MODE ?? 'none';

// PII fields to scrub from recorded responses
const SCRUB_FIELDS: Record<string, string> = {
  first_name: 'Test',
  last_name: 'User',
  full_name: 'Test User',
  email_address: 'test@example.com',
  workspace_name: 'Test Workspace',
  workspace_slug: 'test-workspace',
  secret: 'REDACTED_WEBHOOK_SECRET',
};

// ---------------------------------------------------------------------------
// API Key
// ---------------------------------------------------------------------------

export function getApiKey(): string | undefined {
  const key = process.env.ATTIO_API_KEY;
  if (key) return key;

  try {
    const result = execSync('op read "op://Personal/attio-dev-tools/credential"', {
      timeout: 10_000,
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    return result.trim() || undefined;
  } catch {
    return undefined;
  }
}

// ---------------------------------------------------------------------------
// PII scrubbing
// ---------------------------------------------------------------------------

function scrubDict(obj: unknown): void {
  if (Array.isArray(obj)) {
    for (const item of obj) scrubDict(item);
  } else if (obj && typeof obj === 'object') {
    const record = obj as Record<string, unknown>;
    for (const [field, replacement] of Object.entries(SCRUB_FIELDS)) {
      if (field in record && typeof record[field] === 'string') {
        record[field] = replacement;
      }
    }
    for (const value of Object.values(record)) {
      scrubDict(value);
    }
  }
}

function scrubRequestHeaders(headers: Record<string, string>): Record<string, string> {
  const scrubbed = { ...headers };
  for (const key of ['authorization', 'Authorization', 'cookie', 'Cookie']) {
    if (key in scrubbed) {
      scrubbed[key] = 'Bearer sk_test_REDACTED';
    }
  }
  return scrubbed;
}

function scrubResponseBody(body: string): string {
  try {
    const data = JSON.parse(body);
    scrubDict(data);
    return JSON.stringify(data);
  } catch {
    return body;
  }
}

// ---------------------------------------------------------------------------
// Cassette I/O
// ---------------------------------------------------------------------------

function loadCassette(filePath: string): Cassette | null {
  if (!fs.existsSync(filePath)) return null;
  const content = fs.readFileSync(filePath, 'utf-8');
  return YAML.parse(content) as Cassette;
}

function saveCassette(filePath: string, cassette: Cassette): void {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, YAML.stringify(cassette, { lineWidth: 0 }), 'utf-8');
}

// ---------------------------------------------------------------------------
// Fetch interception
// ---------------------------------------------------------------------------

const _originalFetch = globalThis.fetch;

function createReplayFetch(cassette: Cassette): typeof fetch {
  let index = 0;

  return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    if (index >= cassette.interactions.length) {
      throw new Error(
        `VCR replay exhausted: no more interactions in cassette ` +
          `(expected ${cassette.interactions.length}, got request #${index + 1}). ` +
          `Re-record cassettes with VCR_RECORD_MODE=all.`,
      );
    }

    const interaction = cassette.interactions[index++];
    const requestUrl = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;

    // Match on method + URL path (ignore host differences)
    const expectedPath = new URL(interaction.request.url).pathname + new URL(interaction.request.url).search;
    const actualPath = new URL(requestUrl).pathname + new URL(requestUrl).search;
    const expectedMethod = interaction.request.method;
    const actualMethod = init?.method ?? 'GET';

    if (expectedMethod !== actualMethod || expectedPath !== actualPath) {
      throw new Error(
        `VCR replay mismatch at interaction #${index}:\n` +
          `  Expected: ${expectedMethod} ${expectedPath}\n` +
          `  Got:      ${actualMethod} ${actualPath}\n` +
          `Re-record cassettes with VCR_RECORD_MODE=all.`,
      );
    }

    return new Response(interaction.response.body, {
      status: interaction.response.status,
      statusText: interaction.response.statusText,
      headers: interaction.response.headers,
    });
  };
}

function createRecordFetch(interactions: CassetteInteraction[]): typeof fetch {
  return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    // Make the real request
    const response = await _originalFetch(input, init);

    // Capture request details
    const requestUrl = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
    const requestMethod = init?.method ?? 'GET';
    const requestHeaders: Record<string, string> = {};
    if (init?.headers) {
      const h = new Headers(init.headers);
      h.forEach((value, key) => {
        requestHeaders[key] = value;
      });
    }
    const requestBody = init?.body ? String(init.body) : '';

    // Capture response (clone so caller can still read it)
    const responseBody = await response.clone().text();
    const responseHeaders: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });

    // Remove set-cookie from response headers (not needed for replay)
    delete responseHeaders['set-cookie'];

    // Scrub PII before storing
    interactions.push({
      request: {
        method: requestMethod,
        url: requestUrl,
        headers: scrubRequestHeaders(requestHeaders),
        body: requestBody,
      },
      response: {
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
        body: scrubResponseBody(responseBody),
      },
    });

    return response;
  };
}

// ---------------------------------------------------------------------------
// Public API: useCassette
// ---------------------------------------------------------------------------

/**
 * Vitest helper that wraps a test in a VCR cassette.
 *
 * In replay mode (default): intercepts fetch and returns recorded responses.
 * In record mode (VCR_RECORD_MODE=all): records real API responses to disk.
 *
 * @example
 * ```ts
 * describe('objects', () => {
 *   useCassette('objects_list');
 *
 *   it('lists objects', async () => {
 *     const result = await client.objects.list();
 *     expect(result.data.length).toBeGreaterThan(0);
 *   });
 * });
 * ```
 */
export function useCassette(name: string): void {
  const filePath = path.join(CASSETTE_DIR, `${name}.yaml`);
  let interactions: CassetteInteraction[] = [];

  beforeEach(() => {
    if (RECORD_MODE === 'none') {
      // Replay mode
      const cassette = loadCassette(filePath);
      if (!cassette) {
        throw new Error(
          `VCR cassette not found: ${filePath}\n` +
            `Record it first: VCR_RECORD_MODE=all ATTIO_API_KEY=... vitest run`,
        );
      }
      globalThis.fetch = createReplayFetch(cassette);
    } else {
      // Record mode
      interactions = [];
      globalThis.fetch = createRecordFetch(interactions);
    }
  });

  afterEach(() => {
    // Restore original fetch
    globalThis.fetch = _originalFetch;

    // Save cassette if we were recording
    if (RECORD_MODE !== 'none' && interactions.length > 0) {
      saveCassette(filePath, { version: 1, interactions });
    }
  });
}

/**
 * Wrapper for running a single async callback inside a named cassette.
 * Useful when you need multiple cassettes in the same describe block.
 *
 * @example
 * ```ts
 * it('creates a record', async () => {
 *   await withCassette('records_create', async () => {
 *     const result = await client.records.create('people', { ... });
 *     expect(result.data).toBeDefined();
 *   });
 * });
 * ```
 */
export async function withCassette<T>(name: string, fn: () => Promise<T>): Promise<T> {
  const filePath = path.join(CASSETTE_DIR, `${name}.yaml`);

  if (RECORD_MODE === 'none') {
    // Replay mode
    const cassette = loadCassette(filePath);
    if (!cassette) {
      throw new Error(
        `VCR cassette not found: ${filePath}\n` +
          `Record it first: VCR_RECORD_MODE=all ATTIO_API_KEY=... vitest run`,
      );
    }
    globalThis.fetch = createReplayFetch(cassette);
    try {
      return await fn();
    } finally {
      globalThis.fetch = _originalFetch;
    }
  } else {
    // Record mode -- always save interactions (even if fn throws), so
    // error responses get persisted and can be replayed.
    const interactions: CassetteInteraction[] = [];
    globalThis.fetch = createRecordFetch(interactions);
    try {
      return await fn();
    } finally {
      globalThis.fetch = _originalFetch;
      if (interactions.length > 0) {
        saveCassette(filePath, { version: 1, interactions });
      }
    }
  }
}
