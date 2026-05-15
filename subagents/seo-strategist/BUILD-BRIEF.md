# BUILD-BRIEF — `/seo-strategist`

> **Per la worker chat**: leggi questo file all'inizio. Tutto il contesto necessario per buildare l'agent è qui. Non serve leggere conversazioni precedenti.
>
> **Quick start**: leggi BUILD-BRIEF → leggi PROGRESS.md (se esiste) → leggi DECISIONS.md (se esiste) → esegui Fase A → B → C → D → E.
> Aggiorna PROGRESS.md ad ogni milestone (almeno ogni 25% context fill).

## Identità del subagent

- **Nome**: `/seo-strategist`
- **Cosa fa (1 frase)**: Da audit dominio + obiettivi business a strategia SEO+GEO 2026 actionable (keyword clustering, gap analysis content, schema markup, GEO optimization per LLM citation, backlink strategy, technical audit), con deliverable pronti per content team o agency.
- **Per chi**: Founder, Marketing manager, SEO specialist, Content strategist, Freelancer SEO consulting (audience non-developer Learnn)
- **Use case slide W2**: "Marketing strategy" (#3 dei 8 use case)
- **Skill v1 base da riusare come spunto**: nessuna skill SEO dedicata in pack v1 — primo subagent del topic. Verificare se esiste skill correlata `tech-stack-2026` per cross-reference contenuto e citare.
- **Tier**: 🥈
- **Tempo stimato**: 1-1.5 giorni research + 5-7 ore build = ~10-12 ore totali

## Vincoli di livello "spaventoso"

Filippo ha esplicitamente chiesto agent **"fatti veramente bene, profondi, perfetti, che fanno dire wow"**. Vincoli minimi:

- System prompt **300-450 righe**
- **5 skills companion** in `skills/`
- **6-7 references docs** (best practice 2026, GEO, keyword research, schema markup, technical SEO, content clusters, tool ecosystem)
- **Discovery interattiva** al first run (8 domande mirate)
- **MCP detection automatica** + fallback grazioso
- **Memory persistente** via `memory: project`
- **Almeno 3 esempi reali** documentati nel README (es. SaaS B2B, e-commerce, agency)
- **Italiano** per messaggi utente, **inglese** per nomi tecnici
- **Anti-hallucination**: ogni claim SEO deve essere groundato (citazione fonte autorevole, no "best practice generic")

## Fase A — Deep Research (1-1.5 giorni)

### Research questions (rispondere TUTTE prima di passare a B)

1. **SEO best practice 2026 evolution**: cosa è cambiato post-Helpful Content Update + AI Overviews + March/August 2024 Core Updates. Cosa funziona ancora vs cosa è morto (link velocity, exact-match anchor, ecc.). E-E-A-T criteria.
2. **GEO (Generative Engine Optimization) 2026**: come ottimizzare content per essere citato da ChatGPT, Perplexity, Claude, Gemini. Llms.txt protocol, structured data nuovi types, citation patterns LLM. Differenza GEO vs traditional SEO.
3. **Keyword research framework 2026**: pillar pages + topic clusters, search intent classification (informational/navigational/transactional/commercial), semantic clustering, long-tail strategy post-AI Overview.
4. **Technical SEO 2026**: Core Web Vitals (INP replacing FID), JS rendering, structured data Schema.org 2026 types nuovi (per AI), sitemap strategy, crawl budget per JS-heavy sites, mobile-first definitivo.
5. **Content strategy 2026**: pillar + cluster, content audit, content gap analysis, content refresh frequency, AI-assisted content (linee rosse Google Helpful Content), originality threshold.
6. **Backlink strategy 2026**: cosa funziona (digital PR, guest post quality, broken link building), cosa è morto (link farms, PBN, paid links). Domain authority signals 2026, anchor text distribution.
7. **GDPR + privacy SEO 2026**: cookie consent impact su Analytics 4, tracking consent mode, server-side tagging, IT-specific (Garante cookie banner enforcement).

### Fonti da consultare

**NotebookLM dedicato** (worker chat crea in Fase A — nessun ID pre-allocato):

- Comando: `notebooklm create "SEO + GEO Strategy 2026"`
- Sources da aggiungere (`notebooklm source add`):
  - https://developers.google.com/search/docs (Google Search Central)
  - https://moz.com/blog (latest 2026)
  - https://ahrefs.com/blog
  - https://searchengineland.com/library/seo
  - https://www.semrush.com/blog (cluster SEO 2026)
  - https://backlinko.com/seo-strategies (Brian Dean)
  - https://www.searchenginejournal.com (Helpful Content updates)
  - https://platform.openai.com/docs/gpt/llms-txt (llms.txt spec)
  - https://schema.org (structured data)
  - https://web.dev/articles/inp (Core Web Vitals INP)
- Aspetta indicizzazione 3-5 min, poi `notebooklm ask` per le 7 RQ

**WebSearch query**:

- "SEO best practice 2026 post helpful content update"
- "GEO Generative Engine Optimization 2026 ChatGPT Perplexity citation"
- "llms.txt 2026 specification AI crawler"
- "Core Web Vitals INP 2026 measurement"
- "schema markup JSON-LD 2026 new types AI"
- "topic clusters pillar page strategy 2026"
- "technical SEO JavaScript rendering 2026"
- "GDPR cookie consent SEO Analytics 4 2026"

**WebFetch URL specifici**:

- Google Search Central — Helpful Content
- Schema.org changelog 2026
- llms.txt spec
- Moz/Ahrefs deep guides 2026
- Garante Privacy cookie banner provvedimento 2024

**parallel-cli**:

- `parallel-cli research "GEO Generative Engine Optimization patterns 2026"`
- `parallel-cli research "AI Overview impact organic traffic 2026 study"`

### Output research

Salva in `research/research-summary.md`:

- 1 sezione per ogni RQ (Q1-Q7) con citation
- Top 5 finding più rilevanti per l'agent
- Edge case scoperti (lista)
- Tool/API capabilities mappate (tabella Ahrefs vs SEMrush vs Moz vs SE Ranking)
- 8 GEO-specific patterns
- 4 framework content strategy (pillar+cluster, hub+spoke, glossary+pillar, programmatic SEO)

Salva sintesi anche in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/seo-strategist_2026-MM-DD.md`

## Fase B — Architecture Design (2-3 ore)

### Discovery questionnaire (8 domande)

Bozza coordinator (raffina in Fase B):

| # | Header | Q (italiano) | Options | Conseguenza |
|---|--------|--------------|---------|-------------|
| 1 | Ruolo | Ruolo principale | Founder · Marketing manager · SEO specialist · Content strategist · Agency | Adatta tono e profondità default |
| 2 | Stack | SEO tool primary | Ahrefs · SEMrush · Moz · SE Ranking · Search Console only | Carica recipe API specifica + saving credit advice |
| 3 | Site | Tipo sito | SaaS B2B · eCommerce · Content/Blog · Local business · Agency clients | Adatta playbook: keyword strategy + monetization model |
| 4 | Stage | Stadio SEO | Greenfield (nuovo) · Decay (traffic giù) · Plateau · Scaling | Logica priority: foundation vs recovery vs scaling |
| 5 | Geo | Geografia target | Italia · Europa · USA · Worldwide · Multi-paese | Lingua content + GDPR mode + multi-hreflang strategy |
| 6 | GEO | Optimize per LLM citation? | Sì priority · Sì secondario · Solo SEO classico | Activate skill `geo-optimizer` o skip |
| 7 | Volume | Volume content/mese | <5 · 5-15 · 15-50 · 50+ | Scaling strategy + workflow content team |
| 8 | Budget | Budget tool/mese | <€100 · €100-500 · €500-2k · €2k+ | Tool stack recommendation conservativa vs full-stack |

Salva in `discovery/questions.md`.

### MCP mapping (con fallback)

| MCP | Tipo | Required for | Fallback |
|-----|------|--------------|----------|
| `parallel-cli` | Recommended | Web research SERP + competitor scrape | WebSearch + WebFetch |
| `playwright` | Optional | Scraping JS-heavy sites + render check | Bash + curl + readability parser |
| `apify` | Optional | SERP scraping + ahrefs alternative | Manual export user da Ahrefs UI |
| `google-personal` | Optional | Output report Google Doc/Sheet + Search Console data | Markdown locale |
| `context7` | Optional | Per librerie SEO tools docs | WebFetch fallback |

### Skills companion (5 skill)

1. **`keyword-research/`** (~220 righe)
   - **Cosa fa**: keyword discovery + semantic clustering + search intent classification + long-tail analysis
   - **Input**: seed keywords + ICP + geo
   - **Output**: JSON cluster (pillar + supporting + long-tail) + intent label
   - **References**: `keyword-research-frameworks-2026.md`

2. **`content-audit/`** (~200 righe)
   - **Cosa fa**: gap analysis vs competitor, content decay detection, refresh priority, optimization opportunities
   - **Input**: domain + competitor list + Search Console export (opzionale)
   - **Output**: `{audit_findings, refresh_priority, gap_opportunities, decay_pages}`
   - **References**: `content-audit-methodology.md`

3. **`geo-optimizer/`** (~230 righe)
   - **Cosa fa**: ottimizzazione content per LLM citation (ChatGPT, Perplexity, Claude). Llms.txt generation, schema FAQPage, citation density, source authority signals
   - **Input**: page URL + topic + target LLM (multi)
   - **Output**: `{llms_txt_content, schema_markup, content_recommendations, citation_score}`
   - **References**: `geo-generative-engine-optimization-2026.md`

4. **`schema-generator/`** (~190 righe)
   - **Cosa fa**: genera Schema.org JSON-LD per page type (Article, Product, FAQPage, HowTo, Review, LocalBusiness, Organization, BreadcrumbList, AggregateRating). Validation pre-deploy.
   - **Input**: page metadata + page type + content extract
   - **Output**: JSON-LD pronto per `<head>` injection
   - **References**: `schema-markup-guide-2026.md`

5. **`technical-seo-audit/`** (~210 righe)
   - **Cosa fa**: technical audit (CWV, mobile-first, hreflang, sitemap, robots.txt, canonical, internal linking, JS rendering, indexability)
   - **Input**: domain + sitemap + Search Console (opzionale)
   - **Output**: priority issue list + fix recommendation per issue
   - **References**: `technical-seo-2026-checklist.md`

### Schema config (`<memory>/config.md`)

```yaml
---
agent: seo-strategist
created: 2026-MM-DD
schema_version: 1
---

user:
  role: founder  # founder | marketing_manager | seo_specialist | content_strategist | agency

stack:
  seo_primary: ahrefs  # ahrefs | semrush | moz | se_ranking | search_console_only
  search_console_connected: true
  analytics: ga4

site:
  domain: example.com
  type: saas_b2b  # saas_b2b | ecommerce | content_blog | local | agency
  stage: scaling  # greenfield | decay | plateau | scaling

geo:
  target: italia  # italia | europa | usa | worldwide | multi_paese
  hreflang_required: false
  geo_eu_detected: true  # GDPR + cookie consent mode

strategy:
  geo_llm_optimization: priority  # priority | secondary | skip
  content_volume: 5_15  # <5 | 5_15 | 15_50 | 50plus
  pillar_cluster_strategy: true

budget:
  tool_monthly: 100_500  # <100 | 100_500 | 500_2k | 2kplus

mcp_available: { parallel-cli: true, playwright: true, apify: false, google-personal: true, context7: true }
mcp_fallbacks_active: { apify: webfetch_serp }

api_keys:
  ahrefs_present: false  # env AHREFS_API_KEY
  semrush_present: false  # env SEMRUSH_API_KEY
```

### References docs (6-7 file da scrivere in `references/`)

| File | Content |
|------|---------|
| `seo-best-practices-2026.md` | Helpful Content + Core Updates 2024 impact, E-E-A-T, content quality signals, ranking factors 2026 |
| `geo-generative-engine-optimization-2026.md` | LLM citation optimization, llms.txt spec, schema for AI, citation patterns ChatGPT/Perplexity/Claude |
| `keyword-research-frameworks-2026.md` | Pillar+cluster, search intent classification, semantic clustering, long-tail post-AI Overview |
| `schema-markup-guide-2026.md` | JSON-LD per page type, validation, AI-relevant types nuovi |
| `technical-seo-2026-checklist.md` | CWV (INP), mobile-first, hreflang, sitemap, robots, canonical, JS rendering, indexability |
| `content-audit-methodology.md` | Gap analysis, decay detection, refresh priority, ROI calculation per content piece |
| `tool-ecosystem-seo-2026.md` | Ahrefs vs SEMrush vs Moz vs SE Ranking comparison, free tier capabilities, when to use cosa |

## Fase C — Build (5-7 ore)

### Subagent file principale

`seo-strategist.md` con frontmatter + system prompt 350-450 righe (9 sezioni: identità, discovery, MCP detection, methodology 6 fasi: Audit → Research → Strategy → Content plan → Technical fix → Reporting, tool usage, output, edge case, examples 3 reali, anti-pattern).

### Skills companion + Scripts

- 5 SKILL.md (vedi sopra)
- 6 scripts: `validate_input.py`, `audit_onpage.py`, `keyword_clusters.py`, `schema_generator.py`, `content_brief_gen.py`, `mcp_detect.py` + `requirements.txt`

### README utente-facing

3-5 esempi reali (SaaS B2B keyword research, eCommerce content audit, blog GEO optimization), 8 FAQ, troubleshooting, anti-pattern.

## Fase D — Test (1-2 ore)

10 test checklist (discovery, re-run, input validation, audit run, keyword cluster, GEO output, schema validation, technical audit, MCP fallback, GDPR EU mode), test fixtures (sample sitemap, sample page HTML, fake competitor list).

## Fase E — Documentation + Bundle (1 ora)

1. Update `MASTER-PROGRESS.md` (#5 → ✅)
2. Sezione `dist/CLAUDE_WEEK_SKILL_PACK.md`
3. Nota Obsidian
4. Final PROGRESS.md update

## Definition of Done

- [ ] 5 fasi A→E completate
- [ ] System prompt ≥350 righe
- [ ] 5 skills + 6-7 references + 6 scripts + README + 3 esempi
- [ ] Static + smoke test PASS
- [ ] PROGRESS + MASTER-PROGRESS aggiornati

## Anti-pattern critici (da includere nel system prompt)

1. **Mai claim SEO non groundato** (sempre citazione fonte autorevole — Google, Moz, Ahrefs, SE Land)
2. **Mai keyword stuffing** o suggerire density artificiale
3. **Mai consigliare PBN, link farms, exchange paid** (Google penalty risk)
4. **Mai duplicate content cross-page** (canonical confusion)
5. **Mai schema markup invalid** (validation pre-deploy mandatory via Schema.org validator)
6. **Mai promesse traffic specifiche** ("+200% in 3 mesi") senza disclaimer
7. **Mai consigliare tool che user non può permettersi** (rispetta budget config Q8)
8. **Mai skip GDPR cookie consent** se EU detected (impact GA4 measurement)
9. **Mai over-optimization on-page** (Google penalty Helpful Content)
10. **Mai AI-generated content in mass** (Helpful Content red lines)

## 5 Decisioni emergent flagged per worker chat (Architecture phase)

1. **GEO priority default**: se Q6=priority, ogni content piece ottimizzato dual SEO+GEO. Se secondario, GEO solo per pillar pages.
2. **Tool tier default**: se budget Q8 <€100, suggerisci Ubersuggest free + Search Console. €100-500: Ahrefs Lite o Moz Pro. >€500: full Ahrefs/SEMrush.
3. **Content audit threshold decay**: page con traffic -30% vs 90gg precedenti = candidate refresh.
4. **Schema markup always-on**: per ogni page type rilevante, schema mandatory (validation enforced).
5. **NotebookLM creation**: lasciata a worker chat in Fase A.

## Chain con altri subagent

Input atteso: domain + obiettivi business (no chain mandatory upstream). Output può chainare a:
- `/document-factory` per generare content brief PDF
- `/social-content-engine` per repurposing content social
- `/automation-architect` per workflow content publishing

## Context management

### Update PROGRESS.md ad ogni 25% context
- ✅ Cosa è stato fatto · 🚧 Cosa sto facendo · 📋 Prossimi step · 🐛 Edge case

### A 50% context
1. Update finale PROGRESS + DECISIONS
2. User chiama `/compact`
3. Re-prime: "Leggi PROGRESS.md e DECISIONS.md. Continua."

### File da NON perdere mai
- BUILD-BRIEF.md, PROGRESS.md, DECISIONS.md, ARCHITECTURE.md, research/research-summary.md
