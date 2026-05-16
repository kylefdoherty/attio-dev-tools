# Attio App Templates: Research Report

> Research conducted May 2026. Goal: identify the highest-value frontend app templates that can be scaffolded in seconds with Attio OAuth and API access pre-wired.

---

## Table of Contents

1. [Top 20 App Ideas (Ranked)](#top-20-app-ideas)
2. [Template Categories](#template-categories)
3. [Detailed Template Specs](#detailed-template-specs)
4. [Expert Network Deep Dive](#expert-network-deep-dive)
5. [Technical Patterns & Shared Components](#technical-patterns--shared-components)

---

## Who Uses Attio?

Before diving into templates, it is worth grounding ourselves in who actually uses Attio and what they care about. Attio has ~5,000 paying customers. The median company size is 20-49 employees. The top industries are:

| Segment | Examples | What they track in Attio |
|---------|----------|--------------------------|
| **SaaS startups** | Modal, Replicate, Lovable, ElevenLabs | PLG funnels, deals, customer workspaces, usage signals |
| **VC / PE firms** | Seedcamp, Union Square Ventures | Deal flow, founders, LPs, portfolio companies |
| **Agencies** | Digital marketing, dev shops | Clients, projects, retainers, pipelines |
| **Marketplaces** | Two-sided platforms | Supply-side and demand-side relationships |
| **Expert / talent networks** | Consulting, advisory, freelance platforms | Experts, engagements, performance, earnings |
| **Professional services** | Law, accounting, consulting | Clients, matters, capacity, billing |

Attio's differentiator is its flexible data model: custom objects, custom attributes, lists, and relationships let teams model any business structure. This means the template library needs to work with both standard objects (People, Companies, Deals) and arbitrary custom objects.

---

## Top 20 App Ideas

Ranked by estimated breadth of appeal across Attio's user base, factoring in (a) how many personas need it, (b) how poorly the native CRM UI serves the use case, and (c) how quickly it can deliver value.

### 1. Pipeline Analytics Dashboard
**Who:** RevOps, Sales Managers, Founders
**What:** Funnel conversion rates by stage, average deal velocity, win/loss analysis, pipeline coverage ratio, and forecasted revenue. Goes far beyond Attio's native list views by computing derived metrics and showing trends over time.
**Why it ranks #1:** Every single Attio workspace with deals needs this. It is the most universal "first app" someone would build.

### 2. Sales Leaderboard
**Who:** Sales Managers, AEs, Founders
**What:** Real-time ranked view of reps by closed revenue, deals created, meetings booked, and pipeline generated. Filterable by time period. Gamification elements (streaks, personal bests). Can be displayed on a TV in the office.
**Why it ranks high:** Leaderboards are one of the most requested features in every CRM, and Attio does not have a native one. Simple to build, high daily engagement.

### 3. Pre-Call Prep Sheet Generator
**Who:** AEs, SDRs, Customer Success
**What:** Given a meeting (manual input or calendar integration), pulls the contact's Attio record, company info, deal history, notes, and recent interactions into a single-page brief with talking points. Optionally enriches with LinkedIn/web data.
**Why it ranks high:** Research shows structured pre-call prep increases qualification accuracy by 43%. Every rep does this manually today.

### 4. Customer Health Dashboard
**Who:** Customer Success, Founders
**What:** Grid of all customers with a computed health score based on configurable signals: days since last interaction, deal value, NPS/CSAT (if tracked), support ticket volume, product usage (if synced via Segment). Red/yellow/green traffic lights. Drill-down to individual accounts.
**Why it ranks high:** Churn prevention is existential for SaaS startups. Attio tracks the relationship data; this template turns it into actionable health signals.

### 5. Investor Update / Board Report Generator
**Who:** Founders, CEOs
**What:** Pulls key metrics from Attio (deals closed, pipeline value, new customers, churned customers) and presents them in a clean, shareable format suitable for investor updates. Supports adding manual metrics (MRR, burn rate, runway). Export to PDF or generate a shareable link.
**Why it ranks high:** Every funded startup sends monthly investor updates. Attio's VC/startup user base makes this uniquely relevant.

### 6. Deal Room / Deal Review App
**Who:** Sales Managers, AEs, Founders
**What:** Focused view of a single deal with all associated contacts, companies, notes, tasks, and timeline in one place. Includes a deal scoring rubric, competitive analysis section, and next-steps tracker. Designed for weekly deal review meetings.
**Why it ranks high:** Deal reviews are a core sales ritual. The CRM record view is too cluttered; this is a purpose-built "war room" for each deal.

### 7. CRM Data Quality Audit
**Who:** RevOps, Operations
**What:** Scans the workspace and reports on: records missing key fields (email, company, job title), duplicate detection, stale records (no interaction in 90+ days), orphaned records (contacts not linked to companies), and formatting inconsistencies. Provides a "CRM health score" and actionable fix-it lists.
**Why it ranks high:** Data quality is the #1 complaint in every CRM. RevOps teams spend hours on this manually. Automating the audit is high-leverage.

### 8. Partner Performance Tracker
**Who:** Partnerships/BD, Founders
**What:** Dashboard showing partner/referrer performance: deals generated, deals qualified, deals won, revenue attributed, and partner earnings/commissions. Supports custom objects for partners. This is a generalized version of the Expert Network dashboard.
**Why it ranks high:** Referral and partner programs are common across SaaS, agencies, and marketplaces. Many Attio users track partners as custom objects.

### 9. VC Deal Flow Pipeline
**Who:** VC/PE investors
**What:** Kanban and table views of deal flow with custom stages (Sourced, First Meeting, DD, Term Sheet, Closed). Includes founder profiles pulled from People, company details from Companies, and investment memos from Notes. Co-investor tracking. Source attribution.
**Why it ranks high:** VC firms are a core Attio segment. Attio's custom objects are perfect for modeling deal flow, but the native UI is not purpose-built for investment workflows.

### 10. Renewal & Expansion Tracker
**Who:** Customer Success, RevOps, Founders
**What:** Calendar view of upcoming renewals with deal value, health indicators, and expansion opportunities. Shows ARR at risk, renewals due this month/quarter, and upsell pipeline. Alerts for renewals approaching without recent touchpoints.
**Why it ranks high:** Expansion revenue accounts for 60% of SaaS growth. Tracking renewals in a CRM list view is clunky; a dedicated app with time-based views is far more useful.

### 11. Contact Relationship Map
**Who:** AEs, BD, Founders
**What:** Visual network graph showing relationships between people, companies, and deals. Shows who introduced whom, shared connections, and relationship strength (based on interaction frequency). Useful for navigating complex enterprise sales or investor networks.
**Why it ranks high:** Relationship intelligence is Attio's core thesis. This template makes the implicit network visible.

### 12. Client Portal (External-Facing)
**Who:** Agencies, Professional Services, Customer Success
**What:** A branded, external-facing portal where clients can see their project status, upcoming deliverables, invoices, and key contacts. Pulls data from Attio but presents it through a client-friendly interface with login/auth.
**Why it ranks high:** Agencies and professional services firms constantly need to share project status with clients. Building a portal on CRM data eliminates the need for a separate tool.

### 13. Recruiting Pipeline Dashboard
**Who:** Founders, Hiring Managers, Recruiters
**What:** Kanban view of candidates by role and stage (Applied, Screen, Interview, Offer, Hired/Rejected). Tracks source, time-in-stage, and interviewer feedback. Many startups under 50 people use their CRM for recruiting rather than buying an ATS.
**Why it ranks high:** Attio's flexible objects make it a viable lightweight ATS. A purpose-built recruiting view makes it actually usable for hiring.

### 14. Agency Retainer Dashboard
**Who:** Agency owners, Account Managers
**What:** Shows all active clients with retainer status: hours/budget used vs. allocated, deliverables completed, upcoming milestones, and profitability per client. Alerts when retainers are running low or over-serviced.
**Why it ranks high:** Agencies are a key Attio segment. Retainer management is critical for profitability but poorly served by generic CRM views.

### 15. Weekly Sales Standup View
**Who:** Sales Managers, AEs
**What:** A meeting-ready view designed for 15-minute standups. Shows each rep's committed deals for the period, deals that moved stages, deals at risk, and activity metrics for the week. One click to advance to the next rep's view.
**Why it ranks high:** Every sales team has standups. This replaces the "everyone talks through their pipeline" with a structured, data-driven format.

### 16. LP / Investor Portal
**Who:** VC/PE fund managers
**What:** External-facing portal where LPs can view fund performance, portfolio company updates, capital call status, and distribution history. Pulls portfolio data from Attio custom objects. Secured with login.
**Why it ranks high:** LP reporting is a time-consuming obligation for fund managers. Attio-native funds can automate this with a portal template.

### 17. Outbound Campaign Tracker
**Who:** SDRs, Growth teams, Founders
**What:** Tracks outbound sequences with response rates, meetings booked, and pipeline generated per campaign/sequence. Connects outbound activity (from email tools synced to Attio) to downstream deal outcomes.
**Why it ranks high:** Attribution from outbound activity to revenue is a persistent pain point. This bridges the gap between activity tracking and pipeline reporting.

### 18. Marketplace Supply Dashboard
**Who:** Marketplace operators
**What:** Tracks supply-side health for two-sided marketplaces: number of active suppliers/experts/freelancers, engagement rate, quality scores, earnings, and geographic distribution. Uses custom objects for the supply side.
**Why it ranks high:** Marketplaces using Attio need supply-side analytics that the CRM UI does not provide. This is a generalized version of the Expert Network template.

### 19. Meeting & Interaction Logger
**Who:** AEs, Customer Success, BD
**What:** A streamlined interface for logging meetings with auto-populated attendee info from Attio. Quick-entry form for notes, next steps, and sentiment. Creates Attio notes and tasks automatically. Mobile-friendly for post-meeting logging.
**Why it ranks high:** Logging meetings in the CRM is the #1 hygiene task reps avoid. A fast, mobile-friendly logger reduces friction dramatically.

### 20. Territory & Account Assignment Map
**Who:** RevOps, Sales Managers
**What:** Visual map showing account assignments by territory/region with company data from Attio. Shows coverage gaps, account overlap between reps, and territory-level pipeline metrics. Supports reassignment workflows.
**Why it ranks high:** Territory management is a common RevOps need that no CRM handles well natively. Visual maps make assignment decisions intuitive.

---

## Template Categories

The 20 templates above group naturally into 5 categories:

### Category 1: Analytics & Reporting
Templates that aggregate CRM data into derived metrics, charts, and trend views that the native CRM UI cannot produce.

| Template | Complexity | Primary Persona |
|----------|-----------|-----------------|
| Pipeline Analytics Dashboard | Medium | RevOps / Founders |
| Sales Leaderboard | Low | Sales Managers |
| CRM Data Quality Audit | Medium | RevOps |
| Outbound Campaign Tracker | Medium | Growth / SDRs |
| Territory & Account Map | Medium-High | RevOps |

**Shared patterns:** Charts (bar, line, funnel), date range filters, aggregation logic, comparison periods.

### Category 2: Relationship & Account Intelligence
Templates that surface relationship context and account details in purpose-built views.

| Template | Complexity | Primary Persona |
|----------|-----------|-----------------|
| Pre-Call Prep Sheet | Low-Medium | AEs / SDRs |
| Deal Room / Deal Review | Medium | Sales Managers |
| Contact Relationship Map | High | AEs / BD |
| Customer Health Dashboard | Medium | CS / Founders |

**Shared patterns:** Record detail views, note timelines, relationship links, health scoring logic.

### Category 3: External Portals
Templates that expose a curated subset of CRM data to external parties (clients, investors, partners) through a branded, authenticated interface.

| Template | Complexity | Primary Persona |
|----------|-----------|-----------------|
| Client Portal | Medium-High | Agencies / Services |
| LP / Investor Portal | Medium-High | VC Fund Managers |

**Shared patterns:** External auth (magic link or password), branded theming, read-only data views, PDF/share export.

### Category 4: Workflow-Specific Views
Templates designed for a specific recurring workflow or meeting cadence.

| Template | Complexity | Primary Persona |
|----------|-----------|-----------------|
| Weekly Sales Standup View | Low | Sales Managers |
| Renewal & Expansion Tracker | Medium | CS / RevOps |
| Meeting & Interaction Logger | Low-Medium | AEs / CS |
| Recruiting Pipeline Dashboard | Medium | Founders / Hiring |
| Investor Update Generator | Medium | Founders |

**Shared patterns:** Kanban boards, calendar/timeline views, quick-entry forms, time-period navigation.

### Category 5: Network & Marketplace Performance
Templates for businesses that manage a network of partners, experts, freelancers, or suppliers and need to track their performance and economics.

| Template | Complexity | Primary Persona |
|----------|-----------|-----------------|
| Partner Performance Tracker | Medium | Partnerships/BD |
| Expert Network Dashboard | Medium | Network Operators |
| VC Deal Flow Pipeline | Medium | Investors |
| Marketplace Supply Dashboard | Medium | Marketplace Ops |
| Agency Retainer Dashboard | Medium | Agency Owners |

**Shared patterns:** Custom object mapping, commission/earnings calculations, performance scoring, multi-entity relationships.

---

## Detailed Template Specs

### Spec 1: Pipeline Analytics Dashboard

**Persona:** RevOps lead, Sales Manager, Founder at a 10-50 person SaaS startup
**Problem:** Attio shows deals in a list/kanban, but does not compute conversion rates between stages, show trends over time, or calculate pipeline coverage ratios. Teams export to spreadsheets for this analysis.

**Data Sources:**
- `GET /objects/deals/records/query` — all deals with stage, value, close date, owner
- `GET /objects/companies/records/query` — associated companies
- `GET /objects/people/records/query` — associated contacts
- Status attribute values for pipeline stages

**Key Views:**
1. **Funnel view** — conversion rate between each deal stage (e.g., Qualified -> Proposal: 45%)
2. **Pipeline value by stage** — stacked bar chart showing dollar amounts at each stage
3. **Velocity metrics** — average days in each stage, average deal cycle time
4. **Trends** — line charts showing deals created, won, lost over configurable time periods
5. **Win/Loss analysis** — win rate by source, by rep, by deal size
6. **Coverage ratio** — pipeline value vs. quota, current period vs. previous

**Filters:** Time period, deal owner, deal source, company segment, deal size range

**Complexity:** Medium (requires date math, stage transition calculations, charting)

---

### Spec 2: Sales Leaderboard

**Persona:** Sales Manager, VP Sales at a team with 3-20 AEs
**Problem:** No native way to see ranked rep performance. Managers cobble together metrics from multiple Attio views.

**Data Sources:**
- `GET /objects/deals/records/query` — deals filtered by owner and close date
- `GET /lists/{list_id}/entries` — list entries for activity tracking
- User records for team member info

**Key Views:**
1. **Leaderboard table** — reps ranked by closed revenue, with columns for deals won, average deal size, win rate
2. **Activity metrics** — meetings logged, emails sent, tasks completed (from interaction data)
3. **Time period toggle** — this week, this month, this quarter, custom range
4. **Trend sparklines** — mini charts showing each rep's trajectory
5. **TV mode** — full-screen auto-rotating display for office monitors

**Filters:** Time period, team, metric (revenue, deals, activity)

**Complexity:** Low (aggregation queries + ranked display)

---

### Spec 3: Pre-Call Prep Sheet

**Persona:** AE or SDR preparing for a sales call
**Problem:** Before every call, reps spend 5-15 minutes manually pulling info from the CRM, LinkedIn, and the web. This is repetitive and error-prone.

**Data Sources:**
- `GET /objects/people/records/{record_id}` — contact details
- `GET /objects/companies/records/{record_id}` — company details
- `GET /notes` — recent notes on the contact/company
- `GET /tasks` — open tasks related to the record
- `GET /objects/deals/records/query` — deals involving this contact
- List entries for interaction history

**Key Views:**
1. **Contact brief** — name, title, company, LinkedIn, recent interactions
2. **Company snapshot** — industry, size, recent news, other contacts at the company
3. **Deal context** — current deal stage, value, next steps, competitor mentions
4. **Interaction timeline** — last 5 touchpoints with notes
5. **Suggested talking points** — based on deal stage and contact role
6. **One-page printable/shareable format**

**Filters:** Contact picker / search

**Complexity:** Low-Medium (data assembly from multiple endpoints, formatting)

---

### Spec 4: Customer Health Dashboard

**Persona:** Customer Success Manager, Founder at a SaaS company
**Problem:** No single view of account health across the customer base. Health signals are scattered across deal records, notes, interactions, and external tools.

**Data Sources:**
- `GET /objects/deals/records/query` — customer deals (closed-won, active)
- `GET /objects/companies/records/query` — customer companies
- `GET /notes` — notes per company (recency = engagement signal)
- `GET /lists/{list_id}/entries` — list entries with custom health attributes
- Interaction attribute data for last-contact dates

**Key Views:**
1. **Health grid** — all customers in a sortable table with traffic-light health scores
2. **Health score breakdown** — configurable weights for: days since last interaction, deal value, NPS (if tracked), support activity, product usage
3. **At-risk accounts** — filtered view of red/yellow accounts with recommended actions
4. **Trend view** — health score changes over last 30/60/90 days
5. **Account drill-down** — detailed view of any account's health signals

**Filters:** Health status, CSM owner, customer segment, deal value range, renewal date

**Complexity:** Medium (health scoring logic, configurable weights, multiple data sources)

---

### Spec 5: CRM Data Quality Audit

**Persona:** RevOps lead, Operations Manager
**Problem:** CRM data degrades over time. Missing fields, duplicates, and stale records accumulate silently. Teams discover data quality issues when a report looks wrong.

**Data Sources:**
- `GET /objects` — list all objects and their attributes
- `GET /objects/{object_id}/records/query` — records for each object
- `GET /objects/{object_id}/attributes` — attribute definitions for completeness checks

**Key Views:**
1. **Overall health score** — percentage across completeness, freshness, duplication
2. **Completeness report** — records missing critical fields, grouped by object type
3. **Duplicate detection** — potential duplicates by email, name+company, phone
4. **Staleness report** — records with no interaction in 30/60/90+ days
5. **Orphan report** — contacts not linked to any company, deals not linked to contacts
6. **Fix-it queue** — actionable list of records to clean up, sortable by severity

**Filters:** Object type, severity level, attribute, date range

**Complexity:** Medium (requires iterating over all records, fuzzy matching logic)

---

### Spec 6: Investor Update Generator

**Persona:** Startup Founder / CEO sending monthly updates to investors
**Problem:** Founders manually compile metrics from Attio, Stripe, and spreadsheets into investor update emails. This takes 2-4 hours per month.

**Data Sources:**
- `GET /objects/deals/records/query` — deals closed, pipeline value
- `GET /objects/companies/records/query` — new customers
- `GET /objects/people/records/query` — new contacts/relationships
- Manual input fields for: MRR, burn rate, runway, headcount, key wins, asks

**Key Views:**
1. **Metrics dashboard** — CRM-derived metrics (new deals, pipeline, customers) alongside manually-entered financial metrics
2. **Update editor** — structured template with sections: Highlights, Metrics, Product, Team, Asks
3. **Historical comparison** — this month vs. last month vs. 3 months ago
4. **Preview & export** — clean formatted output suitable for email, PDF, or shareable link
5. **Archive** — searchable history of past updates

**Filters:** Time period for the update

**Complexity:** Medium (template engine, PDF generation, data aggregation)

---

### Spec 7: Client Portal

**Persona:** Agency owner, Professional Services firm
**Problem:** Clients constantly ask "where are we on X?" Agencies send manual updates or give clients direct CRM access (which exposes too much). Need a branded, curated external view.

**Data Sources:**
- `GET /lists/{list_id}/entries` — project/engagement list entries
- `GET /objects/companies/records/{record_id}` — client company details
- `GET /notes` — project update notes
- `GET /tasks` — deliverables and milestones
- Custom object records for projects, deliverables, retainers

**Key Views:**
1. **Login/auth** — magic link or password-based client authentication
2. **Project overview** — active projects with status, timeline, deliverables
3. **Deliverable tracker** — checklist of deliverables with status and due dates
4. **Communication log** — recent notes and updates (curated, not raw CRM notes)
5. **Team contacts** — who to reach out to, with role and contact info
6. **Branding** — client's logo and colors, or agency's white-labeled branding

**Filters:** Client scoping (each client sees only their data)

**Complexity:** Medium-High (external auth, data scoping/security, branding system)

---

### Spec 8: VC Deal Flow Pipeline

**Persona:** VC Partner, Associate, Principal
**Problem:** Attio's generic kanban works, but VC deal flow has unique needs: co-investor tracking, founder bios, investment thesis tagging, memo storage, and source attribution. A purpose-built view accelerates investment decisions.

**Data Sources:**
- `GET /objects/deals/records/query` — deals representing potential investments
- `GET /objects/people/records/query` — founders
- `GET /objects/companies/records/query` — portfolio companies and prospects
- `GET /notes` — investment memos, meeting notes
- Custom objects for funds, co-investors, board seats

**Key Views:**
1. **Deal flow kanban** — stages: Sourced, First Meeting, Deep Dive, DD, Term Sheet, Closed, Passed
2. **Company card** — one-page snapshot with team, traction metrics, thesis fit
3. **Source tracking** — which deals came from which partners, LPs, events, or inbound
4. **Co-investor view** — who else is looking at or invested in each deal
5. **Portfolio dashboard** — funded companies with latest metrics and follow-on status
6. **Weekly pipeline review** — meeting-ready view of new and active deals

**Filters:** Fund, stage, sector, deal size, lead partner, source

**Complexity:** Medium (multiple custom objects, rich relationship views)

---

## Expert Network Deep Dive

This section fleshes out the user's specific use case into a complete template specification.

### Context

The user operates an expert network tracked in Attio using custom objects. Experts are people (or custom objects) who are associated with deals at various stages. The business needs to understand:
- Which experts are generating the most deal flow
- What is the quality of their deals (conversion through stages)
- How much revenue each expert has generated
- What each expert has earned

This pattern generalizes to: **any business that has a network of people (experts, partners, affiliates, freelancers, advisors) who generate or influence deals.**

### Data Model in Attio

```
Expert (Custom Object)
  - Name
  - Email
  - Expertise areas (multi-select)
  - Region (select)
  - Status (Active, Inactive, Onboarding)
  - Joined date
  - Commission rate (number/currency)
  - Linked Deals (record reference -> Deals)
  - Linked Company (record reference -> Companies)

Deal (Standard Object)
  - Name
  - Value (currency)
  - Stage (status: Qualified, Proposal, Negotiation, Closed Won, Closed Lost)
  - Close date
  - Associated Expert (record reference -> Expert)
  - Associated Company (record reference -> Companies)
  - Commission amount (currency, computed or manual)
```

### Attio API Resources Used

| Endpoint | Purpose |
|----------|---------|
| `GET /objects` | Discover custom objects (find the Expert object) |
| `GET /objects/{expert_object_id}/records/query` | List all experts with filtering |
| `GET /objects/{expert_object_id}/attributes` | Get expert attribute definitions |
| `GET /objects/deals/records/query` | List all deals with stage, value, expert reference |
| `GET /objects/deals/attributes` | Get deal attribute definitions including stage options |
| `GET /objects/companies/records/query` | Company details for deal context |
| `GET /notes` | Notes on expert or deal records |

### Dashboard Views

#### View 1: Network Overview
A top-level summary of the entire expert network.

**Metrics:**
- Total active experts
- Total deals generated (all time / this period)
- Total pipeline value (open deals)
- Total revenue (closed-won deals)
- Total expert earnings (commissions paid/owed)
- Average deals per expert
- Network growth (new experts over time)

**Visualization:** KPI cards at top, line chart of deals and revenue over time, bar chart of new experts per month.

#### View 2: Expert Leaderboard
Ranked table of all experts by performance.

**Columns:**
- Expert name
- Deals generated (count)
- Deals qualified (count)
- Deals won (count)
- Win rate (%)
- Revenue generated ($)
- Pipeline value (open deals $)
- Earnings ($)
- Avg deal size ($)
- Last deal date

**Sorting:** By any column. Default: revenue generated, descending.
**Filters:** Time period, expertise area, region, status.

#### View 3: Expert Detail Page
Drill-down view for a single expert.

**Sections:**
1. **Expert profile** — name, contact info, expertise, region, status, join date
2. **Performance summary** — KPI cards for deals, revenue, earnings, win rate
3. **Deal pipeline** — all deals associated with this expert, grouped by stage
4. **Revenue timeline** — chart of revenue generated over time
5. **Earnings tracker** — commissions earned, pending, and paid
6. **Notes & interactions** — recent notes and activity on this expert's records

#### View 4: Deal Stage Funnel (by Expert or Overall)
Funnel visualization showing how deals flow through stages.

**For the whole network:**
- Total deals at each stage
- Conversion rate between stages
- Average time in each stage
- Value at each stage

**Per expert:**
- Same metrics filtered to a single expert
- Comparison to network averages

#### View 5: Earnings & Payouts
Financial view focused on expert compensation.

**Columns:**
- Expert name
- Deals closed this period
- Revenue generated
- Commission rate
- Earnings (computed)
- Earnings YTD
- Payment status (if tracked)

**Summary:** Total earnings owed, total paid, total outstanding.

### Generalized Patterns

This template generalizes into a **"Network Performance"** template that works for:

| Business Type | "Expert" Object | "Deal" Concept | Key Metrics |
|---------------|-----------------|----------------|-------------|
| Expert network | Expert/Consultant | Consulting engagement | Revenue, hours, client satisfaction |
| Referral program | Referral partner | Referred deal | Deals referred, conversion rate, payouts |
| Affiliate network | Affiliate | Attributed sale | Clicks, conversions, commission |
| Talent marketplace | Freelancer/Contractor | Placement/Gig | Placements, fill rate, earnings |
| VC operating partners | Operating partner | Portfolio engagement | Companies supported, outcomes |
| Consulting firm | Associate/Contractor | Project | Utilization, revenue, client rating |
| Advisory network | Advisor | Advisory engagement | Sessions, deals influenced, fees |
| Channel sales | Channel partner | Channel deal | Partner-sourced revenue, deal reg |

The template should allow the user to **map their custom objects** to the template's data model during setup. A configuration step like:

```
Which object represents your network members? → [Expert]
Which object represents engagements/deals? → [Deal]
Which attribute links them? → [Associated Expert]
Which attribute is the value? → [Deal Value]
Which attribute is the stage? → [Deal Stage]
```

This makes the template reusable across all network/marketplace patterns.

---

## Technical Patterns & Shared Components

Building 20 templates from scratch would be wasteful. These templates share significant common infrastructure. Here is what the shared component library needs.

### Authentication & Data Layer

#### `useAttioAuth()` — OAuth Hook
- Handles the full OAuth 2.0 flow with Attio
- Stores access token securely (httpOnly cookie or encrypted localStorage)
- Handles token refresh
- Provides workspace context (workspace ID, user info)
- Scopes: configurable per template

#### `useAttioClient()` — API Client
- Wraps fetch/axios with auth headers
- Handles pagination automatically (`offset`/`limit` with cursor-based fallback)
- Rate limiting awareness (respects 429 responses)
- Error handling with typed error responses
- Caching layer (SWR or React Query)

#### `useAttioRecords(objectSlug, options)` — Generic Record Fetcher
- Fetches records for any object (standard or custom)
- Supports filtering (Attio's filter syntax)
- Supports sorting
- Auto-paginates with `--all` equivalent
- Returns typed records with attribute values resolved

#### `useAttioDeal()` / `useAttioPeople()` / `useAttioCompanies()` — Typed Hooks
- Convenience wrappers around `useAttioRecords` for standard objects
- Pre-typed with known attributes (name, email, stage, value, etc.)
- Include relationship resolution (e.g., deal -> associated company)

#### `useAttioSchema()` — Schema Discovery
- Fetches object definitions and attribute schemas
- Essential for templates that work with custom objects
- Caches schema for the session
- Powers dynamic form generation and field mapping

#### `useAttioNotes(recordId)` — Notes Fetcher
- Fetches notes for a specific record
- Supports pagination
- Parses note content (Attio uses a rich text format)

#### `useAttioTasks(options)` — Task Fetcher
- Fetches tasks with filtering by assignee, status, linked record
- Supports task creation

### UI Components

#### Data Display
- **`<DataTable />`** — Sortable, filterable table with pagination. Supports column configuration, row click handlers, and inline editing. Used by: Leaderboard, Health Dashboard, Data Quality Audit, Expert Leaderboard.
- **`<KPICard />`** — Single metric display with label, value, trend indicator (up/down arrow + percentage), and optional sparkline. Used by: every dashboard template.
- **`<RecordCard />`** — Compact card view of a CRM record (person, company, deal) with key attributes and action buttons. Used by: Prep Sheet, Deal Room, Contact Map.
- **`<Timeline />`** — Chronological list of interactions, notes, and events. Used by: Prep Sheet, Deal Room, Expert Detail.
- **`<StatusBadge />`** — Colored badge for deal stages, health scores, and statuses. Used by: Pipeline Dashboard, Health Dashboard, Recruiting Pipeline.

#### Charts
- **`<FunnelChart />`** — Pipeline conversion funnel. Used by: Pipeline Analytics, Expert Network Funnel.
- **`<BarChart />`** — Horizontal or vertical bars. Used by: Leaderboard, Pipeline by Stage, Territory Map.
- **`<LineChart />`** — Time-series trends. Used by: Pipeline Trends, Revenue Over Time, Health Trends.
- **`<DonutChart />`** — Proportional breakdowns. Used by: Win/Loss Analysis, Source Attribution, Stage Distribution.
- **`<Sparkline />`** — Tiny inline chart for table cells. Used by: Leaderboard Trends, Health Score History.

Recommended charting library: **Recharts** (React-native, composable, good defaults) or **Tremor** (built for dashboards, includes pre-styled metric cards).

#### Filters & Controls
- **`<DateRangePicker />`** — Period selection with presets (This Week, This Month, This Quarter, Custom). Used by: nearly every template.
- **`<ObjectPicker />`** — Search-and-select for Attio records (people, companies, custom objects). Backed by `useAttioRecords` with search. Used by: Prep Sheet, Deal Room, Expert Detail.
- **`<AttributeFilter />`** — Dynamic filter builder based on Attio attribute types (status, select, number range, date range). Used by: Data Quality Audit, any filterable view.
- **`<FieldMapper />`** — UI for mapping custom object attributes to template expectations. Used during template setup for custom object templates (Expert Network, Marketplace, etc.).

#### Layout
- **`<DashboardLayout />`** — Responsive grid layout with sidebar navigation, header with workspace info, and content area. Supports dark mode.
- **`<TVMode />`** — Full-screen, auto-rotating display mode for leaderboards and dashboards on office monitors.
- **`<PrintLayout />`** — Clean, print-optimized layout for prep sheets and investor updates.
- **`<PortalLayout />`** — External-facing layout with branding slots (logo, colors) and simplified navigation for client/investor portals.

### Template Configuration System

Every template should support a configuration step that runs on first launch:

1. **Object mapping** — which Attio objects correspond to the template's data model
2. **Attribute mapping** — which attributes map to expected fields (e.g., "which attribute is deal value?")
3. **Defaults** — default filters, time periods, and display preferences
4. **Branding** — logo, colors, company name (especially for portal templates)

This configuration should be stored in the app's local storage or a lightweight backend, and be editable from a settings page.

### Recommended Tech Stack

| Layer | Recommendation | Rationale |
|-------|---------------|-----------|
| Framework | **Next.js** (App Router) | SSR for portals, API routes for OAuth callbacks, file-based routing |
| Styling | **Tailwind CSS** + **shadcn/ui** | Fast iteration, consistent design system, accessible components |
| Charts | **Recharts** or **Tremor** | React-native, composable, dashboard-optimized |
| Data fetching | **TanStack Query** (React Query) | Caching, refetching, pagination, optimistic updates |
| Auth | **NextAuth.js** with custom Attio provider | OAuth flow handling, session management, CSRF protection |
| State | **Zustand** | Lightweight, template configuration state |
| Export | **@react-pdf/renderer** or **html2canvas** | PDF generation for investor updates, prep sheets |
| Deployment | **Vercel** | Zero-config Next.js deployment, edge functions |

### Scaffolding CLI Integration

Since this project already has an `attio-cli`, the template library should integrate with it:

```bash
# List available templates
attio templates list

# Scaffold a new app from a template
attio templates create --template pipeline-dashboard --name my-dashboard

# This would:
# 1. Clone the template
# 2. Run the object/attribute mapping wizard
# 3. Set up OAuth credentials
# 4. Install dependencies
# 5. Start the dev server
```

### API Scope Requirements by Template

| Template | Required Scopes |
|----------|----------------|
| Pipeline Analytics | `record_permission:read`, `object_configuration:read` |
| Sales Leaderboard | `record_permission:read`, `object_configuration:read`, `user_management:read` |
| Pre-Call Prep Sheet | `record_permission:read`, `object_configuration:read`, `note:read`, `task:read` |
| Customer Health | `record_permission:read`, `object_configuration:read`, `note:read` |
| Data Quality Audit | `record_permission:read`, `object_configuration:read` |
| Investor Update | `record_permission:read`, `object_configuration:read` |
| Client Portal | `record_permission:read`, `object_configuration:read`, `note:read`, `task:read` |
| Expert Network | `record_permission:read`, `object_configuration:read`, `note:read` |
| VC Deal Flow | `record_permission:read`, `object_configuration:read`, `note:read` |
| Meeting Logger | `record_permission:read-write`, `note:read-write`, `task:read-write` |

---

## Implementation Priority

Based on breadth of appeal, build complexity, and the ability to demonstrate the template system's value:

### Phase 1: Foundation + 3 Templates
1. Shared component library (auth, data hooks, UI components)
2. **Pipeline Analytics Dashboard** — the universal first app
3. **Sales Leaderboard** — simple, high engagement, great demo
4. **Expert Network Dashboard** — solves the user's immediate need, showcases custom object support

### Phase 2: Expand Persona Coverage
5. **Pre-Call Prep Sheet** — serves AEs, simple but high-value
6. **Customer Health Dashboard** — serves CS teams
7. **CRM Data Quality Audit** — serves RevOps

### Phase 3: Portals + Industry-Specific
8. **Client Portal** — first external-facing template, unlocks agency segment
9. **VC Deal Flow Pipeline** — serves the VC segment
10. **Investor Update Generator** — serves founders

### Phase 4: Full Library
11-20. Remaining templates, prioritized by user demand signals.

---

## Appendix: Competitive Reference

### What Retool Offers
Retool's template library includes: Custom CRM, CRM Dashboard, HubSpot CRM Dashboard, Field Sales App, Real Estate CRM, B2B CRM. Their templates are drag-and-drop internal tools, not deployable standalone apps. Our advantage: purpose-built for Attio, deployable as standalone web apps, and scaffoldable from a CLI.

### What Salesforce AppExchange Shows
The AppExchange has 9,000+ apps with 10M+ installs. The Analytics category alone has 475 apps (8.4% of all apps). Top categories: dashboards/reporting, data quality, sales productivity, document generation. This validates that reporting and analytics apps are the highest-demand category for CRM ecosystems.

### What the VC CRM Market Shows
Dedicated VC CRMs (Affinity, 4Degrees, Edda, Dialllog) charge $500-2,000/user/month for features that could be built as Attio templates: deal flow management, LP reporting, portfolio monitoring, co-investor tracking. This represents a significant value unlock for VC firms already using Attio.

---

## Sources

- [Attio Customers](https://attio.com/customers)
- [Attio Developer Platform](https://attio.com/platform/developers)
- [Attio Docs: OAuth](https://docs.attio.com/rest-api/tutorials/connect-an-app-through-oauth)
- [Attio Docs: Objects and Lists](https://docs.attio.com/docs/objects-and-lists)
- [Attio Docs: Filtering and Sorting](https://docs.attio.com/rest-api/guides/filtering-and-sorting)
- [Attio Docs: Webhooks](https://docs.attio.com/rest-api/guides/webhooks)
- [Attio Docs: App SDK Overview](https://docs.attio.com/sdk/deep-dives/overview)
- [Modal Case Study](https://attio.com/customers/modal)
- [Retool Templates](https://retool.com/templates)
- [Salesforce AppExchange: Dashboards & Reporting](https://appexchange.salesforce.com/category/dashboards-and-reporting-apps)
- [CRM Dashboards: Real-Time KPIs (Monday.com)](https://monday.com/blog/crm-and-sales/crm-dashboards/)
- [10 Must-Have Sales Dashboards (Highspot)](https://www.highspot.com/blog/sales-dashboards/)
- [Customer Health Dashboard (JoySuite)](https://www.joysuite.com/workflows/health-score-dashboard/)
- [Pre-Call Research Brief (Amplemarket)](https://www.amplemarket.com/skills/pre-call-research-brief)
- [Investor-Ready SaaS Metrics 2026](https://consultefc.com/investor-ready-saas-metrics/)
- [Marketplace Metrics (Sharetribe)](https://www.sharetribe.com/academy/measure-your-success-key-marketplace-metrics/)
- [Best CRM for Venture Capital (Dialllog)](https://dialllog.co/best-crm-for-venture-capital)
- [CRM Data Quality Audit Guide (Cleanlist)](https://www.cleanlist.ai/blog/2026-03-02-how-to-audit-crm-data-quality)
- [Client Portals Buying Guide (WeWeb)](https://www.weweb.io/blog/client-portals-buying-guide)
- [Attio CRM Review (Hackceleration)](https://hackceleration.com/attio-review/)
- [Ultimate Guide to Attio CRM (ClonePartner)](https://clonepartner.com/blog/ultimate-guide-attio-crm-2025)
