# {{PROJECT_NAME_TITLE}}

## Project context

{{DESCRIPTION}}

Tipo: landing page Next.js (no auth, no DB).
Goal: conversion-optimized, SEO-friendly.

## Stack

- **Framework**: Next.js 15
- **Styling**: Tailwind CSS v4
- **UI**: shadcn/ui (opzionale, aggiungi con `npx shadcn@latest add <component>`)
- **Deploy**: Vercel

## Common commands

```bash
npm run dev              # Dev server (localhost:3000)
npm run build            # Production build
npm run lint             # ESLint
vercel deploy --prod     # Production deploy
```

## SEO checklist

- [ ] `<title>` + `<meta description>` in `app/layout.tsx`
- [ ] Open Graph (già impostato in metadata)
- [ ] Sitemap (`next-sitemap` package)
- [ ] `robots.txt` in `public/`
- [ ] Lighthouse > 85

## Anti-patterns

- No JS heavy interactions (mantieni minimal)
- No CSS-in-JS (Tailwind utility only)

## Gotchas

(Vuoto.)
