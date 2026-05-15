# Frontmatter examples

Canonical, validated examples of the YAML frontmatter blocks used at the
top of Markdown atoms in this repository. Use them as drop-in templates
when the librarian proposes a new atom or when a contributor needs to
verify the shape.

All examples obey:

- The schema at `/docs/schemas/frontmatter.schema.yaml`.
- The naming conventions in `/docs/naming-conventions.md`.
- The tag taxonomy in `./taxonomy.md`.

Note: `skills/**/SKILL.md` files follow the **Anthropic skill** frontmatter
format (just `name` and `description`), shown last. They are not validated
by the general frontmatter schema.

## 1. A stable prompt

File: `prompts/library/doc-extraction-v2.md`

```markdown
---
id: doc-extraction-v2
name: Document Extraction (v2)
type: prompt
status: stable
version: 2.0.0
description: Extracts structured fields from Italian legal PDFs into JSON
tags: [extraction, legal, italian, pdf-parsing]
language: it
model: claude-sonnet-4
created: 2026-04-12
updated: 2026-05-10
author: riccardo
---

# Document Extraction (v2)

Extract the following fields from the attached Italian legal document and
return them as JSON: parties, dates, amounts, codice fiscale references.
```

## 2. A draft template (parametric)

File: `prompts/templates/lead-summary.md`

```markdown
---
id: lead-summary
name: Lead Summary Template
type: template
status: draft
version: 0.1.0
description: Parametric template that summarises an inbound lead given CRM context
tags: [summarization, sales, crm, multilingual]
language: multilingual
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---

# Lead Summary

Summarise the lead `{{lead_name}}` from `{{source_channel}}` using the CRM
context `{{crm_context}}`. Output a three-bullet brief in
`{{output_language}}`.
```

## 3. A stack note

File: `stack/supabase.md`

```markdown
---
id: supabase
name: Supabase
type: stack-note
status: stable
version: 1.0.0
description: Operational notes for Supabase usage in Aithos projects
tags: [operations, engineering, english, database, postgres]
language: en
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---

# Supabase

Operational playbook for Supabase: project setup, auth providers, RLS
patterns, and recurring gotchas observed across Aithos client engagements.
```

## 4. A deprecated prompt with a replacement

File: `prompts/library/doc-extraction.md`

```markdown
---
id: doc-extraction
name: Document Extraction (v1, deprecated)
type: prompt
status: deprecated
version: 1.2.0
description: Original extraction prompt — superseded by doc-extraction-v2
tags: [extraction, legal, italian, archived]
language: it
created: 2026-01-08
updated: 2026-05-10
author: riccardo
---

# Document Extraction (v1) — deprecated

Replaced by [`doc-extraction-v2.md`](./doc-extraction-v2.md) on
2026-05-10. Kept for historical reference; do not use in new work.
```

## 5. A skill (Anthropic format)

File: `skills/librarian/SKILL.md`

```markdown
---
name: librarian
description: Process _inbox/ items by classifying them and proposing destinations with frontmatter or manifest. Suggest workflows that could integrate a new atom. Propose coherent tags for a file. Use when the user mentions "process inbox", "where does this go", "tag this file", "suggest workflows for", or when files are detected in _inbox/.
---

# Librarian

Skill body follows. The frontmatter for Anthropic skills is intentionally
minimal: only `name` and `description` are required.
```

## 6. An MCP config companion note

File: `mcp-servers/linear-mcp.md` (companion to `mcp-servers/linear-mcp.json`)

```markdown
---
id: linear-mcp
name: Linear MCP Server
type: stack-note
status: stable
version: 1.0.0
description: Notes accompanying the native Linear MCP server config
tags: [operations, automation, english, mcp]
language: en
created: 2026-05-15
updated: 2026-05-15
author: riccardo
---

# Linear MCP

Auth scopes, recommended tool whitelist, and known rate-limit caveats for
the Linear MCP server defined in `linear-mcp.json` in the same folder.
```
