# Understanding the Attio Data Model

> This guide teaches you how Attio organizes data so you can use the SDKs and CLI effectively. If you have used Salesforce, HubSpot, or even a relational database, the concepts will feel familiar -- but Attio has its own vocabulary and a few important quirks.

## The Big Picture

Attio is a CRM built on a flexible, object-oriented data model. Instead of forcing you into rigid "Contacts" and "Leads" tables, Attio lets you define your own entity types and workflows. Here is the hierarchy at a glance:

```
Workspace                          (your team's Attio account)
 |
 +-- Objects                       (entity types: People, Companies, Deals, ...)
 |    |
 |    +-- Attributes               (fields: name, email, status, ...)
 |    |
 |    +-- Records                  (individual entities: "Jane Doe", "Acme Corp")
 |         |
 |         +-- values              (the data on each record, keyed by attribute)
 |         +-- Notes, Tasks, Comments, Files   (attached to records)
 |
 +-- Lists                         (workflows / pipelines / segments)
      |
      +-- Attributes               (list-specific fields: stage, owner, priority)
      |
      +-- Entries                  (a record placed into the list)
           |
           +-- entry_values        (list-specific data on each entry)
```

If you come from another CRM:

| Attio Concept | Salesforce Equivalent | HubSpot Equivalent | Database Equivalent |
|---|---|---|---|
| Object | Object (Account, Contact) | Object (Contact, Company) | Table |
| Record | Record (a specific Account) | Record (a specific Contact) | Row |
| Attribute | Field | Property | Column |
| List | List View / Report | View / List | Saved Query + extra columns |
| Entry | -- | -- | Row in a join table |

---

## Core Concepts in Detail

### Workspace

A workspace is your team's Attio account -- the top-level container for everything. All API access is scoped to a single workspace.

```python
info = client.self_.identify()
print(info.workspace_name)  # "My Company"
```

### Objects

An **object** defines a *type* of thing you are tracking. Think of it as a table in a database. Attio comes with five **standard objects**:

| Object | Slug | Description |
|---|---|---|
| People | `people` | Individuals you interact with |
| Companies | `companies` | Organizations |
| Deals | `deals` | Sales opportunities |
| Users | `users` | For SaaS: users of your product |
| Workspaces | `workspaces` | For SaaS: customer accounts/tenants |

You can also create **custom objects** for anything else -- Projects, Candidates, Contracts, etc.

```python
# List all objects in your workspace
objects = client.objects.list()
for obj in objects.data:
    print(f"{obj.singular_noun} (slug: {obj.api_slug})")

# Create a custom object
client.objects.create(
    api_slug="projects",
    singular_noun="Project",
    plural_noun="Projects",
)
```

### Records

A **record** is a single instance of an object -- one specific person, one specific company. If objects are tables, records are rows.

```python
person = client.people.create(
    values={
        "email_addresses": [{"email_address": "jane@acme.com"}],
        "name": [{"first_name": "Jane", "last_name": "Doe"}],
        "job_title": [{"value": "CTO"}],
    }
)
print(person.id.record_id)  # "d2c2f990-3af0-..."
print(person.web_url)       # "https://app.attio.com/..."
```

### Attributes

An **attribute** defines what data can be stored on an object or list. Attio supports **17 attribute types**:

| Type | What It Stores | Value Fields |
|---|---|---|
| `text` | Free text | `value` |
| `number` | Numeric value | `value` |
| `checkbox` | Boolean | `value` |
| `currency` | Money amount | `currency_value`, `currency_code` |
| `date` | Calendar date | `value` (ISO 8601) |
| `timestamp` | Date + time | `value` (ISO 8601) |
| `rating` | 1-5 stars | `value` |
| `select` | Dropdown choice | `option.title` or `option.option_id` |
| `status` | Pipeline stage | `status.title` or `status.status_id` |
| `record-reference` | Link to another record | `target_object`, `target_record_id` |
| `personal-name` | First + last name | `first_name`, `last_name`, `full_name` |
| `email-address` | Email | `email_address` |
| `phone-number` | Phone | `original_phone_number`, `country_code` |
| `domain` | Website domain | `domain` |
| `location` | Address | `line_1`, `locality`, `region`, `postcode`, ... |
| `actor-reference` | Who did something | `referenced_actor_type`, `referenced_actor_id` |
| `interaction` | Communication event | `interaction_type`, `interacted_at` |

```python
# List attributes on the People object
attrs = client.attributes.list("objects", "people")
for attr in attrs.data:
    print(f"{attr.title} ({attr.api_slug}): {attr.type}")
```

### Values Are Always Arrays

This is the single most important thing to understand about Attio's API:

**Every attribute value is an array**, even when you only have one value.

```python
# Correct -- values are arrays
values = {
    "name": [{"first_name": "Jane", "last_name": "Doe"}],
    "email_addresses": [{"email_address": "jane@acme.com"}],
    "job_title": [{"value": "CTO"}],
}

# WRONG -- this will fail
values = {
    "name": {"first_name": "Jane"},    # Missing array wrapper!
    "job_title": "CTO",                # Not even an object!
}
```

Why arrays? Two reasons:

1. **Multi-value support.** Some attributes naturally have multiple values -- a person can have 3 email addresses, a company can have multiple domains. Rather than having some attributes return a single value and others return arrays, Attio made everything an array for consistency. You never have to guess whether a field is single or multi-value.
2. **History tracking.** Every value in the array carries `active_from` and `active_until` timestamps. When you change someone's job title from "Engineer" to "CTO", Attio doesn't delete the old value -- it sets `active_until` on "Engineer" and creates a new "CTO" entry with `active_from` set to now. The API returns only currently-active values by default, but you can query the full history. Even a field like "Job Title" that seems like a single value is actually a timeline of every value it has ever had.

This is the #1 source of bugs when starting with the Attio API -- forgetting to wrap values in `[]`.

When reading values back:

```python
person = client.people.get(record_id)
name_values = person.values["name"]  # This is a list
current_name = name_values[0]        # First (usually only) active value
print(current_name.first_name)       # "Jane"

# A person with multiple emails
for email in person.values["email_addresses"]:
    print(email.email_address)  # "jane@acme.com", "j.doe@gmail.com"
```

### Lists and Entries

A **list** is a collection of records used to model a workflow (sales pipeline, hiring funnel, project tracker). An **entry** is what you get when you add a record to a list.

Critical distinction:
- A **record** has `values` -- object-level attributes that exist globally.
- An **entry** has `entry_values` -- list-specific attributes that only exist in that list's context.

```
 Record: "Acme Corp Deal"
   values:
     name: "Acme Corp Enterprise Deal"
     value: $50,000
     |
     +-- Entry in "Q4 Sales Pipeline"
     |     entry_values:
     |       stage: "Negotiation"
     |       owner: "Jane"
     |
     +-- Entry in "Enterprise Deals Tracker"
           entry_values:
             region: "North America"
             review_status: "Pending"
```

```python
# Add a deal to a pipeline
entry = client.entries.create(
    "sales_pipeline",
    parent_object="deals",
    parent_record_id=deal.id.record_id,
    entry_values={"stage": [{"status": "Lead"}]},
)

# Move it to a new stage
client.entries.update(
    "sales_pipeline", entry.id.entry_id,
    entry_values={"stage": [{"status": "Negotiation"}]},
)
```

### Status vs. Select Attributes

**Status** attributes represent workflow stages (Kanban columns). Always single-select. **Select** attributes are general dropdowns. Can be single or multi-select.

```python
# Status (workflow stage)
client.deals.update(record_id, values={"stage": [{"status": "Won"}]})

# Select (multi-value)
client.companies.update(record_id, values={
    "categories": [{"option": "SaaS"}, {"option": "Enterprise"}],
})
```

### Record References (Linking Records)

Record reference attributes create bidirectional relationships. Updating one side automatically updates the other.

```python
# Link a person to a company
client.people.update(person_id, values={
    "company": [{"target_record_id": company_id, "target_object": "companies"}],
})
# This also updates the company's "team" attribute automatically
```

### Notes, Tasks, and Webhooks

```python
# Create a note on a record
client.notes.create(
    parent_object="companies", parent_record_id=company_id,
    title="Q3 Follow-up", format="plaintext",
    content="Discussed renewal pricing. Follow up in two weeks.",
)

# Create a webhook for deal changes
webhook = client.webhooks.create(
    target_url="https://your-app.com/webhooks/attio",
    subscriptions=[{"event_type": "record.created", "filter": {"object": "deals"}}],
)
print(webhook.secret)  # Save this -- only returned on creation
```

---

## SDK Resource Map

| SDK Resource | What It Does | Data Model Concept |
|---|---|---|
| `client.objects` | List, get, create, update entity types | Objects (the blueprints) |
| `client.attributes` | Manage fields on objects or lists | Attributes (the columns) |
| `client.records` | CRUD on any object's records | Records (the rows) |
| `client.people` | Shortcut for records scoped to People | People records |
| `client.companies` | Shortcut for records scoped to Companies | Company records |
| `client.deals` | Shortcut for records scoped to Deals | Deal records |
| `client.users` | Shortcut for records scoped to Users | User records |
| `client.workspaces_` | Shortcut for records scoped to Workspaces | Workspace records |
| `client.lists` | Manage workflow lists | Lists (the pipelines) |
| `client.entries` | CRUD on list entries | Entries (records in a list) |
| `client.select_options` | Manage dropdown options | Select attribute config |
| `client.statuses` | Manage stage options | Status attribute config |
| `client.notes` | Notes on records | Notes |
| `client.tasks` | Tasks linked to records | Tasks |
| `client.comments` | Comments on records/entries | Comments |
| `client.threads` | Comment threads | Threads |
| `client.files` | Upload, download, manage files | Files |
| `client.webhooks` | Manage event subscriptions | Webhooks |
| `client.meetings` | Calendar meetings | Meetings |
| `client.call_recordings` | Call recordings | Recordings |
| `client.transcripts` | Call transcripts | Transcripts |
| `client.workspace_members` | Team members | Members |
| `client.views` | Saved views | Views |
| `client.self_` | Current API token info | Auth info |

---

## Common Recipes

### Create a person and link them to a company

```python
company = client.companies.upsert(
    matching_attribute="domains",
    values={"domains": [{"domain": "acme.com"}], "name": [{"value": "Acme Corp"}]},
)

person = client.people.upsert(
    matching_attribute="email_addresses",
    values={
        "email_addresses": [{"email_address": "jane@acme.com"}],
        "name": [{"first_name": "Jane", "last_name": "Doe"}],
        "company": [{"target_record_id": company.id.record_id, "target_object": "companies"}],
    },
)
```

### Add a deal to a sales pipeline

```python
deal = client.deals.create(values={
    "name": [{"value": "Acme Corp Enterprise"}],
    "value": [{"currency_value": 50000, "currency_code": "USD"}],
})

entry = client.entries.create(
    "sales_pipeline", parent_object="deals",
    parent_record_id=deal.id.record_id,
    entry_values={"stage": [{"status": "Lead"}]},
)
```

### Search across all records

```python
results = client.records.global_search(
    query="Acme", objects=["companies", "people", "deals"], limit=10,
)
for result in results.data:
    print(f"{result.object_slug}: {result.record_text}")
```

### Auto-paginate through all records

```python
for person in client.people.query_all():
    print(person.values["name"][0].full_name)

# Async
async for person in async_client.people.query_all():
    print(person.values["name"][0].full_name)
```

---

## Key Gotchas

1. **Values are always arrays** -- wrap every value in `[]`, even single values
2. **`update` overwrites, `append` adds** -- use `append` for multi-value fields to avoid losing data
3. **`values` vs `entry_values`** -- records use `values`, entries use `entry_values`
4. **Matching attributes for upsert** -- use `email_addresses` for People, `domains` for Companies
5. **Slugs vs IDs** -- both work; slugs are more readable (`"people"` vs UUID)
6. **Relationships are bidirectional** -- linking A to B automatically links B to A
