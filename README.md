# Aithos Selection

## What this is

A curated knowledge base of AI primitives — prompts, skills, MCP server
configs, agents, and workflows — used by Aithos to deliver AI consulting work
for small and medium-sized enterprises. The repository is part working
library, part portfolio asset, and part compounding leverage: every solved
problem becomes a reusable ingredient for the next engagement.

## Mental model

The repository encodes three layers of abstraction.

**Atoms (ingredients).** Single-purpose, reusable units. Each atom lives in
exactly one folder. Skills sit in `skills/`, prompts in `prompts/` (split
between finished `library/` items and parametric `templates/`), MCP server
configs in `mcp-servers/`, Python utilities in `tools/`, and tool-specific
operational playbooks in `stack/`.

**Composites.** Combinations of atoms that form a coherent unit but are not
yet a full workflow. `agents/` is the main composite folder: each agent is a
subfolder containing a system prompt (`agent.md`), a dependency manifest
(`manifest.yaml`), and a `README.md`.

**Subagents.** A fifth layer sitting between composites and recipes.
`subagents/` holds Claude Code subagents — Anthropic primitives that
declare their own `tools`, `mcpServers`, and `skills` dependencies, and
are invoked as slash-commands (`/<name>`) after being deployed under
`.claude/agents/` in a target project. Each subagent is a self-contained
folder with an entrypoint `.md` plus an Aithos-side `manifest.yaml` that
mirrors the entrypoint frontmatter for indexing.

**Recipes.** Orchestrated workflows that solve a complete user-facing task.
`workflows/` contains Claude/agent-based workflows that may delegate to n8n
flows. `n8n-workflows/` holds standalone n8n exports that are not part of a
Claude-orchestrated recipe.

**References.** A fourth category, distinct from the three above. Atoms,
composites, and recipes are content the repo *contains*; references are
content the repo *points to*. `references/` holds curated bookmarks —
GitHub repos in `repos/`, blog posts and papers in `articles/`, and
external workflow or skill templates in `templates/`. References are
never declared as `uses:` dependencies by composites or recipes; they
are pure curation.

Atoms are referenced by composites and recipes through `manifest.yaml`, never
by copying. See `PRD.md` for the strategic rationale and `CLAUDE.md` for the
invariants every contributor (human or AI) must follow.

## How to use this repo

For day-to-day contribution and editing rules, read
[`CONTRIBUTING.md`](./CONTRIBUTING.md). It covers how to add new prompts, MCP
configs, stack notes, agents, and workflows, plus how to use the `_inbox/`
quick-dump zone.

For the strategic spec, read [`PRD.md`](./PRD.md).

For the rules that bind every Claude Code session in this repo, read
[`CLAUDE.md`](./CLAUDE.md) — it is auto-loaded by Claude Code.

## Quick start for Claude Code sessions

The recommended way to start a session:

```bash
cd ~/projects/aithos-selection
claude
```

Claude Code auto-loads `CLAUDE.md` from the working directory. From there,
ask for what you need — adding a new prompt, drafting an agent, processing
the inbox — and Claude will follow the invariants in `CLAUDE.md` and the
guides in `CONTRIBUTING.md`.

To browse what already exists, open `INDEX.md` (auto-generated in Phase 3).

## Folder map

```
.
├── CLAUDE.md                # Invariants for Claude Code sessions (auto-loaded)
├── PRD.md                   # Strategic spec for the repository
├── INDEX.md                 # Auto-generated catalogue (do not hand-edit)
├── CONTRIBUTING.md          # How to add and update content
├── README.md                # This file
├── _inbox/                  # Quick-dump zone (contents gitignored)
├── docs/                    # Meta-docs about the repo itself
│   └── schemas/             # YAML schemas for manifests and frontmatter
├── skills/                  # Claude Code skills (Anthropic format)
├── prompts/                 # Prompt library
│   ├── library/             # Finished, versioned prompts
│   └── templates/           # Parametric templates with {{variables}}
├── mcp-servers/             # MCP server configurations (one JSON per server)
├── tools/                   # Python scripts, CLI utilities, plugins
├── stack/                   # Operational playbooks (one Markdown per tool)
├── agents/                  # Agent definitions (system prompt + manifest)
├── subagents/               # Claude Code subagents (entrypoint + manifest)
├── workflows/               # Claude/agent-based workflows
├── n8n-workflows/           # Standalone n8n workflow exports
├── references/              # Curated bookmarks to external resources
│   ├── repos/               # GitHub repositories
│   ├── articles/            # Blog posts, papers, documentation pages
│   └── templates/           # External n8n / skill / agent templates
└── tasks/                   # Phase specs for the bootstrap process
```
