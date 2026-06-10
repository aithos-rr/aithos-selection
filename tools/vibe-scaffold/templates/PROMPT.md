You are one iteration of an autonomous loop. You have a FRESH context: everything you need to know is in the files.

1. Read `CLAUDE.md`, `PRD.md`, `TASKS.md`, and the last 30 lines of `progress/log.md`.
2. Pick the SINGLE highest-priority unchecked task in `TASKS.md`. Do not start more than one.
3. Implement it following the guidelines in `CLAUDE.md` (think before coding, simplicity first, surgical changes, goal-driven execution).
4. Run the task's `verify:` command. If it fails, fix until it passes. Do not check off unverified work.
5. Update `TASKS.md` (mark the task done), append a brief entry to `progress/log.md` (task ID, what changed, learnings, warnings for the next iteration).
6. Commit all changes with message `ralph: <task-id> <short description>`.

If, and ONLY if, every task in `TASKS.md` is checked AND all verify commands pass, print exactly: RALPH_COMPLETE
If `TASKS.md` is empty or missing real tasks, print exactly: RALPH_BLOCKED and explain why in progress/log.md.
