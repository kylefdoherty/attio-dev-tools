/**
 * Integration tests for Records resource using real API responses.
 */

import { describe, expect, it } from 'vitest';
import { client } from './setup.js';
import { withCassette } from './vcr.js';

describe('records (integration)', () => {
  it('queries people records', async () => {
    await withCassette('records_query_people', async () => {
      const result = await client().records.query('people', { limit: 5 });

      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      if (result.data.length > 0) {
        const record = result.data[0];
        expect(record.id).toBeDefined();
        expect(record.id.record_id).toEqual(expect.any(String));
        expect(record.id.object_id).toEqual(expect.any(String));
        expect(record.id.workspace_id).toEqual(expect.any(String));
        expect(record.values).toBeDefined();
        expect(typeof record.values).toBe('object');
        expect(record.created_at).toEqual(expect.any(String));
        expect(record.web_url).toEqual(expect.stringContaining('https'));
      }
    });
  });

  it('queries company records', async () => {
    await withCassette('records_query_companies', async () => {
      const result = await client().records.query('companies', { limit: 5 });

      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      if (result.data.length > 0) {
        const record = result.data[0];
        expect(record.id.record_id).toEqual(expect.any(String));
        expect(record.id.object_id).toEqual(expect.any(String));
      }
    });
  });

  it('queries with a limit and respects it', async () => {
    await withCassette('records_query_with_limit', async () => {
      const result = await client().records.query('people', { limit: 2 });

      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);
      expect(result.data.length).toBeLessThanOrEqual(2);
    });
  });

  it('gets a single company record by ID', async () => {
    await withCassette('records_get_company', async () => {
      // Step 1: query to find a record (use companies since they have data)
      const queryResult = await client().records.query('companies', { limit: 1 });
      if (queryResult.data.length === 0) {
        console.warn('No company records -- skipping get test');
        return;
      }
      const recordId = queryResult.data[0].id.record_id;

      // Step 2: fetch the individual record
      const result = await client().records.get('companies', recordId);
      expect(result.data).toBeDefined();
      expect(result.data.id.record_id).toBe(recordId);
      expect(result.data.id.object_id).toEqual(expect.any(String));
      expect(result.data.id.workspace_id).toEqual(expect.any(String));
      expect(result.data.values).toBeDefined();
      expect(typeof result.data.values).toBe('object');
      expect(result.data.created_at).toEqual(expect.any(String));
      expect(result.data.web_url).toEqual(expect.stringContaining('https'));
    });
  });

  it('gets attribute values for a company record', async () => {
    await withCassette('records_get_attribute_values', async () => {
      // Step 1: query a company
      const queryResult = await client().records.query('companies', { limit: 1 });
      if (queryResult.data.length === 0) {
        console.warn('No company records -- skipping attribute values test');
        return;
      }
      const recordId = queryResult.data[0].id.record_id;

      // Step 2: get the name attribute values
      const result = await client().records.getAttributeValues('companies', recordId, 'name');
      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      if (result.data.length > 0) {
        const val = result.data[0];
        expect(val.active_from).toEqual(expect.any(String));
        expect(val.attribute_type).toEqual(expect.any(String));
      }
    });
  });

  it('lists entries for a company record', async () => {
    await withCassette('records_list_entries', async () => {
      // Step 1: query a company
      const queryResult = await client().records.query('companies', { limit: 1 });
      if (queryResult.data.length === 0) {
        console.warn('No company records -- skipping list entries test');
        return;
      }
      const recordId = queryResult.data[0].id.record_id;

      // Step 2: list entries (list memberships)
      const result = await client().records.listEntries('companies', recordId);
      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);
    });
  });

  it('performs global search', async () => {
    await withCassette('records_global_search', async () => {
      try {
        const result = await client().records.globalSearch({
          query: 'test',
          limit: 5,
        });

        expect(result.data).toBeDefined();
        expect(Array.isArray(result.data)).toBe(true);

        if (result.data.length > 0) {
          const item = result.data[0];
          expect(item.record_text).toEqual(expect.any(String));
          expect(item.object_slug).toEqual(expect.any(String));
        }
      } catch (err: unknown) {
        // Known issue: global_search endpoint may return 400
        const error = err as { status?: number };
        if (error.status === 400) {
          console.warn('global search returned 400 -- known API issue');
        } else {
          throw err;
        }
      }
    });
  });
});
