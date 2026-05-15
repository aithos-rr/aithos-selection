# Phase 5.1 — GitHub stars bulk import

## Goal

Import the user's GitHub starred repositories as `subtype: repo` reference
files in `references/repos/`. The user (`aithos-rr` on GitHub) wants to
curate the list during import: each starred repo can be **kept**,
**archived** (preserved with `status: archived`), or **deleted** (not
imported at all).

This is the first phase that ingests real content. The repository's
tooling and CI must remain green throughout.

## Prerequisites

- Phase 5.0 complete and merged into `main` (commit `c890ddc` or later).
- The `gh` CLI is authenticated as `aithos-rr` (confirmed by `gh auth status`).
- You are on a fresh feature branch created from `main`:
  ```bash
  git checkout main
  git pull
  git checkout -b feat/ingest-github-stars
  ```
- The repository is in a clean state (`git status` clean,
  `uv run python tools/check.py` exits 0).

## Branch policy

This phase works on `feat/ingest-github-stars`, not directly on `main`.
After the phase commits and pushes, the user will open a PR to merge back
to `main`.

## High-level flow

1. **Fetch** the complete list of starred repositories via `gh api`.
2. **Build** a single review table with one row per starred repo, including
   key metadata (owner/name, stars, language, last commit, description) and
   an `action` column defaulted to `keep`.
3. **Present** the table to the user as Markdown. The user edits the
   `action` column inline (changes `keep` → `archive` or `delete` where
   appropriate).
4. **Apply** the user's decisions: generate reference files for `keep` and
   `archive` actions; skip `delete` entirely.
5. **Validate, commit, push.**

## Deliverables

### 1. Fetch starred repositories

Use the `gh` CLI to fetch the complete starred list. The user has 66 stars
so a single paginated call covers it. Capture the relevant fields:

```bash
gh api users/aithos-rr/starred --paginate \
  --jq '.[] | {
    full_name,
    name,
    owner: .owner.login,
    description,
    stars: .stargazers_count,
    language,
    topics,
    pushed_at,
    html_url
  }'
```

Save the raw output to `_inbox/github-stars-raw.json` for traceability.
Do not commit this file (it is in `_inbox/` and gitignored).

If `gh api` fails (auth, network), STOP and report the error. Do not
fabricate data.

### 2. Build the review table

Generate a Markdown file `_inbox/github-stars-review.md` with the
following structure:

```markdown
# GitHub Stars Review

Total: <N> starred repositories.

Edit the `action` column inline. Allowed values: `keep` (default),
`archive`, `delete`.

| # | Owner/Repo | Stars | Lang | Last commit | Description | Action |
|---|------------|-------|------|-------------|-------------|--------|
| 1 | anthropics/anthropic-sdk-python | 5234 | Python | 2026-05-10 | Official Python SDK ... | keep |
| 2 | ... | ... | ... | ... | ... | keep |
```

Sort the table:
- First by `pushed_at` descending (most recently active first)
- Then by `stars` descending as tiebreaker

Truncate the description to ~80 characters with ellipsis if longer.

After generating the file, output to the terminal:

```
✓ Created _inbox/github-stars-review.md with <N> entries.

Please review the file and edit the 'action' column for each row.
Allowed values: keep, archive, delete.

When done, run:
  /resume

Or, if invoking the skill directly, tell me: "I've reviewed the stars,
apply the decisions."
```

Then **STOP and wait for the user**. Do not proceed to step 3 until the
user explicitly confirms.

### 3. Apply the user's decisions

When the user confirms, re-read `_inbox/github-stars-review.md` and parse
the `action` column for each row.

For each row:

- **`keep`** → create `references/repos/<owner>-<repo-name>.md` with
  `status: active`
- **`archive`** → create `references/repos/<owner>-<repo-name>.md` with
  `status: archived`
- **`delete`** → skip, do not create a file
- Any other value → flag the row, do not create a file, report at the end

The reference file content follows the canonical template from Phase 5.0.
Specifically, the frontmatter must include all required reference schema
fields plus the GitHub-specific optional fields:

```yaml
---
id: <owner>-<repo-name>     # kebab-case, derived from full_name
name: <repo name as displayed on GitHub>
type: reference
subtype: repo
url: <html_url from API>
status: active|archived
description: <description from API, or "(no description)" if null>
tags: [<derived tags, see below>]
language: en               # default; user can edit later
github_owner: <owner>
github_repo: <full_name>
github_stars: <stargazers_count>
github_language: <primary language, e.g. Python>
github_topics: [<topics from API, may be empty>]
github_last_commit: <pushed_at as YYYY-MM-DD>
created: <today's date YYYY-MM-DD>
updated: <today's date YYYY-MM-DD>
author: riccardo
---

# <name>

[<owner>/<repo-name>](<url>)

## Why this is interesting

(To be filled in.)

## Notes

(Optional.)
```

### 4. Tag derivation

Derive tags from the available metadata:

- The `github_language` mapped to lowercase (e.g. `Python` → `python`)
- Each `github_topic` mapped to lowercase, kebab-case
- One **category tag** when inferable from description or topics:
  - Description or topics mention "MCP" or "model context protocol" →
    `mcp-server`
  - Description or topics mention "n8n" → `n8n-template`
  - Description or topics mention "agent" or "skill" → `anthropic-skill`
    or `agent` as appropriate
  - Description or topics mention "cli", "tool", "utility" → `developer-tool`
  - Otherwise omit the category tag (user will add manually later)

Limit total tags to 6 per file. Deduplicate. Keep tag generation
conservative: when uncertain, fewer tags are better.

### 5. Edge cases and constraints

- **Empty description**: emit `description: "(no description)"` in
  frontmatter; the schema requires the field to be a non-empty string,
  but a placeholder is acceptable until the user fills "Why this is
  interesting".
- **No primary language** (some repos): omit `github_language` (it's
  optional).
- **Empty topics**: emit `github_topics: []`.
- **ID collision** (very unlikely for distinct repos): if the generated
  `id` (kebab `<owner>-<repo-name>`) already exists in
  `references/repos/`, suffix `-2`, `-3`, etc.
- **Existing reference file** at the target path: skip and report. Do
  not overwrite.
- **The canonical example** (`references/repos/example-anthropic-sdk-python.md`):
  this file must remain untouched. Even if the user has starred
  `anthropic-sdk-python`, the generated reference must use a different
  id (e.g. `anthropics-anthropic-sdk-python` is the natural form anyway,
  so no collision is expected — verify).

### 6. After applying, run validation

```bash
uv run python tools/generate_index.py
uv run python tools/check.py
```

Both must pass. Specifically `check.py` must report all N references
(canonical example + every kept/archived repo) as valid.

If any check fails, STOP and report. Do not commit a broken state.

### 7. Cleanup

Delete `_inbox/github-stars-raw.json` and `_inbox/github-stars-review.md`
after successful apply. They were working files; the durable artifacts are
the reference files in `references/repos/`.

### 8. Summary report

Print a final summary:

```
GitHub stars import complete.

  Total starred repos:    <N>
  Kept (active):          <X>
  Archived:               <Y>
  Deleted (skipped):      <Z>
  Tag warnings:           <W>   (rows with unrecognized action values)

References created in references/repos/:
  - <owner>-<repo-name-1>.md
  - <owner>-<repo-name-2>.md
  ...

All checks passing. Commit ready.
```

## Done criteria

```bash
# Working files cleaned up
test ! -f _inbox/github-stars-raw.json
test ! -f _inbox/github-stars-review.md

# Reference files created (at least the kept + archived total)
ls references/repos/*.md | wc -l   # should be >= 2 (canonical + at least 1)

# Validation passes
uv run python tools/generate_index.py --check
uv run python tools/check.py

# INDEX has the new references
grep -q "## References" INDEX.md

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.1): import <N> GitHub stars as repo references (<X> kept, <Y> archived)"
git push -u origin feat/ingest-github-stars
```

Replace `<N>`, `<X>`, `<Y>` with actual counts.

## Stop here

After commit and push, stop. Print the PR creation command for the user:

```
To open a PR for review:
  gh pr create --base main --head feat/ingest-github-stars \
    --title "Import GitHub stars as repo references" \
    --body "Imported <N> starred repositories (<X> kept, <Y> archived)"
```

Do not auto-create the PR. The user reviews locally first, may want to
adjust some references manually, then opens the PR themselves.

## Important behavioral note

This phase is **interactive**. There are two distinct moments where the
agent must STOP and wait for explicit user input:

1. After generating the review table (between step 2 and step 3).
2. Never proceed to apply decisions without confirmation.

If the user says "go ahead" or similar without having edited the review
file, ask once more for confirmation. The default for unedited rows is
`keep` and that is acceptable, but the user should confirm awareness of
this default before applying.
