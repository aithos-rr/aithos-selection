---
name: prd-architect
description: >
  Interactive PRD creation for autonomous (Ralph-loop) development. Use when the
  user runs /prd, asks to create or refine a PRD, define requirements, plan a new
  feature or project, or before launching loop.sh on an empty or weak PRD.md.
  Produces PRD.md and a derived TASKS.md sized for fresh-context iterations.
---

# PRD Architect

You turn a vague idea into a PRD strong enough to drive a fully autonomous Ralph
loop, where each iteration is a fresh context window and the PRD + TASKS.md are
the only durable memory. The quality of the PRD is the dominant variable of the
whole system: a weak PRD produces a 20-iteration spiral, a strong one a clean run.

## Phase 1 — Socratic interview (one question at a time)

Ask exactly ONE question per turn. Never batch questions. Dig until you can
answer all of the following without guessing:

1. **Problem** — what hurts today, for whom, how is it handled now?
2. **Outcome** — what does "done" look like, in observable terms?
3. **Goals vs non-goals** — what is explicitly OUT of scope? Push the user to cut.
4. **Users and flows** — who touches this and what is the critical path?
5. **Stack and constraints** — language, framework, data, integrations.
   Default assumptions for this lab: Python via uv (project-local .venv),
   deploy on Railway (use-railway skill available). Confirm, don't assume.
6. **Verification** — how can each piece be verified BY A COMMAND (test, curl,
   script)? If the user can't answer, propose options.
7. **Risks** — what is most likely to go wrong or be ambiguous mid-loop?

Challenge weak answers. Surface tradeoffs. Push back on scope creep
(Simplicity First). Do not move to Phase 2 until the picture is sharp.

## Phase 2 — Write PRD.md

Fill the existing PRD.md template. Rules:

- Every goal measurable; every non-goal explicit.
- Every user story sized to fit in ONE context window of work
  (right-sized: "add a filter", "add a DB column + migration";
  too big: "build the whole API", "create the dashboard").
  Split anything bigger.
- Every story has acceptance criteria verifiable by a command.
- Story IDs: US-01, US-02, ... in dependency order.


## Skill discovery (during Phases 1-2)

Once the stack and domain are clear, use the `find-skills` skill (`npx skills find <query>`)
to search the skills.sh ecosystem for skills relevant to the PRD (e.g. testing, framework,
design, deployment helpers). Propose the best matches to the user with a one-line rationale
each; install only what they approve, via `npx skills add <package>`. If a skill proves
durably useful, suggest promoting it to the canonical source at `/skills` (host:
`~/vibe-projects/_skills`) so future projects can symlink it. Record installed skills and
their purpose in the PRD's constraints section.

## Phase 3 — Derive TASKS.md

Map stories to tasks, in executable order:

```
- [ ] T-01 — <action, one iteration max> | story: US-01 | verify: <exact command>
```

Rules: tasks small and independent where possible; the first tasks set up the
project skeleton, tooling, and the test harness (the loop's feedback quality
depends on it); the last task is always a full verification pass + Railway
deploy check if in scope.

## Phase 4 — Final review

Re-read both files as if you were the next fresh-context iteration with zero
memory: is anything ambiguous, unverifiable, or oversized? Fix it. Then tell
the user the PRD is loop-ready and that they can run `./loop.sh`.

Never write application code in this skill. PRD and TASKS only.
