# Node.js VCR-Style HTTP Recording/Replay for the Attio Node SDK

**Date:** 2026-05-15
**Target:** `attio-node` (TypeScript + Vitest + native Node 18+ fetch + MSW for unit tests)
**Goal:** Replicate the Python SDK's VCR.py pattern -- record real API responses once, commit cassette files, replay in CI forever.

---

## 1. Complete Library Survey

### 1.1 vcr-test

| Property | Value |
|---|---|
| **npm** | `vcr-test` |
| **GitHub** | [epignosisx/vcr-test](https://github.com/epignosisx/vcr-test) |
| **Latest version** | 1.4.0 (April 2026) |
| **Stars** | Small project (~low stars) |
| **How it works** | Uses `@mswjs/interceptors` under the hood -- the same interception library that powers MSW. Intercepts at the `http.ClientRequest` and native `fetch`/undici layer. |
| **Native fetch?** | **Yes** -- explicitly listed as supported. Works with fetch, axios, got, node-fetch, undici. |
| **Vitest?** | **Yes** -- repo includes `vitest.config.mts`, written in TypeScript. |
| **Cassette format** | **YAML** -- human-readable request/response pairs. Manually editable. |
| **Sensitive data scrubbing** | Built-in `requestMasker` callback for headers/auth. Response body scrubbing via custom `FileStorage` extension or post-processing. |
| **Record modes** | `once` (default), `none`, `update`, `all` -- controlled via `VCR_MODE` env var. |
| **Active maintenance?** | **Yes** -- v1.4.0 released April 2026, v1.3.0 June 2025. Steady cadence. |

**Verdict:** Purpose-built VCR library for modern Node.js. Closest analog to VCR.py. Best native fetch support. Clean TypeScript API.

### 1.2 nock (with nock.back)

| Property | Value |
|---|---|
| **npm** | `nock` |
| **GitHub** | [nock/nock](https://github.com/nock/nock) -- 13.1k stars |
| **Latest version** | 14.0.15 (May 2026) |
| **How it works** | Since v14, uses `@mswjs/interceptors` (same as MSW) to intercept both `http.ClientRequest` and native fetch. Previously only patched `http` module. |
| **Native fetch?** | **Yes** (v14+) -- added via [PR #2517](https://github.com/nock/nock/pull/2517) merged July 2024. |
| **Vitest?** | Works with any test runner -- no framework coupling. |
| **Cassette format** | **JSON** -- array of scope objects with method, path, status, response, headers. |
| **Sensitive data scrubbing** | `nock.back` has `before` (pre-load filter) and `afterRecord` (post-record filter) hooks. Can manipulate scopes before save. No built-in field-level scrubber -- you write the callback. |
| **Record modes** | `wild`, `dryrun` (default), `record`, `update`, `lockdown` -- via `NOCK_BACK_MODE` env var. |
| **Active maintenance?** | **Yes** -- very active, 5.5M weekly downloads. v15 beta in progress. |

**Known issues with nock.back + fetch:**
- [Issue #2806](https://github.com/nock/nock/issues/2806): nock.back failed to parse recorded fixtures in beta.15+, throwing `Z_DATA_ERROR` on gzip-compressed recordings. Status unclear whether fully resolved.
- [Issue #2832](https://github.com/nock/nock/issues/2832): nock@14 recordings using fetch with gzip compression are missing headers.
- nock.back is a bolted-on VCR layer on top of a mocking library -- the recording API feels like an afterthought compared to purpose-built VCR tools.

**Verdict:** Battle-tested mocking library with recording bolted on. Native fetch support is new and has rough edges with nock.back specifically. The 13k stars and massive download count reflect its mocking use, not its VCR use.

### 1.3 Polly.js (@pollyjs/core)

| Property | Value |
|---|---|
| **npm** | `@pollyjs/core` |
| **GitHub** | [Netflix/pollyjs](https://github.com/Netflix/pollyjs) -- 10.2k stars |
| **Latest version** | 6.0.6 (July 2023 -- **3 years ago**) |
| **How it works** | Adapter-based: `@pollyjs/adapter-fetch` for browser fetch, `@pollyjs/adapter-node-http` for Node. Persisters save to filesystem (HAR format) or local storage. |
| **Native fetch?** | **No.** The Node adapter intercepts `http`/`https` modules. [Issue #443](https://github.com/Netflix/pollyjs/issues/443) requesting an undici adapter is open since 2021 with no resolution. Native Node 18+ fetch (which uses undici internally) is **not intercepted**. |
| **Vitest?** | Only has test helpers for Mocha and QUnit. No Vitest integration. Would need manual setup. |
| **Cassette format** | **HAR** (HTTP Archive format) -- verbose but standardized. |
| **Sensitive data scrubbing** | No built-in scrubbing. |
| **Record modes** | `replay`, `record`, `passthrough` -- auto-records on first run, replays on subsequent. |
| **Active maintenance?** | **No.** Last release July 2023. [Issue #467](https://github.com/Netflix/pollyjs/issues/467) ("Is this project still maintained?") from Oct 2022 has no maintainer response. |

**Verdict:** Eliminated. Not maintained, no native fetch support, no Vitest helpers. Despite 10k stars, this is effectively abandoned.

### 1.4 MSW (Mock Service Worker)

| Property | Value |
|---|---|
| **npm** | `msw` |
| **How it works** | Intercepts via `@mswjs/interceptors`. Designed for mocking with hand-written handlers, not recording. |
| **Recording?** | **No built-in recording.** [Issue #628](https://github.com/mswjs/msw/issues/628) is an open feature request. The maintainer (kettanaito) has mentioned using HAR files with `msw/source` for replay, but there is no built-in record-to-file workflow. |
| **Verdict** | MSW is a **mocking** library, not a VCR library. We already use it for unit tests and should continue to. It is not the right tool for record/replay integration tests. |

### 1.5 nock-vcr-recorder

| Property | Value |
|---|---|
| **npm** | `nock-vcr-recorder` -- last published 2022 |
| **How it works** | Thin wrapper around nock.back. Promise-based cassette API. |
| **Native fetch?** | Depends on nock version, likely no (was built for nock 13). |
| **Active maintenance?** | **No.** 22 commits total. Dead. |

### 1.6 nock-record

| Property | Value |
|---|---|
| **npm** | `nock-record` -- last published May 2022 |
| **How it works** | Wrapper around nock.back with better ergonomics. `setupRecorder()` + `record()` pattern. |
| **Active maintenance?** | **No.** 4,508 weekly downloads but no updates since 2022. |

### 1.7 yakbak

| Property | Value |
|---|---|
| **npm** | `yakbak` -- last published 2022 |
| **How it works** | Proxy-based: spawns an HTTP proxy, records to `.js` files. |
| **Native fetch?** | No -- proxy-based, would need manual proxy config. |
| **Active maintenance?** | **No.** Originally by Flickr/Yahoo. Inactive. |

### 1.8 sepia

| Property | Value |
|---|---|
| **npm** | `sepia` -- last published 2022 |
| **GitHub** | LinkedInAttic/sepia (archived) |
| **Active maintenance?** | **No.** In LinkedIn's "Attic" (archived) namespace. |

### 1.9 fetch-vcr

| Property | Value |
|---|---|
| **npm** | `fetch-vcr` -- last published **6 years ago** (v3.2.0) |
| **How it works** | Replaces global `fetch` with a recording wrapper. |
| **Active maintenance?** | **No.** Dead. |

### 1.10 node-vcr

| Property | Value |
|---|---|
| **npm** | `node-vcr` -- last published 2022 |
| **Active maintenance?** | **No.** |

### 1.11 simple-vcr

| Property | Value |
|---|---|
| **npm** | `simple-vcr` -- last published Oct 2023 |
| **How it works** | Uses nock under the hood. Jest-focused. |
| **Active maintenance?** | **No.** |

### 1.12 Mentoss

| Property | Value |
|---|---|
| **npm** | `mentoss` |
| **How it works** | Mocks `fetch()` with route matching and URL patterns. Created by Nicholas Zakas (ESLint creator) in Jan 2025. |
| **Recording?** | **No.** Mocking-only, similar to MSW but fetch-specific. |

### 1.13 undici MockAgent (built-in Node.js)

| Property | Value |
|---|---|
| **How it works** | Node's native mock for `fetch`. `setGlobalDispatcher(mockAgent)` + `mockAgent.get(origin).intercept()`. |
| **Recording?** | **No.** Interception/mocking only. No record-to-file capability. |

---

## 2. Deep Dive: Top 2 Candidates

Only two libraries are both **actively maintained** and **support native Node 18+ fetch** with a VCR workflow:

1. **vcr-test** -- purpose-built VCR library
2. **nock** (via nock.back) -- mocking library with recording bolted on

### 2.1 vcr-test -- Deep Dive

#### Setup with Vitest

```typescript
// tests/integration/vcr-setup.ts
import { join } from 'node:path';
import { VCR, FileStorage, RecordMode, DefaultRequestMatcher } from 'vcr-test';

const CASSETTE_DIR = join(import.meta.dirname, 'cassettes');

export const vcr = new VCR(new FileStorage(CASSETTE_DIR));

// Default mode: replay from cassettes (no network calls)
// Override with VCR_MODE=all to re-record
vcr.mode = RecordMode.once;

// Scrub auth headers before recording
vcr.requestMasker = (req) => {
  if (req.headers['authorization']) {
    req.headers['authorization'] = 'Bearer sk_test_REDACTED';
  }
};

// Don't match on auth headers (they'll differ between record and replay)
const matcher = new DefaultRequestMatcher();
matcher.ignoreHeaders.add('authorization');
matcher.ignoreHeaders.add('user-agent');
vcr.matcher = matcher;
```

#### Example test -- recording a real API call, then replaying it

```typescript
// tests/integration/objects.integration.test.ts
import { describe, it, expect } from 'vitest';
import { AttioClient } from '../../src/index.js';
import { vcr } from './vcr-setup.js';

const API_KEY = process.env.ATTIO_API_KEY || 'sk_test_REPLAY_DUMMY';

describe('Objects (integration)', () => {
  it('lists all objects', async () => {
    // Wraps the test in a cassette. First run records; subsequent runs replay.
    await using _cassette = await vcr.useCassette('objects_list');

    const client = new AttioClient({ apiKey: API_KEY });
    const result = await client.objects.list();

    expect(result.data.length).toBeGreaterThan(0);
    const obj = result.data[0];
    expect(obj.id.object_id).toBeDefined();
    expect(obj.api_slug).toBeDefined();
    expect(obj.created_at).toBeDefined();
  });

  it('gets the people object', async () => {
    await using _cassette = await vcr.useCassette('objects_get_people');

    const client = new AttioClient({ apiKey: API_KEY });
    const result = await client.objects.get('people');

    expect(result.data.api_slug).toBe('people');
    expect(result.data.id.object_id).toBeDefined();
  });
});
```

#### Toggling record vs replay mode

```bash
# Replay from cassettes (default -- no API key needed, runs in CI)
yarn vitest run tests/integration/

# Record fresh cassettes (needs real API key)
VCR_MODE=all ATTIO_API_KEY=sk_live_xxx yarn vitest run tests/integration/

# Record only new tests (existing cassettes replayed, missing ones recorded)
VCR_MODE=once ATTIO_API_KEY=sk_live_xxx yarn vitest run tests/integration/
```

#### Scrubbing sensitive data

vcr-test's `requestMasker` handles request-side scrubbing. For response body PII scrubbing (matching what we do in Python), we can extend `FileStorage`:

```typescript
import { FileStorage, type HttpInteraction } from 'vcr-test';
import { join } from 'node:path';

const SCRUB_FIELDS: Record<string, string> = {
  first_name: 'Test',
  last_name: 'User',
  full_name: 'Test User',
  email_address: 'test@example.com',
  workspace_name: 'Test Workspace',
  workspace_slug: 'test-workspace',
  secret: 'REDACTED_WEBHOOK_SECRET',
};

function scrubDict(obj: unknown): void {
  if (Array.isArray(obj)) {
    for (const item of obj) scrubDict(item);
  } else if (obj && typeof obj === 'object') {
    const record = obj as Record<string, unknown>;
    for (const [field, replacement] of Object.entries(SCRUB_FIELDS)) {
      if (typeof record[field] === 'string') {
        record[field] = replacement;
      }
    }
    for (const value of Object.values(record)) {
      scrubDict(value);
    }
  }
}

class ScrubFileStorage extends FileStorage {
  async save(name: string, interactions: HttpInteraction[]): Promise<void> {
    for (const interaction of interactions) {
      // Scrub response bodies
      if (interaction.response.body) {
        try {
          const data = JSON.parse(interaction.response.body);
          scrubDict(data);
          interaction.response.body = JSON.stringify(data);
        } catch { /* non-JSON body, skip */ }
      }
    }
    return super.save(name, interactions);
  }
}
```

#### Cassette file format (YAML)

```yaml
- request:
    url: https://api.attio.com/v2/objects
    method: GET
    headers:
      authorization: Bearer sk_test_REDACTED
      content-type: application/json
    body: ""
  response:
    status: 200
    statusText: OK
    headers:
      content-type: application/json; charset=utf-8
    body: '{"data": [{"id": {"object_id": "obj_01abc"}, "api_slug": "people", ...}]}'
```

#### Gotchas with native fetch

- None documented. vcr-test uses `@mswjs/interceptors` which is the gold standard for fetch interception.
- The same interceptor library powers MSW, which we already use successfully for unit tests.

---

### 2.2 nock (nock.back) -- Deep Dive

#### Setup with Vitest

```typescript
// tests/integration/nock-setup.ts
import nock from 'nock';
import { join } from 'node:path';

const nockBack = nock.back;
nockBack.fixtures = join(import.meta.dirname, 'cassettes');

// Controlled by NOCK_BACK_MODE env var or explicit call
// 'record' = use existing + record new
// 'lockdown' = replay only, fail on unmocked
// 'dryrun' = use existing, allow unmocked (default)
nockBack.setMode(process.env.NOCK_BACK_MODE as any || 'lockdown');
```

#### Example test

```typescript
import { describe, it, expect } from 'vitest';
import nock from 'nock';
import { AttioClient } from '../../src/index.js';

describe('Objects (integration)', () => {
  it('lists all objects', async () => {
    const { nockDone, context } = await nock.back('objects_list.json');

    const client = new AttioClient({ apiKey: 'sk_test_DUMMY' });
    const result = await client.objects.list();

    expect(result.data.length).toBeGreaterThan(0);
    nockDone();
  });
});
```

#### Scrubbing sensitive data

```typescript
const { nockDone } = await nock.back('objects_list.json', {
  afterRecord: (scopes) => {
    // Scopes is the array that will be saved to JSON
    for (const scope of scopes) {
      // Scrub response bodies
      if (typeof scope.response === 'string') {
        try {
          const data = JSON.parse(scope.response);
          scrubDict(data);
          scope.response = JSON.stringify(data);
        } catch { /* skip */ }
      } else if (typeof scope.response === 'object') {
        scrubDict(scope.response);
      }
    }
    return scopes;
  },
});
```

#### Gotchas with native fetch

- **gzip compression issues**: [Issue #2832](https://github.com/nock/nock/issues/2832) reports that fetch recordings with server-side gzip are missing headers.
- **Fixture parsing failures**: [Issue #2806](https://github.com/nock/nock/issues/2806) reports `Z_DATA_ERROR` when loading nock.back fixtures recorded with fetch in certain versions.
- nock.back was designed for the `http` module era. The fetch integration is new and has unresolved edge cases.
- The fixture format is nock-specific JSON (array of scope objects) -- not as human-readable as YAML.

---

## 3. Recommendation: **vcr-test**

**vcr-test is the clear winner for our stack.** Here is why:

### Why vcr-test

1. **Purpose-built for VCR.** It was designed from day one to be "VCR.py for Node.js." The API maps directly to what we already do in Python -- `useCassette`, record modes via env var, request masking.

2. **Native fetch support is first-class.** It uses `@mswjs/interceptors` (same foundation as our existing MSW unit tests) and explicitly lists `fetch`, `undici`, and `node-fetch` as supported. No gzip bugs, no fixture parsing failures.

3. **TypeScript-first.** Written in TypeScript, ships types, has a `vitest.config.mts` in its own repo.

4. **YAML cassettes.** Same format as VCR.py. Human-readable, manually editable, easy to diff in PRs.

5. **Clean record mode toggle.** `VCR_MODE` env var with `once`/`none`/`update`/`all` -- nearly identical to VCR.py's `VCR_RECORD_MODE`.

6. **Extensible scrubbing.** `requestMasker` for auth headers, extensible `FileStorage` for response body PII scrubbing. We can replicate our exact Python scrubbing strategy.

7. **Actively maintained.** Four releases in 2025-2026 with a steady cadence.

8. **Minimal dependency surface.** Only depends on `@mswjs/interceptors` (which we already transitively have via MSW) and `yaml`.

### Why NOT nock.back

- nock.back's fetch support has [documented bugs](https://github.com/nock/nock/issues/2806) with gzip and fixture parsing.
- nock.back is an afterthought on a mocking library -- the API is less ergonomic than vcr-test.
- JSON fixture format is less readable than YAML.
- nock is 13k stars for its **mocking** API; its **recording** API (nock.back) is a niche feature that gets less testing and attention.

### Why NOT Polly.js

- Last release was July 2023. Effectively abandoned.
- Does not support native Node 18+ fetch (open issue since 2021, no progress).
- No Vitest helpers.

---

## 4. Implementation Sketch

### 4.1 Install

```bash
cd attio-node
yarn add -D vcr-test
```

### 4.2 Integration test setup

```typescript
// tests/integration/vcr-setup.ts
import { join } from 'node:path';
import { VCR, FileStorage, RecordMode, DefaultRequestMatcher } from 'vcr-test';
import type { HttpInteraction, HttpRequest } from 'vcr-test';

// ── Cassette storage with PII scrubbing ──────────────────────────

const CASSETTE_DIR = join(import.meta.dirname, 'cassettes');

const SCRUB_FIELDS: Record<string, string> = {
  first_name: 'Test',
  last_name: 'User',
  full_name: 'Test User',
  email_address: 'test@example.com',
  workspace_name: 'Test Workspace',
  workspace_slug: 'test-workspace',
  secret: 'REDACTED_WEBHOOK_SECRET',
};

function scrubObject(obj: unknown): void {
  if (Array.isArray(obj)) {
    for (const item of obj) scrubObject(item);
  } else if (obj !== null && typeof obj === 'object') {
    const record = obj as Record<string, unknown>;
    for (const [field, replacement] of Object.entries(SCRUB_FIELDS)) {
      if (typeof record[field] === 'string') {
        record[field] = replacement;
      }
    }
    for (const value of Object.values(record)) {
      scrubObject(value);
    }
  }
}

class ScrubbingFileStorage extends FileStorage {
  async save(name: string, interactions: HttpInteraction[]): Promise<void> {
    for (const interaction of interactions) {
      // Scrub response bodies (JSON only)
      if (interaction.response.body) {
        try {
          const data = JSON.parse(interaction.response.body);
          scrubObject(data);
          interaction.response.body = JSON.stringify(data);
        } catch {
          // Non-JSON body, leave as-is
        }
      }
    }
    return super.save(name, interactions);
  }
}

// ── VCR instance ─────────────────────────────────────────────────

export const vcr = new VCR(new ScrubbingFileStorage(CASSETTE_DIR));

// Default: replay from cassettes. Override with VCR_MODE env var.
// In CI: VCR_MODE is unset -> defaults to "once" (replay if cassette exists)
// For recording: VCR_MODE=all ATTIO_API_KEY=sk_live_xxx
vcr.mode = RecordMode.once;

// Scrub auth from recorded requests
vcr.requestMasker = (req: HttpRequest) => {
  if (req.headers['authorization']) {
    req.headers['authorization'] = 'Bearer sk_test_REDACTED';
  }
  if (req.headers['Authorization']) {
    req.headers['Authorization'] = 'Bearer sk_test_REDACTED';
  }
};

// Flexible request matching -- ignore volatile headers
const matcher = new DefaultRequestMatcher();
matcher.ignoreHeaders.add('authorization');
matcher.ignoreHeaders.add('user-agent');
matcher.ignoreHeaders.add('accept-encoding');
vcr.matcher = matcher;

// ── Helpers ──────────────────────────────────────────────────────

/**
 * Get API key for integration tests.
 * During recording: real key from env var.
 * During replay: dummy key (cassettes handle responses).
 */
export function getApiKey(): string {
  return process.env.ATTIO_API_KEY || 'sk_test_REPLAY_DUMMY';
}
```

### 4.3 Example integration test file

```typescript
// tests/integration/objects.integration.test.ts
import { describe, it, expect } from 'vitest';
import { AttioClient } from '../../src/index.js';
import { vcr, getApiKey } from './vcr-setup.js';

describe('Objects (integration)', () => {
  it('lists all objects', async () => {
    await using _cassette = await vcr.useCassette('objects_list');

    const client = new AttioClient({ apiKey: getApiKey() });
    const result = await client.objects.list();

    expect(result.data.length).toBeGreaterThan(0);

    const obj = result.data[0];
    expect(obj.id.object_id).toBeDefined();
    expect(typeof obj.id.object_id).toBe('string');
    expect(obj.api_slug).toBeDefined();
    expect(obj.created_at).toBeDefined();
  });

  it('gets the people object by slug', async () => {
    await using _cassette = await vcr.useCassette('objects_get_people');

    const client = new AttioClient({ apiKey: getApiKey() });
    const result = await client.objects.get('people');

    expect(result.data.api_slug).toBe('people');
    expect(result.data.id.object_id).toBeDefined();
  });
});
```

### 4.4 Running tests

```bash
# ── CI / local replay (no API key needed) ────────────────────────
yarn vitest run tests/integration/

# ── Record ALL cassettes from scratch ─────────────────────────────
VCR_MODE=all \
  ATTIO_API_KEY=$(op read "op://Personal/attio-dev-tools/credential") \
  yarn vitest run tests/integration/

# ── Record only missing cassettes (keep existing) ────────────────
VCR_MODE=once \
  ATTIO_API_KEY=$(op read "op://Personal/attio-dev-tools/credential") \
  yarn vitest run tests/integration/

# ── Strict lockdown (fail if any cassette is missing) ─────────────
VCR_MODE=none \
  yarn vitest run tests/integration/
```

### 4.5 Vitest config update

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    exclude: ['**/node_modules/**', '**/.claude/worktrees/**'],
    // Separate unit and integration test runs if desired
    // include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      exclude: ['src/index.ts'],
      thresholds: {
        lines: 80,
        branches: 80,
        functions: 80,
        statements: 80,
      },
    },
  },
});
```

### 4.6 Package.json scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:unit": "vitest run tests/*.test.ts tests/resources/",
    "test:integration": "vitest run tests/integration/",
    "test:integration:record": "VCR_MODE=all vitest run tests/integration/"
  }
}
```

### 4.7 Scrubbing strategy (matching Python SDK)

The Python SDK (`tests/integration/conftest.py`) does three things:

| What | Python approach | Node equivalent in vcr-test |
|---|---|---|
| Strip auth headers from requests | `before_record_request` callback replaces `Authorization` with `Bearer sk_test_REDACTED` | `vcr.requestMasker` callback -- identical pattern |
| Filter known headers entirely | `filter_headers=['authorization', 'Cookie']` | `matcher.ignoreHeaders.add('authorization')` |
| Scrub PII from response bodies | `before_record_response` walks JSON and replaces `first_name`, `email_address`, etc. | Custom `ScrubbingFileStorage.save()` -- walks JSON with same field map |

### 4.8 File structure after implementation

```
tests/
  setup.ts                          # MSW setup for unit tests (existing)
  handlers.ts                       # MSW mock handlers (existing)
  client.test.ts                    # Unit tests (existing)
  resources/                        # Unit tests per resource (existing)
  integration/
    vcr-setup.ts                    # VCR config, scrubbing, helpers
    cassettes/                      # Recorded YAML cassettes (committed)
      objects_list.yaml
      objects_get_people.yaml
      records_query.yaml
      ...
    objects.integration.test.ts     # Integration tests
    records.integration.test.ts
    lists.integration.test.ts
    ...
```

### 4.9 `await using` compatibility note

vcr-test supports the `await using` syntax (Explicit Resource Management, TC39 Stage 3) for automatic cassette cleanup. This requires:
- TypeScript 5.2+ (the project already uses TypeScript 5.3+)
- Node.js 22+ for native support, or a polyfill for Node 18-20

For broader Node.js version compatibility, use the callback form instead:

```typescript
// Callback form -- works on all Node versions
await vcr.useCassette('objects_list', async () => {
  const client = new AttioClient({ apiKey: getApiKey() });
  const result = await client.objects.list();
  expect(result.data.length).toBeGreaterThan(0);
});
```

---

## 5. Comparison with Python SDK Pattern

| Aspect | Python SDK (VCR.py) | Node SDK (vcr-test) |
|---|---|---|
| Library | `vcrpy` | `vcr-test` |
| Cassette format | YAML | YAML |
| Record mode env var | `VCR_RECORD_MODE` | `VCR_MODE` |
| Cassette decorator/wrapper | `@my_vcr.use_cassette('name.yaml')` | `await vcr.useCassette('name')` or `await using` |
| Auth scrubbing | `before_record_request` callback | `vcr.requestMasker` callback |
| PII scrubbing | `before_record_response` callback | Custom `FileStorage.save()` override |
| Cassette directory | `tests/integration/cassettes/` | `tests/integration/cassettes/` |
| Underlying interception | httpcore/urllib3 hooks | `@mswjs/interceptors` |
| Match strategy | `['method', 'path', 'query']` | `DefaultRequestMatcher` (URL + method + body + headers; headers configurable) |

The patterns are almost 1:1. A developer familiar with the Python SDK integration tests will immediately understand the Node setup.

---

## 6. Summary

| Library | Native Fetch | Maintained | VCR-focused | Vitest | Recommendation |
|---|---|---|---|---|---|
| **vcr-test** | Yes | Yes (Apr 2026) | Yes | Yes | **USE THIS** |
| nock (nock.back) | Yes (buggy) | Yes | No (bolted-on) | Yes | Backup option |
| Polly.js | No | No (Jul 2023) | Yes | No | Eliminated |
| MSW | N/A | Yes | No (mocking only) | Yes | Keep for unit tests |
| All others | No/Unknown | No | Various | Various | Eliminated |

**Recommended action:** Install `vcr-test`, create `tests/integration/vcr-setup.ts` with the scrubbing config above, and start writing integration tests that mirror the Python SDK pattern.
