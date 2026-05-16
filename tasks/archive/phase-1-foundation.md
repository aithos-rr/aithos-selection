# Phase 1 — Foundation

## Goal

Establish the governance scaffolding of the repository: README, contributing
guide, machine-readable schemas, naming conventions, empty folder skeleton,
canonical example content, and base tooling configuration. After this phase,
the repository is *ready to receive content* but contains none yet (except
the canonical examples that exercise the schemas).

## Prerequisites

- You are on branch `bootstrap`.
- Working tree is clean.
- `CLAUDE.md` and `PRD.md` exist at repo root.

## Deliverables

### 1. `README.md` (replace existing one-liner)

Audience: someone landing on the repo for the first time (a future Aithos
collaborator, or Riccardo himself in 6 months).

Sections in this order:

- **What this is** — 2 sentences max.
- **Mental model** — atoms → composites → recipes, one short paragraph each.
- **How to use this repo** — pointer to `CONTRIBUTING.md`.
- **Quick start for Claude Code sessions** — the recommended way to open a
  session in this repo (basically: `cd ~/projects/aithos-selection && claude`).
- **Folder map** — tree from `CLAUDE.md` with one-line description per folder.

Length target: 100–150 lines.

### 2. `CONTRIBUTING.md`

Audience: Riccardo (and any future contributor) when adding content.

Required sections:

- **The three golden rules** — restated in user-facing language.
- **Adding a new prompt** — concrete steps with example frontmatter.
- **Adding a new MCP server config** — concrete steps.
- **Adding a new stack note** — concrete steps.
- **Adding a new agent** — concrete steps + canonical example manifest.
- **Adding a new workflow** — concrete steps + canonical example manifest.
- **Using the inbox** — when to drop in `_inbox/` instead of categorizing
  immediately.
- **Updating an existing atom** — version bump rules.

Each "adding" section must include: target folder, naming rule, required
files, required frontmatter or manifest fields, and a minimal example block.

### 3. `docs/schemas/manifest.schema.yaml`

JSON-Schema-compatible YAML schema for `manifest.yaml` files. Implement the
schema from PRD section 5.1.

Use `$schema: http://json-schema.org/draft-07/schema#` for compatibility with
`pydantic` v2 and standard JSON Schema validators.

Required fields: `name`, `version`, `type`, `description`, `status`, `tags`,
`created`, `updated`. Conditional requirements per `type`:

- `type: agent` → `system_prompt` required.
- `type: workflow` → `agents` required (at least one item).

### 4. `docs/schemas/frontmatter.schema.yaml`

JSON-Schema-compatible YAML schema for frontmatter in Markdown content files.
Implement the schema from PRD section 5.2.

Required fields: `id`, `name`, `type`, `status`, `version`, `description`,
`tags`, `language`, `created`, `updated`, `author`. Optional: `model`.

### 5. `docs/naming-conventions.md`

Detailed expansion of PRD section 6. Include explicit examples for every
rule, including edge cases:

- Multi-word folder names (`mcp-servers` not `mcp_servers`).
- Version suffixes vs frontmatter version field — when each applies.
- Italian vs English tags — examples of each.
- Special folders (`_inbox`, `.github`).
- Acceptable characters and disallowed patterns (with regex).

### 6. Empty folder skeleton

Create the following folders with a `.gitkeep` file (empty file) so they are
tracked even when otherwise empty:

```
_inbox/
docs/
docs/schemas/
skills/
prompts/
prompts/library/
prompts/templates/
mcp-servers/
tools/
stack/
agents/
workflows/
n8n-workflows/
.github/
.github/workflows/
```

For `_inbox/`, add a `README.md` (not just `.gitkeep`) explaining that
contents are gitignored and processed by the `librarian` skill.

### 7. Update `.gitignore`

Append the following block to the existing `.gitignore`:

```
# Inbox: contents not tracked, structure tracked via README
_inbox/*
!_inbox/.gitkeep
!_inbox/README.md

# uv
.python-version

# Backups
INDEX.md.bak
```

Do not remove existing entries.

### 8. `pyproject.toml` at repo root

Minimal `pyproject.toml` for `uv`:

```toml
[project]
name = "aithos-selection"
version = "0.1.0"
description = "Curated knowledge base of AI primitives"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "typer>=0.12",
    "rich>=13.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pre-commit>=3.7",
]

[tool.uv]
package = false
```

**Do not** install dependencies or run `uv sync` in this phase. Phase 3 will
do that when the first script is created.

### 9. Canonical example content

Create two minimal example items that exercise the schemas. These serve as
living documentation and as inputs for `check.py` in Phase 4. They are not
deletable.

#### 9a. Example prompt: `prompts/library/example-hello-world.md`

```markdown
---
id: example-hello-world
name: Example Hello World Prompt
type: prompt
status: stable
version: 1.0.0
description: Canonical example prompt to validate the frontmatter schema
tags: [example, canonical]
language: en
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---

# Hello World Prompt

This is the canonical example prompt used to validate the frontmatter
schema. Do not delete.

## Instructions

Respond with "Hello, world!" exactly.
```

#### 9b. Example agent: `agents/example-echo-agent/`

Three files:

`agents/example-echo-agent/agent.md` — minimal system prompt:

```markdown
# Echo Agent

You are an echo agent. Repeat the user's input verbatim, prefixed with
"Echo: ".
```

`agents/example-echo-agent/manifest.yaml`:

```yaml
name: example-echo-agent
version: 0.1.0
type: agent
description: Canonical example agent to validate the manifest schema
status: stable
tags: [example, canonical]
created: 2026-05-15
updated: 2026-05-15

system_prompt: ./agent.md

uses:
  prompts:
    - prompts/library/example-hello-world.md
```

`agents/example-echo-agent/README.md`:

```markdown
# Example Echo Agent

Canonical example agent. Echoes user input verbatim. Used to validate the
manifest schema in `check.py`. Do not delete.
```

## Done criteria

Run these checks in order. All must pass before committing.

```bash
# Files exist
test -f README.md
test -f CONTRIBUTING.md
test -f pyproject.toml
test -f docs/schemas/manifest.schema.yaml
test -f docs/schemas/frontmatter.schema.yaml
test -f docs/naming-conventions.md
test -f _inbox/README.md
test -f prompts/library/example-hello-world.md
test -f agents/example-echo-agent/agent.md
test -f agents/example-echo-agent/manifest.yaml
test -f agents/example-echo-agent/README.md

# Folders exist
for f in skills prompts/library prompts/templates mcp-servers tools stack agents workflows n8n-workflows .github/workflows; do
  test -d "$f" || { echo "Missing: $f"; exit 1; }
done

# Git tree shows expected new files
git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-1): foundation — governance docs, schemas, folder skeleton"
git push
```

## Stop here

Do not start Phase 2 in the same run. Stop after the commit succeeds and
wait for explicit user instruction.
