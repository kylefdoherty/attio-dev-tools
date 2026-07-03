/**
 * Typed builders for Attio attribute WRITE forms.
 *
 * Attio has 17 attribute types; 16 are writable (interaction attributes are
 * system-managed and read-only, so there is no builder for them). Each
 * builder emits the explicit object write form and enforces the type's edge
 * rules (personal-name all-3-fields, location atomic writes, E.164 phones,
 * rating bounds, ...).
 *
 * Values are written keyed by attribute slug under `data.values` (records) or
 * `data.entry_values` (entries); multiselect attributes take arrays.
 *
 * ```ts
 * import {v, recordBody} from "attio-app-kit";
 *
 * const body = recordBody({
 *   name: v.personalName({first: "Jane", last: "Doe"}),
 *   email_addresses: [v.emailAddress("jane@acme.com")],
 *   company: v.recordRef({targetObject: "companies", targetRecordId: companyId}),
 *   stage: v.status("Qualified"),
 * });
 * ```
 */

// ---------------------------------------------------------------------------
// Write-form output types
// ---------------------------------------------------------------------------

export interface TextWrite {
  value: string;
}
export interface NumberWrite {
  value: number;
}
export interface CheckboxWrite {
  value: boolean;
}
export interface CurrencyWrite {
  currency_value: number;
}
export interface RatingWrite {
  value: number;
}
export interface DateWrite {
  value: string;
}
export interface TimestampWrite {
  value: string;
}
export interface StatusWrite {
  status: string;
}
export interface SelectWrite {
  option: string;
}
export interface RecordRefWrite {
  target_object: string;
  target_record_id: string;
}
export interface ActorRefWrite {
  referenced_actor_type: 'workspace-member';
  referenced_actor_id: string;
}
export interface ActorRefByEmailWrite {
  workspace_member_email_address: string;
}
export interface PersonalNameWrite {
  first_name: string;
  last_name: string;
  full_name: string;
}
export interface EmailAddressWrite {
  email_address: string;
}
export interface DomainWrite {
  domain: string;
}
export interface PhoneNumberWrite {
  original_phone_number: string;
  country_code: string | null;
}
export interface LocationWrite {
  line_1: string | null;
  line_2: string | null;
  line_3: string | null;
  line_4: string | null;
  locality: string | null;
  region: string | null;
  postcode: string | null;
  country_code: string | null;
  latitude: string | null;
  longitude: string | null;
}

// ---------------------------------------------------------------------------
// Builders
// ---------------------------------------------------------------------------

/** text — plain string value (10MB max, single). */
export function text(value: string): TextWrite {
  if (typeof value !== 'string') {
    throw new TypeError(`v.text expects a string, got ${typeof value}`);
  }
  return { value };
}

/** number — float64, stored to 4 decimal places. */
export function number(value: number): NumberWrite {
  if (!Number.isFinite(value)) {
    throw new RangeError(`v.number expects a finite number, got ${value}`);
  }
  return { value };
}

/** checkbox — boolean (no null). */
export function checkbox(value: boolean): CheckboxWrite {
  return { value: Boolean(value) };
}

/**
 * currency — amount only. The currency CODE is configured attribute-wide on
 * the attribute itself, not per value. Stored to 4 decimal places.
 */
export function currency(amount: number): CurrencyWrite {
  if (!Number.isFinite(amount)) {
    throw new RangeError(`v.currency expects a finite number, got ${amount}`);
  }
  return { currency_value: amount };
}

/** rating — integer 0–5. */
export function rating(value: number): RatingWrite {
  if (!Number.isInteger(value) || value < 0 || value > 5) {
    throw new RangeError(`v.rating expects an integer 0-5, got ${value}`);
  }
  return { value };
}

/**
 * date — calendar date, no time. Accepts "YYYY-MM-DD" (or partial
 * "YYYY"/"YYYY-MM", which Attio coerces) or a Date (converted to its UTC
 * calendar date).
 */
export function date(value: string | Date): DateWrite {
  if (value instanceof Date) {
    if (Number.isNaN(value.getTime())) throw new RangeError('v.date: invalid Date');
    return { value: value.toISOString().slice(0, 10) };
  }
  if (!/^\d{4}(-\d{2}){0,2}$/.test(value)) {
    throw new RangeError(
      `v.date expects "YYYY-MM-DD" (or partial "YYYY"/"YYYY-MM"), got "${value}". Use v.timestamp for datetimes.`,
    );
  }
  return { value };
}

/**
 * timestamp — point in time, stored in UTC. Accepts a Date or epoch ms
 * (converted to ISO 8601 UTC) or an ISO string (passed through unchanged —
 * note Attio assumes UTC for zoneless strings).
 */
export function timestamp(value: string | Date | number): TimestampWrite {
  if (value instanceof Date || typeof value === 'number') {
    const d = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(d.getTime())) throw new RangeError(`v.timestamp: invalid date ${value}`);
    return { value: d.toISOString() };
  }
  if (typeof value !== 'string' || Number.isNaN(Date.parse(value))) {
    throw new RangeError(
      `v.timestamp expects an ISO 8601 string, Date, or epoch ms, got "${value}"`,
    );
  }
  return { value };
}

/**
 * status — by title or UUID. Unknown titles ERROR (Attio never auto-creates
 * statuses); create the status first via the API or UI.
 */
export function status(titleOrId: string): StatusWrite {
  if (!titleOrId) throw new RangeError('v.status expects a non-empty title or UUID');
  return { status: titleOrId };
}

/**
 * select — by option title or UUID. Unknown titles ERROR (never
 * auto-created). For multiselect attributes pass an array of v.select(...).
 */
export function select(titleOrId: string): SelectWrite {
  if (!titleOrId) throw new RangeError('v.select expects a non-empty title or UUID');
  return { option: titleOrId };
}

/**
 * record-reference — by target record id. The target record MUST already
 * exist (write parents before children).
 */
export function recordRef(ref: { targetObject: string; targetRecordId: string }): RecordRefWrite {
  if (!ref.targetObject || !ref.targetRecordId) {
    throw new RangeError('v.recordRef requires targetObject and targetRecordId');
  }
  return { target_object: ref.targetObject, target_record_id: ref.targetRecordId };
}

/**
 * record-reference by unique-attribute match (assert-style). Standard
 * matchable slugs: `domains` (companies), `email_addresses` (people),
 * `user_id` (users), `workspace_id` (workspaces).
 *
 * ```ts
 * v.recordRefByUnique({
 *   targetObject: "people",
 *   matchingAttribute: "email_addresses",
 *   value: "jane@acme.com",
 * })
 * // => {target_object: "people", email_addresses: ["jane@acme.com"]}
 * ```
 */
export function recordRefByUnique(ref: {
  targetObject: string;
  matchingAttribute: string;
  value: unknown;
}): Record<string, unknown> {
  if (!ref.targetObject || !ref.matchingAttribute) {
    throw new RangeError('v.recordRefByUnique requires targetObject and matchingAttribute');
  }
  return {
    target_object: ref.targetObject,
    [ref.matchingAttribute]: Array.isArray(ref.value) ? ref.value : [ref.value],
  };
}

/**
 * actor-reference — by workspace member id. Only workspace members are
 * writable actor references.
 */
export function actorRef(workspaceMemberId: string): ActorRefWrite {
  if (!workspaceMemberId) throw new RangeError('v.actorRef expects a workspace member id');
  return {
    referenced_actor_type: 'workspace-member',
    referenced_actor_id: workspaceMemberId,
  };
}

/** actor-reference — by workspace member email. */
export function actorRefByEmail(email: string): ActorRefByEmailWrite {
  if (!email.includes('@')) {
    throw new RangeError(`v.actorRefByEmail expects an email address, got "${email}"`);
  }
  return { workspace_member_email_address: email };
}

/**
 * personal-name — object writes require ALL THREE fields
 * (first_name/last_name/full_name); this builder fills them in.
 *
 * - `personalName({first, last})` derives full_name as "first last".
 * - `personalName({first, last, full})` uses your full name verbatim.
 * - `personalName("Doe, Jane")` — a plain string is Attio's string write form
 *   ("Last, First"; no comma means everything lands in first_name) and is
 *   returned as-is for the API to parse.
 */
export function personalName(
  input: { first?: string; last?: string; full?: string } | string,
): PersonalNameWrite | string {
  if (typeof input === 'string') {
    if (!input.trim()) throw new RangeError('v.personalName: empty name');
    return input;
  }
  const first = input.first ?? '';
  const last = input.last ?? '';
  if (!first && !last) {
    throw new RangeError(
      'v.personalName requires at least one of {first, last} — or pass a "Last, First" string',
    );
  }
  return {
    first_name: first,
    last_name: last,
    full_name: input.full ?? [first, last].filter(Boolean).join(' '),
  };
}

/** email-address — strictly validated by the API; derived fields (domain etc.) auto-computed. */
export function emailAddress(email: string): EmailAddressWrite {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new RangeError(`v.emailAddress expects a valid email, got "${email}"`);
  }
  return { email_address: email };
}

/**
 * domain — stores domains, not URLs (Attio trims paths). Accepts a bare
 * domain or a URL, from which the hostname is extracted. Domain attributes
 * are multiselect: pass `[v.domain(...)]` arrays.
 */
export function domain(domainOrUrl: string): DomainWrite {
  let host = domainOrUrl.trim();
  if (!host) throw new RangeError('v.domain expects a domain');
  if (/^[a-z][a-z0-9+.-]*:\/\//i.test(host) || host.includes('/')) {
    try {
      host = new URL(host.includes('://') ? host : `https://${host}`).hostname;
    } catch {
      throw new RangeError(`v.domain could not parse "${domainOrUrl}"`);
    }
  }
  if (!host.includes('.')) {
    throw new RangeError(`v.domain expects a domain like "acme.com", got "${domainOrUrl}"`);
  }
  return { domain: host };
}

/**
 * phone-number — E.164. Pass a "+..." string, or `{original, countryCode}`
 * where a national-format `original` needs its ISO country code (e.g. "US").
 */
export function phoneNumber(
  input: string | { original: string; countryCode?: string | null },
): PhoneNumberWrite {
  if (typeof input === 'string') {
    if (!input.startsWith('+')) {
      throw new RangeError(
        `v.phoneNumber: "${input}" is not E.164 (+ prefix). Pass {original, countryCode} for national formats.`,
      );
    }
    return { original_phone_number: input, country_code: null };
  }
  const { original, countryCode } = input;
  if (!original) throw new RangeError('v.phoneNumber requires original');
  if (!original.startsWith('+') && !countryCode) {
    throw new RangeError(
      `v.phoneNumber: national-format "${original}" requires a countryCode (e.g. "US")`,
    );
  }
  return { original_phone_number: original, country_code: countryCode ?? null };
}

export interface LocationInput {
  line1?: string | null;
  line2?: string | null;
  line3?: string | null;
  line4?: string | null;
  locality?: string | null;
  region?: string | null;
  postcode?: string | null;
  /** ISO 3166-1 alpha-2, e.g. "US". */
  countryCode?: string | null;
  latitude?: string | number | null;
  longitude?: string | number | null;
}

/**
 * location — object writes are ATOMIC: the API requires EVERY property
 * present, nulls included. This builder fills any field you omit with null
 * (which also means a partial update clears the omitted fields — fetch and
 * merge first if you need to preserve them).
 *
 * For a free-form address string, write plain text instead: Attio auto-parses
 * string writes to location attributes.
 */
export function location(input: LocationInput): LocationWrite {
  const coord = (c: string | number | null | undefined): string | null =>
    c === null || c === undefined ? null : typeof c === 'number' ? String(c) : c;
  return {
    line_1: input.line1 ?? null,
    line_2: input.line2 ?? null,
    line_3: input.line3 ?? null,
    line_4: input.line4 ?? null,
    locality: input.locality ?? null,
    region: input.region ?? null,
    postcode: input.postcode ?? null,
    country_code: input.countryCode ?? null,
    latitude: coord(input.latitude),
    longitude: coord(input.longitude),
  };
}

// NOTE: `interaction` attributes (first/last email, calendar interactions...)
// are system-managed and READ-ONLY — there is deliberately no builder.

/** All builders under one namespace: `v.text(...)`, `v.currency(...)`, ... */
export const v = {
  text,
  number,
  checkbox,
  currency,
  rating,
  date,
  timestamp,
  status,
  select,
  recordRef,
  recordRefByUnique,
  actorRef,
  actorRefByEmail,
  personalName,
  emailAddress,
  domain,
  phoneNumber,
  location,
} as const;

// ---------------------------------------------------------------------------
// Payload helpers
// ---------------------------------------------------------------------------

export type ValuesInput = Record<string, unknown>;

/**
 * Build a record create/update body: `{data: {values}}`.
 *
 * `POST /v2/objects/{object}/records` (create),
 * `PATCH .../records/{id}` (append multiselects), `PUT .../records/{id}` (overwrite).
 */
export function recordBody(values: ValuesInput): { data: { values: ValuesInput } } {
  return { data: { values } };
}

/**
 * Build an assert/upsert body — same shape as recordBody; the matching
 * attribute goes in the query string, not the body:
 * `PUT /v2/objects/{object}/records?matching_attribute={slug}`.
 *
 * The matching attribute must be unique; more than one match is an error.
 * Deals have NO default unique attribute — create one before upserting deals.
 */
export function assertBody(values: ValuesInput): { data: { values: ValuesInput } } {
  return recordBody(values);
}

/**
 * Build a list entry create body for `POST /v2/lists/{list}/entries`.
 * `entryValues` are the LIST's own attributes — parent record values live on
 * the record, not the entry.
 */
export function entryBody(input: {
  parentObject: string;
  parentRecordId: string;
  entryValues?: ValuesInput;
}): { data: { parent_object: string; parent_record_id: string; entry_values: ValuesInput } } {
  return {
    data: {
      parent_object: input.parentObject,
      parent_record_id: input.parentRecordId,
      entry_values: input.entryValues ?? {},
    },
  };
}
