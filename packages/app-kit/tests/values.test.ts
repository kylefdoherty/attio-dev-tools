import { describe, expect, it } from 'vitest';
import { assertBody, entryBody, recordBody, v } from '../src/values.js';

describe('v.text', () => {
  it('wraps a string', () => {
    expect(v.text('hello')).toEqual({ value: 'hello' });
    expect(v.text('')).toEqual({ value: '' });
  });
  it('rejects non-strings', () => {
    // @ts-expect-error runtime guard
    expect(() => v.text(42)).toThrow(TypeError);
  });
});

describe('v.number', () => {
  it('wraps finite numbers', () => {
    expect(v.number(42.5)).toEqual({ value: 42.5 });
    expect(v.number(0)).toEqual({ value: 0 });
    expect(v.number(-1)).toEqual({ value: -1 });
  });
  it('rejects NaN and Infinity', () => {
    expect(() => v.number(Number.NaN)).toThrow(RangeError);
    expect(() => v.number(Number.POSITIVE_INFINITY)).toThrow(RangeError);
  });
});

describe('v.checkbox', () => {
  it('wraps booleans', () => {
    expect(v.checkbox(true)).toEqual({ value: true });
    expect(v.checkbox(false)).toEqual({ value: false });
  });
});

describe('v.currency', () => {
  it('emits currency_value only (code is attribute-wide config)', () => {
    expect(v.currency(1500.25)).toEqual({ currency_value: 1500.25 });
  });
  it('rejects non-finite amounts', () => {
    expect(() => v.currency(Number.NaN)).toThrow(RangeError);
  });
});

describe('v.rating', () => {
  it('accepts integers 0-5', () => {
    for (const n of [0, 1, 2, 3, 4, 5]) expect(v.rating(n)).toEqual({ value: n });
  });
  it('rejects out-of-range and non-integers', () => {
    expect(() => v.rating(-1)).toThrow(RangeError);
    expect(() => v.rating(6)).toThrow(RangeError);
    expect(() => v.rating(2.5)).toThrow(RangeError);
  });
});

describe('v.date', () => {
  it('accepts YYYY-MM-DD strings', () => {
    expect(v.date('2026-07-03')).toEqual({ value: '2026-07-03' });
  });
  it('accepts partial dates (Attio coerces)', () => {
    expect(v.date('2026')).toEqual({ value: '2026' });
    expect(v.date('2026-07')).toEqual({ value: '2026-07' });
  });
  it('converts Date to its UTC calendar date', () => {
    expect(v.date(new Date('2026-07-03T23:59:59Z'))).toEqual({ value: '2026-07-03' });
  });
  it('rejects datetimes and garbage', () => {
    expect(() => v.date('2026-07-03T12:00:00Z')).toThrow(/timestamp/);
    expect(() => v.date('July 3rd')).toThrow(RangeError);
    expect(() => v.date(new Date('invalid'))).toThrow(RangeError);
  });
});

describe('v.timestamp', () => {
  it('converts Date and epoch ms to ISO UTC', () => {
    const iso = '2026-07-03T12:34:56.000Z';
    expect(v.timestamp(new Date(iso))).toEqual({ value: iso });
    expect(v.timestamp(Date.parse(iso))).toEqual({ value: iso });
  });
  it('passes valid ISO strings through unchanged (no local-time reinterpretation)', () => {
    expect(v.timestamp('2026-07-03T12:00:00+02:00')).toEqual({
      value: '2026-07-03T12:00:00+02:00',
    });
  });
  it('rejects unparseable strings and invalid dates', () => {
    expect(() => v.timestamp('not a time')).toThrow(RangeError);
    expect(() => v.timestamp(new Date('invalid'))).toThrow(RangeError);
  });
});

describe('v.status / v.select', () => {
  it('wraps title or UUID', () => {
    expect(v.status('Qualified')).toEqual({ status: 'Qualified' });
    expect(v.select('Tier 1')).toEqual({ option: 'Tier 1' });
  });
  it('rejects empty values', () => {
    expect(() => v.status('')).toThrow(RangeError);
    expect(() => v.select('')).toThrow(RangeError);
  });
});

describe('v.recordRef', () => {
  it('emits snake_case target fields', () => {
    expect(v.recordRef({ targetObject: 'companies', targetRecordId: 'rec-1' })).toEqual({
      target_object: 'companies',
      target_record_id: 'rec-1',
    });
  });
  it('requires both fields', () => {
    expect(() => v.recordRef({ targetObject: '', targetRecordId: 'x' })).toThrow(RangeError);
    expect(() => v.recordRef({ targetObject: 'people', targetRecordId: '' })).toThrow(RangeError);
  });
});

describe('v.recordRefByUnique', () => {
  it('builds an assert-style reference with an array value', () => {
    expect(
      v.recordRefByUnique({
        targetObject: 'people',
        matchingAttribute: 'email_addresses',
        value: 'jane@acme.com',
      }),
    ).toEqual({ target_object: 'people', email_addresses: ['jane@acme.com'] });
  });
  it('keeps array values as-is', () => {
    expect(
      v.recordRefByUnique({
        targetObject: 'companies',
        matchingAttribute: 'domains',
        value: ['acme.com'],
      }),
    ).toEqual({ target_object: 'companies', domains: ['acme.com'] });
  });
});

describe('v.actorRef / v.actorRefByEmail', () => {
  it('emits a workspace-member reference', () => {
    expect(v.actorRef('member-uuid')).toEqual({
      referenced_actor_type: 'workspace-member',
      referenced_actor_id: 'member-uuid',
    });
  });
  it('emits the email shorthand form', () => {
    expect(v.actorRefByEmail('kyle@example.com')).toEqual({
      workspace_member_email_address: 'kyle@example.com',
    });
  });
  it('validates inputs', () => {
    expect(() => v.actorRef('')).toThrow(RangeError);
    expect(() => v.actorRefByEmail('nope')).toThrow(RangeError);
  });
});

describe('v.personalName (all-3-fields rule)', () => {
  it('emits all three fields, deriving full_name', () => {
    expect(v.personalName({ first: 'Jane', last: 'Doe' })).toEqual({
      first_name: 'Jane',
      last_name: 'Doe',
      full_name: 'Jane Doe',
    });
  });
  it('respects an explicit full name', () => {
    expect(v.personalName({ first: 'Jane', last: 'Doe', full: 'Dr. Jane Doe' })).toEqual({
      first_name: 'Jane',
      last_name: 'Doe',
      full_name: 'Dr. Jane Doe',
    });
  });
  it('fills missing first/last with empty strings (still all 3 present)', () => {
    expect(v.personalName({ first: 'Cher' })).toEqual({
      first_name: 'Cher',
      last_name: '',
      full_name: 'Cher',
    });
    expect(v.personalName({ last: 'Doe' })).toEqual({
      first_name: '',
      last_name: 'Doe',
      full_name: 'Doe',
    });
  });
  it('passes the "Last, First" string form through for the API to parse', () => {
    expect(v.personalName('Doe, Jane')).toBe('Doe, Jane');
  });
  it('rejects empty inputs', () => {
    expect(() => v.personalName({})).toThrow(RangeError);
    expect(() => v.personalName('   ')).toThrow(RangeError);
  });
});

describe('v.emailAddress', () => {
  it('wraps a valid email', () => {
    expect(v.emailAddress('jane@acme.com')).toEqual({ email_address: 'jane@acme.com' });
  });
  it('rejects invalid emails', () => {
    expect(() => v.emailAddress('nope')).toThrow(RangeError);
    expect(() => v.emailAddress('a@b')).toThrow(RangeError);
    expect(() => v.emailAddress('a b@c.com')).toThrow(RangeError);
  });
});

describe('v.domain', () => {
  it('wraps bare domains', () => {
    expect(v.domain('acme.com')).toEqual({ domain: 'acme.com' });
    expect(v.domain('sub.acme.co.uk')).toEqual({ domain: 'sub.acme.co.uk' });
  });
  it('extracts the hostname from URLs (Attio stores domains, not URLs)', () => {
    expect(v.domain('https://acme.com/pricing?x=1')).toEqual({ domain: 'acme.com' });
    expect(v.domain('acme.com/about')).toEqual({ domain: 'acme.com' });
  });
  it('rejects non-domains', () => {
    expect(() => v.domain('')).toThrow(RangeError);
    expect(() => v.domain('localhost')).toThrow(RangeError);
  });
});

describe('v.phoneNumber', () => {
  it('accepts E.164 strings', () => {
    expect(v.phoneNumber('+15551234567')).toEqual({
      original_phone_number: '+15551234567',
      country_code: null,
    });
  });
  it('accepts national format with a country code', () => {
    expect(v.phoneNumber({ original: '555-123-4567', countryCode: 'US' })).toEqual({
      original_phone_number: '555-123-4567',
      country_code: 'US',
    });
  });
  it('allows null country code when the number has a + prefix', () => {
    expect(v.phoneNumber({ original: '+445551234567' })).toEqual({
      original_phone_number: '+445551234567',
      country_code: null,
    });
  });
  it('rejects national format without a country code', () => {
    expect(() => v.phoneNumber('555-123-4567')).toThrow(RangeError);
    expect(() => v.phoneNumber({ original: '555-123-4567' })).toThrow(RangeError);
  });
});

describe('v.location (atomic write rule)', () => {
  it('fills every omitted field with null', () => {
    expect(v.location({ locality: 'Denver', region: 'CO', countryCode: 'US' })).toEqual({
      line_1: null,
      line_2: null,
      line_3: null,
      line_4: null,
      locality: 'Denver',
      region: 'CO',
      postcode: null,
      country_code: 'US',
      latitude: null,
      longitude: null,
    });
  });
  it('includes all provided fields in snake_case', () => {
    const full = v.location({
      line1: '123 Main St',
      line2: 'Suite 4',
      locality: 'Denver',
      region: 'CO',
      postcode: '80202',
      countryCode: 'US',
      latitude: 39.7392,
      longitude: '-104.9903',
    });
    expect(full.line_1).toBe('123 Main St');
    expect(full.line_2).toBe('Suite 4');
    expect(full.postcode).toBe('80202');
    // numbers are stringified; strings pass through
    expect(full.latitude).toBe('39.7392');
    expect(full.longitude).toBe('-104.9903');
  });
  it('an empty input still emits all 10 fields as null (atomic clear)', () => {
    const cleared = v.location({});
    expect(Object.keys(cleared)).toHaveLength(10);
    expect(Object.values(cleared).every((x) => x === null)).toBe(true);
  });
});

describe('payload helpers', () => {
  it('recordBody wraps values', () => {
    expect(recordBody({ name: 'Acme' })).toEqual({ data: { values: { name: 'Acme' } } });
  });
  it('assertBody has the same shape (matching_attribute is a query param)', () => {
    expect(assertBody({ domains: [{ domain: 'acme.com' }] })).toEqual({
      data: { values: { domains: [{ domain: 'acme.com' }] } },
    });
  });
  it('entryBody builds a list entry payload', () => {
    expect(
      entryBody({ parentObject: 'people', parentRecordId: 'rec-1', entryValues: { stage: 'New' } }),
    ).toEqual({
      data: { parent_object: 'people', parent_record_id: 'rec-1', entry_values: { stage: 'New' } },
    });
  });
  it('entryBody defaults entry_values to {}', () => {
    expect(entryBody({ parentObject: 'people', parentRecordId: 'rec-1' }).data.entry_values).toEqual(
      {},
    );
  });
  it('composes into a realistic create payload', () => {
    expect(
      recordBody({
        name: v.personalName({ first: 'Jane', last: 'Doe' }),
        email_addresses: [v.emailAddress('jane@acme.com')],
        company: v.recordRefByUnique({
          targetObject: 'companies',
          matchingAttribute: 'domains',
          value: 'acme.com',
        }),
        rating: v.rating(4),
      }),
    ).toEqual({
      data: {
        values: {
          name: { first_name: 'Jane', last_name: 'Doe', full_name: 'Jane Doe' },
          email_addresses: [{ email_address: 'jane@acme.com' }],
          company: { target_object: 'companies', domains: ['acme.com'] },
          rating: { value: 4 },
        },
      },
    });
  });
});
