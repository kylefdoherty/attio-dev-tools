# GitHub Copilot Instructions — attio-node SDK

> Full SDK reference is in [AGENTS.md](../AGENTS.md) at the project root.
> Read that file for complete resource/method signatures, code patterns, and examples.

## Essentials

```typescript
import { AttioClient } from 'attio-node';
const client = new AttioClient({ apiKey: process.env.ATTIO_API_KEY });
```

- All resources: `client.{resource}.{method}()`
- Response shapes: list/query → `{ data: T[] }`, get/create/update → `{ data: T }`, delete → void
- Record values are always arrays: `name: [{ value: 'Acme' }]`
- `upsert` = create or update by matching attribute
- Rate limiting is automatic — don't add manual retry logic
- Errors: `AttioError` (base), `RateLimitError` (429), `ScopeError` (403)

## Common Mistakes to Avoid

- Forgetting to wrap record values in arrays
- Using `update` when `upsert` is the right choice
- Adding manual rate limit handling (the SDK does this automatically)
- Trying to create `email-address` type attributes via API (use `text` type instead)
