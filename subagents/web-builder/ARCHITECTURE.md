# ARCHITECTURE — `/web-builder`

> Output Fase B (Architecture Design) post-research. Non è il system prompt finale (vedi `web-builder.md`) — è il design document che spiega come l'agent è costruito e perché.

## Identità del subagent

`/web-builder` è un **subagent ARTIFACT-driven** del Pack v2 Learnn. L'output non è un report markdown né dati strutturati: è un **progetto web reale che gira**, scaffoldato da brief in linguaggio naturale, deploy-pronto, con CLAUDE.md preconfigurato.

**Audience**: Founder, Freelancer, Marketing manager, Entrepreneur non-tech che vogliono buildare landing/SaaS interno/dashboard senza developer team. Mente Learnn target: capisce la logica, non la sintassi (vibe coder).

**Promessa al primo run**: 8 domande discovery + 30 minuti = scaffold completo, deploy preview live, CLAUDE.md per continuare lo sviluppo.

**Posizione nel pack v2**: 3° subagent (validation pattern Tier 1), il più complesso (output = repo Git con app deployata, vs lead-finder-pro = CSV, competitor-deep-dive = markdown report, outbound-orchestrator = action chain).

## Architettura — overview

```
/web-builder (subagent)
│
├── Discovery flow (8 domande sequenziali)
│   └── salva in <memory>/config.md (memory: project)
│
├── MCP + CLI detection
│   └── verify_mcp(vercel|github|context7|playwright|apify|n8n-*)
│   └── shutil.which(vercel|gh|npx|git|node|convex)
│
├── Methodology principale (6 fasi)
│   ├── Phase 1: Discover (config in memory)
│   ├── Phase 2: Scaffold project (skill: project-scaffolder)
│   ├── Phase 3: CLAUDE.md + .claude/settings.json (skill: claude-md-generator)
│   ├── Phase 4: Auth + DB integration (skill: auth-database-setup)
│   ├── Phase 5: Components + routes (manual + shadcn-patterns reference)
│   ├── Phase 6: Deploy automation (skill: deploy-automation)
│   └── Phase 7 (cond Q7=Yes): n8n integration (skill: n8n-bridge)
│
├── Skills companion (5)
│   ├── project-scaffolder      — copia template + sostituisce placeholder
│   ├── claude-md-generator     — compila CLAUDE.md + .claude/settings.json
│   ├── auth-database-setup     — Clerk+Convex (default) o Supabase override
│   ├── deploy-automation       — Vercel MCP-first, CLI fallback
│   └── n8n-bridge (opzionale)  — webhook handler + n8n workflow template
│
├── References docs (8)
│   ├── stack-comparison-2026.md
│   ├── database-integration-2026.md
│   ├── auth-integration-2026.md
│   ├── deploy-vercel-2026.md
│   ├── claude-md-templates.md
│   ├── n8n-integration-2026.md
│   ├── deploy-check-rules.md
│   └── shadcn-patterns-2026.md
│
├── Scripts (6)
│   ├── discovery_check.py      — verifica/load config
│   ├── mcp_detect.py           — check MCP server availability
│   ├── cli_detect.sh           — bash check CLI installati
│   ├── scaffold_project.py     — wrapper template copy + placeholder substitution
│   ├── vercel_deploy.sh        — wrapper Vercel CLI con error handling
│   └── smoke_test.py           — post-deploy HTTP 200 + screenshot via Playwright
│
└── Templates starter (5: 3 completi + 2 stub)
    ├── nextjs-saas/            — Next 15 + Convex + Clerk + Stripe + shadcn dashboard
    ├── nextjs-landing/         — Next 15 + Tailwind + shadcn hero+pricing+CTA
    ├── astro-marketing/        — Astro + Tailwind v4 + Content Collections
    ├── next-internal-tool/     — STUB v1 (variant del nextjs-saas)
    └── expo-mobile/            — STUB v1 (placeholder + roadmap v2 in README)
```

## Discovery flow (dettaglio)

### Stato `<memory>/config.md`

Memory scope: `project` (DECISION-004) — config legata al working directory specifico. File path: `<project_root>/.claude/web-builder/config.md` (gestito automaticamente da Claude Code memory system).

### Sequenza domande

Vedi `discovery/questions.md` per testo completo. Sintesi:

| # | Question | Maps to | Conseguenza logica |
|---|---|---|---|
| Q1 | Tipo prodotto | `project.type` | Driver template + stack default Q3 |
| Q2 | Esperienza dev | `user.experience` | Driver verbosity output |
| Q3 | Tech stack | `stack.framework/database/auth` | Driver template-id + skip skill |
| Q4 | Dominio | `project.domain` | Driver Vercel domain config |
| Q5 | Auth | `stack.auth` | Driver skill `auth-database-setup` (Clerk vs WorkOS vs none) |
| Q6 | Database | `stack.database` | Driver skill `auth-database-setup` (Convex vs Supabase vs none) |
| Q7 | n8n | `integrations.n8n` | Driver skill `n8n-bridge` activation |
| Q8 | Deploy auto | `deploy.auto_deploy_main` | Driver skill `deploy-automation` 3-tier flow |

### Logica condizionale

- Q1 = `landing` → Q3 default proposto: Astro (DECISION-005)
- Q1 = `mobile` → Q3 ridotto a Expo stub o una piattaforma no-code (DECISION-008)
- Q3 = `Astro` → Q5 forced `none` o `custom` (Astro non integra Clerk nativo)
- Q3 = `no-code` → skip Q5, Q6 (no-code platform handles auth+DB)
- Q5 = `none` + Q6 = `none` → skip Q7

### Skip discovery

Se `<memory>/config.md` esiste e schema valido (`schema_version: 1`), salta discovery e mostra:

```
Trovo config /web-builder esistente: <project.name>, stack <framework+database+auth>.
Riprendiamo da: <config.build.last_step_completed>.
Comandi:
  - continue: prosegue da dove eravamo
  - reconfigure: ridiscute setup (sovrascrive config.md)
  - status: mostra stato build dettagliato
```

## MCP + CLI detection

### Detection logic (eseguita all'avvio post-discovery)

```python
# Pseudocode — vedi scripts/mcp_detect.py per impl reale
mcp_status = {}
for mcp_server in ["vercel", "github", "context7", "playwright", "apify", "n8n-default"]:
    mcp_status[mcp_server] = verify_mcp(mcp_server)  # via Claude Code MCP API

cli_status = {
    "vercel": shutil.which("vercel") is not None,
    "gh": shutil.which("gh") is not None,
    "npx": shutil.which("npx") is not None,
    "git": shutil.which("git") is not None,
    "node": shutil.which("node") is not None,
    "convex": shutil.which("convex") is not None,  # rare, usually via npx
}

# Save in config.md mcp_available + cli_available
```

### Mostra summary all'utente

```
🔍 Tool disponibili:
  ✅ Vercel MCP (uso questo per deploy automation)
  ✅ GitHub MCP
  ✅ context7 (per fetch docs runtime)
  ⚠️  playwright MCP (smoke test post-deploy useremo curl)
  ❌ Apify MCP (non serve per il tuo use case)

🛠️  CLI installati:
  ✅ vercel (v32+), gh, npx, git, node v20+
  ⚠️  convex CLI: useremo via npx (no install richiesto)

✅ Tutto pronto. Procedo con scaffold? [si/dettagli]
```

### Fallback chain (DECISION-007)

| Tool | Tier 1 (preferred) | Tier 2 | Tier 3 (last resort) |
|---|---|---|---|
| Vercel | MCP `https://mcp.vercel.com` (OAuth) | `vercel` CLI + `vercel login` | `VERCEL_TOKEN` env var |
| GitHub | GitHub MCP | `gh` CLI + `gh auth login` | `GITHUB_TOKEN` env var |
| Convex | (no MCP) | `npx convex dev` + `npx convex login` | manual env entry |
| Clerk | (no MCP) | Dashboard manual | n/a |

## Tech stack decision matrix

Da `tech-stack-2026` baseline + override permessi (DECISION-005, 006):

| Use case | Default | Override | Quando override |
|---|---|---|---|
| Landing/marketing | Next.js (baseline) | **Astro** | Performance/SEO critical, no auth/DB |
| SaaS micro | **Next + Convex + Clerk** ✅ | Supabase override | SQL legacy, RLS critical |
| Internal tool | **Next + Convex + Clerk** ✅ | — | Default sempre |
| Content/blog | Next + MDX | **Astro + Content Collections** | SEO/perf critical, no realtime |
| Mobile | Expo + Convex (stub v1) | una piattaforma no-code mobile-via-web | MVP rapido senza native |

**Anti-pattern**: scegliere stack non in `tech-stack-2026` senza warning esplicito (es. Vue/Nuxt/SvelteKit). Se utente lo richiede, flag "fuori da baseline Filippo" + procede comunque.

## Methodology principale (6 fasi sequenziali)

### Phase 1 — Discover

- Run discovery flow (8 Q) o load config esistente
- Save config.md
- Output user: summary stack + conferma "Procedo?"
- Checkpoint approval prima di Phase 2

### Phase 2 — Scaffold project

**Skill**: `project-scaffolder`

- Determine `template_id` da `config.project.type` + `config.stack.framework`
  - `saas_micro` + `nextjs_15` → `nextjs-saas`
  - `landing` + `astro` → `astro-marketing`
  - `landing` + `nextjs_15` → `nextjs-landing`
  - `internal_tool` + `nextjs_15` → `next-internal-tool` (stub) or fallback `nextjs-saas` semplificato
  - `mobile` + `expo` → `expo-mobile` (stub, mostra README v2 scope)
- Copia template da `scripts/templates/<template_id>/` a `<project_path>/` con sostituzione placeholder (`{{PROJECT_NAME}}`, `{{AUTHOR}}`, `{{DOMAIN}}`)
- Init git: `git init && git add . && git commit -m "Initial scaffold"`
- Output: `{path, files_created: [...], next_steps: [...]}`
- Checkpoint approval prima di Phase 3

### Phase 3 — CLAUDE.md + .claude/settings.json

**Skill**: `claude-md-generator`

- Compila `CLAUDE.md` da template (3 varianti: saas, landing, internal-tool) + sostituisce placeholder
- Sezioni standard: Project context, Stack, Common commands, Code style, Key files, Testing, Glossary, Anti-patterns, Gotchas (vuoto)
- Target: <200 righe (best practice 2026)
- Genera `.claude/settings.json` con `allowed-tools` sensati per il template
  - SaaS: Read, Write, Edit, Bash (git/npm/npx/vercel), Glob, Grep
  - Landing: idem - vercel
- Output: 2 file scritti
- Checkpoint approval prima di Phase 4

### Phase 4 — Auth + DB integration

**Skill**: `auth-database-setup`

- Branch su `config.stack.auth + config.stack.database`:
  - **Default Clerk + Convex**: install via `npm install @clerk/nextjs convex`, scaffold `app/ConvexClientProvider.tsx`, `middleware.ts` Clerk, `convex/schema.ts` example, `.env.local.example` con `CLERK_*` + `NEXT_PUBLIC_CONVEX_URL`
  - **Supabase override**: install `@supabase/supabase-js + @supabase/ssr`, scaffold `lib/supabase/{client,server}.ts`, RLS policy template, `.env.local.example`
  - **WorkOS enterprise**: install AuthKit, scaffold AuthKit middleware + callback route
  - **None**: skip
- Genera 1 protected route example (`app/(dashboard)/dashboard/page.tsx`) per validation utente
- Output: lista file scritti + `env_vars_required: [...]`
- Checkpoint: prompt utente per env vars (Clerk keys da dashboard, Convex già auto via `npx convex dev`)

### Phase 5 — Components + routes

- Lista shadcn components inizializzati (riferimento `references/shadcn-patterns-2026.md`):
  - Default sempre: button, card, input, form, dialog, sheet, dropdown-menu, toast
  - SaaS aggiungi: data-table, command-palette, sidebar, mode-toggle, skeleton
  - Landing aggiungi: hero, pricing-card, cta-section
- Run `npx shadcn@latest init` (se non già in template)
- Run `npx shadcn@latest add <list>` batch
- Genera 1-3 page example basate su use case (es. SaaS: `/dashboard`, `/settings`, `/billing`)
- Checkpoint approval prima di Phase 6

### Phase 6 — Deploy automation

**Skill**: `deploy-automation`

- Branch su `config.deploy.auto_deploy_main`:
  - **Yes auto**: 3-tier detection (DECISION-007):
    - Tier 1: Vercel MCP available → use MCP `create_project`, `set_env_vars`, `deploy`
    - Tier 2: `vercel` CLI installed → `vercel login` + `vercel link` + `vercel env add` per ogni env + `vercel deploy --preview`
    - Tier 3: `VERCEL_TOKEN` env var → CLI con `--token`
  - **No manual**: skip, genera `vercel.json` + istruzioni README
  - **Already configured**: ask `vercel project ID`, link config
- Push a GitHub (via GitHub MCP o `gh` CLI)
- Smoke test post-deploy preview URL: HTTP 200 + screenshot homepage (skill `smoke_test.py`)
- Output: `{deploy_url_preview, status, smoke_results}` + comando promote a prod
- Checkpoint approval prima di promote a prod

### Phase 7 (conditional) — n8n integration

**Skill**: `n8n-bridge` (attivata solo se Q7=Sì)

- Genera `app/api/webhook/[event]/route.ts` con HMAC verify scaffold
- Genera `n8n-workflows/<event>.json` template (Webhook trigger + Code node HMAC verify + Set node example)
- Aggiungi env var `N8N_WEBHOOK_SECRET` a `.env.local.example`
- Document in `CLAUDE.md` sezione "Integrazioni"

## Skills companion — contracts

### 1. `project-scaffolder/SKILL.md` (~220 righe)

- **Cosa fa**: copia template starter + sostituisce placeholder
- **Input**: `{template_id, project_name, project_path, options: {auth, database, payments}}`
- **Output**: `{path, files_created: [...], next_steps: [...]}`
- **References**: `references/stack-comparison-2026.md`, `scripts/templates/<template_id>/`
- **Activation**: Phase 2 methodology
- **Tools used**: Bash (cp -r, git init), Read (template files), Write (substituted output)

### 2. `claude-md-generator/SKILL.md` (~180 righe)

- **Cosa fa**: compila CLAUDE.md preconfigurato + .claude/settings.json
- **Input**: `{discovery_answers, stack_config, project_name, project_path}`
- **Output**: `{claude_md_path, settings_json_path, sections_included: [...]}`
- **References**: `references/claude-md-templates.md`, `<pack-root>/skills/CLAUDE_starter_template.md`
- **Activation**: Phase 3 methodology
- **Tools used**: Read (template), Write (output)

### 3. `auth-database-setup/SKILL.md` (~250 righe)

- **Cosa fa**: integra auth + DB nel progetto scaffoldato
- **Input**: `{auth_provider, db_provider, project_path}`
- **Output**: `{files_written: [...], env_vars_required: [...], checkpoint: "set env vars then continue"}`
- **References**: `references/auth-integration-2026.md`, `references/database-integration-2026.md`
- **Activation**: Phase 4 methodology
- **Tools used**: Bash (npm install), Write (config files)

### 4. `deploy-automation/SKILL.md` (~280 righe)

- **Cosa fa**: orchestrazione deploy Vercel via MCP/CLI/token (3-tier)
- **Input**: `{project_path, vercel_method: 'mcp'|'cli'|'token', env_vars: {...}, prod: bool}`
- **Output**: `{deploy_url, status, smoke_test_results, rollback_command}`
- **References**: `references/deploy-vercel-2026.md`, `references/deploy-check-rules.md`
- **Activation**: Phase 6 methodology
- **Tools used**: Bash (vercel CLI), MCP (vercel server)

### 5. `n8n-bridge/SKILL.md` (~180 righe, opzionale)

- **Cosa fa**: webhook handler Next.js + n8n workflow template
- **Input**: `{event_name, webhook_secret_strategy: 'hmac'|'api_key', direction: 'in'|'out'|'both', project_path}`
- **Output**: `{route_handler_path, workflow_template_path, env_vars_added: [...]}`
- **References**: `references/n8n-integration-2026.md`
- **Activation**: Phase 7 methodology (conditional Q7=Yes)
- **Tools used**: Write (route handler + JSON workflow)

## Config schema (`<memory>/config.md`)

```yaml
---
agent: web-builder
created: 2026-MM-DD
last_updated: 2026-MM-DD
schema_version: 1
---

# Identità progetto
project:
  name: "my-saas"                    # da Q discovery preliminare
  path: "~/Dev/projects/my-saas"
  type: saas_micro                    # landing | saas_micro | internal_tool | content | mobile
  domain: "my-saas.com"               # optional, da Q4

# Esperienza utente
user:
  experience: vibe_coder              # zero | vibe_coder | junior | senior
  language_preference: it             # always it for Learnn audience

# Tech stack
stack:
  framework: nextjs_15                # nextjs_15 | astro | sveltekit | expo | no-code
  database: convex                    # convex | supabase | none | sanity
  auth: clerk                         # clerk | workos | supabase_auth | none | custom
  styling: tailwind_v4                # always
  ui_library: shadcn                  # always (eccetto no-code platform)
  payments: stripe                    # stripe | autumn | none
  deploy: vercel                      # vercel | netlify | cloudflare | railway

# Integrations
integrations:
  n8n: true                           # webhook in/out enabled
  ai_sdk: false                       # Vercel AI SDK
  composio: false                     # AI agent tool integration

# Deploy config
deploy:
  vercel_project_id: "prj_xxx"        # populated after vercel link
  github_repo: "username/my-saas"
  auto_deploy_main: true
  preview_deploys: true
  domain_configured: false            # set true after vercel domain add

# MCP availability (auto-detected)
mcp_available:
  vercel: true
  github: false
  context7: true
  playwright: true
  apify: false

cli_available:
  vercel: true
  gh: true
  npx: true
  git: true
  node: true
  convex: false                       # ok, useremo via npx

# Build state
build:
  last_step_completed: "phase_3_claude_md"  # phase_1...phase_7
  scaffold_done: true
  claude_md_done: true
  auth_db_done: false
  deploy_done: false
  smoke_test_passed: false

# Reconfigure trace (opzionale)
previous_config:
  - {timestamp: "2026-04-30T10:00", changed_field: "stack.database", old: "supabase", new: "convex"}
```

## Edge cases (handling esplicito in system prompt)

| Edge case | Detection | Handling |
|---|---|---|
| Cartella esistente con file | `os.listdir(project_path)` non vuoto | Prompt: "Trovo file esistenti, vuoi mergiare/abortire/backup?" — NO overwrite silenzioso |
| Node version mismatch (<20) | `node --version` parsing | Suggest `nvm install 20` con warning. Skip se senior |
| `npm install` fail | `npm install` exit !=0 | Mostra log, suggest `--legacy-peer-deps`, retry o abort |
| Vercel deploy fail | log Vercel `error` | Parse error log, identifica: env mancante / build fail / quota. Prompt fix |
| Env vars missing | grep `process.env.X` not in `.env.local` | Lista vars mancanti, prompt utente con hint per ognuna |
| GitHub repo name conflict | `gh repo view` 200 ok | Suggest variant name (-2, -app) o ask override |
| Clerk dashboard manual setup | no API per create app | Open URL `https://dashboard.clerk.com/sign-up`, instructions copy/paste keys |
| Convex deployment partial | `convex.json` esiste ma deployment id mancante | Run `npx convex dev` re-init |

## Output format & file conventions

- Naming progetto: `kebab-case` (es. `my-saas`, `lead-finder-app`)
- Struttura cartelle: vedi template starter
- Env vars: `NEXT_PUBLIC_<X>` per client-exposed, `<X>` per server-only
- Git initial commit: `"Initial scaffold via /web-builder — <stack>"`
- File NON committati di default: `.env.local`, `.env.*.local`, `node_modules/`, `.next/`, `.vercel/`, `*.log`, `.DS_Store`

## Tool usage rules

- **Vercel**: MCP-first (DECISION-007), CLI fallback, token last resort
- **GitHub**: MCP first se disponibile, `gh` CLI fallback
- **context7**: usa per fetch docs aggiornati Next/Convex/Clerk runtime quando dubbio versione
- **playwright**: solo per smoke test post-deploy (HTTP 200 + screenshot home)
- **`npx`**: sempre con `--yes` flag in non-interactive (esempio: `npx --yes shadcn@latest add button`)
- **Bash destructive ops**: NO `rm -rf` senza esplicita autorizzazione utente, NO `git push --force`, NO `git reset --hard`

## Anti-patterns critici (system prompt sez 10)

1. Mai overwrite CLAUDE.md esistente senza chiedere
2. Mai commit secrets (`.env*` sempre in `.gitignore`)
3. Mai deploy senza user approval (checkpoint Phase 6)
4. Mai scegliere stack non in `tech-stack-2026` senza warning esplicito
5. Mai generare 1000 file boilerplate inutili (template min, lazy add)
6. Mai hardcoded credentials in file generati (sempre `process.env.X`)
7. Mai usare `git add -A` (solo file specifici)
8. Mai assumere Node version (check before)

## Output Fase B — checklist

- ✅ `discovery/questions.md` (8 domande finalizzate, ~210 righe)
- ✅ `ARCHITECTURE.md` (questo file, ~360 righe)
- ✅ Skill contracts per 5 skill (sezione sopra)
- ✅ Config schema YAML completo (sezione sopra)
- ✅ Methodology 6+1 fasi documentate (sezione sopra)
- ✅ MCP+CLI detection logic
- ✅ Edge cases identificati (8)
- ✅ Output conventions

**Prossimo step**: Fase C build — scrivere `web-builder.md` (350-500 righe), 5 skill SKILL.md, 8 references docs, 6 scripts, 5 templates starter, README.md.
