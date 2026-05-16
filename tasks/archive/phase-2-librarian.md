# Phase 2 — Librarian Skill

## Goal

Create a Claude Code skill called `librarian` that processes `_inbox/` and
helps maintain the repository's organization. The skill removes the cognitive
cost of "where does this go?" by classifying inbox items, generating
frontmatter and manifests, and proposing destinations.

## Prerequisites

- Phase 1 complete and committed.
- You are on branch `bootstrap`.
- Working tree is clean.

## Deliverables

### 1. `skills/librarian/SKILL.md`

The main skill file in Anthropic skill format. The skill declares three
sub-flows:

- `process-inbox` — read all files in `_inbox/`, classify each, propose
  destination and metadata, ask the user to approve, apply approved moves.
- `suggest-workflow` — given a newly added atom, scan existing workflows
  and suggest which could integrate it.
- `tag` — given a file path, propose tags coherent with the existing
  taxonomy.

#### SKILL.md frontmatter

```yaml
---
name: librarian
description: Process _inbox/ items by classifying them and proposing destinations with frontmatter or manifest. Suggest workflows that could integrate a new atom. Propose coherent tags for a file. Use when the user mentions "process inbox", "where does this go", "tag this file", "suggest workflows for", or when files are detected in _inbox/.
---
```

#### SKILL.md body structure

1. **Purpose** — one paragraph.
2. **When to invoke** — explicit trigger phrases and conditions.
3. **Sub-flow: `process-inbox`** — see detailed spec below.
4. **Sub-flow: `suggest-workflow`** — see detailed spec below.
5. **Sub-flow: `tag`** — see detailed spec below.
6. **Output style** — always show a plan before any move; require user
   confirmation; never auto-apply destructive changes.
7. **References** — pointers to the `references/` files (see below).

#### Sub-flow: `process-inbox` — detailed spec

Input: contents of `_inbox/`.

Algorithm:

1. List all files (recursive) in `_inbox/`. Ignore `.gitkeep` and `README.md`.
2. For each file, classify into one of:
   - `prompt` → `prompts/library/<id>.md` or `prompts/templates/<id>.md`
     (templates if it contains `{{...}}` placeholders)
   - `mcp-config` → `mcp-servers/<name>.json` (+ optional companion `.md`)
   - `stack-note` → `stack/<tool>.md`
   - `tool-script` → `tools/<name>.py` (or appropriate extension)
   - `skill` → `skills/<name>/SKILL.md`
   - `agent` → `agents/<name>/` (multi-file: requires `agent.md`,
     `manifest.yaml`, `README.md`)
   - `workflow` → `workflows/<name>/` (multi-file: requires `flow.md`,
     `manifest.yaml`, `README.md`)
   - `n8n-workflow` → `n8n-workflows/<name>.json` (or folder)
   - `unknown` → keep in `_inbox/`, flag for user
3. For each classified file, generate:
   - Proposed final path
   - Proposed frontmatter (atoms) or manifest (composites/recipes), filling
     required fields from the file's content
   - Proposed tags: 3–6 tags following `references/taxonomy.md`
4. Present a single consolidated plan as a Markdown table:

```
| Source              | →  | Destination                       | Type        | Tags                          |
|---------------------|----|-----------------------------------|-------------|-------------------------------|
| _inbox/foo.md       | →  | prompts/library/foo.md            | prompt      | extraction, italian, legal    |
| _inbox/bar.json     | →  | mcp-servers/bar.json              | mcp-config  | filesystem                    |
| _inbox/baz/         | →  | agents/baz/                       | agent       | classification, italian       |
```

5. Show generated frontmatter/manifest for each item in collapsible sections
   (or sequentially).
6. Ask the user: "Apply this plan? (yes / no / partial)"
   - **yes**: move all files, write frontmatter/manifests, commit with
     `chore(librarian): processed inbox (<N> items)`.
   - **partial**: ask the user to list the row numbers to apply, then
     proceed with the subset.
   - **no**: stop without changes.
7. After moving, do not delete `_inbox/`. Leave it for future use.

#### Sub-flow: `suggest-workflow` — detailed spec

Input: a path to a newly added atom (e.g.
`prompts/library/new-prompt.md`).

Algorithm:

1. Read the atom and extract its tags.
2. Scan all `workflows/*/manifest.yaml` and `workflows/*/README.md`.
3. For each workflow, compute a relevance score (0–10) based on:
   - Tag overlap (Jaccard similarity × 6)
   - Domain similarity from the workflow's README introduction (subjective,
     0–4)
4. Return top 3 workflows with score ≥ 5, each with a one-sentence
   rationale.

Do not modify any manifest automatically. Output is advisory only.

#### Sub-flow: `tag` — detailed spec

Input: a file path.

Algorithm:

1. Read the file.
2. Load the existing tag taxonomy from `references/taxonomy.md`.
3. Propose 3–6 tags:
   - At least one **category** tag (`extraction`, `analysis`, etc.)
   - At least one **domain** tag (`legal`, `finance`, etc.)
   - At least one **language** tag (`italian`, `english`)
4. Flag any proposed tag that is not in the existing taxonomy as
   "new tag, confirm with user".

### 2. `skills/librarian/references/frontmatter-examples.md`

A reference document with 4–6 well-formed frontmatter examples:

- A stable prompt
- A draft template (with `{{variables}}`)
- A stack note
- A deprecated prompt with replacement
- A skill

Each example must show every required field correctly filled. Include 2–3
lines of body content after each frontmatter block so the example is
self-contained.

### 3. `skills/librarian/references/manifest-examples.md`

A reference document with 3 well-formed manifest examples:

- A minimal agent (no MCP servers, one prompt dependency)
- A complete agent (prompts, templates, MCP servers, tools)
- A workflow combining two agents and one n8n flow

### 4. `skills/librarian/references/taxonomy.md`

The canonical tag taxonomy, organized in groups. Each tag has a one-line
description.

- **Category tags** (what kind of task):
  `extraction`, `analysis`, `generation`, `classification`,
  `summarization`, `translation`, `reasoning`, `code`, `search`,
  `automation`, `evaluation`.
- **Domain tags** (what subject matter):
  `legal`, `finance`, `real-estate`, `marketing`, `sales`, `hr`,
  `operations`, `engineering`, `education`, `general`.
- **Language tags**:
  `italian`, `english`, `multilingual`.
- **Status tags** (optional, complement to the frontmatter `status` field):
  `experimental`, `production`, `archived`.
- **Special tags**:
  `example`, `canonical` — used for items that exist for schema
  validation and must not be deleted.

End the file with the rule for adding new tags: a new tag may be proposed
during inbox processing or tagging, but the user must approve it; if
approved, the tag is added to this file in the same commit.

### 5. `skills/librarian/references/classification-heuristics.md`

Concrete rules the skill consults when classifying inbox items:

- File contains `system_prompt:` YAML and `agents:` list → likely workflow
  manifest.
- File contains `system_prompt:` YAML but no `agents:` list → likely agent
  manifest.
- `.json` file with `mcpServers` key or matching MCP server schema → MCP
  config.
- `.md` file starting with `---` (frontmatter block) → categorize by the
  `type:` field.
- `.md` file without frontmatter, content starts with "How I use X" /
  "Setting up X" / "My X workflow" → stack-note.
- `.md` file without frontmatter, content is an instruction directed at an
  LLM ("You are…", "When the user…", "Respond with…") → prompt.
- `.py` file in inbox → tool-script.
- Folder in `_inbox/`:
  - Contains `agent.md` → agent.
  - Contains `flow.md` → workflow.
  - Contains `SKILL.md` → skill.
  - Otherwise → unknown, flag for user.

End the file with the rule for ambiguous cases: when content matches more
than one category, prefer the more specific one and flag the alternatives.
When nothing matches, classify as `unknown` and keep in `_inbox/`.

## Done criteria

```bash
# Files exist
test -f skills/librarian/SKILL.md
test -f skills/librarian/references/frontmatter-examples.md
test -f skills/librarian/references/manifest-examples.md
test -f skills/librarian/references/taxonomy.md
test -f skills/librarian/references/classification-heuristics.md

# SKILL.md has valid frontmatter with required fields
head -5 skills/librarian/SKILL.md | grep -q '^name: librarian'
head -10 skills/librarian/SKILL.md | grep -q '^description:'

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-2): librarian skill for inbox processing and tagging"
git push
```

## Stop here

Stop after the commit. Wait for user instruction before Phase 3.
