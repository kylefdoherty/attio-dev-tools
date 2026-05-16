/**
 * Shared fixtures and configuration for VCR-based integration tests.
 *
 * These tests use a lightweight VCR layer to record and replay real API
 * responses. Cassette files (YAML) are committed to the repo so tests
 * work without an API key.
 *
 * To record new cassettes:
 *     VCR_RECORD_MODE=all \
 *     ATTIO_API_KEY=$(op read "op://Personal/attio-dev-tools/credential") \
 *     yarn test -- --config vitest.integration.config.ts
 *
 * To replay from existing cassettes (default, no API key needed):
 *     yarn test -- --config vitest.integration.config.ts
 */

import { AttioClient } from '../../src/index.js';
import { getApiKey, RECORD_MODE } from './vcr.js';

let _apiKey: string | undefined;
let _client: AttioClient | undefined;

/**
 * Get the API key for integration tests.
 * In record mode, requires a real key (from env or 1Password).
 * In replay mode, returns a dummy key.
 */
export function apiKey(): string {
  if (_apiKey) return _apiKey;

  // In replay mode, skip the (potentially slow) 1Password lookup entirely
  if (RECORD_MODE === 'none') {
    _apiKey = process.env.ATTIO_API_KEY ?? 'sk_test_REPLAY_DUMMY';
    return _apiKey;
  }

  const key = getApiKey();

  if (!key) {
    throw new Error(
      'No ATTIO_API_KEY available for recording.\n' +
        'Set ATTIO_API_KEY env var or install the op CLI.\n' +
        'Example: ATTIO_API_KEY=$(op read "op://Personal/attio-dev-tools/credential")',
    );
  }

  _apiKey = key;
  return _apiKey;
}

/**
 * Get a shared AttioClient instance for integration tests.
 * Uses a real API key in record mode, dummy key in replay mode.
 */
export function client(): AttioClient {
  if (_client) return _client;

  _client = new AttioClient({
    apiKey: apiKey(),
    // Disable retries in tests to avoid confusion
    maxRetries: 0,
  });

  return _client;
}
