import { createHmac, timingSafeEqual } from 'node:crypto';

// ---------------------------------------------------------------------------
// Webhook Event Types
// ---------------------------------------------------------------------------

export const WebhookEventType = {
  // Records
  RECORD_CREATED: 'record.created',
  RECORD_UPDATED: 'record.updated',
  RECORD_DELETED: 'record.deleted',
  RECORD_MERGED: 'record.merged',

  // List entries
  LIST_ENTRY_CREATED: 'list-entry.created',
  LIST_ENTRY_UPDATED: 'list-entry.updated',
  LIST_ENTRY_DELETED: 'list-entry.deleted',

  // Lists
  LIST_CREATED: 'list.created',
  LIST_UPDATED: 'list.updated',
  LIST_DELETED: 'list.deleted',

  // Tasks
  TASK_CREATED: 'task.created',
  TASK_UPDATED: 'task.updated',
  TASK_DELETED: 'task.deleted',

  // Notes
  NOTE_CREATED: 'note.created',
  NOTE_UPDATED: 'note.updated',
  NOTE_DELETED: 'note.deleted',
  NOTE_CONTENT_UPDATED: 'note-content.updated',

  // Comments
  COMMENT_CREATED: 'comment.created',
  COMMENT_DELETED: 'comment.deleted',
  COMMENT_RESOLVED: 'comment.resolved',
  COMMENT_UNRESOLVED: 'comment.unresolved',

  // Object attributes
  OBJECT_ATTRIBUTE_CREATED: 'object-attribute.created',
  OBJECT_ATTRIBUTE_UPDATED: 'object-attribute.updated',

  // List attributes
  LIST_ATTRIBUTE_CREATED: 'list-attribute.created',
  LIST_ATTRIBUTE_UPDATED: 'list-attribute.updated',

  // Workspace members
  WORKSPACE_MEMBER_CREATED: 'workspace-member.created',

  // Call recordings
  CALL_RECORDING_CREATED: 'call-recording.created',
} as const;

export type WebhookEventType = (typeof WebhookEventType)[keyof typeof WebhookEventType];

// ---------------------------------------------------------------------------
// Signature Verification
// ---------------------------------------------------------------------------

/**
 * Verify the HMAC-SHA256 signature on an incoming Attio webhook request.
 *
 * @param rawBody - The raw request body as a string or Buffer
 * @param signature - The value of the `Attio-Signature` header
 * @param secret - Your webhook signing secret
 * @returns `true` if the signature is valid
 */
export function verifyWebhookSignature(
  rawBody: string | Buffer,
  signature: string,
  secret: string,
): boolean {
  const expected = createHmac('sha256', secret).update(rawBody).digest('hex');

  const expectedBuffer = Buffer.from(expected, 'utf8');
  const receivedBuffer = Buffer.from(signature, 'utf8');

  if (expectedBuffer.length !== receivedBuffer.length) {
    return false;
  }

  return timingSafeEqual(expectedBuffer, receivedBuffer);
}
