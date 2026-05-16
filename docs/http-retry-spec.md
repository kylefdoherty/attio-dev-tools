# HTTP Retry and Rate-Limit Behavior Spec

This document is the canonical specification for retry, rate-limit, and timeout
behavior across all Attio SDK implementations (Python, Node/TypeScript, and any
future SDKs). Both SDK implementations MUST conform to this spec. When in doubt,
this document wins.

## 1. Configuration Defaults

| Parameter     | Default | Unit         | Description                        |
|---------------|---------|--------------|------------------------------------|
| `max_retries` | 3       | count        | Maximum number of retry attempts   |
| `retry_delay` | 1.0     | seconds      | Base delay for exponential backoff |
| `timeout`     | 30.0    | seconds      | Per-request timeout                |

All three values are user-configurable at client construction time.

`max_retries = 0` means the request is attempted exactly once with no retries.

## 2. Retryable Conditions

A request is retried when **all** of the following hold:

1. The condition is retryable (see table below), AND
2. `attempt < max_retries` (i.e., retries remain).

| Condition              | Retryable? | Notes                                           |
|------------------------|------------|-------------------------------------------------|
| HTTP 429               | Yes        | Rate limit; uses Retry-After header for delay   |
| HTTP 5xx (500-599)     | Yes        | Server error; uses exponential backoff           |
| Network/connection err | Yes        | DNS failure, connection refused, reset, etc.     |
| HTTP 4xx (not 429)     | No         | Client errors are never retried                  |
| Timeout                | No         | Raised immediately; no retry                     |

## 3. Backoff Strategy

### 3.1 Rate Limit (429)

```
delay = parse_retry_after(response.headers["retry-after"])
        ?? retry_delay          // fallback when header is absent
```

- The `Retry-After` header value is parsed as a **float** (seconds).
- If the header is missing or unparseable, fall back to the configured
  `retry_delay` value.
- There is no exponential increase for 429 -- the server tells us when to
  retry.

### 3.2 Server Error (5xx)

```
delay = retry_delay * (2 ** attempt)
```

- `attempt` is zero-indexed: first request is attempt 0, first retry is
  attempt 1, etc.
- Delays for default config: 1s, 2s, 4s.

### 3.3 Network/Connection Error

```
delay = retry_delay * (2 ** attempt)
```

Same formula as 5xx.

## 4. Timeout Behavior

- Each individual request has a timeout of `timeout` seconds.
- A timeout raises immediately -- it is **not** retried.
- The error type is a timeout-specific error (e.g., `AttioTimeoutError`).

## 5. Retry Exhaustion

When all retries are exhausted:

| Condition         | Error raised                                        |
|-------------------|-----------------------------------------------------|
| HTTP 429          | `RateLimitError` with `retry_after` from last resp  |
| HTTP 5xx          | `AttioAPIError` (or language equivalent) with status |
| Network error     | `AttioConnectionError` (or equivalent)               |

## 6. Non-Retryable Errors (4xx)

These are raised immediately on the first attempt, with no retry:

| Status | Error type               |
|--------|--------------------------|
| 400    | `AttioValidationError`   |
| 401    | `AuthenticationError`    |
| 403    | `AttioPermissionError` / `ScopeError` |
| 404    | `NotFoundError` / `AttioError` |
| 409    | `ConflictError`          |

## 7. Request Flow (Pseudocode)

```
for attempt in 0..max_retries:
    try:
        response = execute_request(timeout=timeout)
    except TimeoutError:
        raise AttioTimeoutError(...)    # no retry
    except ConnectionError:
        if attempt < max_retries:
            sleep(retry_delay * 2**attempt)
            continue
        raise AttioConnectionError(...)

    if response.status == 429 and attempt < max_retries:
        delay = parse_retry_after(response) ?? retry_delay
        sleep(delay)
        continue

    if response.status >= 500 and attempt < max_retries:
        sleep(retry_delay * 2**attempt)
        continue

    # If we get here with a retryable status but no retries left,
    # or with a non-retryable status, raise the appropriate error.
    raise_for_status(response)
    return response.json()
```

## 8. Test Scenarios

Every SDK implementation MUST pass these scenarios:

1. **retry_on_429_then_success** -- First request returns 429 with
   `Retry-After: 0`, second returns 200. Verify 2 attempts and success.

2. **retry_on_5xx_then_success** -- First request returns 500, second
   returns 200. Verify 2 attempts and success.

3. **retry_on_network_error_then_success** -- First request raises a
   connection error, second returns 200. Verify 2 attempts and success.

4. **429_exhaustion_raises_rate_limit_error** -- All attempts return 429.
   Verify `RateLimitError` is raised.

5. **5xx_exhaustion_raises_api_error** -- All attempts return 502. Verify
   an API error with status 502 is raised.

6. **network_error_exhaustion** -- All attempts raise connection errors.
   Verify a connection error is raised.

7. **4xx_no_retry** -- Request returns 400. Verify exactly 1 attempt and a
   validation error is raised.

8. **timeout_no_retry** -- Request times out. Verify exactly 1 attempt
   (no retry) and a timeout error is raised.

9. **retry_after_header_respected** -- 429 with `Retry-After: <value>`.
   Verify the delay uses the header value, not the default backoff.

10. **5xx_uses_exponential_backoff** -- Verify delays follow
    `retry_delay * 2^attempt`.
