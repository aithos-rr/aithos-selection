# Manifest examples

Canonical, validated examples of `manifest.yaml` files for composites
(`agents/`) and recipes (`workflows/`). Use them as drop-in templates when
the librarian proposes a new agent or workflow.

All examples obey:

- The schema at `/docs/schemas/manifest.schema.yaml`.
- The naming conventions in `/docs/naming-conventions.md`.
- The tag taxonomy in `./taxonomy.md`.

Paths in `system_prompt`, `uses.*`, `agents`, and `n8n_workflows` follow the
rules from PRD section 5.1: `system_prompt` is relative to the manifest;
everything else is relative to the repo root.

## 1. Minimal agent

The smallest manifest that still satisfies the schema. One prompt
dependency, no MCP servers, no tools.

File: `agents/agent-echo/manifest.yaml`

```yaml
name: agent-echo
version: 0.1.0
type: agent
description: Echoes user input verbatim — used as a smoke-test agent
status: draft
tags: [example, general, english]
created: 2026-05-15
updated: 2026-05-15

system_prompt: ./agent.md

uses:
  prompts:
    - prompts/library/example-hello-world.md
```

Notes:

- `system_prompt` points at the sibling `agent.md` with a `./` prefix.
- `uses.prompts` references the canonical example prompt from the repo
  root.
- No `mcp_servers`, no `tools`, no `templates` — all optional.

## 2. Complete agent

A realistic agent that combines prompts, a parametric template, an MCP
server, and a Python tool.

File: `agents/agent-doc-analyst/manifest.yaml`

```yaml
name: agent-doc-analyst
version: 1.0.0
type: agent
description: Extracts structured data from Italian legal documents
status: stable
tags: [extraction, legal, italian, pdf-parsing, production]
created: 2026-04-12
updated: 2026-05-10

system_prompt: ./agent.md

uses:
  prompts:
    - prompts/library/doc-extraction-v2.md
  templates:
    - prompts/templates/lead-summary.md
  mcp_servers:
    - mcp-servers/filesystem.json
    - mcp-servers/linear-mcp.json
  tools:
    - tools/pdf-parse.py
```

Notes:

- Every dependency is referenced by repo-root-relative path.
- Tags combine a category (`extraction`), a domain (`legal`), a language
  (`italian`), a technique (`pdf-parsing`), and a status tag
  (`production`).
- The agent does **not** copy any of the referenced atoms — they live in
  their own folders. The manifest is the single source of truth for the
  dependency graph.

## 3. Workflow combining two agents and one n8n flow

A recipe that orchestrates two agents plus an n8n trigger flow.

File: `workflows/wf-lead-qualification/manifest.yaml`

```yaml
name: wf-lead-qualification
version: 0.2.0
type: workflow
description: Qualifies inbound leads via doc analysis and CRM enrichment
status: draft
tags: [sales, crm, italian, automation, multilingual]
created: 2026-05-01
updated: 2026-05-15

agents:
  - agents/agent-doc-analyst
  - agents/agent-crm-enricher

uses:
  prompts:
    - prompts/library/lead-summary.md

n8n_workflows:
  - n8n-workflows/wf-lead-qualification-trigger/flow.json
```

Notes:

- `type: workflow` requires the `agents` field with at least one entry
  (enforced by the manifest schema).
- A workflow has **no** `system_prompt` field — that belongs to agents.
- `n8n_workflows` is optional; include it only when the recipe genuinely
  has an n8n component. Pure n8n flows that are not orchestrated by Claude
  belong directly in `/n8n-workflows/`, not here.
- The companion `flow.md` and `README.md` in the workflow folder describe
  the human-readable steps and the purpose; they do not replace the
  manifest.
