# Project: Aithos Selection

This repository is a curated knowledge base of AI primitives — prompts, skills,
MCP server configs, agents, subagents, workflows, and curated references —
used by Aithos for AI consulting work with SMEs.

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

Scope identifies the phase or component touched. Bootstrap phases used the
`phase-N` form (e.g. `phase-1`, `phase-2`, … `phase-5.2`, `phase-5.2-bis`,
`phase-5.3`, `phase-5.4`, `phase-5.5`). Component scopes used during and
after bootstrap include `governance`, `librarian`, `index`, `check`,
`install`, `subagents`, `nightly-sync`. New ongoing work picks the scope
that best describes the touched area; introduce a new scope only when none
fits.

Commit at the end of each phase or logical unit of work, as specified in
the relevant task file (or — for ongoing work — when the change forms a
self-contained whole).

## Branch policy

- `main` — stable, manually reviewed. Never push directly.
- Feature work: `feat/<name>`. Fixes: `fix/<name>`. Chores: `chore/<name>`.
  Docs: `docs/<name>`.
- The bootstrap-era `bootstrap` branch is historical and no longer in use;
  all bootstrap phase work has been merged.

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
│   └── schemas/             # YAML schemas for manifests, frontmatter, references, subagents
├── skills/                  # Claude Code skills (Anthropic format)
├── prompts/                 # prompt library
│   ├── library/             # finished, versioned prompts (single-file or folder-as-prompt)
│   └── templates/           # parametric templates
├── mcp-servers/             # MCP server configurations
├── tools/                   # Python scripts (index, validator, install)
├── stack/                   # operational playbooks (one .md per tool)
├── agents/                  # agent definitions (system prompt + manifest)
├── subagents/               # Claude Code subagents (entrypoint + manifest)
├── workflows/               # Claude/agent-based workflows
├── n8n-workflows/           # standalone n8n workflow exports
├── references/              # curated bookmarks (repos/, articles/, templates/)
└── tasks/                   # task specs (active + archived bootstrap)
```

## Execution rules

- One phase or one logical unit of work per session. After completing it,
  commit, push, and stop.
- Never proceed past the agreed scope without explicit user instruction.
- Before starting a new task, re-read this file and the relevant task file
  in `tasks/` (or `tasks/archive/` if referring to a completed bootstrap
  phase).
- If a task file conflicts with this file for invariants (rules, naming,
  conventions), this file wins. If it conflicts for execution details, the
  task file wins.

## Bootstrap status

Bootstrap (Phases 1–5.5) is complete. Ongoing intake of new content
happens through the librarian skill's `nightly-sync` sub-flow (see
`skills/librarian/SKILL.md` §5). Historical phase specs live in
`tasks/archive/`.

## When in doubt

- Read `PRD.md` for strategic context.
- Check `tasks/archive/` for the spec of any completed bootstrap phase
  whose decisions are still relevant.
- Ask the user before deviating from any spec. Do not improvise.
