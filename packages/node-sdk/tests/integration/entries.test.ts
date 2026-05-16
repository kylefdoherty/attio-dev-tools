/**
 * Integration tests for Entries resource using real API responses.
 */

import { describe, expect, it } from 'vitest';
import { client } from './setup.js';
import { withCassette } from './vcr.js';

describe('entries (integration)', () => {
  it('queries entries on a list', async () => {
    await withCassette('entries_query', async () => {
      // Step 1: discover a list
      const allLists = await client().lists.list();
      if (allLists.data.length === 0) {
        console.warn('No lists in workspace -- skipping entries query');
        return;
      }

      const slug = allLists.data[0].api_slug;

      // Step 2: query entries
      const result = await client().entries.query(slug, { limit: 5 });
      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      for (const entry of result.data) {
        expect(entry.id).toBeDefined();
        expect(entry.id.entry_id).toEqual(expect.any(String));
        expect(entry.parent_record_id).toEqual(expect.any(String));
        expect(entry.parent_object).toEqual(expect.any(String));
        expect(entry.created_at).toEqual(expect.any(String));
        // Critical: entries use entry_values, NOT values
        expect(entry.entry_values).toBeDefined();
        expect(typeof entry.entry_values).toBe('object');
      }
    });
  });

  it('gets a single entry by ID', async () => {
    await withCassette('entries_get', async () => {
      // Step 1: discover a list
      const allLists = await client().lists.list();
      if (allLists.data.length === 0) {
        console.warn('No lists in workspace -- skipping entry get');
        return;
      }

      const slug = allLists.data[0].api_slug;

      // Step 2: query to find an entry_id
      const queryResult = await client().entries.query(slug, { limit: 1 });
      if (queryResult.data.length === 0) {
        console.warn('No entries on list -- skipping entry get');
        return;
      }

      const entryId = queryResult.data[0].id.entry_id;

      // Step 3: fetch the individual entry
      const result = await client().entries.get(slug, entryId);
      expect(result.data).toBeDefined();
      expect(result.data.id.entry_id).toBe(entryId);
      expect(result.data.parent_record_id).toEqual(expect.any(String));
      expect(result.data.parent_object).toEqual(expect.any(String));
      expect(result.data.created_at).toEqual(expect.any(String));
      expect(result.data.entry_values).toBeDefined();
      expect(typeof result.data.entry_values).toBe('object');
    });
  });
});
