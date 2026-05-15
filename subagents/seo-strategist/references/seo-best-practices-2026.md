# SEO Best Practices 2026

> Reference doc per `/seo-strategist`. Helpful Content Update + Core Updates 2024-2026 + E-E-A-T criteria + ranking signals + anti-pattern. Ground primary su Google Search Central, secondary su Moz/Ahrefs/Search Engine Land.

## Helpful Content Framework — primary

[Google Search Central](https://developers.google.com/search/docs/fundamentals/creating-helpful-content):

> «Google's automated ranking systems are designed to present helpful, reliable information that's primarily created to benefit people, not to gain search engine rankings»

### Self-assessment questions chiave

Quote primary:

- «Does the content provide original information, reporting, research, or analysis?»
- «Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?»
- «Is this the sort of page you'd want to bookmark, share with a friend, or recommend?»

### "Who, How, Why" Framework

Google ha codificato 3 dimensioni di trasparenza:

- **Who**: bylines visibili, autore identificabile (nome + bio + credentials)
- **How**: disclosure su AI/automation usage + methodology research
- **Why**: «primarily to help people, not manipulate rankings»

### Red flag esplicito

Quote Google primary:

- «producing lots of content on many different topics in hopes that some of it might perform well»
- «extensive automation to produce content on many topics»

→ Translation tattica: NO content farm via AI mass generation. NO topic spread caotico senza expertise.

## E-E-A-T 2026 — primary

4 pillar [Google Search Central]:

1. **Experience** — first-hand knowledge (es. provato il prodotto, visitato il posto)
2. **Expertise** — credentials or demonstrated deep knowledge
3. **Authoritativeness** — recognized authority in topic (citation da peer, awards)
4. **Trustworthiness** — most important. «Trust is most important»

### Signals che fanno trust

- HTTPS + sito secure
- Author bio + credentials + sameAs LinkedIn/Twitter/etc
- About page + contact info
- Editorial process disclosed
- Citation a fonti autorevoli
- Update timestamp visible
- No deceptive design (popups, dark pattern, hidden CTA)

## Core Updates timeline 2024-2026

[Source: Search Engine Land update tracker, official Google announcements]:

- **March 2024 Core Update** — focused su content quality, downranking AI mass content
- **August 2024 Core Update** — independent publisher boost
- **November 2024 Core Update** — site reputation abuse policy enforcement
- **March 2025 Core Update** — Helpful Content fully integrated in core (no longer separate update)
- **August 2025 Core Update** — AI Overview rollout impact assessment
- **March 2026 Core Update** — «re-weighted Information Gain signal» (secondary, almcorp.com)

→ Pattern: Google sposta peso da "match keyword" a "answer well + add new info".

## Information Gain — emergent signal

[secondary, [almcorp.com](https://almcorp.com/blog/google-march-2026-core-update-complete/)]:

> «a ranking signal that measures how much genuinely new knowledge a piece of content adds relative to what already ranks for the same query»

Translation tattica:
- Original research, proprietary data, first-hand testing → boost
- Re-hash di top 10 articoli ranking → penalty
- Insight unique, expertise rare → opportunity

## Topical authority

[secondary, multi-source]:

> «A website covering SEO consistently will rank better for SEO-related topics than a general blog occasionally posting about SEO»

Translation tattica:
- Niche depth > breadth random
- Pillar+cluster strategy enforce topical authority signal
- Author specialization (1 author = topical expert per cluster)

## Search intent classification

| Intent | Signal | Strategy |
|--------|--------|----------|
| Informational | "how to", "what is", "guide" | Content depth, schema Article |
| Navigational | brand+name | Brand SERP optimization, schema Organization |
| Transactional | "buy", "trial", "discount" | Landing page conversion-focused, schema Product |
| Commercial investigation | "best X for Y", "X vs Y" | Listicle + comparison content + schema |

## Long-tail strategy post AI Overview

AI Overview ha eroso traffic head informational. Pivot:
- 4+ word query (specifici, AI Overview spesso non triggherato)
- Brand + use-case ("[product] for [persona]")
- Local intent ("near me", "[city] [service]")
- Question-format ("come usare X per Y")

## Mobile-first

- Definitivo since 2020
- Mobile UX pari priority desktop
- Touch target size, readable font, no intrusive interstitial
- Mobile responsive viewport meta tag mandatory

## Page speed

CWV thresholds 2026 [primary, web.dev]:

| Metric | Good | Needs improvement | Poor |
|--------|------|---------------------|------|
| LCP | ≤2.5s | 2.5-4.0s | >4.0s |
| INP | ≤200ms | 200-500ms | >500ms |
| CLS | ≤0.1 | 0.1-0.25 | >0.25 |

INP became CWV March 12, 2024 [primary, web.dev]. INP è field-only — measure via CrUX, Search Console.

## Internal linking

Best practice 2026:
- 3-5 contextual link per page
- Anchor varied (no exact-match repetition)
- Topic cluster cross-linking aggressive
- Pillar ↔ supporting reciprocal
- No sitewide footer link spam

## Image optimization

- WebP/AVIF format
- Lazy loading native (`loading="lazy"`)
- `alt` text descriptive (no keyword stuffing)
- Responsive sizes via `srcset`
- CDN delivery preferred

## URL structure

- Short, readable, keyword-relevant
- Hyphens not underscores
- Lowercase only
- No session ID o tracking parameter visible
- Permanent URL (no breaking changes post-publication)

## Anti-pattern critici 2026

[multi-source, secondary]:

1. **AI mass content** — Helpful Content red flag, Google penalty risk
2. **Keyword stuffing** — over-optimization signal
3. **Exact-match anchor abuse** — 70%+ exact-match = unnatural pattern
4. **Cloaking** — manual action risk
5. **Doorway pages** — penalty
6. **Hidden text** — penalty
7. **Link schemes** — paid links, link exchange, PBN (vedi `seo-strategist` anti-pattern)
8. **Boilerplate >70%** — programmatic SEO red flag
9. **Schema markup invalid** — no rich result + warning Search Console
10. **Thin content** — pages <300 word con minimal value

## Rank tracking 2026

Tools:
- Search Console (own data, free)
- Ahrefs Rank Tracker (Pro plan)
- SEMrush Position Tracking
- SE Ranking
- AccuRanker (dedicated)

Cadenza: weekly per top 100 keyword, monthly review trend.

## Sources

### Primary

- [Google Search Central — Helpful Content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search Central — E-E-A-T Quality Rater Guidelines](https://services.google.com/fh/files/misc/hsw-sqrg.pdf)
- [web.dev — Core Web Vitals](https://web.dev/vitals/)

### Secondary

- [Moz — Algorithm Update History](https://moz.com/google-algorithm-change)
- [Search Engine Land — SEO News](https://searchengineland.com/library/seo)
- [Ahrefs Blog](https://ahrefs.com/blog)
- [evertune.ai — March 2026 Core Update](https://www.evertune.ai/resources/insights-on-ai/googles-march-2026-core-update-a-content-best-practices-guide-for-seo-and-ai-search)
- [almcorp.com — Information Gain analysis](https://almcorp.com/blog/google-march-2026-core-update-complete/)
- [orbitinfotech.com — Helpful Content guide 2026](https://orbitinfotech.com/blog/google-2026-helpful-content-update/)
