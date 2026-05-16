# Content Audit Methodology 2026

> Reference doc per skill `content-audit`. Gap analysis vs competitor, decay detection, refresh priority queue, ROI calculation per content piece.

## Audit phases

```
1. Inventory existing content
2. Performance baseline (90gg + 90gg precedenti delta)
3. Decay detection
4. Gap analysis vs competitor
5. Refresh priority scoring
6. Content brief generation
```

## 1. Inventory

Source:
- Sitemap.xml parse (primary)
- CSV manual export (fallback)
- CMS DB query (Wordpress wp_posts table, ecc.)

Per URL extract:
- Title
- H1
- H2 list (hierarchy)
- Word count
- DateModified (visible o schema dateModified)
- Schema type (Article? Product?)
- Author byline presence

Output: inventory CSV/JSON.

## 2. Performance baseline

Data source priority:

### Tier 1: Search Console API

- `searchanalytics.query` per 90gg + 90gg precedenti
- Capture: clicks, impressions, position, CTR per URL
- Calculate `traffic_delta_pct = (current - previous) / previous * 100`

### Tier 2: GA4 (se Search Console limited)

- `screenPageViews` event per page
- Source/medium = `google` + `organic`

### Tier 3: Manual user input

- Top performer list (top 30 page) input by user
- Decay flag manual

## 3. Decay detection

### Threshold

DECISION-007 in `/seo-strategist`:

| Status | Traffic delta 90d-90d |
|--------|------------------------|
| `decay: candidate_refresh` | < -30% |
| `decay: monitor` | -30% to -10% |
| `decay: healthy` | ≥ -10% |

### Root cause analysis (rule-based)

| Root cause | Signal |
|------------|--------|
| `staleness` | dateModified > 18 mesi ago + traffic decay |
| `competitor_outranked` | position_avg dropped > 5 |
| `ctr_issue` (likely AI Overview eat) | clicks dropped + impressions stable |
| `topic_decay` | clicks + impressions both dropped > 30% |
| `algorithmic_demote` | sudden drop coinciding with Google update |

Cross-reference with [Search Engine Land update tracker](https://searchengineland.com/library/seo) for `algorithmic_demote` confirmation.

## 4. Gap analysis vs competitor

### Methodology

Per ogni competitor in list (1-5):

1. Crawl competitor sitemap (rate-limit 1 req/2s)
2. Extract URL list + title/h1
3. Topical entity extraction (NER su title+h1)
4. Build entity coverage matrix:
   - own = set of entities covered
   - competitor1 = set
   - competitor2 = set
   - ...

5. Compare:
   - `topics_only_competitor` = (competitor1 ∪ competitor2 ∪ ...) - own
   - `topics_only_own` = own - (competitor1 ∪ ...) — your strengths
   - `topics_shared` = own ∩ (competitor1 ∪ ...) — battle for ranking

### Gap prioritization

Per gap topic:
- `estimated_volume`: bucketed (low/med/high) via Google Trends + autosuggest count
- `competitor_coverage_count`: 1+ competitor cover = signal industry relevance
- `own_resources`: existing content related (could pivot vs new)
- `priority_score`: weighted formula

```
priority_score = (
  volume_weight * 30 +
  competitor_count * 10 +
  intent_match_score * 20 +
  difficulty_penalty * -10
)
```

### Output gap matrix

```json
{
  "topics_only_competitor": [
    {"topic": "AI marketing automation", "covered_by": ["c1", "c2"], "priority_score": 85}
  ],
  "topics_only_own": [
    {"topic": "B2B GTM engineering", "competitor_count": 0}
  ],
  "topics_shared": [
    {"topic": "...", "own_position": 8, "best_competitor_position": 3}
  ]
}
```

## 5. Refresh priority scoring

Per ogni decay candidate, calcola `refresh_priority_score` 0-100:

```
refresh_priority_score = (
  current_traffic_value * 30 +        # higher value = higher priority
  abs(traffic_delta_pct) * 0.5 +      # bigger decay = higher priority
  rankability_indicator * 20          # already ranking = easier to recover
) / normalization_factor
```

Where:
- `current_traffic_value` = clicks_90d * average_value_per_click (default €0.5 or user-specified)
- `rankability_indicator`:
  - position_avg <20 → 1.0 (already ranking, easy to recover)
  - 20-50 → 0.5
  - >50 → 0.0 (rebuild from scratch likely)

Score buckets:
- 80-100: P0 critical — refresh immediato
- 60-79: P1 high — sprint corrente
- 40-59: P2 medium — backlog
- <40: P3 low — re-evaluate o deprecate

## 6. Refresh ROI estimation

Per piece refresh:

```
roi_estimated = (recovery_potential * value_per_click) - refresh_cost

recovery_potential = clicks_pre_decay * 0.7  # 70% recovery realistic average
refresh_cost = (
  hours_writer * hourly_rate +
  hours_reviewer * hourly_rate +
  cms_publishing_overhead
)
```

Default values:
- `hourly_rate`: €40-80 (junior to senior writer)
- `cms_publishing_overhead`: €20-50 per piece
- `hours_writer`: 4-8 per refresh (vs 12-20 net new)
- `hours_reviewer`: 1-2

Refresh ROI > new content ROI in most cases (lower cost, faster ranking recovery).

## 7. Content brief generation

Per top 5-10 refresh candidate + top 5 gap opportunities:

```markdown
# Brief: <topic>

**Target keyword**: <kw> (volume X, KD Y, intent Z)
**Search intent**: <informational | commercial | ...>
**Word count target**: <wc> (basato top 3 ranking competitor + 20% bonus)
**E-E-A-T signal needed**: author byline + N expert quote + dateModified
**Competitor benchmark**:
- Top 1: <URL>, <wc> word, <key sections>
- Top 2: <URL>, <wc>, <sections>
- Top 3: <URL>, <wc>, <sections>
**Content outline**:
- H1: ...
- H2 q-format: ...
- H2: ...
**Schema**: Article + FAQPage (if Q&A in body) + Author Person
**GEO patterns**: H2 question-format + 1 citation per 250 word + author bio sameAs
**Internal link target**: <pillar URL>
**CTA**: <conversion goal>
**SEO checklist**:
- [ ] Title 50-60 char
- [ ] Meta description 130-155 char
- [ ] H1 includes primary KW
- [ ] 3-5 internal link
- [ ] Image alt descriptive
- [ ] Schema validated
- [ ] dateModified updated
```

## Anti-pattern content audit

1. **Mass refresh sprint** — refresh 50 piece in 1 settimana → Google sees pattern + may de-rank
2. **Refresh without intent change** — same content, different date → no signal change
3. **Boilerplate refresh** ("Updated 2026" inserito) — penalty risk
4. **Cannibalization** — refresh creates 2 page same intent
5. **Skip search intent re-validation** — query intent può shift over time
6. **Auto-AI rewrite** — Helpful Content red flag

## Success metrics post-audit

4-week:
- Refresh queue execution rate (target 80%+ delivered)
- Schema validity 100%
- Internal linking audit fix complete

12-week:
- Decay candidate recovery rate (target 50%+ recovered to baseline)
- Gap content publication (target top 5 opportunity addressed)
- Organic clicks delta vs baseline +10% target

24-week:
- Cluster authority signal (top 3 ranking cluster items improved)
- AI-referred sessions detected (if GEO=priority)
- Content portfolio quality score (Helpful Content compliance)

## Refresh frequency cycle

Best practice 2026:
- Pillar pages: refresh every 6-12 mesi
- Cluster supporting: refresh every 12-18 mesi
- Decay candidate: refresh ad hoc when threshold hit
- Programmatic SEO: monitor + spot-fix monthly
- Evergreen content: refresh annually

## Sources

### Primary
- [Google Search Central — content updates](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)

### Secondary
- [Ahrefs Blog — content decay](https://ahrefs.com/blog/content-decay/)
- [Wellows — when to update content for better SEO](https://wellows.com/blog/update-strategy/)
- [Search Engine Land — content audit guide](https://searchengineland.com/guide/content-audit)
- [Backlinko — content refresh strategy](https://backlinko.com/content-refresh)
