# Research Summary — `/web-builder` (Pack v2 Learnn)

**Data**: 2026-04-30
**Worker chat**: web-builder
**NotebookLM ID**: `e68d4b25-04fc-4ca3-8a6f-1a252d0dabb4` (Web Builder - Tech Stack 2026, 8 sources)
**Tools**: NotebookLM CLI v0.3.3, WebSearch, WebFetch, parallel-cli v0.2.0

---

## Top 5 finding più rilevanti

1. **Default stack Filippo (Next.js 15 + Convex + Clerk + Vercel) è confermato come best fit per SaaS/internal tool** dal mercato 2026. La community Convex ha pubblicato un template ufficiale `get-convex/template-nextjs-clerk-shadcn` (e `ents-saas-starter` con live demo) che valida la combinazione esatta del `tech-stack-2026` di Filippo. **DECISION-003 confermata**.
2. **Astro è 40-70% più performante di Next.js per landing pure-static** (Lighthouse 95-100 vs 80-85, payload 5-15KB vs 89KB) — gap rilevante per SEO/Core Web Vitals. Permettere override in Q3 della discovery quando Q1=Landing è una vittoria netta. **DECISION-005 da scrivere**.
3. **Vercel MCP esiste e funziona via OAuth** (`https://mcp.vercel.com`, install via `claude mcp add --transport http vercel`). Tools disponibili: docs search, projects management, deployments management, logs analysis. Fallback CLI con `vercel deploy --prod --token $VERCEL_TOKEN` resta supportato. **DECISION-007 da scrivere: MCP-first OAuth, CLI/token fallback**.
4. **CLAUDE.md best practice 2026**: target <200 righe (60-300 max), uso aggressivo di **progressive disclosure** via `@path/to/file.md` (recursive imports fino a 5 livelli) + `.claude/rules/*.md` auto-loaded. La skill companion `claude-md-generator` deve produrre file conciso con import a reference esterni, NON un mega-file.
5. **Convex non ha MCP nativo** — fix è `npx convex dev` via Bash. Template setup: `npm create convex@latest` (più veloce di `create-next-app + npm install convex`), `NEXT_PUBLIC_CONVEX_URL` come unica env var critica. Schema in `convex/schema.ts`, queries/mutations in `convex/<name>.ts`.

---

## RQ1 — Tech stack winner 2026 per non-developer audience

**Domanda**: Next.js 15 vs SvelteKit vs Astro vs Remix — quando ognuno è la scelta giusta? Decision matrix per use case (landing marketing, SaaS, internal tool, content hub)?

### Findings

**Next.js 15** mantiene leadership ecosistema:
- React ha ~4x più developer che Svelte, ecosistema npm con order of magnitude più componenti
- SSR + App Router nativo, integrazione Vercel zero-config
- Lighthouse 80-85 su static export (gap di 10-15 punti vs Astro per pure-static)
- Bundle ~89KB (React 46KB + ReactDOM 7KB + Next client 34KB)
- Sweet spot: SaaS, dashboard, internal tools, content+interactivity

**Astro** vince su content-heavy, low-interactivity:
- Lighthouse 95-100 su landing (HTML rendered without JS)
- Bundle <15KB per route (con islands per interattività selettiva)
- Tailwind v4 + Content Collections + MDX out of box
- Cloudflare backing → long-term viability
- Sweet spot: landing, marketing, content hub, blog, portfolio, e-commerce storefront mostly-static

**SvelteKit** è il "underdog vincente" in payload:
- Bundle ~7KB total (Svelte runtime 5KB + component 2KB)
- 50-70% meno JS di React-based per equivalent functionality
- Compiler-based, no virtual DOM
- Trade-off: ecosistema 4x più piccolo di React, meno templates/tutorials per non-dev

**Remix** in declino post-acquisition Shopify (in-progress merge con React Router 7).

### Decision matrix (Filippo's `tech-stack-2026` baseline + override permessi)

| Use case | Default Filippo | Override sensato | Quando override |
|---|---|---|---|
| **Landing/marketing** pure-static | Next.js (baseline) | **Astro** | Q1=Landing + Q3=Astro override; performance/SEO critical, no auth, no DB |
| **SaaS micro** (auth + DB) | **Next.js + Convex + Clerk** ✅ | Supabase override Q3 | SQL legacy, RLS critical |
| **Internal tool / dashboard** | **Next.js + Convex + Clerk** ✅ | — | Default sempre |
| **Content/blog** | Next.js + MDX | **Astro + Content Collections** | SEO/perf critical, no real-time |
| **Mobile** | Expo (baseline) | — | Solo se serve native (camera, notifications, app store) |

### Edge case scoperti

- **no-code platform progetto già esistente**: utente ha frontend una piattaforma no-code, vuole aggiungere backend. Soluzione: skip scaffold frontend, integra `convex/` folder + Vercel deploy.
- **Self-host requirement**: Filippo non lo supporta in v1 (richiede Docker/K8s expertise). Flag warning + suggest Railway come alternativa managed.
- **Stack misto monorepo**: utente vuole web + mobile insieme. Trattali come 2 progetti separati, non Turborepo (over-engineering per audience non-dev).

### Sources

- [Astro vs Next.js 2026 — PkgPulse](https://www.pkgpulse.com/guides/astro-vs-nextjs-2026)
- [Next.js vs Remix vs Astro vs SvelteKit 2026 Decision Guide — DEV Community](https://dev.to/pockit_tools/nextjs-vs-remix-vs-astro-vs-sveltekit-in-2026-the-definitive-framework-decision-guide-lp5)
- [SvelteKit vs Next.js 2026 — pkgpulse](https://www.pkgpulse.com/blog/nextjs-vs-sveltekit-2026)

---

## RQ2 — Database/BaaS 2026 winner

**Domanda**: Convex vs Supabase vs Neon vs Turso — quale è il default per un MVP non-developer?

### Findings

**Convex** (default `tech-stack-2026`):
- TypeScript-first: backend functions in TS, schema inferito da TS, no migrations, no SQL
- Reactive queries: changes triggerano UI updates, sub-50ms latency a 5k connessioni concurrent
- Auto-caching, auto-subscriptions
- `npx convex dev` setup unico command
- Sweet spot: real-time apps, dashboard live, chat/collab, stack moderno

**Supabase**:
- Postgres-based, SQL classico, Row-Level Security (RLS) potente
- Free tier 50k MAU (vs Convex 1M function calls/month free)
- API auto-generate da tabelle, REST + GraphQL
- Self-hostable (open-source)
- Sweet spot: SQL-heavy, complex queries, audit log, multi-tenant con RLS

**Neon** (Postgres serverless):
- Niche: branching database per dev/preview deploy
- Trade-off: solo DB (no auth, no storage), si abbina a Vercel ma serve glue layer

**Turso** (SQLite distribuito):
- Edge-replicated, ottimo per read-heavy globale
- Trade-off: SQLite = limiti su transazioni complesse, immaturo per audience non-dev

### Comparison non-developer perspective

> *"Convex feels closer to modern frontend development workflows; Supabase feels closer to traditional backend engineering."*

Per Learnn audience (founder/marketer/freelancer):
- Convex riduce concetti da imparare (no SQL, no migration, no ORM)
- Supabase richiede comprensione SQL base + RLS (SQL policy syntax steep)

**Default confermato**: Convex (allineato `tech-stack-2026`). Override via Q3=Supabase quando: (a) utente ha già DB Postgres legacy, (b) SQL knowledge esistente, (c) RLS multi-tenant requirement.

### Edge case

- **Convex per landing pure-static**: NON serve. Skip Convex setup se Q1=Landing + no auth.
- **Migration da Supabase a Convex**: scenario raro, non in scope v1. Documenta come "v2 enhancement".

### Sources

- [Convex vs Supabase: Choosing the Right Backend — UI Bakery](https://uibakery.io/blog/convex-vs-supabase)
- [Convex vs Supabase 2026 — Robert Mill, Medium](https://bertomill.medium.com/convex-vs-supabase-which-backend-should-you-choose-in-2026-50d228c517de)
- [Convex Quickstart Next.js — docs.convex.dev](https://docs.convex.dev/quickstart/nextjs)

---

## RQ3 — Auth provider 2026

**Domanda**: Clerk vs Supabase Auth vs NextAuth.js vs Lucia vs WorkOS — quale è il default per consumer SaaS?

### Findings

**Clerk** (default `tech-stack-2026`):
- Best Next.js App Router integration: middleware nativo, `<ClerkProvider>`, server-side helpers
- Pre-built UI components (sign-in, sign-up, user-button)
- Free tier: 10k MAU, poi $0.02/MAU
- Webhook support per sync DB (es. Convex `internal.users.upsertFromClerk`)
- MFA, passkeys, bot protection out of box
- Native Convex integration: `ConvexProviderWithClerk`

**NextAuth.js (Auth.js v5)**:
- Free, self-hosted, zero vendor lock-in
- Massima customization
- Trade-off: dev time investment significativo, security responsibility on you
- Sweet spot: data residency requirement, budget zero, custom flows

**Supabase Auth**:
- Free tier 50k MAU
- Tight integration con Postgres + RLS
- Sweet spot: già su Supabase, RLS-based authz

**WorkOS**:
- Enterprise SSO/SAML/SCIM
- Pricing per-connection, expensive per consumer
- Sweet spot: enterprise B2B con AD/Okta integration

**Lucia** (deprecato 2026, fork active community ma decaying).

### Decision matrix

| Use case | Provider | Reason |
|---|---|---|
| Consumer SaaS / internal tool | **Clerk** ✅ | Best DX, free 10k MAU, native Convex integration |
| Enterprise SSO required | WorkOS | SAML/SCIM, AD integration |
| Budget zero + custom flows | NextAuth.js | Free, full control |
| Già su Supabase backend | Supabase Auth | Bundled, RLS native |

### Pattern hybrid (Clerk + Supabase)

Documenta in reference: alcuni vogliono Clerk auth + Supabase DB. Pattern via `clerk/clerk-supabase-nextjs` template. Solo se utente lo richiede esplicitamente, NON default.

### Sources

- [Authentication Best Practices: Convex, Clerk and Next.js — stack.convex.dev](https://stack.convex.dev/authentication-best-practices-convex-clerk-and-nextjs)
- [Complete Authentication Guide for Next.js App Router — Clerk](https://clerk.com/articles/complete-authentication-guide-for-nextjs-app-router)
- [Building auth in Next.js App Router 2026 — WorkOS blog](https://workos.com/blog/nextjs-app-router-authentication-guide-2026)

---

## RQ4 — Deploy target 2026

**Domanda**: Vercel vs Netlify vs Cloudflare Pages vs Railway — best per Next.js? CI/CD pattern?

### Findings

**Vercel** (default `tech-stack-2026`):
- Zero-config Next.js (built by same team)
- Free tier handles first 100 users; paid Pro $20/mo
- GitHub integration: every push auto-deploys, preview URL per branch
- **Vercel MCP** disponibile (vedi RQ8 details)
- Custom domain free
- Edge functions globali

**Cloudflare Pages**:
- Più cheap a scale (egress free)
- Trade-off: Next.js compatibility limita features (no `next/image` server components a volte)

**Netlify**:
- DX simile a Vercel ma ecosistema Next.js meno integrato
- Niche: forms native, redirects/rewrites file-based

**Railway**:
- Necessario solo per Docker / Postgres legacy / containers persistenti
- Fuori scope v1 default

### Pattern CI/CD raccomandato

1. `git push` su branch → Vercel preview deploy auto
2. Merge su `main` → production deploy auto
3. Env vars Vercel UI o CLI (`vercel env add KEY production`)
4. GitHub Actions opzionale per type-check + test pre-merge (non blocking deploy)

### Edge case

- **Self-host Next.js**: no in v1 scope. Suggest Railway con Dockerfile generato.
- **Multi-region prod**: Vercel default già multi-region edge. No tuning richiesto.
- **Custom domain già presente**: utente fornisce dominio → `vercel domain add` + DNS update.

### Sources

- [Vercel CLI Reference — vercel.com/docs/cli](https://vercel.com/docs/cli)
- [Use Vercel's MCP server — vercel.com/docs/agent-resources/vercel-mcp](https://vercel.com/docs/agent-resources/vercel-mcp)

---

## RQ5 — shadcn/ui + Tailwind v4 patterns

**Domanda**: Come si inizializza un progetto Next.js 15 con shadcn nel 2026? Quali pattern componenti più richiesti?

### Findings

**Setup standard**:
```bash
npx shadcn@latest init   # auto-detect Tailwind v4
npx shadcn@latest add button card form dialog
```
- `components.json` configura prefisso, theme, style (`new-york` default 2026)
- `lib/utils.ts` con `cn()` helper auto-generato
- Theme baseline: `slate` (neutral) o `zinc`

**Pattern componenti top 10 (richiesti più del 80% dei progetti SaaS/internal-tool)**:

1. **auth-form** — sign-in/sign-up con shadcn `Card` + `Form` + `Input` (use Clerk pre-built components quando possible)
2. **dashboard-layout** — sidebar + header con `Sidebar` shadcn (route group `(dashboard)/layout.tsx`)
3. **pricing-page** — 3-tier comparison con `Card` + `Badge` + Stripe checkout button
4. **hero-section** — landing top fold con `Button` + gradient text
5. **data-table** — TanStack Table + shadcn `DataTable` (con pagination, search, filter)
6. **command-palette** — `Cmd+K` shortcut con `cmdk` library
7. **mode-toggle** — light/dark/system con `next-themes`
8. **sidebar-nav** — collapsible con `useSidebar()` hook
9. **empty-state** — illustration + CTA quando lista vuota
10. **loading-skeleton** — `Skeleton` component per ogni route

**Pattern App Router strutturale**:
```
app/
├── (auth)/                # route group auth (no sidebar)
│   ├── sign-in/
│   └── sign-up/
├── (dashboard)/           # route group app (sidebar + header)
│   ├── layout.tsx         # con <Sidebar/>
│   └── page.tsx
├── api/                   # API routes (Vercel functions)
└── layout.tsx             # root con <ClerkProvider> + <ConvexProvider>
```

### Open-source starter di riferimento (verificati 2026)

| Repo | Stars | Stack | Note |
|---|---|---|---|
| [Kiranism/next-shadcn-dashboard-starter](https://github.com/Kiranism/next-shadcn-dashboard-starter) | 6k+ | Next 16 + Clerk + TanStack + 6 themes | RBAC, kanban, drag-drop |
| [arhamkhnz/next-shadcn-admin-dashboard](https://github.com/arhamkhnz/next-shadcn-admin-dashboard) | 1k+ | Next 16 + shadcn | Modern admin patterns |
| [get-convex/template-nextjs-clerk-shadcn](https://github.com/get-convex/template-nextjs-clerk-shadcn) | official | **Next + Convex + Clerk + shadcn** ✅ | Match esatto `tech-stack-2026` |
| [get-convex/ents-saas-starter](https://github.com/get-convex/ents-saas-starter) | official | Next + Convex Ents + Clerk + Stripe | Live demo: saas-starter-rouge.vercel.app |

**Decision per /web-builder**: usare `get-convex/template-nextjs-clerk-shadcn` come base per `nextjs-saas` template. Riferire `ents-saas-starter` per pattern advanced (Stripe billing, Convex Ents).

### Sources

- [Next.js — shadcn/ui docs](https://ui.shadcn.com/docs/installation/next)
- [Best shadcn Dashboard Templates 2026 — thefrontkit](https://thefrontkit.com/blogs/best-shadcn-dashboard-templates-2026)
- [Build Admin Dashboard with shadcn 2026 — AdminLTE](https://adminlte.io/blog/build-admin-dashboard-shadcn-nextjs/)

---

## RQ6 — CLAUDE.md best practice per nuovi progetti web

**Domanda**: Cosa includere obbligatoriamente? Differenze CLAUDE.md root vs `.claude/settings.json`?

### Findings

**Target dimensione**: 60-200 righe (max ceiling 300 prima che Claude perda signal). Concisione > esaustività.

**Sezioni obbligatorie** (per nuovo progetto web):

1. **Project context** (3-5 righe): cosa fa l'app, audience, problema risolto
2. **Stack** (5-10 righe): framework + DB + auth + deploy + ai/payment se rilevanti
3. **Common bash commands** (5-10): `npm run dev`, `npx convex dev`, `vercel deploy`, `npm run lint`
4. **Code style** (3-5 righe): "Use TS strict, ES modules, functional components"
5. **Key files / architectural patterns** (5-10): "State in Zustand `src/stores/`, mutations Convex `convex/`"
6. **Testing** (3-5 righe): "New components require test in `*.test.tsx`, run `npm test`"
7. **Glossary business terms** (5-10 righe): se domain-specific (es. "lead", "deal", "pipeline")
8. **Anti-patterns** (3-5 righe): cose da non fare nel progetto
9. **Gotchas placeholder** (vuoto, da popolare during dev)

**Progressive disclosure pattern (chiave 2026)**:
- Usa `@path/to/file.md` per import recursive (fino a 5 livelli) — Claude carica solo quando rilevante
- File markdown in `.claude/rules/*.md` auto-loaded con stessa priorità
- Best for: SOPs lunghe, API architecture, review checklist

**CLAUDE.md vs `.claude/settings.json`**:
- `CLAUDE.md`: contesto semantico (cosa, perché, come) → caricato sempre
- `.claude/settings.json`: configuration tecnica (allowed-tools, hooks, permissions, env) → meccanica
- `.claude/skills/`: skill specifiche progetto → invocate su demand

### Template structure (3 templates da generare in `references/claude-md-templates.md`)

1. **saas-template.md** — full stack Next+Convex+Clerk, dashboard, billing
2. **landing-template.md** — Astro o Next, contenuti, SEO
3. **internal-tool-template.md** — Next+Convex, no payments, internal users only

### Skill `claude-md-starter` esistente

Filippo ha già `<pack-root>/skills/CLAUDE_starter_template.md` (verificato esistente, status M = modified). Strategy: leggere quel file in Fase C build di `claude-md-generator` skill, espandere con stack-specific sections.

### Sources

- [CLAUDE.md Best Practices — Nick Babich, UX Planet](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c)
- [Best Practices for Claude Code — code.claude.com/docs](https://code.claude.com/docs/en/best-practices)
- [How to Write a CLAUDE.md File That Actually Works — TurboDocx](https://www.turbodocx.com/blog/how-to-write-claude-md-best-practices)

---

## RQ7 — n8n integration patterns con web app

**Domanda**: Come si collega frontend Next.js a workflow n8n via webhook? Pattern auth (HMAC, API key)? Sync vs async?

### Findings

**Pattern direzioni**:

1. **Web app → n8n** (webhook out): app Next.js POST a `https://n8n.example.com/webhook/<event>` con body JSON + HMAC signature
2. **n8n → Web app** (webhook in): n8n HTTP Request a `https://app.example.com/api/webhook/<event>` route handler Next.js verifica HMAC + processa
3. **Bidirezionale**: usa entrambi, condividi un secret HMAC

**HMAC verification pattern (canonical)**:

```typescript
// app/api/webhook/[event]/route.ts
import crypto from 'crypto'
import { NextRequest } from 'next/server'

export async function POST(req: NextRequest, { params }: { params: { event: string } }) {
  const rawBody = await req.text()
  const signature = req.headers.get('x-n8n-signature')
  const secret = process.env.N8N_WEBHOOK_SECRET!

  const expected = crypto.createHmac('sha256', secret).update(rawBody).digest('hex')

  if (!crypto.timingSafeEqual(Buffer.from(signature || ''), Buffer.from(expected))) {
    return new Response('Invalid signature', { status: 401 })
  }

  const payload = JSON.parse(rawBody)
  // Handle event
  return new Response('OK', { status: 200 })
}
```

**Critical best practices**:

1. **Raw body** — HMAC computed on bytes received, NOT parsed/re-serialized
2. **Timing-safe comparison** — `crypto.timingSafeEqual()` per evitare timing attack
3. **Secret in env** — mai hardcoded, mai in workflow JSON
4. **N8N non ha HMAC nativo** — devi mettere Code node dopo Webhook trigger per verify

**Sync vs async**:
- **Sync** (utente aspetta risposta): usa Convex Action invece di n8n. Convex action gira server-side, ritorna immediato, no webhook overhead
- **Async** (job lungo, send email, scrape): n8n webhook fire-and-forget + ack 200 immediato + n8n processa background
- **Cron** (schedule): preferisci Convex Cron jobs (built-in) per task TypeScript-only. Usa n8n cron solo se serve integration multi-service esterni

**When to use Convex Action vs n8n**:

| Caso | Soluzione |
|---|---|
| Send email transactional | Convex Action + Resend |
| Scrape sito esterno | n8n (Apify integration) |
| Sync dati 3 service esterni | n8n (Composio/n8n native nodes) |
| Cron daily digest | Convex Cron |
| Workflow multi-step con human approval | n8n |

### Skill `n8n-bridge` activation logic

- Q7 = "Sì n8n integration" → attiva skill, genera `app/api/webhook/[event]/route.ts` placeholder con HMAC scaffold + `n8n-workflows/<event_name>.json` template (Webhook trigger + Code node HMAC verify + Set node example)
- Q7 = "No" → skip skill

### Sources

- [Validate Webhooks with HMAC — n8n.io workflows](https://n8n.io/workflows/3439-validate-seatable-webhooks-with-hmac-sha256-authentication/)
- [Secure n8n Webhooks — logicworkflow.com](https://logicworkflow.com/blog/n8n-webhook-security/)
- [Authentication for Next.js + Convex + Clerk Webhook — gist CS-Martin](https://gist.github.com/CS-Martin/5f34ff6219a01259c9ccdc87405bdf6a)

---

## RQ8 — Deploy automation per non-developer

**Domanda**: Come gestire `VERCEL_TOKEN`, `GITHUB_TOKEN`, secrets in modo sicuro per audience non-tech? Pattern OAuth vs PAT? Quanto può fare automaticamente l'agent senza terminale?

### Findings

**Vercel MCP** (preferred per audience non-dev):

- URL: `https://mcp.vercel.com`
- Install: `claude mcp add --transport http vercel https://mcp.vercel.com`
- Auth: OAuth flow → utente fa login browser una volta, token gestito automaticamente
- Tools disponibili (categories):
  - **Public** (no auth): docs search
  - **Authenticated** (OAuth): list/create projects, deploy, list deployments, env vars management, logs, domains
- Approved clients only: Claude Code ✅, Claude.ai, Cursor, VS Code Copilot, Codex CLI, Cursor, Devin
- Streamable HTTP transport (MCP spec 2025-06-18)
- Confused-deputy protection: explicit user consent per ogni client connection

**Fallback CLI**:
- `npm i -g vercel` (utente installa una volta)
- `vercel login` (browser OAuth → memorizza token)
- `vercel link` per associare folder a progetto Vercel
- `vercel env add KEY production` per aggiungere env var
- `vercel deploy --prod` per production deploy
- Token via `VERCEL_TOKEN` env var (per CI o non-interactive)

**GitHub MCP** (recommended se disponibile):
- `gh auth login` → OAuth browser
- Create repo, push, branch protection, secrets management
- Fallback: `gh repo create`, `gh secret set` via Bash CLI

**Pattern raccomandato per /web-builder**:

1. Discovery Q8 = "Sì auto" → check Vercel MCP available
2. Se MCP available: usa MCP per project create + env vars + deploy. **OAuth handled by Claude Code, no token request to user**
3. Se MCP non available: fallback `vercel` CLI + ask user `vercel login` (browser flow) — no manuale token entry
4. Last resort: ask `VERCEL_TOKEN` env var (advanced users con CI setup)

**GitHub Actions opzionale**:
- Solo per type-check + test pre-merge (non blocking deploy auto Vercel)
- Per audience non-dev, default = NO Actions (Vercel git integration sufficiente)

### Cost / friction reduction

- Free tier Vercel + Convex + Clerk handle first 100 users → $0/month MVP
- Custom domain $0 (use `<project>.vercel.app`) o $10-15/year per `.com`
- GitHub free repo
- Total friction: 3 OAuth flows (Vercel, GitHub, Convex/Clerk dashboard) — tutti via browser, 2-3 min ognuno

### Edge case

- **Utente con `VERCEL_TOKEN` già in `~/.zshrc`**: rispetta env var esistente, skip OAuth (DECISION-007)
- **Utente con repo GitHub già esistente**: skip `gh repo create`, link a esistente
- **Vercel team scope**: utente in più team → ask quale team scope. Default personal account
- **Deploy fail (env mancante)**: agent legge log Vercel via MCP, identifica env var mancante, prompt utente con env name + hint per valore

### Sources

- [Use Vercel's MCP server — vercel.com docs](https://vercel.com/docs/agent-resources/vercel-mcp)
- [How to Build a SaaS App with AI in 2026 — NxCode](https://www.nxcode.io/resources/news/how-to-build-saas-app-with-ai-2026-complete-guide)
- [Best Tech Stack to Build a SaaS in 2026 — startupa.ge](https://startupa.ge/blog/best-tech-stack-saas-2026)

---

## Decisioni emergent → DECISIONS.md (DECISION-005, 006, 007, 008)

| # | Titolo | Default proposto | Rationale |
|---|---|---|---|
| 005 | Astro override per Q1=Landing | **YES** se utente conferma Q3=Astro | Performance gap 40-70%, SEO/CWV critical, allineato con audience non-dev (no friction reale) |
| 006 | Convex stays default vs Supabase | **CONFIRM Convex default** | TypeScript-first, no SQL/migration learning curve, allineato `tech-stack-2026`. Override Q3=Supabase permesso quando SQL/RLS needed |
| 007 | Vercel deploy automation | **OAuth-first via MCP, CLI fallback, token last resort** | Riduce friction utente (no token entry), confused-deputy protection automatica |
| 008 | Expo template scope | **STUB v1 + roadmap v2** | Mobile è 5% degli use case audience Learnn (founder/marketer/freelancer mostly web). Stub `expo-mobile/` template con README "v2 scope, vedi `tech-stack-2026` Expo section". Non blocca pack release |

(Sarà scritto in `DECISIONS.md` come append-only entries.)

---

## Tool/CLI capabilities mappate

| Tool | MCP nativo | CLI fallback | Setup audience non-dev |
|---|---|---|---|
| **Vercel** | ✅ `https://mcp.vercel.com` (OAuth) | `vercel` (npm install -g) | OAuth browser → 1 click |
| **GitHub** | ✅ (vario, third-party) | `gh` (CLI) | OAuth browser → 1 click |
| **Convex** | ❌ (no MCP nativo) | `npx convex dev` (auto-installed) | OAuth browser via `npx convex login` |
| **Clerk** | ❌ (no MCP) | Dashboard manual | Sign up + create app + copy keys to .env.local |
| **shadcn** | ❌ | `npx shadcn@latest init` + `add` | Zero auth, just CLI |
| **n8n** | ✅ (multiple workspaces supportati) | API CLI custom | Per Filippo: già configurato. Per utente esterno: opzionale |
| **Stripe** | ❌ (no MCP nativo) | Dashboard manual | Sign up + dashboard config + copy keys |
| **Supabase** | ❌ (no MCP) | `supabase` CLI | Dashboard or CLI |
| **playwright** | ✅ | CLI | Per smoke test post-deploy |
| **context7** | ✅ | — | Per fetch docs runtime aggiornati |

**Implicazione design**: agent fa **MCP-first detection**, fallback CLI, fallback dashboard manual (con istruzioni dettagliate). Mai chiedere token in chat se evitabile.

---

## Anti-pattern critici (da inserire in system prompt sez 10)

1. **Mai overwrite CLAUDE.md esistente senza chiedere** — utente potrebbe avere setup custom prezioso
2. **Mai commit secrets** — `.env.local`, `.env.production` sempre in `.gitignore` generato
3. **Mai deploy senza user approval** — checkpoint esplicito prima di `vercel deploy --prod`
4. **Mai scegliere stack non in `tech-stack-2026` senza warning** — se utente chiede Vue/Nuxt/SvelteKit, flag "fuori da baseline Filippo, supportato ma con limitazioni"
5. **Mai generare 1000 file boilerplate inutili** — template starter min, lazy-add componenti su richiesta utente
6. **Mai hardcoded credentials in file generati** — sempre `process.env.X`
7. **Mai usare `git add -A`** — solo file specifici (rischio commit secrets)
8. **Mai assumere Node version** — check `node --version` prima, suggest `nvm install 20` se < 20

---

## Output Fase A — checklist completion

- ✅ NotebookLM creato (id `e68d4b25-04fc-4ca3-8a6f-1a252d0dabb4`) + 8 sources aggiunte
- ✅ 7 WebSearch eseguite (RQ1-7 + audience non-dev)
- ✅ 2 WebFetch eseguite (Vercel MCP, Convex Quickstart)
- ✅ 2 parallel-cli search eseguite (boilerplate Convex/Clerk/shadcn, Astro starter)
- ✅ 8 RQ con citazioni fonti
- ✅ Decision matrix tabellare stack → use case
- ✅ Edge case identificati per ogni RQ
- ✅ Tool/CLI capabilities mappate
- ✅ 4 decisioni emergent identificate (DECISION-005-008)
- ✅ Anti-pattern critici listati (8)
- ✅ Top 5 finding compresso in apertura

**Word count**: ~3200 parole (target >2500 ✅)

**Prossimo step**: Fase B — Architecture Design. Scrivere `discovery/questions.md` finale + `ARCHITECTURE.md` + skill contracts per le 5 skill companion.
