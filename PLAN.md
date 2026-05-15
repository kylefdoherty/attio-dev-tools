# Attio Python SDK -- Implementation Plan

> Generated 2026-05-15. This is the build roadmap for the `attio` Python SDK monorepo.

---

## Preamble: Critical Design Decisions (Locked Before Coding)

Before any code is written, these decisions are finalized. They affect every phase.

### 1. Sync/Async Code Sharing Strategy

The SDK provides `AttioClient` (sync) and `AsyncAttioClient` (async) as separate classes. To avoid duplicating all resource logic:

- `_http.py` defines two transport classes: `HttpTransport` (wraps `httpx.Client`) and `AsyncHttpTransport` (wraps `httpx.AsyncClient`). Both expose the same method signatures (`request`, `request_multipart`) but one is sync and one is async.
- Each resource has a sync and async class. To avoid duplicating parameter-construction and response-parsing logic, use a **shared mixin pattern**: a private `_RecordsMixin` class (no `self._http` calls) that contains helper methods like `_build_query_params`, `_build_create_body`, `_parse_record_response`. The sync `RecordsResource` and async `AsyncRecordsResource` both inherit from the mixin and add the actual HTTP calls (one line per method that calls `self._http.request(...)` or `await self._http.request(...)`).
- This keeps each resource's logic in one file. The mixin holds 100% of the parameter/URL/body construction logic. The sync/async variants are thin wrappers that differ only in `await` vs direct call.

### 2. Pydantic Model Patterns

- Base class: `AttioModel(BaseModel)` with `model_config = ConfigDict(populate_by_name=True, extra="allow", frozen=False)`.
- All ID objects are nested models (e.g., `ObjectId`, `RecordId`, `EntryId`).
- Response wrapper models: `DataWrapper[T]` (for `{"data": T}`), `ListResponse[T]` (for `{"data": [T]}`), `PaginatedResponse[T]` (for `{"data": [T], "pagination": {...}}`).
- The transport layer deserializes JSON into the wrapper model, then resource methods unwrap: single-item methods return `T` directly, list methods return `ListResponse[T]` (preserving `.data` for iteration and pagination metadata).
- `extra="allow"` on all models for forward compatibility.

### 3. Monorepo Configuration

- Root `pyproject.toml` uses Hatch as build backend with `hatch-workspace` plugin for monorepo management.
- The SDK package lives at `packages/sdk/` and publishes as `attio` on PyPI.
- CLI package at `packages/cli/` is future work and not part of this plan.
- Python 3.10+ minimum (enables `X | Y` syntax, `match` statements).

### 4. Import Structure and Public API Surface

```python
# Primary imports (what users use)
from attio import AttioClient, AsyncAttioClient
from attio.models import Record, Object, List, Entry, Note, Task, ...
from attio.exceptions import AttioError, RateLimitError, NotFoundError, ...
from attio import verify_webhook_signature, WebhookEventType

# Internal (private) modules prefixed with underscore
attio._client, attio._http, attio._config, attio._exceptions, attio._pagination, attio._types
```

`__init__.py` re-exports only the public API surface. All internal modules use underscore prefix.

### 5. Resource Build Order

Start with the simplest and most foundational, building toward the most complex:

1. Objects (4 methods, simple CRUD, no nesting)
2. Lists (4 methods, simple CRUD)
3. Attributes (4 methods, nested paths with target/id)
4. Select Options (3 methods, deeply nested paths)
5. Statuses (3 methods, deeply nested paths)
6. Workspace Members (2 methods, read-only)
7. Self (1 method, read-only)
8. Views (2 methods, cursor pagination)
9. Notes (4 methods, query params filtering)
10. Tasks (5 methods, CRUD + query params)
11. Webhooks (5 methods, full CRUD)
12. Records (12 methods, most complex -- query, upsert, global search, attribute values, entries)
13. Entries (10 methods, mirrors records complexity)
14. Comments (3 methods)
15. Threads (2 methods)
16. Files (6 methods, includes multipart upload)
17. Meetings (2 methods, cursor pagination, many query params)
18. Call Recordings (2 methods, nested under meetings)
19. Transcripts (1 method, nested under meetings/recordings)
20. Standard Object Wrappers: People, Companies, Deals, Users, Workspaces (delegates to Records)

---

## Phase 0: Project Scaffolding

**Goal**: Set up the monorepo structure, build system, linting, and CI configuration so all subsequent phases have a working development environment.

**Dependencies**: None (this is the root phase).

**Files to create**:

- `attio-python/pyproject.toml` -- Root workspace config for Hatch. Defines workspace members (`packages/sdk`). Contains shared dev dependencies (ruff, mypy). Configures ruff settings (line-length=120, target Python 3.10, isort rules). Configures mypy settings (strict mode, pydantic plugin).

- `attio-python/packages/sdk/pyproject.toml` -- SDK package config. Name: `attio`. Version: `0.1.0`. Requires-python: `>=3.10`. Dependencies: `httpx>=0.27,<1.0` and `pydantic>=2.0,<3.0`. Optional dependencies group `[dev]`: pytest, pytest-asyncio, respx, pytest-cov, vcrpy, ruff, mypy. Build backend: hatchling. Entry points: none. Classifiers: standard PyPI classifiers.

- `attio-python/packages/sdk/src/attio/__init__.py` -- Empty initially, will be populated in Phase 1.

- `attio-python/packages/sdk/src/attio/py.typed` -- Empty marker file for PEP 561 typed package.

- `attio-python/packages/sdk/tests/__init__.py` -- Empty.

- `attio-python/packages/sdk/tests/conftest.py` -- Skeleton with minimal fixture setup. Will be fleshed out in Phase 1.

- `attio-python/.gitignore` -- Standard Python gitignore (dist, __pycache__, .venv, *.egg-info, .coverage, .mypy_cache, .ruff_cache, tests/fixtures/cassettes/).

- `attio-python/CLAUDE.md` -- Development instructions for Claude Code, modeled after the attio-node CLAUDE.md.

- `attio-python/README.md` -- Minimal readme with project description, installation, and quick start placeholder.

- `attio-python/.github/workflows/ci.yml` -- GitHub Actions CI: matrix test on Python 3.10/3.11/3.12/3.13, run ruff check, mypy, pytest with coverage.

**Acceptance criteria**:
- [ ] `hatch env create` succeeds in the root.
- [ ] `hatch run pytest --co` in `packages/sdk` shows test collection works (even if zero tests).
- [ ] `ruff check packages/sdk/src/attio/` passes with no errors.
- [ ] `mypy packages/sdk/src/attio/` passes with no errors.
- [ ] Package structure matches the tree from RESEARCH.md section 2.1.

**Estimated complexity**: Low. Mostly config files and empty scaffolding.

---

## Phase 1: Core Infrastructure (Client, HTTP Transport, Exceptions, Config)

**Goal**: Build the foundational layer that every resource depends on. After this phase, you can make authenticated HTTP requests to the Attio API with retry logic, rate limiting, and proper error handling.

**Dependencies**: Phase 0.

**Files to create**:

### 1a. `packages/sdk/src/attio/_config.py`

Contains constants and configuration:
```python
DEFAULT_BASE_URL = "https://api.attio.com/v2"
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds
DEFAULT_TIMEOUT = 30.0  # seconds
API_VERSION = "v2"
USER_AGENT = "attio-python/{version}"
```

Also a `ClientConfig` dataclass or Pydantic model holding `api_key`, `base_url`, `max_retries`, `retry_delay`, `timeout`. Used internally by the transport.

### 1b. `packages/sdk/src/attio/_exceptions.py`

Full error hierarchy as specified in RESEARCH.md section 2.5:
- `AttioError(Exception)` -- base, with `message`, `status_code`, `code`, `body` attributes.
- `AttioAPIError(AttioError)` -- non-2xx responses.
- `RateLimitError(AttioAPIError)` -- 429, with `retry_after: float`.
- `AuthenticationError(AttioAPIError)` -- 401.
- `AttioPermissionError(AttioAPIError)` -- 403 (named to avoid shadowing built-in).
- `NotFoundError(AttioAPIError)` -- 404.
- `ConflictError(AttioAPIError)` -- 409.
- `AttioValidationError(AttioAPIError)` -- 400 (named to avoid Pydantic clash).
- `AttioConnectionError(AttioError)` -- network failures.
- `AttioTimeoutError(AttioError)` -- timeout.

Also a `_raise_for_status(response: httpx.Response)` helper function that inspects status code and raises the appropriate exception. Parses JSON body to extract `message`, `code`, `type` fields.

### 1c. `packages/sdk/src/attio/_http.py`

Two transport classes:

**`HttpTransport`**:
- Constructor takes `ClientConfig`.
- Creates `httpx.Client` with `base_url`, `timeout`, `headers` (Authorization bearer, User-Agent, Content-Type: application/json).
- `request(method, path, *, params=None, json=None) -> dict` -- core method. Implements retry loop: for 429, reads `Retry-After` and sleeps; for 5xx and network errors, exponential backoff; for timeout, raises immediately. After exhausting retries, raises appropriate exception. On success, returns `response.json()`.
- `request_multipart(method, path, *, data=None, files=None, params=None) -> dict` -- for file upload. Same retry logic but sends multipart instead of JSON.
- `close()` -- closes the httpx client.
- `__enter__` / `__exit__` -- context manager support.

**`AsyncHttpTransport`**:
- Identical interface but uses `httpx.AsyncClient` and `async def` methods.
- `async def request(...)`, `async def request_multipart(...)`, `async def close()`.
- `__aenter__` / `__aexit__` -- async context manager.

Both transports share the retry logic via a private helper function or base class. The key difference is just sync sleep vs async sleep (`time.sleep` vs `anyio.sleep` or `asyncio.sleep`).

### 1d. `packages/sdk/src/attio/_types.py`

Shared type aliases:
```python
from typing import Any, TypeAlias
JsonDict: TypeAlias = dict[str, Any]
PathParam: TypeAlias = str  # object slug or UUID
```

### 1e. `packages/sdk/src/attio/_client.py`

Two client classes:

**`AttioClient`**:
- Constructor: `def __init__(self, api_key: str, *, base_url: str = DEFAULT_BASE_URL, max_retries: int = 3, retry_delay: float = 1.0, timeout: float = 30.0)`.
- Creates `HttpTransport` from params.
- Resource properties (lazy-initialized via `@cached_property`): `self.objects`, `self.records`, etc. Each returns the corresponding sync resource class initialized with `self._http`.
- `close()` method, `__enter__` / `__exit__`.
- `http` property exposing the transport for custom requests.

**`AsyncAttioClient`**:
- Identical but uses `AsyncHttpTransport` and async resource classes.
- `async close()`, `__aenter__` / `__aexit__`.

Initially, only wire up a stub for `objects` resource (Phase 3 will add the first real resource). Leave other resource properties as placeholders that get filled in as phases complete.

### 1f. `packages/sdk/src/attio/__init__.py`

Public API exports:
```python
from attio._client import AttioClient, AsyncAttioClient
from attio._exceptions import (
    AttioError, AttioAPIError, RateLimitError, AuthenticationError,
    AttioPermissionError, NotFoundError, ConflictError, AttioValidationError,
    AttioConnectionError, AttioTimeoutError,
)
```

### Tests for Phase 1

- `tests/test_config.py` -- Tests that `ClientConfig` defaults are correct.
- `tests/test_exceptions.py` -- Tests each exception class can be instantiated and has correct attributes. Tests `_raise_for_status` maps status codes correctly.
- `tests/test_http.py` -- Using `respx`:
  - Auth header is present on requests.
  - Rate limit retry: mock 429 with Retry-After, then 200 -- verify two requests made.
  - Rate limit exhaustion: mock 429 for all retries -- verify `RateLimitError` raised.
  - Network error retry: mock connection error, then 200.
  - Timeout: mock timeout -- verify `AttioTimeoutError`.
  - 5xx retry: mock 500, then 200.
  - 4xx no retry: mock 400 -- verify single request, `AttioValidationError` raised.
  - 401 -> `AuthenticationError`.
  - 403 -> `AttioPermissionError`.
  - 404 -> `NotFoundError`.
  - 409 -> `ConflictError`.
  - Non-JSON error body handled gracefully.
- `tests/test_client.py` -- Tests that `AttioClient` and `AsyncAttioClient` can be instantiated, context manager works, `close()` works.
- `tests/conftest.py` -- Shared fixtures: `sync_client` fixture, `async_client` fixture, `base_url` fixture.

**Acceptance criteria**:
- [ ] `AttioClient(api_key="test")` instantiates without error.
- [ ] `AsyncAttioClient(api_key="test")` instantiates without error.
- [ ] All HTTP transport tests pass (retry, rate limit, error mapping).
- [ ] Context manager protocol works for both clients.
- [ ] `mypy` passes with strict mode.
- [ ] 100% coverage on `_exceptions.py`, `_config.py`, `_http.py`.

**Estimated complexity**: Medium-high. The retry/rate-limit logic is the most intricate part of the entire SDK.

---

## Phase 2: Pydantic Models -- Foundation and First Resources

**Goal**: Establish the Pydantic model patterns and build models for the simplest resources (Objects, Lists, Workspace Members, Self). These models validate the base model approach before scaling to complex resources.

**Dependencies**: Phase 1.

**Files to create**:

### 2a. `packages/sdk/src/attio/models/__init__.py`

Re-exports all public model classes.

### 2b. `packages/sdk/src/attio/models/_base.py`

```python
from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar

T = TypeVar("T")

class AttioModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        frozen=False,
    )

class DataWrapper(AttioModel, Generic[T]):
    """Wrapper for {"data": T} responses."""
    data: T

class ListResponse(AttioModel, Generic[T]):
    """Wrapper for {"data": [T]} responses."""
    data: list[T]

class Pagination(AttioModel):
    next_cursor: str | None = None

class PaginatedResponse(AttioModel, Generic[T]):
    """Wrapper for {"data": [T], "pagination": {...}} responses."""
    data: list[T]
    pagination: Pagination
```

### 2c. `packages/sdk/src/attio/models/common.py`

Shared models used across multiple resources:
```python
class ActorReference(AttioModel):
    id: str | None = None
    type: str  # "api-token" | "workspace-member" | "system" | "app"

class AttributeValue(AttioModel):
    active_from: datetime
    active_until: datetime | None = None
    created_by_actor: ActorReference
    attribute_type: str
    # Type-specific fields captured by extra="allow"
```

### 2d-2g. Resource models

- `models/objects.py` -- `ObjectId`, `Object`
- `models/lists.py` -- `ListId`, `List`
- `models/workspace_members.py` -- `WorkspaceMemberId`, `WorkspaceMember`
- `models/self_info.py` -- `SelfInfo`

### Tests for Phase 2

- `tests/test_models.py` -- For each model:
  - Can be constructed from a dict matching the API response shape.
  - `extra="allow"` works: adding unknown fields does not raise.
  - `model_dump()` round-trips correctly.
  - Missing optional fields default correctly.
  - `datetime` fields parse ISO 8601 strings.
  - `ListResponse[Object]` can be validated from `{"data": [...]}`

**Acceptance criteria**:
- [ ] All model classes instantiate from mock API response dicts.
- [ ] Forward compatibility: extra fields are silently accepted.
- [ ] `mypy` passes on all model files.
- [ ] Model tests have 100% coverage.

**Estimated complexity**: Low-medium.

---

## Phase 3: First Resource Implementation -- Objects (Sync + Async)

**Goal**: Implement the first complete resource end-to-end. Objects is chosen because it has only 4 methods (list, get, create, update) with simple paths and no nesting. This phase validates the entire resource pattern before scaling.

**Dependencies**: Phase 1, Phase 2.

**Files to create**:

### 3a. `packages/sdk/src/attio/resources/__init__.py`

Re-exports all resource classes.

### 3b. `packages/sdk/src/attio/resources/_base.py`

```python
class SyncResource:
    def __init__(self, http: HttpTransport) -> None:
        self._http = http

class AsyncResource:
    def __init__(self, http: AsyncHttpTransport) -> None:
        self._http = http
```

### 3c. `packages/sdk/src/attio/resources/objects.py`

Contains three classes:

**`_ObjectsMixin`** -- shared parameter/body construction logic.

**`ObjectsResource(SyncResource, _ObjectsMixin)`**:
- `def list(self) -> ListResponse[Object]`
- `def get(self, object: str) -> Object`
- `def create(self, *, api_slug: str, singular_noun: str, plural_noun: str) -> Object`
- `def update(self, object: str, *, singular_noun: str | None = None, plural_noun: str | None = None) -> Object`

**`AsyncObjectsResource(AsyncResource, _ObjectsMixin)`** -- same four methods but `async def`.

### 3d. Wire up in `_client.py`

### 3e. Mock data factory

`tests/fixtures/__init__.py` and `tests/fixtures/factory.py` with `MOCK_OBJECT`, `MOCK_OBJECTS_LIST`, etc.

### Tests for Phase 3

- `tests/resources/test_objects.py` -- all 4 methods sync + async, error cases (404, 403).

**Acceptance criteria**:
- [ ] `client.objects.list()` returns `ListResponse[Object]` with correct data.
- [ ] `client.objects.get("deals")` returns `Object`.
- [ ] `client.objects.create(...)` sends correct body and returns `Object`.
- [ ] `client.objects.update(...)` sends correct body and returns `Object`.
- [ ] Async variants all work identically.
- [ ] Error cases are tested.
- [ ] The sync/async mixin pattern works without code duplication.

**Estimated complexity**: Medium. This is the template for all other resources.

---

## Phase 4: Simple CRUD Resources (Lists, Workspace Members, Self, Views)

**Goal**: Implement four more simple resources using the patterns established in Phase 3.

**Dependencies**: Phase 3.

**Files**: `resources/lists.py`, `resources/workspace_members.py`, `resources/self_resource.py`, `resources/views.py`, `models/views.py`

**Key details**:
- Lists: 4 methods (list, get, create, update)
- Workspace Members: 2 methods (list, get) -- read-only
- Self: 1 method (`identify()`) -- client property is `client.self_`
- Views: 2 methods with cursor pagination (`list_for_object`, `list_for_list`)

**Acceptance criteria**:
- [ ] All four resources work correctly (sync + async).
- [ ] Views resource correctly handles cursor pagination query params.
- [ ] All tests pass with full coverage.

**Estimated complexity**: Low.

---

## Phase 5: Pagination Helpers

**Goal**: Build auto-pagination iterators for cursor-based and offset-based endpoints.

**Dependencies**: Phase 4 (Views provides the first cursor-based endpoint to test).

**File**: `packages/sdk/src/attio/_pagination.py`

**Classes**:
- `CursorIterator[T]` -- sync auto-paginator, implements `__iter__`
- `AsyncCursorIterator[T]` -- async auto-paginator, implements `__aiter__`
- `OffsetIterator[T]` -- sync, increments offset, stops when `len(data) < limit`
- `AsyncOffsetIterator[T]` -- async variant

Add `list_all()` methods to Views resource as the first auto-paginating method.

**Acceptance criteria**:
- [ ] `CursorIterator` correctly fetches all pages.
- [ ] `AsyncCursorIterator` correctly fetches all pages.
- [ ] `OffsetIterator` stops when partial page received.
- [ ] Empty results handled without error.

**Estimated complexity**: Medium.

---

## Phase 6: Nested Path Resources (Attributes, Select Options, Statuses)

**Goal**: Implement resources that use nested URL paths with target/id segments.

**Dependencies**: Phase 3.

**Files**: `models/attributes.py`, `models/select_options.py`, `resources/attributes.py`, `resources/select_options.py`, `resources/statuses.py`

**Key details**:
- Attributes: `list(target: Literal["objects", "lists"], target_id, ...)` -> GET `/{target}/{target_id}/attributes`
- Select Options: deeply nested paths `/{target}/{target_id}/attributes/{attr}/options`
- Statuses: same nesting pattern, different response shape

**Acceptance criteria**:
- [ ] `client.attributes.list("objects", "people")` hits `/objects/people/attributes`.
- [ ] `client.select_options.list("objects", "people", "status")` hits `/objects/people/attributes/status/options`.
- [ ] `Literal["objects", "lists"]` type constraint works.

**Estimated complexity**: Medium.

---

## Phase 7: Notes, Tasks, Webhooks (Medium-Complexity CRUD)

**Goal**: Implement resources with query parameter filtering and full CRUD.

**Dependencies**: Phase 3.

**Files**: `models/notes.py`, `models/tasks.py`, `models/webhooks.py`, `resources/notes.py`, `resources/tasks.py`, `resources/webhooks.py`, `webhook_utils.py`

**Key details**:
- Notes: query param filtering by parent_object/parent_record_id
- Tasks: filtering by is_completed, assignee; includes `completed_at` field (missing from Node SDK)
- Webhooks: full CRUD + `WebhookEventType` StrEnum (26 event types)
- `verify_webhook_signature()` public utility function

**Acceptance criteria**:
- [ ] Notes query param filtering works.
- [ ] Tasks list filtering works.
- [ ] Webhooks full CRUD cycle.
- [ ] `verify_webhook_signature` correctly validates and rejects.
- [ ] `WebhookEventType` enum has all 26 event types.

**Estimated complexity**: Medium.

---

## Phase 8: Records (Most Complex Resource)

**Goal**: Implement the Records resource -- the centerpiece of the SDK with 12 methods.

**Dependencies**: Phase 3, Phase 5 (pagination helpers for `query_all`).

**Files**: `models/records.py`, `resources/records.py`

**12 methods**:
1. `list(object, *, limit, offset)`
2. `query(object, *, filter, filter_view_id, sorts, limit, offset)`
3. `get(object, record_id)`
4. `create(object, *, values)`
5. `update(object, record_id, *, values)`
6. `append(object, record_id, *, values)`
7. `delete(object, record_id)`
8. `upsert(object, *, matching_attribute, values)`
9. `get_attribute_values(object, record_id, attribute, *, show_historic, limit, offset)`
10. `list_entries(object, record_id, *, limit, offset)`
11. `global_search(*, query, objects, limit)`
12. `query_all(object, *, filter, sorts, limit)` -- auto-paginating via `OffsetIterator`

**Acceptance criteria**:
- [ ] All 12 methods work correctly (sync + async).
- [ ] `values` dict is properly wrapped in `{"data": {"values": ...}}` envelope.
- [ ] Query with filter + sorts + limit + offset sends correct body.
- [ ] Global search works with the different URL pattern (`/objects/records/search`).
- [ ] `query_all` iterates across multiple pages.
- [ ] Delete returns None.

**Estimated complexity**: High.

---

## Phase 9: Entries (Second Most Complex Resource)

**Goal**: Implement list entries, which mirrors Records complexity.

**Dependencies**: Phase 8.

**Files**: `models/entries.py`, `resources/entries.py`

**10 methods** (mirrors Records minus global_search and list_entries, plus upsert).

**Important**: Response field is `entry_values`, not `values`. This is a fix over the Node SDK.

**Acceptance criteria**:
- [ ] All 10 methods work correctly.
- [ ] Response model uses `entry_values` field name.
- [ ] Create body includes `parent_record_id` and `parent_object`.

**Estimated complexity**: Medium (patterns established in Phase 8).

---

## Phase 10: Comments and Threads

**Goal**: Implement as separate resources (improvement over Node SDK).

**Dependencies**: Phase 3.

**Files**: `models/comments.py`, `models/threads.py`, `resources/comments.py`, `resources/threads.py`

**Key details**:
- Comments: `create(*, thread_id=None, record=None, entry=None, ...)` -- exactly one target must be provided, validated at call time
- Threads: `list(...)`, `get(thread_id)`

**Acceptance criteria**:
- [ ] All three comment creation variants work.
- [ ] Client-side validation prevents ambiguous create calls.

**Estimated complexity**: Low-medium.

---

## Phase 11: Files (Including Multipart Upload)

**Goal**: Implement Files resource with working multipart upload (fixes Node SDK's broken implementation).

**Dependencies**: Phase 1 (transport's `request_multipart`).

**Files**: `models/files.py`, `resources/files.py`

**6 methods**: `list`, `get`, `create_folder`, `upload`, `download`, `delete`

The `upload` method uses `self._http.request_multipart(...)` with `files={"file": (filename, file)}`.

**Acceptance criteria**:
- [ ] File upload actually works (unlike Node SDK).
- [ ] Multipart form data is sent correctly.
- [ ] Cursor pagination works for file listing.

**Estimated complexity**: Medium.

---

## Phase 12: Meetings, Call Recordings, Transcripts

**Goal**: Implement remaining read-only nested resources.

**Dependencies**: Phase 5 (cursor pagination).

**Files**: `models/meetings.py`, `models/call_recordings.py`, `models/transcripts.py`, `resources/meetings.py`, `resources/call_recordings.py`, `resources/transcripts.py`

**Key details**:
- Meetings: many query params (participants, timezone, date ranges)
- Call Recordings: nested under meetings
- Transcripts: deeply nested under meetings/recordings

**Acceptance criteria**:
- [ ] Meeting query params correctly encoded.
- [ ] Nested paths correct (`/meetings/{id}/call_recordings/{id}/transcript`).
- [ ] Cursor pagination works on all three.

**Estimated complexity**: Low-medium.

---

## Phase 13: Standard Object Convenience Wrappers

**Goal**: Implement `client.people`, `client.companies`, `client.deals`, `client.users`, `client.workspaces` as convenience wrappers that delegate to Records. New feature not in Node SDK.

**Dependencies**: Phase 8 (Records must be complete).

**Files**: `resources/_standard_object.py`, `resources/people.py`, `resources/companies.py`, `resources/deals.py`, `resources/users.py`, `resources/workspaces_resource.py`

**Pattern**: Base class `StandardObjectResource` with `_object_slug` set by subclass. All methods delegate to `self._records.<method>(self._object_slug, ...)`. Each concrete class is a one-liner:

```python
class PeopleResource(StandardObjectResource):
    _object_slug = "people"
```

**Acceptance criteria**:
- [ ] `client.people.create(values={...})` hits `/objects/people/records` with correct body.
- [ ] All standard object wrappers delegate correctly.
- [ ] No logic duplication.

**Estimated complexity**: Low.

---

## Phase 14: Final Public API, Exports, and Documentation

**Goal**: Polish the public API surface, ensure all exports are correct, finalize CLAUDE.md and README.

**Dependencies**: All previous phases.

**Work**:
- Final `__init__.py` with all exports and `__all__`
- `models/__init__.py` re-exports all model classes
- `resources/__init__.py` re-exports all resource classes
- Docstrings audit: every public method gets a one-line docstring
- `CLAUDE.md` -- complete development guide
- `README.md` -- full README with installation, quick start, examples, error handling, pagination, webhook verification

**Acceptance criteria**:
- [ ] `from attio import AttioClient, AsyncAttioClient` works.
- [ ] `from attio.models import Record` works.
- [ ] `from attio import verify_webhook_signature` works.
- [ ] `mypy` passes on the entire package.
- [ ] `ruff check` passes with no errors.

**Estimated complexity**: Low-medium.

---

## Phase 15: Integration Tests and CI Finalization

**Goal**: Add VCR.py cassette-based integration tests, finalize CI pipeline, achieve 95%+ coverage.

**Dependencies**: All previous phases.

**Work**:
- `tests/integration/` directory with VCR.py configuration
- Cassettes for high-priority resources (objects, records)
- Sensitive data scrubbed via VCR.py hooks
- All integration tests gated on `@pytest.mark.integration` + `ATTIO_API_KEY` env var
- CI runs unit tests on all PRs, integration tests only on main with secrets
- Coverage threshold check (fail if below 95%)

**Acceptance criteria**:
- [ ] VCR.py cassettes recorded and playback works.
- [ ] Sensitive data scrubbed from cassettes.
- [ ] CI runs cleanly on all Python versions (3.10-3.13).
- [ ] Coverage >= 95%.
- [ ] `mypy --strict` passes.
- [ ] `ruff check` and `ruff format --check` pass.

**Estimated complexity**: Medium.

---

## Phase Dependency Graph

```
Phase 0 (Scaffolding)
  │
Phase 1 (Core: HTTP, Exceptions, Config, Client)
  │
Phase 2 (Models: Base, Common, Objects, Lists, Members, Self)
  │
Phase 3 (First Resource: Objects) ─── establishes the pattern
  │
  ├──→ Phase 4 (Lists, Members, Self, Views)
  │      │
  │      └──→ Phase 5 (Pagination Helpers)
  │
  ├──→ Phase 6 (Attributes, Select Options, Statuses)
  │
  ├──→ Phase 7 (Notes, Tasks, Webhooks, Webhook Utils)
  │
  ├──→ Phase 8 (Records) ←── depends on Phase 5 for query_all
  │      │
  │      ├──→ Phase 9 (Entries)
  │      │
  │      └──→ Phase 13 (Standard Object Wrappers)
  │
  ├──→ Phase 10 (Comments, Threads)
  │
  ├──→ Phase 11 (Files)
  │
  └──→ Phase 12 (Meetings, Call Recordings, Transcripts)
  │
Phase 14 (Public API, Docs) ─── depends on ALL above
  │
Phase 15 (Integration Tests, CI) ─── depends on ALL above
```

Phases 4, 6, 7, 8, 10, 11, 12 can be built in parallel once Phase 3 is complete, with the caveat that Phase 8 needs Phase 5 for `query_all`, and Phases 9 and 13 need Phase 8.

---

## Complete File Inventory (~90 files)

### Root
- `pyproject.toml`
- `.gitignore`
- `CLAUDE.md`
- `README.md`
- `RESEARCH.md` (exists)
- `PLAN.md` (this file)
- `.github/workflows/ci.yml`

### SDK Source (`packages/sdk/src/attio/`)
- `__init__.py`, `py.typed`
- `_client.py`, `_http.py`, `_config.py`, `_exceptions.py`, `_types.py`, `_pagination.py`
- `webhook_utils.py`
- `models/__init__.py`, `models/_base.py`, `models/common.py`
- `models/objects.py`, `models/lists.py`, `models/attributes.py`, `models/select_options.py`
- `models/records.py`, `models/entries.py`, `models/notes.py`, `models/tasks.py`, `models/webhooks.py`
- `models/workspace_members.py`, `models/views.py`, `models/comments.py`, `models/threads.py`
- `models/files.py`, `models/meetings.py`, `models/call_recordings.py`, `models/transcripts.py`, `models/self_info.py`
- `resources/__init__.py`, `resources/_base.py`, `resources/_standard_object.py`
- `resources/objects.py`, `resources/lists.py`, `resources/attributes.py`, `resources/select_options.py`, `resources/statuses.py`
- `resources/records.py`, `resources/entries.py`, `resources/notes.py`, `resources/tasks.py`, `resources/webhooks.py`
- `resources/workspace_members.py`, `resources/views.py`, `resources/comments.py`, `resources/threads.py`
- `resources/files.py`, `resources/meetings.py`, `resources/call_recordings.py`, `resources/transcripts.py`
- `resources/self_resource.py`, `resources/people.py`, `resources/companies.py`, `resources/deals.py`, `resources/users.py`, `resources/workspaces_resource.py`

### Tests (`packages/sdk/tests/`)
- `__init__.py`, `conftest.py`
- `test_config.py`, `test_exceptions.py`, `test_http.py`, `test_client.py`, `test_pagination.py`, `test_webhook_utils.py`, `test_init.py`
- `fixtures/__init__.py`, `fixtures/factory.py`
- `resources/__init__.py`, `resources/test_objects.py`, `resources/test_lists.py`, `resources/test_attributes.py`
- `resources/test_select_options.py`, `resources/test_statuses.py`, `resources/test_records.py`, `resources/test_entries.py`
- `resources/test_notes.py`, `resources/test_tasks.py`, `resources/test_webhooks.py`, `resources/test_workspace_members.py`
- `resources/test_views.py`, `resources/test_comments.py`, `resources/test_threads.py`, `resources/test_files.py`
- `resources/test_meetings.py`, `resources/test_call_recordings.py`, `resources/test_transcripts.py`, `resources/test_self.py`
- `resources/test_people.py`, `resources/test_companies.py`, `resources/test_deals.py`
- `integration/__init__.py`, `integration/conftest.py`, `integration/test_objects_integration.py`, `integration/test_records_integration.py`
