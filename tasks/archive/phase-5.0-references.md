# Phase 5.0 — References extension

## Goal

Extend the repository to support **references** — structured bookmarks for
external resources (GitHub repositories, articles, workflow templates) that
the user wants to catalog without ingesting their content. References are a
new top-level category alongside atoms, composites, and recipes. They are
*not* dependencies (workflows do not "use" a reference) — they are pure
curation.

This phase establishes the schema, folder structure, tooling support, and
canonical example. No real content is ingested in this phase (that is
Phase 5.1 and onwards).

## Prerequisites

- Phases 1–4 complete and committed.
- The repository is in a clean, CI-green state (`git status` clean,
  `uv run python tools/check.py` exits 0).
- You are on branch `bootstrap`.

## Deliverables

### 1. New folder structure

Create the following folders, each with a `.gitkeep`:

```
references/
references/repos/
references/articles/
references/templates/
```

The three subfolders correspond to the three reference subtypes:

- `repos/` — GitHub repositories (or other code repository URLs)
- `articles/` — blog posts, papers, documentation pages, tweets
- `templates/` — n8n workflow templates, skill templates, agent templates
  found online

### 2. `docs/schemas/reference.schema.yaml`

A new JSON-Schema-compatible YAML schema for reference frontmatter, separate
from the atom frontmatter schema.

Required fields:

- `id` (string, kebab-case, unique within its subfolder)
- `name` (string, human-readable title)
- `type` (literal: `"reference"`)
- `subtype` (enum: `"repo"` | `"article"` | `"template"`)
- `url` (string, must start with `http://` or `https://`)
- `status` (enum: `"active"` | `"archived"` | `"broken"`)
- `description` (string, one-line summary)
- `tags` (array of lowercase kebab-case strings)
- `language` (enum: `"it"` | `"en"` | `"multilingual"`)
- `created` (date, ISO 8601)
- `updated` (date, ISO 8601)
- `author` (string, default `"riccardo"`)

Optional fields (only meaningful when `subtype: repo`):

- `github_owner` (string)
- `github_repo` (string, full `owner/name` form)
- `github_stars` (integer)
- `github_language` (string, primary language)
- `github_topics` (array of strings)
- `github_last_commit` (date)

The schema must enforce that `subtype` matches the parent folder name (a
file in `references/repos/` has `subtype: repo`, and so on). If JSON Schema
expressing this constraint is awkward, document the rule in the schema
description and enforce it in `tools/check.py` instead.

### 3. Reference Markdown body convention

The body of each reference file follows this template:

```markdown
---
<frontmatter>
---

# <Name>

[<short link text>](<url>)

## Why this is interesting

<User's notes on why this resource was bookmarked. Free-form Markdown.
May be left empty when initially imported in batch — to be filled later.>

## Notes

<Optional additional context, related resources, caveats. May be omitted.>
```

The body is short by design. References point *outward*; their value is the
URL plus the user's curation note, not duplicated content.

### 4. `librarian` skill — new sub-flow `process-reference`

Extend `skills/librarian/SKILL.md` with a new sub-flow `process-reference`.

#### Input modes

The sub-flow accepts three input modes:

- **Single URL** — user provides one URL.
- **List of URLs** — user provides a Markdown file (typically
  `_inbox/links-dump.md`) containing one URL per line.
- **GitHub stars bulk** — special mode triggered by the user phrase
  "import my GitHub stars". The skill uses `gh api
  users/<username>/starred --paginate` to fetch the complete list.

#### Algorithm

For each URL:

1. **Classify subtype**:
   - URL matches `https://github.com/<owner>/<repo>` (no further path) →
     `repo`
   - URL contains a known template hosting pattern (e.g. `n8n.io/workflows`,
     gist with template content) → `template`
   - Anything else → `article`
2. **Extract metadata**:
   - For `repo`: use `gh api repos/<owner>/<repo>` to fetch name,
     description, stargazers_count, language, topics, pushed_at. Populate
     the optional GitHub fields.
   - For `article` and `template`: best-effort web fetch to extract page
     title and meta description. If fetching fails, leave description
     empty and flag for user review.
3. **Generate frontmatter** with the schema-required fields.
4. **Propose destination path**: `references/<subtype>s/<id>.md` where
   `<id>` is derived from the URL (for repos: `<owner>-<repo-name>`; for
   articles/templates: a slug of the title).
5. **Compose body** with the canonical template; leave "Why this is
   interesting" empty by default.

#### Output

Present a consolidated plan as a Markdown table (one row per URL with
proposed path, subtype, and detected tags), then ask for approval:
`yes` / `no` / `partial`, same as the existing `process-inbox` sub-flow.

For GitHub stars bulk mode, present the result as a single scrollable
table the user can review row-by-row, with one extra column `action`
defaulting to `keep` that the user can change to `archive` or `delete`
before applying.

#### Important constraint

The skill must not download any content from the URLs. It only fetches
metadata (HTML title, GitHub API metadata). This keeps the repository
free of copyrighted material and keeps the operation fast.

### 5. `librarian` skill — references update

Update `skills/librarian/references/taxonomy.md` to add reference-specific
tag suggestions when relevant (e.g. `mcp-server`, `n8n-template`,
`anthropic-skill`, `developer-tool`). Mark these as **subtype hints** —
they help searching references by their nature without changing the
existing category/domain/language taxonomy.

Update `skills/librarian/references/classification-heuristics.md` with the
URL pattern rules from §4 above.

### 6. `tools/generate_index.py` — extension

Extend the generator:

1. Add a `discover_references(root: Path)` function that walks
   `references/*/*.md`, parses frontmatter, returns a list of References
   grouped by subtype.
2. Add a new top-level section `## References` to `INDEX.md`, with three
   subsections (`### Repos`, `### Articles`, `### Templates`).
3. Each subsection is a table with columns: `Name`, `URL`, `Status`,
   `Tags`, `Description`. Sort alphabetically by `id`.
4. References do **not** participate in the inverse dependency graph
   (they are not depended on by composites or recipes). Do not modify the
   inverse graph logic.

Keep the function exported so `tools/check.py` can import it.

### 7. `tools/check.py` — extension

Extend the validator:

1. Add a check `reference_schema_compliance` that validates every
   `references/*/*.md` against the new reference schema.
2. Add a check `reference_subtype_folder_match` that verifies each
   reference's `subtype` matches its parent folder (a reference in
   `references/repos/` must have `subtype: repo`).
3. Both new checks appear as additional rows in the summary table.
4. Do **not** add a network-based "broken link" check in this phase.
   Broken-link detection is out of scope (network in CI is fragile and
   slow).

### 8. `CONTRIBUTING.md` — new section

Add a new top-level section `## Adding a reference` after the existing
"Adding a new workflow" section. Include:

- The three subtypes and when to use each.
- The required frontmatter fields with a concrete example for each
  subtype.
- The recommended body template.
- A note that bulk import from GitHub stars or a `_inbox/links-dump.md`
  file is the preferred path, handled by the `librarian` skill.

### 9. `README.md` — update

Update the existing `README.md` to reflect the new reference category:

- In the **Mental model** section: add a fourth paragraph explaining
  references as a category distinct from atoms, composites, and recipes.
  Atoms, composites, and recipes are content the repo *contains*;
  references are content the repo *points to*.
- In the **Folder map** section: add the `references/` entry with its
  three subfolders (`repos/`, `articles/`, `templates/`) and one-line
  descriptions consistent with the rest of the map.
- Do not change any other section.

Keep the tone and length consistent with the existing README. The total
addition should be ~15 lines.

### 10. Canonical example reference

Create one example reference to validate the schema, analogous to the
`example-hello-world` prompt from Phase 1.

`references/repos/example-anthropic-sdk-python.md`:

```markdown
---
id: example-anthropic-sdk-python
name: Anthropic SDK Python
type: reference
subtype: repo
url: https://github.com/anthropics/anthropic-sdk-python
status: active
description: Official Python SDK for the Anthropic API
tags: [example, canonical, anthropic, sdk, python]
language: en
github_owner: anthropics
github_repo: anthropics/anthropic-sdk-python
github_stars: 0
github_language: Python
github_topics: [anthropic, claude, sdk]
github_last_commit: 2026-05-15
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---

# Anthropic SDK Python

[anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python)

## Why this is interesting

Canonical example reference used to validate the reference schema. Also
the official Anthropic SDK, the reference implementation for Python
clients calling the Claude API.

## Notes

Do not delete. Used by `tools/check.py` to verify the reference schema
validates correctly.
```

The `github_stars: 0` and `github_last_commit: 2026-05-15` are stub
values — do not fetch live data for this example.

## Done criteria

```bash
# README extended with references section
grep -q "references/" README.md
grep -qi "fourth category\|references are\|references point\|points to" README.md

# Folder structure
test -d references/repos
test -d references/articles
test -d references/templates
test -f references/repos/.gitkeep
test -f references/articles/.gitkeep
test -f references/templates/.gitkeep

# Schema file
test -f docs/schemas/reference.schema.yaml

# Canonical example
test -f references/repos/example-anthropic-sdk-python.md

# Librarian extension
grep -q "process-reference" skills/librarian/SKILL.md

# CONTRIBUTING extended
grep -q "Adding a reference" CONTRIBUTING.md

# Tools updated and idempotent
uv run python tools/generate_index.py
uv run python tools/generate_index.py --check
grep -q "## References" INDEX.md
grep -q "example-anthropic-sdk-python" INDEX.md

# Validator passes including the two new checks
uv run python tools/check.py

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.0): references extension — schema, folders, librarian, tools, readme"
git push
```

The pre-commit hook will run. If it modifies `INDEX.md`, re-stage and
commit again with the same message.

## Stop here

Stop after the commit. Do not start Phase 5.1 (GitHub stars import) in the
same session. Wait for explicit user instruction.

After this phase, the repository will be ready to receive real references
in Phase 5.1.
