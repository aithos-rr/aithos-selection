# {{PROJECT_NAME_TITLE}}

## Project context

{{DESCRIPTION}}

Tipo: landing/marketing site (Astro static).

## Stack

- **Framework**: Astro 5.0+
- **Styling**: Tailwind CSS v4
- **Content**: Astro Content Collections (blog opzionale)
- **Deploy**: Vercel (adapter `@astrojs/vercel`)

## Common commands

```bash
npm run dev              # Dev server (localhost:4321)
npm run build            # Production build
npm run preview          # Preview prod local
vercel deploy --prod     # Production deploy
```

## Code style

- Astro components: frontmatter `---` per logic, template per HTML
- TypeScript strict (configured via `astro/tsconfigs/strict`)
- Tailwind utility classes only

## Key files

- `src/pages/index.astro` — Home
- `src/layouts/Layout.astro` — Base layout (head, meta tags, OG)
- `src/content/config.ts` — Content schema (blog)
- `astro.config.mjs` — Astro config + Vercel adapter
- `src/styles/global.css` — Tailwind v4 theme

## SEO checklist

- [x] OG tags in Layout.astro
- [x] Sitemap (`@astrojs/sitemap` integration)
- [ ] Lighthouse > 90 (Astro target 95+)
- [ ] Structured data JSON-LD per pagine principali

## Performance target

- FCP < 1.5s
- LCP < 2.5s
- Lighthouse > 95 (Astro static + Tailwind)

## Anti-patterns

- No client-side JS oltre necessario (use `client:load` selettivamente)
- No CSS-in-JS (Tailwind only)
- No bundles > 50KB

## Gotchas

(Vuoto.)
