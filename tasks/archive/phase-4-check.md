# Phase 4 — Validator and CI

## Goal

Implement `tools/check.py`, a single-entry validator that enforces all
repository invariants. Wire it into a GitHub Action that runs on every push
and pull request.

## Prerequisites

- Phases 1, 2, 3 complete and committed.
- `tools/generate_index.py` works and is idempotent.
- You are on branch `bootstrap`.

## Deliverables

### 1. `tools/check.py`

A Python script that runs all repository validations and exits non-zero on
any failure.

#### CLI

```bash
uv run python tools/check.py [--fix]
```

- Without flags: runs all checks, reports issues, exits non-zero if any fail.
- `--fix`: where safely possible, auto-fixes issues (e.g. regenerate
  `INDEX.md`). Exits 0 if fixes succeed; exits non-zero if some issues are
  unfixable.

#### Checks (run all, do not fail-fast)

1. **Manifest schema compliance**: every `agents/*/manifest.yaml` and
   `workflows/*/manifest.yaml` validates against
   `docs/schemas/manifest.schema.yaml`.
2. **Frontmatter schema compliance**: every `prompts/**/*.md`, `stack/*.md`,
   and `skills/*/SKILL.md` (the skill-format frontmatter, not the full
   prompt schema) has a frontmatter block with the required fields per the
   relevant schema.
3. **No broken references**: every path listed in a manifest's `uses` block,
   `system_prompt` field, `agents:` array, or `n8n_workflows:` array must
   resolve to an existing file or folder.
4. **No duplicate atoms**: the same content (by SHA-256 hash of the body
   *without* frontmatter) does not appear in two different atom locations.
   Warn if two atoms have the same `name` field or `id` frontmatter.
5. **Composite completeness**: every `agents/<name>/` folder contains
   `agent.md`, `manifest.yaml`, and `README.md`. Every `workflows/<name>/`
   folder contains `flow.md`, `manifest.yaml`, and `README.md`.
6. **Index up to date**: `INDEX.md` matches `generate_index.py` output.
   This is equivalent to running `generate_index.py --check`.
7. **Naming conventions**: every folder name under `agents/`, `workflows/`,
   `skills/`, `prompts/library/`, `prompts/templates/`, `mcp-servers/`,
   `stack/`, `tools/`, `n8n-workflows/` is kebab-case (regex
   `^[a-z0-9]+(-[a-z0-9]+)*$`). The only exception is `_inbox` itself.

#### Output format

Use `rich` to print a summary table:

```
              Aithos Selection — Repository Check
┌─────────────────────────────────────┬─────────┬─────────────────────────┐
│ Check                               │ Status  │ Details                 │
├─────────────────────────────────────┼─────────┼─────────────────────────┤
│ Manifest schema compliance          │ ✓       │ 1 manifest valid        │
│ Frontmatter schema compliance       │ ✓       │ 1 file valid            │
│ No broken references                │ ✓       │                         │
│ No duplicate atoms                  │ ✓       │                         │
│ Composite completeness              │ ✓       │ 1 agent complete        │
│ Index up to date                    │ ✗ FAIL  │ Run generate_index.py   │
│ Naming conventions                  │ ✓       │                         │
└─────────────────────────────────────┴─────────┴─────────────────────────┘

1 check failed.
```

For each failing check, print details below the table (which files, which
issues) before exiting.

Exit code: `0` if all pass, `1` if any fail.

#### Implementation notes

- **Reuse code from Phase 3.** Import `discover_atoms`, `discover_composites`,
  `discover_recipes`, and `build_inverse_graph` from
  `tools/generate_index.py`. Do not duplicate the discovery logic. If
  needed, factor common helpers into `tools/_common.py`.
- Each check is a separate function with signature
  `def check_<name>(root: Path) -> CheckResult` where `CheckResult` is a
  dataclass with `passed: bool`, `summary: str`, and `details: list[str]`.
- Run all checks even after a failure. Collect all results, then render the
  table once.

### 2. `.github/workflows/check.yml`

A GitHub Action that runs `check.py` on every push to any branch and on
pull requests targeting `main`.

```yaml
name: check

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync

      - name: Run repository check
        run: uv run python tools/check.py
```

### 3. Smoke test before committing

```bash
uv run python tools/check.py
```

Must exit `0` on the current repo state.

Then, to confirm the validator catches errors, run a temporary failure
test:

```bash
# Temporarily break a reference
sed -i 's|example-hello-world.md|nonexistent.md|' agents/example-echo-agent/manifest.yaml

# Validator should now fail
uv run python tools/check.py
echo "Exit code: $?"   # must be 1

# Revert
git checkout agents/example-echo-agent/manifest.yaml

# Validator should pass again
uv run python tools/check.py
```

Do not commit the temporary break.

## Done criteria

```bash
# Files exist
test -f tools/check.py
test -f .github/workflows/check.yml

# All checks pass on current state
uv run python tools/check.py

# Generator and validator agree
uv run python tools/generate_index.py --check

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-4): check.py validator and GitHub Action CI"
git push
```

After pushing, verify on GitHub that the `check` action runs and passes on
the `bootstrap` branch. The first run may be slower because the runner
must download dependencies; subsequent runs use the cache.

If the CI fails on the `bootstrap` branch, do not push a fix automatically.
Report the failure to the user and wait for instruction.

## Stop here — final stop of bootstrap

This is the last automated phase. Do not start Phase 5 (manual bulk-ingest
of real content).

After this commit, the repository is ready for Riccardo to:

1. Open a PR from `bootstrap` to `main` for review.
2. Merge once approved.
3. Start dropping real content into `_inbox/` and invoking the `librarian`
   skill in a fresh Claude Code session.
