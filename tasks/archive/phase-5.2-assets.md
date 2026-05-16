# Phase 5.2 — Asset bulk import (zips + prompts + visual prompt)

## Goal

Import the user's real assets accumulated outside the repository into the
appropriate locations:

1. **A batch of ~30 zip archives** containing Claude Code skills or agents
   in Anthropic standard format. Filenames are descriptive of the
   contained skill/agent.
2. **A few Markdown files** containing pure text prompts (Italian),
   ready for `prompts/library/`.
3. **One free-floating image file** (`.jpg`, `.png`, etc.) at the root
   of `_inbox/` representing a visual prompt. To be turned into a
   folder-as-prompt in `prompts/library/`.

The phase also makes a small extension to the system to support
**folder-as-prompt** structures: a `prompts/library/<name>/` directory
containing a `README.md` (frontmatter + description) and a companion
image asset.

This phase is **auto-pilot**: CC processes everything in `_inbox/`
without asking for per-item confirmation, then presents a rich final
report. The user reviews the resulting commit.

## Prerequisites

- Phase 5.1 complete and merged into `main` (commit `7d23ff8` or later).
- The repository is in a clean state on a fresh feature branch
  `feat/ingest-assets-batch-1`.
- The inbox is populated with:
  - ~30 zip files (skill or agent bundles)
  - 2 Markdown prompt files
  - 1 free image file (`.jpg`)
  - Plus the always-present `.gitkeep` and `README.md`

- `git status` clean.

## Behavioral defaults for auto-pilot mode

- **Process everything**: no per-item confirmation. The user has
  pre-curated the inbox; everything in it should be ingested.
- **Skip noise**: ignore `.gitkeep`, `README.md` (the inbox's own
  readme), and any file whose name ends in `:Zone.Identifier` (Windows
  metadata noise).
- **Skip and flag, don't guess wildly**: on truly ambiguous inputs,
  prefer leaving the entry in `_inbox/` with a flag in the report over
  fabricating a destination.
- **No collision overwrites**: if a destination path already exists,
  skip the import and flag in the report.
- **Italian source content is fine**: prompt `.md` files may be in
  Italian; reflect this in the `language` frontmatter field.

## High-level flow

1. **System extension** (deliverables §1–§3): support folder-as-prompt.
2. **Inventory inbox**: classify every entry deterministically.
3. **Process each zip**: extract → inspect → classify → move →
   generate manifest if needed.
4. **Process each pure-prompt `.md`**: derive frontmatter from content
   and filename → move to `prompts/library/<id>.md`.
5. **Process the free image**: create `prompts/library/<id>/` with the
   image and a generated `README.md`.
6. **Validate** the whole repository.
7. **Report** the results richly.
8. **Commit and push**.

## Deliverables — Part A: system extension

### 1. Schema update — support folder-as-prompt

Update the prompt-handling logic in tooling to accept two structural
variants:

- **Single-file prompt** (existing): `prompts/library/<id>.md` with
  frontmatter
- **Folder prompt** (new): `prompts/library/<id>/README.md` with
  frontmatter; the folder may contain companion assets (images, code
  samples)

The folder's `id` (in frontmatter) must match the folder name.

No change is needed to `docs/schemas/frontmatter.schema.yaml` itself
(the schema validates frontmatter content, not file structure). The
structural variation is handled in the discovery and validation logic.

### 2. Generator update — `tools/generate_index.py`

Extend `discover_atoms` (the prompt section specifically) to walk both:

- `prompts/library/*.md` (single-file)
- `prompts/library/*/README.md` (folder-as-prompt)

Both variants are represented identically in `INDEX.md` (same row in the
Prompts library table). The presence of additional files in the folder
(beyond `README.md`) does not change the index output.

### 3. Validator update — `tools/check.py`

Extend the prompt frontmatter compliance check to handle folder prompts:

- A prompt folder must contain exactly one `README.md` with valid
  frontmatter.
- The frontmatter `id` must equal the folder name.
- Additional files (images, etc.) are allowed and not validated.
- A folder named like a prompt that does NOT contain `README.md` is a
  validation failure.

Add no new top-level check; extend the existing
`frontmatter_schema_compliance` to recognize folder prompts.

## Deliverables — Part B: ingestion

### 4. Inbox inventory and classification

Scan `_inbox/` (direct children only) and classify each entry:

| Pattern | Classification |
|---|---|
| `*.zip` | candidate skill or agent (determined after extraction) |
| `*.md` (except `README.md`) | pure-text prompt |
| `*.png`, `*.jpg`, `*.jpeg`, `*.webp` at root | visual prompt |
| Directory containing exactly one image and possibly small text files | visual prompt (folder form) |
| `.gitkeep`, `README.md`, `*:Zone.Identifier` | ignore silently |
| Anything else | flag in report as "unhandled, left in inbox" |

### 5. Zip processing

For each `*.zip` in `_inbox/`:

1. **Extract** to a temporary directory:
   `_inbox/.tmp-extract/<zip-base-name>/`
2. **Determine top-level structure**:
   - If extracted content has a single top-level folder containing
     `SKILL.md` → classify as **skill**, that folder name becomes the
     skill `id`.
   - If extracted content has `SKILL.md` at root (no wrapping folder) →
     classify as **skill**, the zip's base name becomes the `id`.
   - If `agent.md` is present instead of `SKILL.md` → classify as
     **agent**.
   - If neither file is present → flag in report as "unrecognized zip
     structure", leave the original zip in `_inbox/` untouched, and
     clean up the temp directory for that zip.
3. **Validate frontmatter** of `SKILL.md` / `agent.md`:
   - Must contain a frontmatter block (delimited by `---`).
   - Required fields: `name`, `description`. If missing or malformed,
     infer reasonable defaults from the zip filename and the file body,
     and note the inference in the report.
4. **Move to destination**:
   - Skills → `skills/<id>/`, preserving the internal structure
     (`SKILL.md`, `references/`, `scripts/`, etc.).
   - Agents → `agents/<id>/` with the standard files (`agent.md`,
     `manifest.yaml`, `README.md`). If `manifest.yaml` is missing, CC
     generates a minimal one from the available frontmatter (use the
     existing canonical example `agents/example-echo-agent/manifest.yaml`
     as a template for required fields).
5. **ID collision handling**: if the target folder already exists in
   `skills/` or `agents/`, skip and flag. Do not overwrite.
6. **Delete** the original zip from `_inbox/` only after successful
   move AND successful validation of the destination.

### 6. Pure-prompt `.md` processing

For each `*.md` file in `_inbox/` (excluding `README.md` and any
`:Zone.Identifier`):

1. **Read** the file content.
2. **Derive the `id`**: kebab-case slug of the filename, stripped of
   the `.md` extension, lowercased, replacing spaces and special
   characters with hyphens. Maximum 60 characters; truncate if longer.
   Example: `Prompt Workflow per creare un AI Booking Assistant con
   Claude Code.md` → `prompt-workflow-ai-booking-assistant-claude-code`.
3. **Determine the language**: detect from content (Italian markers:
   "il", "la", "di", "che", "per", etc.). For these specific files
   the user has indicated they are in Italian (`language: it`).
4. **Compose frontmatter** for the prompt:
   - `id`: from step 2
   - `name`: human-readable from original filename (preserve original
     casing and Italian text)
   - `type`: `prompt`
   - `status`: `stable` (user-curated)
   - `version`: `1.0.0`
   - `description`: derive from the first heading or first few lines of
     the content (one sentence, ~80 chars max)
   - `tags`: derive 3-5 tags from content (e.g. `workflow`, `claude-code`,
     `italian`, plus a domain tag from the content like `booking`,
     `lead-generation`)
   - `language`: `it` (for these specific files)
   - `created`/`updated`: today
   - `author`: `riccardo`
5. **Write the file** to `prompts/library/<id>.md` with the new
   frontmatter prepended to the original content (preserve the original
   body verbatim).
6. **Delete** the original from `_inbox/` after successful write.

### 7. Free image processing (visual prompt)

For each image file (`.png`, `.jpg`, `.jpeg`, `.webp`) at the root of
`_inbox/`:

1. **Derive the `id`**: kebab-case slug from the filename (without
   extension). Example: `The Anatomy of a Claude 4.6 Prompt.jpg` →
   `anatomy-of-claude-4-6-prompt`. Strip leading articles like "the"
   for cleanliness; the user can rename later if desired.
2. **Inspect the image** using vision capability and compose a one-line
   description of what the image represents (the prompt content,
   diagram type, etc.).
3. **Create the destination folder**: `prompts/library/<id>/`.
4. **Move the image** into the folder, renaming it to a clean name:
   `prompt.<original-extension>` (e.g. `prompt.jpg`).
5. **Create `README.md`** in the folder with:
   - Frontmatter:
     - `id`: from step 1
     - `name`: human-readable from original filename
     - `type`: `prompt`
     - `status`: `stable`
     - `version`: `1.0.0`
     - `description`: from step 2
     - `tags`: `[visual, prompt, image-based]` + any topical tags
       inferred from the image content (max 6 total)
     - `language`: `multilingual` (visual prompts are language-agnostic
       by default)
     - `created`/`updated`: today
     - `author`: `riccardo`
   - Body:
     ```markdown
     # <name>

     ## Description

     <CC-generated description from step 2>

     ## Image

     ![<name>](./prompt.<ext>)

     ## Usage

     Attach `prompt.<ext>` to a Claude session along with your task
     description, or paste it inline if your client supports image
     uploads.
     ```

### 8. Cleanup

After all processing:

- Remove `_inbox/.tmp-extract/` directory entirely.
- The `_inbox/` should contain only `.gitkeep` and `README.md`, plus any
  entries flagged as "unhandled" with notes in the report.

### 9. Validate

```bash
uv run python tools/generate_index.py
uv run python tools/check.py
```

Both must pass. If any check fails, STOP and report. Do not commit
broken state.

### 10. Final report

Print a comprehensive report:

```
Asset import complete.

  Inbox entries processed:    <N>
    Zips → skills:            <S>
    Zips → agents:            <A>
    Pure .md → prompts:       <P>
    Image → folder-prompt:    <V>
    Ignored (system):         <I>
    Unhandled (left inbox):   <U>
    Skipped (collisions):     <C>

Skills imported (skills/):
  - <id-1>   (from skill-name-1.zip)
  - <id-2>   (from skill-name-2.zip)
  ...

Agents imported (agents/):
  - <id>   (from filename.zip)

Pure prompts imported (prompts/library/):
  - <id-1>.md   (from <original-name>.md)
  - <id-2>.md   (from <original-name>.md)

Folder prompts imported (prompts/library/):
  - <id>/   (from <original-name>.jpg)
    description: "<CC-generated description>"

Inferences and flags:
  - <id-1>: description auto-inferred from filename, recommend review
  - <id-2>: minimal manifest synthesized, recommend review
  - <unhandled-entry>: <reason>

All checks passing. Commit ready.
```

## Done criteria

```bash
# Inbox cleaned
ls _inbox/ | grep -v -E '^\.gitkeep$|^README\.md$' | wc -l   # should be 0 if no unhandled

# Working temp directory removed
test ! -d _inbox/.tmp-extract

# At least some skills imported
test $(ls skills/ | grep -v librarian | grep -v '\.gitkeep' | wc -l) -ge 1

# Pure prompts imported
test $(ls prompts/library/*.md 2>/dev/null | grep -v example-hello-world | wc -l) -ge 1

# Folder prompts exercised
ls -d prompts/library/*/ 2>/dev/null | head -3

# Validation passes
uv run python tools/generate_index.py --check
uv run python tools/check.py

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.2): import <N> assets — <S> skills, <A> agents, <P> prompts, <V> visual prompt

Inbox processed via auto-pilot mode. See session report for per-item details.
Tag and description inferences may benefit from manual review."
git push -u origin feat/ingest-assets-batch-1
```

## Stop here

After commit and push, stop. Print the PR creation command:

```
gh pr create --base main --head feat/ingest-assets-batch-1 \
  --title "Import asset batch 1 — skills, agents, prompts" \
  --body "Imported <N> assets from inbox in auto-pilot mode. See commit body and session report."
```

Do not auto-create the PR. The user reviews the commit (which contains
auto-generated descriptions, tags, and minimal manifests), corrects what's
needed locally, then opens the PR themselves.

## Safety brakes

- If the inbox is unexpectedly empty (no zips, no md, no images), abort
  early with the message "Nothing to ingest in _inbox/" and do not
  commit.
- If more than 60 entries are detected in `_inbox/` (excluding system
  files), abort with the message "Inbox unexpectedly large (>60
  entries). Aborting to prevent runaway." The user can re-run after
  splitting the batch.
- Never run network calls in this phase. No `gh api`, no web fetch.
  Everything is local.
