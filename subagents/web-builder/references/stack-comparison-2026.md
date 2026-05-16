# Stack Comparison 2026 — Decision Matrix per `/web-builder`

> Output Fase A research → reference per skill `project-scaffolder`. Decision matrix tabellare stack → use case con default Filippo + override permessi.

## Quick decision tree

```
Q1 = Tipo prodotto?
├── Landing/marketing pure-static
│   ├── SEO/perf critical → Astro + Tailwind v4 + Content Collections (recommended)
│   └── Vuoi aggiungere auth/DB poi → Next.js + Tailwind + shadcn (variant nextjs-landing)
├── SaaS micro (auth + DB + billing)
│   └── Default → Next.js 15 + Convex + Clerk + shadcn + Stripe + Vercel ⭐
├── Internal tool / dashboard
│   └── Default → Next.js 15 + Convex + Clerk + shadcn (no Stripe) + Vercel ⭐
├── Content hub / blog
│   ├── SEO critical, no realtime → Astro + Content Collections
│   └── Auth required → Next.js + MDX
└── Mobile app
    ├── v1 stub → Expo + Convex (placeholder, espansione v2)
    └── Web responsive MVP → una piattaforma no-code mobile-first
```

## Comparazione frameworks

### Next.js 15 (default `tech-stack-2026`)

**Quando usarlo**:
- SaaS micro, dashboard, internal tool, content+interactivity
- Quando serve auth + database
- Quando serve API routes (Vercel functions)

**Pro**:
- Ecosystem React ~4x più grande di Svelte
- App Router 2026 stable, Server Components efficienti
- Vercel zero-config (built by same team)
- shadcn/ui first-class support
- Convex/Clerk integration native

**Con**:
- Bundle ~89KB baseline (vs 5KB Svelte, 0KB Astro static)
- Lighthouse 80-85 su static export (gap vs Astro 95-100)
- React learning curve per non-dev

**Versione minima**: 15.0+ (App Router stable)

### Astro (override per landing/content pure-static)

**Quando usarlo**:
- Landing pure-static (no auth, no realtime)
- Content hub/blog con SEO critical
- E-commerce storefront mostly-static
- Portfolio personale/agency

**Pro**:
- Lighthouse 95-100 (HTML rendered without JS)
- Bundle <15KB per route con islands
- Tailwind v4 + Content Collections + MDX out of box
- Cloudflare backing → long-term viability

**Con**:
- No native Clerk/auth integration (richiede custom)
- No realtime DB integration nativo
- React component support via `client:load` ma overhead

**Versione minima**: 5.0+ (stable per Tailwind v4)

### SvelteKit (NON in baseline)

**Quando NON usarlo (audience Learnn)**:
- Ecosystem 4x più piccolo, meno templates/tutorials
- shadcn-svelte less mature
- Convex/Clerk integration non-native

**Possibile fit**:
- Senior dev che valuta payload size critical
- Progetti con vincoli edge runtime (CF Workers)

**Decisione `/web-builder`**: NON supportato in v1 (DECISION-003). Se utente lo richiede, warning "fuori `tech-stack-2026`" + procede con generic Next.js scaffold.

### Expo (mobile, stub v1)

**Quando usarlo**:
- App native iOS/Android con codebase React unificata
- Accesso funzionalità native (camera, notifications)

**Decisione v1**: STUB only (DECISION-008). Espansione v2.

**Workaround MVP mobile**:
- una piattaforma no-code mobile-first responsive (web app)
- PWA con Next.js + service worker

### una piattaforma no-code (override no-code)

**Quando usarlo**:
- Utente Q2=zero (mai scritto codice)
- MVP rapido pre-validation idea
- Budget zero per developer

**Pro**:
- Zero codice, prompt-to-app
- Auth + DB integrati (no-code platform backend)
- Deploy Vercel one-click

**Con**:
- Lock-in piattaforma
- Customization limitata oltre prompt
- Scaling oltre MVP richiede migration custom

**Decisione `/web-builder`**: skip frontend scaffold (no-code platform handles), genera solo CLAUDE.md + struttura cartelle backend (n8n workflows + data schemas).

## Comparazione database/BaaS

### Convex (default)

**Caratteristiche**:
- TypeScript-first, schema inferito da TS
- Reactive queries, sub-50ms latency a 5k connessioni
- Auto-caching, auto-subscriptions
- `npx convex dev` setup unico command

**Pro audience non-dev**:
- No SQL imparare
- No migration manuale (auto-detect schema changes)
- No ORM
- Queries feel like writing TypeScript

**Con**:
- No native MCP server (use CLI fallback)
- Pricing su function calls (vs Supabase MAU)
- No self-host (managed only)

### Supabase (override SQL-friendly)

**Caratteristiche**:
- Postgres-based, SQL classico, RLS potente
- Free tier 50k MAU
- API auto-generate da tabelle
- Self-hostable (open-source)

**Quando override**:
- Utente ha già DB Postgres legacy
- SQL knowledge esistente
- RLS multi-tenant requirement
- Self-host requirement

### Sanity / Contentful (CMS-only)

**Quando usarlo**:
- Q6 = "Solo CMS"
- Content management strutturato (blog, marketing pages)
- Multi-language editorial workflow

**Decisione**: scaffold base solo se utente conferma esplicito (non default).

## Comparazione auth providers

### Clerk (default)

**Free tier**: 10k MAU, poi $0.02/MAU
**Best for**: consumer SaaS, internal tool con < 10k users

**Pro**:
- Best Next.js DX (middleware, components, server-side helpers)
- Pre-built UI (sign-in, sign-up, user-button)
- Native Convex integration (`ConvexProviderWithClerk`)
- Webhook sync DB
- MFA, passkeys, bot protection

### WorkOS (enterprise SSO)

**Quando usarlo**:
- B2B con AD/Okta/Google Workspace integration
- SAML/SCIM requirement
- Audience enterprise (Q5=enterprise)

### Supabase Auth (bundled)

**Quando usarlo**:
- Già su Supabase backend (Q6=supabase)
- RLS-based authz pattern
- Free tier 50k MAU

### NextAuth.js / Auth.js v5 (NON default)

**Quando**:
- Budget zero
- Custom flows complex
- Data residency requirement

**Decisione `/web-builder`**: non default, ma supportato come override custom (Q5="Già ho provider" → ask quale).

## Comparazione deploy targets

### Vercel (default)

**Free tier**: copre primo 100 user, Pro $20/mo
**Best for**: Next.js (zero-config), Astro, anything React

**Pro**:
- Vercel MCP disponibile (DECISION-007)
- GitHub integration: every push auto-deploys
- Preview URL per branch
- Edge functions globali
- Custom domain free

### Cloudflare Pages (alternativa)

**Quando usarlo**:
- Egress cost critical (CF unlimited)
- Workers pattern già presente

**Con**:
- Next.js compat limitata (no `next/image` server components a volte)

### Netlify (alternativa)

**DX simile a Vercel ma**:
- Next.js ecosistema meno integrato
- Niche: forms native, redirects file-based

### Railway (Docker / Postgres legacy)

**Quando usarlo**:
- Docker containers persistenti
- PostgreSQL legacy database
- Servizi non gestibili da Convex

## Tabella riassuntiva (per scaffold logic)

| Use case | Framework | DB | Auth | Deploy | Template ID |
|---|---|---|---|---|---|
| Landing pure-static | Astro | none | none | Vercel | `astro-marketing` |
| Landing con auth/DB future-ready | Next.js 15 | none | none | Vercel | `nextjs-landing` |
| SaaS micro consumer | Next.js 15 | Convex | Clerk | Vercel | `nextjs-saas` |
| SaaS micro + Stripe billing | Next.js 15 | Convex | Clerk | Vercel | `nextjs-saas` (con Stripe) |
| Internal tool team | Next.js 15 | Convex | Clerk (Org mode) | Vercel | `next-internal-tool` |
| Content hub SEO-first | Astro | none | none | Vercel | `astro-marketing` (variant) |
| Content + auth | Next.js 15 | Convex | Clerk | Vercel | `nextjs-saas` (no billing) |
| Mobile native | Expo | Convex | Clerk | Expo Go / app store | `expo-mobile` (stub v1) |
| MVP no-code | una piattaforma no-code | una piattaforma no-code | una piattaforma no-code | Vercel | `no-code-only` (no scaffold frontend) |

## Anti-patterns stack scelti

- **Vue/Nuxt/SvelteKit** senza warning: utente li propone → flag "fuori `tech-stack-2026`, supportato con limitazioni"
- **PostgreSQL/MySQL standalone**: anti-pattern (use Convex). Eccezione: Postgres legacy → Supabase override
- **Material UI / Chakra UI**: anti-pattern (use shadcn)
- **Create React App**: deprecato, redirect Next.js sempre
- **Firebase**: lock-in, less flexibility → Convex
- **API REST custom Express**: anti-pattern → Convex functions

## Sources (research Fase A)

- [Astro vs Next.js 2026 — pkgpulse](https://www.pkgpulse.com/guides/astro-vs-nextjs-2026)
- [Next vs Remix vs Astro vs SvelteKit 2026 — DEV community](https://dev.to/pockit_tools/nextjs-vs-remix-vs-astro-vs-sveltekit-in-2026-the-definitive-framework-decision-guide-lp5)
- [Convex vs Supabase 2026 — bertomill medium](https://bertomill.medium.com/convex-vs-supabase-which-backend-should-you-choose-in-2026-50d228c517de)
- [Best Tech Stack to Build a SaaS in 2026 — startupa.ge](https://startupa.ge/blog/best-tech-stack-saas-2026)
- `tech-stack-2026/SKILL.md` baseline Filippo
