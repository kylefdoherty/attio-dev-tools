import { describe, it, expect } from 'vitest';
import {
  mockEntry,
  mockTask,
  mockRecord,
  mockStatus,
  mockSelectOption,
  mockObject,
  mockList,
  mockNote,
} from './handlers.js';

describe('Mock data matches API schemas', () => {
  it('mockEntry has entry_values, not values', () => {
    expect(mockEntry).toHaveProperty('entry_values');
    expect(mockEntry).not.toHaveProperty('values');
  });

  it('mockTask has completed_at', () => {
    expect(mockTask).toHaveProperty('completed_at');
  });

  it('mockTask linked_records use target_object_id', () => {
    const taskWithLinks = {
      ...mockTask,
      linked_records: [{ target_object_id: 'people', target_record_id: 'rec_01abc' }],
    };
    expect(taskWithLinks.linked_records[0]).toHaveProperty('target_object_id');
    expect(taskWithLinks.linked_records[0]).not.toHaveProperty('target_object');
  });

  it('mockStatus has target_time_in_status', () => {
    expect(mockStatus).toHaveProperty('target_time_in_status');
    expect(mockStatus).not.toHaveProperty('target_time');
    expect(mockStatus).not.toHaveProperty('target_time_unit');
  });

  it('all ID objects include workspace_id', () => {
    expect(mockObject.id).toHaveProperty('workspace_id');
    expect(mockRecord.id).toHaveProperty('workspace_id');
    expect(mockList.id).toHaveProperty('workspace_id');
    expect(mockEntry.id).toHaveProperty('workspace_id');
    expect(mockNote.id).toHaveProperty('workspace_id');
    expect(mockTask.id).toHaveProperty('workspace_id');
    expect(mockSelectOption.id).toHaveProperty('workspace_id');
    expect(mockStatus.id).toHaveProperty('workspace_id');
  });

  it('mockSelectOption id has full composite key', () => {
    expect(mockSelectOption.id).toHaveProperty('workspace_id');
    expect(mockSelectOption.id).toHaveProperty('object_id');
    expect(mockSelectOption.id).toHaveProperty('attribute_id');
    expect(mockSelectOption.id).toHaveProperty('option_id');
  });

  it('mockStatus id has full composite key', () => {
    expect(mockStatus.id).toHaveProperty('workspace_id');
    expect(mockStatus.id).toHaveProperty('object_id');
    expect(mockStatus.id).toHaveProperty('attribute_id');
    expect(mockStatus.id).toHaveProperty('status_id');
  });
});
