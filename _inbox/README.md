# Inbox

This folder is the quick-dump zone for content that has not yet been
classified. Drop new prompts, drafts, screenshots of agent transcripts,
half-formed ideas, or anything else here without worrying about which folder
it should ultimately live in.

## Tracking policy

- The folder itself is tracked (via this `README.md` and a `.gitkeep`).
- The folder's **contents are gitignored**. See `.gitignore` for the rules.
- The `librarian` skill (Phase 2) reads this folder, proposes destinations
  and metadata, and moves items into the right place under your supervision.

## How to use

1. Dump material here freely. Filenames can be ugly. Metadata is optional.
2. Run the `librarian` skill from a Claude Code session in this repo when
   you want to process the backlog.
3. Approve, edit, or reject each proposal as the librarian walks you
   through the inbox.

## Not for long-term storage

If you find yourself avoiding triage and leaving things in `_inbox/`
indefinitely, that is a signal to run the librarian. The inbox is a buffer,
not a folder.
