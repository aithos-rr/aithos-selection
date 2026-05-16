---
name: technical-seo-audit
description: Technical SEO audit completo (Core Web Vitals INP/LCP/CLS, mobile-first, hreflang, sitemap, robots.txt, canonical, internal linking, JS rendering, indexability) con priority issue list + fix recommendation per issue. INP guidance only (field-only metric — non misurabile lab, agent guida user a Search Console/CrUX). Output JSON `{cwv, mobile_ready, https, sitemap_status, robots_status, canonical_issues, hreflang_issues, schema_coverage, indexability_issues, issues_priority_list[]}` con P0/P1/P2 ranking.
when_to_use: Audit baseline pre-strategy, recovery diagnostic post Google Core Update, fix list per dev team handoff, technical regression check post-deploy, due diligence M&A leggera lato SEO
---

# Technical SEO Audit

Skill che esegue technical SEO audit deterministico via on-page parse + sitemap analysis + (optional) Search Console data + PageSpeed Insights API.

## Scope

- **In scope**: Core Web Vitals (INP guidance, LCP/CLS lab via PSI), mobile-first check, HTTPS check, sitemap.xml audit, robots.txt audit, canonical tag audit, hreflang audit, schema coverage detection, internal linking audit, indexability check
- **Out of scope**: log file analysis (richiede server access), competitor technical audit (vedi `content-audit` skill)

## Input contract

```yaml
domain: example.com
sitemap_url: optional, fallback /sitemap.xml
robots_url: optional, fallback /robots.txt
sample_size: 50  # urls to deep-audit, default 50, max 200
search_console_connected: true | false
pagespeed_api_key: optional, env PSI_API_KEY
geo_target: italia  # for hreflang validation
```

## Methodology

### Step 1 — Robots.txt audit

Fetch `<domain>/robots.txt`:
1. Parse User-agent blocks
2. Check Disallow patterns (warn if `Disallow: /` global)
3. **GEO check**: User-agent: GPTBot, ChatGPT-User, PerplexityBot, anthropic-ai → allowed?
4. Sitemap reference present?
5. Crawl-delay directive (rispettare in audit)

Output: `{robots_status: ok|missing|blocking, gpt_allowed, perplexity_allowed, anthropic_allowed, sitemap_referenced}`

### Step 2 — Sitemap audit

Fetch `<sitemap_url>`:
1. Parse XML sitemap (urlset or sitemapindex)
2. Count URL total
3. Check freshness (lastmod older than 6 months suspicious)
4. Validation: <50,000 URL per file, gzipped if large
5. URL list extracted for sample audit

Output: `{sitemap_status: ok|invalid|missing, total_urls, last_mod_summary, gzipped: bool}`

### Step 3 — On-page sample audit

Sample N URL (default 50, stratified random or priority by sitemap priority):
For each URL:
1. Fetch HTML (WebFetch o Playwright se JS-heavy + Q3 hint)
2. Parse via beautifulsoup4 + lxml
3. Extract:
   - `<title>` length (10-60 char ideal)
   - Meta description length (50-160 char)
   - H1 presence + count (1 expected)
   - H2 hierarchy
   - Word count
   - `<link rel="canonical">` presence + value
   - `<link rel="alternate" hreflang>` presence + reciprocal
   - `<script type="application/ld+json">` schema detection
   - `<meta name="robots">` (noindex? nofollow?)
   - Internal link count
   - External link count
   - Image alt presence%

### Step 4 — Core Web Vitals (DECISION-009)

INP è field-only (March 12, 2024 became CWV [primary, web.dev]).

**Strategy**:
1. Se `pagespeed_api_key` present → call PSI API per `lcp` + `cls` (lab metrics) + `inp` (field if CrUX data exists)
2. Se `search_console_connected: true` → guida user a export "Core Web Vitals" report
3. Otherwise → output guidance only:

```text
⚠ INP è metrica field-only — non misurabile via Bash/lab tools.
Per ottenere il valore INP del tuo sito:
1. Vai a Search Console > Core Web Vitals report
2. Filtra per "Mobile" e "Desktop" separati
3. Esporta CSV
4. Re-run audit con --search-console-export <file.csv>

Threshold reference:
- ≤200 ms = good
- 200-500 ms = needs improvement
- >500 ms = poor
Source: https://web.dev/blog/inp-cwv-march-12
```

### Step 5 — Mobile-first check

PageSpeed Insights (se API key):
1. Mobile + Desktop strategy entrambi
2. Mobile responsive: viewport meta tag present?
3. Touch target size (manual flag se UI cluttered)
4. Mobile page speed score

### Step 6 — HTTPS + redirect check

1. Curl `<domain>` → 200/301/302 status
2. `http://<domain>` → must 301 redirect a https
3. Mixed content scan (insecure resource in HTTPS page)

### Step 7 — Hreflang validation

Se `geo_target: multi_paese` o site has `<link rel="alternate" hreflang>`:
1. Extract hreflang declarations from sample URL
2. Check reciprocal pattern (URL A → B + URL B → A)
3. Check `x-default` presence
4. Check valid ISO codes

### Step 8 — Issue priority ranking

Categorize all issues:

| Priority | Criteria | Examples |
|----------|----------|----------|
| **P0 critical** | Blocks indexability or major user impact | Disallow / global, all-page noindex, HTTPS broken, sitemap missing/invalid |
| **P1 high** | Significant SEO impact | INP poor (>500ms), LCP poor (>4s), schema invalid sitewide, hreflang reciprocal broken, canonical contradictory |
| **P2 medium** | Optimization opportunity | INP needs improvement (200-500ms), missing schema where applicable, alt text missing >50% images, internal linking sparse |

## Output JSON schema

```json
{
  "domain": "example.com",
  "audit_date": "2026-05-01",
  "sample_size_audited": 50,
  "data_sources": ["page_fetch", "psi_api", "search_console"],
  "robots_status": "ok",
  "robots_gpt_allowed": true,
  "robots_perplexity_allowed": false,
  "sitemap_status": "ok",
  "sitemap_total_urls": 142,
  "https_status": "ok",
  "mobile_first_score": 78,
  "cwv": {
    "lcp_p75_ms": 2400,
    "lcp_status": "good",
    "inp_p75_ms": null,
    "inp_status": "no_data_field_only",
    "inp_guidance": "...",
    "cls_p75": 0.08,
    "cls_status": "good"
  },
  "schema_coverage_pct": 67,
  "schema_issues": [
    {"url": "...", "issue": "schema_invalid", "detail": "..."}
  ],
  "canonical_issues": [],
  "hreflang_issues": [],
  "indexability_issues": [
    {"url": "...", "issue": "robots_noindex", "intentional": "unknown"}
  ],
  "issues_priority_list": [
    {"priority": "P0", "issue": "...", "fix_recommendation": "...", "effort": "high|medium|low", "impact": "high|medium|low"},
    {"priority": "P1", "issue": "...", "fix_recommendation": "...", "effort": "...", "impact": "..."}
  ]
}
```

## Anti-hallucination contract

- INP value mai inventato. Se no Search Console + no PSI field data → `inp_p75_ms: null` + guidance
- Schema validation rule-based, no LLM hallucination
- Sample size dichiarato (mai claim "site-wide" se sample 50/1000)
- Rate-limit respect (1 req/2s default, parametrico)

## Edge cases

1. **Sito JS-heavy SPA no SSR** → audit limitato (HTML scraped è shell, no content) → suggest Playwright MCP + render check
2. **Cloudflare anti-bot** (403/503 on WebFetch) → fallback PSI API + Search Console only + warning
3. **Sito >10k URL** → stratified random sample 200 max + flag «full audit richiede tool dedicato (Screaming Frog, Ahrefs Site Audit)»
4. **No sitemap accessible** → robots.txt fallback + manual user URL list input
5. **Hreflang con codici invalidi** (es. `it-IT` valid, `it_IT` invalid) → flag + correction
6. **Schema test marker in production** → flag

## Tool integration

| Tool | Use | Free tier |
|------|-----|------------|
| PageSpeed Insights API | LCP/CLS/INP field if CrUX | 25k req/day free |
| Google Search Console | INP + indexability + impressions | Free (own site) |
| Schema.org Validator | Validation external | Free |
| Screaming Frog | Full crawl audit (alternative) | 500 URL free, then £199/yr |
| Ahrefs Site Audit | Full crawl audit (alternative) | Pro plan |

## CLI invocation

```bash
python3 scripts/audit_onpage.py \
  --domain example.com \
  --sample-size 50 \
  --psi-key $PSI_API_KEY \
  --search-console-export sc-cwv.csv \
  --output output/audit-tech.json
```

## Output downstream

Audit JSON → consumed da:
- Main agent Fase 1 → strategy synthesis
- `schema-generator` (fix schema issue list)
- `geo-optimizer` (robots.txt LLM allow check)
- `/document-factory` (PDF technical audit report)

## References

- `references/technical-seo-2026-checklist.md` — full checklist + INP detail + mobile-first + hreflang
- `references/schema-markup-guide-2026.md` — schema validation rules
- `references/seo-best-practices-2026.md` — E-E-A-T signals lato technical

## Examples

### Example 1: SaaS B2B audit

Input: domain=app.example.com, sample 50, PSI API key present.

Output: 3 P0 issue (sitemap missing, mixed content 12 URL, robots disallow staging leak), 5 P1 (schema Article missing 18 page, INP 480ms needs improvement guida user), 8 P2 (alt text 43% images, canonical missing 6 page).

### Example 2: eCommerce decay diagnostic

Input: domain=shop.example.com, sample 100, search_console_connected=true.

Output: INP poor 720ms p75 P0 (root cause: long task in checkout JS), schema Product invalid 80% category page P1, hreflang reciprocal broken IT↔EN P1, breadcrumb missing 100% category page P2. Recovery roadmap fix list ordered.

### Example 3: Content blog no PSI key

Input: domain=blog.example.com, no PSI, no GSC connected.

Output: audit limited (no CWV data), focus on-page parse only. Warning «Per audit completo CWV connetti PSI API + Search Console». Output schema coverage + canonical + sitemap audit complete.
