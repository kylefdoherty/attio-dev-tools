# Attio CLI -- Research & Architecture Blueprint

> Generated 2026-05-15. This document is the comprehensive blueprint for building a best-in-class CLI for the Attio CRM API, designed to serve both human developers and AI coding agents as first-class citizens.

---

## Table of Contents

1. [Best Practices from Top CLIs](#1-best-practices-from-top-clis)
2. [Agent-Friendly CLI Design](#2-agent-friendly-cli-design)
3. [Proposed Command Structure](#3-proposed-command-structure)
4. [Output Strategy](#4-output-strategy)
5. [Auth & Config Strategy](#5-auth--config-strategy)
6. [Technical Architecture](#6-technical-architecture)
7. [Killer Features](#7-killer-features)
8. [MCP Server Potential](#8-mcp-server-potential)

---

## 1. Best Practices from Top CLIs

### 1.1 GitHub CLI (`gh`) -- The Gold Standard

**What makes it exceptional:**

- **Noun-verb command structure**: `gh pr create`, `gh issue list`, `gh repo clone`. The resource comes first, then the action. This is discoverable -- you can explore `gh pr --help` to see all PR operations.
- **`--json` with `--jq`**: Every data-returning command supports `--json` to select specific fields and `--jq` for inline filtering. Example: `gh pr list --json number,title --jq '.[] | select(.title | contains("fix"))'`. This is the single most important feature for agent and scripting workflows.
- **Intelligent defaults**: `gh pr create` auto-fills the title from the branch name and body from commit messages. Zero-arg commands do the most obvious thing.
- **`gh api` escape hatch**: Direct REST/GraphQL access with full auth, pagination (`--paginate`), and jq integration. When the CLI doesn't cover a use case, you never have to leave it.
- **Auth via browser OAuth**: `gh auth login` opens a browser, completes OAuth, stores the token in the OS keychain. Environment variable `GH_TOKEN` overrides for CI/headless.
- **Multi-account switching**: `gh auth switch -u <username>` enables workspace switching.
- **Extension system**: Third-party commands integrate as `gh <extension>` subcommands.
- **Aliases**: `gh alias set` lets users define shortcuts for complex command chains.

**Patterns to adopt**: Noun-verb structure, `--json` everywhere, `--jq` integration, browser-based auth with env var override, `api` escape hatch command.

### 1.2 Stripe CLI

**What makes it exceptional:**

- **Resource CRUD mirroring the API**: `stripe customers create --name="Jane"`, `stripe charges list`. Every API resource is a command group, every API action is a subcommand. This 1:1 mapping means anyone who knows the API can use the CLI.
- **Real-time event streaming**: `stripe listen` opens a WebSocket to stream webhook events to your terminal, with `--forward-to` to proxy them to a local server. This is killer for development workflows.
- **`stripe logs tail`**: Live-stream API request logs with filtering by status code, method, or path. Debug production issues in real time.
- **`stripe trigger`**: Fire test webhook events to exercise your integration without setting up real data.
- **Test mode vs live mode**: Clear separation via `--api-key` flag, preventing accidental production mutations.
- **Agent-forward updates (2025-2026)**: Added `--map` flag for recursive command tree, agent guidance in help output, and fast-fail on auth errors in non-interactive contexts. Stripe is actively adapting their CLI for agent consumption.

**Patterns to adopt**: 1:1 API-to-CLI resource mapping, real-time streaming commands (listen, logs tail), test event triggering, explicit agent-mode support.

### 1.3 Vercel CLI

**What makes it exceptional:**

- **Zero-config deployment**: `vercel` with no arguments deploys the current directory. Progressive disclosure -- simple tasks are simple, complex tasks are possible.
- **Non-interactive / agentic mode**: Dedicated ActionRequiredPayload and AgentErrorPayload interfaces for structured agent communication. `--format json` for all output. `-y` to bypass all confirmations.
- **Team switching**: `vercel switch` or `--team <slug>` per-command. Clean multi-context support.
- **`VERCEL_TOKEN` env var**: Token-based auth for CI/CD without interactive login.
- **SKILL.md files**: Vercel publishes agent skills that describe CLI usage patterns for AI agents -- a pioneering approach.

**Patterns to adopt**: Zero-config happy path, dedicated non-interactive mode, SKILL.md for agent discovery, team/workspace switching.

### 1.4 Railway CLI

**What makes it exceptional:**

- **Interactive project linking**: `railway link` uses a fuzzy-search interactive picker to connect local directories to remote projects. Beautiful TUI experience.
- **Environment-aware execution**: `railway run <command>` injects environment variables from the linked service, creating a local dev environment that mirrors production.
- **`railway shell`**: Opens a subshell with all service env vars loaded.

**Patterns to adopt**: Interactive project/workspace linking with fuzzy search, environment-aware command execution.

### 1.5 Supabase CLI

**What makes it exceptional:**

- **Secure credential storage**: Tokens stored in native OS credentials storage, with plain-text fallback and clear warning.
- **Auth hooks configuration**: Comprehensive auth customization from CLI.
- **DB branching**: Environment branching for development workflows.

**Patterns to adopt**: Native credential storage with fallback, branch-aware workflows.

### 1.6 Fly.io CLI (`flyctl`)

**What makes it exceptional:**

- **Pervasive `--json`**: Supported on app, machine, status, log, secret, certificate, org, volume, and virtually every other command.
- **`fly.toml` discovery**: Local config file discovery for project-scoped settings, similar to how git finds `.git/`.
- **Cobra-based architecture**: Same framework as Docker, Kubernetes -- familiar command/subcommand patterns.

**Patterns to adopt**: Config file discovery for project-scoped defaults, comprehensive JSON support.

### 1.7 Key Lessons from `jq`

jq became essential to the CLI ecosystem because it solved a fundamental problem: CLI tools produce JSON, but humans and scripts need to transform it. Key design lessons:

- **Every filter is composable**: The pipe `|` operator lets you chain transformations. CLIs should produce output that composes well with jq.
- **`-r` for raw strings**: When piping to other tools, you need unquoted output. CLIs should offer equivalent raw/plain modes.
- **`-c` for compact output**: One JSON object per line (JSONL) is the standard for streaming and piping.
- **Color auto-detection**: Colored output to terminal, plain output when piped.

**Implication for our CLI**: Produce clean JSON that works seamlessly with jq. Consider offering a built-in `--jq` filter flag like `gh` does, so users don't need jq installed separately.

### 1.8 SalesNexus CLI (`snx`) -- CRM-Specific Lessons

The closest existing CRM CLI to what we're building:

- **Comprehensive resource coverage**: contacts, opportunities, tasks, notes, goals, pipelines, fields, templates, reports -- all as command groups.
- **Pipeline commands**: Chainable one-liners for complex CRM workflows: `snx contacts list --all --json | jq '[.data[] | select(.state=="TX")]'`.
- **Bulk operation support**: Process hundreds of records in batch from the command line.

**Patterns to adopt**: Full CRM resource coverage, pipeline-friendly output, bulk operation support.

---

## 2. Agent-Friendly CLI Design

This is the most critical differentiator for this CLI. The research reveals a maturing ecosystem of agent-CLI interaction patterns that we must implement from day one, not bolt on later.

### 2.1 The Agent-First Paradigm Shift

The research overwhelmingly supports a key insight: **design for agents first, and humans benefit automatically**. Agent-friendly design produces better CLIs for everyone because agents demand the properties that make CLIs reliable: predictable output, clear errors, non-interactive operation, and composable commands.

Key statistics backing this approach:
- 78% of professional developers spend more than half their workday in a terminal (Stack Overflow 2025)
- CLI-based agents achieve 100% reliability vs MCP's 72% in comparative studies
- CLIs are 10-32x cheaper on tokens than MCP for equivalent tasks
- AXI-style CLIs achieve 100% success at $0.074/task vs $0.100/task for MCP

### 2.2 The 10 Core Principles (Synthesized from Research)

Drawing from Trevin Chow's 10 Principles, InfoQ's patterns article, the AXI framework, the OpenStatus blog, and clig.dev:

#### Principle 1: Non-Interactive by Default
- Every command must be fully operable without any prompts when `stdin` is not a TTY.
- `--yes` / `--force` / `--no-input` flags bypass all confirmation prompts.
- TTY detection determines interactive vs scripted mode automatically.
- The "wizard fallback" pattern: if required flags are missing AND stdin is a TTY, launch an interactive wizard. If non-TTY, return a structured error listing the exact missing flags.

#### Principle 2: Structured Output Everywhere
- `--json` flag on every data-returning command. No exceptions.
- JSON output is a **parallel code path** that returns complete data, including fields the human table omits.
- `--json` routes data to stdout; progress indicators, spinners, warnings go to stderr.
- ANSI codes suppressed when stdout is not a TTY (auto-detect) or when `NO_COLOR` is set.
- One consistent flag name: always `--json`, never `--format=json` on some commands and `--output json` on others.

#### Principle 3: Errors That Teach
- Every error includes: what went wrong, why, and what to do next.
- When rejecting invalid input against an enum, surface the valid set: `error: --status must be one of: open, won, lost (got: 'active')`.
- Structured JSON errors when `--json` is active: `{"error": {"type": "validation_error", "message": "...", "field": "status", "valid_values": ["open", "won", "lost"], "suggestion": "..."}}`.
- Distinguish transient errors (retry-worthy) from permanent ones via error type codes.

#### Principle 4: Semantic Exit Codes
- `0` = success
- `1` = general/unknown error
- `2` = usage/argument error (wrong flags, missing required args)
- `3` = authentication error (bad/missing API key)
- `4` = permission denied (valid auth but insufficient scopes)
- `5` = resource not found
- `6` = conflict (resource already exists, version mismatch)
- `7` = rate limited (with retry-after info in stderr)
- `8` = validation error (API rejected the request body)

Agents need to branch on failure modes without parsing error messages.

#### Principle 5: Idempotent and Safe
- Mutations should be retryable. `attio records upsert` is inherently idempotent.
- `--dry-run` on all write operations shows what would change without doing it.
- Create operations return the existing resource with an `"existing": true` field on conflict rather than failing.
- All mutation responses include the resource ID for verification.

#### Principle 6: Bounded Responses
- Default list limits to 25 items (not unbounded).
- Include `"truncated": true` and total count in JSON output.
- Provide `--limit`, `--offset`, and `--all` flags for pagination control.
- `--fields` flag to select specific attributes, reducing token consumption.

#### Principle 7: Consistent Vocabulary
Following Cloudflare's enforced consistency:
- Always `list`, never `ls` or `index`
- Always `get`, never `show` or `info` or `describe`
- Always `create`, never `add` or `new`
- Always `update`, never `edit` or `modify`
- Always `delete`, never `remove` or `rm` or `destroy`
- Always `--json`, never `--format json`
- Always `--force`, never `--skip-confirmations`
- Always `--limit`, never `--count` or `--max`

#### Principle 8: Three-Layer Introspection
- **Layer 1 (Human-readable)**: `--help` on every command with examples, flag descriptions, and required scopes.
- **Layer 2 (Machine-readable)**: `attio agent-context` command returning versioned JSON schema of all commands, flags, types, and enums. This is what agents parse to understand capabilities.
- **Layer 3 (Skill manifests)**: SKILL.md files describing composition patterns, multi-step workflows, and CRM-specific recipes.

#### Principle 9: Contextual Next Steps
After every operation output, append "help lines" suggesting logical next commands. Example:
```
Created company "Acme Corp" (id: abc123)

Next steps:
  attio records get companies abc123             # View full details
  attio notes create --record=abc123 --body="…"  # Add a note
  attio entries create --list=pipeline --record=abc123  # Add to pipeline
```

In `--json` mode, include these as a `"next_actions"` array in the response.

#### Principle 10: Profile-Based State
- `attio profile save <name> --api-key=... --workspace=...`
- `attio profile use <name>` sets the active profile.
- `--profile <name>` per-command override.
- Profiles discoverable via `agent-context` so agents know what workspaces are available.
- Precedence: explicit flag > environment variable > active profile > default.

### 2.3 How AI Agents Consume CLIs

Based on research into Claude Code, Cursor, Codex CLI, and other agent frameworks:

**Discovery**: Agents run `attio --help` and `attio <group> --help` to discover capabilities. The help text must be concise, example-rich, and parseable. The `agent-context` command provides a structured alternative.

**Execution**: Agents construct CLI commands programmatically and execute them via shell. They parse stdout for results and stderr for diagnostics. They branch on exit codes.

**Chaining**: Agents pipe output between commands: `attio records list people --json --limit=5 | jq '.[].id'` then loop over results. JSONL output enables streaming pipelines.

**Verification**: Agents don't trust a single command's success. They follow up with get/list commands to verify state changes actually happened.

**Retry**: Agents retry on transient errors (rate limits, network issues). Semantic exit codes let them distinguish retryable from permanent failures.

**Authentication**: Agents prefer environment variables (`ATTIO_API_KEY`) over interactive login flows. They cannot open browsers or type at prompts.

### 2.4 AGENTS.md and SKILL.md Integration

The CLI package should ship with:
- `AGENTS.md` at the package root describing build/test/lint commands and CLI conventions.
- `SKILL.md` files for agent skill marketplaces describing CRM workflow recipes.
- An `attio agent-context` command that outputs structured JSON describing all available commands, flags, and their types.

---

## 3. Proposed Command Structure

### 3.1 Design Philosophy

**Noun-verb, two levels deep**: `attio <resource> <action>`. This mirrors the Attio API structure and is the most discoverable pattern for both humans and agents. It matches how gh, stripe, and aws structure their CLIs.

**Standard objects get first-class commands**: People, companies, and deals are the bread and butter of CRM work. They get their own top-level command groups even though they delegate to the generic records system underneath.

### 3.2 Complete Command Tree

```
attio
├── auth
│   ├── login              # Interactive browser OAuth or API key input
│   ├── logout             # Remove stored credentials
│   ├── status             # Show current auth state, workspace, scopes
│   ├── switch             # Switch between saved profiles/workspaces
│   └── token              # Print current token (for piping to other tools)
│
├── config
│   ├── get <key>          # Get a config value
│   ├── set <key> <value>  # Set a config value
│   ├── list               # List all config values
│   └── path               # Print config file path
│
├── profile
│   ├── list               # List saved profiles
│   ├── save <name>        # Save current auth as named profile
│   ├── use <name>         # Set active profile
│   ├── show <name>        # Show profile details
│   └── delete <name>      # Delete a profile
│
├── people                 # Convenience alias for records --object=people
│   ├── list               # List people (--filter, --sort, --limit, --offset, --all, --fields)
│   ├── get <id>           # Get a person by ID
│   ├── create             # Create a person (--name, --email, --values JSON)
│   ├── update <id>        # Update a person
│   ├── upsert             # Create or update by matching attribute
│   ├── delete <id>        # Delete a person
│   ├── search <query>     # Full-text search across people
│   └── export             # Export to CSV/JSON file (--format, --file)
│
├── companies              # Same structure as people
│   ├── list
│   ├── get <id>
│   ├── create
│   ├── update <id>
│   ├── upsert
│   ├── delete <id>
│   ├── search <query>
│   └── export
│
├── deals                  # Same structure as people, plus pipeline operations
│   ├── list
│   ├── get <id>
│   ├── create
│   ├── update <id>
│   ├── upsert
│   ├── delete <id>
│   ├── search <query>
│   ├── export
│   └── move <id> <stage>  # Move deal to a pipeline stage (convenience)
│
├── records                # Generic records for any object (including custom objects)
│   ├── list               # --object=<slug> required
│   ├── get <id>           # --object=<slug> required
│   ├── create
│   ├── update <id>
│   ├── upsert
│   ├── delete <id>
│   ├── search <query>
│   ├── values <id>        # Get attribute values for a record
│   └── export
│
├── objects                # Attio object definitions (schema management)
│   ├── list               # List all objects in workspace
│   ├── get <id-or-slug>   # Get object definition with attributes
│   ├── create             # Create custom object
│   └── update <id>        # Update object definition
│
├── attributes             # Attribute definitions on objects/lists
│   ├── list               # --object=<slug> or --list=<slug>
│   ├── get <id>
│   ├── create
│   └── update <id>
│
├── lists                  # List definitions
│   ├── list               # List all lists
│   ├── get <id-or-slug>
│   ├── create
│   └── update <id>
│
├── entries                # List entries (records in lists)
│   ├── list               # --list=<slug> required
│   ├── get <id>           # --list=<slug> required
│   ├── create             # Add record to list
│   ├── update <id>
│   ├── upsert
│   ├── delete <id>
│   ├── values <id>        # Get attribute values for an entry
│   └── export
│
├── notes
│   ├── list               # --record=<id> to filter by parent record
│   ├── get <id>
│   ├── create             # --record=<id> --title --body (supports stdin for body)
│   └── delete <id>
│
├── tasks
│   ├── list               # --assignee, --status, --record filters
│   ├── get <id>
│   ├── create
│   ├── update <id>
│   ├── delete <id>
│   └── complete <id>      # Convenience: mark task as completed
│
├── comments
│   ├── create             # --thread=<id> --body
│   ├── get <id>
│   └── delete <id>
│
├── threads
│   ├── list               # --record=<id>
│   └── get <id>
│
├── webhooks
│   ├── list
│   ├── get <id>
│   ├── create             # --url --events (comma-separated event types)
│   ├── update <id>
│   ├── delete <id>
│   └── events             # List all available webhook event types
│
├── workspace
│   ├── info               # Current workspace details
│   └── members            # List workspace members
│
├── files
│   ├── list               # --record=<id>
│   ├── get <id>
│   ├── upload             # --record=<id> --file=<path>
│   ├── download <id>      # --output=<path>
│   ├── create-folder      # --record=<id> --name
│   └── delete <id>
│
├── views
│   ├── list               # --object=<slug> or --list=<slug>
│   └── get <id>
│
├── meetings
│   ├── list               # --from, --to date filters
│   └── get <id>
│
├── recordings
│   ├── list               # --meeting=<id>
│   └── get <id>
│
├── transcripts
│   └── get <id>           # --recording=<id>
│
├── select-options
│   ├── list               # --attribute=<id>
│   ├── create
│   └── update <id>
│
├── statuses
│   ├── list               # --attribute=<id>
│   ├── create
│   └── update <id>
│
├── api                    # Raw API escape hatch (like gh api)
│   └── <method> <path>    # attio api GET /v2/objects
│                          # attio api POST /v2/records --body='...'
│                          # Supports --paginate, --jq
│
├── search <query>         # Global search across all objects
│
├── import                 # Bulk import from files
│   ├── csv                # --object=<slug> --file=<path> --mapping=<json>
│   └── json               # --object=<slug> --file=<path>
│
├── export                 # Bulk export to files
│   ├── csv                # --object=<slug> --file=<path> --fields=...
│   └── json               # --object=<slug> --file=<path>
│
├── agent-context          # Machine-readable CLI schema for AI agents
│                          # Returns JSON with all commands, flags, types, enums
│
├── completion             # Shell completion setup
│   ├── bash
│   ├── zsh
│   ├── fish
│   └── powershell
│
└── version                # Print version info
```

### 3.3 Global Flags (Available on Every Command)

```
--json                 Output as JSON (to stdout)
--json-pretty          Output as formatted/indented JSON
--jq <expression>      Apply jq filter to JSON output (implies --json)
--fields <f1,f2,...>   Select specific fields in output
--limit <n>            Limit number of results (default: 25)
--all                  Fetch all results (auto-paginate)
--profile <name>       Use a specific auth profile
--api-key <key>        Override API key for this command
--debug                Print HTTP request/response details to stderr
--quiet                Suppress all output except errors
--no-color             Disable colored output
--no-input             Disable all interactive prompts
--yes                  Auto-confirm all prompts
--dry-run              Show what would happen without doing it
--help                 Show help for the command
--version              Show version
```

### 3.4 Standard Filter and Sort Flags (on list/query commands)

```
--filter <json>          Raw filter JSON (matches API filter format)
--filter-attr <attr>     Filter by attribute name (repeatable)
--filter-op <op>         Filter operator ($eq, $contains, $gt, etc.)
--filter-value <val>     Filter value
--sort <attr>            Sort by attribute
--sort-direction <dir>   asc or desc (default: asc)
--offset <n>             Pagination offset
```

The `--filter-attr`, `--filter-op`, `--filter-value` triple provides a human-friendly alternative to raw `--filter` JSON. They can be repeated for multiple conditions:

```bash
attio people list --filter-attr=email --filter-op='$contains' --filter-value='@acme.com' --sort=name
```

---

## 4. Output Strategy

### 4.1 Dual-Mode Architecture

Every data-returning command has two output paths that share the same underlying data but present it differently:

**Human mode** (default when stdout is a TTY):
- Rich-formatted tables using the Rich library
- Colored status indicators (green for active, red for failed, etc.)
- Relative timestamps ("2 hours ago" instead of ISO 8601)
- Truncated long text fields with ellipsis
- Record count and pagination info at the bottom
- Contextual next-step suggestions

**Machine mode** (`--json` flag or non-TTY stdout):
- Complete JSON with all fields, including those omitted from the table
- ISO 8601 timestamps
- Full text content (not truncated unless `--fields` limits it)
- Pagination metadata as a top-level field
- No ANSI escape codes
- `next_actions` array with suggested follow-up commands

### 4.2 JSON Output Schema

All JSON output follows a consistent envelope:

```json
{
  "data": [...],
  "pagination": {
    "offset": 0,
    "limit": 25,
    "total": 142,
    "has_more": true
  },
  "meta": {
    "command": "attio people list",
    "timestamp": "2026-05-15T10:30:00Z",
    "duration_ms": 234
  },
  "next_actions": [
    "attio people list --offset=25 --limit=25",
    "attio people get <id>"
  ]
}
```

For single-item responses:

```json
{
  "data": { ... },
  "meta": {
    "command": "attio people get abc123",
    "timestamp": "2026-05-15T10:30:00Z",
    "duration_ms": 89
  },
  "next_actions": [
    "attio people update abc123 --values '{...}'",
    "attio notes list --record=abc123",
    "attio entries list --list=pipeline --filter-attr=record --filter-value=abc123"
  ]
}
```

For mutations:

```json
{
  "data": { ... },
  "action": "created",
  "existing": false,
  "meta": { ... },
  "next_actions": [ ... ]
}
```

### 4.3 Error Output Schema

Errors always go to stderr in human mode. In `--json` mode, errors are structured JSON to stdout (with appropriate non-zero exit code):

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_attribute_value",
    "message": "The value 'active' is not valid for attribute 'status'",
    "field": "status",
    "valid_values": ["open", "won", "lost"],
    "suggestion": "Use one of the valid values listed above",
    "retryable": false,
    "documentation_url": "https://docs.attio.com/rest-api/attribute-types/attribute-types-status"
  },
  "meta": {
    "command": "attio deals update abc123",
    "timestamp": "2026-05-15T10:30:00Z",
    "exit_code": 8
  }
}
```

### 4.4 Table Formatting Strategy

Using Rich tables with adaptive column sizing:

**Wide terminal (120+ chars)**: Show all primary columns -- ID, name, email, status, created_at, updated_at.

**Medium terminal (80-119 chars)**: Drop less-essential columns (updated_at, some attributes). Use truncation on long fields.

**Narrow terminal (<80 chars)**: Switch to a compact card layout -- one record per block with key: value lines. This is more readable than a crushed table.

**Always**: Detect terminal width at render time. Never wrap mid-word in IDs or email addresses (use `no_wrap=True` on those columns).

### 4.5 Additional Output Formats

```
--format table         Default human-readable table (alias for no flag)
--format csv           CSV output (for spreadsheet import)
--format tsv           Tab-separated values
--format jsonl         One JSON object per line (for streaming/piping)
--format yaml          YAML output (for config-like use cases)
```

The `--json` flag is a shortcut for `--format json` (the most common case). Both work.

### 4.6 Respecting Environment Conventions

- `NO_COLOR=1`: Disable all color output
- `TERM=dumb`: Disable colors and formatting
- `CLICOLOR_FORCE=1`: Force color even in pipes
- `COLUMNS=<n>`: Override terminal width detection
- Non-TTY stdout: Auto-disable color, spinners, progress bars, and interactive prompts

---

## 5. Auth & Config Strategy

### 5.1 Authentication Methods (Priority Order)

1. **`--api-key` flag**: Highest priority. Per-command override. Never stored.
2. **`ATTIO_API_KEY` environment variable**: Standard for CI/CD, Docker, agent workflows. Most agent-friendly method.
3. **Active profile**: Stored in config file, selected via `attio profile use <name>`.
4. **Default profile**: The profile named "default" if it exists.

### 5.2 Credential Storage

**Recommended approach**: Use the Python `keyring` library for cross-platform secure storage.

- **macOS**: Keychain
- **Linux**: Secret Service (GNOME Keyring / KDE Wallet)
- **Windows**: Windows Credential Locker
- **Fallback**: Encrypted file at `~/.config/attio/credentials` (with a warning on first use)
- **CI/Headless**: Environment variable only -- no file storage needed

```python
import keyring

# Store
keyring.set_password("attio-cli", f"profile:{profile_name}", api_key)

# Retrieve
api_key = keyring.get_password("attio-cli", f"profile:{profile_name}")
```

### 5.3 Config File Structure

Location: `~/.config/attio/config.toml` (XDG-compliant)

```toml
[core]
default_profile = "work"
default_format = "table"
default_limit = 25
color = "auto"  # auto | always | never

[profiles.work]
workspace_name = "Acme Corp"
workspace_id = "ws_abc123"
# API key stored in keyring, not in this file

[profiles.personal]
workspace_name = "Side Project"
workspace_id = "ws_def456"

[aliases]
contacts = "people list"
pipeline = "entries list --list=sales-pipeline"
```

### 5.4 Login Flow

```
$ attio auth login

Welcome to the Attio CLI!

How would you like to authenticate?

  > API Key (paste your key from Settings > Developers)
    OAuth (open browser for Attio login)

Enter your API key: ****************************

Verifying... OK

Authenticated as Kyle Doherty in workspace "Acme Corp"
Profile saved as "default"

To switch workspaces later, use:
  attio auth login         # Add another workspace
  attio auth switch        # Switch between saved profiles
  attio profile list       # See all profiles
```

For agents (non-interactive):
```bash
export ATTIO_API_KEY="your_key_here"
attio auth status  # Verify auth works
```

### 5.5 Multi-Workspace Support

Each profile stores a separate API key and workspace reference. Users can:
- `attio profile save staging --api-key=...` to save a new profile
- `attio profile use staging` to switch the active profile
- `attio people list --profile=staging` for per-command overrides
- `ATTIO_PROFILE=staging attio people list` via environment variable

---

## 6. Technical Architecture

### 6.1 Package Structure

```
packages/cli/
├── pyproject.toml              # Package config: name "attio-cli", depends on "attio" SDK
├── src/
│   └── attio_cli/
│       ├── __init__.py
│       ├── __main__.py         # Entry point: python -m attio_cli
│       ├── app.py              # Root Typer app with lazy-loaded command groups
│       ├── _version.py         # Version string
│       │
│       ├── core/               # Shared infrastructure
│       │   ├── __init__.py
│       │   ├── auth.py         # Auth management (keyring, env var, config)
│       │   ├── config.py       # Config file read/write (TOML)
│       │   ├── client.py       # SDK client factory (creates AttioClient from auth)
│       │   ├── output.py       # Output formatting engine (table, json, csv, etc.)
│       │   ├── errors.py       # Error formatting and exit code mapping
│       │   ├── pagination.py   # Auto-pagination helpers
│       │   ├── filters.py      # Filter flag parsing (--filter-attr/op/value to API format)
│       │   ├── context.py      # Global state (active profile, output format, flags)
│       │   ├── console.py      # Rich console singleton (respects NO_COLOR, width)
│       │   └── types.py        # Shared type definitions
│       │
│       ├── commands/           # One module per command group
│       │   ├── __init__.py
│       │   ├── auth.py         # attio auth login/logout/status/switch/token
│       │   ├── config_cmd.py   # attio config get/set/list/path
│       │   ├── profile.py      # attio profile list/save/use/show/delete
│       │   ├── people.py       # attio people list/get/create/update/upsert/delete/search/export
│       │   ├── companies.py    # attio companies (same structure)
│       │   ├── deals.py        # attio deals (same + move)
│       │   ├── records.py      # attio records (generic)
│       │   ├── objects.py      # attio objects list/get/create/update
│       │   ├── attributes.py   # attio attributes
│       │   ├── lists.py        # attio lists
│       │   ├── entries.py      # attio entries
│       │   ├── notes.py        # attio notes
│       │   ├── tasks.py        # attio tasks
│       │   ├── comments.py     # attio comments
│       │   ├── threads.py      # attio threads
│       │   ├── webhooks.py     # attio webhooks
│       │   ├── workspace.py    # attio workspace info/members
│       │   ├── files.py        # attio files
│       │   ├── views.py        # attio views
│       │   ├── meetings.py     # attio meetings
│       │   ├── recordings.py   # attio recordings
│       │   ├── transcripts.py  # attio transcripts
│       │   ├── select_options.py
│       │   ├── statuses.py
│       │   ├── api.py          # attio api (raw escape hatch)
│       │   ├── search.py       # attio search (global)
│       │   ├── import_cmd.py   # attio import csv/json
│       │   ├── export_cmd.py   # attio export csv/json
│       │   ├── agent.py        # attio agent-context
│       │   └── completion.py   # attio completion bash/zsh/fish
│       │
│       └── formatters/         # Output format renderers
│           ├── __init__.py
│           ├── table.py        # Rich table formatter
│           ├── json_fmt.py     # JSON/JSONL formatter
│           ├── csv_fmt.py      # CSV/TSV formatter
│           └── yaml_fmt.py     # YAML formatter
│
├── tests/
│   ├── conftest.py             # Shared fixtures (CliRunner, mock client)
│   ├── test_auth.py
│   ├── test_people.py
│   ├── test_records.py
│   ├── test_output.py
│   ├── test_errors.py
│   └── ...
│
├── CLAUDE.md                   # Dev instructions for this package
├── AGENTS.md                   # Agent instructions for this package
└── SKILL.md                    # Agent skill manifest
```

### 6.2 Typer App Setup with Lazy Loading

The root app uses lazy loading to keep startup fast. Only the invoked command group's module is imported:

```python
# app.py
import importlib
from typing import Optional

import typer
from click import Group

# Lazy-loaded command registry
COMMAND_GROUPS = {
    "auth": "attio_cli.commands.auth",
    "config": "attio_cli.commands.config_cmd",
    "profile": "attio_cli.commands.profile",
    "people": "attio_cli.commands.people",
    "companies": "attio_cli.commands.companies",
    "deals": "attio_cli.commands.deals",
    "records": "attio_cli.commands.records",
    "objects": "attio_cli.commands.objects",
    "attributes": "attio_cli.commands.attributes",
    "lists": "attio_cli.commands.lists",
    "entries": "attio_cli.commands.entries",
    "notes": "attio_cli.commands.notes",
    "tasks": "attio_cli.commands.tasks",
    "comments": "attio_cli.commands.comments",
    "threads": "attio_cli.commands.threads",
    "webhooks": "attio_cli.commands.webhooks",
    "workspace": "attio_cli.commands.workspace",
    "files": "attio_cli.commands.files",
    "views": "attio_cli.commands.views",
    "meetings": "attio_cli.commands.meetings",
    "recordings": "attio_cli.commands.recordings",
    "transcripts": "attio_cli.commands.transcripts",
    "select-options": "attio_cli.commands.select_options",
    "statuses": "attio_cli.commands.statuses",
    "api": "attio_cli.commands.api",
    "search": "attio_cli.commands.search",
    "import": "attio_cli.commands.import_cmd",
    "export": "attio_cli.commands.export_cmd",
    "agent-context": "attio_cli.commands.agent",
    "completion": "attio_cli.commands.completion",
}


class LazyGroup(Group):
    """Click group that lazy-loads subcommands on first access."""

    def __init__(self, *args, lazy_subcommands: dict[str, str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._lazy_subcommands = lazy_subcommands or {}

    def list_commands(self, ctx):
        base = super().list_commands(ctx)
        lazy = sorted(self._lazy_subcommands.keys())
        return base + lazy

    def get_command(self, ctx, cmd_name):
        if cmd_name in self._lazy_subcommands:
            module_path = self._lazy_subcommands[cmd_name]
            mod = importlib.import_module(module_path)
            app = getattr(mod, "app")
            return typer.main.get_command(app)
        return super().get_command(ctx, cmd_name)


app = typer.Typer(
    name="attio",
    help="The Attio CRM command-line interface.",
    cls=LazyGroup,
    lazy_subcommands=COMMAND_GROUPS,
    rich_markup_mode="rich",
    no_args_is_help=True,
)
```

### 6.3 Command Implementation Pattern

Each command module follows a consistent pattern:

```python
# commands/people.py
from __future__ import annotations

from typing import Optional

import typer

from attio_cli.core.client import get_client
from attio_cli.core.context import GlobalContext
from attio_cli.core.errors import handle_api_error
from attio_cli.core.output import render_output

app = typer.Typer(
    name="people",
    help="Manage people records in Attio.",
    no_args_is_help=True,
)


@app.command()
def list(
    ctx: typer.Context,
    limit: int = typer.Option(25, help="Maximum number of results"),
    offset: int = typer.Option(0, help="Pagination offset"),
    all_results: bool = typer.Option(False, "--all", help="Fetch all results"),
    filter_json: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON"),
    sort: Optional[str] = typer.Option(None, help="Sort by attribute"),
    sort_direction: str = typer.Option("asc", help="Sort direction: asc or desc"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated field names"),
) -> None:
    """List people records with optional filtering and sorting."""
    gctx = GlobalContext.from_typer(ctx)
    client = get_client(gctx)

    try:
        if all_results:
            results = []
            for record in client.people.query_all(
                filter=_parse_filter(filter_json),
                sorts=_parse_sorts(sort, sort_direction),
            ):
                results.append(record)
            render_output(gctx, data=results, resource_type="person")
        else:
            response = client.people.list(
                limit=limit,
                offset=offset,
                filter=_parse_filter(filter_json),
                sorts=_parse_sorts(sort, sort_direction),
            )
            render_output(
                gctx,
                data=response.data,
                resource_type="person",
                pagination={"offset": offset, "limit": limit, "total": len(response.data)},
            )
    except Exception as e:
        handle_api_error(gctx, e)


@app.command()
def get(
    ctx: typer.Context,
    record_id: str = typer.Argument(help="The record ID to retrieve"),
) -> None:
    """Get a person by ID."""
    gctx = GlobalContext.from_typer(ctx)
    client = get_client(gctx)

    try:
        record = client.people.get(record_id)
        render_output(gctx, data=record, resource_type="person", single=True)
    except Exception as e:
        handle_api_error(gctx, e)
```

### 6.4 Output Rendering Engine

The output engine is the central abstraction that routes data to the correct formatter:

```python
# core/output.py
from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.table import Table

from attio_cli.core.context import GlobalContext


def render_output(
    ctx: GlobalContext,
    data: Any,
    resource_type: str,
    single: bool = False,
    pagination: dict | None = None,
    action: str | None = None,
    existing: bool = False,
) -> None:
    """Route data to the appropriate output formatter."""
    if ctx.output_format == "json" or ctx.json:
        _render_json(ctx, data, resource_type, single, pagination, action, existing)
    elif ctx.output_format == "csv":
        _render_csv(ctx, data, resource_type)
    elif ctx.output_format == "jsonl":
        _render_jsonl(ctx, data)
    elif ctx.output_format == "yaml":
        _render_yaml(ctx, data)
    else:
        _render_table(ctx, data, resource_type, single, pagination)


def _render_json(ctx, data, resource_type, single, pagination, action, existing):
    """Render complete JSON envelope to stdout."""
    envelope = {"data": _serialize(data)}
    if pagination:
        envelope["pagination"] = pagination
    if action:
        envelope["action"] = action
        envelope["existing"] = existing
    envelope["meta"] = {
        "command": ctx.full_command,
        "timestamp": _now_iso(),
        "duration_ms": ctx.elapsed_ms(),
    }
    envelope["next_actions"] = _suggest_actions(resource_type, data, single)

    output = json.dumps(envelope, indent=2 if ctx.json_pretty else None, default=str)

    if ctx.jq_filter:
        output = _apply_jq(output, ctx.jq_filter)

    sys.stdout.write(output + "\n")


def _render_table(ctx, data, resource_type, single, pagination):
    """Render Rich table to terminal."""
    console = ctx.console
    columns = _get_columns_for_type(resource_type, console.width)

    if single:
        _render_detail_panel(console, data, resource_type)
    else:
        table = Table(show_header=True, header_style="bold", expand=True)
        for col in columns:
            table.add_column(col.header, style=col.style, no_wrap=col.no_wrap)
        for item in data:
            table.add_row(*[col.extract(item) for col in columns])
        console.print(table)

        if pagination:
            console.print(
                f"\nShowing {len(data)} of {pagination.get('total', '?')} results",
                style="dim",
            )
```

### 6.5 Global Context and Flag Handling

```python
# core/context.py
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field

import typer
from rich.console import Console


@dataclass
class GlobalContext:
    """Stores global flag state resolved from flags, env vars, and config."""

    output_format: str = "table"
    json: bool = False
    json_pretty: bool = False
    jq_filter: str | None = None
    fields: list[str] | None = None
    profile: str | None = None
    api_key: str | None = None
    debug: bool = False
    quiet: bool = False
    no_color: bool = False
    no_input: bool = False
    yes: bool = False
    dry_run: bool = False
    full_command: str = ""
    _start_time: float = field(default_factory=time.monotonic)

    @classmethod
    def from_typer(cls, ctx: typer.Context) -> GlobalContext:
        """Build context from Typer context params and environment."""
        params = ctx.parent.params if ctx.parent else {}
        is_tty = sys.stdout.isatty()

        return cls(
            json=params.get("json", False) or not is_tty,
            json_pretty=params.get("json_pretty", False),
            jq_filter=params.get("jq", None),
            fields=params.get("fields", "").split(",") if params.get("fields") else None,
            profile=params.get("profile") or os.environ.get("ATTIO_PROFILE"),
            api_key=params.get("api_key") or os.environ.get("ATTIO_API_KEY"),
            debug=params.get("debug", False),
            quiet=params.get("quiet", False),
            no_color=params.get("no_color", False) or "NO_COLOR" in os.environ,
            no_input=params.get("no_input", False) or not sys.stdin.isatty(),
            yes=params.get("yes", False),
            dry_run=params.get("dry_run", False),
            full_command=" ".join(sys.argv),
        )

    @property
    def console(self) -> Console:
        return Console(
            no_color=self.no_color,
            quiet=self.quiet,
        )

    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self._start_time) * 1000)
```

### 6.6 Error Handling and Exit Codes

```python
# core/errors.py
from __future__ import annotations

import json
import sys

from attio import (
    AttioAPIError,
    AttioConnectionError,
    AttioPermissionError,
    AttioTimeoutError,
    AttioValidationError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
)

from attio_cli.core.context import GlobalContext

EXIT_CODES = {
    "general": 1,
    "usage": 2,
    "auth": 3,
    "permission": 4,
    "not_found": 5,
    "conflict": 6,
    "rate_limit": 7,
    "validation": 8,
}

ERROR_TYPE_MAP = {
    AuthenticationError: ("auth", "Authentication failed. Check your API key or run 'attio auth login'."),
    AttioPermissionError: ("permission", "Insufficient permissions. Verify your API key scopes."),
    NotFoundError: ("not_found", "Resource not found. Verify the ID and object type."),
    ConflictError: ("conflict", "Resource conflict. The resource may already exist."),
    RateLimitError: ("rate_limit", "Rate limited. Wait and retry, or reduce request frequency."),
    AttioValidationError: ("validation", "Validation error. Check your input values."),
    AttioConnectionError: ("general", "Connection failed. Check your network and try again."),
    AttioTimeoutError: ("general", "Request timed out. Try again or increase timeout."),
}


def handle_api_error(ctx: GlobalContext, error: Exception) -> None:
    """Format error and exit with appropriate code."""
    error_type = "general"
    suggestion = str(error)
    retryable = False

    for exc_class, (etype, default_suggestion) in ERROR_TYPE_MAP.items():
        if isinstance(error, exc_class):
            error_type = etype
            suggestion = default_suggestion
            retryable = etype in ("rate_limit", "general")
            break

    exit_code = EXIT_CODES.get(error_type, 1)

    if ctx.json:
        error_envelope = {
            "error": {
                "type": error_type,
                "message": str(error),
                "suggestion": suggestion,
                "retryable": retryable,
            },
            "meta": {
                "command": ctx.full_command,
                "exit_code": exit_code,
            },
        }
        sys.stdout.write(json.dumps(error_envelope, indent=2) + "\n")
    else:
        console = ctx.console
        console.print(f"[red bold]Error:[/] {error}", highlight=False)
        console.print(f"[dim]{suggestion}[/]")

    raise SystemExit(exit_code)
```

### 6.7 Testing Strategy

**Framework**: pytest with `typer.testing.CliRunner`

**Three test tiers:**

1. **Unit tests**: Test individual formatters, filter parsers, config handling, error mapping. No network, no SDK client. Fast.

2. **Integration tests**: Test full command invocation with mocked SDK client. Uses `CliRunner` to invoke commands and assert on output (both human and JSON modes) and exit codes.

3. **End-to-end tests** (optional, CI-only): Test against real Attio API with a test workspace. Gated behind `ATTIO_TEST_API_KEY` environment variable.

```python
# tests/test_people.py
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch

from attio_cli.app import app

runner = CliRunner()


def test_people_list_json():
    """people list --json returns valid JSON envelope."""
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(id=MagicMock(record_id="rec_123"), values={"name": [{"value": "Jane Doe"}]}),
    ]

    with patch("attio_cli.commands.people.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.people.list.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["people", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "data" in data
        assert "meta" in data


def test_people_list_not_found_exit_code():
    """Missing resource returns exit code 5."""
    with patch("attio_cli.commands.people.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.people.get.side_effect = NotFoundError("Not found")
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["people", "get", "nonexistent", "--json"])

        assert result.exit_code == 5
```

### 6.8 Dependencies

```toml
# packages/cli/pyproject.toml
[project]
name = "attio-cli"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "attio>=0.1.0",           # The SDK (sibling package)
    "typer[all]>=0.14.0",     # CLI framework (includes Rich, shellingham)
    "rich>=14.0",             # Terminal formatting (included via typer[all] but pinned)
    "keyring>=25.0",          # Secure credential storage
    "tomli>=2.0;python_version<'3.11'",  # TOML parsing (stdlib in 3.11+)
    "tomli-w>=1.0",           # TOML writing
    "pyjq>=2.6",              # jq filter support (optional, with fallback)
]

[project.scripts]
attio = "attio_cli.__main__:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

### 6.9 Startup Performance Budget

Target: **under 150ms** for `attio --help` on a cold start.

Strategies:
- Lazy-load command groups (only import the invoked group's module)
- Lazy-import Rich components (don't import Rich until output is needed)
- Lazy-import the SDK (don't create an AttioClient until a command needs API access)
- No top-level network calls (auth validation only when needed)
- Consider using `__import__` or `importlib` for deferred imports of heavy dependencies

Benchmark: Run `time attio --help` in CI and fail if it exceeds 200ms.

---

## 7. Killer Features

These are the features that would make this CLI stand out from generic API wrappers and establish it as a genuinely useful tool that people reach for daily.

### 7.1 `attio api` -- The Universal Escape Hatch

Like `gh api`, this command lets you hit any Attio API endpoint directly with full auth, pagination, and jq:

```bash
# GET request
attio api GET /v2/objects

# POST with body
attio api POST /v2/objects/people/records/query \
  --body '{"filter": {"email_addresses": {"$contains": "@acme.com"}}}'

# Auto-paginate and extract
attio api GET /v2/objects --paginate --jq '.data[].api_slug'
```

This means the CLI never blocks users -- even if a command doesn't exist yet, they can always use `attio api`.

### 7.2 `attio search` -- Global Fuzzy Search

A single command that searches across all objects:

```bash
$ attio search "Jane Doe"

People:
  Jane Doe (jane@acme.com)              rec_abc123
  Jane Doe-Smith (jane.s@example.com)   rec_def456

Companies:
  JaneDoe Consulting                     rec_ghi789

Use 'attio people get rec_abc123' to view full details.
```

With `--json`, returns structured results grouped by object type. In human mode, uses Rich panels with color-coded object types.

### 7.3 `attio deals move` -- Pipeline Stage Shortcuts

Moving deals through pipeline stages is one of the most common CRM operations:

```bash
# Move a deal to "Negotiation" stage
attio deals move deal_abc123 negotiation

# Interactive: select from available stages
attio deals move deal_abc123
# > Prospecting
#   Qualification
#   Negotiation     <-- selected
#   Closed Won
#   Closed Lost
```

### 7.4 Smart Import/Export with Column Mapping

```bash
# Export all people to CSV
attio people export --format csv --file people.csv

# Import with automatic column detection
attio import csv --object=people --file contacts.csv
# Detected columns: Name, Email, Phone, Company
# Mapping:
#   Name  -> name (personal_name)
#   Email -> email_addresses (email)
#   Phone -> phone_numbers (phone)
#   Company -> company (text)
# Proceed? [Y/n]

# Import with explicit mapping (non-interactive)
attio import csv --object=people --file contacts.csv \
  --mapping '{"Name": "name", "Email": "email_addresses"}'
```

### 7.5 Interactive Wizards with Fallback

When a human runs a create command without all required args, launch an interactive wizard. When an agent runs it, return a structured error with required fields:

```bash
# Human (TTY):
$ attio people create
Name: Jane Doe
Email: jane@acme.com
Created person "Jane Doe" (rec_abc123)

# Agent (non-TTY or --no-input):
$ attio people create --no-input
Error: Missing required values. Provide --values with at least: name
Exit code: 2

# Agent (complete command):
$ attio people create --values '{"name": [{"first_name": "Jane", "last_name": "Doe"}], "email_addresses": [{"email_address": "jane@acme.com"}]}'
```

### 7.6 `attio agent-context` -- Machine-Readable CLI Schema

A purpose-built command that agents call first to understand the CLI's capabilities:

```bash
$ attio agent-context --json
{
  "version": "0.1.0",
  "commands": {
    "people list": {
      "description": "List people records with filtering and sorting",
      "flags": {
        "--limit": {"type": "int", "default": 25, "description": "Max results"},
        "--filter": {"type": "json", "description": "Raw API filter object"},
        "--sort": {"type": "string", "description": "Attribute slug to sort by"},
        "--json": {"type": "bool", "description": "Output as JSON"}
      },
      "examples": [
        "attio people list --limit=10 --json",
        "attio people list --filter='{\"email_addresses\": {\"$contains\": \"@acme.com\"}}'"
      ],
      "required_scopes": ["record_permission:read", "object_configuration:read"]
    },
    ...
  },
  "auth": {
    "method": "env_var",
    "variable": "ATTIO_API_KEY",
    "profiles": ["default", "staging"]
  },
  "exit_codes": {
    "0": "success",
    "1": "general_error",
    "2": "usage_error",
    "3": "auth_error",
    "4": "permission_error",
    "5": "not_found",
    "6": "conflict",
    "7": "rate_limit",
    "8": "validation_error"
  }
}
```

This eliminates the need for agents to parse `--help` text. They get a structured schema they can reason over directly.

### 7.7 Built-in `--jq` Filter

Embed jq-like filtering directly in the CLI so users don't need jq installed:

```bash
# Extract just email addresses from people
attio people list --json --jq '.data[].values.email_addresses[0].email_address'

# Count deals by stage
attio deals list --all --json --jq '[.data[] | .values.stage[0].status.title] | group_by(.) | map({stage: .[0], count: length})'
```

This uses the `pyjq` library (wrapping the C jq library) for full jq compatibility.

### 7.8 Contextual Suggestions After Every Command

After every successful operation, suggest logical next steps:

```bash
$ attio people create --values '{"name": [{"first_name": "Jane", "last_name": "Doe"}]}'

Created person "Jane Doe" (rec_abc123)

Next steps:
  attio people get rec_abc123                         # View full record
  attio notes create --record=rec_abc123 --body="..."  # Add a note
  attio entries create --list=pipeline --record=rec_abc123  # Add to a list
```

Suppressible with `--quiet`. In `--json` mode, these appear in the `next_actions` array.

### 7.9 `attio completion` -- Shell Completion Setup

One-command setup for tab completion:

```bash
# Zsh (most common on macOS)
attio completion zsh >> ~/.zshrc

# Bash
attio completion bash >> ~/.bashrc

# Fish
attio completion fish > ~/.config/fish/completions/attio.fish
```

Tab completion should cover:
- Command and subcommand names
- Flag names
- Object slugs (dynamically fetched: `attio records list --object=<TAB>`)
- List slugs
- Attribute slugs
- Record IDs (from recent operations cache)

### 7.10 `--dry-run` for All Mutations

Every create, update, delete, and upsert command supports `--dry-run` to preview the API request that would be sent:

```bash
$ attio people create --values '{"name": [{"first_name": "Test"}]}' --dry-run

Dry run: would send POST /v2/objects/people/records
Body:
{
  "data": {
    "values": {
      "name": [{"first_name": "Test"}]
    }
  }
}

No changes were made.
```

---

## 8. MCP Server Potential

### 8.1 The Opportunity

Attio already has an official MCP server at `mcp.attio.com/mcp` with ~40 tools. However, there is a compelling case for the CLI to also function as a local MCP server:

1. **Offline/local development**: Works without internet for cached operations.
2. **Custom workspace scoping**: Uses the user's own API key with profile switching, not OAuth.
3. **Richer tool surface**: Exposes bulk operations, import/export, and pipeline management that the official MCP server may not cover.
4. **CLI + MCP convergence**: Users who already have the CLI installed get MCP for free.
5. **Token efficiency**: CLI-based operations are 10-32x cheaper on tokens than MCP, but if the MCP layer wraps the CLI's efficient logic, you get the best of both.

### 8.2 Architecture: CLI-First, MCP-Second

The recommended pattern (supported by research):

> "Build a good CLI first, then wrap it as an MCP."

The CLI is the source of truth. The MCP server is a thin adapter that:
1. Imports CLI command functions directly (not subprocess calls)
2. Maps MCP tool schemas to CLI command signatures
3. Returns the same structured JSON that `--json` produces
4. Uses the same auth/profile system

```python
# mcp_server.py (future)
from fastmcp import FastMCP

from attio_cli.commands import people, companies, deals, records, notes, tasks

mcp = FastMCP("attio-cli")


@mcp.tool()
def list_people(limit: int = 25, filter: str | None = None) -> dict:
    """List people records in Attio CRM."""
    # Reuse the same logic as `attio people list --json`
    return people._list_impl(limit=limit, filter_json=filter)


@mcp.tool()
def create_person(values: dict) -> dict:
    """Create a new person record in Attio CRM."""
    return people._create_impl(values=values)


# ... map all CLI commands to MCP tools
```

### 8.3 MCP Tool Schema Design

Each MCP tool maps to one CLI command. The tool descriptions follow agent-native best practices:

```json
{
  "name": "list_people",
  "description": "List people records in Attio CRM. Returns name, email, and key attributes. Use filter parameter for searching. Default limit is 25; use --all for complete results.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {"type": "integer", "default": 25, "description": "Max results to return"},
      "filter": {
        "type": "string",
        "description": "JSON filter object, e.g. {\"email_addresses\": {\"$contains\": \"@acme.com\"}}"
      },
      "sort": {"type": "string", "description": "Attribute slug to sort by"},
      "fields": {"type": "string", "description": "Comma-separated field names to return"}
    }
  }
}
```

### 8.4 Running as MCP Server

```bash
# Start as MCP server (stdio transport for Claude Desktop / Cursor)
attio mcp serve

# Start as MCP server (HTTP transport for remote agents)
attio mcp serve --transport http --port 8080

# Install into Claude Desktop config
attio mcp install --target claude-desktop
```

### 8.5 Why Not Just MCP?

The research is clear: CLI is more reliable and efficient than MCP for most operations. But MCP provides better discoverability and schema validation. The answer is **both**:

- Agents that support shell execution (Claude Code, Codex CLI) should use the CLI directly -- it's cheaper and more reliable.
- Agents that only support MCP (Claude Desktop, ChatGPT) use the MCP adapter.
- The same code powers both, ensuring consistency.

---

## Appendix A: Recommended Build Order

### Phase 1: Foundation (Week 1)
1. Package scaffolding (pyproject.toml, src layout, tests/)
2. Core infrastructure: auth, config, client factory, output engine, error handling
3. Global flags and context management
4. `attio auth login/status/logout` commands
5. `attio config get/set/list` commands
6. `attio profile save/use/list/show/delete` commands
7. `attio version` and `attio completion` commands

### Phase 2: Core Resources (Week 2)
8. `attio people list/get/create/update/delete/upsert/search` with both human and JSON output
9. `attio companies` (same structure, reuse patterns from people)
10. `attio deals` (same structure + move)
11. `attio records` (generic, supports custom objects)
12. `attio search` (global search)

### Phase 3: Supporting Resources (Week 3)
13. `attio objects list/get/create/update`
14. `attio attributes`
15. `attio lists` and `attio entries`
16. `attio notes` and `attio tasks`
17. `attio webhooks`

### Phase 4: Everything Else (Week 4)
18. `attio comments`, `attio threads`
19. `attio workspace`
20. `attio files`, `attio views`
21. `attio meetings`, `attio recordings`, `attio transcripts`
22. `attio select-options`, `attio statuses`
23. `attio api` escape hatch
24. `attio import/export` (CSV and JSON)
25. `attio agent-context`

### Phase 5: Polish (Week 5)
26. Shell completion with dynamic suggestions
27. SKILL.md and AGENTS.md files
28. Interactive wizards for create commands
29. `--dry-run` support on all mutations
30. Performance optimization (startup time)
31. Comprehensive test coverage

### Phase 6: MCP (Week 6, Optional)
32. MCP server adapter using FastMCP
33. `attio mcp serve/install` commands
34. MCP tool schema generation from CLI commands

---

## Appendix B: Key Research Sources

- [Command Line Interface Guidelines](https://clig.dev/) -- The foundational reference for CLI design
- [10 Principles for Agent-Native CLIs](https://trevinsays.com/p/10-principles-for-agent-native-clis) -- Trevin Chow's comprehensive agent-first framework
- [Keep the Terminal Relevant: Patterns for AI Agent Driven CLIs](https://www.infoq.com/articles/ai-agent-cli/) -- InfoQ's deep-dive on agent-CLI patterns
- [AXI: Agent eXperience Interface](https://axi.md/) -- 10 principles with benchmark data showing CLI > MCP for cost and reliability
- [Building a CLI That Works for Humans and Machines](https://www.openstatus.dev/blog/building-cli-for-human-and-agents) -- OpenStatus's practical dual-consumer patterns
- [Writing CLI Tools That AI Agents Actually Want to Use](https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no) -- Exit code taxonomy and idempotency patterns
- [GitHub CLI Manual](https://cli.github.com/manual/) -- The gold standard for developer CLI design
- [Stripe CLI Reference](https://docs.stripe.com/cli) -- Resource-mirroring and real-time streaming
- [Typer Documentation](https://typer.tiangolo.com/) -- CLI framework reference
- [Rich Documentation](https://rich.readthedocs.io/) -- Terminal formatting reference
- [FastMCP Documentation](https://gofastmcp.com/patterns/cli) -- CLI-to-MCP bridge patterns
- [Attio API Documentation](https://docs.attio.com/rest-api/overview) -- API reference
- [Attio MCP Documentation](https://docs.attio.com/mcp/overview) -- Official MCP server reference
- [AGENTS.md Specification](https://agents.md/) -- Cross-tool agent configuration standard
- [Agent Skills Overview](https://agentskills.io/home) -- SKILL.md format and ecosystem
- [Vercel CLI for AI Agents](https://agentskills.so/skills/vercel-vercel-vercel-cli) -- Agent skill patterns from Vercel
- [MCP vs CLI: Measuring Token Cost](https://www.mindstudio.ai/blog/mcp-vs-cli-agentic-workflows-token-overhead-reliability) -- CLI is 10-32x cheaper and more reliable
- [Typer Lazy Loading Gist](https://gist.github.com/danielomiya/6a9c098c7094eefd1651eef2d967d3af) -- LazyGroup pattern for fast startup
- [Python keyring Library](https://pypi.org/project/keyring/) -- Cross-platform secure credential storage
