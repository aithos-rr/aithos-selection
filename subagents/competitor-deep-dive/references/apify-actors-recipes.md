# Apify Actors Recipes 2026 — Reviews + Tech + Funding Scrape

> Reference completa Apify actor maintained 2026 + input schema + recipes pratiche. Verificato Aprile 2026 via Apify Store. Used by `reviews-sentiment` skill + scripts/reviews_apify.py.

## Apify in 30 secondi

- **Marketplace serverless** di scraper ("actors") + browser automation
- **Pricing**: $0.25/CU credit + actor-specific cost (tipicamente $1-10 per 1000 results)
- **Output**: dataset (JSON/CSV/Excel) + key-value store
- **MCP server nativo**: `mcp__apify__call-actor` per chiamata diretta da Claude
- **Rate limit**: gestito automaticamente da Apify worker queue

## Reviews scraping — actor chain

### Primary (raccomandato)

#### `zen-studio/software-review-scraper`

**Tipo**: multi-platform reviews
**Coverage**: G2, Capterra, TrustRadius, Gartner, Trustpilot
**Pricing**: $3.99 / 1.000 reviews
**Maintenance**: ✓ ultimo update 8gg fa al 2026-04-30
**Rating Apify**: 4.0/5 (1 review)
**Active users**: 27 mensili

**Input schema**:
```json
{
  "query": "Make",
  "platforms": ["G2", "Trustpilot"],
  "maxResults": 100,
  "includeProsAndCons": true,
  "sortBy": "most_recent",
  "language": "en"
}
```

**Output schema** (per review):
```json
{
  "review_id": "g2-12345",
  "platform": "G2",
  "competitor_slug": "make",
  "rating": 5,
  "title": "Best workflow tool I've used",
  "content": "intuitive drag-drop UI saved me hours weekly...",
  "pros": "Easy to use, 10000+ integrations",
  "cons": "Pricing scales steep for enterprise",
  "reviewer_role": "VP Operations",
  "reviewer_company_size": "500-1000",
  "verified": true,
  "date": "2026-03-15",
  "url": "https://g2.com/products/make/reviews/g2-12345",
  "language": "en"
}
```

**Recipe Bash**:
```bash
# Via Apify CLI (non-MCP path)
apify call zen-studio/software-review-scraper \
  --input '{"query":"Make","platforms":["G2","Trustpilot"],"maxResults":100}' \
  --output-dataset-id make_reviews
```

**Recipe MCP** (preferito):
```python
mcp.call("apify__call-actor", {
    "actor_id": "zen-studio/software-review-scraper",
    "input": {"query": "Make", "platforms": ["G2", "Trustpilot"], "maxResults": 100},
    "async": False
})
```

### Fallback chain (se primary fail)

| Priority | Actor ID | Coverage | Pricing |
|----------|----------|----------|---------|
| 2 | `focused_vanguard/multi-platform-reviews-scraper` | G2 + Capterra + Trustpilot | ~$5/1k |
| 3 | `taroyamada/g2-capterra-review-intelligence` | G2 + Capterra only | ~$4/1k |
| 4 | `scrapepilot/g2-software-reviews-scraper-ratings-pros-cons` | G2 only, pros/cons strutturati | ~$3/1k |
| 5 | `samstorm/g2-capterra-review-scraper` | G2 + Capterra | ~$4/1k |

### Specializzati

#### `imadjourney/capterra-reviews-scraper`

**Use case**: Capterra-specific (cross-link a GetApp + Software Advice automatic).

**Input schema**:
```json
{
  "productSlug": "make",
  "maxResults": 100
}
```

#### `sovereigntaylor/g2-reviews-scraper`

**Use case**: G2-specific con CLI binding nativo.

### ❌ DEPRECATED (NON usare)

- `lanky_quantifier/b2b-review-intelligence` — flag DEPRECATED visibile in Apify Store

## Tech stack scraping

### `builtwith-scraper` (3rd party Apify actor)

**Use case** (Deep tier only): tech stack detection se BuiltWith API costa troppo.

**Input schema**:
```json
{
  "domains": ["make.com", "n8n.io", "zapier.com"],
  "maxResults": 1
}
```

**Output**: list of technologies con first/last detected date.

**Note**: BuiltWith API ufficiale meno costosa per single lookup. Usa Apify per bulk batch (10+ domain).

## Crunchbase scraping

### `crunchbase-company-search` (3rd party)

**Use case**: funding rounds + leadership se Crunchbase API non disponibile.

**Input schema**:
```json
{
  "companyName": "Make",
  "domain": "make.com",
  "fields": ["funding_rounds", "investors", "leadership"]
}
```

**Note**: Crunchbase API ufficiale ($29-49/mo Pro) preferita per single project. Apify scrape per multi-tenant.

## Rate limit safe defaults (per platform)

Da impostare in actor input se actor lo supporta, altrimenti settati di default:

| Platform | Min delay | Max parallel | Note |
|----------|-----------|--------------|------|
| G2 | 5s | 3 | Cloudflare bot detection aggressiva |
| Trustpilot | 3s | 5 | Più permissivo |
| Capterra | 5s | 3 | Cross-link GetApp |
| Gartner | 10s | 1 | Strictest paywall |
| Crunchbase API | 1s | 10 | Pro tier 120 req/min |
| BuiltWith API | 2s | 5 | Free tier rate-limited |
| Generic homepage (Playwright) | 2s | 1 | Per dominio singolo |

## Cost estimation per analisi

### Quick scan (1-3 competitor, ~50 reviews per competitor, 1 platform)

```python
n_competitor = 3
reviews_per_competitor = 50
platforms = 1
cost_apify_actor = (n_competitor * reviews_per_competitor / 1000) * 3.99
cost_apify_cu = ~0.50  # CU usage stimato
total = cost_apify_actor + cost_apify_cu  # ~$1-3
```

### Standard dossier (3 competitor, ~100 reviews, 2 platform)

```python
n_competitor = 3
reviews_per_competitor = 100
platforms = 2
cost_apify_actor = (n_competitor * reviews_per_competitor * platforms / 1000) * 3.99
cost_apify_cu = ~2.00
total = cost_apify_actor + cost_apify_cu  # ~$15-20
```

### Deep strategic (5 competitor, ~150 reviews, 3 platform + tech + funding)

```python
total = ~$50-60
# Aggiunge BuiltWith API + Crunchbase API (single seat $49)
```

## Anti-pattern Apify

- **NO bulk scrape >5000 results in 1 run** — split in batch + checkpoint
- **NO ignorare rate limit hit** — exponential backoff (5s, 30s, 5min)
- **NO usare actor DEPRECATED** — sempre fallback chain
- **NO mock review_id** se Apify fail — output `insufficient_evidence` invece
- **NO hardcode API key** in script — usare env var `APIFY_TOKEN`
- **NO scrape behind login** anche con Apify (CNIL violation)

## Recipes — Common patterns

### Pattern 1: Multi-platform single competitor

```python
# Use case: Quick scan 1 competitor, 1 platform
result = mcp.call("apify__call-actor", {
    "actor_id": "zen-studio/software-review-scraper",
    "input": {"query": "Make", "platforms": ["G2"], "maxResults": 100}
})
reviews_dataset = mcp.call("apify__get-actor-output", {"run_id": result["runId"]})
```

### Pattern 2: Sequential batch competitor

```python
# Use case: Standard dossier 3 competitor, evita rate limit
import time
for competitor in ["Make", "n8n", "Zapier"]:
    result = mcp.call("apify__call-actor", {
        "actor_id": "zen-studio/software-review-scraper",
        "input": {"query": competitor, "platforms": ["G2", "Trustpilot"], "maxResults": 100}
    })
    save_to_local(result, f"output/reviews_{slug(competitor)}.json")
    time.sleep(5)  # safety delay tra batch
```

### Pattern 3: Fallback chain on failure

```python
PRIMARY = "zen-studio/software-review-scraper"
FALLBACKS = [
    "focused_vanguard/multi-platform-reviews-scraper",
    "taroyamada/g2-capterra-review-intelligence",
    "scrapepilot/g2-software-reviews-scraper-ratings-pros-cons"
]

def scrape_with_fallback(competitor, platforms):
    for actor in [PRIMARY] + FALLBACKS:
        try:
            return mcp.call("apify__call-actor", {
                "actor_id": actor,
                "input": {"query": competitor, "platforms": platforms, "maxResults": 100}
            })
        except (RateLimitError, ActorError) as e:
            log.warning(f"Actor {actor} failed: {e}, trying next")
            continue
    return {"insufficient_evidence": True, "reason": "all_actors_failed"}
```

### Pattern 4: GDPR EU mode con anonimizzazione

```python
# Auto-applicato se gdpr.mode_active = true
def anonymize_reviewer(review):
    review["reviewer_role"] = review.get("reviewer_role")  # keep role
    review.pop("reviewer_name", None)  # remove name
    review.pop("reviewer_email", None)  # remove email
    review.pop("reviewer_linkedin", None)  # remove personal links
    return review

reviews = [anonymize_reviewer(r) for r in scraped_reviews]
```

## Output verification

Pre-storage validation:

```python
def validate_apify_output(reviews_data):
    required_fields = ["review_id", "rating", "content", "url", "date"]
    valid_count = 0
    for r in reviews_data:
        if all(r.get(f) for f in required_fields):
            valid_count += 1
    completeness = valid_count / max(1, len(reviews_data)) * 100
    if completeness < 70:
        return {"valid": False, "completeness_pct": completeness, "warning": "low data quality"}
    return {"valid": True, "completeness_pct": completeness}
```

## Reference

- [Apify Store](https://apify.com/store) — marketplace
- [Apify CLI](https://docs.apify.com/cli) — local invocation
- [Apify MCP server](https://docs.apify.com/platform/integrations/mcp) — Claude integration
- `scripts/reviews_apify.py` — wrapper Python
- `skills/reviews-sentiment/SKILL.md` — orchestrator
- `research/research-summary.md` RQ4 — fonte derivazione actor list
