import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockSelfInfo } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('SelfResource', () => {
  it('get() → GET /self', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/self`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockSelfInfo });
      }),
    );
    const result = await client.self.get();
    expect(url).toBe('/v2/self');
    expect(result.data.workspace_name).toBe('Acme Corp');
    expect(result.data.workspace_slug).toBe('acme-corp');
    expect(result.data.workspace_id).toBe('ws_01abc');
    expect(result.data.authorized_by_workspace_member_id).toBe('wm_01abc');
  });
});
