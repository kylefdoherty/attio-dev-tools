import type { HttpClient } from '../client.js';
import type { SqlQueryResponse } from '../types.js';

export class SqlResource {
  constructor(private client: HttpClient) {}

  /**
   * Query records and lists with read-only SQL. (beta, Enterprise plan only)
   *
   * Tables are exposed as `objects.<slug>` and `lists.<slug>` (each list row
   * is an entry); `information_schema` and `pg_catalog` are also queryable.
   * Only SELECT statements are allowed. Rate limited to 2 queries per second
   * with a 30 second timeout. Emails and interactions are not yet exposed.
   *
   * @example
   * ```ts
   * const { data } = await client.sql.query(
   *   "SELECT name, domains FROM companies WHERE name ILIKE '%acme%'",
   * );
   * console.log(data.rows);
   * ```
   */
  async query(sql: string): Promise<SqlQueryResponse> {
    return this.client.request('POST', '/sql', { body: { sql } });
  }
}
