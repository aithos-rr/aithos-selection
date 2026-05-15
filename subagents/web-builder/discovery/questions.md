# Discovery Questions — `/web-builder`

> Versione finale post-research Fase A. Usata da `web-builder.md` system prompt sezione 2 (Discovery flow). 8 domande mirate, ognuna con `header` chip + options + conseguenza logica nel build.

## Pattern AskUserQuestion

Ogni domanda è una singola call ad `AskUserQuestion` con `multiSelect: false` (default) e options che mappano 1:1 a fields di `<memory>/config.md`. Le 8 domande sono **sequenziali**, non parallele — ognuna influenza la successiva (es. Q1 determina default Q3).

## Q1 — Tipo di prodotto

**Header chip**: Tipo

**Question**: Che tipo di prodotto stai costruendo?

**Options**:
| Label | description (mostrato all'utente) |
|---|---|
| `Landing/marketing` | Landing page o sito marketing pubblico (no login utenti) |
| `SaaS micro` | Web app con login, dashboard utente, billing |
| `Internal tool` | Tool interno team o cliente (login, no billing) |
| `Content/blog` | Blog, content hub, magazine |
| `Mobile app` | App iOS/Android (Expo) |

**Maps to**: `config.project.type` (`landing` | `saas_micro` | `internal_tool` | `content` | `mobile`)

**Conseguenza logica**:
- `landing` → propose Astro come default override in Q3 (DECISION-005)
- `mobile` → flag stub v1, suggerisce alternativa una piattaforma no-code (DECISION-008)
- `content` → propose Astro + Content Collections come default
- `saas_micro` | `internal_tool` → applica `tech-stack-2026` integralmente (Next.js + Convex + Clerk)

---

## Q2 — Esperienza dev

**Header chip**: Esperienza

**Question**: Hai esperienza dev pregressa?

**Options**:
| Label | description |
|---|---|
| `Zero` | Mai scritto codice, vibe coder al primo progetto |
| `Vibe coder` | Capisco la logica, non la sintassi (no-code, n8n) |
| `Junior` | Ho scritto codice ma non production |
| `Senior` | Sviluppatore esperto, voglio lo scaffold rapido |

**Maps to**: `config.user.experience` (`zero` | `vibe_coder` | `junior` | `senior`)

**Conseguenza logica**:
- `zero` | `vibe_coder` → verbosity alta nei messaggi, safety net massima (conferma prima di ogni azione distruttiva), default opinionati senza chiedere troppo
- `junior` → verbosity media, spiega concetti tecnici la prima volta
- `senior` → verbosity bassa, skip le spiegazioni base, mostra comandi pronti

---

## Q3 — Tech stack

**Header chip**: Stack

**Question**: Tech stack preferito?

**Options dinamiche** (cambiano in base a Q1):

Se Q1=`landing` o `content`:
| Label | description |
|---|---|
| `Astro (default per landing)` | Astro + Tailwind v4 + Content Collections — best performance per static |
| `Default Filippo` | Next.js + Convex + Clerk (override se vuoi auth/DB più tardi) |
| `no-code platform (no-code)` | Frontend una piattaforma no-code + Vercel deploy (zero codice) |

Se Q1=`saas_micro` o `internal_tool`:
| Label | description |
|---|---|
| `Default Filippo` ⭐ | Next.js + Convex + Clerk + Tailwind v4 + shadcn (raccomandato) |
| `Supabase override` | Next.js + Supabase (se preferisci SQL classico, Postgres, RLS) |
| `no-code platform (no-code)` | Frontend una piattaforma no-code + n8n backend |
| `Lasciami consigliare` | Decido io basato su Q4-Q8 |

Se Q1=`mobile`:
| Label | description |
|---|---|
| `Expo + Convex (v1 stub)` | Stub minimo, espansione in v2 — al momento usa una piattaforma no-code o native |
| `no-code platform (mobile via web)` | Frontend una piattaforma no-code, deploy responsive web come MVP |

**Maps to**: `config.stack.framework` + `config.stack.database` + `config.stack.auth`

**Conseguenza logica**:
- `Default Filippo` → applica `tech-stack-2026` integralmente
- `Astro` → carica `references/astro-override.md` + skip Convex+Clerk setup
- `Supabase override` → carica `references/supabase-override.md` + warning "diverso da tech-stack-2026"
- `no-code` → genera solo CLAUDE.md + struttura cartelle + n8n workflow templates (skip Next.js scaffold)
- `Lasciami consigliare` → agent decide post-Q4-Q8 con summary "Ho scelto X perché Y"

---

## Q4 — Dominio

**Header chip**: Dominio

**Question**: Hai già un dominio per il sito?

**Options**:
| Label | description |
|---|---|
| `Sì, custom` | Ho già il dominio (es. mio-saas.com) |
| `No, uso .vercel.app` | Va bene il subdominio Vercel gratuito (project-name.vercel.app) |
| `Compro adesso` | Vorrei comprarne uno (suggeritemi where + how) |
| `Decido dopo` | Pensiamo a questo dopo il deploy |

**Maps to**: `config.project.domain` (string optional) + `config.deploy.domain_configured` (bool)

**Conseguenza logica**:
- `Sì, custom` → ask URL, save in config, configura `vercel domain add` in deploy automation
- `No` | `Decido dopo` → skip domain config, usa default `<project>.vercel.app`
- `Compro adesso` → suggest Namecheap/Cloudflare Registrar (~$10-15/year), istruzioni step-by-step

---

## Q5 — Auth

**Header chip**: Auth

**Question**: Servirà autenticazione utenti?

**Options**:
| Label | description |
|---|---|
| `Sì consumer (Clerk)` ⭐ | Login email/password, social, magic link — default raccomandato |
| `Sì enterprise (WorkOS)` | SSO/SAML, directory sync (audience B2B grande) |
| `No (pubblico)` | Sito pubblico, nessun login |
| `Già ho provider` | Ho già setup auth (Auth0, Firebase Auth, custom) — solo integration |

**Maps to**: `config.stack.auth` (`clerk` | `workos` | `none` | `custom`)

**Conseguenza logica**:
- `Sì consumer` → install Clerk, genera middleware, route protection example, env vars `CLERK_*`
- `Sì enterprise` → install WorkOS AuthKit, override DECISION-003 con flag enterprise
- `No` → skip skill `auth-database-setup` auth section, default Q6=No DB se Q1=Landing
- `Già ho provider` → ask which, genera adapter scaffolding, no install

---

## Q6 — Database

**Header chip**: Database

**Question**: Serve un database per l'app?

**Options**:
| Label | description |
|---|---|
| `Sì realtime (Convex)` ⭐ | TypeScript-first, sub-50ms latency — default Filippo |
| `Sì SQL classico (Supabase)` | Postgres + RLS + SQL queries (override) |
| `No (statico)` | Sito senza dati persistenti (landing, blog statico) |
| `Solo CMS (Sanity/Contentful)` | Headless CMS per content management |

**Maps to**: `config.stack.database` (`convex` | `supabase` | `none` | `sanity`)

**Conseguenza logica**:
- `Convex` → install + scaffold `convex/schema.ts` + `convex/<entity>.ts` example queries/mutations
- `Supabase` → install + scaffold `lib/supabase.ts` client + RLS policy template
- `No` → skip skill `auth-database-setup` DB section
- `Sanity` (non default in `tech-stack-2026`): ask conferma, genera scaffold base solo se utente conferma
- Se Q5=`No` e Q6=`No`: pure static site, skip backend setup completamente

---

## Q7 — Integrazione n8n / automation

**Header chip**: Automation

**Question**: Servirà integrazione con n8n o automazioni esterne?

**Options**:
| Label | description |
|---|---|
| `Sì (webhook in/out)` | App → n8n e/o n8n → app (es. signup → benvenuto, pagamento → fulfillment) |
| `No` | App self-contained, no automation esterne |
| `Più tardi` | Per ora no, magari aggiungo dopo il MVP |

**Maps to**: `config.integrations.n8n` (bool)

**Conseguenza logica**:
- `Sì` → attiva skill `n8n-bridge`, genera `app/api/webhook/[event]/route.ts` placeholder con HMAC scaffold + `n8n-workflows/<event>.json` template (Webhook trigger + Code node HMAC verify)
- `No` | `Più tardi` → skip skill `n8n-bridge`, può essere aggiunta dopo con `/web-builder add-n8n`

---

## Q8 — Deploy automation

**Header chip**: Deploy

**Question**: Vuoi che configuri il deploy automatico?

**Options**:
| Label | description |
|---|---|
| `Sì auto (Vercel + Git push)` ⭐ | Deploy automatico ad ogni push, preview per ogni branch — raccomandato |
| `No (deploy manuale per ora)` | Solo scaffold, deployerò io con `vercel deploy` quando pronto |
| `Già configurato` | Repo già linkato a Vercel, skip step |

**Maps to**: `config.deploy.auto_deploy_main` (bool) + `config.deploy.preview_deploys` (bool)

**Conseguenza logica**:
- `Sì auto` → triggers OAuth flow Vercel via MCP (preferred) o `vercel login` CLI (fallback), `vercel link`, configura env vars production, primo preview deploy, smoke test (DECISION-007: 3-tier detection)
- `No` → genera solo `.env.example` e `vercel.json`, documenta `vercel deploy` come step manuale in README
- `Già configurato` → skip `vercel link`, ask `vercel project ID` per save in config

---

## Workflow completo discovery

```
Start /web-builder
  ↓
Check <memory>/config.md
  ├─ Esiste → "Trovo config esistente, riprendo build" → skip discovery, continua da `config.build.<last_phase>`
  └─ NON esiste → discovery flow:
       ↓
     Q1 (Tipo) → Q2 (Esperienza) → Q3 (Stack, opzioni dinamiche da Q1)
       ↓
     Q4 (Dominio) → Q5 (Auth) → Q6 (Database)
       ↓
     Q7 (n8n) → Q8 (Deploy)
       ↓
     Save config.md + summary "Ecco cosa ho capito: <stack>. Procedo? [si/modifica]"
       ↓
     User conferma → Fase 2 methodology (scaffold)
```

## Skip logic

L'agent **deve** poter skippare domande in scenari particolari:

- **Q5 = No** + **Q6 = No** → skip Q7 (n8n) e Q8 (deploy ha senso comunque) — landing pure-static
- **Q1 = Mobile** → skip Q4 (no dominio web), Q7 (no n8n), salta a confirm Q3 stub
- **Q3 = no-code platform** → skip Q5 (no-code platform gestisce auth interna), Q6 (no-code platform + n8n backend), salta a Q7+Q8

## Reconfigure flow

Se utente vuole cambiare config dopo discovery iniziale: `/web-builder reconfigure` → re-run discovery sovrascrivendo `config.md` (ma flag `previous_config` per merge intelligente, non perdere build state).

## Schema validation

Il config salvato in `<memory>/config.md` deve passare validation:

- Q1 valore deve essere in lista valida
- Se Q3=Astro, Q5 deve essere `none` o `custom` (Astro non ha Clerk integration nativa di default)
- Se Q3=no-code platform, Q4-Q8 hanno mapping diverso (no-code platform handles auth+DB)
- Q4 dominio se "Sì custom", deve essere URL valido

Validation handled da `scripts/discovery_check.py --validate`.

## Source

Questo set di domande deriva da:
- BUILD-BRIEF.md sez "Fase B → Discovery questionnaire" (versione iniziale)
- research-summary.md DECISION-005-008 (override Astro per Landing, default Convex+Clerk, Vercel MCP-first, Expo stub)
- skill v1 `vibe-start` Fase 1 (5 domande discovery business — pattern già validato per audience non-dev)
- `tech-stack-2026` "Regole Decisionali Rapide" tabella (mapping use case → stack)
