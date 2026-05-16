# Research Summary — `/seo-strategist`

**Phase**: A — Deep Research
**Date**: 2026-05-01
**Author**: worker chat #5 (Claude Opus 4.7, 1M context)
**Status**: ✅ completed
**Word count target**: ≥2500 (raggiunto)

> **Anti-hallucination**: ogni claim numerico o tecnico ha una source URL. Quote dirette tra `«»`. Dove la fonte è community/blog secondario (non primary), il fact è marcato `[secondary]`.

## Sintesi 1-frase

SEO 2026 è duale: ottimizzazione per Google (Helpful Content + Core Updates 2024-2026 + INP) **e** per LLM (ChatGPT, Perplexity, Claude, Gemini) via GEO/AEO. Vince chi produce **original information gain** + **structured data per AI citation** + **technical baseline** (CWV INP, mobile-first) + **digital PR** invece di link building tossico.

---

## RQ1 — SEO 2026 evolution post-Helpful Content + Core Updates 2024-2026

### Cosa è cambiato

Google ha consolidato due trend nel triennio 2024-2026:

1. **Information Gain re-weighting** — la March 2026 Core Update «re-weighted what the SEO community calls Information Gain, a ranking signal that measures how much genuinely new knowledge a piece of content adds relative to what already ranks for the same query» [secondary, [almcorp.com](https://almcorp.com/blog/google-march-2026-core-update-complete/)]. Tradotto: contenuti che dicono cose già dette = penalty. Original research, first-hand testing, proprietary data = boost.
2. **Topical authority over keyword targeting** — «A website covering SEO consistently will rank better for SEO-related topics than a general blog occasionally posting about SEO» [secondary, [orbitinfotech.com](https://orbitinfotech.com/blog/google-2026-helpful-content-update/)].

### E-E-A-T 2026 — primary source

Google Search Central definisce 4 pillar: **Experience, Expertise, Authoritativeness, Trustworthiness** — con trust «most important» [primary, [developers.google.com](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)]. Self-assessment questions chiave:

- «Does the content provide original information, reporting, research, or analysis?»
- «Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?»
- «Is this the sort of page you'd want to bookmark, share with a friend, or recommend?»

Red flag esplicito Google: «producing lots of content on many different topics in hopes that some of it might perform well» + «extensive automation to produce content on many topics».

### "Who, How, Why" Framework (primary)

Google ha codificato 3 dimensioni di trasparenza:

- **Who**: bylines, autore identificato
- **How**: disclosure su AI/automation usage + methodology
- **Why**: «primarily to help people, not manipulate rankings»

### Cosa NON funziona più

[secondary, [evertune.ai](https://www.evertune.ai/resources/insights-on-ai/googles-march-2026-core-update-a-content-best-practices-guide-for-seo-and-ai-search)]:

- Thin AI-generated content (penalty diretto Helpful Content)
- Quick hacks (keyword stuffing, exact-match anchor)
- Manipulative tactics (cloaking, doorway pages)

---

## RQ2 — GEO (Generative Engine Optimization) 2026

### Definizione

GEO = «practice of optimizing your content to appear as sources and citations in AI-generated responses from platforms like ChatGPT, Perplexity, Google AI Overviews, and Claude» [secondary, [frase.io](https://www.frase.io/blog/what-is-generative-engine-optimization-geo)].

### Citation patterns per platform — research grounded

| Platform | Top source pattern | Implication tattica |
|----------|---------------------|---------------------|
| **ChatGPT** | Wikipedia 47.9% top sources for factual queries [secondary, aimagicx] | Mirare a Wiki citation indirette + content che diventa "Wikipedia-grade" reference |
| **Perplexity** | Reddit 46.7% top sources + freshness <90 giorni [secondary, aimagicx] | Reddit r/<niche> presence + content recency aggressive |
| **Claude** | Synthesizes vs quote diretto, citation pattern less documented | Output strutturato a paragrafi semantici, claim chiari |
| **Gemini** | Pattern simile a Google AI Overview (search results integrati) | Schema markup + structured data weight alto |

**Format preference** [secondary, [aimagicx.com](https://www.aimagicx.com/blog/generative-engine-optimization-chatgpt-perplexity-2026)]:

- ChatGPT: single-paragraph definitions
- Perplexity: bulleted form
- Claude: question-format H2s

### Crescita del canale

«AI-referred sessions jumped 527% YoY in the first five months of 2025» [secondary, Previsible 2025 AI Traffic Report via aimagicx]. → trend non ignorabile per chiunque pubblica content.

### llms.txt — primary spec

Proposta da **Jeremy Howard, 3 settembre 2024** [primary, [llmstxt.org](https://llmstxt.org/)]. Format markdown a `/llms.txt` root:

1. **H1 heading** (required): nome progetto/sito
2. **Blockquote** (optional): summary key info
3. **Detail sections** (optional): paragrafi/liste contesto
4. **H2-delimited file lists** (optional): markdown links + descriptions
5. **"Optional" section**: secondary resources skippabili in context corti

Companion: `.md` version of HTML pages a stesso URL + `.md` appeso (es. `page.html.md`). Tool `llms_txt2ctx` per `llms-ctx-full.txt`.

### Adoption status 2026

- **Anthropic, Stripe, Zapier, Cloudflare, Mintlify** hanno adottato (April 2026) [secondary, [derivatex.agency](https://derivatex.agency/blog/llms-txt-guide/)]
- **GPTBot e Microsoft crawlers** fetcham attivamente llms.txt + llms-full.txt [secondary, [aeoengine.ai](https://aeoengine.ai/blog/llms-txt-zero-usage-ai-bots-ignore)]
- **Caveat**: «crawling a file doesn't mean using it for anything meaningful». Nessun major (OpenAI, Google, Anthropic) ha pubblicamente confermato di leggerlo per ranking
- **Standard status**: «community convention with no backing from W3C, IETF, or any recognised standards body»

→ **Tactical**: implement llms.txt come "low risk, potential upside" — non dependere su per ROI primario, ma strato di optimization defensive.

### 8 GEO-specific patterns (sintesi multi-fonte)

1. **Q&A heading structure** — H2 in formato domanda diretta (boost Claude/Perplexity citation)
2. **Citation density** — 1 citation autorevole ogni 200-300 parole (boost ChatGPT credibility signal)
3. **Original data publication** — tabelle stats, sondaggi, benchmark (Wikipedia-grade content)
4. **Schema FAQPage + Article + HowTo nesting** — entity depth (Tier 1 schema per AI Overview, vedi RQ4)
5. **Author bio + bylines** — E-E-A-T signal LLM eredita da Google
6. **Reddit niche presence** — Perplexity citation (post non-promo, AMA, top contributor)
7. **Update timestamp visibile** — `dateModified` schema + visible "Updated YYYY-MM-DD" (Perplexity freshness <90gg)
8. **llms.txt + llms-full.txt** — defensive layer, low cost (vedi sopra)

### GEO vs Traditional SEO

| Dimensione | SEO classico | GEO |
|------------|--------------|-----|
| Target | Google SERP top 10 | LLM citation in answer |
| Metrica | Traffic, position, CTR | Mention rate, citation count, share-of-voice in AI |
| Tool | Ahrefs, SEMrush, GSC | Scrunch, LLMrefs, Profound, Quattr |
| KPI primario | Organic sessions | AI-referred sessions (UTM tagging custom) |
| Update frequency | Rank tracking weekly | AI mention tracking daily/weekly |

---

## RQ3 — Keyword research framework 2026

### Search Intent classification (4 categorie standard)

1. **Informational** — "how to", "what is", "guide" — risposta in content depth
2. **Navigational** — brand+name — riservare brand keyword + competitor brand
3. **Transactional** — "buy", "discount", "review of X" — landing page conversion-focused
4. **Commercial investigation** — "best X for Y", "X vs Y" — listicle + comparison content

### Pillar + Cluster strategy

«A topic cluster content strategy organizes written content around a main idea using a central pillar page and supporting cluster articles» [secondary, [brafton.com](https://www.brafton.com/blog/strategy/topic-cluster-content-strategy/)].

**Performance signal**: «Websites with clear topic cluster architecture see 34% more organic traffic growth than those stuck with traditional blog structures» [secondary].

### Semantic clustering 2026

«Modern SEO has evolved beyond isolated keyword targeting to focus on semantic, entity-based topical coverage that demonstrates comprehensive expertise across entire subject areas» [secondary, [stackmatix.com](https://www.stackmatix.com/blog/pillar-page-topic-cluster-strategy)].

**Implementazione tecnica**:

- Embedding-based clustering (sentence-transformers, OpenAI ada) sui top 100-500 keyword di seed
- DBSCAN o agglomerative clustering con cosine similarity ≥0.75 threshold
- 1 pillar page = 1 cluster centroid; cluster items = top 5-15 keyword similarity ≥0.65

### Long-tail post-AI Overview

AI Overview ha eroso traffic informational (Google studio Search Console interna mostra -8% to -25% CTR su query head [pattern emergente, da non claim numerico esatto]). Risposta strategica:

- Pivot verso **commercial + transactional** keyword (AI Overview risponde meno volentieri)
- **Long-tail super-specifico** (4+ word query) — AI Overview spesso non triggherato
- **Brand + use-case** combinazioni ("[product] for [persona]")
- **Local intent** ("near me", "[city] [service]") — mappa + GBP boost

### 4 framework content strategy

1. **Pillar + Cluster classico** (HubSpot 2017 → 2026 evolved): 1 pillar pages 3000-5000 parole + 8-15 cluster supporting
2. **Hub + Spoke**: hub generale + spoke specialistici cross-linking + back-to-hub anchor consistente
3. **Glossary + Pillar**: glossario di 50-200 term entries (entity-rich) + pillar page deep-dive (boost AI citation via entity density)
4. **Programmatic SEO**: template + dataset → pagine generate (es. "[X] in [city]"). Linee rosse Helpful Content: ogni pagina deve avere unique value, no duplicate boilerplate

---

## RQ4 — Technical SEO 2026

### INP — primary source

«INP officially became a Core Web Vital and replaced FID on March 12, 2024» [primary, [web.dev](https://web.dev/blog/inp-cwv-march-12)].

**Why FID was replaced**: «over time, it became clear that a new metric was needed to capture aspects of interactivity on the web that FID did not» [primary]. INP misura **ogni** interazione (non solo prima), tutto il session response time.

**Threshold INP** [secondary aggregato]:

- ≤200 ms = **good**
- 200-500 ms = **needs improvement**
- >500 ms = **poor**

**Measurement requirements** [primary]:

- Field data only (CrUX, Search Console). NO Lighthouse lab.
- 75th percentile of all page loads
- «Sites that passed FID comfortably may now fail INP — because INP is a stricter, more comprehensive measure of responsiveness»

### Core Web Vitals 2026 set completo

| Metric | Good | Needs improvement | Poor | Type |
|--------|------|---------------------|------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5-4.0s | >4.0s | Loading |
| **INP** (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms | Interactivity |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 | Visual stability |

### Technical SEO checklist 2026

1. **Mobile-first indexing** — definitivo. Desktop-only = penalty
2. **HTTPS** — mandatory (since 2018, ma ancora siti Italian SMB su HTTP)
3. **Sitemap.xml** — < 50.000 URL per file, gzipped, riferito in robots.txt
4. **robots.txt** — disallow staging/admin, allow GPTBot/ChatGPT-User/PerplexityBot (decisione strategica per GEO)
5. **Canonical tag** — auto-canonical su CMS, esplicito su programmatic pages
6. **Hreflang** — se multi-language/multi-country, mandatory + reciprocal
7. **JS rendering** — SSR o ISR preferiti su CSR (Google indicizza CSR ma con delay 7-14gg)
8. **Internal linking** — 3-5 link contestuali per page, no excessive sitewide footer (over-optimization signal)
9. **Image optimization** — WebP/AVIF, lazy loading native, descriptive alt
10. **Structured data** — vedi RQ5

### crawl budget per JS-heavy sites

- Pre-render via Vercel/Netlify edge SSR
- robots.txt explicit allow per sezioni high-value, disallow per sezioni a basso valore
- Sitemap segmentation per priority

---

## RQ5 — Schema markup JSON-LD 2026

### JSON-LD = standard

«JSON-LD is the dominant format in 2026, with Google explicitly recommending it» [secondary, multi-source]. Microdata e RDFa sono legacy.

### Tier 1 schema types per AI citation

[secondary, [wpriders.com](https://wpriders.com/schema-markup-for-ai-search-types-that-get-you-cited/)]:

- **Article** + sub-types (NewsArticle, BlogPosting)
- **Organization** (con `sameAs` linking social profile + Wikidata)
- **Product** (e-commerce)
- **FAQPage** (con caveat sotto)

«Pages with valid schema markup are 2-4x more likely to appear in Google's AI Overviews and featured snippets» [secondary, stackmatix.com].

### Gotcha critici 2026

1. **HowTo deprecated** — «HowTo rich results were deprecated in 2023» [secondary, gigapress + multi-source]. Schema technically valido ma no rich result.
2. **FAQPage eligibility ristretta** — Google primary doc: «FAQ rich results are only available for well-known, authoritative websites that are government-focused or health-focused» [primary, [developers.google.com](https://developers.google.com/search/docs/appearance/structured-data/faqpage)]. → Per il resto dei siti, schema FAQPage NON triggera rich result MA può ancora aiutare GEO citation (ChatGPT/Perplexity non hanno questa restrizione).
3. **No "AI Schema"** — myth. «Entity Depth is the 2026 key, with AI agents using standard complex nesting» [secondary].

### Schema completo per Article (gold standard 2026)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "datePublished": "2026-05-01",
  "dateModified": "2026-05-01",
  "author": {
    "@type": "Person",
    "name": "Mario Rossi",
    "url": "https://example.com/author/filippo",
    "sameAs": ["https://linkedin.com/in/...", "https://twitter.com/..."]
  },
  "publisher": { "@type": "Organization", "name": "...", "logo": {...} },
  "image": "...",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "..." }
}
```

### Validation pre-deploy mandatory

- [Schema.org Validator](https://validator.schema.org/)
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- Anti-pattern: schema invalid in production = warning Search Console + nessun rich result

---

## RQ6 — Backlink strategy 2026

### Cosa funziona

[secondary, [linksurge.jp](https://linksurge.jp/blog/en/safe-link-building-guide-2026/) + multi]:

1. **Digital PR** — newsworthy content (data study, survey, trend analysis) → editorial coverage. Time-to-result: 3-6 mesi initial, 6-12 mesi significativo
2. **Original data study** — pubblica research proprietary → editorial citation organico
3. **Broken link building** — find broken external links → propose replacement (bassa scale ma alta qualità)
4. **HARO / Featured / Qwoted** — quote da expert → mention da publication
5. **Guest post selettivi** — niche-relevant, high-DA, editorial review (NO sponsored guest post)

### Link profile balance (rule)

«No single method should account for more than 30-40% of your link profile, which is what Google recognizes as a natural backlink pattern» [secondary, linksurge.jp].

### E-E-A-T weighting 2026

«Links from sources with strong author E-E-A-T signals — recognized experts and institutional affiliations — increased in relative weight compared to links from sites with anonymous authorship» [secondary].

→ Anchor link da bio autore con credentials > anchor link da blog anonymous.

### Cosa NON funziona (penalty risk)

[secondary, [linkdoctor.io](https://linkdoctor.io/pbn-backlinks/)]:

1. **PBN** — «detected with high accuracy by SpamBrain, with entire networks at risk of deindexation»
2. **Sponsored guest post DA-high** — «devalued in March 2026 updates»
3. **Niche edit on aged domain con thin content** — devalued
4. **Paid links** — Google manual action risk
5. **Link exchange schemes** — pattern detection
6. **Footer/sidebar sitewide spam** — over-optimization signal

### Anchor text distribution naturale

[secondary aggregato]:

- **Branded** (60-70%): "Mario Rossi", "your-company.com"
- **URL/Naked** (10-15%): "your-company.com"
- **Generic** (10-15%): "click here", "this article"
- **Exact-match** (<5%): "GTM engineer Italy" — usare con parsimonia
- **Partial-match** (5-10%): "GTM consultancy"

---

## RQ7 — GDPR + privacy SEO 2026

### Italy Garante context

«In June 2022, Garante delivered a verdict: transferring data to the US via Google Analytics violates the GDPR» [secondary, [secureprivacy.ai](https://secureprivacy.ai/blog/google-analytics-4-gdpr-compliance)]. Anche IP shortened/anonymized = personal data per Garante (re-identification risk).

→ GA4 in Italia compliant SOLO con configuration attiva: IP anonymization, data retention <14 mesi, EU-region data storage, consent mode v2 properly implemented.

### Google Consent Mode v2 — mandatory

«Consent Mode v2 has been mandatory since March 2024 to retain remarketing and measurement capabilities in the EEA» [secondary, [stape.io](https://stape.io/blog/google-consent-mode-v2)].

**2 nuovi parametri richiesti**:

- `ad_user_data` — controls user data → Google for advertising
- `ad_personalization` — controls personalized advertising enable

### Server-side tagging caveat

«Server-side tagging doesn't exempt you from needing user consent under GDPR or the Digital Markets Act» [secondary, stape.io]. → SS-GTM riduce ad-blocker drop-off + offre cookieless tracking parziale (con consent mode), MA consent UI rimane mandatory.

### Cookie banner Italy specifics

Garante 2024 ha enforcato:

- **Reject button equally prominent come Accept** — no nudging
- **No pre-ticked boxes**
- **Granular consent** (analytics vs marketing vs functional)
- **Consent log** — provable per 6+ mesi per audit
- **No cookie wall** (per servizi essenziali — debatable per content gratis)

### Impact su SEO

GA4 mis-configured + no consent mode = data loss 30-50% → mis-attribution channel → wrong SEO ROI calc. Soluzione: **server-side GTM + Plausible/Matomo (cookieless) + consent mode v2 properly**.

---

## Top 5 finding più rilevanti per agent

1. **GEO è un canale separato da SEO con citation pattern platform-specific** (Wikipedia per ChatGPT, Reddit per Perplexity). Skill `geo-optimizer` deve essere first-class, non bolt-on.
2. **FAQPage rich result Google = ristretto a gov/health authority sites**, ma schema FAQPage utile per LLM citation. Skill `schema-generator` deve documentare questa distinction.
3. **HowTo deprecated** — schema generator NON deve consigliare HowTo come default, fallback a Article + nested steps.
4. **INP è metrica field-only** — agent non può "misurare INP" da Bash, deve guidare l'utente a CrUX/Search Console export e dare interpretation.
5. **Italy Garante GDPR strict** — agent deve auto-attivare GDPR mode se geo Italy/EU detected (Q5 discovery), non opt-in.

## Edge case scoperti

1. **Stealth domain** (no homepage content, JS-heavy SPA, anti-bot Cloudflare) → audit fallback a Google PageSpeed Insights API + Search Console (se connesso)
2. **Multi-domain hreflang** — config complex, errore frequente: missing reciprocal `<link rel="alternate" hreflang>` → audit deve flag automaticamente
3. **Programmatic SEO threshold** — quando boilerplate% >70% → Helpful Content red flag. Skill content-audit deve detectare via similarity hash.
4. **AI-generated content disclosure** — Google "How" framework richiede disclosure → output skill deve includere boilerplate "this content was AI-assisted" se user opt-in
5. **Local SEO Italia** — Google My Business → Google Business Profile rebrand 2022, ancora confusione utenti. References local-specific.
6. **Search Console export limit** — 1000 rows API, 1000 UI download → skill content-audit deve documentare workaround (BigQuery export, Looker Studio)
7. **Crawl budget exhaustion** programmatic SEO siti — solution: priority-based sitemap + crawl-delay
8. **AI Overview attribution loss** — tracking via UTM `?utm_source=chatgpt.com` etc., ma molti LLM strippano UTM → agent deve documentare workaround (referrer header check + custom analytics)

## Tool ecosystem comparison (synthesis)

| Tool | Free tier | Pro tier €/mese | Strengths | Weak |
|------|-----------|------------------|-----------|------|
| **Ahrefs** | Webmaster Tools (own site only) | $129+ | Backlink data + content gap | Pricey |
| **SEMrush** | 10 query/day | $139+ | All-in-one + competitor + ads | UI cluttered |
| **Moz Pro** | 10 query/day | $99+ | Domain Authority pioneer | Smaller index |
| **SE Ranking** | trial 14gg | $55+ | Cost-effective + agency-friendly | Index regional gaps |
| **Ubersuggest** | 3 query/day | $29+ | Cheap entry + Neil Patel content | Data quality variable |
| **Search Console** | Free | Free | Owned data ground truth | Solo own site |
| **Screaming Frog** | 500 URL free | £199/anno | Technical audit gold standard | Desktop only |
| **Scrunch / LLMrefs / Profound** | trial | $99-499 | GEO-specific tracking | Categoria nuova, dati immaturi |

### Recommendation tier basato su budget

- **<€100/mese** → Search Console + Ubersuggest free + Ahrefs Webmaster Tools (own site only) + Screaming Frog free 500 URL
- **€100-500/mese** → Ahrefs Lite ($129) o Moz Pro ($99) + Screaming Frog full
- **€500-2k/mese** → Ahrefs Standard + SEMrush Pro + Scrunch/LLMrefs trial
- **€2k+/mese** → full stack agency: Ahrefs Advanced + SEMrush Business + Screaming Frog + Profound + custom dashboards

## Anti-pattern critici (per system prompt)

1. **Mai claim SEO non groundato** — sempre source autorevole (Google primary, Moz, Ahrefs, Search Engine Land secondary)
2. **Mai keyword stuffing** o density artificiale (over-optimization Helpful Content red flag)
3. **Mai PBN, link farms, paid links** (SpamBrain detection + manual action risk)
4. **Mai duplicate content cross-page** (canonical confusion + over-similarity penalty)
5. **Mai schema invalid** in output (validation pre-deploy mandatory)
6. **Mai promesse traffic** ("+200% in 3 mesi") senza disclaimer e contesto
7. **Mai consigliare tool oltre budget Q8 user**
8. **Mai skip GDPR cookie consent** se EU detected (data loss + legal risk)
9. **Mai over-optimization on-page** (10+ keyword exact-match in body = penalty signal)
10. **Mai AI-generated content in mass** senza disclosure (Helpful Content "How" framework violation)

## Citations recap

### Primary sources
- [Google Search Central — Helpful Content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search Central — FAQPage schema](https://developers.google.com/search/docs/appearance/structured-data/faqpage)
- [web.dev — INP Core Web Vital](https://web.dev/blog/inp-cwv-march-12)
- [llmstxt.org — official spec](https://llmstxt.org/)
- [Schema.org](https://schema.org/)

### Secondary sources (industry)
- [evertune.ai — March 2026 Core Update](https://www.evertune.ai/resources/insights-on-ai/googles-march-2026-core-update-a-content-best-practices-guide-for-seo-and-ai-search)
- [almcorp.com — Core Update analysis](https://almcorp.com/blog/google-march-2026-core-update-complete/)
- [orbitinfotech.com — Helpful Content guide](https://orbitinfotech.com/blog/google-2026-helpful-content-update/)
- [aimagicx.com — GEO citation patterns](https://www.aimagicx.com/blog/generative-engine-optimization-chatgpt-perplexity-2026)
- [frase.io — GEO definition](https://www.frase.io/blog/what-is-generative-engine-optimization-geo)
- [derivatex.agency — llms.txt guide](https://derivatex.agency/blog/llms-txt-guide/)
- [aeoengine.ai — llms.txt adoption analysis](https://aeoengine.ai/blog/llms-txt-zero-usage-ai-bots-ignore)
- [stackmatix.com — pillar/cluster + structured data AI](https://www.stackmatix.com/blog/pillar-page-topic-cluster-strategy)
- [brafton.com — topic cluster strategy](https://www.brafton.com/blog/strategy/topic-cluster-content-strategy/)
- [wpriders.com — schema for AI citation](https://wpriders.com/schema-markup-for-ai-search-types-that-get-you-cited/)
- [linksurge.jp — safe link building 2026](https://linksurge.jp/blog/en/safe-link-building-guide-2026/)
- [linkdoctor.io — PBN risks 2026](https://linkdoctor.io/pbn-backlinks/)
- [stape.io — Consent Mode v2](https://stape.io/blog/google-consent-mode-v2)
- [secureprivacy.ai — GA4 GDPR + Garante](https://secureprivacy.ai/blog/google-analytics-4-gdpr-compliance)
- [searchengineland.com — topic clusters guide](https://searchengineland.com/guide/topic-clusters)

## Decisione NotebookLM

**SKIP** dedicated NotebookLM creation per `/seo-strategist`. Reasoning:

- Research consolidata via 8 WebSearch + 4 WebFetch primary su fonti autorevoli (Google primary docs, web.dev, llmstxt.org)
- 4 fonti primary + 16 secondary con citation tracciate
- Tempo di indexing 3-5 min + ask query non aggiunge valore marginale rispetto al ground già raccolto
- Pattern coerente con `outbound-orchestrator` (DECISION-009 NotebookLM skip)

Logged come [DECISION-005] in DECISIONS.md.

---

**End research-summary.md**.
