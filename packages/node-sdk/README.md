# attio-node

A typed TypeScript SDK for the [Attio](https://attio.com) CRM API. Zero runtime dependencies, automatic rate-limit retries, and full coverage of the REST API surface.

```bash
npm install attio-node    # or: yarn add attio-node
```

```typescript
import { AttioClient } from 'attio-node';

const client = new AttioClient({
  apiKey: process.env.ATTIO_API_KEY,
});

// List all companies
const { data: companies } = await client.records.list('companies');
```

Get your API key from **Attio Settings > Developers > API Keys** ([open settings](https://app.attio.com/settings/developers)).

---

## Why use this SDK

- **Typed end-to-end** -- every resource, parameter, and response has TypeScript interfaces
- **Automatic retries** -- rate limits (429) and network errors are retried with exponential backoff
- **Consistent API** -- all resources follow the same `client.resource.method()` pattern
- **Zero dependencies** -- uses built-in `fetch` (Node 18+), nothing else
- **AI-friendly** -- ships with `AGENTS.md` context so AI coding tools generate correct SDK calls

---

## Examples

### Query records with filters

```typescript
const { data: deals } = await client.records.query('deals', {
  filter: {
    stage: { status: { title: 'Closed Won' } },
  },
  sorts: [{ attribute: 'created_at', direction: 'desc' }],
  limit: 50,
});
```

### Upsert a contact (create or update by email)

```typescript
const { data: person } = await client.records.upsert('people', {
  data: {
    matching_attribute: 'email_addresses',
    values: {
      email_addresses: [{ email_address: 'jane@acme.com' }],
      name: [{ first_name: 'Jane', last_name: 'Smith' }],
    },
  },
});
```

### Search across all records

```typescript
const { data: results } = await client.records.globalSearch({
  query: 'Acme',
  objects: ['companies', 'people'],
  limit: 10,
});
```

### Create a note on a record

```typescript
await client.notes.create({
  data: {
    parent_object: 'companies',
    parent_record_id: recordId,
    title: 'Q3 follow-up',
    format: 'plaintext',
    content: 'Discussed renewal pricing. Follow up in two weeks.',
  },
});
```

### Verify a webhook signature

```typescript
import { verifyWebhookSignature, WebhookEventType } from 'attio-node';

app.post('/webhooks/attio', (req, res) => {
  const valid = verifyWebhookSignature(
    req.rawBody,
    req.headers['attio-signature'],
    process.env.ATTIO_WEBHOOK_SECRET,
  );

  if (!valid) return res.status(401).send('Invalid signature');

  const event = req.body;
  if (event.event_type === WebhookEventType.RECORD_CREATED) {
    // handle new record
  }

  res.sendStatus(200);
});
```

---

## Resources

Every method is available as `client.{resource}.{method}()`.

| Resource | Methods |
|----------|---------|
| `objects` | list, get, create, update |
| `attributes` | list, get, create, update |
| `records` | list, query, search, globalSearch, get, create, update, append, delete, upsert, getAttributeValues, listEntries |
| `lists` | list, get, create, update |
| `entries` | list, query, get, create, update, append, delete, upsert, getAttributeValues |
| `notes` | list, get, create, delete |
| `tasks` | list, get, create, update, delete |
| `webhooks` | list, get, create, update, delete |
| `workspaceMembers` | list, get |
| `selectOptions` | list, create, update, listStatuses, createStatus, updateStatus |
| `views` | list |
| `comments` | create, get, delete, getThread, listThreads |
| `files` | list, get, createFolder, download, delete |
| `meetings` | list, get |
| `callRecordings` | list, get |
| `transcripts` | get |
| `self` | get |

For detailed method signatures and parameters, see [AGENTS.md](./AGENTS.md).

---

## Key patterns

**Response shapes** -- list/query methods return `{ data: T[] }`. Get/create/update methods return `{ data: T }`. Delete methods return void.

**Record values are arrays** -- this is the most common mistake. Every attribute value must be wrapped in an array:

```typescript
// Correct
{ name: [{ value: 'Acme Corp' }], domains: [{ domain: 'acme.com' }] }

// Wrong -- will fail
{ name: 'Acme Corp' }
```

**Update vs append** -- `update` overwrites the field. `append` adds to multi-value fields (like tags or multiselect).

**Upsert** -- `upsert` matches on a unique attribute and creates or updates the record. Use this when you want "add or update" behavior.

**Views as filters** -- list views on an object, then pass `filter_view_id` to `query` to reuse saved view filters:

```typescript
const { data: views } = await client.views.list('objects', 'deals');
const closedView = views.find(v => v.title === 'Closed Won');

const { data: deals } = await client.records.query('deals', {
  filter_view_id: closedView.id.view_id,
});
```

---

## Error handling

```typescript
import { AttioError, RateLimitError, ScopeError } from 'attio-node';

try {
  await client.records.get('deals', 'invalid-id');
} catch (error) {
  if (error instanceof ScopeError) {
    // 403 -- API key is missing a required permission
  } else if (error instanceof RateLimitError) {
    // 429 -- only thrown after automatic retries are exhausted
    console.log(`Retry after ${error.retryAfter}s`);
  } else if (error instanceof AttioError) {
    // Any other API error
    console.log(error.status, error.message, error.body);
  }
}
```

Rate limiting is handled automatically. The SDK retries 429 responses up to 3 times with the server-specified `Retry-After` delay. You do not need to add your own retry logic.

---

## Configuration

```typescript
const client = new AttioClient({
  apiKey: 'sk_...',         // Required
  baseUrl: 'https://...',   // Default: https://api.attio.com/v2
  maxRetries: 3,            // Default: 3
  retryDelay: 1000,         // Default: 1000ms (base for exponential backoff)
  timeout: 30000,           // Default: 30000ms
});
```

---

## Escape hatch

For any endpoint not covered by a resource, use the HTTP client directly:

```typescript
const result = await client.http.request('GET', '/some/endpoint', {
  params: { key: 'value' },
  body: { data: '...' },
});
```

This uses the same authentication, retries, and error handling as the resource methods.

---

## Requirements

- Node.js 18+
- ESM (`"type": "module"` in your package.json, or use dynamic `import()`)

## License

MIT
