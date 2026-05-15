---
name: librarian
description: Process _inbox/ items by classifying them and proposing destinations with frontmatter or manifest. Suggest workflows that could integrate a new atom. Propose coherent tags for a file. Use when the user mentions "process inbox", "where does this go", "tag this file", "suggest workflows for", or when files are detected in _inbox/.
---

# Librarian

## 1. Purpose

The librarian skill keeps the Aithos Selection repository tidy. It removes
the cognitive cost of "where does this go?" by triaging the `_inbox/` quick
dump zone, generating well-formed frontmatter and manifests for new items,
proposing coherent tags from a controlled taxonomy, and surfacing existing
workflows that a newly added atom could plug into. The skill is advisory and
plan-first: it always shows what it intends to do before touching a file,
and it never auto-applies destructive changes.

## 2. When to invoke

Invoke this skill in any of the following situations:

- The user types one of the trigger phrases: "process inbox", "process the
  inbox", "process `_inbox/`", "triage inbox", "where does this go", "tag
  this file", "suggest tags", "suggest workflows for `<path>`", "what
  workflows could use `<path>`".
- The user asks a generic "help me classify/organize/move this" question
  about a file in `_inbox/` or about a new atom.
- You (Claude Code) detect that `_inbox/` contains files other than
  `.gitkeep` and `README.md` at the start of a session, and the user has not
  yet asked about them — surface the count and offer to run the
  `process-inbox` sub-flow.
- The user has just added a new atom (prompt, MCP config, tool, stack note,
  skill) and asks which agents or workflows might benefit from it.

Do **not** invoke this skill for changes that the user is making in a
deliberate, hand-driven flow (e.g. they are editing an existing prompt's
frontmatter themselves). The librarian is for triage, not authoring.

## 3. Sub-flow: `process-inbox`

### Input

Everything currently inside `_inbox/`, recursively. Ignore `.gitkeep` and
`README.md` — those are the folder's permanent scaffolding.

### Algorithm

1. **Enumerate.** List every file under `_inbox/` recursively. Treat any
   subfolder as a single candidate (a folder in the inbox almost always
   represents a composite — agent, workflow, or skill — that ships as a
   bundle).
2. **Classify.** For each candidate, pick exactly one type from the table
   below. Consult `references/classification-heuristics.md` for the precise
   rules.

   | Type           | Destination shape                                            |
   |----------------|--------------------------------------------------------------|
   | `prompt`       | `prompts/library/<id>.md`                                    |
   | `template`     | `prompts/templates/<id>.md` (when the file contains `{{...}}` placeholders) |
   | `mcp-config`   | `mcp-servers/<name>.json` (+ optional companion `<name>.md`) |
   | `stack-note`   | `stack/<tool>.md`                                            |
   | `tool-script`  | `tools/<name>.py` (or the appropriate extension)             |
   | `skill`        | `skills/<name>/SKILL.md`                                     |
   | `agent`        | `agents/<name>/` (requires `agent.md`, `manifest.yaml`, `README.md`) |
   | `workflow`     | `workflows/<name>/` (requires `flow.md`, `manifest.yaml`, `README.md`) |
   | `n8n-workflow` | `n8n-workflows/<name>.json` or `n8n-workflows/<name>/`       |
   | `unknown`      | keep in `_inbox/`, flag for the user                         |

3. **Generate metadata.** For each classified candidate, draft:
   - The **proposed final path** (kebab-case stem matching the `id` / `name`
     field).
   - The **proposed frontmatter** (for atoms) or **manifest** (for
     composites and recipes). Fill every required field from the file's
     content; use today's date for `created` and `updated`; default
     `author: riccardo`; default `status: draft` unless the file content
     explicitly says otherwise; pick `version: 0.1.0` for new items.
     See `references/frontmatter-examples.md` and
     `references/manifest-examples.md` for the canonical shapes.
   - **3–6 proposed tags** following `references/taxonomy.md`. At least one
     category tag, one domain tag, one language tag. Flag any tag that is
     not in the taxonomy as `new tag, confirm with user`.

4. **Present the plan.** Produce a single consolidated Markdown table:

   ```
   | # | Source              | →  | Destination                       | Type        | Tags                          |
   |---|---------------------|----|-----------------------------------|-------------|-------------------------------|
   | 1 | _inbox/foo.md       | →  | prompts/library/foo.md            | prompt      | extraction, italian, legal    |
   | 2 | _inbox/bar.json     | →  | mcp-servers/bar.json              | mcp-config  | filesystem                    |
   | 3 | _inbox/baz/         | →  | agents/baz/                       | agent       | classification, italian       |
   ```

   Below the table, show the generated frontmatter or manifest for each row
   in sequence (or under collapsible sections if the renderer supports it).
   Make every proposed change inspectable before any file moves.

5. **Ask for approval.** Prompt the user verbatim:

   > Apply this plan? (yes / no / partial)

   - **yes** — perform the moves, write the frontmatter/manifests, then
     commit with `chore(librarian): processed inbox (<N> items)` where
     `<N>` is the number of items moved.
   - **partial** — ask the user to list the row numbers (e.g. `1, 3`) to
     apply, then proceed with that subset only. Commit the same way with
     the actual count moved.
   - **no** — stop without changes.

6. **Apply.** When applying:
   - Use `git mv` so history follows the file when possible.
   - Write the frontmatter or manifest **before** staging, so the moved
     file is already well-formed.
   - For composites (`agent`, `workflow`, `skill`), create every required
     sibling file (`agent.md`, `manifest.yaml`, `README.md`, etc.) even if
     stubbed — the destination must satisfy `check.py`.
   - Never delete `_inbox/` itself or its `.gitkeep` and `README.md`. The
     folder stays for future use.

7. **Report.** After committing, summarize what was moved (counts by type)
   and what remained in `_inbox/` as `unknown`, so the user can decide next
   steps.

### Failure modes to watch

- A candidate matches more than one type → see the tie-breaking rule at the
  end of `references/classification-heuristics.md`.
- A candidate is a folder but missing required sibling files (e.g. an
  `agents/` candidate with no `agent.md`) → classify as `unknown` and ask
  the user whether to stub the missing pieces.
- A proposed destination already exists → never overwrite. Ask the user
  whether to suffix (`-v2`), merge, or skip.

## 4. Sub-flow: `suggest-workflow`

### Input

A path to a newly added atom, for example
`prompts/library/new-prompt.md`. The atom should already have valid
frontmatter (or, for MCP configs, a companion `.md` with one).

### Algorithm

1. **Read the atom.** Extract its `tags` list. If the atom is an MCP config
   (`.json`), read its companion `.md` instead; if there is no companion,
   ask the user to supply candidate tags before proceeding.
2. **Scan workflows.** Enumerate every `workflows/*/manifest.yaml` and the
   sibling `workflows/*/README.md`.
3. **Score each workflow** on a 0–10 scale:
   - **Tag overlap** — Jaccard similarity between the atom's tags and the
     workflow's `tags` (from `manifest.yaml`), multiplied by 6.
   - **Domain similarity** — read the first paragraph of the workflow's
     `README.md` and assign a subjective 0–4 based on whether the atom's
     purpose plausibly fits the workflow's domain.
4. **Filter and rank.** Keep only workflows with a total score `≥ 5`. Sort
   descending. Take the top 3.
5. **Return** a Markdown list, one item per workflow, each with:
   - The workflow path.
   - The score (e.g. `7.5/10`).
   - A one-sentence rationale referencing the overlapping tags and the
     workflow's stated purpose.

### Boundaries

This sub-flow is **advisory only**. Never modify any `manifest.yaml`
automatically — the user decides whether to wire the new atom into a
workflow.

If fewer than three workflows score `≥ 5`, return however many qualify
(possibly zero) and say so explicitly. Do not pad with low-scoring
suggestions.

## 5. Sub-flow: `tag`

### Input

A single file path inside the repository (any atom or composite).

### Algorithm

1. **Read the file.** Use both the body and any existing frontmatter or
   manifest fields as signal.
2. **Load the taxonomy** from `references/taxonomy.md`. Treat it as the
   closed set of accepted tags unless step 4 applies.
3. **Propose 3–6 tags**, with at least one from each of the three required
   groups:
   - At least one **category** tag (`extraction`, `analysis`,
     `generation`, …).
   - At least one **domain** tag (`legal`, `finance`, `real-estate`, …).
     Use `general` if the file is genuinely cross-domain.
   - At least one **language** tag (`italian`, `english`,
     `multilingual`).
   Optionally add status tags (`experimental`, `production`, `archived`)
   and special tags (`example`, `canonical`) when appropriate.
4. **Flag new tags.** Any proposed tag that is not in the taxonomy must be
   labeled `new tag, confirm with user` in the output. If the user
   approves a new tag, add it to `references/taxonomy.md` **in the same
   commit** that applies the tag.

### Output shape

Return a Markdown block of this form:

```
Proposed tags for `<path>`:

- `extraction`         (category)
- `legal`              (domain)
- `italian`            (language)
- `partita-iva`        (new tag, confirm with user)
```

The user can then accept the list as-is, drop individual tags, or ask for
alternatives.

## 6. Output style

The librarian is plan-first and confirmation-driven:

1. **Plan before action.** Always show the proposed moves, frontmatter, or
   tags before any file is created, moved, or modified. The user must be
   able to read the entire intent of the operation in one screen.
2. **Single explicit prompt.** Use the exact prompt strings defined in each
   sub-flow (`Apply this plan? (yes / no / partial)` for inbox
   processing). Do not paraphrase.
3. **No silent side effects.** Never auto-apply destructive changes
   (renames, deletions, overwrites, manifest edits) without an explicit
   user confirmation captured in the conversation.
4. **One commit per applied batch.** Inbox processing produces one commit
   covering all moved items in that batch, with the message
   `chore(librarian): processed inbox (<N> items)`.
5. **Respect the golden rules.** No duplication, manifest is the source of
   truth, Markdown and YAML only — refuse to apply a plan that would
   violate them and explain why.
6. **Stay inside the repo.** The librarian only reads from and writes to
   the current repository tree. It never touches files outside the project
   root.

## 7. References

Consult these files in `skills/librarian/references/` whenever the relevant
information is needed:

- [`frontmatter-examples.md`](./references/frontmatter-examples.md) —
  canonical, validated frontmatter for prompts, templates, stack notes,
  deprecated atoms, and skills.
- [`manifest-examples.md`](./references/manifest-examples.md) — canonical
  manifests for minimal agents, full-featured agents, and workflows.
- [`taxonomy.md`](./references/taxonomy.md) — the closed set of accepted
  tags, grouped by category, domain, language, status, and special. Also
  the rule for proposing new tags.
- [`classification-heuristics.md`](./references/classification-heuristics.md)
  — the rules that decide whether an inbox item is a prompt, MCP config,
  stack note, tool, skill, agent, workflow, or `unknown`.

Repository-wide references (outside this skill) that the librarian also
honours:

- [`/CLAUDE.md`](../../CLAUDE.md) — invariants for every session.
- [`/PRD.md`](../../PRD.md) — strategic spec, including the schemas in
  section 5.
- [`/docs/schemas/frontmatter.schema.yaml`](../../docs/schemas/frontmatter.schema.yaml)
  — authoritative shape of the frontmatter the librarian generates.
- [`/docs/schemas/manifest.schema.yaml`](../../docs/schemas/manifest.schema.yaml)
  — authoritative shape of the manifests the librarian generates.
- [`/docs/naming-conventions.md`](../../docs/naming-conventions.md) —
  kebab-case, identifier matching, versioning, and tag rules the librarian
  must obey when proposing paths and identifiers.
