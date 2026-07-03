import { describe, expect, it } from 'vitest';
import { createRateLimiter } from '../src/rate-limit.js';

/**
 * Virtual clock where sleep() advances time deterministically. Because the
 * limiter serializes acquires through a FIFO chain, sequential time
 * advancement models real timer behavior for these tests.
 */
function virtualClock() {
  let time = 0;
  return {
    now: () => time,
    sleep: async (ms: number) => {
      time += ms;
    },
    get time() {
      return time;
    },
  };
}

describe('createRateLimiter — token bucket', () => {
  it('allows an initial burst without waiting', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 10, ...clock });
    for (let i = 0; i < 10; i++) await limiter.acquire();
    expect(clock.time).toBe(0); // full bucket => no sleeping
  });

  it('throttles beyond the burst at the sustained rate', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 10, burst: 1, ...clock });
    // 11 acquires at 10/s with burst 1: first free, then 100ms each
    for (let i = 0; i < 11; i++) await limiter.acquire();
    expect(clock.time).toBeGreaterThanOrEqual(1000);
    expect(clock.time).toBeLessThan(1100);
  });

  it('keeps a bulk loop under 25 writes/s (the Attio write limit)', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 20, burst: 5, ...clock });
    const timestamps: number[] = [];
    for (let i = 0; i < 60; i++) {
      await limiter.acquire();
      timestamps.push(clock.now());
    }
    // In any sliding 1000ms window, at most burst + rate = 25 acquisitions
    for (let i = 0; i < timestamps.length; i++) {
      const windowEnd = timestamps[i] + 1000;
      const inWindow = timestamps.filter((t) => t >= timestamps[i] && t < windowEnd).length;
      expect(inWindow).toBeLessThanOrEqual(25);
    }
    // 60 acquires at 20/s with burst 5 needs ~(60-5)/20 = 2.75s
    expect(clock.time).toBeGreaterThanOrEqual(2700);
  });

  it('refills the bucket during idle time', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 10, burst: 2, ...clock });
    await limiter.acquire();
    await limiter.acquire();
    await clock.sleep(1000); // idle: refills to capacity (2)
    const before = clock.time;
    await limiter.acquire();
    await limiter.acquire();
    expect(clock.time).toBe(before); // both free
  });

  it('never exceeds burst capacity after long idle', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 10, burst: 2, ...clock });
    await clock.sleep(60_000);
    await limiter.acquire();
    await limiter.acquire();
    const before = clock.time;
    await limiter.acquire(); // third must wait ~100ms
    expect(clock.time).toBeGreaterThan(before);
  });

  it('run() returns the function result and propagates errors', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 100, ...clock });
    expect(await limiter.run(() => 42)).toBe(42);
    expect(await limiter.run(async () => 'async')).toBe('async');
    await expect(limiter.run(() => Promise.reject(new Error('boom')))).rejects.toThrow('boom');
  });

  it('a rejected task does not wedge the limiter', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 100, ...clock });
    await expect(limiter.run(() => Promise.reject(new Error('boom')))).rejects.toThrow('boom');
    expect(await limiter.run(() => 'still works')).toBe('still works');
  });

  it('serves parallel callers FIFO under throttling', async () => {
    const clock = virtualClock();
    const limiter = createRateLimiter({ requestsPerSecond: 10, burst: 1, ...clock });
    const order: number[] = [];
    await Promise.all(
      [0, 1, 2, 3, 4].map((i) => limiter.run(() => order.push(i))),
    );
    expect(order).toEqual([0, 1, 2, 3, 4]);
  });

  it('enforces maxConcurrent', async () => {
    // Rate high enough that only the concurrency cap throttles (no sleeps).
    const limiter = createRateLimiter({
      requestsPerSecond: 1000,
      burst: 1000,
      maxConcurrent: 2,
    });
    const flush = async () => {
      for (let i = 0; i < 25; i++) await Promise.resolve();
    };
    let running = 0;
    let peak = 0;
    const gate: Array<() => void> = [];
    const tasks = Array.from({ length: 6 }, () =>
      limiter.run(async () => {
        running++;
        peak = Math.max(peak, running);
        await new Promise<void>((resolve) => gate.push(resolve));
        running--;
      }),
    );
    await flush();
    expect(running).toBe(2); // only 2 started; 4 queued
    for (let i = 0; i < 6; i++) {
      gate.shift()?.();
      await flush();
    }
    await Promise.all(tasks);
    expect(peak).toBe(2);
  });

  it('validates options', () => {
    expect(() => createRateLimiter({ requestsPerSecond: 0 })).toThrow(RangeError);
    expect(() => createRateLimiter({ requestsPerSecond: -5 })).toThrow(RangeError);
    expect(() => createRateLimiter({ requestsPerSecond: 10, burst: 0 })).toThrow(RangeError);
    expect(() => createRateLimiter({ requestsPerSecond: 10, maxConcurrent: 0 })).toThrow(
      RangeError,
    );
  });

  it('works with real timers for a tiny load (smoke test)', async () => {
    const limiter = createRateLimiter({ requestsPerSecond: 200, burst: 2 });
    const start = Date.now();
    const results = await Promise.all(
      Array.from({ length: 6 }, (_, i) => limiter.run(() => i)),
    );
    expect(results).toEqual([0, 1, 2, 3, 4, 5]);
    // 6 tasks, burst 2, 200/s => ~20ms minimum
    expect(Date.now() - start).toBeGreaterThanOrEqual(15);
  });
});
