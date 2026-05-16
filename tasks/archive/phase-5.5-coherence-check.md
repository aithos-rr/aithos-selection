# Phase 5.5 — Coherence Check

## Goal

After many phases of construction and ingestion (1 through 5.4), the
repository's documentation needs an audit pass. This phase performs a
**coherence check**: it verifies that every governance document
(README, CONTRIBUTING, CLAUDE.md, PRD.md, naming conventions, librarian
skill) is **internally consistent and aligned with the current state
of the repository**.

The phase also addresses two concrete pieces of housekeeping:

- Move historical task files (Phases 1-4) to `tasks/archive/` to
  reduce clutter while preserving them in git history.
- Generate sensible auto-descriptions for assets that currently have
  placeholder content (mainly imported skills/subagents whose
  `description` was auto-inferred and may need polish).

## Design choices (decided with user)

- **Run order**: after all other phases (5.2 + 5.2-bis + 5.3 + 5.4),
  in a single final pass.
- **Task archival**: phases 1-4 task specs → `tasks/archive/`. The
  current "active" tasks/ contains only ongoing work (none after
  this phase).
- **Description placeholders**: CC pre-cooks improved descriptions
  based on file content; user reviews on the resulting commit.

## Prerequisites

- Phases 1-5.4 complete and committed across multiple branches:
  `feat/ingest-assets-batch-1`, `feat/install-script`,
  `feat/nightly-sync`. All have associated PRs (open or
  to-be-opened).
- Working tree clean, current branch `feat/nightly-sync`.
- Phase 5.5 work happens on a new branch off `feat/nightly-sync`:

  ```bash
  git checkout feat/nightly-sync
  git checkout -b feat/coherence-check
  ```

## High-level flow

1. **Audit pass**: read every governance document and identify
   inconsistencies, gaps, or stale content.
2. **Generate improvements** for each issue found, in the order:
   - README.md updates
   - CONTRIBUTING.md updates
   - CLAUDE.md updates
   - PRD.md updates
   - docs/naming-conventions.md updates
   - skills/librarian/SKILL.md description refresh
3. **Pre-cook descriptions** for imported skills/subagents with weak
   or placeholder descriptions, based on the actual content of their
   SKILL.md / agent.md / entrypoint files.
4. **Archive historical task files** to `tasks/archive/`.
5. **Single coherence report**: show all proposed changes in one
   pass (since this is auto-pilot, CC applies them; the user
   reviews the resulting commit afterwards).
6. **Validate, commit, push**.

## Deliverables

### 1. Inventory the current state

Build a complete picture of what the repo currently contains, to
compare against what the docs claim it contains:

- Number of skills in `skills/`
- Number of agents in `agents/`
- Number of subagents in `subagents/`
- Number of prompts in `prompts/library/` (separating single-file
  and folder-as-prompt)
- Number of reference files in `references/repos/` and the (empty
  for now) `references/articles/`, `references/templates/`
- Number of MCP servers in `mcp-servers/`
- Number of tools in `tools/`
- Number of stack notes in `stack/`
- The full list of top-level categories the repo currently
  recognizes
- The full list of sub-flows the librarian skill currently exposes

This inventory is the source of truth for the coherence check.

### 2. README.md audit and update

Read README.md and verify:

- **Mental model section**: lists 5 layers (atoms, composites,
  subagents, recipes, references) or accurately reflects the
  current categorization? If outdated (e.g. only mentions 3
  layers because Phase 5.0 update was minimal), regenerate the
  section to reflect the current state. Use one short paragraph
  per layer with one concrete example.
- **Folder map section**: lists every top-level category that
  exists? Each entry has a one-line description that matches the
  category's actual purpose?
- **Quick start section**: mentions the nightly-sync evening
  routine? The install.py tool?
- **Length**: still within ~100-200 lines? If grown beyond,
  consider trimming.

Apply needed changes.

### 3. CONTRIBUTING.md audit and update

Read CONTRIBUTING.md and verify:

- Has sections for adding each type currently supported: prompt
  (including folder-as-prompt), MCP server, stack note, agent,
  subagent, workflow, reference.
- Each "Adding X" section includes: target folder, required
  frontmatter/manifest, concrete example.
- The "Deploying skills and subagents" section reflects the
  current `install.py` interface.
- The "Evening routine" section is present and accurate.
- The three golden rules at the top are still relevant.

Apply needed changes.

### 4. CLAUDE.md audit and update

Read CLAUDE.md and verify:

- The folder structure listed reflects the current repo (with
  `subagents/`, `references/`, etc.).
- Stack constraints are still accurate (Python 3.12, uv, allowed
  libraries).
- Commit protocol scopes are up to date (the list of allowed
  `<scope>` values now includes the new phase scopes).
- The "When in doubt" section still points to PRD.md and tasks/.

Apply needed changes.

### 5. PRD.md audit and update

Read PRD.md and verify:

- The "Mental model" section in PRD (more detailed than README's)
  reflects all 5 layers.
- The "Folder structure" section matches reality.
- The "Phase overview" section shows which phases are complete.
  Add a brief addendum noting that bootstrap is complete and the
  repo is now in maintenance mode (using nightly-sync for ongoing
  intake).
- Schemas section (§5) mentions the reference schema and the
  subagent schema, not just the original three (manifest,
  frontmatter, reference).
- Done criteria section (§10) — mark as complete the things that
  are now complete.

Apply needed changes.

### 6. docs/naming-conventions.md audit and update

Read this doc and verify:

- Covers `subagents/` as a top-level category.
- Covers folder-as-prompt naming.
- Mentions the `feat/<name>` branch pattern that has emerged.

Apply needed changes.

### 7. Skill description refresh

For each imported skill in `skills/` (excluding `librarian` which is
canonical and unchanged):

1. Read the skill's `SKILL.md` frontmatter `description` field.
2. If the description is short (< 20 words), generic, or appears
   to be auto-generated boilerplate, generate an improved
   description (1-2 sentences, 30-80 chars typically; longer
   only if the skill genuinely warrants it).
3. The improved description should:
   - Lead with a verb (e.g. "Generates landing page copy from a
     structured brief...")
   - State what the skill does, not what it is (e.g. NOT "A
     landing page generator skill")
   - Include the primary use case in the same sentence
4. Update the frontmatter in place.
5. Log the change.

Apply the same logic to subagents in `subagents/` (using the
entrypoint's `description` field, which is the Anthropic-format
field, AND the manifest.yaml `description` field, which is the
Aithos-side mirror).

For the canonical examples (`prompts/library/example-hello-world.md`,
`agents/example-echo-agent/`, `references/repos/example-anthropic-sdk-python.md`):
do NOT touch their descriptions. They are intentionally meta-references.

### 8. Archive historical task files

Move the bootstrap-era task files to `tasks/archive/`:

- `tasks/phase-1-foundation.md`
- `tasks/phase-2-librarian.md`
- `tasks/phase-3-index.md`
- `tasks/phase-4-check.md`
- `tasks/phase-5.0-references.md`
- `tasks/phase-5.1-stars.md`
- `tasks/phase-5.2-assets.md`
- `tasks/phase-5.2-bis-subagents.md`
- `tasks/phase-5.3-install.md`
- `tasks/phase-5.4-nightly-sync.md`
- `tasks/phase-5.5-coherence-check.md` (THIS task file, after
  Phase 5.5 commits and stops — see below)

After this phase, `tasks/` directory should contain ONLY:

- `tasks/archive/` (a subfolder with the 10 historical specs)
- Optionally a `tasks/README.md` explaining what `tasks/` is and
  that "active" tasks are now empty because bootstrap is complete

Create `tasks/README.md` (~30 lines):

```markdown
# Tasks

This directory holds task specifications for one-off phases of work
on this repository. Each task is a self-contained spec that an
agent (typically Claude Code) can follow autonomously.

During the bootstrap (Phases 1 through 5.5), this directory
contained the specs for each construction phase. Those are now in
`archive/` for historical reference.

## Active tasks

(None — bootstrap is complete.)

## Archived tasks

See `archive/` for the completed bootstrap phases.
```

Important: the move of `tasks/phase-5.5-*.md` should happen AS
PART of the work, but the spec file you're reading right now will
still exist on disk at the time you read it. Move it as the very
last action before commit.

### 9. Final coherence report

Print a structured report with sections:

```
Coherence Check Report

Inventory (current state):
  Skills:     <N>
  Agents:     <N>
  Subagents:  <N>
  Prompts:    <N> (single-file: <X>, folder: <Y>)
  References: <N> (repos: <X>, articles: <Y>, templates: <Z>)
  MCP:        <N>
  Tools:      <N>
  Stack:      <N>

Documents audited:
  - README.md: <updates applied | already coherent>
  - CONTRIBUTING.md: <updates applied | already coherent>
  - CLAUDE.md: <updates applied | already coherent>
  - PRD.md: <updates applied | already coherent>
  - docs/naming-conventions.md: <updates applied | already coherent>
  - skills/librarian/SKILL.md (frontmatter description): <updates applied | already coherent>

Description refreshes:
  Skills:    <N> updated
  Subagents: <N> updated
  Prompts:   <N> updated

Task archive:
  Moved <N> task files to tasks/archive/
  Created tasks/README.md

Validation: all checks pass.
Commit: <hash>, pushed to feat/coherence-check.
```

If a section finds no changes needed, say "already coherent" — do
not invent changes for the sake of having something to do.

### 10. Validate

```bash
uv run python tools/generate_index.py
uv run python tools/check.py
```

Both must pass.

## Done criteria

```bash
# Archive folder created
test -d tasks/archive
ls tasks/archive/ | wc -l   # should be >= 10

# tasks/ contains only README.md and archive/
ls tasks/ | grep -v -E '^README\.md$|^archive$' | wc -l   # should be 0

# tasks/README.md exists
test -f tasks/README.md

# Documents are intact (no accidental wipes)
test -s README.md
test -s CONTRIBUTING.md
test -s CLAUDE.md
test -s PRD.md

# Validation passes
uv run python tools/generate_index.py --check
uv run python tools/check.py

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.5): coherence check — docs audit, description refresh, task archive

Final pass of the bootstrap. Audited README, CONTRIBUTING, CLAUDE,
PRD, naming-conventions, and the librarian skill description for
internal consistency with the current state of the repository.
Refreshed auto-generated descriptions on imported skills and
subagents. Moved historical task specs (Phases 1-5.5) to
tasks/archive/, leaving tasks/ with only README.md and archive/.

Bootstrap is now complete. Future work uses the nightly-sync
sub-flow for ongoing intake."
git push -u origin feat/coherence-check
```

## Stop here

After commit and push, stop and report.

This is the final phase of the bootstrap. The user will then merge
all four open PRs in order:

1. PR for `feat/ingest-assets-batch-1` (Phases 5.2 + 5.2-bis)
2. PR for `feat/install-script` (Phase 5.3)
3. PR for `feat/nightly-sync` (Phase 5.4)
4. PR for `feat/coherence-check` (Phase 5.5, to be created after
   commit)

Each merges into `main` sequentially, since each branch is built on
the previous one.

## Safety brakes

- No network calls.
- Do not modify any imported content (skills, subagents, prompts,
  references) beyond the `description` field refresh.
- Do not modify canonical examples.
- Do not modify tools/*.py scripts.
- The task spec file you are reading (this very file) must be the
  LAST thing moved into archive, after all other changes are
  committed-ready. If something fails before the final commit,
  this file should remain accessible.
