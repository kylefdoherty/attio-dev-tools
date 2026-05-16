/**
 * Integration tests for Objects resource using real API responses.
 */

import { describe, expect, it } from 'vitest';
import { client } from './setup.js';
import { withCassette } from './vcr.js';

describe('objects (integration)', () => {
  it('lists all objects in the workspace', async () => {
    await withCassette('objects_list', async () => {
      const result = await client().objects.list();

      expect(result.data).toBeDefined();
      expect(result.data.length).toBeGreaterThan(0);

      const obj = result.data[0];
      expect(obj.id).toBeDefined();
      expect(obj.id.workspace_id).toEqual(expect.any(String));
      expect(obj.id.object_id).toEqual(expect.any(String));
      expect(obj.api_slug).toEqual(expect.any(String));
      expect(obj.created_at).toEqual(expect.any(String));

      // Verify standard objects exist
      const slugs = result.data.map((o) => o.api_slug);
      expect(slugs).toContain('people');
      expect(slugs).toContain('companies');
    });
  });

  it('gets the people object by slug', async () => {
    await withCassette('objects_get_people', async () => {
      const result = await client().objects.get('people');

      expect(result.data).toBeDefined();
      expect(result.data.api_slug).toBe('people');
      expect(result.data.id.workspace_id).toEqual(expect.any(String));
      expect(result.data.id.object_id).toEqual(expect.any(String));
      expect(result.data.singular_noun).toEqual(expect.any(String));
      expect(result.data.plural_noun).toEqual(expect.any(String));
      expect(result.data.created_at).toEqual(expect.any(String));
    });
  });

  it('gets the companies object by slug', async () => {
    await withCassette('objects_get_companies', async () => {
      const result = await client().objects.get('companies');

      expect(result.data).toBeDefined();
      expect(result.data.api_slug).toBe('companies');
      expect(result.data.id.workspace_id).toEqual(expect.any(String));
      expect(result.data.id.object_id).toEqual(expect.any(String));
      expect(result.data.created_at).toEqual(expect.any(String));
    });
  });
});
