# ARCHITECTURE — `/seo-strategist`

> Documento riferimento per architettura interna agent. Letto in Phase B per design + Phase C per build coerente. Source-of-truth per data flow + skill orchestration + config schema.

## 1. Vision e scope

`/seo-strategist` trasforma:

- **Input**: dominio + obiettivi business
- **Output**: strategia SEO+GEO 2026 actionable (audit findings + keyword cluster + content plan + schema markup + technical fix list + tracking plan)

**NON è**:
- Lead enricher (vedi `/lead-finder-pro`)
- Competitor-only analyzer (vedi `/competitor-deep-dive`, anche se cross-uso possibile)
- Content generator (genera brief, NOT 5000-word article)
- Outbound orchestrator (vedi `/outbound-orchestrator`)

## 2. Pipeline 6-fase

```
Discovery (first run only) → Audit → Research → Strategy → Content Plan → Technical Fix → Reporting
                                ↑                                                          |
                                └──────────────── feedback loop (90gg refresh) ────────────┘
```

### Fase 1 — Audit (skill `technical-seo-audit`)

Input: domain + sitemap + (optional) Search Console connected
Output:
- Tech baseline JSON: `{cwv: {lcp, inp_field, cls}, mobile_ready, https, sitemap_status, robots_status, canonical_issues, hreflang_issues, schema_coverage, indexability_issues}`
- Priority list: P0/P1/P2 issues con fix recommendation

### Fase 2 — Research (skill `keyword-research`)

Input: seed keyword + ICP + geo + competitor (optional)
Output:
- Cluster JSON: `{pillar_keywords[], cluster_topics{topic: [supporting_kw...]}, intent_label, search_volume, difficulty, opportunity_score}`
- Long-tail list (4+ word, AI Overview safe)

### Fase 3 — Strategy

Synthesizes Audit + Research → strategic plan markdown:
- Pillar+cluster mapping
- 90-day priority roadmap
- Quick-win list (effort/impact matrix)
- GEO layer (if Q6 ≠ skip)

### Fase 4 — Content Plan (skill `content-audit`)

Input: existing content + cluster mapping + competitor gap
Output:
- Content audit findings (decay, refresh, gap)
- Content brief generation per piece pianificato
- Refresh priority queue

### Fase 5 — Technical Fix

Output schema markup (skill `schema-generator`) + technical issue resolution detail per priority list.

### Fase 6 — Reporting

Output strutturato:
- Executive summary 1-page
- Detailed findings markdown
- KPI tracking plan (4-week, 12-week, 24-week)
- Tool config recommendation (basato Q8 budget)

## 3. Skill orchestration

| Skill | When invoked | Input source | Output destination |
|-------|--------------|--------------|---------------------|
| `keyword-research` | Fase 2 + on-demand | seed kw + Q1+Q3+Q5 | cluster JSON → Fase 3 |
| `content-audit` | Fase 4 + 90gg refresh | domain + competitor + GSC | gap matrix → strategy doc |
| `geo-optimizer` | Fase 5 (gated by Q6) | content piece URL + topic | llms.txt + schema FAQ + GEO score |
| `schema-generator` | Fase 5 | page metadata + page type | JSON-LD validated |
| `technical-seo-audit` | Fase 1 + on-demand | domain + sitemap | priority issue JSON |

### Conditional loading

- Q6=`skip` → skip `geo-optimizer` totalmente
- Q6=`secondary` → load `geo-optimizer` solo per top pillar pages
- Q6=`priority` → load `geo-optimizer` per ogni content piece

- Q8=`lt100` + Q4=`greenfield` → focus solo skill `keyword-research` + `technical-seo-audit` (skip content-audit fino a quando contenuto esiste)

## 4. MCP detection + fallback

Script `mcp_detect.py` esegue check disponibilità MCP:

| MCP | Required for | Fallback if missing |
|-----|--------------|----------------------|
| `parallel-cli` | SERP scraping + competitor enrichment + deep research | WebSearch + WebFetch chain |
| `playwright` | JS-heavy site rendering check + screenshot audit | Bash + curl + python readability parser |
| `apify` | SERP scraping + Ahrefs alternative bulk | Manual user export da Ahrefs UI |
| `google-personal` | Search Console data export + Google Doc/Sheet output | Markdown locale |
| `context7` | SEO library docs lookup | WebFetch fallback |

Output `mcp_detect.py` → JSON `{mcp_available: {...}, fallback_active: {...}}` → caricato in config session-only (NOT persisted in `config.md`, refresh ogni run).

## 5. Data flow

```
[user input: "audit example.com"]
        |
        v
[discovery check] → exists? yes → reprime config / no → run questions
        |
        v
[mcp_detect.py] → JSON capability matrix
        |
        v
[validate_input.py] → domain valid? sitemap reachable? robots.txt readable?
        |
        v
[skill: technical-seo-audit] → Fase 1 → audit.json
        |
        v
[skill: keyword-research] → Fase 2 → cluster.json
        |
        v
[strategy synthesis] → strategy.md (markdown deterministic)
        |
        v
[skill: content-audit] → Fase 4 → content-plan.md (gated by Q4 stage)
        |
        v
[skill: schema-generator + geo-optimizer] → Fase 5 → fix-list.md + schema.json
        |
        v
[reporting] → final report markdown + executive summary
```

## 6. Config schema (`<memory>/config.md`)

```yaml
---
agent: seo-strategist
created: 2026-MM-DD
schema_version: 1
last_run: 2026-MM-DD
---

user:
  role: founder | marketing_manager | seo_specialist | content_strategist | agency

stack:
  seo_primary: ahrefs | semrush | moz | se_ranking | search_console_only | none
  search_console_connected: true | false
  analytics: ga4 | matomo | plausible | none
  cms: wordpress | webflow | shopify | nextjs | astro | other

site:
  domain: example.com
  type: saas_b2b | ecommerce | content_blog | local | agency
  stage: greenfield | decay | plateau | scaling

geo:
  target: italia | europa | usa | worldwide | multi_paese
  hreflang_required: true | false
  geo_eu_detected: true | false  # auto-derived from target

strategy:
  geo_llm_optimization: priority | secondary | skip
  content_volume: lt5 | 5_15 | 15_50 | 50plus
  pillar_cluster_strategy: true | false  # auto-true unless content_volume=lt5

budget:
  tool_monthly: lt100 | 100_500 | 500_2k | 2kplus
  recommended_stack: []  # populated based on tier

mcp_available: { parallel-cli: bool, playwright: bool, apify: bool, google-personal: bool, context7: bool }
mcp_fallbacks_active: { ... }

api_keys:
  ahrefs_present: false  # env AHREFS_API_KEY
  semrush_present: false  # env SEMRUSH_API_KEY
  pagespeed_insights_present: false  # env PSI_API_KEY (free 25k req/day)
```

## 7. References docs

7 file in `references/`:

1. `seo-best-practices-2026.md` — Helpful Content + Core Updates 2024-2026, E-E-A-T, ranking signals
2. `geo-generative-engine-optimization-2026.md` — LLM citation patterns + llms.txt + 8 GEO patterns
3. `keyword-research-frameworks-2026.md` — pillar+cluster, search intent, semantic clustering, long-tail
4. `schema-markup-guide-2026.md` — JSON-LD per page type, validation, gotcha (HowTo, FAQPage)
5. `technical-seo-2026-checklist.md` — CWV INP, mobile-first, hreflang, sitemap, robots, canonical
6. `content-audit-methodology.md` — gap analysis, decay detection, refresh ROI calculation
7. `tool-ecosystem-seo-2026.md` — Ahrefs vs SEMrush vs Moz vs SE Ranking + budget tier
8. `gdpr-privacy-seo-2026.md` — bonus 8th: Garante + Consent Mode v2 + GA4 strict config (auto-loaded if EU detected)

> NOTA: BUILD-BRIEF dice "6-7 references" — implemento 8 con #8 condizionale (auto-load se EU). Pattern coerente con `/competitor-deep-dive` 7 references.

## 8. Scripts

6 scripts in `scripts/`:

1. `validate_input.py` — schema validation domain/sitemap/competitor list
2. `audit_onpage.py` — fetch page + parse HTML (lxml/bs4) + tech audit (meta, schema, canonical, hreflang, headings)
3. `keyword_clusters.py` — semantic clustering keyword via similarity matrix (sentence-transformers stub o cosine fallback)
4. `schema_generator.py` — JSON-LD generation per page type + validation hint
5. `content_brief_gen.py` — content brief markdown da keyword + competitor top 3
6. `mcp_detect.py` — MCP availability check + fallback chain config

`requirements.txt`: PyYAML, requests, beautifulsoup4, lxml (no heavy ML deps — semantic clustering usa cosine similarity su simple bag-of-words se sentence-transformers non disponibile).

## 9. Output formats

### Executive summary (markdown, 1 page max)

```markdown
# SEO Audit Summary — example.com — 2026-05-01

**Stage**: scaling
**Geo**: Italia (GDPR mode active)

## Top 3 findings
1. INP threshold violato (P0): ...
2. Schema FAQPage invalid (P1): ...
3. Cluster gap "...": opportunità +35% traffic potential

## Top 3 quick-win (≤2 sett)
1. ...
2. ...
3. ...

## 90-day roadmap
- Sett 1-4: ...
- Sett 5-8: ...
- Sett 9-12: ...

## KPI tracking plan
- ...
```

### Detailed report (markdown, max 6000 parole)

Sections:
1. Audit baseline
2. Keyword strategy
3. Content plan
4. Technical fix
5. GEO layer (if not skip)
6. Tool stack recommendation
7. Tracking + reporting

## 10. Anti-pattern critici (system prompt enforce)

10 anti-pattern (vedi `seo-strategist.md` sezione "Anti-pattern" + research-summary.md sezione finale).

## 11. Edge case handling

- **Stealth domain** (no homepage content, JS-heavy SPA, Cloudflare anti-bot) → audit fallback PageSpeed Insights API + Search Console (se connesso) + warning utente
- **Multi-domain hreflang missing** → flag + reciprocal mapping suggestion
- **Programmatic SEO boilerplate >70%** → flag Helpful Content red flag → suggest unique-value injection per page
- **AI-generated content disclosure** → output skill include boilerplate "this content was AI-assisted" se user opt-in
- **Search Console export 1000 row limit** → workaround BigQuery export documentato + Looker Studio link
- **AI Overview attribution loss** → tracking via referrer header + custom analytics setup
- **Crawl budget exhaustion** → priority sitemap + crawl-delay strategy

## 12. Memory lifecycle

- `<memory>/config.md` creato Phase B post-discovery
- Re-prime ogni run via Read del file
- Update on `reconfigure` o cambio Q1-Q8 esplicito user
- 90gg refresh prompt: «Sono passati 90gg dall'ultimo audit. Re-run audit per refresh baseline?»

## 13. Chain con altri subagent

Output può chainare a:
- `/document-factory` per generare content brief PDF / executive summary docx
- `/social-content-engine` per repurposing pillar content social
- `/automation-architect` per workflow content publishing automation
- `/competitor-deep-dive` per competitor cross-research (input keyword/competitor list)

Input atteso: nessun upstream chain mandatory — `/seo-strategist` può partire da zero.
