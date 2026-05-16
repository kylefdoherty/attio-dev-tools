/**
 * Integration tests for Lists resource using real API responses.
 */

import { describe, expect, it } from 'vitest';
import { client } from './setup.js';
import { withCassette } from './vcr.js';

describe('lists (integration)', () => {
  it('lists all lists in the workspace', async () => {
    await withCassette('lists_list', async () => {
      const result = await client().lists.list();

      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      if (result.data.length > 0) {
        const lst = result.data[0];
        expect(lst.id).toBeDefined();
        expect(lst.id.workspace_id).toEqual(expect.any(String));
        expect(lst.id.list_id).toEqual(expect.any(String));
        expect(lst.api_slug).toEqual(expect.any(String));
        expect(lst.name).toEqual(expect.any(String));
        // parent_object can be a string or an array of strings depending on API version
        expect(lst.parent_object).toBeDefined();
        expect(lst.created_at).toEqual(expect.any(String));
      }
    });
  });

  it('gets a single list by slug', async () => {
    await withCassette('lists_get', async () => {
      // Step 1: discover a list slug
      const allLists = await client().lists.list();
      if (allLists.data.length === 0) {
        console.warn('No lists in workspace -- skipping get test');
        return;
      }

      const slug = allLists.data[0].api_slug;

      // Step 2: fetch the individual list
      const result = await client().lists.get(slug);
      expect(result.data).toBeDefined();
      expect(result.data.api_slug).toBe(slug);
      expect(result.data.name).toEqual(expect.any(String));
      expect(result.data.id.list_id).toEqual(expect.any(String));
      expect(result.data.created_at).toEqual(expect.any(String));
    });
  });
});
