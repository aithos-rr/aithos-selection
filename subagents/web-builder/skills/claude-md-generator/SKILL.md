---
name: claude-md-generator
description: Genera CLAUDE.md preconfigurato e .claude/settings.json per un progetto web scaffoldato. Sceglie il template (saas / landing / internal-tool) basato sulla discovery, riempie sezioni standard (Project context, Stack, Common commands, Code style, Key files, Testing, Glossary, Anti-patterns, Gotchas) con i valori reali. Target <200 righe (best practice 2026). Usa progressive disclosure via @import per docs lunghe. Da usare in Phase 3 della methodology /web-builder.
when_to_use: Phase 3 di /web-builder, generazione CLAUDE.md per nuovo progetto, configurazione .claude/settings.json con allowed-tools sensati per stack
---

# CLAUDE.md Generator

Skill di Phase 3 della methodology `/web-builder`. Prende la config discovery + stack scelto, e produce due file critici: `CLAUDE.md` (contesto progetto) e `.claude/settings.json` (configurazione tecnica).

## When to use

Attiva quando:
- Phase 2 (scaffold) completata (`config.build.scaffold_done == true`)
- `config.build.claude_md_done == false`
- Progetto scaffoldato esiste in `config.project.path`

## Input contract

```yaml
discovery_answers:
  q1: saas_micro | landing | internal_tool | content | mobile
  q2: zero | vibe_coder | junior | senior
  q3: nextjs_15 | astro | sveltekit | expo | no-code
  # ... q4-q8
stack_config:
  framework: nextjs_15
  database: convex
  auth: clerk
  styling: tailwind_v4
  ui_library: shadcn
  payments: stripe | autumn | none
  deploy: vercel
project_name: my-saas
project_path: /path/to/project
existing_claude_md: false  # se true, backup + merge mode
```

## Output contract

```yaml
status: success | merged | failed
claude_md_path: /path/to/project/CLAUDE.md
claude_md_lines: 165          # target <200
settings_json_path: /path/to/project/.claude/settings.json
sections_included:
  - "Project context"
  - "Stack"
  - "Common commands"
  - "Code style"
  - "Key files"
  - "Testing"
  - "Glossary"
  - "Anti-patterns"
  - "Gotchas (placeholder)"
allowed_tools_settings:
  - "Read", "Write", "Edit", "Bash(git:*)", "Bash(npm:*)", "Bash(npx:*)", "Bash(vercel:*)"
backup_created: false  # true se existing_claude_md era true
```

## Workflow

### Step 1 — Determine template variant

| `discovery_answers.q1` | Template variant | File source |
|---|---|---|
| `saas_micro` | `saas-template.md` | `references/claude-md-templates.md` sez SaaS |
| `landing` | `landing-template.md` | sez Landing |
| `internal_tool` | `internal-tool-template.md` | sez Internal Tool |
| `content` | `landing-template.md` (variant) | sez Landing |
| `mobile` | `saas-template.md` (variant Expo) | sez SaaS con Expo notes |

### Step 2 — Check existing CLAUDE.md

Se `<project_path>/CLAUDE.md` esiste:

1. Backup: `cp CLAUDE.md CLAUDE.md.bak`
2. Switch to merge mode: leggi sezioni esistenti, mantieni custom content (specifico utente), inserisci sezioni standard mancanti
3. Output user: "Trovato CLAUDE.md esistente. Backup in `CLAUDE.md.bak`. Merge sezioni standard? [Sì/Solo backup, fai tu]"

Se non esiste: skip backup, write fresh.

### Step 3 — Compila template

Sostituisce placeholder nel template variant:

| Placeholder | Source |
|---|---|
| `{{PROJECT_NAME}}` | `project_name` |
| `{{PROJECT_DESCRIPTION}}` | derivato da Q1 + Q3 (es. "SaaS micro per gestione clienti freelance") |
| `{{STACK_LIST}}` | rendered da `stack_config` (es. "Next.js 15 + Convex + Clerk + Stripe + Vercel") |
| `{{COMMON_COMMANDS}}` | comandi specifici stack (es. `npm run dev`, `npx convex dev`, `vercel deploy`) |
| `{{KEY_FILES}}` | file architetturali (es. "Auth middleware: `middleware.ts`. Convex schema: `convex/schema.ts`. Stripe webhook: `app/api/webhook/stripe/route.ts`") |

### Step 4 — Best practices applicate

- **Target lunghezza**: <200 righe (best practice 2026)
- **Progressive disclosure**: per docs lunghe (architettura, SOPs), usa `@references/<file>.md` import sintassi
- **Sezioni minime obbligatorie** (9):
  1. Project context (3-5 righe)
  2. Stack (5-10 righe, lista stack tools)
  3. Common bash commands (5-10 righe)
  4. Code style (3-5 righe)
  5. Key files / architectural patterns (5-10 righe)
  6. Testing (3-5 righe)
  7. Glossary business terms (5-10 righe, se domain-specific)
  8. Anti-patterns (3-5 righe)
  9. Gotchas placeholder (vuoto, da popolare during dev)

### Step 5 — Write CLAUDE.md

```markdown
# {{PROJECT_NAME}}

## Project context

{{PROJECT_DESCRIPTION}}

Audience: <derivato Q1+Q5>
Problem solved: <derivato narrativa Q1>

## Stack

{{STACK_LIST}}

Per dettaglio integrations: vedi `@docs/architecture.md` (se esiste)

## Common commands

```bash
npm run dev              # Start dev server
npm run build            # Production build
npm run lint             # ESLint check
{{convex_commands}}      # if convex
{{vercel_commands}}      # if vercel
```

## Code style

- TypeScript strict mode
- ES modules (no CommonJS)
- Functional components + hooks (no class)
- Tailwind utility classes (no CSS modules, no styled-components)
{{additional_style_rules}}

## Key files

- `app/layout.tsx` — Root layout, providers ({{provider_chain}})
- `middleware.ts` — Auth route protection (if Clerk)
- `convex/schema.ts` — Database schema (if Convex)
- `lib/utils.ts` — `cn()` helper for shadcn
{{key_files_specific_template}}

## Testing

- Component tests: `npm test` (Vitest)
- E2E: `npm run e2e` (Playwright, se aggiunto)
- Type check: `npm run type-check`

## Glossary business terms

{{glossary_optional}}

## Anti-patterns

- No SQL diretto (use Convex queries)
- No `git add -A` (rischio commit secrets)
- No env vars in `NEXT_PUBLIC_*` per secrets
{{anti_patterns_specific}}

## Gotchas

(Vuoto. Popolare during dev quando incontri sorprese.)
```

### Step 6 — Write .claude/settings.json

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "Bash(git:*)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "{{deploy_specific}}"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)"
    ]
  },
  "env": {}
}
```

`deploy_specific`:
- Vercel: `"Bash(vercel:*)"`
- GitHub: `"Bash(gh:*)"`

### Step 7 — Output user

```
✅ CLAUDE.md generato (<N> righe — target <200 ✅)

📋 Sezioni incluse:
  - Project context
  - Stack ({{stack_summary}})
  - Common commands ({{N_commands}})
  - Code style
  - Key files ({{N_files}} files referenced)
  - Testing
  - {{Glossary if present}}
  - Anti-patterns
  - Gotchas (vuoto, popolato durante dev)

⚙️  .claude/settings.json generato con allowed-tools per <stack>

Procedo con auth + database? [Sì/No]
```

## Best practices CLAUDE.md 2026

- **Conciseness > completeness**: 60-200 righe target. Max 300 prima che Claude perda signal
- **Progressive disclosure**: usa `@path/to/file.md` per import recursive (5 livelli max)
- **`.claude/rules/*.md`**: auto-loaded con stessa priorità — best per coding rules team-wide
- **Information hierarchy**: sezioni scannable, Claude estrae senza leggere tutto
- **Glossary domain-specific**: solo se rilevante (es. SaaS B2B con termini "lead", "deal", "pipeline")

## Edge cases

### Existing CLAUDE.md custom

```
⚠️  Trovo CLAUDE.md esistente con <N> righe.

Sezioni rilevate:
  - Project context (custom)
  - Stack (custom)
  - + 3 sezioni mancanti standard

Cosa fare?
1. Backup + merge sezioni mancanti (raccomandato)
2. Solo backup, gestisci manualmente
3. Sovrascrivi (perdi contenuto custom)

Scegli [1/2/3]:
```

### Project name con caratteri speciali

Se `project_name` contiene caratteri non kebab-case (es. spaces, uppercase): warn + suggest convert via `to-kebab-case` lib o ask utente conferma name.

### no-code platform-only mode

Per Q3=no-code platform: CLAUDE.md ha sezioni custom:
- Stack: "no-code platform (frontend) + n8n (backend) + Vercel (deploy)"
- Common commands: vuoti, sostituiti da "Vai su no-code.dev per editing"
- Key files: `backend/n8n-workflows/*.json`, `docs/no-code-prompt.md`

## Examples

### Esempio A — SaaS micro

```yaml
Input:
  q1: saas_micro
  stack: {framework: nextjs_15, database: convex, auth: clerk, payments: stripe, deploy: vercel}
  project_name: freelance-crm

Output:
  CLAUDE.md (~150 righe):
    - Project context: "SaaS micro per gestione clienti freelance"
    - Stack: Next.js 15 + Convex + Clerk + Stripe + Tailwind v4 + shadcn + Vercel
    - Common commands: npm run dev, npx convex dev, vercel deploy
    - Key files: middleware.ts, convex/schema.ts, app/api/webhook/stripe/route.ts
```

### Esempio B — Landing Astro

```yaml
Input:
  q1: landing
  stack: {framework: astro, database: none, auth: none, deploy: vercel}
  project_name: ai-mastery-2026

Output:
  CLAUDE.md (~80 righe):
    - Project context: "Landing page per corso AI Mastery 2026"
    - Stack: Astro + Tailwind v4 + Content Collections + Vercel
    - Common commands: npm run dev (port 4321), npm run build, vercel deploy
    - Key files: src/pages/index.astro, src/content/config.ts
```

## References

- `references/claude-md-templates.md` — 3 template variant (saas, landing, internal-tool)
- `<pack-root>/skills/CLAUDE_starter_template.md` — Filippo's CLAUDE.md starter (reuse pattern)
- Anthropic [Claude Code best practices](https://code.claude.com/docs/en/best-practices)

## Crediti

Skill creata per `/web-builder` (Pack v2 Learnn). Pattern derivato da Anthropic CLAUDE.md best practices 2026 + Filippo's `CLAUDE_starter_template.md`.
