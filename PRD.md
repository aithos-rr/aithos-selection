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

## 3. Mental model: ingredients → composites → recipes

The repository encodes three layers of abstraction.

### Atoms (ingredients)

Single-purpose, reusable units. Each atom lives in exactly one folder.

- **`skills/`** — Claude Code skills in Anthropic format (each with its own
  `SKILL.md`).
- **`prompts/`** — prompt library split in:
  - `library/` — finished, versioned prompts ready to use as-is
  - `templates/` — parametric templates with `{{variables}}`
- **`mcp-servers/`** — JSON config files for MCP servers (one server per file)
- **`tools/`** — Python scripts, CLI utilities, plugins (own or third-party)
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

### Recipes

Orchestrated workflows that solve a complete user-facing task.

- **`workflows/`** — Claude/agent-based workflows, one subfolder each, with:
  - `README.md` — purpose, inputs, outputs, KPIs
  - `flow.md` — step-by-step human-readable description
  - `manifest.yaml` — declares which agents, atoms, and n8n flows it uses
  - `n8n.json` (optional) — if the workflow includes an n8n component
- **`n8n-workflows/`** — n8n flows that don't belong to a Claude-orchestrated
  workflow above. Pure n8n.

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

For `prompts/**/*.md`, `stack/*.md`, `skills/**/SKILL.md` (note: `SKILL.md`
files use the Anthropic skill frontmatter format which is a stricter subset).

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

### 5.3 MCP server config

Native MCP format (no Aithos-specific wrapping) in `mcp-servers/*.json`. The
frontmatter convention above does not apply to JSON files; metadata for an
MCP config lives in a companion `<name>.md` in the same folder when needed.

## 6. Naming conventions

- **Folders and files**: kebab-case, no spaces, no underscores (except for
  the conventional `_inbox/`).
- **Identifiers** (`id` in frontmatter, `name` in manifest): kebab-case, must
  match the folder or file name when applicable.
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
- **Scopes** during bootstrap: `phase-1`, `phase-2`, `phase-3`, `phase-4`,
  `governance`, `librarian`, `index`, `check`.
- One commit per logical change. End-of-phase commits are required by each
  task file.

## 9. Phase overview

The bootstrap of this repository is split in 4 automated phases plus a
manual Phase 5. Each phase has its own task file in `tasks/`:

| Phase | File | Goal |
|-------|------|------|
| 1 | `tasks/phase-1-foundation.md` | Governance docs, schemas, naming conventions, empty folder skeleton, canonical examples |
| 2 | `tasks/phase-2-librarian.md` | The `librarian` skill that processes `_inbox/` |
| 3 | `tasks/phase-3-index.md` | `generate_index.py` + pre-commit hook |
| 4 | `tasks/phase-4-check.md` | `check.py` validator + GitHub Action |
| 5 | manual | Riccardo's bulk-ingest of existing content (out of bootstrap scope) |

Execute phases 1 through 4 in order. After each phase, commit, push, and
stop. The user (Riccardo) will review and instruct continuation.

## 10. Done criteria for bootstrap

After all four phases:

- `INDEX.md` regenerates cleanly with no errors.
- `uv run python tools/check.py` passes on a clean state.
- `pre-commit run --all-files` passes.
- GitHub Actions CI passes on push.
- All schemas validate against the canonical example content created in
  Phase 1.
- `README.md` is presentable: a reader who knows nothing about the repo can
  read it and understand the mental model.
