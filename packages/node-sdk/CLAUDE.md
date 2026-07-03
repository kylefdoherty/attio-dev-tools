# attio-node SDK — Claude Code Context

> See [AGENTS.md](./AGENTS.md) for full SDK reference (resources, methods, patterns, examples).
> This file adds Claude Code-specific guidance.

## Quick Reference

```typescript
import { AttioClient } from 'attio-node';
const client = new AttioClient({ apiKey: process.env.ATTIO_API_KEY });
```

## Resources

- `client.objects` — list, get, create, update
- `client.attributes` — list, get, create, update
- `client.records` — list, listAll, query, queryAll, globalSearch (beta), get, create, update, append, delete, upsert, getAttributeValues, listEntries
- `client.lists` — list, get, create, update
- `client.entries` — list, listAll, query, queryAll, get, create, update, append, delete, upsert, getAttributeValues
- `client.notes` — list, get, create, delete
- `client.tasks` — list, get, create, update, delete
- `client.webhooks` — list, get, create, update, delete
- `client.workspaceMembers` — list, get
- `client.selectOptions` — list, create, update, listStatuses, createStatus, updateStatus
- `client.views` — list, listAll (on objects or lists)
- `client.comments` — create, get, delete, getThread, listThreads
- `client.files` (beta) — list, listAll, get, upload, createFolder, createConnected, download, delete
- `client.meetings` (beta) — list, listAll, get, create (alpha)
- `client.callRecordings` (beta) — list, listAll, get, create (alpha), delete (alpha)
- `client.transcripts` (beta) — get, segments
- `client.sql` (beta, Enterprise) — query
- `client.self` — get

## Key Patterns

- All list/query → `{ data: T[] }`. All get/create/update → `{ data: T }`. Delete → void.
- Record values are always arrays: `name: [{ value: 'Acme' }]`
- `upsert` = create or update by matching attribute
- `update` = overwrite, `append` = add to multi-value fields
- `client.http.request()` for any uncovered endpoint

## Error Types

- `AttioError` (base) — `status`, `code`, `body`
- `RateLimitError` — 429, `retryAfter` (auto-retried)
- `ScopeError` — 403, missing permission

## Source Structure

```
src/
  index.ts          — AttioClient class, re-exports
  client.ts         — HttpClient (auth, retry, rate limiting)
  errors.ts         — Error classes
  types.ts          — TypeScript interfaces
  resources/        — One file per API resource
```

## Build & Test

```bash
yarn build          # Compile to dist/
yarn dev            # Watch mode
yarn test           # Vitest
yarn check          # Biome lint
yarn check:fix      # Auto-fix
```

## Claude Code Guidelines

- When a user describes a CRM workflow in plain English, translate it into SDK calls using the resources above.
- Prefer `upsert` over create-then-update when the user says "add or update" / "upsert".
- Always wrap record values in arrays — this is the most common mistake.
- For filtering records, use `client.records.query()` with a `filter` object. `filter` and `filter_view_id` are mutually exclusive.
- The SDK handles rate limiting automatically — don't add manual retry logic.
- Cannot create `email-address` type attributes via API — use `text` type for custom email fields.
