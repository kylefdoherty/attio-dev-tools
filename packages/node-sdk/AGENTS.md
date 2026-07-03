# attio-node SDK — AI Agent Context

> This file provides context for AI coding tools (Cursor, GitHub Copilot, Windsurf, Gemini CLI, and others).
> It helps you write correct code with the attio-node SDK.

## SDK Overview

`attio-node` is a TypeScript SDK for the Attio CRM REST API. Zero runtime dependencies, Node 18+.

## Installation & Setup

```bash
npm install attio-node
```

```typescript
import { AttioClient } from 'attio-node';

const client = new AttioClient({ apiKey: process.env.ATTIO_API_KEY });
```

The API key comes from Attio Settings → Developers → API Keys.

## Resources & Methods

All resources follow the pattern: `client.{resource}.{method}()`.

- `client.objects` — list, get, create, update
- `client.attributes` — list(objectSlug), get(objectSlug, attributeSlug), create(objectSlug, data), update(objectSlug, attributeSlug, data)
- `client.records` — list(objectSlug), listAll(objectSlug), query(objectSlug, filters?), queryAll(objectSlug, filters?), globalSearch(params) (beta), get(objectSlug, recordId), create(objectSlug, data), update(objectSlug, recordId, data), append(objectSlug, recordId, data), delete(objectSlug, recordId), upsert(objectSlug, data), getAttributeValues(objectSlug, recordId, attributeSlug), listEntries(objectSlug, recordId)
- `client.lists` — list, get, create, update
- `client.entries` — list(listId), query(listId, filters?), get(listId, entryId), create(listId, data), update(listId, entryId, data), append(listId, entryId, data), delete(listId, entryId), upsert(listId, data), getAttributeValues(listId, entryId, attributeSlug)
- `client.notes` — list(objectSlug, recordId), get(noteId), create(objectSlug, recordId, data), delete(noteId)
- `client.tasks` — list, get, create, update, delete
- `client.webhooks` — list, get, create, update, delete
- `client.workspaceMembers` — list, get
- `client.selectOptions` — list(objectSlug, attributeSlug), create(objectSlug, attributeSlug, data), update(objectSlug, attributeSlug, optionId, data), listStatuses(objectSlug, attributeSlug), createStatus(objectSlug, attributeSlug, data), updateStatus(objectSlug, attributeSlug, statusId, data)
- `client.views` — list(target, targetIdOrSlug, params?), listAll(target, targetIdOrSlug, params?) — list saved views on an object or list; use view_id as filter_view_id in queries
- `client.comments` — create(data), get(commentId), delete(commentId), getThread(threadId), listThreads(recordId)
- `client.files` (beta) — list(params?), listAll(params?), get(fileId), upload({file, object, record_id, filename?}), createFolder({object, record_id, name}), createConnected(params), download(fileId) → {url} (signed URL from 302), delete(fileId)
- `client.meetings` (beta) — list(params?), listAll(params?), get(meetingId), create(data) (alpha, find-or-create by external_ref)
- `client.callRecordings` (beta) — list(meetingId, params?), listAll(meetingId), get(meetingId, callRecordingId), create(meetingId, {data: {video_url}}) (alpha, 1 req/s), delete(meetingId, callRecordingId) (alpha)
- `client.transcripts` (beta) — get(meetingId, callRecordingId, {cursor?}), segments(meetingId, callRecordingId) — async-iterate transcript segments
- `client.sql` (beta, Enterprise) — query(sql) → {data: {rows}} — read-only SELECT over objects.<slug>/lists.<slug>
- `client.self` — get() — current token and workspace info

## Key Patterns

### Response shapes
- All list/query methods return `{ data: T[] }`
- All get/create/update methods return `{ data: T }`
- Delete methods return void

### Record values format
Record values are always wrapped in arrays:
```typescript
await client.records.create('companies', {
  data: {
    values: {
      name: [{ value: 'Acme Corp' }],
      domains: [{ domain: 'acme.com' }],
    },
  },
});
```

### Update vs Append
- `update` — overwrites the attribute value
- `append` — adds to multi-value attributes (like multiselect)

### Upsert
`upsert` matches on a unique attribute and creates or updates:
```typescript
await client.records.upsert('people', {
  data: {
    matching_attribute: 'email_addresses',
    values: {
      email_addresses: [{ email_address: 'jane@acme.com' }],
      name: [{ first_name: 'Jane', last_name: 'Smith' }],
    },
  },
});
```

### Querying with filters
```typescript
const { data: deals } = await client.records.query('deals', {
  filter: { stage: { status: { title: 'Closed Won' } } },
  sorts: [{ attribute: 'created_at', direction: 'desc' }],
  limit: 50,
});
```

`filter` and `filter_view_id` are mutually exclusive — the SDK throws a `TypeError` if both are provided.

### Auto-pagination
`queryAll`/`listAll` (offset-based) and `listAll`/`segments` on cursor-based resources (views, files, meetings, call recordings, transcripts) return `AsyncIterable`s:
```typescript
for await (const record of client.records.queryAll('people')) { /* ... */ }
const all = await collectAll(client.files.listAll({ object: 'deals' }));
```

### Low-level HTTP
For endpoints not covered by a resource:
```typescript
const result = await client.http.request('GET', '/some/endpoint', {
  params: { key: 'value' },
});
```

## Error Handling

```typescript
import { AttioError, RateLimitError, ScopeError } from 'attio-node';
```

- `AttioError` — base class with `status`, `code`, `body`
- `RateLimitError` — 429, has `retryAfter` (retries are automatic)
- `ScopeError` — 403, missing API permission scope

Rate limiting is handled automatically with exponential backoff (3 retries by default).

## Source Structure

```
src/
  index.ts          — AttioClient class, re-exports everything
  client.ts         — HttpClient with auth, retry, rate limiting
  errors.ts         — Error classes
  types.ts          — All TypeScript interfaces
  resources/        — One file per API resource
```

## Build & Test

```bash
npm run build          # Compile TypeScript to dist/
npm run dev            # Watch mode
npm run test           # Run tests (vitest)
npm run test:watch     # Watch mode tests
npm run test:coverage  # Coverage report
npm run check          # Lint with Biome
npm run check:fix      # Auto-fix lint issues
```

## Known Limitations

- Cannot create `email-address` type attributes via API — use `text` type instead for custom email fields
- The SDK targets ESM (`"type": "module"` in package.json)
