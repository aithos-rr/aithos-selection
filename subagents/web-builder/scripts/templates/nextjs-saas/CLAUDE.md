# {{PROJECT_NAME_TITLE}}

## Project context

{{DESCRIPTION}}

Audience: utenti consumer / freelance / piccole aziende.

## Stack

- **Framework**: Next.js 15 (App Router)
- **Database**: Convex (TypeScript-first, realtime)
- **Auth**: Clerk (consumer, free 10k MAU)
- **Styling**: Tailwind CSS v4
- **UI**: shadcn/ui (style: new-york, base: neutral)
- **Deploy**: Vercel

## Common commands

```bash
npm run dev              # Dev server (localhost:3000)
npm run build            # Production build
npx convex dev           # Convex dev deployment
npx convex deploy        # Convex prod
vercel deploy            # Preview deploy
vercel deploy --prod     # Production deploy
npm run lint             # ESLint
npm run type-check       # TypeScript strict
```

## Code style

- TypeScript strict (no `any`, no `// @ts-ignore`)
- ES modules (no CommonJS)
- Functional components + hooks
- Tailwind utility classes

## Key files

- `app/layout.tsx` — Root layout, providers (`ClerkProvider` + `ConvexProviderWithClerk`)
- `middleware.ts` — Clerk auth protection (`/dashboard`, `/api`, `/settings`)
- `convex/schema.ts` — Database schema
- `convex/<entity>.ts` — Queries + mutations
- `lib/utils.ts` — `cn()` helper for shadcn
- `app/(dashboard)/dashboard/page.tsx` — Protected dashboard

## Testing

- `npm run type-check` — TS strict
- (Add `vitest` setup quando ti serve unit testing)

## Anti-patterns

- No SQL diretto (use Convex queries)
- No `git add -A` (rischio commit secrets)
- No env vars secret in `NEXT_PUBLIC_*`
- No password storing custom (Clerk gestisce)

## Gotchas

(Vuoto. Popolare during dev.)
