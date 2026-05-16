# Phase 5.4 — Nightly sync sub-flow

## Goal

Add a `nightly-sync` sub-flow to the `librarian` skill that, in a single
command, performs the user's typical evening maintenance routine on the
repository:

1. Process anything new in `_inbox/` (zips, prompts, images, subagents).
2. Delta-sync GitHub stars (add new ones, flag unstarred).
3. Validate, commit, push — leaving the user on the current feature
   branch with a clean working tree.

The sub-flow is intended to be invoked in a Claude Code session with
phrases like "run nightly sync", "process inbox and sync stars",
"nightly check", etc. It is **fully auto-pilot** within a single
session — no per-item confirmation. The user reviews the resulting
commit afterwards.

## Design choices (decided with user)

- **Trigger**: librarian sub-flow, invoked via natural language in a
  Claude Code session (not a standalone bash script).
- **Scope**: inbox processing + stars delta. No automatic install of
  skills/subagents — the user installs manually when needed.
- **Branch behavior**: the sub-flow operates on the currently
  checked-out branch. It does NOT switch branches. If the user wants
  the work on a separate feature branch, they create it before
  invoking nightly-sync.
- **Commit and push**: the sub-flow commits and pushes automatically.
  If there is nothing to do (empty inbox, no new stars, no unstarred
  delta), it prints "Nothing to sync" and exits without committing.
- **Stars delta-aware**: must NOT overwrite existing reference files'
  user-edited content (like "Why this is interesting"). It only
  updates volatile GitHub metadata (stars count, last commit) on
  existing files when stars changed significantly.

## Prerequisites

- Phase 5.3 complete and pushed.
- Working tree clean, current branch `feat/install-script` (or any
  feature branch — the sub-flow doesn't care which, only that it's
  not `main`).
- Phase 5.4 work happens on a **new branch off feat/install-script**:

  ```bash
  git checkout feat/install-script
  git checkout -b feat/nightly-sync
  ```

  `git status` clean, current branch `feat/nightly-sync`.

## High-level flow

This phase is purely an extension of the librarian skill — no new
top-level categories, no schema changes, no new tools. Therefore:

1. **Extend `skills/librarian/SKILL.md`** with a new `nightly-sync`
   sub-flow that orchestrates the existing logic of
   `process-inbox` + a new delta-aware version of `process-reference`
   for stars.
2. **Add detailed reference docs** for the new delta logic.
3. **Update the CONTRIBUTING and README** to mention the new sub-flow.

## Deliverables

### 1. New sub-flow in `skills/librarian/SKILL.md`

Add a section `## Sub-flow: nightly-sync` to the SKILL.md, after the
existing `process-reference` sub-flow.

#### Trigger phrases

The skill should recognize these phrases as invocations of
`nightly-sync`:

- "run nightly sync"
- "nightly sync"
- "process inbox and sync stars"
- "evening sync"
- "evening routine"
- "sync everything"
- Italian equivalents: "sync serale", "controlla l'inbox", "fai la
  routine serale", "sincronizza tutto"

Also extend the top-level skill description in the frontmatter to
mention this sub-flow.

#### Algorithm

Execute these steps in order, gracefully handling each "nothing to
do" case:

**Step 1: Pre-flight check.**

- Verify current branch is NOT `main`. If it is, print an error and
  exit ("nightly-sync requires a feature branch; create one with
  git checkout -b feat/nightly-YYYY-MM-DD before running").
- Verify `git status` is clean. If not, print a warning listing the
  uncommitted changes and ask the user to commit or stash first.
  Exit without action.

**Step 2: Inbox processing.**

- Reuse the logic from Phase 5.2 (the `process-inbox` sub-flow) and
  Phase 5.2-bis (subagent recognition) in auto-pilot mode.
- If `_inbox/` is empty (only `.gitkeep` and `README.md`), skip this
  step and log "Inbox: empty, skipping."
- If there are entries, process them all deterministically. Generate
  a sub-report of what was processed.

**Step 3: Stars delta sync.**

- Fetch the current starred list via `gh api
  users/aithos-rr/starred --paginate`.
- For each starred repo, compute the canonical id (`<owner>-<name>`,
  kebab-case).
- Compare with existing files in `references/repos/`:
  - **New star** (not present as a reference file): create a new
    reference file with `status: active`, default frontmatter, and
    the canonical body template. Use the same template and tag
    derivation as Phase 5.1's stars import.
  - **Existing star** (already a reference): update only volatile
    metadata fields (`github_stars`, `github_last_commit`,
    `updated`) IF they have changed. **Never** modify the body,
    `description`, `tags`, `language`, or any user-edited content.
  - **Unstarred** (reference present but no longer in user's stars):
    do NOT delete. Print a flag in the report: "Reference
    `<owner>-<name>` is no longer starred. Consider archiving by
    changing status: active → status: archived, or delete the
    file."
- The example reference file
  `references/repos/example-anthropic-sdk-python.md` is excluded
  from delta logic — it's canonical and untouched.

**Step 4: Validate.**

- Run `uv run python tools/generate_index.py` to refresh `INDEX.md`.
- Run `uv run python tools/check.py`.
- If validation fails, STOP and report. Do not commit broken state.

**Step 5: Commit.**

- If nothing was actually changed (no new files, no metadata
  updates), print "Nothing to sync." and exit code 0 without
  committing.
- Otherwise, generate a commit message:

  ```
  chore(nightly-sync): <summary>

  Inbox: <N entries processed>
  Stars: <X new, Y metadata updates, Z unstarred flags>

  See report in session output for details.
  ```

  Where summary is a short comma-separated list like
  `3 inbox, 2 new stars` or `2 inbox` or `1 new star` etc.

**Step 6: Push.**

- `git push` (use the current branch's upstream; if no upstream is
  set, set it with `git push -u origin <branch>`).

**Step 7: Final report.**

Print a unified report combining inbox processing and stars delta:

```
Nightly sync complete (commit <hash>).

Inbox processed:
  - <N> items
  Skills: <S>, Subagents: <SA>, Prompts: <P>, Visual: <V>
  Unhandled: <U>

Stars delta:
  - <X> new starred repos imported
  - <Y> existing references updated (metadata changed)
  - <Z> references flagged as unstarred (no longer in your GitHub stars)

References created:
  - <id-1>
  - <id-2>
  ...

References updated (metadata only):
  - <id-1>: stars 5234 → 5489
  - <id-2>: stars 412 → 425

Flagged for review (unstarred or anomalies):
  - <id>: <reason>

Validation: all 11 checks pass.
Commit: <hash>, pushed to origin/<branch>.
```

If nothing was synced, print:

```
Nightly sync: nothing to do.
  Inbox: empty (excluding .gitkeep, README.md).
  Stars: no delta detected.

Repository unchanged. No commit created.
```

#### Important constraints

- **Idempotent**: re-running nightly-sync immediately after a
  successful run must result in "Nothing to sync."
- **Safe by default**: never deletes user-edited content. Worst case
  on failure: prints a report and exits without modifying anything.
- **Network-aware**: the stars step requires `gh api` (network). If
  the network fails, the inbox step has already completed; report
  partial success and exit code 0 with a warning ("Stars sync
  skipped due to network error; inbox processed normally").
- **Reusable logic**: the implementation should reuse code from
  `process-inbox` and `process-reference` sub-flows where possible
  (or at minimum, share the algorithmic patterns documented in the
  classification heuristics).

### 2. New reference doc — `skills/librarian/references/nightly-sync-runbook.md`

A runbook explaining how nightly-sync works internally, for the
skill's own consultation when invoked. This is the "implementation
notes" the skill reads to execute correctly.

Sections:

- **When to invoke**: trigger phrases (mirror of the skill section).
- **Pre-flight checks**: branch, working tree, gh auth.
- **Inbox classification reuse**: pointer to
  `classification-heuristics.md`.
- **Stars delta algorithm**: step-by-step pseudocode for the delta
  comparison logic.
- **Volatile fields**: explicit list of frontmatter fields that may
  be auto-updated on existing references (only `github_stars`,
  `github_last_commit`, `updated`). All other fields are
  user-owned.
- **Commit message conventions**: format and examples.
- **Failure modes**: what to do if `gh api` fails, if extraction
  fails, if check.py fails.
- **Recovery**: how to recover from a bad state (mostly: don't
  commit, manual review).

Length: ~150-200 lines, similar in depth to
`classification-heuristics.md`.

### 3. Update `skills/librarian/references/taxonomy.md`

No structural change, just add one new tag in the "Special tags"
section:

- `nightly-sync` — added automatically to reference files updated
  by the nightly-sync sub-flow (so the user can see which
  references have been touched recently).

Actually wait — adding a tag to every reference touched would
pollute. Reconsider: do NOT add this tag automatically. Just
mention in the runbook that the `updated` field is the canonical
way to see what nightly-sync touched.

Therefore: no change to taxonomy.md. Skip this deliverable.

### 4. README.md update

Add one sentence to the "Quick start for Claude Code sessions"
section:

> For evening maintenance — processing the inbox and syncing GitHub
> stars in one go — open a Claude Code session and say "run nightly
> sync". The librarian skill handles the rest.

### 5. CONTRIBUTING.md update

Add a small section `## Evening routine` at the end of the document
explaining:

- The nightly-sync sub-flow exists for hands-off batch processing.
- It's invoked by natural language in Claude Code.
- Pre-conditions: branch is not `main`, working tree clean.
- What it does: inbox + stars delta + commit + push.
- What it does NOT do: install skills, modify user-edited content,
  delete unstarred references.

Length: ~20-30 lines.

### 6. Smoke test

After implementing, run a smoke test:

```bash
# Verify the librarian SKILL.md mentions the new sub-flow
grep -q "nightly-sync" skills/librarian/SKILL.md

# Verify the runbook exists
test -f skills/librarian/references/nightly-sync-runbook.md

# Validation
uv run python tools/generate_index.py --check
uv run python tools/check.py
```

All must pass.

Note: a full end-to-end test of nightly-sync requires actually
invoking the librarian skill in a Claude Code session, which is
not testable from within the phase's own session. The smoke test
above verifies the artifacts exist and the system remains
consistent. Real-world testing happens when the user invokes it
the next time they have new content.

## Done criteria

```bash
# Sub-flow added
grep -q "nightly-sync" skills/librarian/SKILL.md
grep -qi "Sub-flow: nightly-sync\|nightly sync" skills/librarian/SKILL.md

# Runbook created
test -f skills/librarian/references/nightly-sync-runbook.md

# README updated
grep -q "nightly sync" README.md

# CONTRIBUTING updated
grep -qi "Evening routine\|nightly-sync\|nightly sync" CONTRIBUTING.md

# Validation passes (no regressions)
uv run python tools/generate_index.py --check
uv run python tools/check.py

git status --short
```

## Commit

```bash
git add .
git commit -m "feat(phase-5.4): nightly-sync sub-flow for librarian

Adds a hands-off evening routine that processes the inbox and
delta-syncs GitHub stars in one Claude Code session. Reuses
existing process-inbox and process-reference logic; never modifies
user-edited content. Reference runbook in
skills/librarian/references/nightly-sync-runbook.md. README and
CONTRIBUTING updated to document the trigger phrases and
constraints."
git push -u origin feat/nightly-sync
```

## Stop here

After commit and push, stop. Do not start Phase 5.5.

Do not auto-create a PR. The user prefers to merge all remaining
phases at end of day in a single coherent batch.

## Safety brakes

- No network calls in this phase (we're DOCUMENTING the sub-flow,
  not invoking it). The actual gh api call happens at runtime when
  the user invokes nightly-sync in a future session.
- Do not modify Phase 5.1's reference files. The runbook may
  reference them but must not change them.
- Do not modify any tool scripts (tools/*.py) in this phase. The
  sub-flow is a librarian skill capability, not a new tool. It
  operates by orchestrating CC's existing abilities + reading the
  runbook for guidance.
