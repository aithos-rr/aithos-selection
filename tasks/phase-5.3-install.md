# Phase 5.3 — Install script (skills and subagents deployment)

## Goal

Build a unified Python tool `tools/install.py` that deploys skills and
subagents from this curated library to their runtime location.
Without this tool, the library is purely catalog: skills sit in
`skills/<name>/` but Claude Code does not see them. The tool bridges
that gap by creating symlinks or copies in the appropriate
`.claude/skills/` or `.claude/agents/` location.

## Design choices (decided with user)

- **Deployment modes**: symlink (default) and copy. Symlink keeps the
  library as single source of truth; copy is for sharing across
  systems where the source path won't exist.
- **Install tracking**: a log file at `~/.aithos-install-log.yaml`
  records every install (what, where, mode, date). Enables `--list`
  and `--uninstall`.
- **Default targets**:
  - Skills install to `~/.claude/skills/<name>/` by default (global).
  - Subagents require an explicit `--target` (they live in a project's
    `.claude/agents/`, not globally).

## Prerequisites

- Phase 5.2-bis complete and pushed.
- The current branch should be a new feature branch off `main`:

  ```bash
  git checkout main
  git pull        # main is currently behind, PR #3 is open
  ```

  However, PR #3 (containing 5.2 + 5.2-bis) is still open. The user
  prefers to merge it at end of day along with 5.4 and 5.5.
  Therefore Phase 5.3 must be developed on a new branch that
  **branches off `feat/ingest-assets-batch-1`** (the current state),
  not off `main`:

  ```bash
  git checkout feat/ingest-assets-batch-1
  git pull        # ensure local is up to date
  git checkout -b feat/install-script
  ```

  This way Phase 5.3 builds on the work just done. After all phases
  are complete, the user will merge them in order (5.2-bundle, 5.3,
  5.4, 5.5) into `main`.

- `git status` clean, current branch `feat/install-script`.

## High-level flow

1. **Design** the CLI (`install`, `uninstall`, `list`, `info`).
2. **Implement** `tools/install.py` with the Typer framework
   (consistent with existing tooling).
3. **Test** locally by installing one skill, listing, then
   uninstalling.
4. **Update CONTRIBUTING.md** with a deployment section explaining
   how to use the script.
5. **Update README.md** briefly to mention the install tool.
6. **Commit and push**.

## Deliverables

### 1. `tools/install.py` — main script

Implement using Typer (already in the project's dependencies). The CLI
must expose four subcommands:

#### `install <item-path> [--target <path>] [--mode symlink|copy] [--force]`

Install a single skill or subagent.

Arguments:

- `item-path` (positional, required): relative path from repo root
  to the item to install. Must be either `skills/<name>` or
  `subagents/<name>`. Path validation is strict — the directory must
  exist, must contain the expected entrypoint (`SKILL.md` for skills,
  the manifest-declared `entrypoint` for subagents).

Options:

- `--target <path>` (optional): destination directory. Defaults:
  - For skills: `~/.claude/skills/<name>`
  - For subagents: **required** (no default; if missing, error and
    exit with code 2 and a message explaining that subagents need a
    project-specific target).
- `--mode symlink|copy` (default: `symlink`): how to deploy.
- `--force` (flag, default off): if the target already exists, remove
  it (recursively if it's a directory, unlink if it's a symlink) and
  proceed. Without `--force`, exit with code 3 and an error message.

Behavior:

1. Resolve the absolute path of the source (canonical, follows the
   current working dir's repo root).
2. Validate the source structure (skill or subagent).
3. Resolve the target path (expand `~`, normalize, make absolute).
4. Check for target collision; honor `--force` or abort.
5. Ensure the parent directory of the target exists; create it
   recursively if needed.
6. Apply the deployment:
   - `symlink`: `os.symlink(source_abs, target_abs)`
   - `copy`: `shutil.copytree(source_abs, target_abs,
     symlinks=False)` (recursive copy, dereference any internal
     symlinks)
7. Record the install in the log (see §2 below).
8. Print a confirmation message: `✓ Installed <name> to <target>
   (mode=<mode>)`.

#### `uninstall <name-or-target>`

Uninstall a previously installed item.

Argument:

- `name-or-target` (positional, required): either the item name
  (kebab-case, matches a logged install) or the full path of an
  installed item.

Behavior:

1. Look up in the log: find one or more matching entries.
2. If multiple matches (e.g. the same skill installed to multiple
   targets), list them and ask the user to disambiguate. Print exit
   code 4 if non-interactive.
3. For each match: remove the target (`os.unlink` if symlink,
   `shutil.rmtree` if directory). Remove the entry from the log.
4. Print: `✓ Uninstalled <name> from <target>`.

#### `list`

Show all currently installed items.

Output as a `rich` table with columns: `Name`, `Type` (skill/subagent),
`Target`, `Mode`, `Installed`.

If the log is empty: print `No items installed.`.

If a target listed in the log no longer exists on disk (user
manually deleted it): mark the row with a warning icon `⚠️` and
include the column `Status` with values `ok` or `missing`.

#### `info <item-path>`

Show metadata about a library item without installing.

Output: name, type, version, status, description, tags, and (for
subagents) declared tools/mcp_servers/skills_dependencies.

### 2. Install log — `~/.aithos-install-log.yaml`

Format:

```yaml
installs:
  - name: librarian
    type: skill
    source: /home/riccardo/projects/aithos-selection/skills/librarian
    target: /home/riccardo/.claude/skills/librarian
    mode: symlink
    installed: 2026-05-16T01:15:00Z

  - name: automation-architect
    type: subagent
    source: /home/riccardo/projects/aithos-selection/subagents/automation-architect
    target: /home/riccardo/projects/martina-os/.claude/agents/automation-architect
    mode: copy
    installed: 2026-05-16T02:30:00Z
```

The file is created on first install if missing. Operations on it
must be **atomic** (write to temp file, then rename) to avoid
corruption on partial writes.

The log file is NOT tracked in git (it's a user-local artifact).

### 3. Error handling and exit codes

Use distinct exit codes for scriptability:

- `0`: success
- `1`: generic error / unexpected exception
- `2`: invalid arguments (e.g. subagent without `--target`)
- `3`: target collision without `--force`
- `4`: ambiguous uninstall (multiple matches, non-interactive)
- `5`: source not found / not a valid skill or subagent
- `6`: log file corrupt or unreadable

All error messages should be printed via `rich` to stderr, with a
prefix `Error:` in red.

### 4. Idempotency

Re-installing the same item to the same target is a no-op (the log
already has the entry, the target already exists and points to the
same source). Print a message: `Already installed at <target>
(mode=<mode>). Use --force to reinstall.` and exit code 0.

This is important because the `nightly-sync` phase (5.4) may
re-install skills periodically; it must not error on each run.

### 5. Edge cases

- **Source moved/renamed**: if a previously-installed item's source
  no longer exists, `list` shows `Status: missing` for that entry.
  `uninstall` still works (removes target and log entry).
- **Target is a regular file (not directory or symlink)**: error,
  refuse to clobber.
- **Cross-device symlink**: if target is on a different filesystem
  and symlinks aren't supported, error explicitly and suggest
  `--mode copy`.
- **Permissions**: if target requires elevated permissions, error
  explicitly (don't try to sudo).
- **Relative source paths**: must be relative to the current working
  directory. If the user runs from elsewhere, the script should
  resolve correctly via `Path.cwd()` and `Path.resolve()`.

### 6. CONTRIBUTING.md update

Add a new section `## Deploying skills and subagents` after the
existing `## Adding a subagent` section. Cover:

- Why deployment is needed (catalog vs runtime location).
- Symlink vs copy mode — when to choose each.
- Default targets and how to override.
- Example commands for each subcommand.
- Mention of the install log location.

Length: ~30-40 lines.

### 7. README.md update

In the existing folder map, augment the `tools/` entry to mention
`install.py` briefly. One line is enough:

> `tools/` — Python utilities (index generator, validator, install
> script for deploying skills/subagents).

### 8. Test the script

Before committing, run a self-test inside the phase:

```bash
# Install the canonical example skill (a no-op skill, safe to test)
uv run python tools/install.py install skills/librarian

# Verify the symlink was created and resolves correctly
ls -la ~/.claude/skills/librarian
test -L ~/.claude/skills/librarian
readlink ~/.claude/skills/librarian
test -f ~/.claude/skills/librarian/SKILL.md

# List installs
uv run python tools/install.py list

# Uninstall
uv run python tools/install.py uninstall librarian

# Verify it's gone
test ! -e ~/.claude/skills/librarian
```

All eight commands must succeed (exit 0 where expected). If any
fails, fix the script before committing.

After the test, clean up: the log file should be back to its initial
state (no installs).

## Done criteria

```bash
# Script exists
test -f tools/install.py

# Script is executable in the project venv
uv run python tools/install.py --help

# All four subcommands work (smoke test)
uv run python tools/install.py install skills/librarian
test -L ~/.claude/skills/librarian
uv run python tools/install.py list
uv run python tools/install.py info skills/librarian
uv run python tools/install.py uninstall librarian
test ! -e ~/.claude/skills/librarian

# CONTRIBUTING.md extended
grep -q "Deploying skills and subagents" CONTRIBUTING.md

# README.md extended
grep -q "install" README.md

# Validation still passes (no regressions)
uv run python tools/generate_index.py --check
uv run python tools/check.py

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.3): unified install.py for deploying skills/subagents

Adds tools/install.py with four subcommands (install, uninstall, list,
info) supporting symlink and copy modes. Install log at
~/.aithos-install-log.yaml. Default target for skills is
~/.claude/skills/; subagents require an explicit --target.
CONTRIBUTING.md extended with a deployment section."
git push -u origin feat/install-script
```

## Stop here

After commit and push, stop. Do not start Phase 5.4.

Do not auto-create a PR. The user prefers to merge all remaining
phases at end of day in a single coherent batch.

## Safety brakes

- No network calls in this phase.
- Do not modify the install log if testing fails partway — clean up
  on error.
- Do not modify any imported assets from Phase 5.2 or 5.2-bis.
- Test installation must be done on a real path
  (`~/.claude/skills/librarian`) but cleaned up before commit, so the
  user's `~/.claude/skills/` is untouched after the phase completes.
