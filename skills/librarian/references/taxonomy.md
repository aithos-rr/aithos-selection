# Tag taxonomy

This file is the **canonical, closed set** of tags accepted in frontmatter
and manifests across the Aithos Selection repository. The librarian skill
consults it whenever it tags or classifies a file.

Rules common to every group:

- Tags are lowercase, kebab-case if multi-word (see
  `/docs/naming-conventions.md` section 4).
- Each item in this repository carries at least one tag from each of the
  three required groups: **category**, **domain**, **language**.
- Status and special tags are optional and complement (do not replace) the
  `status` field in frontmatter or manifest.

## 1. Category tags — what kind of task

What the atom or composite *does*, abstracted from the subject matter.

| Tag              | Meaning                                                       |
|------------------|---------------------------------------------------------------|
| `extraction`     | Pull structured fields out of unstructured content.           |
| `analysis`       | Interpret, compare, or evaluate content to reach a judgement. |
| `generation`     | Produce new artefacts from scratch (text, code, plans).       |
| `classification` | Assign items to predefined categories or labels.              |
| `summarization`  | Condense longer content into shorter form.                    |
| `translation`    | Convert between natural languages.                            |
| `reasoning`      | Multi-step inference, planning, or chain-of-thought work.     |
| `code`           | Generate, review, or transform source code.                   |
| `search`         | Retrieve information from a corpus, index, or external API.   |
| `automation`     | Drive an end-to-end process (often via n8n or tool calls).    |
| `evaluation`     | Score, grade, or test other prompts, agents, or models.       |

## 2. Domain tags — what subject matter

The business or knowledge domain the atom serves. Use `general` only when
the atom is genuinely cross-domain; otherwise pick the most specific match.

| Tag           | Meaning                                                       |
|---------------|---------------------------------------------------------------|
| `legal`       | Contracts, compliance, regulatory text, legal correspondence. |
| `finance`     | Accounting, financial analysis, controlling, treasury.        |
| `real-estate` | Property listings, valuations, transactions, tenancy.         |
| `marketing`   | Campaigns, copy, content strategy, brand assets.              |
| `sales`       | Lead qualification, outreach, CRM, pipeline work.             |
| `hr`          | Recruiting, onboarding, performance, internal comms.          |
| `operations`  | Ops playbooks, internal processes, tooling for delivery.      |
| `engineering` | Software engineering work that is not project-specific.       |
| `education`   | Training material, learning content, course design.           |
| `general`     | Cross-domain or domain-agnostic atom. Use sparingly.          |

## 3. Language tags

Always assign exactly one of the three.

| Tag             | Meaning                                                     |
|-----------------|-------------------------------------------------------------|
| `italian`       | Primary content language is Italian.                        |
| `english`       | Primary content language is English.                        |
| `multilingual`  | The atom is genuinely language-agnostic or covers several.  |

These mirror the `language` field values (`it`, `en`, `multilingual`) but
spelled out for use in the `tags` array.

## 4. Status tags — optional

These complement the `status` field in frontmatter or manifest. They are
not required and never replace the `status` field; use them when extra
nuance is helpful.

| Tag             | Meaning                                                     |
|-----------------|-------------------------------------------------------------|
| `experimental`  | Probationary work; the atom is being trialled.              |
| `production`    | Battle-tested in real Aithos client work.                   |
| `archived`      | Kept for history; not recommended for new work.             |

## 5. Special tags

Reserved tags with operational meaning.

| Tag         | Meaning                                                          |
|-------------|------------------------------------------------------------------|
| `example`   | The atom exists to demonstrate the schema or conventions.        |
| `canonical` | The atom is a reference fixture used by `check.py`; must not be deleted. |

`example` and `canonical` together identify the schema-validation fixtures
created during Phase 1. Removing or renaming an item that carries the
`canonical` tag breaks repository validation — do not propose such moves
without explicit user instruction.

## 6. Subtype hints — references only

These tags are **optional subtype hints** for items in `references/`.
They help the user search references by their nature without changing the
category/domain/language taxonomy above. They never substitute for the
required category/domain/language tags — they layer on top, just like
the `example`/`canonical` special tags in section 5.

| Tag                  | Meaning                                                  |
|----------------------|----------------------------------------------------------|
| `mcp-server`         | The reference points to an MCP server implementation.    |
| `n8n-template`       | The reference points to a reusable n8n workflow template.|
| `anthropic-skill`    | The reference points to an Anthropic-format Claude skill.|
| `developer-tool`     | The reference points to a developer-facing CLI, library, or service. |
| `learnn`             | Material sourced from the Learnn community / course platform. |
| `community-resource` | Third-party public material curated for future reference. |

Use only when the hint adds genuine signal — do not tag every reference
with one of these. They are unlocked specifically for the
`process-reference` sub-flow in `SKILL.md` section 4 and for subagent
bundles in `subagents/` that originate from third-party sources. When
applied to a subagent, `learnn` and `community-resource` are usually
combined: `learnn` identifies the specific source; `community-resource`
identifies that the item is third-party material rather than internally
authored.

## 7. Adding a new tag

The taxonomy is intentionally closed so that tagging stays useful. New
tags are not forbidden, but they require explicit user approval.

Process:

1. During inbox processing or tagging, the librarian proposes a tag that is
   not in this file.
2. In the plan, the proposed tag is flagged exactly as
   `new tag, confirm with user`.
3. If the user approves the new tag, the librarian:
   - Adds it to this file under the appropriate group (with a one-line
     description).
   - Applies it to the file under triage.
   - Both changes ship in the **same commit** so the taxonomy can never
     fall behind the tagged content.
4. If the user rejects the new tag, the librarian picks the closest
   accepted tag instead, or drops the tag from the proposal.
