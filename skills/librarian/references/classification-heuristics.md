# Classification heuristics

Concrete, ordered rules the librarian uses to assign an inbox item to one
of the categories defined in `SKILL.md` section 3. Apply the rules in
order and stop at the first match; the tie-breaking rule at the end
handles ambiguity.

## 1. File-content rules

Apply these before looking at the filename or extension when the file's
content is unambiguous.

- **Workflow manifest.** A YAML file that contains both a top-level
  `system_prompt:` field and a top-level `agents:` list → likely
  `workflow` manifest (the file belongs inside a folder under
  `workflows/`).
- **Agent manifest.** A YAML file that contains a top-level
  `system_prompt:` field but **no** `agents:` list → likely `agent`
  manifest (the file belongs inside a folder under `agents/`).
- **MCP server config.** A `.json` file whose top level contains an
  `mcpServers` key, or whose shape matches the native MCP server
  configuration schema (a `command`, `args`, and optional `env`) →
  `mcp-config`.
- **Markdown with frontmatter.** A `.md` file that begins with a
  `---` frontmatter block → categorise by the frontmatter's `type:`
  field:
  - `type: prompt` → `prompt`
  - `type: template` → `template`
  - `type: stack-note` → `stack-note`
  - `type: skill` → `skill` (also requires a `SKILL.md` filename when
    inside a folder)
- **Subagent frontmatter.** A `.md` file whose frontmatter contains
  `name` and `description` *and* at least one of `tools`,
  `mcpServers`, or `skills` → `subagent`. The filename is typically
  `<name>.md` (not `SKILL.md`), and the file is the entrypoint of a
  bundle described in §3.
- **Markdown without frontmatter, playbook-style.** A `.md` file with
  **no** frontmatter whose body opens with phrasing such as
  "How I use X", "Setting up X", "My X workflow", "Notes on X" → treat as
  `stack-note`. Propose a kebab-case tool name as the destination stem.
- **Markdown without frontmatter, LLM instruction.** A `.md` file with
  **no** frontmatter whose body is an instruction directed at an LLM —
  e.g. starts with "You are…", "When the user…", "Respond with…", "Your
  task is…" → treat as `prompt`. If the body contains `{{...}}`
  placeholders, treat it as `template` instead.

## 2. Filename and extension rules

When the content rules above are inconclusive, fall back to extension and
location signals.

- **`.py` file directly in `_inbox/`** → `tool-script`. The destination is
  `tools/<name>.py`.
- **`.json` file** without an MCP shape → `n8n-workflow` if the JSON looks
  like an n8n export (top-level `nodes` array and `connections` object);
  otherwise classify as `unknown` and flag for the user.
- **`.yaml` or `.yml` file** that does not match the agent or workflow
  manifest rules above → `unknown`. Manifest-shaped YAML that is not in a
  composite folder is suspicious; ask the user.
- **`.md` file** that did not match any content rule → `unknown`.

## 3. Folder rules

A subfolder inside `_inbox/` is treated as a single bundled candidate.

- The folder contains `agent.md` → classify as `agent`. Required sibling
  files at the destination: `agent.md`, `manifest.yaml`, `README.md`. If
  any are missing in the inbox folder, propose stubbed versions in the
  plan and let the user accept or reject the stubs.
- The folder contains `flow.md` → classify as `workflow`. Required sibling
  files at the destination: `flow.md`, `manifest.yaml`, `README.md`. Same
  stub rule as above.
- The folder contains `SKILL.md` → classify as `skill`. Destination is
  `skills/<name>/`. Anthropic skill frontmatter is required at the top of
  `SKILL.md`; if missing, generate it from the folder name and the body's
  opening paragraph.
- The folder contains a single `<name>.md` (matching the folder name)
  whose frontmatter declares at least one of `tools`, `mcpServers`, or
  `skills`, and **no** `SKILL.md` or `agent.md` is present → classify as
  `subagent`. Destination is `subagents/<name>/`. Generate the
  Aithos-side `manifest.yaml` from the entrypoint frontmatter (see
  `references/manifest-examples.md`). Supporting files that often
  accompany a subagent bundle and may be present without changing the
  classification: `BUILD-BRIEF.md`, `ARCHITECTURE.md`, `PROGRESS.md`,
  `README.md`, `references/`, `discovery/`, `research/`,
  `test-fixtures/`.
- The folder looks like an n8n workflow bundle (a `flow.json` plus a
  `README.md`, no `agent.md` and no `flow.md`) → classify as
  `n8n-workflow`. Destination is `n8n-workflows/<name>/`.
- Otherwise → `unknown`. Do not move the folder; surface its contents in
  the plan and ask the user how to categorise it.

## 4. Identifier derivation

Once a category is chosen, derive the destination `id` / `name`:

1. Start from the source filename or folder name.
2. Lowercase it; replace whitespace and underscores with single hyphens;
   strip any disallowed characters; collapse consecutive hyphens.
3. Verify the result matches `^[a-z0-9]+(-[a-z0-9]+)*$` (the pattern from
   `/docs/naming-conventions.md`).
4. If a different existing item already uses that identifier, append a
   `-v2` (or higher) suffix and surface the rename in the plan so the user
   can confirm.

## 5. Ambiguity and tie-breaking

When more than one rule above matches:

- **Prefer the more specific category.** `template` beats `prompt` when
  placeholders are present. `mcp-config` beats `unknown` for a `.json`
  with `mcpServers`. `workflow` beats `agent` when both `system_prompt:`
  and `agents:` are present.
- **Surface the alternatives in the plan.** Always list the runner-up
  category alongside the proposed one so the user can override before
  applying.
- **Default to caution.** If specificity does not break the tie, classify
  as `unknown` rather than guessing. The cost of leaving a file in the
  inbox is small; the cost of misfiling it (and creating duplication or a
  broken manifest reference) is high.

## 6. Nothing matches

If no rule matches at all, classify as `unknown`. Keep the file in
`_inbox/`, include it in the plan with a short explanation of why it is
ambiguous, and ask the user to provide a category before the next inbox
processing run.

## 7. URL pattern rules — `process-reference`

These rules apply to the `process-reference` sub-flow in `SKILL.md`
section 4. They classify a URL into one of the three reference
subtypes (`repo`, `article`, `template`) before any metadata fetch.
Apply in order; stop at the first match.

- **`repo`.** The URL matches
  `^https?://github\.com/<owner>/<repo>/?$` with no further path
  segments. The path may end with a trailing slash but must not contain
  `/issues`, `/pulls`, `/blob/…`, `/tree/…`, or other deep paths.
  Destination: `references/repos/<owner>-<repo>.md`.
- **`template`.** The URL matches any of the following template-hosting
  patterns:
  - `^https?://n8n\.io/workflows/…` — an n8n workflow template page.
  - `^https?://gist\.github\.com/…` — *only when* the gist body is
    visibly a skill/agent/workflow template (frontmatter present,
    `{{variables}}` present, or filename ends in `SKILL.md` /
    `manifest.yaml`). Otherwise treat the gist as `article`.
  - Other URLs the user explicitly flags as a template
    (e.g. "this is a template" alongside the link).
  Destination: `references/templates/<slug>.md`.
- **`article`.** Anything else with a valid `http://` or `https://`
  scheme. Destination: `references/articles/<slug>.md`.

The `<slug>` for `article` and `template` is a kebab-case slug of the
fetched HTML `<title>` (lowercased, punctuation stripped, capped at
roughly 50 characters). If the title cannot be fetched, fall back to
the last meaningful path segment of the URL.

When the same destination identifier already exists, append a `-v2`
(or higher) suffix and surface the collision in the plan. Never
overwrite an existing reference file.

Anything that is not a well-formed `http(s)://` URL is dropped from
the plan and reported in the closing summary; it never becomes a
reference file.
