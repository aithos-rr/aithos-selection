# CLAUDE.md Templates — Reference

> Output Fase A research RQ6 → reference per skill `claude-md-generator`. 3 template variant: SaaS, Landing, Internal Tool.

## Best practices 2026

- Target: <200 righe (60-300 max)
- Progressive disclosure via `@path/to/file.md` (recursive imports max 5 livelli)
- `.claude/rules/*.md` auto-loaded con stessa priority
- Information hierarchy: scannable, no walls of text
- Concise > complete

---

## Template 1 — SaaS micro

```markdown
# {{PROJECT_NAME}}

## Project context

{{PROJECT_DESCRIPTION}}

Audience: utenti consumer / freelance / piccole aziende.
Problem solved: {{Q1_DERIVED_PROBLEM}}.

## Stack

- **Framework**: Next.js 15 (App Router)
- **Database**: Convex (TypeScript-first, realtime)
- **Auth**: Clerk (consumer, free 10k MAU)
- **Styling**: Tailwind CSS v4
- **UI**: shadcn/ui
- **Payments**: Stripe (via Convex Components)
- **Deploy**: Vercel

Per integrations dettagliate: vedi `@docs/integrations.md` (se popolato).

## Common commands

```bash
npm run dev              # Dev server (localhost:3000)
npm run build            # Production build local
npx convex dev           # Convex dev deployment (foreground)
npx convex deploy        # Convex prod deployment
vercel deploy            # Preview deploy
vercel deploy --prod     # Production deploy
npm run lint             # ESLint
npm run type-check       # TypeScript strict check
```

## Code style

- TypeScript strict (no `any`, no `// @ts-ignore`)
- ES modules (no CommonJS `require`)
- Functional components + hooks (no class)
- Tailwind utility classes (no CSS modules / styled-components)
- Naming: PascalCase componenti, camelCase funzioni, kebab-case file route

## Key files

- `app/layout.tsx` — Root layout, providers (`ClerkProvider` + `ConvexProviderWithClerk`)
- `middleware.ts` — Clerk auth route protection (matcher in `config`)
- `convex/schema.ts` — Database schema (defineTable, indexes)
- `convex/<entity>.ts` — Queries + mutations per entity
- `app/api/webhook/stripe/route.ts` — Stripe webhook handler
- `lib/utils.ts` — `cn()` helper per shadcn

## Testing

- Unit/component: Vitest (`npm test`)
- E2E (se aggiunto): Playwright (`npm run e2e`)
- Type check: `npm run type-check` deve passare prima di ogni deploy

## Glossary business

(Da popolare se domain-specific. Esempi: "Cliente", "Progetto", "Fattura", "Subscription".)

## Anti-patterns

- No SQL diretto (use Convex queries)
- No `git add -A` o `git add .` (rischio commit secrets)
- No env vars secret in `NEXT_PUBLIC_*`
- No password storing custom (Clerk gestisce)
- No state management oltre Convex queries (no Redux/Zustand inutile)

## Gotchas

(Vuoto. Popolare during dev quando incontri sorprese.)
```

---

## Template 2 — Landing / Marketing

```markdown
# {{PROJECT_NAME}}

## Project context

{{PROJECT_DESCRIPTION}}

Tipo: landing page / marketing site (no auth, no DB).
Goal: conversion-optimized, SEO-friendly, fast load.

## Stack

- **Framework**: {{Astro 5.0 o Next.js 15}}  ← branch su Q3
- **Styling**: Tailwind CSS v4
- **UI**: shadcn/ui
- **Content**: {{Content Collections (Astro) o MDX (Next)}}
- **Deploy**: Vercel

## Common commands

```bash
npm run dev              # Dev server ({{port: 4321 Astro o 3000 Next}})
npm run build            # Production build
npm run preview          # Preview prod build local
vercel deploy            # Preview deploy
vercel deploy --prod     # Production deploy
```

## Code style

- TypeScript strict
- {{Astro: .astro components, frontmatter --- per logic | Next: TSX functional}}
- Tailwind utility classes

## Key files

- {{Astro: `src/pages/index.astro` — Home | Next: `app/page.tsx`}}
- {{Astro: `src/content/config.ts` — Content schema | Next: `app/blog/[slug]/page.mdx`}}
- `src/components/Hero.{{astro|tsx}}` — Hero section
- `src/components/Pricing.{{astro|tsx}}` — Pricing cards
- `tailwind.config.ts` — Theme colors

## SEO checklist

- [ ] `<title>` + `<meta description>` ogni pagina
- [ ] Open Graph + Twitter Card meta tags
- [ ] `sitemap.xml` (Astro: `@astrojs/sitemap`, Next: `next-sitemap`)
- [ ] `robots.txt`
- [ ] Lighthouse score >90 (Astro target 95+, Next target 85+)
- [ ] Structured data (JSON-LD) per pagine principali

## Performance target

- FCP < 1.5s
- LCP < 2.5s
- CLS < 0.1
- INP < 200ms

## Anti-patterns

- No JS heavy interactions (use Astro islands, lazy load)
- No CSS-in-JS (Tailwind utility only)
- No large client-side bundles (check `npm run build` output)
- No images senza optimization (use `<Image>` component)

## Gotchas

(Vuoto. Popolare during dev.)
```

---

## Template 3 — Internal Tool

```markdown
# {{PROJECT_NAME}}

## Project context

{{PROJECT_DESCRIPTION}}

Tipo: tool interno team / dashboard custom.
Audience: <N> utenti interni (team {{team_name}}).
Problem solved: {{Q1_DERIVED_PROBLEM}}.

## Stack

- **Framework**: Next.js 15
- **Database**: Convex
- **Auth**: Clerk (Organizations mode per multi-team)
- **Styling**: Tailwind v4 + shadcn/ui
- **Deploy**: Vercel (custom domain {{custom_domain}})

## Common commands

```bash
npm run dev              # Dev (localhost:3000)
npx convex dev           # Convex dev
vercel deploy --prod     # Production deploy
```

## Key files

- `middleware.ts` — Clerk auth + Organization scope
- `convex/schema.ts` — Schema (con `users`, `<entity1>`, `<entity2>`, ...)
- `convex/auth.config.ts` — Clerk JWT config
- `app/(dashboard)/layout.tsx` — Sidebar layout
- `app/(dashboard)/<entity>/page.tsx` — Entity routes

## Glossary business

(Popolare con termini specifici team. Esempi YT GTM Engineering: "lead", "deal", "campaign", "sequence".)

## Convenzioni team

- Naming entità: kebab-case routes, PascalCase components
- Permission model: tutti gli auth users vedono tutti i dati (no RLS — internal tool)
- Audit log: ogni mutation logga `{userId, action, entityId, timestamp}` in `convex/audit.ts`

## Anti-patterns

- No multi-tenancy strict (è internal tool, audience small)
- No public-facing pages (tutto sotto auth middleware)
- No PII export senza warning utente

## Gotchas

(Vuoto.)
```

---

## Mapping discovery → template

| `discovery.q1` | Template |
|---|---|
| `saas_micro` | Template 1 (SaaS) |
| `landing` | Template 2 (Landing) |
| `internal_tool` | Template 3 (Internal Tool) |
| `content` | Template 2 (Landing variant) |
| `mobile` | Template 1 con Expo notes (stub) |

## Sostituzioni placeholder

Skill `claude-md-generator` sostituisce:
- `{{PROJECT_NAME}}` → `config.project.name`
- `{{PROJECT_DESCRIPTION}}` → narrativa derivata Q1+Q3
- `{{Q1_DERIVED_PROBLEM}}` → utente-fornito durante discovery preliminare
- `{{Astro|Next.js}}` → ramificazione condizionale Q3
- `{{custom_domain}}` → `config.project.domain` o `<project>.vercel.app`
- `{{team_name}}` → opzionale, ask se internal tool

## Filippo's `CLAUDE_starter_template.md` reuse

Esiste `<pack-root>/skills/CLAUDE_starter_template.md`. Pattern: leggere quel file in skill `claude-md-generator`, espandere sezioni stack-specific basate su `tech-stack-2026`. Riusare struttura sezioni Filippo, NON sovrascrivere.

## Sources

- [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices)
- [uxplanet.org/claude-md-best-practices-1ef4f861ce7c](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c)
- [turbodocx.com — How to Write a CLAUDE.md File That Actually Works](https://www.turbodocx.com/blog/how-to-write-claude-md-best-practices)
