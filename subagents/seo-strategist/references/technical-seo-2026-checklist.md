# Technical SEO 2026 — Checklist completa

> Reference doc per skill `technical-seo-audit`. Core Web Vitals INP, mobile-first, hreflang, sitemap, robots.txt, canonical, JS rendering, indexability.

## Core Web Vitals 2026

[primary, [web.dev](https://web.dev/blog/inp-cwv-march-12)]:

| Metric | Threshold good | Threshold needs improvement | Threshold poor | Type |
|--------|----------------|------------------------------|----------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5-4.0s | >4.0s | Loading |
| **INP** (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms | Interactivity |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 | Visual stability |

### INP — primary doc

> «INP officially became a Core Web Vital and replaced FID on March 12, 2024»

[primary, web.dev]:

> «over time, it became clear that a new metric was needed to capture aspects of interactivity on the web that FID did not»

INP è metrica field-only:
- Non misurabile via Lighthouse lab
- Source: CrUX, Search Console, RUM custom

[primary]:

> «Core Web Vitals are assessed using field data specifically, not laboratory measurements. The evaluation happens at the 75th percentile of all page loads»

### Caveat per /seo-strategist

DECISION-009: skill `technical-seo-audit` NON tenta INP measurement automatic. Output: link Search Console URL property + PSI API call for LCP/CLS lab + interpretation guidance.

### Common INP fix

[secondary aggregated]:

1. **Long task breakdown** — split JS task >50ms in chunks via `setTimeout`/`scheduler.yield`
2. **Defer non-critical JS** — `defer` attribute + dynamic import
3. **Reduce main thread work** — Web Workers per heavy compute
4. **Optimize event handlers** — debounce input handlers
5. **Avoid synchronous layout** — read+write batched
6. **Code-split** by route (Next.js auto, vite-plugin-split)
7. **Remove third-party scripts heavy** (chat widgets, analytics overload)

## Mobile-first indexing

Definitivo since 2020. Desktop-only = penalty.

Check:
- Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Touch target ≥48px square
- Font size readable (≥16px body)
- No intrusive interstitials (Google penalty Pop-up Cover)
- Content parity desktop ↔ mobile (no hidden mobile content)

## HTTPS

Mandatory since 2018.

Check:
- All pages served HTTPS
- HTTP redirects 301 to HTTPS
- No mixed content (insecure resource HTTP in HTTPS page)
- TLS 1.2+ supported
- HSTS header (recommended)

## Sitemap.xml

Best practice:
- ≤50,000 URL per file (gzipped if large)
- Referenced in `robots.txt`
- Submitted to Search Console
- `<lastmod>` accurato (not all-set-to-today)
- `<priority>` (legacy, ignored by Google ma utile per crawl-budget tools)

Multi-sitemap pattern:
- `sitemap-index.xml` master
- `sitemap-pages.xml`, `sitemap-products.xml`, `sitemap-blog.xml` segmented

Sitemap freshness signal:
- `<lastmod>` aggiornato → Google priorizza re-crawl

## robots.txt

Best practice:
- Disallow staging/admin path
- Disallow internal search results (avoid duplicate)
- Allow CSS/JS (Google needs to render)
- Reference `Sitemap:` directive
- User-agent specifici per AI crawler (vedi GEO ref doc)

Esempio:

```
User-agent: *
Disallow: /admin/
Disallow: /staging/
Disallow: /search?
Allow: /

Sitemap: https://example.com/sitemap-index.xml

User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /
```

⚠ Common mistake: `Disallow: /` global → blocca indexability totale. Audit P0 critical.

## Canonical tag

```html
<link rel="canonical" href="https://example.com/page" />
```

Best practice:
- Canonical su ogni page (no excludendo)
- Self-referential canonical OK (most case)
- Avoid canonical chain (A→B→C confonde Google)
- Avoid contradiction (canonical points elsewhere + noindex meta)
- Cross-domain canonical OK (syndication scenario)
- HTTPS variants → canonical to HTTPS

Common issues:
- Canonical missing → Google inferisce, può sbagliare
- Canonical to non-existent URL → ignored
- Multiple canonical tag → first wins (Chrome) or ignored (Google)
- Canonical relative URL → fragile, prefer absolute

## Hreflang — multi-language

```html
<link rel="alternate" hreflang="it" href="https://example.com/it/page" />
<link rel="alternate" hreflang="en" href="https://example.com/en/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

Best practice:
- Reciprocal mandatory (URL A → B + URL B → A)
- `x-default` for fallback
- ISO 639-1 language code + ISO 3166-1 country code (es. `it-IT`, `en-US`)
- Self-reference required (each page links to itself)
- Use lowercase + hyphen (`it-IT` valid, `it_IT` invalid)

Validation:
- Test via Search Console > International Targeting (legacy report)
- 3rd party tool: Hreflang Tags Validator

Common issues:
- Reciprocal broken (most common, P1)
- Invalid ISO code
- Mixed methods (hreflang in HTML + sitemap + headers → conflict)

## URL structure

Best practice:
- Short readable
- Hyphens not underscores
- Lowercase only
- Keyword-relevant (not stuffed)
- No session ID visible
- Permanent post-publication

## Internal linking

Best practice 2026:
- 3-5 contextual link per page
- Anchor varied (no exact-match repetition)
- Topic cluster cross-link aggressive
- Pillar ↔ supporting reciprocal
- Footer link curated (no sitewide spam)
- No nofollow per internal (waste)

## JS rendering

[primary, [Google Search Central](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)]:

Google indicizza JS, ma:
- Indexing latency 7-14gg per CSR pure
- SSR/ISR preferiti per content-critical
- Hydration errors risk
- Pre-render via Vercel/Netlify edge

Check:
- View page rendered HTML (Chrome DevTools "View Page Source") vs CSR DOM
- Fetch as Googlebot (Search Console URL Inspection)
- Lighthouse SEO audit

## Structured data (vedi schema-markup-guide-2026.md)

Min recommended sitewide:
- Organization (homepage)
- Article (blog post)
- BreadcrumbList (ecommerce)
- Product (ecommerce SKU)
- LocalBusiness (local site)
- Person (author bio)

## Indexability

### Common issues

| Issue | Detection | Severity |
|-------|-----------|----------|
| `<meta name="robots" content="noindex">` accidentally | HTML parse | P0 if intentional unclear |
| robots.txt Disallow blocking page | robots.txt audit | P0 |
| Canonical pointing elsewhere | HTML parse | P1 |
| Soft 404 (200 status, "not found" content) | Search Console + content scan | P1 |
| Crawl budget exhaustion | Server log | P2 |
| Rendering issue (CSR no SSR) | View source vs DOM | P1 |

### Search Console URL Inspection

Use case:
- "Why is this URL not indexed?"
- Detect canonical mismatch (declared vs Google-selected)
- Detect rendering issue
- Detect crawl date

## Image optimization

- WebP/AVIF format
- Lazy loading native (`loading="lazy"`)
- Alt text descriptive (no keyword stuffing)
- Responsive sizes via `srcset`
- CDN delivery
- Compression < 100KB per image ideal

## Page speed audit tools

| Tool | Type | Free |
|------|------|------|
| PageSpeed Insights | Lab + field (CrUX) | ✅ |
| Lighthouse | Lab only | ✅ Chrome DevTools |
| WebPageTest | Lab detailed | ✅ + paid |
| Search Console > Core Web Vitals | Field | ✅ |
| GTmetrix | Lab + history | ✅ free + paid |
| Chrome User Experience Report (CrUX) | Field | ✅ BigQuery |

## Crawl budget per JS-heavy

Solutions:
- Pre-render via Vercel/Netlify edge SSR
- Sitemap segmentation per priority (`<priority>` 1.0 head pages)
- robots.txt allow surgical
- Crawl-delay directive (rispetta per non-Googlebot UA)
- Canonical clean (no chain)

## Search Console setup

Mandatory:
- Property added (URL prefix or Domain property)
- DNS verification (TXT record)
- Sitemap submitted
- International targeting (if multi-language)
- Email notifications on (manual action alert)

## Anti-pattern technical

1. **Disallow / global** by mistake — total deindex
2. **Canonical chain** A→B→C
3. **Schema invalid sitewide**
4. **Hreflang reciprocal broken**
5. **Mixed content** HTTP in HTTPS
6. **JS rendering required for content** (CSR no fallback)
7. **Soft 404** (200 status, "not found" content)
8. **Duplicate sitemap entries**
9. **Robots.txt Disallow CSS/JS**
10. **HTTPS not enforced** (mixed http/https)

## Sources

### Primary

- [web.dev — Core Web Vitals](https://web.dev/vitals/)
- [web.dev — INP guide](https://web.dev/articles/inp)
- [web.dev — INP CWV announcement](https://web.dev/blog/inp-cwv-march-12)
- [Google Search Central — JS SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
- [Google Search Central — robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Google Search Central — sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)
- [Google Search Central — hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)

### Secondary

- [Cloudflare Blog — INP](https://blog.cloudflare.com/inp-get-ready-for-the-new-core-web-vital/)
- [Hyperspeed Blog — Core Web Vitals 2026 changes](https://hyperspeed.me/blog/core-web-vitals-2026-what-changed)
- [Nitropack — Most Important CWV 2026](https://nitropack.io/blog/most-important-core-web-vitals-metrics/)
