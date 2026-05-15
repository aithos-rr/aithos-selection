# Project: Aithos Selection

This repository is a curated knowledge base of AI primitives — prompts, skills,
MCP server configs, agents, and workflows — used by Aithos for AI consulting
work with SMEs.

This file contains permanent invariants that you (Claude Code) must respect in
every session. It is auto-loaded.

## The three golden rules

1. **No duplication.** Every atom (prompt, skill, MCP config, tool, stack note)
   lives in exactly one place. Composites and recipes reference atoms via
   `manifest.yaml`, never by copying.

2. **Manifest is the source of truth.** When an agent or workflow needs to
   declare its dependencies, it does so in its `manifest.yaml`. Documentation
   prose may describe relationships but never replaces the manifest.

3. **Markdown and YAML only for content.** No proprietary formats, no JSON for
   human-edited content (only for machine-generated artifacts like n8n exports).
   Code goes in `tools/` as Python.

## Naming conventions

- All folders, files, identifiers: **kebab-case**. No spaces, no CamelCase.
- Versioned items use semver in the `version` field of frontmatter, or as a
  suffix when the file itself is the version boundary (e.g.
  `doc-extraction-v2.md`).
- Tags: lowercase, single word or hyphenated, prefer English for universals
  (`extraction`, `italian`, `legal`), use Italian only for domain-specific
  Italian terms.

## Stack constraints

- Python 3.12+ managed via `uv` (no system Python).
- Dependencies declared in a single root `pyproject.toml`.
- Allowed runtime libraries for `tools/`: `pydantic`, `pyyaml`, `typer`,
  `rich`, `pytest`. Do not add others without explicit instruction.
- All `tools/` scripts run as `uv run python tools/<script>.py`.
- `pre-commit` framework for git hooks.
- GitHub Actions for CI.

## Commit protocol

Conventional Commits format:

```
<type>(<scope>): <short imperative description>

<optional body>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.

Scope is the phase or component: `phase-1`, `phase-2`, `phase-3`, `phase-4`,
`governance`, `librarian`, `index`, `check`.

Commit at the end of each phase as specified in the task file.

## Branch policy

- `main` — stable, manually reviewed. Never push directly during bootstrap.
- `bootstrap` — the working branch during this initial buildout. All your
  commits go here.
- After bootstrap is merged, feature work uses `feat/<name>`, fixes `fix/<name>`.

## Folder structure

```
.
├── CLAUDE.md                # this file
├── PRD.md                   # strategic spec
├── INDEX.md                 # auto-generated (do not hand-edit)
├── CONTRIBUTING.md          # how to add content
├── README.md                # public-facing overview
├── _inbox/                  # quick dump zone (contents gitignored)
├── docs/                    # meta-docs about the repo itself
│   └── schemas/             # YAML schemas for manifests and frontmatter
├── skills/                  # Claude Code skills (Anthropic format)
├── prompts/                 # prompt library
│   ├── library/             # finished, versioned prompts
│   └── templates/           # parametric templates
├── mcp-servers/             # MCP server configurations
├── tools/                   # Python scripts, CLI utilities, plugins
├── stack/                   # operational playbooks (one .md per tool)
├── agents/                  # agent definitions (system prompt + manifest)
├── workflows/               # Claude/agent-based workflows
├── n8n-workflows/           # standalone n8n workflow exports
└── tasks/                   # phase specs for bootstrap
```

## Execution rules during bootstrap

- One phase per run. After completing a phase, commit, push, and stop.
- Never proceed to the next phase without explicit user instruction.
- Before each phase, re-read this file and the relevant `tasks/phase-N-*.md`.
- If a task file conflicts with this file for invariants (rules, naming,
  conventions), this file wins. If it conflicts for execution details, the
  task file wins.

## When in doubt

- Read `PRD.md` for strategic context.
- Read the current task file in `tasks/` for the specific spec.
- Ask the user before deviating from any spec. Do not improvise.
