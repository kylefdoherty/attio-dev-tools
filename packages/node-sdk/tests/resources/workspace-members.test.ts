import { describe, it, expect } from 'vitest';
import { http, HttpResponse } from 'msw';
import { AttioClient } from '../../src/index.js';
import { server, mockWorkspaceMember } from '../handlers.js';

const BASE = 'https://api.attio.com/v2';
const client = new AttioClient({ apiKey: 'test-key', maxRetries: 0 });

describe('WorkspaceMembersResource', () => {
  it('list() → GET /workspace_members', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/workspace_members`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: [mockWorkspaceMember] });
      }),
    );
    const result = await client.workspaceMembers.list();
    expect(url).toBe('/v2/workspace_members');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].first_name).toBe('Jane');
  });

  it('get() → GET /workspace_members/:id', async () => {
    let url = '';
    server.use(
      http.get(`${BASE}/workspace_members/:id`, ({ request }) => {
        url = new URL(request.url).pathname;
        return HttpResponse.json({ data: mockWorkspaceMember });
      }),
    );
    const result = await client.workspaceMembers.get('wm_01abc');
    expect(url).toBe('/v2/workspace_members/wm_01abc');
    expect(result.data.email_address).toBe('jane@example.com');
  });
});
