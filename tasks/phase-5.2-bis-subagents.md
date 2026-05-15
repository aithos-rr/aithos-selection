# Phase 5.2-bis — Subagents extension and import

## Goal

Add **Claude Code subagents** as a new top-level category of the
repository, parallel to `skills/`, `agents/`, `prompts/`, `workflows/`,
and `references/`. A subagent is a Claude Code primitive: an
agent-like prompt with declared `tools` and `mcpServers`, invoked via
slash-command (`/subagent-name`) and living in `.claude/agents/` of a
project at deploy time.

After the system extension, import the 6 subagent bundles currently
left in `_inbox/` as public materials sourced from Learnn community
courses.

## Background

In Phase 5.2, 6 zips were correctly flagged as "non-standard layout"
because they don't contain `SKILL.md` or `agent.md` but instead a
`<name>/<name>.md` file with a Claude Code subagent frontmatter:

```yaml
---
name: automation-architect
description: ...
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, Glob, AskUserQuestion
mcpServers:
  - n8n-knowledge
  - context7
skills:
  - workflow-designer
  - node-validator
memory: project
---
```

These are real Claude Code subagents (Anthropic primitive), distinct
from the project's existing `agents/` category (which holds declarative
agents with system_prompt + manifest). They need their own home.

## Prerequisites

- Phase 5.2 complete and committed on `feat/ingest-assets-batch-1`.
- Working tree clean, current branch `feat/ingest-assets-batch-1`.
- The 6 subagent zips are still present in `_inbox/`:
  `automation-architect.zip`, `competitor-deep-dive.zip`,
  `lead-finder-pro.zip`, `outbound-orchestrator.zip`,
  `seo-strategist.zip`, `web-builder.zip`.

## High-level flow

1. **System extension** (deliverables §1–§5): new `subagents/`
   folder, schema, librarian update, generator update, validator
   update, CONTRIBUTING update, README update.
2. **Bulk import** (deliverable §6): extract the 6 zips into
   `subagents/<name>/`, generate the Aithos-side manifest for each.
3. **Validate**.
4. **Commit and push** (same branch `feat/ingest-assets-batch-1`).

## Deliverables — Part A: system extension

### 1. New folder

Create `subagents/` at repo root with a `.gitkeep`. No subfolders;
each subagent lives in its own directory directly under `subagents/`.

### 2. Schema — `docs/schemas/subagent.schema.yaml`

A JSON-Schema-compatible YAML schema for subagent **manifest.yaml**
files (the Aithos-side manifest, separate from the inner subagent
frontmatter which follows the Anthropic format).

Required fields for `subagents/<name>/manifest.yaml`:

- `name` (string, kebab-case, matches folder name)
- `version` (string, semver)
- `type` (literal: `"subagent"`)
- `description` (string, one-line summary)
- `status` (enum: `"draft"` | `"stable"` | `"deprecated"`)
- `tags` (array of strings)
- `language` (enum: `"it"` | `"en"` | `"multilingual"`)
- `origin` (object with `source`, `url` optional, `notes` optional)
- `entrypoint` (string, relative path to the main subagent `.md`
  file, e.g. `./automation-architect.md`)
- `created` (date)
- `updated` (date)
- `author` (string)

Optional fields:

- `tools` (array of strings, mirrors the subagent's declared tools
  for quick scanning without opening the entrypoint)
- `mcp_servers` (array of strings, mirrors the declared MCP servers)
- `skills_dependencies` (array of skill ids declared in the subagent
  frontmatter — useful for the inverse dependency graph)
- `memory` (enum: `"project"` | `"none"`)

Document in the schema's description that subagent contents may also
include `BUILD-BRIEF.md`, `ARCHITECTURE.md`, `PROGRESS.md`,
`README.md`, `references/`, `discovery/`, `research/`,
`test-fixtures/` — these are not validated but documented as common.

### 3. Generator update — `tools/generate_index.py`

Extend the generator:

1. Add a `discover_subagents(root: Path)` function that walks
   `subagents/*/manifest.yaml`, parses each, returns a list of
   Subagent objects.
2. Add a new section `## Subagents` to `INDEX.md`, between `Composites`
   and `Recipes`. Subagents are conceptually closer to composites
   (multi-file, declarative) than to recipes (workflows), so their
   placement is between the two.
3. Table columns: `Name`, `Status`, `Origin`, `Tools (count)`,
   `MCP (count)`, `Skills (count)`, `Description`.
4. Subagents participate in the inverse dependency graph: if a
   subagent declares `skills_dependencies: [foo, bar]`, those entries
   show up in the inverse graph as "used by subagent `<name>`".
5. Export `discover_subagents` so `tools/check.py` can import it.

### 4. Validator update — `tools/check.py`

Extend the validator with two new checks:

1. **Subagent manifest compliance** — each `subagents/*/manifest.yaml`
   validates against `docs/schemas/subagent.schema.yaml`.
2. **Subagent entrypoint exists** — the file referenced by
   `entrypoint` in each manifest exists.

Both appear as additional rows in the summary table. Also extend the
existing `composite_completeness` check to skip subagents (they have
their own structure, different from `agents/`).

### 5. Librarian update — `skills/librarian/SKILL.md` and references

Update the librarian skill:

1. **`SKILL.md`** — update the `description` field in frontmatter to
   mention subagents as a recognized category. Add a paragraph in
   the body explaining when something should be classified as a
   subagent (vs skill, vs agent).
2. **`references/classification-heuristics.md`** — add a section on
   subagent identification:
   - Zip extracts to `<name>/<name>.md`
   - That file has a frontmatter with `name`, `description`, and at
     least one of: `tools`, `mcpServers`, `skills`
   - Optional supporting files: `BUILD-BRIEF.md`, `ARCHITECTURE.md`,
     `PROGRESS.md`, `README.md`, `references/`, `discovery/`,
     `research/`, `test-fixtures/`
3. **`references/manifest-examples.md`** — add one canonical subagent
   manifest example.
4. **`references/taxonomy.md`** — add two new subtype-hint tags:
   `learnn` (for Learnn-sourced public materials) and
   `community-resource` (for any third-party public material).

### 6. README and CONTRIBUTING updates

**README.md**:
- In the Mental model section, mention that subagents are a fifth
  layer between composites and recipes (orchestrated agents with
  declared tools, MCP servers, and skill dependencies, invoked as
  Claude Code slash-commands).
- In the Folder map, add `subagents/` between `agents/` and
  `workflows/`.

**CONTRIBUTING.md**:
- Add a new section `## Adding a subagent` after the existing
  `## Adding a reference` section. Include:
  - When to add a subagent vs a skill or agent.
  - The required structure (folder with entrypoint .md +
    manifest.yaml).
  - A concrete frontmatter example for the inner subagent file (the
    Anthropic format).
  - A concrete manifest.yaml example (the Aithos manifest with
    schema-required fields).
  - A note on `origin: { source: learnn, url: ..., notes: ... }`
    for third-party materials.

## Deliverables — Part B: ingestion

### 7. Import the 6 subagent zips from `_inbox/`

For each of the 6 zips, in this order (smallest first to validate the
flow quickly):

1. `seo-strategist.zip`
2. `web-builder.zip`
3. `lead-finder-pro.zip`
4. `competitor-deep-dive.zip`
5. `outbound-orchestrator.zip`
6. `automation-architect.zip`

Processing per zip:

1. **Extract** to `_inbox/.tmp-extract/<name>/`.
2. **Verify structure**: the extraction must produce a top-level
   directory `<name>/` containing at least `<name>.md` (or in some
   cases `<name>/<name>.md` may not exist — `seo-strategist.zip` for
   example shows a different layout; treat as a flag in the report).
   For the cases where the entrypoint is not exactly `<name>/<name>.md`,
   inspect the directory: there's exactly one `.md` file at depth 1
   that has the Anthropic subagent frontmatter — that becomes the
   entrypoint.
3. **Parse the entrypoint frontmatter** to extract: `name`,
   `description`, `tools`, `mcpServers`, `skills`, `memory`.
4. **Move the entire extracted folder** to `subagents/<name>/`.
5. **Generate `subagents/<name>/manifest.yaml`** with:
   - `name`: from frontmatter `name` field (must match folder name)
   - `version`: `1.0.0`
   - `type`: `subagent`
   - `description`: first 150 chars of the `description` field,
     truncated cleanly at a word boundary
   - `status`: `stable`
   - `tags`: derive from content — always include `learnn`,
     `community-resource`. Add 2-4 topical tags inferred from the
     description and the subagent name (e.g. for
     `automation-architect`: `automation`, `n8n`, `workflow`; for
     `seo-strategist`: `seo`, `marketing`; etc.)
   - `language`: `it` (the Learnn audience is Italian, descriptions
     are bilingual but Italian-leaning)
   - `origin`:
     ```yaml
     origin:
       source: learnn
       notes: Public material from Learnn community courses, saved
         by Riccardo for future work reference.
     ```
   - `entrypoint`: relative path to the discovered entrypoint
     `.md` file (typically `./<name>.md`)
   - `tools`: copy the `tools` array from the entrypoint frontmatter
     (if present) as a list of strings
   - `mcp_servers`: copy the `mcpServers` array (if present)
   - `skills_dependencies`: copy the `skills` array (if present)
   - `memory`: copy `memory` field (if present), default to `"none"`
   - `created`: today
   - `updated`: today
   - `author`: `learnn`
6. **Validate** the generated manifest against the schema.
7. **Delete** the original zip from `_inbox/` only after successful
   move + manifest generation + validation.

### 8. ID collision and edge cases

- Folder names must match the subagent's declared `name`. If
  collision occurs (folder `subagents/<name>/` already exists), skip
  and flag.
- The `frontend-design.zip` previously imported in Phase 5.2 (now in
  `skills/frontend-design/`) is unrelated — different concept (skill
  vs subagent). No conflict.
- If a subagent zip's content lacks the expected frontmatter or has
  malformed YAML, skip and flag.

### 9. Cleanup

- Remove `_inbox/.tmp-extract/` directory.
- The `_inbox/` should now contain only `.gitkeep` and `README.md`.

### 10. Validation

```bash
uv run python tools/generate_index.py
uv run python tools/check.py
```

Both must pass. Specifically `check.py` must report:
- All 6 (or fewer if any were flagged) subagent manifests valid.
- All entrypoints exist.
- INDEX up to date with the new Subagents section.

### 11. Final report

```
Subagents extension and import complete.

System extensions:
  - subagents/ folder created
  - docs/schemas/subagent.schema.yaml
  - generate_index.py extended (discover_subagents, Subagents section)
  - check.py extended (manifest compliance, entrypoint existence)
  - librarian skill updated (description, heuristics, taxonomy)
  - README and CONTRIBUTING updated

Subagents imported (subagents/):
  - seo-strategist     (Learnn / SEO strategy)
  - web-builder        (Learnn / fullstack web)
  - lead-finder-pro    (Learnn / lead generation)
  - competitor-deep-dive (Learnn / competitor analysis)
  - outbound-orchestrator (Learnn / outbound sales)
  - automation-architect (Learnn / n8n automation)

Manifests generated: 6 / 6
All checks passing.
Commit ready.
```

## Done criteria

```bash
# Folder structure
test -d subagents
test -f subagents/.gitkeep

# Schema
test -f docs/schemas/subagent.schema.yaml

# All 6 subagents imported (or fewer if flagged)
test $(ls subagents/ | grep -v .gitkeep | wc -l) -ge 1

# Each has a manifest
for d in subagents/*/; do
  name=$(basename "$d")
  test -f "$d/manifest.yaml" || { echo "Missing manifest for $name"; exit 1; }
done

# Inbox cleaned
test ! -d _inbox/.tmp-extract
test $(ls _inbox/ | grep -v -E '^\.gitkeep$|^README\.md$' | wc -l) -eq 0

# Validation passes
uv run python tools/generate_index.py --check
uv run python tools/check.py

# INDEX includes subagents
grep -q "## Subagents" INDEX.md

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.2-bis): subagents extension + import 6 Learnn subagents

Added new top-level category 'subagents/' for Claude Code subagent
primitives. Imported 6 community subagents from Learnn courses as
public reference materials (author: learnn). Tooling extended for
discovery, validation, and indexing. Documentation updated."
git push
```

## Stop here

After commit and push, stop. The PR for `feat/ingest-assets-batch-1`
remains open (or to-be-opened) on the same branch — Phase 5.2 and
Phase 5.2-bis ship together as a single PR titled "Import asset
batch 1".

The user will open the PR command after later phases (or now if they
prefer), with an updated title that reflects both phases:

```
gh pr create --base main --head feat/ingest-assets-batch-1 \
  --title "Import asset batch 1 — skills, prompts, subagents" \
  --body "Phases 5.2 + 5.2-bis: 27 skills/prompts + 6 Learnn subagents.
folder-as-prompt structural variant. subagents/ new top-level category."
```

## Safety brakes

- Do not modify any of the 27 assets already imported in Phase 5.2.
- Do not modify `skills/frontend-design/` (already imported, named
  similarly to a hypothetical future subagent but it IS a skill).
- No network calls.
- If extraction fails for any zip, skip that one and continue with the
  others. Report at the end.
