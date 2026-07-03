/**
 * Token-bucket rate limiter with optional concurrency cap, for self-throttled
 * bulk write loops against the Attio REST API.
 *
 * Attio has NO bulk endpoints — bulk work is a loop of single requests, and
 * the API enforces 100 reads/s and 25 writes/s. Loops must self-throttle
 * below those limits or spend their 30s server-function budget in 429
 * retries.
 *
 * No background timers: tokens are refilled lazily from elapsed time on each
 * acquire, so an idle limiter holds no resources (important in the Attio
 * sandbox).
 */

export interface RateLimiterOptions {
  /** Sustained rate. For Attio writes stay under 25; 20 is a safe default for loops. */
  requestsPerSecond: number;
  /** Bucket capacity (max burst before throttling kicks in). Default: requestsPerSecond. */
  burst?: number;
  /** Max tasks running at once via `run()`. Default: unlimited. */
  maxConcurrent?: number;
  /** Injectable clock/sleep for deterministic tests. */
  now?: () => number;
  sleep?: (ms: number) => Promise<void>;
}

export interface RateLimiter {
  /** Wait until a token is available, then run `fn` (respecting maxConcurrent). */
  run<T>(fn: () => T | Promise<T>): Promise<T>;
  /** Wait for a token without running anything (manual throttling). */
  acquire(): Promise<void>;
}

function defaultSleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Create a token-bucket rate limiter.
 *
 * ```ts
 * const limiter = createRateLimiter({ requestsPerSecond: 20 });
 * await Promise.all(rows.map((row) => limiter.run(() => api.post(...))));
 * ```
 */
export function createRateLimiter(options: RateLimiterOptions): RateLimiter {
  const rate = options.requestsPerSecond;
  if (!Number.isFinite(rate) || rate <= 0) {
    throw new RangeError(`requestsPerSecond must be a positive number, got ${rate}`);
  }
  const capacity = options.burst ?? rate;
  if (!Number.isFinite(capacity) || capacity < 1) {
    throw new RangeError(`burst must be >= 1, got ${capacity}`);
  }
  const maxConcurrent = options.maxConcurrent ?? Number.POSITIVE_INFINITY;
  if (maxConcurrent < 1) {
    throw new RangeError(`maxConcurrent must be >= 1, got ${maxConcurrent}`);
  }
  const now = options.now ?? Date.now;
  const sleep = options.sleep ?? defaultSleep;

  let tokens = capacity;
  let lastRefill = now();
  // FIFO queue: each acquire waits for the previous one, so callers get
  // tokens in the order they asked.
  let tail: Promise<void> = Promise.resolve();

  function refill(): void {
    const t = now();
    tokens = Math.min(capacity, tokens + ((t - lastRefill) * rate) / 1000);
    lastRefill = t;
  }

  async function acquireInner(): Promise<void> {
    refill();
    while (tokens < 1) {
      const deficit = 1 - tokens;
      const waitMs = Math.max(1, Math.ceil((deficit * 1000) / rate));
      await sleep(waitMs);
      refill();
    }
    tokens -= 1;
  }

  function acquire(): Promise<void> {
    const turn = tail.then(acquireInner);
    // Keep the chain alive even if a caller's turn rejects (it shouldn't).
    tail = turn.catch(() => {});
    return turn;
  }

  // Counting semaphore for maxConcurrent. On release the slot is handed
  // directly to the next waiter (running stays counted), so the cap can
  // never be exceeded by a racing new caller.
  let running = 0;
  const waiters: Array<() => void> = [];

  function acquireSlot(): Promise<void> {
    if (running < maxConcurrent) {
      running++;
      return Promise.resolve();
    }
    return new Promise<void>((resolve) => waiters.push(resolve));
  }

  function releaseSlot(): void {
    const next = waiters.shift();
    if (next) {
      next(); // slot transfers to the waiter; `running` unchanged
    } else {
      running--;
    }
  }

  async function withConcurrency<T>(fn: () => T | Promise<T>): Promise<T> {
    await acquireSlot();
    try {
      return await fn();
    } finally {
      releaseSlot();
    }
  }

  return {
    acquire,
    async run<T>(fn: () => T | Promise<T>): Promise<T> {
      await acquire();
      return withConcurrency(fn);
    },
  };
}
