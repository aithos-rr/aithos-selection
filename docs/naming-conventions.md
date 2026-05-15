# Naming Conventions

This document expands PRD section 6 with explicit examples and edge cases.
It is binding for every contributor (human or AI). When in doubt, this file
plus `CLAUDE.md` win.

## 1. Folders and files

All folders and files are **kebab-case**: lowercase ASCII letters, digits,
and hyphens. No spaces, no underscores, no CamelCase.

### Examples — accepted

- `mcp-servers/`
- `prompts/library/doc-extraction-v2.md`
- `agents/agent-doc-analyst/manifest.yaml`
- `stack/lm-studio.md`

### Examples — rejected

- `mcp_servers/` (underscore)
- `McpServers/` (CamelCase)
- `mcp servers/` (space)
- `MCP-Servers/` (uppercase)
- `prompts/library/Doc Extraction.md` (space + CamelCase)

### Multi-word folders

Always use a single hyphen between words. The repository uses `mcp-servers`,
not `mcp_servers`. The same applies to multi-word file stems
(`doc-extraction`, not `doc_extraction`).

### Special folders

A small set of folders is exempt from kebab-case because they follow
established conventions outside this repository:

| Folder            | Reason                                             |
|-------------------|----------------------------------------------------|
| `_inbox/`         | Leading underscore marks it as a staging area.     |
| `.github/`        | GitHub-mandated location for Actions and metadata. |
| `.github/workflows/` | GitHub-mandated.                               |
| `.git/`           | Created and managed by git.                        |
| `.venv/`          | uv-managed virtual environment (gitignored).       |

Do not invent new exempt folders.

### Acceptable characters and regex

A valid folder or file stem matches:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

Allowed file extensions in human-edited content: `.md`, `.yaml`, `.yml`,
`.toml`, `.json` (only for machine-generated artifacts and MCP server
configs).

Disallowed patterns (with regex examples):

- Underscores: anything matching `_` (except the exempt folders listed
  above).
- Trailing or leading hyphens: `^-` or `-$`.
- Consecutive hyphens: `--`.
- Uppercase letters: `[A-Z]`.

## 2. Identifiers

Identifiers in frontmatter (`id`) and in manifests (`name`) follow the same
kebab-case rule. They must match the parent file or folder name where
applicable.

### Examples

- File `prompts/library/doc-extraction-v2.md` → frontmatter
  `id: doc-extraction-v2`.
- Folder `agents/agent-doc-analyst/` → `manifest.yaml` field
  `name: agent-doc-analyst`.

A mismatch between file/folder name and identifier is a `check.py` error in
Phase 4.

## 3. Versioning

Two distinct mechanisms exist; pick exactly one per item.

### 3.1 Frontmatter/manifest `version` field

Use for in-place changes that do not break consumers. Bump per semver:

- Patch (`1.0.0` → `1.0.1`): typo, clarification, additional example.
- Minor (`1.0.0` → `1.1.0`): additive change, new optional section.
- Major (`1.0.0` → `2.0.0`): incompatible change. Often you should use a
  version-suffixed file instead — see below.

### 3.2 Version-suffixed filenames

Use when a major rewrite changes the intent of the atom and you want to keep
the old version around for history or for consumers still pinned to it.

- Old file: `prompts/library/doc-extraction.md` →
  `status: deprecated` in its frontmatter.
- New file: `prompts/library/doc-extraction-v2.md` → `status: stable`,
  `version: 2.0.0`.

Rules:

- Start suffixing at `-v2`. Never write `-v1`; the un-suffixed file is
  implicitly v1.
- Suffix numbers are strictly monotonic. Skip none.
- Deprecated files must not be deleted during bootstrap; they are kept for
  history.

## 4. Tags

Tags live in frontmatter (`tags: [...]`) and manifests (`tags: [...]`). They
are lowercase, kebab-case if multi-word.

### Language choice

Prefer English for universal concepts; use Italian only when the concept is
genuinely Italian-specific.

| Concept                          | Tag             |
|----------------------------------|-----------------|
| Document extraction              | `extraction`    |
| Italian language content         | `italian`       |
| Legal domain                     | `legal`         |
| Codice fiscale (Italian-specific)| `codice-fiscale`|
| Partita IVA (Italian-specific)   | `partita-iva`   |
| Generic CRM                      | `crm`           |
| Italian healthcare codes (SSN)   | `ssn`           |

A good rule of thumb: if the tag corresponds to a term Italians would also
write in English in a professional context, use English. If it is a proper
noun or a domain term with no clean English equivalent, keep Italian.

### Examples — accepted

- `extraction`
- `italian`
- `legal`
- `partita-iva`
- `pdf-parsing`

### Examples — rejected

- `Extraction` (uppercase)
- `pdf_parsing` (underscore)
- `partitaIva` (CamelCase)
- `partita iva` (space)

## 5. Branch names

- `bootstrap` — the working branch during initial buildout.
- `feat/<name>` — new features.
- `fix/<name>` — bug fixes.
- `chore/<name>` — chores, dependency bumps, formatting.
- `docs/<name>` — documentation changes only.

`<name>` itself is kebab-case (e.g. `feat/agent-doc-analyst`).

## 6. Commit messages

Conventional Commits. See `CLAUDE.md` section *Commit protocol* for the
authoritative spec. Recap:

```
<type>(<scope>): <short imperative description>
```

Type ∈ {`feat`, `fix`, `chore`, `docs`, `refactor`, `test`}.
Scope during bootstrap ∈ {`phase-1`, `phase-2`, `phase-3`, `phase-4`,
`governance`, `librarian`, `index`, `check`}.
