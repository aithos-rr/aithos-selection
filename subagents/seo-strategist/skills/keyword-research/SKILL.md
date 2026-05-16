---
name: keyword-research
description: Discovery + semantic clustering + search intent classification + long-tail post-AI-Overview analysis per progetto SEO. Da seed keyword + ICP + geo a cluster JSON deterministico (pillar + supporting + long-tail) con intent label, search volume estimate, difficulty score, opportunity score. Usa Ahrefs/SEMrush/Moz API se key presente, fallback semantic clustering via cosine similarity manuale + Search Console queries (se connesso) + Ubersuggest free per volume estimate. Anti-hallucination — mai inventare volume/difficulty number, output sempre `estimated` o `from_api` flag esplicito.
when_to_use: Avvio strategia content nuovo dominio, expansion cluster esistente, gap analysis vs competitor, content brief generation per content team, refresh strategy decay pages
---

# Keyword Research

Skill che trasforma seed keyword + contesto progetto in cluster JSON deterministico actionable per content strategy.

## Scope

- **In scope**: keyword discovery, semantic clustering, search intent classification, long-tail mining, opportunity scoring
- **Out of scope**: content writing (vedi `content-audit` skill per brief generation), backlink analysis, technical audit

## Input contract

```yaml
seed_keywords: ["analytics ecommerce", "shopify analytics"]  # 1-10 seed
icp_description: "founder/CMO ecommerce italiani 1-50M GMV"
geo_target: italia | europa | usa | worldwide | multi_paese
site_type: saas_b2b | ecommerce | content_blog | local | agency
content_volume: lt5 | 5_15 | 15_50 | 50plus
competitor_domains: ["competitor1.com", "competitor2.com"]  # optional, 0-5
existing_keyword_data: path/to/csv  # optional, da Search Console export
```

## Methodology

### Step 1 — Seed expansion

Per ogni seed keyword:
1. Se Ahrefs/SEMrush API key presente → call `keywords_explorer` endpoint con metric (volume, difficulty, CPC)
2. Fallback Ubersuggest (3 query/day free) o WebSearch + extract da SERP autosuggest
3. Capture: 50-200 keyword expansion per seed
4. Dedupe + filter (length 2-7 word, geo-relevant, language-relevant)

### Step 2 — Search intent classification

Tag ogni keyword con intent (rule-based + LLM fallback):

| Intent | Pattern signal | Esempio |
|--------|----------------|---------|
| `informational` | "how to", "what is", "guide", "tutorial", "ultimate" | "what is google analytics" |
| `navigational` | brand+name, domain | "ahrefs login" |
| `transactional` | "buy", "discount", "deal", "free", "trial", "signup" | "ahrefs free trial" |
| `commercial` | "best", "vs", "review", "comparison", "alternative" | "ahrefs vs semrush" |

Output field: `intent: <enum>`.

### Step 3 — Semantic clustering

Cluster keyword by topical similarity:
1. Se `sentence-transformers` Python lib disponibile → embeddings + cosine similarity matrix → DBSCAN clustering (eps=0.3, min_samples=3)
2. Fallback: bag-of-words + cosine similarity + manual centroid identification
3. 1 pillar page = 1 cluster centroid (top volume + low difficulty preference)
4. Cluster items = top 5-15 keyword similarity ≥0.65 al centroid

### Step 4 — Long-tail mining (post AI Overview)

Long-tail strategy 2026 priority (ground research-summary RQ3):
- 4+ word query (AI Overview spesso non triggherato)
- Brand + use-case combinazioni
- Local intent ("near me", "[city] [service]")
- Question-format ("come usare X per Y", "perché usare X")

Output field: `long_tail_keywords: []` separato dal main cluster.

### Step 5 — Opportunity scoring

Score 0-100 per keyword (estimated):

```
opportunity_score = (
  log10(volume + 1) * 20 *           # volume importance
  (100 - difficulty) / 100 *          # easier = better
  intent_weight                       # commercial+transactional bonus
)
```

`intent_weight`:
- transactional/commercial = 1.5
- informational = 1.0
- navigational = 0.3 (low ROI for non-brand owner)

## Output JSON schema

```json
{
  "seed_keywords": ["..."],
  "geo_target": "italia",
  "site_type": "saas_b2b",
  "generated_at": "2026-05-01T16:30:00Z",
  "data_sources": ["ahrefs_api", "search_console", "ubersuggest_free"],
  "clusters": [
    {
      "pillar_keyword": "ecommerce analytics guide",
      "pillar_intent": "informational",
      "pillar_volume_estimate": 2400,
      "pillar_difficulty_estimate": 38,
      "pillar_opportunity_score": 72,
      "supporting_keywords": [
        {
          "keyword": "shopify analytics dashboard",
          "intent": "informational",
          "volume_estimate": 880,
          "difficulty_estimate": 28,
          "opportunity_score": 65,
          "source": "ahrefs_api"
        }
      ],
      "cluster_size": 12
    }
  ],
  "long_tail_keywords": [
    {
      "keyword": "come misurare conversion rate ecommerce shopify",
      "intent": "informational",
      "volume_estimate": 90,
      "difficulty_estimate": 12,
      "opportunity_score": 45,
      "source": "google_autosuggest"
    }
  ],
  "rejected_keywords": [
    {"keyword": "...", "reason": "low_volume_under_50"},
    {"keyword": "...", "reason": "geo_mismatch"}
  ],
  "anti_hallucination_flags": {
    "volume_estimated_no_api": false,
    "difficulty_estimated_no_api": false,
    "fallback_clustering_used": false
  }
}
```

## Anti-hallucination contract

**MANDATORY**:
- Mai inventare volume number senza data source. Se no Ahrefs/SEMrush/Ubersuggest API → flag `volume_estimated_no_api: true` + use bucketing range ("low <100", "medium 100-1k", "high >1k") instead of specific number
- Mai inventare difficulty score. Se no API → flag `difficulty_estimated_no_api: true` + qualitative ("low/med/high")
- Source field obbligatorio per ogni keyword (`ahrefs_api`, `semrush_api`, `ubersuggest_free`, `search_console`, `google_autosuggest`, `manual`)
- Se < 20 keyword recovered total → flag `insufficient_evidence` + suggest expand seed

## Edge cases

1. **Seed keyword troppo broad** ("seo") → expansion >500 keyword → suggest narrowing seed con use-case modifier
2. **Seed keyword troppo niche** ("seo agenzia bologna ristorante") → <10 keyword → flag + suggest broader seed
3. **Geo mismatch** (seed Italian su geo USA) → reject + warning
4. **Multi-language** (Italian + English mixed) → cluster separati per lingua
5. **Stop word noise** ("come fare il" prefix per maggior keyword) → filter pre-cluster
6. **Branded keyword competitor** → flag in `branded_competitor` separate (no opportunity score, navigational intent)

## Tool integration

| Tool | Method | Free tier limit |
|------|--------|------------------|
| Ahrefs API | `keywords_explorer` | API plan dedicated, no free |
| SEMrush API | `phrase_kdi`, `phrase_related` | Pro plan minimum |
| Moz API | `keyword_metrics` | Pro plan |
| Ubersuggest | Web scrape (fragile) o API plan | 3 query/day free |
| Search Console | API `searchanalytics.query` | Free, own site only |
| Google Autosuggest | WebFetch SERP suggest | Free, manual |

Default if no API key: Search Console (own keyword) + Google Autosuggest expansion + manual cluster identification + bucketed volume.

## CLI invocation

```bash
python3 scripts/keyword_clusters.py \
  --seed "ecommerce analytics" "shopify analytics" \
  --geo italia \
  --site-type saas_b2b \
  --competitors competitor1.com,competitor2.com \
  --output cluster.json
```

## Output downstream

Cluster JSON → consumed da:
- Main agent Fase 3 (strategy synthesis)
- `content-audit` skill (gap analysis vs competitor)
- `geo-optimizer` skill (pillar identification per GEO layer)

## References

- `references/keyword-research-frameworks-2026.md` — pillar+cluster framework + 4 strategy approaches
- `references/seo-best-practices-2026.md` — search intent + long-tail post AI Overview
- `references/tool-ecosystem-seo-2026.md` — Ahrefs vs SEMrush vs Moz vs SE Ranking comparison

## Examples

### Example 1: SaaS B2B greenfield

Input: seed=["analytics ecommerce", "shopify analytics"], site_type=saas_b2b, geo=italia.

Output: 4 cluster (analytics features, BI tools comparison, KPI guide, integration recipes), 60+ keyword totale, top opportunity score 78 ("shopify analytics dashboard 2026"), 25 long-tail.

### Example 2: Content blog plateau

Input: seed=["content marketing italia"], site_type=content_blog, geo=italia, no API key.

Output: clustering manuale via Google Autosuggest + Search Console, 3 cluster (strategy, tools, case studies), 40 keyword bucketed (low/med/high), warning «volume_estimated_no_api: true → consigliato Ubersuggest free per refinement».
