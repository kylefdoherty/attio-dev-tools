/**
 * Integration tests for Attributes resource using real API responses.
 */

import { describe, expect, it } from 'vitest';
import { client } from './setup.js';
import { withCassette } from './vcr.js';

describe('attributes (integration)', () => {
  it('lists attributes on the people object', async () => {
    await withCassette('attributes_list_people', async () => {
      const result = await client().attributes.list('objects', 'people');

      expect(result.data).toBeDefined();
      expect(result.data.length).toBeGreaterThan(0);

      const attr = result.data[0];
      expect(attr.id).toBeDefined();
      expect(attr.id.attribute_id).toEqual(expect.any(String));
      expect(attr.title).toEqual(expect.any(String));
      expect(attr.api_slug).toEqual(expect.any(String));
      expect(attr.type).toEqual(expect.any(String));
      expect(typeof attr.is_system_attribute).toBe('boolean');
      expect(typeof attr.is_required).toBe('boolean');
      expect(typeof attr.is_unique).toBe('boolean');
      expect(typeof attr.is_multiselect).toBe('boolean');
      expect(attr.created_at).toEqual(expect.any(String));
    });
  });

  it('lists attributes on the companies object', async () => {
    await withCassette('attributes_list_companies', async () => {
      const result = await client().attributes.list('objects', 'companies');

      expect(result.data).toBeDefined();
      expect(result.data.length).toBeGreaterThan(0);

      const attr = result.data[0];
      expect(attr.id.attribute_id).toEqual(expect.any(String));
      expect(attr.title).toEqual(expect.any(String));
      expect(attr.api_slug).toEqual(expect.any(String));
      expect(attr.type).toEqual(expect.any(String));
    });
  });

  it('gets the name attribute on people', async () => {
    await withCassette('attributes_get_people_name', async () => {
      const result = await client().attributes.get('objects', 'people', 'name');

      expect(result.data).toBeDefined();
      expect(result.data.api_slug).toBe('name');
      expect(result.data.id.attribute_id).toEqual(expect.any(String));
      expect(result.data.title).toEqual(expect.any(String));
      expect(result.data.type).toEqual(expect.any(String));
      expect(result.data.is_system_attribute).toBe(true);
      expect(result.data.created_at).toEqual(expect.any(String));
    });
  });
});
