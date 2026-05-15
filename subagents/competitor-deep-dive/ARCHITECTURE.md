# ARCHITECTURE — `/competitor-deep-dive`

> **Output Fase B**: design completo subagent prima del build (Fase C). Letto da worker chat e dal coordinator come riferimento durante build + review. Frozen post-Fase B salvo emergent decisions documentate in DECISIONS.md.
>
> **Reference**: BUILD-BRIEF.md (definitivo), DECISIONS.md (4 decisioni iniziali), research/research-summary.md (3887 parole).

## 1. Mission + differenziazione

**Mission**: trasformare 1-5 nomi competitor in dossier strategico markdown deterministico, evidence-first, multi-source, in 1 day standard / 2h quick / 3d deep.

**Output deterministico**:
- `dossier_<competitor>.md` × N (max 1500 parole ognuno)
- `synthesis.md` (cross-competitor patterns, max 1000 parole)
- `opportunities.md` (top 3 raccomandazioni, max 800 parole)
- `gap-matrix.json` (machine-readable matrix 6-dim)
- artefatti intermedi: `positioning.json`, `tov.json`, `reviews.json` per competitor

**Differenziazione vs altri subagent Pack v2**:

| Subagent | Driver | Input → Output |
|----------|--------|----------------|
| `/lead-finder-pro` | DATA-driven | ICP → lista lead enriched + scorati |
| **`/competitor-deep-dive`** | **OUTPUT-driven** | **Nomi competitor → dossier sintetizzato evidence-first** |
| `/web-builder` | ARTIFACT-driven | Spec → Next.js+Convex+Clerk+Vercel app |
| `/outbound-orchestrator` | ACTION-driven | Lead Hot → campagna outbound multi-channel |

**Filosofia evidence-first**: ogni claim (sentiment, ToV score, positioning, gap) ha source URL + quote/review_id. Mai allucinazioni. Se evidence insufficiente → flag `"insufficient_evidence"` + suggerimento espansione corpus.

## 2. Discovery flow al first run

**8 domande** sequenziali via AskUserQuestion (definitivo in `discovery/questions.md`):

| # | Header | Salvato in | Logica conseguente |
|---|--------|------------|---------------------|
| 1 | Ruolo | `user.role` | Routing framework gap-finder (5 ruoli → 3-5 framework) |
| 2 | Settore | `business.industry` | Default reviews focus |
| 3 | Competitor | `competitors_input[]` | Block se 0, warning se >5 |
| 4 | Profondita | `analysis.depth` | Skip ToV+reviews se Quick, +deep tier se Deep |
| 5 | Output | `analysis.output_format` | Verify MCP availability |
| 6 | Baseline | `business.baseline` | Block se incompleto (gap impossible) |
| 7 | Geo | `business.geo_target` | EU mode auto-load GDPR refs |
| 8 | Reviews | `analysis.reviews_focus[]` | Multi-platform cost flag |

**Re-run skip**: se `<memory>/config.md` esiste con `schema_version: 1` → skip discovery, mostra summary, chiedi solo "Quali competitor analizzare adesso?".

**Reconfigure trigger**: keyword "reconfigure", "reset", "ricomincia" → re-run 8 domande, sovrascrivi config (mantieni `competitors_analyzed[]` history).

## 3. MCP mapping completa

| MCP | Tipo | Use case | Fallback se mancante |
|-----|------|----------|----------------------|
| `apify` | **Required (primary)** | Reviews scrape G2/Trustpilot/Capterra (zen-studio actor), BuiltWith tech, Crunchbase funding (deep tier) | parallel-cli search + WebFetch (degraded — no structured reviews, flag warning) |
| `playwright` | **Required (primary)** | Scrape homepage/about/product per positioning + ToV corpus (JS-rendered SPA) | Bash + curl + html parsing (degraded, no JS rendering, log "ToV qualità ridotta") |
| `parallel-cli` (CLI Bash) | Recommended | parallel-cli research per long-tail signal (Reddit r/SaaS, HN, blog mention) | WebSearch (meno preciso, no deep research) |
| `google-personal` | Optional | Output Google Doc se `analysis.output_format = google_doc` | Markdown locale + suggerimento "Installa google-personal MCP per Google Doc" |
| `slack` | Optional | Post sintesi in canale team se `analysis.output_format = slack` | Stdout markdown |
| `attio-mcp` | Optional | Salva competitor come record CRM tipo "Account/Competitor" (link bidirezionale) | Skip CRM linkage |
| `notebooklm` (CLI) | Optional | Cross-check research grounded se evidence ambiguo | Skip — usare WebSearch + parallel-cli |

**Detection logic** (`scripts/mcp_detect.py` riusa pattern lead-finder-pro):

```python
verify_mcp("apify"):
    if missing → ERROR "Reviews scraping richiede apify, fallback parallel-cli sub-quality"
    elif rate_limited → checkpoint + retry exponential backoff (5s, 30s, 5min)

verify_mcp("playwright"):
    if missing → WARNING "ToV analysis qualità ridotta (no JS render)"

verify_mcp("parallel-cli", check_cli=True):
    if missing → INFO "Long-tail signal scope ridotto a WebSearch"

verify_mcp("google-personal"):
    if user_choice == "google_doc" and missing → ERROR "Installa MCP o cambia output format"
    else → SKIP

verify_mcp("slack"):
    if user_choice == "slack" and missing → ERROR
    else → SKIP

verify_mcp("attio-mcp"):
    optional always
```

## 4. Skills chain deterministica

**Pipeline 5 skill** (output di N = input di N+1, parallelizzabile in step 2):

```
[discovery/config validato]
        ↓
[Per ogni competitor in competitors_input[]:]
        ↓
   ┌─ positioning-mapper (Playwright scrape homepage/about/product)
   │     output: positioning.json
   ↓
   ├─ tov-analyzer (corpus testuale dal positioning + 5 blog post)    ┐ parallel
   │     output: tov.json                                              │
   │                                                                   │ entrambi servono
   ├─ reviews-sentiment (Apify zen-studio actor multi-platform)        ┘ a gap-finder
   │     output: reviews.json (anti-hallucination MANDATORY)
        ↓
[Tutti competitor processati + cliente baseline ingerito]
        ↓
   ┌─ gap-finder (input: tutti i positioning/tov/reviews + baseline)
   │     output: gap-matrix.json + gap-narrative.md
        ↓
   ┌─ dossier-writer (input: tutti gli artefatti)
   │     output:
   │       - dossier_<competitor>.md × N
   │       - synthesis.md
   │       - opportunities.md
        ↓
[Output sync verso target (markdown locale | Google Doc | Notion | Slack)]
```

### Schema JSON I/O per skill

#### `positioning-mapper`

**Input**:
```json
{
  "competitor": "Make",
  "domain": "make.com",
  "scrape_pages": ["homepage", "about", "product", "pricing"]
}
```

**Output `positioning.json`**:
```json
{
  "competitor": "Make",
  "domain": "make.com",
  "scrape_date": "2026-04-30",
  "tagline": "Automate work, anywhere — visually",
  "tagline_source": {"url": "make.com", "selector": "h1"},
  "value_prop": "...",
  "icp_inferred": "Mid-market SaaS, technical operators",
  "icp_evidence": [{"url": "...", "quote": "..."}],
  "differentiators": [
    {"claim": "Visual no-code workflow builder", "evidence": [{"url": "...", "quote": "..."}]},
    {"claim": "10,000+ apps integrated", "evidence": [...]},
    {"claim": "Free tier with 1,000 ops/month", "evidence": [...]}
  ],
  "pricing_summary": {"model": "subscription", "tiers": [...], "lowest_tier_usd": 9},
  "stealth_flag": false
}
```

#### `tov-analyzer`

**Input**:
```json
{
  "competitor": "Make",
  "corpus_sources": ["homepage", "about", "5 latest blog posts"],
  "corpus_text": "<aggregated text>",
  "min_words_required": 200
}
```

**Output `tov.json`**:
```json
{
  "competitor": "Make",
  "corpus_size_words": 1247,
  "scores": {
    "formal_casual": {"score": 2, "label": "Casual", "evidence": [{"quote": "...", "url": "...", "metric": "contraction"}]},
    "funny_serious": {"score": 4, "label": "Serious", "evidence": [...]},
    "respectful_irreverent": {"score": 3, "label": "Neutral", "evidence": [...]},
    "enthusiastic_matter_of_fact": {"score": 2, "label": "Enthusiastic", "evidence": [...]}
  },
  "derived_metrics": {
    "jargon_density_pct": 4.2,
    "pronoun_ratio_we_you": 0.78,
    "avg_sentence_length_words": 12.4,
    "cta_style": "imperative",
    "exclamation_density_per_100w": 1.8
  },
  "insufficient_evidence": false
}
```

**Fallback**: se `corpus_size_words < 200` → `insufficient_evidence: true, reason: "corpus too small"`.

#### `reviews-sentiment`

**Input**:
```json
{
  "competitor": "Make",
  "platforms": ["G2", "Trustpilot"],
  "actor_preferred": "zen-studio/software-review-scraper",
  "max_reviews_per_platform": 100,
  "rate_limit_seconds": {"G2": 5, "Trustpilot": 3, "Capterra": 5}
}
```

**Output `reviews.json`** (anti-hallucination MANDATORY):
```json
{
  "competitor": "Make",
  "platform": "G2",
  "scrape_date": "2026-04-30",
  "actor_used": "zen-studio/software-review-scraper",
  "total_reviews_scraped": 142,
  "sentiment_breakdown": {"positive_pct": 62, "neutral_pct": 25, "negative_pct": 13},
  "top_strengths": [
    {
      "theme": "Ease of use / drag-drop UI",
      "frequency": 47,
      "evidence": [
        {"review_id": "g2-12345", "quote": "intuitive drag-drop UI saved me hours weekly", "rating": 5, "date": "2026-03-15", "url": "g2.com/products/make/reviews/g2-12345"}
      ]
    }
  ],
  "top_weaknesses": [...],
  "top_jtbd": [...],
  "love_hate_want": {"love": [...], "hate": [...], "want": [...]},
  "insufficient_evidence": false
}
```

**Fallback**: se Apify fail / no reviews → `insufficient_evidence: true, reason: "<error>", fallback_used: "WebFetch+manual"` o skip totalmente. **Mai inventare review_id o quote**.

#### `gap-finder`

**Input**:
```json
{
  "client_baseline": {"tagline": "...", "value_prop": "...", "icp": "..."},
  "competitors": [
    {"positioning": <pos.json>, "tov": <tov.json>, "reviews": <reviews.json>}
  ],
  "user_role": "marketing",
  "framework_routing": ["strategy_canvas", "positioning_map", "tov_diff"]
}
```

**Output `gap-matrix.json`**:
```json
{
  "client_baseline": {...},
  "competitors_analyzed": ["Make", "n8n", "Zapier"],
  "framework_used": ["Strategy Canvas", "Positioning Map 2x2", "ToV Diff"],
  "gaps": [
    {
      "id": "gap-001",
      "dimension": "feature",
      "description": "AI-assisted workflow builder mancante in cliente, presente in 3/3 competitor",
      "impact": 5, "ease": 3, "evidence_strength": 5, "complexity_penalty": 2,
      "gap_score": 37.5,
      "love_hate_want": "want",
      "jtbd_primary": "build automation 10x faster than manual",
      "evidence": [
        {"competitor": "Make", "source": "make.com/ai", "quote": "..."},
        {"competitor": "Zapier", "review_id": "g2-9999", "quote": "..."}
      ]
    }
  ],
  "ranking": ["gap-001", "gap-007", "gap-003"]
}
```

**Output `gap-narrative.md`**: 5-10 gap rankati per `gap_score` con narrativa actionable (Quick wins / Strategic bets / Ignore).

**Block**: se `client_baseline` incompleto (mancano tagline OR value_prop OR icp) → block + prompt utente.

#### `dossier-writer`

**Input**:
```json
{
  "config": <memory/config.md>,
  "artifacts": {
    "positioning": [...], "tov": [...], "reviews": [...],
    "gap_matrix": <gap-matrix.json>, "gap_narrative": <gap-narrative.md>
  },
  "word_budget": {"dossier": 1500, "synthesis": 1000, "opportunities": 800}
}
```

**Output**:
- `dossier_<slug>.md` × N (1 per competitor, max 1500 parole)
- `synthesis.md` (max 1000 parole, cross-competitor patterns)
- `opportunities.md` (max 800 parole, top 3 raccomandazioni)

**Anti-pattern enforced HARD**:
- No claim senza citazione (URL o review_id)
- No dossier monolite >5000 parole (split forced)
- Ogni numero ha source URL
- Ogni ToV score ha 3+ evidence quotes
- Ogni gap ha evidence strength score

## 5. Methodology principal — 6 fasi operative (per system prompt)

1. **Ingest**: leggi `<memory>/config.md` + ricevi `competitors_input[]` da utente
2. **Per competitor (parallel max 3)**: positioning-mapper → tov-analyzer + reviews-sentiment in parallel
3. **Cross-competitor**: pattern detection (common positioning, common gap, common ToV)
4. **Gap analysis**: gap-finder con cliente baseline overlay (block se baseline incomplete)
5. **Dossier render**: dossier-writer (markdown deterministico)
6. **Output sync**: target esterno (Google Doc / Notion / Slack / markdown locale)

## 6. Config schema (`<memory>/config.md`)

```yaml
---
agent: competitor-deep-dive
schema_version: 1
created: 2026-MM-DD
last_updated: 2026-MM-DD
---

user:
  role: marketing  # founder | marketing | pm | sales | analyst

business:
  industry: "SaaS B2B - workflow automation"  # SaaS B2B | eCommerce/DTC | Agency/Servizi B2B | Marketplace/Platform
  geo_target: EU  # Italia | EU | EMEA | USA/Worldwide
  baseline:
    tagline: "Automate workflows without code"
    value_prop: "10x faster than Zapier for technical teams"
    icp: "Mid-market SaaS, 50-500 employees, technical PMs"

analysis:
  depth: standard  # quick | standard | deep
  output_format: markdown  # markdown | google_doc | notion | slack
  reviews_focus: [G2, Trustpilot]  # subset di [G2, Trustpilot, Capterra]
  framework_routing: [strategy_canvas, positioning_map, tov_diff]  # auto da user.role

gdpr:
  mode_active: true  # auto-true se geo_target ∈ {Italia, EU, EMEA}
  lia_template_path: "<memory>/lia_template.md"  # generato auto se mode_active

competitors_input:  # current run
  - name: "Make"
    domain: "make.com"
  - name: "n8n"
    domain: "n8n.io"
  - name: "Zapier"
    domain: "zapier.com"

competitors_analyzed:  # history (mantenuto across reconfigure)
  - name: "Make"
    domain: "make.com"
    analyzed_at: 2026-04-30
    dossier_path: "research/dossier_make.md"
    artifacts: {positioning: "...", tov: "...", reviews: "..."}

mcp_available:
  apify: true
  playwright: true
  parallel_cli: true
  google_personal: false
  slack: true
  attio_mcp: true
  notebooklm: true

mcp_fallbacks_active:
  google_personal: markdown
```

## 7. References docs (7 totali in `references/`)

| # | File | Scope | Source primaria research |
|---|------|-------|--------------------------|
| 1 | `competitor-analysis-frameworks-2026.md` | 7 framework + when-to-use per ruolo | RQ1 |
| 2 | `tov-rubric-nielsen-norman.md` | 4-dim NN scoring 1-5 + metriche derivate + 3 esempi | RQ2 + nngroup.com |
| 3 | `tool-ecosystem-2026.md` | SimilarWeb/SemRush/Ahrefs/BuiltWith/Crunchbase/G2/Trustpilot/Capterra/Apify/parallel-cli pricing 2026 | RQ3 + Riff Analytics 2026 |
| 4 | `gdpr-scraping-compliance.md` | Lecito/non lecito + LIA template + rate-limit safe | RQ6 + CNIL 2024 |
| 5 | `dossier-anatomy.md` | Structure "wow", word budget, signal/noise, actionability | RQ7 + MADX/Olushad/Octopus |
| 6 | `gap-analysis-methodology.md` | Matrice 6-dim + Love-Hate-Want + ranking formula | RQ5 |
| 7 | `apify-actors-recipes.md` | Actor IDs maintained 2026 + input schema + esempi | RQ4 + Apify Store |

## 8. Output format target

### `dossier_<slug>.md` (max 1500 parole, target 700-900)

```markdown
# <Competitor Name>

> **TL;DR (50-75 parole)**: snapshot 1 frase + 3 bullet che il reader può tweetare.

## Positioning + Value Prop (100-150 parole)
- Tagline: "..." [source]
- Value prop: "..." [source]
- ICP: "..." [evidence quotes]
- 3 differentiators con citazioni

## Tone of Voice (100-150 parole)
- 4-dim NN scores 1-5 con label
- 3 evidence quotes per dim
- Derived metrics tabella

## Reviews Sentiment (150-200 parole)
- Sentiment breakdown % (positive/neutral/negative)
- Top 5 strengths (review_id + quote)
- Top 5 weaknesses (review_id + quote)
- Top 3 JTBD (con frequenza)
- Love / Hate / Want

## Tech & Funding (deep tier only, 100-150 parole)
- BuiltWith stack
- Crunchbase last round + total raised

## Gap vs cliente baseline (100-150 parole)
- 3-5 gap rankati con score
```

### `synthesis.md` (max 1000 parole)

- Common positioning tropes
- Common ToV pattern (es. tutti casual → blue ocean su formal-respectful?)
- Common gap (cosa nessuno fa)
- Customer Love-Hate-Want overlap

### `opportunities.md` (max 800 parole)

- 3 raccomandazioni rankate per impact × ease
- Per ogni reco: cosa fare, owner suggerito, success metric, due date
- 7-day next step concreto

## 9. Anti-pattern enforced (8 critical)

1. **Sentiment senza review_id + quote** → output blocked
2. **ToV claim senza ≥3 evidence quotes per dim** → output blocked
3. **Inventare funding/pricing** → flag `"data_not_verified"`
4. **Bulk scrape senza rate-limit** → default delay per source enforced
5. **Dossier monolite >5000 parole** → word budget hard-cap, split forced
6. **Gap analysis senza cliente baseline** → block + prompt
7. **Scrape LinkedIn behind login senza Sales Nav** → skip + log
8. **Auto-publish Slack/Notion senza preview** → sempre conferma utente

## 10. Edge case handling (15 mappati — vedi research-summary)

Documentati come check in skill prompts:

- Stealth competitor (homepage vuota) → flag, skip with grace
- No public reviews → fallback parallel-cli mention
- Corpus <200 parole → ToV unmeasurable
- Conflicting positioning sources → trust più recente, flag
- Pricing not public → flag "request demo"
- Funding non in Crunchbase → flag "data not verified"
- LinkedIn behind login → skip
- G2 reviews pre-2024 verified era → flag low confidence
- Cliente baseline missing → block
- Multi-product competitor → AskUserQuestion clarification
- Geo split USA/EU pricing → 2 sezioni dossier
- Post-acquisition volatility → flag review pre-pivot
- Domain rebranding → redirect catch + nota
- Apify rate limit → checkpoint + exponential backoff
- EU mode + reviews fuori UE → GDPR cross-border flag in LIA

## 11. Costo + tempo stimati

| Tier | Tempo | Costo Apify | Tool aggiuntivi |
|------|-------|-------------|------------------|
| Quick scan | 2h | ~$5 (1 platform × 3 competitor) | Solo Playwright |
| Standard dossier | 1d | ~$15-20 (2 platform × 3 competitor) | + parallel-cli |
| Deep strategic | 3d | ~$50+ | + BuiltWith API + Crunchbase API + LinkedIn Sales Nav |

## 12. File deliverable Fase C — checklist

Quando Fase C è done, devono esistere:

- [ ] `competitor-deep-dive.md` (main agent, 400-500 righe)
- [ ] `skills/positioning-mapper/SKILL.md`
- [ ] `skills/tov-analyzer/SKILL.md`
- [ ] `skills/reviews-sentiment/SKILL.md` (anti-hallucination MANDATORY)
- [ ] `skills/gap-finder/SKILL.md`
- [ ] `skills/dossier-writer/SKILL.md`
- [ ] `references/competitor-analysis-frameworks-2026.md`
- [ ] `references/tov-rubric-nielsen-norman.md`
- [ ] `references/tool-ecosystem-2026.md`
- [ ] `references/gdpr-scraping-compliance.md`
- [ ] `references/dossier-anatomy.md`
- [ ] `references/gap-analysis-methodology.md`
- [ ] `references/apify-actors-recipes.md`
- [ ] `scripts/discovery_check.py` ✅ (Fase B)
- [ ] `scripts/mcp_detect.py`
- [ ] `scripts/positioning_extract.py`
- [ ] `scripts/tov_score.py`
- [ ] `scripts/reviews_apify.py`
- [ ] `scripts/gap_matrix_build.py`
- [ ] `scripts/dossier_render.py`
- [ ] `scripts/requirements.txt` ✅ (Fase B)
- [ ] `README.md` (user-facing, italiano, ~270 righe, 3 esempi)
