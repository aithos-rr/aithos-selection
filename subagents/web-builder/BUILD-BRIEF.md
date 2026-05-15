# BUILD-BRIEF — `/web-builder`

> **Per la worker chat**: leggi questo file all'inizio. Tutto il contesto necessario per buildare l'agent è qui. Non serve leggere conversazioni precedenti.
>
> **Quick start**: leggi BUILD-BRIEF -> leggi PROGRESS.md (se esiste) -> leggi DECISIONS.md (4 decisioni iniziali gia scritte) -> esegui Fase A -> B -> C -> D -> E.
> Aggiorna PROGRESS.md ad ogni milestone (almeno ogni 25% context fill).

## Identita del subagent

- **Nome**: `/web-builder`
- **Cosa fa (1 frase)**: Da brief utente in linguaggio naturale a progetto web production-grade scaffoldato (Next.js 15 + Convex + Clerk + shadcn + Vercel) con CLAUDE.md preconfigurato, componenti base, auth, database, deploy automation — tutto in un comando, audience non-developer.
- **Per chi**: Founder, Freelancer, Marketing manager, Entrepreneur non-tech che vogliono buildare landing/SaaS interno/dashboard senza developer team
- **Use case slide W2**: "Costruire intere applicazioni, siti web o landing page" (#8 dei 8 use case)
- **Skill v1 base da riusare come spunto**:
  - `<pack-root>/skills/webinar-3/vibe-start/SKILL.md` (236 righe — pattern discovery + scaffold)
  - `<pack-root>/skills/webinar-3/deploy-check/SKILL.md` (165 righe — pattern pre-deploy gating)
  - `~/.claude/skills/tech-stack-2026/SKILL.md` (skill globale di Filippo — tech stack di riferimento, **baseline da onorare**)
- **Tier**: 🥇 (validation pattern del subagent #3, il piu complesso del pack v2)
- **Tempo stimato**: 1.5 giorni research + 8-10 ore build = ~14-16 ore totali

## Vincoli di livello "spaventoso" (specifici per questo agent)

Questo agent e **ARTIFACT-driven**: il suo output non e un report ne dati, e un **progetto reale che gira e si deploya**. Vincoli minimi:

- System prompt **350-500 righe** (denso, con methodology stack-specific)
- **4-5 skills companion** in `skills/`
- **6+ references docs** (stack guide, CLAUDE.md template, deploy automation, integrations)
- **5+ template starter** in `scripts/templates/` (uno per stack: nextjs-saas, nextjs-landing, astro-marketing, next-internal-tool, expo-mobile)
- **Discovery interattiva** al first run (6-8 domande mirate per stack/scope)
- **MCP detection automatica** + fallback (Vercel MCP, GitHub MCP, Convex non ha MCP nativo -> CLI fallback)
- **Memory persistente** via `memory: project` (config legata al progetto web specifico)
- **Almeno 3 esempi reali end-to-end** documentati nel README utente (landing, SaaS micro, internal tool)
- **Italiano** per messaggi utente, **inglese** per nomi tecnici e codice

## Differenziazione vs altri subagent del pack

| Tipo | Esempi pack | `/web-builder` |
|------|-------------|----------------|
| DATA-driven | `/lead-finder-pro` (output = CSV lead) | NO |
| REPORT-driven | `/competitor-deep-dive` (output = markdown analysis) | NO |
| **ARTIFACT-driven** | **`/web-builder`** | **SI — output = repo Git con app deployata** |
| WORKFLOW-driven | `/automation-architect` (output = n8n workflow) | NO |

Questo significa: il "Definition of Done" dell'agent include un'app raggiungibile via URL (preview Vercel), non un file markdown.

## Fase A — Deep Research (1-1.5 giorni)

### Research questions (rispondere TUTTE prima di passare a B)

1. **Tech stack winner 2026 per non-developer audience**: Next.js 15 vs SvelteKit vs Astro vs Remix — quando ognuno e la scelta giusta? Decision matrix per use case (landing marketing, SaaS, internal tool, content hub)? Cosa dice la `tech-stack-2026` di Filippo (baseline) e dove puo essere overridden?
2. **Database/BaaS 2026 winner**: Convex vs Supabase vs Neon vs Turso — quale e il default per un MVP non-developer? Trade-off realtime vs SQL flexibility, lock-in, pricing, MCP support? Filippo usa Convex (tech-stack-2026) ma molti tutorial citano Supabase — quando suggerire override?
3. **Auth provider 2026**: Clerk vs Supabase Auth vs NextAuth.js vs Lucia vs WorkOS — quale e il default per consumer SaaS? Quando serve enterprise SSO? Quanto costa scalare? Integration con Convex e Next.js 15 App Router?
4. **Deploy target 2026**: Vercel vs Netlify vs Cloudflare Pages vs Railway — best per Next.js? Quando serve Railway (Docker, PostgreSQL legacy)? CI/CD pattern con GitHub Actions vs Vercel auto-deploy?
5. **shadcn/ui + Tailwind v4 patterns**: come si inizializza un progetto Next.js 15 con shadcn nel 2026? Quale theme baseline (slate, zinc, custom)? Pattern componenti piu richiesti (auth forms, dashboard layout, pricing page, hero sections)?
6. **CLAUDE.md best practice per nuovi progetti web**: cosa includere obbligatoriamente (stack, conventions, glossario business, anti-pattern, gotchas)? Differenze CLAUDE.md root vs `.claude/` settings.json? Vedi anche `skills/CLAUDE_starter_template.md` se esiste.
7. **n8n integration patterns con web app**: come si collega frontend Next.js a workflow n8n via webhook? Pattern auth (HMAC, API key)? Sync vs async? Quando usare Convex action invece di n8n?
8. **Deploy automation per non-developer**: come gestire `VERCEL_TOKEN`, `GITHUB_TOKEN`, secrets in modo sicuro per audience non-tech? Pattern OAuth vs PAT? Quanto puo fare automaticamente l'agent senza che l'utente debba toccare un terminale?

### Fonti da consultare

**NotebookLM dedicato** (DA CREARE in Fase A da worker chat):

```bash
notebooklm create "Web Builder - Tech Stack 2026"
# -> restituisce notebook_id, salvalo in research/notebook-id.txt

# Aggiungi 8 sources URL:
notebooklm source add <notebook_id> https://nextjs.org/docs
notebooklm source add <notebook_id> https://docs.convex.dev/home
notebooklm source add <notebook_id> https://supabase.com/docs/guides/getting-started
notebooklm source add <notebook_id> https://clerk.com/docs/quickstarts/nextjs
notebooklm source add <notebook_id> https://vercel.com/docs/cli
notebooklm source add <notebook_id> https://ui.shadcn.com/docs/installation/next
notebooklm source add <notebook_id> https://docs.astro.build/en/getting-started/
notebooklm source add <notebook_id> https://vercel.com/docs/agent-resources/vercel-mcp

# Aspetta indicizzazione 3-5 min, poi ask per ognuna delle 8 RQ
notebooklm ask <notebook_id> "<research question 1 testo completo>"
```

**WebSearch query** (cross-check fonti recenti):

- "Next.js 15 vs Astro vs SvelteKit 2026 production landing page comparison"
- "Convex vs Supabase 2026 startup MVP non-developer comparison"
- "Vercel CLI deploy automation MCP server 2026"
- "Clerk vs NextAuth vs Supabase Auth 2026 Next.js 15 App Router"
- "shadcn/ui Tailwind v4 2026 starter template patterns"
- "CLAUDE.md best practices new project 2026 monorepo"
- "n8n webhook integration Next.js Convex action pattern"

**WebFetch URL specifici** (estrai dettagli tecnici):

- https://nextjs.org/docs/app (App Router 2026)
- https://docs.convex.dev/quickstart/nextjs (Convex + Next.js setup)
- https://clerk.com/docs/quickstarts/nextjs (Clerk Next.js quickstart)
- https://vercel.com/docs/cli/deploy (Vercel CLI deploy reference)
- https://vercel.com/docs/mcp (Vercel MCP server official)
- https://ui.shadcn.com/docs/components-json (shadcn config schema)
- https://docs.astro.build/en/install-and-setup/ (Astro setup per landing alternative)

**parallel-cli** per ricerca approfondita su use case business:

- `parallel-cli research "non-developer founder build SaaS MVP 2026 stack"`
- `parallel-cli research "shadcn boilerplate Next.js Convex Clerk 2026"`
- `parallel-cli search "site:reddit.com/r/nextjs Convex vs Supabase 2026"`

### Output research

Salva in `research/research-summary.md`:

- 1 sezione per ogni research question (1-8)
- Ogni claim con citazione fonte (URL)
- Top 5 finding piu rilevanti per l'agent
- **Decision matrix tabellare** stack -> use case (landing | SaaS | internal tool | content) con raccomandazione default Filippo
- Edge case scoperti (lista) — es. "se utente ha gia repo no-code platform", "se utente vuole self-host"
- Tool/CLI capabilities mappate (Vercel CLI, Convex CLI, GitHub CLI, shadcn CLI)
- Eventuali decisioni emergent -> append in `DECISIONS.md` come DECISION-005, 006, ...

Salva sintesi finale anche in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/web-builder_2026-MM-DD.md` con frontmatter standard (vedi `~/Dev/obsidian-vault/CLAUDE.md`).

## Fase B — Architecture Design (2-3 ore)

### Discovery questionnaire (proposta — affina basato su research)

Salva versione finale in `discovery/questions.md`. Proposta iniziale:

| # | Question | Header chip | Options | Conseguenza logica |
|---|----------|-------------|---------|--------------------|
| 1 | Che tipo di prodotto stai costruendo? | Tipo | Landing/marketing site - SaaS micro - Internal tool/dashboard - Content/blog - Mobile app | Determina template starter e stack default |
| 2 | Hai esperienza dev pregressa? | Esperienza | Zero - Vibe coder (capisco la logica) - Junior dev - Senior | Adatta verbosity spiegazioni e safety net |
| 3 | Tech stack preferito? | Stack | Default Filippo (Next.js+Convex+Clerk) - Supabase (piu SQL-friendly) - Astro (solo se landing) - una piattaforma no-code (no-code first) - Lasciami consigliare | Override DECISION-003 se utente sceglie esplicitamente |
| 4 | Hai gia un dominio? | Dominio | Si (custom) - No (uso .vercel.app) - Compro adesso | Configura Vercel domain in deploy automation |
| 5 | Auth richiesta? | Auth | Si consumer (Clerk) - Si enterprise SSO (WorkOS) - No (pubblico) - Gia ho provider | Skip Clerk setup se No, install WorkOS se enterprise |
| 6 | Database necessario? | Database | Si realtime (Convex) - Si SQL classico (Supabase) - No (statico) - Solo CMS (Sanity/Contentful) | Determina backend init |
| 7 | Integrazione n8n/automation? | Automation | Si (webhook in/out) - No - Piu tardi | Aggiungi `n8n-integration.md` reference + esempio webhook handler |
| 8 | Deploy automation? | Deploy | Si auto (Vercel + Git push) - No (deploy manuale per ora) - Gia configurato | Setup `VERCEL_TOKEN` flow se Si |

Logica conseguente esempi:
- Se Q1 = "Landing/marketing" -> propose Astro come default (DECISION-005 da fare in Fase B se confermata)
- Se Q3 = "Default Filippo" -> applica `tech-stack-2026` integralmente
- Se Q3 = "Supabase" -> carica `references/supabase-override.md` + warning "diverso da tech-stack-2026"
- Se Q5 = "Enterprise SSO" -> install WorkOS, NON Clerk
- Se Q7 = "Si n8n" -> genera anche `app/api/webhook/route.ts` placeholder + n8n workflow template
- Se Q8 = "Si auto" -> triggers OAuth flow Vercel + GitHub link

### MCP mapping

| MCP server | Tipo | Required for | Fallback se mancante |
|------------|------|--------------|----------------------|
| `vercel` (mcp.vercel.com OAuth) | **Recommended primary** | Deploy automation, env vars management, project linking | Vercel CLI via Bash (`vercel deploy --prod --token $VERCEL_TOKEN`) — funziona ma richiede token manuale |
| `github` MCP (se disponibile) | Recommended | Init repo, push, branch protection | `gh` CLI via Bash (`gh repo create`, `gh secret set`) |
| `context7` | **Recommended** | Fetch docs aggiornati Next.js/Convex/Clerk runtime | WebFetch URL specifici (piu lento) |
| `playwright` | Optional | Smoke test post-deploy (HTTP 200, screenshot) | curl + bash check status |
| `apify` | Optional | Scrape design reference se utente fornisce URL screenshot | WebFetch + html2text |
| `n8n-default` / `n8n-knowledge` | Optional (se Q7=Si) | Create webhook workflow companion | Genera solo file `.json` workflow, utente lo importa manualmente |

**NOTE chiave**: Convex non ha MCP nativo (verificato Q2 research). Si usa `npx convex dev` via Bash + Convex CLI.

### Pattern detection (pseudocode per system prompt)

```python
# All'avvio del subagent, dopo discovery:
mcp_status = {}
for mcp in ["vercel", "github", "context7", "playwright", "apify"]:
    mcp_status[mcp] = verify_mcp(mcp)

# Detection CLI installati locale (richiesti come fallback)
cli_status = {
    "vercel": shutil.which("vercel") is not None,
    "gh": shutil.which("gh") is not None,
    "npx": shutil.which("npx") is not None,
    "git": shutil.which("git") is not None,
    "node": shutil.which("node") is not None,
}

# Save in config.md mcp_available + cli_available + mcp_fallbacks_active
# Mostra summary all'utente: "Tool disponibili: Vercel MCP OK, gh CLI OK, Convex CLI installato OK. Fallback attivi: GitHub MCP missing -> useremo gh CLI."
```

### Skills companion (4-5 skill, contratto chiaro)

#### 1. `project-scaffolder/SKILL.md`

- **Cosa fa**: genera struttura cartelle + file base in base a template scelto (nextjs-saas, nextjs-landing, astro-marketing, next-internal-tool, expo-mobile). Include `package.json`, `tsconfig.json`, `tailwind.config.ts`, `app/` o `src/`, `.gitignore`, `.env.example`.
- **Input**: `{template_id, project_name, project_path, options: {auth, database, payments}}`
- **Output**: cartella popolata + log file creati. Ritorna `{path, files_created: [...], next_steps: [...]}`.
- **References**: `references/stack-comparison-2026.md`, `scripts/templates/<template_id>/`
- **Activation**: Fase 2 methodology (post-discovery)
- **Target righe SKILL.md**: ~220

#### 2. `claude-md-generator/SKILL.md`

- **Cosa fa**: compila CLAUDE.md preconfigurato in base a discovery + stack scelto. Include sezioni: Contesto business, Stack, Convenzioni, Glossario business, Anti-patterns, Gotchas placeholder.
- **Input**: discovery answers + stack config + project_name
- **Output**: file `CLAUDE.md` scritto in project root + `.claude/settings.json` con allowed-tools sensati.
- **References**: `references/claude-md-templates.md` (3 template: SaaS, landing, internal tool)
- **Activation**: Fase 2 methodology (subito dopo `project-scaffolder`)
- **Target righe**: ~180

#### 3. `auth-database-setup/SKILL.md`

- **Cosa fa**: integra Clerk + Convex (default) o Supabase Auth + Supabase (override) nel progetto scaffoldato. Genera env vars template, `convex/schema.ts` o `lib/supabase.ts`, middleware auth, route protetta esempio.
- **Input**: `{auth_provider, db_provider, project_path}`
- **Output**: file integration scritti + checklist env vars da settare. Ritorna lista `env_vars_required: [...]`.
- **References**: `references/auth-integration-2026.md`, `references/database-integration-2026.md`
- **Activation**: Fase 3 methodology (dopo scaffolder)
- **Target righe**: ~250

#### 4. `deploy-automation/SKILL.md`

- **Cosa fa**: orchestrazione deploy Vercel via MCP (preferito) o CLI. Init `vercel link`, push GitHub, configura env vars production, primo deploy preview, smoke test, switch a prod. Riusa pattern `deploy-check` skill v1 come gating pre-deploy.
- **Input**: `{project_path, vercel_token | oauth, env_vars: {...}, prod: bool}`
- **Output**: `{deploy_url, status, smoke_test_results, rollback_command}`
- **References**: `references/deploy-vercel-2026.md`, `references/deploy-check-rules.md` (riusa pattern v1)
- **Activation**: Fase 5 methodology (post user approval)
- **Target righe**: ~280

#### 5. `n8n-bridge/SKILL.md` (opzionale, attivata se Q7=Si)

- **Cosa fa**: genera webhook handler `app/api/webhook/[event]/route.ts` Next.js + workflow n8n template `.json` companion. Include HMAC verification pattern, error handling, retry logic.
- **Input**: `{event_name, webhook_secret_strategy: "hmac" | "api_key", direction: "in" | "out" | "both"}`
- **Output**: file route.ts scritto + `n8n-workflows/<event_name>.json` template
- **References**: `references/n8n-integration-2026.md`
- **Activation**: Fase 4 methodology (solo se Q7=Si)
- **Target righe**: ~180

### Config schema (`<memory>/config.md`)

```yaml
---
agent: web-builder
created: 2026-MM-DD
last_updated: 2026-MM-DD
schema_version: 1
---

# Identita progetto

project:
  name: "my-saas"
  path: "~/Dev/projects/my-saas"
  type: saas_micro  # landing | saas_micro | internal_tool | content | mobile
  domain: "my-saas.com"  # optional, default <name>.vercel.app

# Esperienza utente

user:
  experience: vibe_coder  # zero | vibe_coder | junior | senior
  language_preference: it

# Tech stack

stack:
  framework: nextjs_15  # nextjs_15 | astro | sveltekit | expo | no-code
  database: convex  # convex | supabase | none | sanity
  auth: clerk  # clerk | workos | supabase_auth | none
  styling: tailwind_v4  # always
  ui_library: shadcn  # always
  payments: none  # stripe | autumn | none
  deploy: vercel  # vercel | netlify | cloudflare | railway

# Integrations

integrations:
  n8n: true  # webhook in/out enabled
  ai_sdk: false  # Vercel AI SDK
  composio: false  # AI agent tool integration

# Deploy config

deploy:
  vercel_project_id: "prj_xxx"
  github_repo: "username/my-saas"
  auto_deploy_main: true
  preview_deploys: true
  domain_configured: false  # set true after vercel domain add

# MCP availability

mcp_available:
  vercel: true
  github: false  # fallback gh CLI
  context7: true
  playwright: true
  apify: false

cli_available:
  vercel: true
  gh: true
  npx: true
  git: true
  node: true

# Build state

build:
  scaffold_done: true
  claude_md_done: true
  auth_db_done: true
  first_deploy_done: false
  smoke_test_passed: false
```

### References docs (6+ file in `references/`)

Lista minima:

1. `stack-comparison-2026.md` — Decision matrix Next.js / Astro / SvelteKit / una piattaforma no-code vs use case (landing | SaaS | internal | content | mobile). Output da Fase A Q1.
2. `database-integration-2026.md` — Convex setup completo (schema, queries, mutations, actions) + Supabase override section. Output Fase A Q2.
3. `auth-integration-2026.md` — Clerk + Next.js App Router setup, middleware, protected routes. WorkOS section per enterprise. Output Fase A Q3.
4. `deploy-vercel-2026.md` — Vercel MCP usage + CLI fallback (`vercel link`, `vercel env add`, `vercel deploy --prod`), GitHub Actions pattern, env vars management, custom domain. Output Fase A Q4.
5. `claude-md-templates.md` — 3 CLAUDE.md template (saas-template.md, landing-template.md, internal-tool-template.md). Riusa pattern `skills/CLAUDE_starter_template.md` se esiste.
6. `n8n-integration-2026.md` — Webhook handler Next.js + n8n workflow template, HMAC verification, async pattern. Output Fase A Q7.
7. `deploy-check-rules.md` — 14 regole pre-deploy (riusa skill v1 `deploy-check`, espandi).
8. `shadcn-patterns-2026.md` — Component patterns top 10 (auth-form, dashboard-layout, pricing-page, hero-section, data-table, command-palette, mode-toggle, sidebar-nav, empty-state, loading-skeleton). Output Fase A Q5.

### Output Fase B

Salva tutto in `ARCHITECTURE.md` nella cartella dell'agent. Format come `lead-finder-pro/ARCHITECTURE.md` (~420 righe target).

## Fase C — Build (5-7 ore)

### Subagent file principale

`<pack-root>/.claude/agents/web-builder/web-builder.md`

Frontmatter (esempio iniziale — adatta in base a research):

```yaml
---
name: web-builder
description: Da brief utente in linguaggio naturale a progetto web production-grade scaffoldato (Next.js 15 + Convex + Clerk + shadcn + Vercel) con CLAUDE.md preconfigurato, componenti base, auth, database, deploy automation. Multi-template (SaaS, landing, internal tool, content, mobile). Self-configuring al first run con discovery interattiva (8 domande), poi memoria persistente per build successive nello stesso progetto. Audience non-developer Learnn.
when_to_use: Nuovo progetto web da zero, MVP rapido SaaS, landing page marketing, dashboard interno team, content/blog, app mobile (Expo), sostituzione Google Sheet con tool custom, prototipo cliente
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, Glob, AskUserQuestion
mcpServers:
  - vercel
  - github
  - context7
  - playwright
  - apify
skills:
  - project-scaffolder
  - claude-md-generator
  - auth-database-setup
  - deploy-automation
  - n8n-bridge
memory: project
model: sonnet
color: blue
---

[SYSTEM PROMPT 350-500 righe — vedi struttura sotto]
```

### Struttura system prompt (10 sezioni)

Target totale: **350-500 righe** (questo e l'agent piu complesso del pack).

| # | Sezione | Righe target | Content |
|---|---------|--------------|---------|
| 1 | Identita + ruolo | 25 | Chi sei, per chi lavori, audience non-developer Learnn, italiano user-facing, principio "production-grade ma comprensibile" |
| 2 | Discovery flow | 70 | Check `<memory>/config.md`. Se mancante -> 8 AskUserQuestion sequence (vedi `discovery/questions.md`) -> save config. Logica conseguente per ogni Q (Q1 driver template, Q3 driver stack override, Q5 driver auth provider, Q7 driver n8n bridge skill) |
| 3 | MCP + CLI detection logic | 45 | `verify_mcp()` per ogni server, check CLI installati (vercel, gh, npx, git, node), save status, mostra summary "Tool disponibili: X. CLI presenti: Y. Fallback attivi: Z" |
| 4 | Tech stack decision matrix | 50 | Quando applicare `tech-stack-2026` di Filippo integralmente vs override (es. Astro per landing-only, Supabase se utente ha SQL legacy). Tabella decision integrata + reasoning step-by-step |
| 5 | Methodology principal (6 fasi) | 90 | Discover -> Scaffold -> CLAUDE.md+config -> Auth+DB integration -> Components+routes -> Deploy automation. Ogni fase ha checkpoint user approval prima di proseguire |
| 6 | Tool usage rules | 50 | Quando Vercel MCP vs Vercel CLI; quando context7 vs WebFetch; quando playwright smoke test; rules per `npx` (sempre con `--yes` flag in non-interactive) |
| 7 | Output format & file conventions | 30 | Naming convention progetto (kebab-case), struttura cartelle standard, env vars naming (NEXT_PUBLIC_ prefix per client), git initial commit message |
| 8 | Edge cases handling | 50 | Cartella gia esistente (offer merge vs abort), Node version mismatch, npm install fail, Vercel deploy fail, env vars missing, GitHub repo name conflict, Convex/Clerk auth setup partial |
| 9 | Examples input -> output | 60 | 3 esempi reali end-to-end: (a) "voglio una landing per il mio corso AI" -> Astro+Tailwind+Vercel, (b) "voglio un SaaS micro per gestire i miei clienti freelance" -> Next.js+Convex+Clerk+Stripe, (c) "tool interno per tracciare campagne" -> Next.js+Convex+Clerk+Sheet input |
| 10 | Anti-patterns | 30 | Cosa NON fa MAI: deploy senza user approval, commit secrets, override CLAUDE.md esistente senza chiedere, scegliere stack non in `tech-stack-2026` senza warning, generare 1000 file boilerplate inutili, hardcoded credentials |

### Skills companion

Per ogni skill in `skills/<skill-name>/SKILL.md`, formato standard. Vedi `skills/meta/skill-builder/SKILL.md` per pattern di scrittura skill.

### References

In `references/`, file markdown ben strutturati. **Output Fase A si converte in references** (es. `stack-comparison-2026.md` viene da `research-summary.md` Q1).

### Scripts e templates

In `scripts/`:

- `discovery_check.py` — verifica esistenza config.md, ritorna stato
- `mcp_detect.py` — check MCP disponibili
- `cli_detect.sh` — bash check (vercel, gh, npx, git, node, convex CLI)
- `scaffold_project.py` — wrapper che copia template -> project path con sostituzione placeholder
- `vercel_deploy.sh` — wrapper Vercel CLI con error handling (fallback se MCP missing)
- `smoke_test.py` — post-deploy HTTP 200 check + screenshot via playwright

In `scripts/templates/` (5 starter):

- `nextjs-saas/` — Next.js 15 + Convex + Clerk + Stripe + shadcn dashboard layout (~30 file)
- `nextjs-landing/` — Next.js 15 + Tailwind + shadcn hero+pricing+CTA (~15 file)
- `astro-marketing/` — Astro + Tailwind + content collections (~12 file)
- `next-internal-tool/` — Next.js 15 + Convex + Clerk + data table + filters (~20 file)
- `expo-mobile/` — Expo + Convex + Clerk auth (placeholder, ~10 file)

**NOTE**: i template starter contengono placeholder `{{PROJECT_NAME}}`, `{{AUTHOR}}`, `{{DOMAIN}}` che il scaffolder sostituisce. **Non includere `node_modules/` ne `.next/`** nei template.

### README utente-facing

`README.md` user-friendly:

- Cosa fa in 2 paragrafi (audience non-tech: "ti scaffoldo un'app vera in 30 min")
- Installazione (4 step max: install Claude Code, link MCP Vercel/GitHub, install CLI vercel+gh+node)
- Esempi (3 reali con prompt -> output): landing, SaaS micro, internal tool
- FAQ (8-10 domande comuni: "posso cambiare stack dopo?", "come gestisco i secrets?", "deploy costa?")
- Troubleshooting (7 problemi comuni con fix)

## Fase D — Test (1.5-2 ore)

### Test checklist (7 test concreti, eseguibili)

1. **Discovery flow**: in cartella vuota `~/tmp/web-builder-test-1/`, invoca `/web-builder` -> verifica 8 AskUserQuestion mostrate, salvataggio config in `<memory>/config.md`.
2. **Re-run skip discovery**: stessa cartella con config.md -> verifica nessuna AskUserQuestion, conferma "Config trovata, riprendiamo dal build state".
3. **Real build landing**: in `~/tmp/web-builder-test-2/`, prompt "voglio una landing per il mio corso AI dal nome 'AI Mastery'" -> discovery (Q1=landing, Q3=Astro override) -> verifica scaffold completato, file `CLAUDE.md` presente, `npm install` eseguito, `npm run dev` parte su localhost:4321.
4. **Real build SaaS micro**: in `~/tmp/web-builder-test-3/`, prompt "SaaS per gestire clienti freelance, login email+password, dashboard, billing mensile" -> discovery -> scaffold Next.js+Convex+Clerk+Stripe -> verifica `convex/schema.ts` esiste, `middleware.ts` Clerk presente, `.env.local.example` con tutti i KEY required.
5. **MCP fallback Vercel**: simula Vercel MCP non disponibile (rinomina in settings.json) -> verifica messaggio "Vercel MCP non disponibile, uso CLI con `VERCEL_TOKEN`", richiesta token, deploy procede via CLI.
6. **Deploy automation end-to-end**: dopo test #4, esegui `/web-builder deploy` -> verifica `vercel link`, `vercel env add` per ogni env, `vercel deploy --prod`, ritorno URL preview -> smoke test playwright HTTP 200 + screenshot home.
7. **Edge case cartella esistente**: in cartella con file pre-esistenti, invoca `/web-builder` -> verifica prompt "trovo file esistenti, vuoi mergiare/abortire/backup?", no overwrite silenzioso.

Salva risultati in `TEST-RESULTS.md` (format come `lead-finder-pro/TEST-RESULTS.md`). Per i test che richiedono runtime live (3-7), documentali come checklist manuale per Filippo se la worker chat non puo eseguirli direttamente.

### Fixtures suggeriti

In `test-fixtures/`:

- `prompt-landing.md` — prompt completo per test #3
- `prompt-saas-micro.md` — prompt completo per test #4
- `prompt-internal-tool.md` — prompt extra
- `expected-files-saas.txt` — lista file attesi post-scaffold (per verification)

## Fase E — Documentation + Bundle (1 ora)

1. Aggiorna `MASTER-PROGRESS.md` (path `<pack-root>/.claude/agents/MASTER-PROGRESS.md`): cambia stato `/web-builder` da intermedio a OK Done
2. Aggiungi sezione in `dist/CLAUDE_WEEK_SKILL_PACK.md` con descrizione + install + 3 esempi
3. Salva sintesi in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/web-builder_2026-MM-DD.md`
4. (Opzionale) Screencast 5 min — solo se hai tempo. Per audience webinar W3 Vibe Coding e particolarmente utile
5. Notifica al coordinator chat (ping Filippo): "web-builder DONE, ready per test"

## Definition of Done

- [ ] Tutte le 5 fasi completate
- [ ] PROGRESS.md aggiornato a "Done"
- [ ] MASTER-PROGRESS.md aggiornato (Done)
- [ ] Test checklist 7/7 documentati (eseguiti o checklist manuale per Filippo)
- [ ] README utente comprensibile da non-tech (test mentale: lo darei a un freelancer marketer?)
- [ ] System prompt > 350 righe e sostanzioso
- [ ] 5 skills companion + 6+ references docs
- [ ] **5 template starter funzionanti** in `scripts/templates/` (smoke `npm install` + `npm run dev` su almeno nextjs-saas e astro-marketing)
- [ ] Almeno 3 esempi reali documentati end-to-end nel README
- [ ] research-summary.md > 2500 parole con citazioni
- [ ] **Almeno 1 progetto demo deployato** (URL Vercel pubblico, anche placeholder) come prova ARTIFACT-driven

## Context management (per worker chat)

### Update PROGRESS.md (ogni 25% context, MINIMO ogni fase)

Template entry:

```markdown
## YYYY-MM-DD HH:MM — Milestone X

### OK Cosa e stato fatto
- Fase X completata
- File creati: <lista path>
- Decisioni prese: <link a DECISIONS.md riga N>

### IN CORSO Cosa sto facendo ora
- <step corrente>

### TODO Prossimi step
1. ...
2. ...

### BUG Edge case scoperti
- <problema>: <fix proposto>

### LINK File esterni rilevanti
- <path file letto/scritto>
```

### A 50% context fill

1. Update finale PROGRESS.md + DECISIONS.md
2. User chiama `/compact` (o tu lo suggerisci)
3. Re-prime: "Leggi BUILD-BRIEF.md, PROGRESS.md, DECISIONS.md. Continua da dove eravamo."

### File da NON perdere mai (re-leggi sempre dopo compact)

- BUILD-BRIEF.md (questo file)
- PROGRESS.md
- DECISIONS.md (decisioni immutabili)
- ARCHITECTURE.md (se Fase B completata)
- research/research-summary.md (se Fase A completata)
- `~/.claude/skills/tech-stack-2026/SKILL.md` (baseline tech stack di Filippo)

### Update MASTER-PROGRESS.md

Aggiorna anche `<pack-root>/.claude/agents/MASTER-PROGRESS.md` quando:
- Inizi build (cambia stato a In progress)
- Completi una fase (aggiungi entry log)
- Termini (Done)

## Decisioni che il coordinator deve approvare prima di Fase B

Durante Fase A research potrebbero emergere queste decisioni che richiedono input Filippo:

1. **Deploy automation senza credenziali utente?** Vercel MCP usa OAuth (l'utente fa login in browser una volta), ma se utente ha gia `VERCEL_TOKEN` in `~/.zshrc` lo riusiamo? Pattern proposto: prima check OAuth via MCP, fallback su token env var.
2. **Convex vs Supabase default**: `tech-stack-2026` dice Convex, ma molti tutorial 2026 indipendenti citano Supabase per audience non-tech (piu SQL-friendly). Confermare Convex come default oppure permettere choice in Q3?
3. **Astro come override per landing**: tech-stack-2026 dice Next.js sempre. Ma per landing pure-static Astro e 40-70% piu performante (verificato in research). Permettere override Q3=Astro per Q1=Landing?
4. **Mobile (Expo) scope**: includere template Expo o postponare a v2 dell'agent?

Queste decisioni vanno documentate in DECISIONS.md come emergent (DECISION-005+).

## Riferimenti incrociati

- **Skills v1 base (spunto, non overwrite)**:
  - `<pack-root>/skills/webinar-3/vibe-start/SKILL.md`
  - `<pack-root>/skills/webinar-3/deploy-check/SKILL.md`
- **Skill globale baseline obbligatoria**: `~/.claude/skills/tech-stack-2026/SKILL.md`
- **Pattern subagent ufficiale**: https://code.claude.com/docs/en/sub-agents
- **Pattern skill ufficiale**: https://code.claude.com/docs/en/skills
- **Skill builder pattern**: `<pack-root>/skills/meta/skill-builder/SKILL.md`
- **Validation pattern (qualita target)**: `.claude/agents/lead-finder-pro/{BUILD-BRIEF,ARCHITECTURE,PROGRESS,DECISIONS}.md`
- **NotebookLM dedicato**: DA CREARE in Fase A (worker chat)
- **CLAUDE.md progetto**: `<pack-root>/CLAUDE.md`
- **Master plan**: `~/.claude/plans/analizza-attentamente-il-progetto-glowing-taco.md`
- **CLAUDE.md utente globale**: `~/.claude/CLAUDE.md` (regole engineering, persona, stack operativo)
- **MASTER-PROGRESS pack v2**: `<pack-root>/.claude/agents/MASTER-PROGRESS.md`
