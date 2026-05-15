# Contributing to Aithos Selection

This guide tells you how to add and update content in this repository.
Strategic context lives in [`PRD.md`](./PRD.md); session invariants live in
[`CLAUDE.md`](./CLAUDE.md). When in doubt, those two files win.

## The three golden rules

1. **No duplication.** Every atom — a prompt, a skill, an MCP config, a tool,
   a stack note — lives in exactly one folder. Composites (agents) and
   recipes (workflows) reference atoms through their `manifest.yaml`. Never
   copy a prompt into an agent folder; reference it by path instead.

2. **Manifest is the source of truth.** When an agent or workflow declares
   what it uses, it does so in `manifest.yaml`. Prose in a `README.md` may
   describe the relationship for humans, but the manifest is what scripts
   like `generate_index.py` and `check.py` read.

3. **Markdown and YAML only for content.** No proprietary formats. JSON is
   reserved for machine-generated artifacts (n8n workflow exports, MCP server
   configs in their native JSON format). All human-edited content is
   Markdown (prose) or YAML (structured).

## Adding a new prompt

Prompts live in `prompts/library/` (finished, versioned, ready to use) or
`prompts/templates/` (parametric, contain `{{variables}}`).

Steps:

1. Pick the target folder: `prompts/library/` if the prompt is concrete and
   ready to send as-is, `prompts/templates/` if it has placeholders.
2. Name the file in kebab-case, ending in `.md`. The file stem must match
   the `id` in the frontmatter. Example: `doc-extraction-v2.md`.
3. Add frontmatter at the top of the file. Required fields:

   ```yaml
   ---
   id: doc-extraction-v2
   name: Document Extraction (v2)
   type: prompt              # or "template" for prompts/templates/
   status: stable            # draft | stable | deprecated
   version: 2.0.0            # semver
   description: One-line summary of what the prompt does
   tags: [extraction, italian, legal]
   language: it              # it | en | multilingual
   created: 2026-05-15
   updated: 2026-05-15
   author: riccardo
   ---
   ```

4. Write the prompt body in Markdown below the frontmatter.
5. If this is a new major version of an existing prompt, suffix the filename
   with `-v2` (or higher) and mark the previous one as
   `status: deprecated`. See the *Updating an existing atom* section below.

## Adding a new MCP server config

MCP server configs live in `mcp-servers/` in their native JSON format. The
folder is flat — one server per file.

Steps:

1. Name the file in kebab-case, ending in `.json`. Example:
   `linear-mcp.json`.
2. Use the native MCP server configuration format. Do not wrap it in an
   Aithos-specific envelope.
3. If the config needs accompanying notes (auth setup, scopes, gotchas),
   create a sibling Markdown file with the same stem and a frontmatter block:
   `mcp-servers/linear-mcp.md`. Frontmatter for this companion file uses
   `type: stack-note`.

## Adding a new stack note

Stack notes are operational playbooks for tools and services you actually
use (e.g. `vscode`, `supabase`, `lm-studio`). One Markdown file per tool,
lives in `stack/`.

Steps:

1. Name the file after the tool in kebab-case, ending in `.md`. Example:
   `supabase.md`.
2. Add frontmatter:

   ```yaml
   ---
   id: supabase
   name: Supabase
   type: stack-note
   status: stable
   version: 1.0.0
   description: Operational notes for Supabase usage in Aithos projects
   tags: [database, backend, postgres]
   language: en
   created: 2026-05-15
   updated: 2026-05-15
   author: riccardo
   ---
   ```

3. Structure the body around: setup, configuration, common tasks, known
   issues, links. Keep it task-oriented; this is a playbook, not a tutorial.

## Adding a new agent

Each agent is a self-contained folder under `agents/`.

Steps:

1. Create `agents/<agent-name>/` in kebab-case. Example:
   `agents/agent-doc-analyst/`.
2. Inside, create three files:
   - `agent.md` — the system prompt, plain Markdown.
   - `manifest.yaml` — dependency declarations and metadata.
   - `README.md` — what the agent does, when to use it, examples.
3. Reference atoms in `manifest.yaml` by path relative to repo root. Do not
   copy atoms into the agent folder.
4. Optionally add an `examples/` subfolder with sample input/output
   transcripts.

Minimal canonical manifest:

```yaml
name: agent-doc-analyst
version: 0.1.0
type: agent
description: Extracts structured data from Italian legal documents
status: draft
tags: [extraction, italian, legal]
created: 2026-05-15
updated: 2026-05-15

system_prompt: ./agent.md

uses:
  prompts:
    - prompts/library/doc-extraction-v2.md
  mcp_servers:
    - mcp-servers/filesystem.json
  tools:
    - tools/pdf-parse.py
```

See `agents/example-echo-agent/` for the canonical example.

## Adding a new workflow

Workflows orchestrate one or more agents (and optionally n8n flows) into a
complete recipe. Each workflow is a folder under `workflows/`.

Steps:

1. Create `workflows/<workflow-name>/` in kebab-case. Example:
   `workflows/wf-lead-qualification/`.
2. Inside, create:
   - `README.md` — purpose, inputs, outputs, KPIs.
   - `flow.md` — step-by-step human-readable description of the flow.
   - `manifest.yaml` — dependency declarations.
   - `n8n.json` — optional, only if the workflow includes an n8n component.
3. Reference agents and atoms by path; never copy them.

Minimal canonical manifest:

```yaml
name: wf-lead-qualification
version: 0.1.0
type: workflow
description: Qualifies inbound leads via doc analysis and CRM enrichment
status: draft
tags: [sales, crm, italian]
created: 2026-05-15
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

Pure n8n flows that are not orchestrated by Claude live directly in
`n8n-workflows/` instead.

## Adding a reference

References are structured bookmarks for external resources the repository
wants to remember but not ingest — GitHub repositories, blog posts and
papers, workflow or skill templates found online. They are a fourth
category alongside atoms, composites, and recipes: composites and
recipes never declare a reference under `uses:`. References are pure
curation.

The three subtypes and where to put each:

| Subtype    | Folder                    | When to use                                                  |
|------------|---------------------------|--------------------------------------------------------------|
| `repo`     | `references/repos/`       | GitHub (or other code-host) repositories you want to track.  |
| `article`  | `references/articles/`    | Blog posts, papers, documentation pages, tweets.             |
| `template` | `references/templates/`   | n8n workflow templates, skill or agent templates from gists. |

Required frontmatter (validated by
[`docs/schemas/reference.schema.yaml`](./docs/schemas/reference.schema.yaml)):

```yaml
---
id: example-anthropic-sdk-python      # kebab-case, unique in the subfolder
name: Anthropic SDK Python            # human-readable title
type: reference                       # always this literal
subtype: repo                         # repo | article | template
url: https://github.com/anthropics/anthropic-sdk-python
status: active                        # active | archived | broken
description: Official Python SDK for the Anthropic API
tags: [example, canonical, anthropic, sdk, python]
language: en                          # it | en | multilingual
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---
```

For `subtype: repo` you may add the optional GitHub snapshot fields
`github_owner`, `github_repo`, `github_stars`, `github_language`,
`github_topics`, `github_last_commit`. They are a snapshot taken at
import time — not kept live.

Example frontmatter for an article:

```yaml
---
id: anthropic-engineering-skills
name: Equipping Agents for the Real World with Agent Skills
type: reference
subtype: article
url: https://www.anthropic.com/engineering/agent-skills
status: active
description: How Anthropic designs skills as a primitive for Claude agents
tags: [analysis, anthropic-skill, general, english]
language: en
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---
```

Example frontmatter for a template:

```yaml
---
id: n8n-rag-starter
name: RAG Starter Template
type: reference
subtype: template
url: https://n8n.io/workflows/2345-rag-starter
status: active
description: An n8n workflow template wiring up a basic RAG pipeline
tags: [automation, n8n-template, general, english]
language: en
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---
```

The body of every reference file follows a short, fixed template:

```markdown
---
<frontmatter>
---

# <Name>

[<short link text>](<url>)

## Why this is interesting

<Your notes on why this resource was bookmarked. Free-form Markdown.
May be left empty when initially imported in batch.>

## Notes

<Optional additional context, related resources, caveats. Omit when
not needed.>
```

The body stays short by design — references point *outward*. The value
is the URL plus your curation note, not duplicated content.

The constraint `subtype` must equal the parent folder's reference type
(`repo`/`article`/`template`) is enforced by `tools/check.py`. Misplacing
a file in the wrong subfolder fails the validator.

**Preferred path: bulk import.** Use the `librarian` skill's
`process-reference` sub-flow instead of hand-rolling references. The
skill accepts three input modes — a single URL, a Markdown list of URLs
(typically `_inbox/links-dump.md`), or a full GitHub stars import via
`import my GitHub stars`. It proposes paths, frontmatter, and tags as a
plan, and only writes files after your explicit approval. Hand-rolling
is fine for one-offs, but a batch is faster and more consistent through
the skill.

## Using the inbox

`_inbox/` is the quick-dump zone for content you have not yet classified.
Its contents are gitignored (the folder itself is tracked through
`README.md` and `.gitkeep`).

Use the inbox when:

- You are capturing something fast and the classification cost would
  interrupt your flow.
- You are unsure which folder a piece of content belongs to.
- You are batch-importing material that needs human or AI-assisted triage.

Do **not** use the inbox as long-term storage. The `librarian` skill
(Phase 2) processes inbox items, proposes destinations and metadata, and
moves them with your approval.

## Updating an existing atom

Two cases:

**Minor change** (typo, clarification, additional example): edit the file in
place, bump the `version` field in the frontmatter following semver
(`1.0.0` → `1.0.1`), and update the `updated` date.

**Major change** (different intent, breaking modifications to a template,
significant rewrite): create a new file with a version suffix (`-v2`,
`-v3`). Set the previous file's `status` to `deprecated` and keep it for
history. Update any composites that referenced the old version to point at
the new one.

When updating a manifest in `agents/` or `workflows/`, also bump the
manifest's `version` field and the `updated` date.
