import { describe, it, expect } from 'vitest';
import { createHmac } from 'node:crypto';
import { verifyWebhookSignature, WebhookEventType } from '../src/index.js';

describe('verifyWebhookSignature', () => {
  const secret = 'whsec_test_secret_123';
  const body = JSON.stringify({ event_type: 'record.created', data: { id: '123' } });
  const validSignature = createHmac('sha256', secret).update(body).digest('hex');

  it('returns true for a valid signature', () => {
    expect(verifyWebhookSignature(body, validSignature, secret)).toBe(true);
  });

  it('returns true for Buffer body', () => {
    const bufferBody = Buffer.from(body, 'utf8');
    expect(verifyWebhookSignature(bufferBody, validSignature, secret)).toBe(true);
  });

  it('returns false for an invalid signature', () => {
    expect(verifyWebhookSignature(body, 'bad_signature', secret)).toBe(false);
  });

  it('returns false for a tampered body', () => {
    const tampered = body.replace('123', '456');
    expect(verifyWebhookSignature(tampered, validSignature, secret)).toBe(false);
  });

  it('returns false for wrong secret', () => {
    expect(verifyWebhookSignature(body, validSignature, 'wrong_secret')).toBe(false);
  });
});

describe('WebhookEventType', () => {
  it('contains record events', () => {
    expect(WebhookEventType.RECORD_CREATED).toBe('record.created');
    expect(WebhookEventType.RECORD_UPDATED).toBe('record.updated');
    expect(WebhookEventType.RECORD_DELETED).toBe('record.deleted');
    expect(WebhookEventType.RECORD_MERGED).toBe('record.merged');
  });

  it('contains comment events including resolution', () => {
    expect(WebhookEventType.COMMENT_CREATED).toBe('comment.created');
    expect(WebhookEventType.COMMENT_RESOLVED).toBe('comment.resolved');
    expect(WebhookEventType.COMMENT_UNRESOLVED).toBe('comment.unresolved');
  });

  it('contains new event types', () => {
    expect(WebhookEventType.CALL_RECORDING_CREATED).toBe('call-recording.created');
    expect(WebhookEventType.WORKSPACE_MEMBER_CREATED).toBe('workspace-member.created');
  });
});
