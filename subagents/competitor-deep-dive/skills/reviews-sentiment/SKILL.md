---
name: reviews-sentiment
description: Estrae sentiment grounded da reviews G2/Trustpilot/Capterra di un competitor via Apify zen-studio actor (multi-platform 1 chiamata, $3.99/1k). Output reviews.json con sentiment breakdown %, top 5 strengths/weaknesses/JTBD, Love-Hate-Want — ogni claim ha review_id + verbatim quote + URL. Anti-hallucination MANDATORY — se Apify fail / no reviews / rate limit → output insufficient_evidence (mai inventare review_id o quote). Rate-limit safe defaults (G2 5s, Trustpilot 3s, Capterra 5s). Da usare in parallel a tov-analyzer dopo positioning-mapper.
when_to_use: Pipeline `/competitor-deep-dive` Fase 2c (parallel a tov-analyzer). Anche per audit "cosa pensano i customer di NOI" (passa cliente come "competitor"). Anche per detect post-launch sentiment shift (re-run 30gg dopo release).
allowed-tools: Read Write Bash(python:*)
---

# Reviews Sentiment

Trasforma 1 competitor (`name + platforms`) in reviews sentiment grounded JSON. Apify zen-studio actor multi-platform G2+Trustpilot+Capterra+Gartner+TrustRadius in 1 chiamata. Anti-hallucination by design: ogni claim ha review_id + verbatim quote + URL.

## When to use

Attivare quando:

- Pipeline `/competitor-deep-dive` Fase 2c — input: competitor name + platforms da config
- Audit own brand sentiment ("cosa pensano di NOI") con cliente come input
- Detect post-launch sentiment shift (re-run 30gg dopo release)
- Pre-feature prioritization: estrai "Want" customer per validare roadmap

Non attivare se:

- Profondità analisi `quick` con multi-platform (Quick scan = 1 platform only)
- Apify MCP non disponibile (block + fallback parallel-cli search degradato — flag warning utente)
- Competitor very new (<6 mesi launch) — fallback Reddit/HN mention
- B2B vendor con 0 reviews G2 confermato → skip

## Prerequisiti

- `apify` MCP available (REQUIRED) — primary actor `zen-studio/software-review-scraper`
- `<memory>/config.md` con `analysis.reviews_focus[]` definito
- Reference `references/apify-actors-recipes.md` accessibile (input schema)

## Instructions

### Fase 1 — Validate platforms + actor selection

Da config `analysis.reviews_focus[]` (subset di `[G2, Trustpilot, Capterra]`):

| Reviews focus | Actor selezionato (priority) |
|---------------|------------------------------|
| `[G2, Trustpilot, Capterra]` (all) | `zen-studio/software-review-scraper` (multi-platform, 1 chiamata, ottimale) |
| `[G2, Trustpilot]` | `zen-studio/software-review-scraper` |
| `[G2]` only | `scrapepilot/g2-software-reviews-scraper-ratings-pros-cons` (G2-specialized, pros/cons strutturati) |
| `[Capterra]` only | `imadjourney/capterra-reviews-scraper` |
| `[Trustpilot]` only | `zen-studio/software-review-scraper` (Trustpilot-capable) |

**Fallback chain** se primary fallisce:
1. `zen-studio/software-review-scraper` (primary)
2. `focused_vanguard/multi-platform-reviews-scraper`
3. `taroyamada/g2-capterra-review-intelligence`
4. `samstorm/g2-capterra-review-scraper`
5. **DEPRECATO** `lanky_quantifier/b2b-review-intelligence` — NON usare

### Fase 2 — Run Apify actor

```bash
python scripts/reviews_apify.py \
  --competitor "<name>" \
  --platforms "G2,Trustpilot" \
  --actor "zen-studio/software-review-scraper" \
  --max-reviews-per-platform 100 \
  --rate-limit-g2 5 \
  --rate-limit-trustpilot 3 \
  --rate-limit-capterra 5 \
  --output output/reviews_<slug>.json
```

Lo script:
1. Costruisce input Apify schema (es. `{"query": "<competitor>", "maxResults": 100}`)
2. Invoca via MCP `apify` `call-actor` (preferito) o `apify` REST API direct
3. Parse output dataset → JSON normalizzato con review_id + quote + rating + date + URL
4. Apply rate-limit safe defaults per platform
5. Se rate limit hit → checkpoint + retry exponential backoff (5s, 30s, 5min)
6. Se 3 retries fail → output `insufficient_evidence: true, reason: "rate_limit_persistent"` + log

**Rate-limit defaults safe** (mai bypass):
- G2: 5 secondi tra request
- Trustpilot: 3 secondi
- Capterra: 5 secondi
- BuiltWith: 2 secondi

### Fase 3 — Sentiment classification

Per ogni review:
- Rating ≥4 → `positive`
- Rating == 3 → `neutral`
- Rating ≤2 → `negative`

Compute breakdown:
```python
positive_pct = (count_positive / total_reviews) * 100
neutral_pct = (count_neutral / total_reviews) * 100
negative_pct = (count_negative / total_reviews) * 100
```

### Fase 4 — Theme extraction (anti-hallucination MANDATORY)

#### Top 5 strengths

Cluster review verbatim quotes per theme via:
1. Extract pros field (Apify output strutturato)
2. Cluster simili (es. "intuitive UI" + "easy to use" + "drag drop simple" → theme "Ease of use")
3. Per theme: count frequency + select 2-3 best evidence quotes
4. Top 5 themes by frequency

**Schema obbligatorio** per ogni theme:
```json
{
  "theme": "Ease of use / drag-drop UI",
  "frequency": 47,
  "evidence": [
    {
      "review_id": "g2-12345",
      "quote": "intuitive drag-drop UI saved me hours weekly",
      "rating": 5,
      "date": "2026-03-15",
      "url": "g2.com/products/make/reviews/g2-12345",
      "reviewer_role": "VP Operations" // optional
    },
    ...
  ]
}
```

**Anti-hallucination**: se `evidence[].review_id` mancante o quote non verbatim da review estratta → BLOCK output, fail loud.

#### Top 5 weaknesses

Stesso pattern su `cons` field. Esempi: "steep learning curve advanced", "pricing enterprise-only", "limited mobile support", "documentation gaps", "slow customer support".

#### Top 3 JTBD (Jobs-To-Be-Done)

Cluster verbatim per outcome che il customer "hires" il prodotto per fare:
- "build automation 10x faster than manual"
- "replace 3 separate tools with 1 unified"
- "scale workflow without engineering ticket"

Per ogni JTBD: frequency + 2 evidence quotes.

#### Love-Hate-Want

Mining specifico:
- **Love**: cosa adorano e non vogliono mai perdere
- **Hate**: cosa odiano (potenziale opportunità differentiation per noi)
- **Want**: cosa chiedono e ancora nessuno offre (potenziale blue ocean)

```json
{
  "love_hate_want": {
    "love": [
      {"text": "Drag-drop visual UI", "frequency": 47, "evidence_review_ids": ["g2-12345", "g2-12346"]},
      ...
    ],
    "hate": [
      {"text": "Steep curve for advanced workflows", "frequency": 32, "evidence_review_ids": [...]},
      ...
    ],
    "want": [
      {"text": "AI-assisted suggestion for next module", "frequency": 12, "evidence_review_ids": [...]},
      ...
    ]
  }
}
```

### Fase 5 — Quality flags

- `low_confidence_pre_verified`: review pre-2024 (G2 dropped paid review program 2024) — flag review se `date < 2024-01-01`
- `bot_review_suspected`: pattern repetitive language → flag e suggest manual review
- `competitor_drive_by_review`: rating low + reviewer linked competitor → flag possibile sabotaggio

### Fase 6 — Build reviews.json

```json
{
  "competitor": "Make",
  "platforms": ["G2", "Trustpilot"],
  "scrape_date": "2026-04-30",
  "actor_used": "zen-studio/software-review-scraper",
  "actor_run_id": "<apify_run_id>",
  "rate_limit_applied": {"G2": 5, "Trustpilot": 3},
  "total_reviews_scraped": {"G2": 142, "Trustpilot": 89, "total": 231},
  "low_confidence_pre_verified_count": 23,
  "sentiment_breakdown": {
    "G2": {"positive_pct": 62, "neutral_pct": 25, "negative_pct": 13},
    "Trustpilot": {"positive_pct": 70, "neutral_pct": 18, "negative_pct": 12},
    "weighted_avg": {"positive_pct": 65, "neutral_pct": 22, "negative_pct": 13}
  },
  "top_strengths": [
    {"theme": "Ease of use / drag-drop UI", "frequency": 47, "evidence": [...]}
  ],
  "top_weaknesses": [
    {"theme": "Steep curve for advanced", "frequency": 32, "evidence": [...]}
  ],
  "top_jtbd": [
    {"outcome": "Build automation 10x faster than manual", "frequency": 38, "evidence": [...]}
  ],
  "love_hate_want": {...},
  "insufficient_evidence": false,
  "cost_usd": 4.50
}
```

### Fase 7 — Validate output

Pre-write validation:
- [ ] `total_reviews_scraped.total >= 10` (else `insufficient_evidence: true`)
- [ ] Ogni `evidence[].review_id` non vuoto
- [ ] Ogni `evidence[].quote` non vuoto e <500 char
- [ ] Ogni `evidence[].url` regex valid (g2.com, trustpilot.com, capterra.com)
- [ ] `sentiment_breakdown` percentuali sommano a 100 (±2 tolerance)
- [ ] `cost_usd` calcolato basato su Apify pricing

## Output examples

Caso success: vedi JSON Make sopra.

Caso insufficient_evidence:
```json
{
  "competitor": "NewProduct",
  "platforms": ["G2"],
  "scrape_date": "2026-04-30",
  "actor_used": "zen-studio/software-review-scraper",
  "total_reviews_scraped": {"G2": 3, "total": 3},
  "insufficient_evidence": true,
  "reason": "Only 3 reviews on G2 (min 10 for sentiment significance)",
  "fallback_suggestion": "Use parallel-cli search 'site:reddit.com/r/SaaS <competitor>' for long-tail mentions",
  "cost_usd": 0.05
}
```

Caso rate-limit hit:
```json
{
  "competitor": "BigCo",
  "platforms": ["G2", "Trustpilot", "Capterra"],
  "scrape_date": "2026-04-30",
  "actor_used": "zen-studio/software-review-scraper",
  "actor_run_id": "<apify_run_id>",
  "rate_limit_hits": 3,
  "retries_exponential": [5, 30, 300],
  "insufficient_evidence": true,
  "reason": "rate_limit_persistent_after_3_retries",
  "fallback_suggestion": "Wait 1h then retry, or scrape only 1 platform at a time",
  "cost_usd": 1.20
}
```

## Anti-pattern

- **NO claim sentiment senza review_id + verbatim quote + URL** — output blocked, fail loud
- **NO inventare review_id** — solo da Apify dataset output
- **NO inventare frequency** — count effettivo dalle review estratte
- **NO bulk scrape senza rate-limit safe** — sempre default delay
- **NO ignorare anti-bot detection** — se Cloudflare challenge, retry esponenziale, no bypass
- **NO scrape reviews behind login** (G2 has some private) — public only
- **NO usare actor DEPRECATED** (`lanky_quantifier/b2b-review-intelligence`) — fallback a chain alternativa

## Edge cases

- **Multi-language reviews** (G2 has EN + ES + DE): scrape all, segment by language, prefer EN for primary themes
- **Reviews stale** (last 12 months scarcity): widen window a 24 mesi, flag `recent_reviews_scarce: true`
- **Acquisition / Pivot recente**: review pre-pivot non actionable, flag `post_acquisition_volatility` e separa dataset pre/post
- **G2 verified buyer badge** (introdotto 2024): se review ha `verified: true` → boost evidence weight in clustering
- **Competitor drive-by review** (rating low + reviewer ha competitor link in profile): flag `competitor_drive_by_suspected`
- **Industry niche** (es. legaltech): G2 scarcity → fallback Trustpilot + Reddit specialty
- **EU competitor scraping reviews fuori UE** (G2 USA-hosted): GDPR cross-border — verify in LIA template

## Reference

- `references/apify-actors-recipes.md` — actor IDs maintained 2026 + input schema esempi
- `references/gdpr-scraping-compliance.md` — rate-limit safe defaults per platform
- [Apify Store — zen-studio actor](https://apify.com/zen-studio/software-review-scraper/api)
- `research/research-summary.md` RQ4 — sentiment grounded methodology
