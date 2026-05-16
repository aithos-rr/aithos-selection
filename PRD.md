# Aithos Selection — Product Requirements Document

## 1. Vision & Goal

Aithos Selection is a curated personal knowledge base of AI primitives that
Riccardo (founder of Aithos, an AI consulting firm for SMEs) uses to deliver
client work. The repository serves three purposes:

1. **Working library.** Single place to look up prompts, agent configs, MCP
   server setups, and operational notes when building solutions.
2. **Portfolio asset.** Demonstrable proof of methodology when pitching SME
   clients: the repo itself is a case study in AI-augmented knowledge
   management.
3. **Compounding leverage.** Every solved problem becomes a reusable
   ingredient. Future client engagements assemble from existing pieces instead
   of starting from zero.

## 2. Non-goals

- Not a public open-source project (for now).
- Not a replacement for client-specific deliverables (those live in their own
  repos or client-side systems).
- Not a CMS or web app — Markdown + YAML + git, nothing more.
- Not a documentation site (no MkDocs, no Docusaurus). `INDEX.md` is enough.

## 3. Mental model: five layers

The repository encodes five layers. The first four are content the repo
*contains* and reuse each other through `manifest.yaml` declarations; the
fifth points outward.

### Atoms (ingredients)

Single-purpose, reusable units. Each atom lives in exactly one folder.

- **`skills/`** — Claude Code skills in Anthropic format (each with its own
  `SKILL.md`).
- **`prompts/`** — prompt library split in:
  - `library/` — finished, versioned prompts ready to use as-is. Two
    structural variants are valid: a single-file `library/<id>.md`, or a
    folder `library/<id>/` containing `README.md` plus optional companion
    assets (image, code snippet) — see `CONTRIBUTING.md` for the
    folder-as-prompt rules.
  - `templates/` — parametric templates with `{{variables}}`
- **`mcp-servers/`** — JSON config files for MCP servers (one server per file)
- **`tools/`** — Python scripts, CLI utilities, plugins (own or third-party).
  Includes the index generator, the validator, and `install.py` which
  deploys skills and subagents to their runtime locations.
- **`stack/`** — operational playbooks for tools you use, one Markdown per
  technology (e.g. `vscode.md`, `supabase.md`, `lm-studio.md`)

### Composites

Combinations of atoms that form a coherent unit but aren't yet a full
workflow.

- **`agents/`** — each subfolder is one agent with:
  - `agent.md` — system prompt
  - `manifest.yaml` — declares which prompts, MCP servers, tools it uses
  - `README.md` — what it does, when to use it, examples
  - `examples/` (optional) — sample input/output transcripts

### Subagents

Claude Code subagent primitives (Anthropic format). Each subagent is an
agent-like prompt that declares its own `tools`, `mcpServers`, and
`skills` dependencies and is invoked as a slash-command (`/<name>`) once
deployed under a target project's `.claude/agents/`.

- **`subagents/`** — each subfolder is one subagent with:
  - `<name>.md` — the entrypoint, in Anthropic subagent frontmatter format
  - `manifest.yaml` — the Aithos-side manifest mirroring the entrypoint's
    declared tools / MCP servers / skill dependencies for indexing and
    inverse-graph linkage. Validated by
    `docs/schemas/subagent.schema.yaml`.
  - Optional supporting bundle: `BUILD-BRIEF.md`, `ARCHITECTURE.md`,
    `PROGRESS.md`, `README.md`, `references/`, `discovery/`, `research/`,
    `test-fixtures/`, `scripts/`.

### Recipes

Orchestrated workflows that solve a complete user-facing task.

- **`workflows/`** — Claude/agent-based workflows, one subfolder each, with:
  - `README.md` — purpose, inputs, outputs, KPIs
  - `flow.md` — step-by-step human-readable description
  - `manifest.yaml` — declares which agents, atoms, and n8n flows it uses
  - `n8n.json` (optional) — if the workflow includes an n8n component
- **`n8n-workflows/`** — n8n flows that don't belong to a Claude-orchestrated
  workflow above. Pure n8n.

### References

Curated bookmarks — content the repo *points to* rather than contains.

- **`references/repos/`** — GitHub repositories worth tracking.
- **`references/articles/`** — blog posts, papers, documentation pages.
- **`references/templates/`** — external n8n workflow / skill / agent
  templates.

References never appear under `uses:` declarations in composites,
subagents, or recipes; they are pure curation. Reference files are
validated against `docs/schemas/reference.schema.yaml`.

## 4. Architectural decisions

### AD-1. No duplication

Atoms live in exactly one place. Composites reference them via paths in
`manifest.yaml`. Never copy a prompt into an agent folder.

**Rationale.** Avoids drift between copies. A single update to a prompt
propagates to every agent and workflow using it.

### AD-2. Manifest is source of truth

`manifest.yaml` files declare all dependencies. Documentation prose may
describe relationships but the manifest is authoritative for tools like
`generate_index.py` and `check.py`.

**Rationale.** Enables programmatic validation (no broken references) and
auto-generated indexes (no manual book-keeping).

### AD-3. Markdown + YAML, nothing else for content

All human-edited content is Markdown (prose) or YAML (structured). JSON is
only for machine-generated artifacts (n8n exports, lockfiles).

**Rationale.** Maximum portability, git-friendly diffs, no proprietary
lock-in, works on every editor.

### AD-4. Inbox-first ingestion

New content is dropped into `_inbox/` without classification. A skill called
`librarian` processes the inbox, classifies items, proposes destinations and
metadata, and (with user OK) moves them.

**Rationale.** Removes the cognitive cost of "where does this go?" at capture
time. Capture is fast; organization is batched and AI-assisted.

### AD-5. Single source of truth = git

No external database, no CMS. The repo on GitHub is canonical. Local clones
on WSL or Windows are working copies.

**Rationale.** Versioning, history, blame, branching, and PR review come for
free. No infrastructure to maintain.

## 5. Schemas

### 5.1 Manifest schema

For `agents/<name>/manifest.yaml` and `workflows/<name>/manifest.yaml`.

```yaml
# Required
name: string                    # kebab-case, matches folder name
version: string                 # semver, e.g. "0.1.0"
type: enum                      # "agent" | "workflow"
description: string             # one-line summary
status: enum                    # "draft" | "stable" | "deprecated"
tags: [string]                  # lowercase, kebab-case
created: date                   # ISO 8601, YYYY-MM-DD
updated: date                   # ISO 8601, YYYY-MM-DD

# Required for agents
system_prompt: path             # relative to manifest, e.g. "./agent.md"

# Optional dependencies (all paths relative to repo root)
uses:
  prompts: [path]               # e.g. ["prompts/library/doc-extraction-v2.md"]
  templates: [path]
  mcp_servers: [path]
  tools: [path]

# Required for workflows
agents: [path]                  # e.g. ["agents/agent-doc-analyst"]
n8n_workflows: [path]           # e.g. ["n8n-workflows/wf-leads/flow.json"]
```

### 5.2 Frontmatter schema

For `prompts/library/*.md`, `prompts/library/*/README.md` (folder-as-prompt
form), `prompts/templates/*.md`, `stack/*.md`, and `skills/**/SKILL.md`
(note: `SKILL.md` files use the Anthropic skill frontmatter format which
is a stricter subset).

```yaml
---
id: string                      # unique within its folder, kebab-case
name: string                    # human-readable title
type: enum                      # "prompt" | "template" | "stack-note" | "skill"
status: enum                    # "draft" | "stable" | "deprecated"
version: string                 # semver
description: string             # one-line summary
tags: [string]                  # lowercase, kebab-case
language: enum                  # "it" | "en" | "multilingual"
model: string                   # optional, e.g. "claude-sonnet-4"
created: date
updated: date
author: string                  # default "riccardo"
---
```

For folder-as-prompt files (`prompts/library/<id>/README.md`), the
`id` field must equal the folder name; this is enforced by
`tools/check.py`.

### 5.3 MCP server config

Native MCP format (no Aithos-specific wrapping) in `mcp-servers/*.json`. The
frontmatter convention above does not apply to JSON files; metadata for an
MCP config lives in a companion `<name>.md` in the same folder when needed.

### 5.4 Reference schema

For `references/<subtype>/*.md`. Validated by
`docs/schemas/reference.schema.yaml`.

```yaml
---
id: string                      # kebab-case, unique within the subfolder
name: string                    # human-readable title
type: literal                   # always "reference"
subtype: enum                   # "repo" | "article" | "template"
url: string                     # https?:// URL
status: enum                    # "active" | "archived" | "broken"
description: string             # one-line summary
tags: [string]                  # lowercase, kebab-case
language: enum                  # "it" | "en" | "multilingual"
created: date
updated: date
author: string

# Optional GitHub snapshot (only meaningful for subtype: repo)
github_owner: string
github_repo: string
github_stars: integer (>= 0)
github_language: string
github_topics: [string]
github_last_commit: date
---
```

The `subtype` field must match the parent folder (`repos`/`articles`/
`templates`); this is enforced by `tools/check.py`.

### 5.5 Subagent manifest schema

For `subagents/<name>/manifest.yaml`. Validated by
`docs/schemas/subagent.schema.yaml`. The manifest is separate from the
inner subagent entrypoint frontmatter (which follows the Anthropic
subagent format).

```yaml
name: string                    # kebab-case, matches folder name
version: string                 # semver
type: literal                   # always "subagent"
description: string             # one-line summary
status: enum                    # "draft" | "stable" | "deprecated"
tags: [string]
language: enum                  # "it" | "en" | "multilingual"
origin:                         # provenance metadata
  source: string                # e.g. "learnn", "internal"
  url: string (optional)
  notes: string (optional)
entrypoint: path                # relative to manifest, e.g. "./<name>.md"

# Optional, mirror the entrypoint frontmatter for indexing
tools: [string]
mcp_servers: [string]
skills_dependencies: [string]   # skill ids; matches against skills/ for inverse graph
memory: enum                    # "project" | "none"

created: date
updated: date
author: string
```

## 6. Naming conventions

- **Folders and files**: kebab-case, no spaces, no underscores (except for
  the conventional `_inbox/`).
- **Identifiers** (`id` in frontmatter, `name` in manifest): kebab-case, must
  match the folder or file name when applicable. For folder-as-prompt
  (`prompts/library/<id>/README.md`), the frontmatter `id` must equal the
  folder name.
- **Versioning**:
  - Files with `version` in frontmatter: bump the field on changes.
  - Files where the file *is* the version boundary (e.g. major rewrites):
    suffix with `-v2`, `-v3`. The previous version may be marked
    `status: deprecated` and kept for history.
- **Tags**: lowercase, kebab-case if multi-word. Prefer English for universal
  concepts. Use Italian only when the tag *is* Italian-specific.
- **Branch names**: `feat/<name>`, `fix/<name>`, `chore/<name>`, `docs/<name>`.

## 7. Stack constraints

- **Python**: 3.12+, managed via `uv`. No system Python.
- **Single `pyproject.toml`** at repo root declares all dependencies for
  `tools/`.
- **Allowed Python libraries**: `pydantic` (schema validation), `pyyaml`
  (parsing), `typer` (CLI), `rich` (terminal output), `pytest` (testing).
  No additions without explicit instruction.
- **All scripts** in `tools/` run as `uv run python tools/<script>.py`.
- **`pre-commit`** framework for git hooks.
- **GitHub Actions** for CI.
- **No databases, no servers, no web frameworks.**

## 8. Commit protocol

Conventional Commits format:

```
<type>(<scope>): <short imperative description>

<optional body>
```

- **Types**: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.
- **Scopes** identify the phase or component touched. Bootstrap phases used
  the `phase-N` form (`phase-1` through `phase-5.5`, including
  `phase-5.2-bis`). Component scopes used during and after bootstrap
  include `governance`, `librarian`, `index`, `check`, `install`,
  `subagents`, `nightly-sync`. Pick the scope that best describes the
  touched area; introduce a new scope only when none fits.
- One commit per logical change. End-of-phase commits are required by each
  task file.

## 9. Phase overview

Bootstrap (Phases 1–5.5) is complete. All historical task specs live in
`tasks/archive/`.

| Phase    | File                                       | Goal                                                                                              | Status |
|----------|--------------------------------------------|---------------------------------------------------------------------------------------------------|--------|
| 1        | `phase-1-foundation.md`                    | Governance docs, schemas, naming conventions, empty folder skeleton, canonical examples           | done   |
| 2        | `phase-2-librarian.md`                     | The `librarian` skill that processes `_inbox/`                                                    | done   |
| 3        | `phase-3-index.md`                         | `generate_index.py` + pre-commit hook                                                             | done   |
| 4        | `phase-4-check.md`                         | `check.py` validator + GitHub Action                                                              | done   |
| 5.0      | `phase-5.0-references.md`                  | `references/` category + reference schema + first canonical reference                              | done   |
| 5.1      | `phase-5.1-stars.md`                       | Bulk import of the user's GitHub stars into `references/repos/`                                    | done   |
| 5.2      | `phase-5.2-assets.md`                      | Bulk ingest of 27 assets (skills, prompts, folder-as-prompt visual prompt)                         | done   |
| 5.2-bis  | `phase-5.2-bis-subagents.md`               | New `subagents/` top-level category + import of 6 Learnn subagents                                 | done   |
| 5.3      | `phase-5.3-install.md`                     | `tools/install.py` for deploying skills/subagents to runtime locations                              | done   |
| 5.4      | `phase-5.4-nightly-sync.md`                | `nightly-sync` sub-flow on the librarian skill                                                    | done   |
| 5.5      | `phase-5.5-coherence-check.md`             | Coherence audit + task archive (this phase)                                                       | done   |

## 10. Done criteria for bootstrap

All criteria below are met as of Phase 5.5:

- `INDEX.md` regenerates cleanly with no errors. ✓
- `uv run python tools/check.py` passes on a clean state (11 checks). ✓
- `pre-commit run --all-files` passes. ✓
- GitHub Actions CI passes on push. ✓
- All schemas (manifest, frontmatter, reference, subagent) validate
  against the canonical example content. ✓
- `README.md` is presentable: a reader who knows nothing about the repo
  can read it and understand the mental model. ✓

## 11. Maintenance mode

After bootstrap, ongoing intake of new content happens through the
`librarian` skill's `nightly-sync` sub-flow (see
`skills/librarian/SKILL.md` §5 and the runbook at
`skills/librarian/references/nightly-sync-runbook.md`). A typical evening
session: drop new material into `_inbox/`, say "run nightly sync" in
Claude Code, review the resulting commit, push.

Deployment of skills and subagents to runtime locations (`~/.claude/skills/`
or a project's `.claude/agents/`) is handled by
`uv run python tools/install.py`. See `CONTRIBUTING.md` →
"Deploying skills and subagents".
