import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    include: ['tests/integration/**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/.claude/worktrees/**'],
    // No setupFiles — integration tests use VCR, not MSW
    testTimeout: 30_000,
  },
});
