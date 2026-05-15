# attio-python

Unofficial Python SDK for the [Attio](https://attio.com) CRM API.

**This project is not affiliated with, endorsed by, or associated with Attio.**

## Installation

```bash
pip install attio
```

Requires Python 3.10+.

## Quick Start

### Synchronous

```python
from attio import AttioClient

client = AttioClient(api_key="your_api_key")

# List all people
people = client.people.list()
for person in people.data:
    print(person.id)

# Create a company
company = client.companies.create(
    values={
        "name": [{"value": "Acme Corp"}],
        "domains": [{"domain": "acme.com"}],
    }
)

# Upsert a person by email
person = client.people.upsert(
    matching_attribute="email_addresses",
    values={
        "email_addresses": [{"email_address": "jane@acme.com"}],
        "name": [{"first_name": "Jane", "last_name": "Doe"}],
    },
)

client.close()
```

### Asynchronous

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

## Resources

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

### Convenience Wrappers

These pre-fill the object slug and delegate to `client.records`:

| Resource | Object Slug |
|---|---|
| `client.people` | `people` |
| `client.companies` | `companies` |
| `client.deals` | `deals` |
| `client.users` | `users` |
| `client.workspaces_` | `workspaces` |

## Error Handling

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

The SDK automatically retries on rate limits (429) and server errors (5xx) with exponential backoff.

## Pagination

### Manual Pagination

```python
result = client.records.query("people", limit=50, offset=0)
for record in result.data:
    print(record.id)
```

### Auto-Pagination

```python
# Iterate through all records automatically
for record in client.people.query_all(filter={"name": {"$contains": "Acme"}}):
    print(record.id)
```

Async auto-pagination:

```python
async for record in client.people.query_all():
    print(record.id)
```

## Webhook Signature Verification

```python
from attio import verify_webhook_signature

is_valid = verify_webhook_signature(
    raw_body=request.body,       # bytes
    signature=request.headers["X-Attio-Signature"],
    secret="your_webhook_secret",
)
if not is_valid:
    raise ValueError("Invalid webhook signature")
```

## Configuration

```python
client = AttioClient(
    api_key="your_api_key",
    base_url="https://api.attio.com/v2",  # default
    max_retries=3,                         # default
    retry_delay=1.0,                       # seconds, default
    timeout=30.0,                          # seconds, default
)
```

## API Documentation

For the full Attio API reference, see: https://developers.attio.com/reference

## License

MIT
