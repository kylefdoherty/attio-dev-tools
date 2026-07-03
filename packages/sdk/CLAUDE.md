# attio-python SDK -- Claude Code Context

## Quick Reference

```python
from attio import AttioClient

client = AttioClient(api_key="your_api_key")
```

Async usage:

```python
from attio import AsyncAttioClient

async with AsyncAttioClient(api_key="your_api_key") as client:
    people = await client.people.list()
```

## Resources

- `client.objects` -- list, get, create, update
- `client.attributes` -- list, get, create, update (on objects or lists)
- `client.records` -- list, query, get, create, update, append, delete, upsert, get_attribute_values, list_entries, global_search, query_all
- `client.lists` -- list, get, create, update
- `client.entries` -- list, query, get, create, update, append, delete, upsert, get_attribute_values, query_all
- `client.notes` -- list, get, create, delete
- `client.tasks` -- list, get, create, update, delete
- `client.webhooks` -- list, get, create, update, delete
- `client.workspace_members` -- list, get
- `client.self_` -- identify
- `client.select_options` -- list, create, update (on objects or lists)
- `client.statuses` -- list, create, update (on objects or lists)
- `client.views` -- list_for_object, list_for_list, list_all_for_object, list_all_for_list
- `client.comments` -- create, get, delete
- `client.threads` -- list, get
- `client.files` -- list, get, create_folder, connect, upload, download, delete, list_all (beta)
- `client.meetings` -- list, get, create (alpha find-or-create), list_all (beta)
- `client.call_recordings` -- list, get, create (alpha, 1 req/s), delete (alpha), list_all (beta)
- `client.transcripts` -- get, get_all (beta)
- `client.sql` -- query (beta, Enterprise plan, read-only SELECT, 2 req/s)

### Convenience wrappers (delegate to records)

- `client.people` -- list, query, get, create, update, append, delete, upsert, get_attribute_values, list_entries, query_all
- `client.companies` -- same as people
- `client.deals` -- same as people
- `client.users` -- same as people
- `client.workspaces_` -- same as people

## Key Patterns

- All list/query endpoints return `ListResponse[T]` with `.data: list[T]`.
- Cursor-paginated endpoints return `PaginatedResponse[T]` with `.data` and `.pagination.next_cursor`.
- Single-item endpoints return the model directly (unwrapped from `{"data": T}`).
- Delete endpoints return `None`.
- Record/entry values use **arrays**: `{"name": [{"value": "Acme"}]}`.
- Entries use `entry_values` instead of `values`.
- `update` overwrites multiselect fields; `append` adds to them.
- `upsert` = create or update by matching attribute.
- Use `query_all()` for auto-paginated iteration (returns `OffsetIterator` / `AsyncOffsetIterator`).
- Cursor endpoints have `list_all()` / `get_all()` auto-paginators (returns `CursorIterator` / `AsyncCursorIterator`).
- `query`/`query_all` accept `filter` OR `filter_view_id` (mutually exclusive; `ValueError` if both).
- `records.global_search` posts to `/objects/records/search` (beta, eventually consistent) with a required `request_as` (defaults to `{"type": "workspace"}`).
- `files.download` returns the signed URL from the 302 redirect (`DownloadUrl.url`) -- it does not download file contents.
- `client.http.request()` for any endpoint not yet covered.

## Error Types

- `AttioError` (base) -- `message`, `status_code`, `code`, `body`
- `AttioAPIError` -- non-2xx responses
- `RateLimitError` -- 429, `retry_after` (auto-retried)
- `AuthenticationError` -- 401
- `AttioPermissionError` -- 403
- `NotFoundError` -- 404
- `ConflictError` -- 409
- `AttioValidationError` -- 400
- `AttioConnectionError` -- network failures
- `AttioTimeoutError` -- request timeouts

## Source Structure

```
packages/sdk/
  src/attio/
    __init__.py         -- Public API, re-exports
    _client.py          -- AttioClient, AsyncAttioClient
    _http.py            -- HttpTransport, AsyncHttpTransport (retry, rate limit)
    _config.py          -- ClientConfig, constants
    _exceptions.py      -- Error hierarchy
    _pagination.py      -- CursorIterator, OffsetIterator (sync + async)
    _types.py           -- JsonDict, PathParam aliases
    webhook_utils.py    -- verify_webhook_signature
    models/             -- Pydantic models (one file per resource)
    resources/          -- Resource classes (one file per resource, sync + async)
  tests/                -- pytest test suite
  pyproject.toml        -- Package config, deps, dev extras
```

## Build and Test

```bash
# Install (with dev dependencies)
pip install -e "packages/sdk[dev]"

# Run tests
cd packages/sdk && .venv/bin/python -m pytest tests/ -v

# Run tests with coverage
cd packages/sdk && .venv/bin/python -m pytest tests/ --cov=attio --cov-report=term-missing

# Lint
cd packages/sdk && .venv/bin/ruff check src/ tests/

# Type check
cd packages/sdk && .venv/bin/mypy src/attio/
```

## Claude Code Guidelines

- When a user describes a CRM workflow in plain English, translate it into SDK calls using the resources above.
- Prefer `upsert` over create-then-update when the user says "add or update" / "upsert".
- Always wrap record values in arrays -- this is the most common mistake.
- For filtering records, use `client.records.query()` with a `filter` object.
- The SDK handles rate limiting automatically -- do not add manual retry logic.
- Entries use `entry_values`, not `values`. This is a key difference from records.
- Cannot create `email-address` type attributes via API -- use `text` type for custom email fields.
