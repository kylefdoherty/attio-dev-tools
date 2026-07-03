import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient, AttioError, ScopeError } from '../../src/index.js';
import { server, mockSqlRow } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('SqlResource', () => {
  it('query() → POST /sql with body', async () => {
    let method = '';
    let url = '';
    let body: unknown;
    server.use(
      http.post(`${BASE}/sql`, async ({ request }) => {
        method = request.method;
        url = new URL(request.url).pathname;
        body = await request.json();
        return HttpResponse.json({ data: { rows: [mockSqlRow] } });
      }),
    );
    const result = await client.sql.query("SELECT * FROM companies WHERE name = 'Acme Corp'");
    expect(method).toBe('POST');
    expect(url).toBe('/v2/sql');
    expect(body).toEqual({ sql: "SELECT * FROM companies WHERE name = 'Acme Corp'" });
    expect(result.data.rows).toHaveLength(1);
    expect(result.data.rows[0].name).toBe('Acme Corp');
  });

  it('query() with invalid SQL throws AttioError', async () => {
    server.use(
      http.post(`${BASE}/sql`, () =>
        HttpResponse.json(
          { code: 'VALIDATION_ERROR', message: 'Only SELECT statements are allowed.' },
          { status: 400 },
        ),
      ),
    );
    await expect(client.sql.query('DROP TABLE companies')).rejects.toThrow(AttioError);
  });

  it('query() without Enterprise access throws ScopeError', async () => {
    server.use(
      http.post(`${BASE}/sql`, () =>
        HttpResponse.json({ message: 'SQL API requires an Enterprise plan.' }, { status: 403 }),
      ),
    );
    await expect(client.sql.query('SELECT 1')).rejects.toThrow(ScopeError);
  });
});
