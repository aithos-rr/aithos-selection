# Nightly sync — runbook

The internal runbook the `librarian` skill consults when invoking the
`nightly-sync` sub-flow (see `SKILL.md` §5). It documents the exact
steps, the bounded mutations, the commit-message conventions, and the
recovery procedure for each failure mode.

This file is read-only at runtime. Update it only when the sub-flow's
contract changes (e.g. a new validation step, a new volatile field).

## 1. When to invoke

Trigger phrases (English):

- "run nightly sync"
- "nightly sync"
- "process inbox and sync stars"
- "evening sync"
- "evening routine"
- "sync everything"

Trigger phrases (Italian):

- "sync serale"
- "controlla l'inbox"
- "fai la routine serale"
- "sincronizza tutto"

Do **not** invoke this sub-flow:

- When the user is editing a specific file by hand (use the hand-driven
  flow, not the orchestrator).
- When the user explicitly says "just process the inbox" (run
  `process-inbox` alone) or "just bookmark this" (run
  `process-reference` alone).
- When the working tree is dirty or the current branch is `main`
  (Step 1 will abort anyway, but flag this proactively).

## 2. Pre-flight checks

Before touching anything, verify:

1. **Branch.** `git rev-parse --abbrev-ref HEAD` must NOT be `main`.
   If it is, print:

   > nightly-sync requires a feature branch; create one with
   > `git checkout -b feat/nightly-YYYY-MM-DD` before running.

   Exit without action.

2. **Working tree.** `git status --porcelain` must be empty, ignoring
   files inside `_inbox/` (which are gitignored anyway). If there are
   uncommitted edits or untracked files outside `_inbox/`, list them
   and ask the user to commit or stash first. Exit without action.

3. **`gh` auth (lazy check).** Do not pre-flight `gh auth status`;
   instead, attempt Step 3 and catch the failure gracefully (see §8
   *Failure modes*). The inbox step (Step 2) does not need network at
   all and should still run if `gh` is broken.

## 3. Inbox classification reuse

Step 2 of the sub-flow reuses the algorithm in
[`classification-heuristics.md`](./classification-heuristics.md) verbatim,
including the additions made in Phase 5.2-bis for subagent
recognition. Behavioural notes specific to nightly-sync:

- **Auto-pilot.** No per-item confirmation. The user pre-curated the
  inbox; everything in it should be ingested.
- **Skip noise silently.** `.gitkeep`, `README.md` (the inbox's own
  scaffolding), and any name ending in `:Zone.Identifier`.
- **Safety brake.** If `_inbox/` (excluding scaffolding) contains more
  than 60 entries, abort the inbox step with the same message used by
  `process-inbox`. The stars step (Step 3) still runs; the abort is
  reported in the final summary.
- **Empty inbox.** Log `Inbox: empty, skipping.` and proceed to
  Step 3.

For each processed entry record:

- The source path inside `_inbox/`.
- The destination path created.
- The classification (`skill`, `subagent`, `prompt`, `visual-prompt`,
  `reference`, `unhandled`).
- Any inferred metadata that warranted a manual-review flag.

These records feed both the commit message and the final report.

## 4. Stars delta algorithm

The delta step is the only mutator that exists *just* in this
sub-flow. It is implemented inside `process-reference` as a
delta-only variant.

```
listing = run("gh api users/aithos-rr/starred --paginate")
remote = { canonical_id(r): r for r in listing }
local  = { stem(p): p for p in references/repos/*.md
           if stem(p) != "example-anthropic-sdk-python" }

new_ids       = remote.keys - local.keys
existing_ids  = remote.keys & local.keys
unstarred_ids = local.keys  - remote.keys

# New stars — create reference files
for id in sorted(new_ids):
    fm = derive_frontmatter_from_repo(remote[id])
    write(references/repos/{id}.md, frontmatter=fm, body=canonical_template)
    record_created(id)

# Existing — volatile-only update
for id in sorted(existing_ids):
    file_fm = read_frontmatter(local[id])
    new_stars         = remote[id].stargazers_count
    new_last_commit   = remote[id].pushed_at.date()
    if file_fm.github_stars != new_stars
       or file_fm.github_last_commit != new_last_commit:
        rewrite_frontmatter_fields_only(local[id], {
            "github_stars": new_stars,
            "github_last_commit": new_last_commit,
            "updated": today(),
        })
        record_updated(id, file_fm.github_stars, new_stars)

# Unstarred — flag, never delete
for id in sorted(unstarred_ids):
    record_flagged(id, reason="no longer in your GitHub stars")
```

`canonical_id(repo)` is `<owner>-<name>`, both lowercased, with any
character not matching `[a-z0-9-]` replaced by `-`, collapsed
hyphens, and trimmed. This mirrors Phase 5.1's identifier derivation.

`derive_frontmatter_from_repo` follows the same rules as Phase 5.1's
stars import: required fields (`id`, `name`, `type: reference`,
`subtype: repo`, `url`, `status: active`, `description`, `tags`,
`language`, `created`, `updated`, `author: riccardo`) plus the
optional GitHub snapshot fields (`github_owner`, `github_repo`,
`github_stars`, `github_language`, `github_topics`,
`github_last_commit`). The canonical body template is the short
`# <Name>` + `[link](url)` + `## Why this is interesting` (left
empty for the user) + `## Notes` (optional) shape documented in
`CONTRIBUTING.md` §"Adding a reference".

## 5. Volatile fields

The only frontmatter fields that nightly-sync may auto-rewrite on an
**existing** reference file are:

- `github_stars`
- `github_last_commit`
- `updated`

Every other field is user-owned and must be preserved byte-for-byte:

- `id`, `name`, `type`, `subtype`, `url`, `status`, `description`,
  `language`, `created`, `author`
- `tags`
- `github_owner`, `github_repo`, `github_language`, `github_topics`
  (these are snapshots taken at creation time; do not refresh them)
- The Markdown body in its entirety, including
  `## Why this is interesting` notes the user has written by hand

When rewriting the three volatile fields, preserve key order in the
frontmatter block (don't reformat the YAML, don't reorder unrelated
keys, don't strip comments).

A *new* reference file created by Step 3 is allowed to set every
field — it has no user content to preserve yet.

## 6. Commit message conventions

Format:

```
chore(nightly-sync): <summary>

Inbox: <N entries processed>
Stars: <X new, Y metadata updates, Z unstarred flags>

See report in session output for details.
```

`<summary>` is a short comma-separated list of the buckets that
actually changed something. Skip zero buckets.

Examples:

- `chore(nightly-sync): 3 inbox, 2 new stars`
- `chore(nightly-sync): 2 inbox`
- `chore(nightly-sync): 1 new star, 5 metadata updates`
- `chore(nightly-sync): 7 metadata updates`

If nothing changed, do NOT create a commit. Print:

```
Nightly sync: nothing to do.
  Inbox: empty (excluding .gitkeep, README.md).
  Stars: no delta detected.

Repository unchanged. No commit created.
```

…and exit code 0.

## 7. Final report

The closing report combines the two streams. Use this shape when at
least one mutation happened:

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

If the run was a no-op, use the `Nightly sync: nothing to do.` shape
from §6 instead.

## 8. Failure modes

Each failure mode below describes what the sub-flow MUST do — not
what it MIGHT do. Be explicit; never silently mask errors.

- **Not on a feature branch.** Step 1 stops the run. Print the
  prescribed message and exit 0 (this is a user-error nudge, not a
  system failure). Nothing on disk is touched.

- **Working tree dirty.** Step 1 stops the run. List the offending
  paths (`git status --short` excluding `_inbox/`) and ask the user
  to commit or stash. Exit 0. Nothing on disk is touched.

- **Inbox safety brake (>60 entries).** Abort Step 2 with the same
  message used by `process-inbox` (`Inbox unexpectedly large (>60
  entries). Aborting to prevent runaway.`). Step 3 still runs; the
  abort is reported in the final summary.

- **`gh` not authenticated, rate-limited, or offline.** Step 3 is
  skipped. Print a warning:

  > Stars sync skipped due to network error: <short error>; inbox
  > processed normally.

  If Step 2 produced changes, continue to Steps 4-6 with inbox-only
  results. If Step 2 was also a no-op, fall through to the "nothing
  to do" report.

- **Validation fails after the run** (`check.py` returns non-zero, or
  `generate_index.py --check` reports stale after a regeneration).
  Step 4 stops the run before any commit. Print the validator's
  output and:

  > Validation failed. Inbox/stars changes are on disk but were NOT
  > committed. Inspect with `git status` and `git diff`, fix the
  > issue (often a malformed frontmatter the sub-flow could not
  > auto-correct), then either commit manually or `git restore .` to
  > discard.

  Exit 1.

- **`git push` fails** (no upstream, auth issue, remote rejection).
  The commit has already been created locally in Step 5. Print the
  push error and:

  > The commit was created locally but pushing to origin failed:
  > <error>. Run `git push` once the issue is resolved, or
  > `git reset --soft HEAD~1` to undo the commit if you prefer to
  > redo the run.

  Exit 1.

## 9. Recovery

The sub-flow is designed to fail safely: at any failure point, the
worst-case state is reversible with standard git commands.

- **After a Step 4 failure** (validation), nothing is committed. Use
  `git restore .` and `git clean -fd` to discard the inbox/stars
  changes, or inspect them manually and fix the validation issue
  before re-running.

- **After a Step 6 failure** (push), the commit exists locally.
  Either fix the push issue and run `git push`, or
  `git reset --soft HEAD~1` to undo the commit while keeping the
  changes staged.

- **Accidental unstarred deletion** is not possible — the sub-flow
  never deletes files. If the report flags a reference as unstarred,
  acting on the flag is a manual user choice (edit `status` to
  `archived`, or `git rm` the file).

- **Volatile field rewrite went wrong.** Because Step 3 touches only
  three named fields and preserves YAML key order, `git diff` will
  show only those keys changing. Revert with `git restore
  references/repos/<id>.md` if needed.

When in doubt, do not commit. The user can always re-run nightly-sync
after a manual cleanup; idempotency guarantees the second run will
either be a no-op or process whatever still needs processing.
