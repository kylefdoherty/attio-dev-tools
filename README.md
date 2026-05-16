# Attio Dev Tools

Unofficial developer toolkit for the [Attio](https://attio.com) CRM API -- a Python SDK, a Node/TypeScript SDK, and a CLI that covers the entire API surface.

**This project is not affiliated with, endorsed by, or associated with Attio.**

## Why this exists

Attio is a powerful CRM, but building on its API means dealing with a flexible data model, array-wrapped values, and a lot of endpoints. These tools handle that complexity so you can focus on what you're building:

- **Full API coverage** -- every Attio endpoint is mapped to a typed method or CLI command
- **Automatic retries** -- rate limits and transient errors are handled with exponential backoff
- **Type safety** -- Pydantic models in Python, TypeScript interfaces in Node, structured output in the CLI
- **Data model helpers** -- convenience wrappers for People, Companies, Deals, and other standard objects

---

## Packages

| Package | Install | What it is |
|---|---|---|
| **Python SDK** | `pip install attio` | Sync + async Python client with Pydantic models |
| **Node SDK** | `npm install attio-node` | Zero-dependency TypeScript client with full type coverage |
| **CLI** | `pip install attio-cli` | Command-line interface for humans and AI agents |

Python packages require Python 3.10+. Node SDK requires Node 18+.

---

## Quick Start: CLI

The CLI wraps the entire Attio API in a single `attio` command. Every SDK method has a corresponding CLI command, and all output supports `--json` for scripting.

```bash
# Authenticate
attio auth login

# Or via 1Password (no secret stored on disk)
attio auth login --1password "op://Personal/attio-cli/credential"

# List people
attio people list

# Create a person (simplified values -- no array-of-dicts needed)
attio people create --values '{"name": "Jane Doe", "email": "jane@acme.com"}'

# Search across all objects
attio search "Acme"

# Auto-paginate through all deals
attio deals list --all

# JSON output for scripting and AI agents
attio people list --json

# Raw API access (any endpoint, auth handled)
attio api GET /objects
attio api POST /objects/people/records/query --body '{"filter": {"name": {"$contains": "Jane"}}}'
```

The CLI supports 23 command groups. Run `attio --help` to see them all.

**Key features:**
- **Simplified values** -- `{"name": "Jane Doe"}` auto-expands to Attio's array-of-dicts format
- **`--json` everywhere** -- structured output for scripting, auto-enabled when piped
- **`--all` flag** -- auto-paginate through all results on any list command
- **`attio api` escape hatch** -- hit any endpoint with auth handled
- **Semantic exit codes** -- 0-8 mapping (auth, permission, not found, rate limit, etc.)
- **Agent-first** -- non-interactive by default, data to stdout, errors to stderr

---

## Quick Start: Python SDK

```python
from attio import AttioClient

client = AttioClient(api_key="your_api_key")

# List all people
people = client.people.list()
for person in people.data:
    print(person.id)

# Upsert a person by email
person = client.people.upsert(
    matching_attribute="email_addresses",
    values={
        "email_addresses": [{"email_address": "jane@acme.com"}],
        "name": [{"first_name": "Jane", "last_name": "Doe"}],
    },
)

# Search across all records
results = client.records.global_search(query="Acme", limit=10)

client.close()
```

### Async

```python
import asyncio
from attio import AsyncAttioClient

async def main():
    async with AsyncAttioClient(api_key="your_api_key") as client:
        people = await client.people.list()
        for person in people.data:
            print(person.id)

asyncio.run(main())
```

### Auto-Pagination

```python
# Sync
for person in client.people.query_all():
    print(person.values["name"][0].full_name)

# Async
async for person in client.people.query_all():
    print(person.values["name"][0].full_name)
```

### Error Handling

```python
from attio import AttioClient, NotFoundError, RateLimitError, AttioAPIError

client = AttioClient(api_key="your_api_key")

try:
    person = client.people.get("nonexistent-id")
except NotFoundError:
    print("Person not found")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except AttioAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

The Python SDK automatically retries on rate limits (429) and server errors (5xx) with exponential backoff.

### Configuration

```python
client = AttioClient(
    api_key="your_api_key",
    base_url="https://api.attio.com/v2",  # default
    max_retries=3,                         # default
    retry_delay=1.0,                       # seconds, default
    timeout=30.0,                          # seconds, default
)
```

### Webhook Signature Verification

```python
from attio import verify_webhook_signature

is_valid = verify_webhook_signature(
    raw_body=request.body,       # bytes
    signature=request.headers["X-Attio-Signature"],
    secret="your_webhook_secret",
)
```

---

## Quick Start: Node SDK

```typescript
import { AttioClient } from 'attio-node';

const client = new AttioClient({
  apiKey: process.env.ATTIO_API_KEY,
});

// List all companies
const { data: companies } = await client.records.list('companies');

// Upsert a contact by email
const { data: person } = await client.records.upsert('people', {
  data: {
    matching_attribute: 'email_addresses',
    values: {
      email_addresses: [{ email_address: 'jane@acme.com' }],
      name: [{ first_name: 'Jane', last_name: 'Smith' }],
    },
  },
});

// Query deals with filters
const { data: deals } = await client.records.query('deals', {
  filter: {
    stage: { status: { title: 'Closed Won' } },
  },
  sorts: [{ attribute: 'created_at', direction: 'desc' }],
  limit: 50,
});

// Search across all records
const { data: results } = await client.records.globalSearch({
  query: 'Acme',
  objects: ['companies', 'people'],
  limit: 10,
});
```

### Error Handling

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

### Webhook Signature Verification

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

### Configuration

```typescript
const client = new AttioClient({
  apiKey: 'sk_...',         // Required
  baseUrl: 'https://...',   // Default: https://api.attio.com/v2
  maxRetries: 3,            // Default: 3
  retryDelay: 1000,         // Default: 1000ms (base for exponential backoff)
  timeout: 30000,           // Default: 30000ms
});
```

For the full Node SDK documentation, see [packages/node-sdk/README.md](packages/node-sdk/README.md).

---

## Python SDK Resources

Both the Python SDK and CLI share the same resource structure:

| Resource | Methods |
|---|---|
| `client.objects` | list, get, create, update |
| `client.records` | list, query, get, create, update, append, delete, upsert, get_attribute_values, list_entries, global_search, query_all |
| `client.lists` | list, get, create, update |
| `client.entries` | list, query, get, create, update, append, delete, upsert, get_attribute_values, query_all |
| `client.attributes` | list, get, create, update |
| `client.select_options` | list, create, update |
| `client.statuses` | list, create, update |
| `client.notes` | list, get, create, delete |
| `client.tasks` | list, get, create, update, delete |
| `client.webhooks` | list, get, create, update, delete |
| `client.workspace_members` | list, get |
| `client.self_` | identify |
| `client.views` | list_for_object, list_for_list, list_all_for_object, list_all_for_list |
| `client.comments` | create, get, delete |
| `client.threads` | list, get |
| `client.files` | list, get, create_folder, upload, download, delete |
| `client.meetings` | list, get |
| `client.call_recordings` | list, get |
| `client.transcripts` | get |

**Convenience wrappers** (pre-fill the object slug and delegate to `client.records`):

| Resource | Object Slug |
|---|---|
| `client.people` | `people` |
| `client.companies` | `companies` |
| `client.deals` | `deals` |
| `client.users` | `users` |
| `client.workspaces_` | `workspaces` |

---

## Attio Data Model

If you are new to Attio, you should understand its data model before using these tools. The key things to know:

- **Objects** are entity types (People, Companies, Deals). Think database tables.
- **Records** are individual entities. Think rows.
- **Attributes** are fields on objects. Think columns.
- **Lists** model workflows (sales pipelines, hiring funnels). Records are added to lists as **entries**.
- **Values are always arrays** -- this is the #1 source of bugs. Even a single value like a job title must be wrapped in `[]`.

```python
# Correct
values = {"name": [{"first_name": "Jane", "last_name": "Doe"}]}

# Wrong -- will fail
values = {"name": {"first_name": "Jane"}}
```

For the full data model guide -- including all 17 attribute types, the difference between `values` and `entry_values`, status vs. select attributes, record references, and common recipes -- see **[docs/attio-data-model.md](docs/attio-data-model.md)**.

---

## API Documentation

For the full Attio API reference, see: https://developers.attio.com/reference

## License

MIT
