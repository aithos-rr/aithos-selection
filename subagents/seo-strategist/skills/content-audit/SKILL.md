---
name: content-audit
description: Gap analysis vs competitor + content decay detection + refresh priority queue + optimization opportunity per content blog/SaaS B2B/eCommerce. Da domain + competitor list + (optional) Search Console export a JSON {audit_findings, refresh_priority, gap_opportunities, decay_pages, content_briefs[]}. Threshold decay -30% traffic vs 90gg precedenti = candidate refresh. Anti-hallucination — mai stimare traffic numero senza data source, output sempre `data_source` flag esplicito (search_console, manual_input, web_extraction).
when_to_use: Audit content esistente per piano refresh, gap analysis vs 1-5 competitor, decay detection post Google update, brief generation per content team, prioritizzazione refresh queue mensile
---

# Content Audit

Skill che mappa lo stato del content asset esistente vs competitor + identifica decay + prioritizza refresh actionable.

## Scope

- **In scope**: gap analysis vs competitor (topic coverage), decay detection (traffic loss vs benchmark), refresh priority scoring, content brief generation per piece, refresh ROI estimation
- **Out of scope**: keyword research da scratch (vedi `keyword-research`), schema markup (vedi `schema-generator`), full content writing

## Input contract

```yaml
domain: example.com
competitor_domains: ["competitor1.com", "competitor2.com"]  # 1-5
search_console_export: path/to/sc-90day.csv  # optional
existing_content_list: path/to/content-inventory.csv  # optional, fallback sitemap parse
content_volume_target: 5_15  # da Q7 discovery
geo_target: italia
site_type: content_blog
```

## Methodology

### Step 1 — Inventory existing content

1. Se `existing_content_list` provided → load CSV
2. Fallback: parse sitemap.xml + crawl URL list (limit 1000)
3. Extract per URL: title, h1, h2, word_count, dateModified, schema type
4. Save inventory JSON

### Step 2 — Performance baseline

Per ogni URL inventoried:
1. Se Search Console connected → query `searchanalytics.query` per 90gg + 90gg precedenti delta
2. Capture: clicks, impressions, position, CTR
3. Calculate `traffic_delta_pct = (current - previous) / previous * 100`

**Output field per URL**: `{url, clicks_90d, impressions_90d, position_avg, traffic_delta_pct, status: declining|stable|growing}`

### Step 3 — Decay detection

Threshold (DECISION da BUILD-BRIEF emergent #3):
- `traffic_delta_pct < -30%` → `decay: candidate_refresh`
- `traffic_delta_pct -30% to -10%` → `decay: monitor`
- `traffic_delta_pct >= -10%` → `decay: healthy`

Root cause analysis (rule-based):
- `dateModified > 18 mesi ago` → cause: `staleness`
- `position_avg dropped > 5` → cause: `competitor_outranked`
- `clicks dropped + impressions stable` → cause: `ctr_issue` (likely AI Overview eat)
- `clicks + impressions both dropped > 30%` → cause: `topic_decay` o `algorithmic_demote`

### Step 4 — Gap analysis vs competitor

Per ogni competitor in list:
1. Crawl competitor sitemap + extract content topic (URL slug + title + h1)
2. Topical entity extraction (NER su title+h1)
3. Compare entity coverage own vs competitor
4. Output gap matrix:
   - `topics_only_competitor[]` — topic dove competitor copre, tu no
   - `topics_only_own[]` — topic dove tu copri, competitor no (tuoi punti forza)
   - `topics_shared[]` — topic in comune (battle for ranking)

### Step 5 — Refresh priority scoring

Per ogni decay candidate, calcola `refresh_priority_score` 0-100:

```
refresh_priority_score = (
  current_traffic_value * 30 +        # higher value = higher priority
  -traffic_delta_pct * 0.5 +          # bigger decay = higher priority
  rankability_indicator * 20          # already ranking = easier to recover
) / normalization_factor
```

`current_traffic_value`: clicks_90d * average_value_per_click (default €0.5 if not specified)
`rankability_indicator`: 1 if position_avg <20, 0.5 if 20-50, 0 if >50

### Step 6 — Content brief generation

Per top 5-10 refresh candidate + top 5 gap opportunities, generate brief:

```markdown
# Brief: <topic>

**Target keyword**: <kw>
**Search intent**: <intent>
**Word count target**: <wc>
**E-E-A-T signal needed**: author byline + N expert quote
**Competitor benchmark**: top 3 ranking URL + word count + outline
**Schema**: Article + FAQPage (if Q&A in body)
**GEO patterns**: H2 question-format + 1 citation per 250 word + author bio
**Internal link target**: <pillar URL>
**CTA**: <conversion goal>
```

## Output JSON schema

```json
{
  "domain": "example.com",
  "audit_date": "2026-05-01",
  "data_sources": ["search_console", "sitemap_crawl"],
  "inventory": {"total_urls": 142, "indexed": 138, "non_indexed": 4},
  "decay_summary": {
    "candidate_refresh": 12,
    "monitor": 25,
    "healthy": 101
  },
  "decay_pages": [
    {
      "url": "/blog/...",
      "clicks_90d": 450,
      "traffic_delta_pct": -42,
      "root_cause": "staleness",
      "refresh_priority_score": 78,
      "data_source": "search_console"
    }
  ],
  "gap_opportunities": [
    {
      "topic": "AI marketing automation",
      "competitor_coverage": ["competitor1.com/x", "competitor2.com/y"],
      "own_coverage": null,
      "estimated_volume": "medium",
      "priority_score": 85
    }
  ],
  "content_briefs": [
    {"topic": "...", "brief_path": "output/brief-001.md"}
  ],
  "anti_hallucination_flags": {
    "traffic_estimated_no_gsc": false,
    "competitor_data_partial": false
  }
}
```

## Anti-hallucination contract

- Mai inventare clicks/impressions/position number senza Search Console data o user input. Flag `traffic_estimated_no_gsc: true` + use qualitative bucketing
- Competitor crawl rate-limited 1 req/2s default (rispettare robots.txt)
- Se competitor blocca crawl → flag `competitor_data_partial: true` + suggest manual user input
- Se <20 URL in inventory → `insufficient_evidence` + suggest sitemap fix

## Edge cases

1. **No Search Console access** → fallback qualitative audit (manual user input top performer + manual decay flag)
2. **Site <20 page** → audit limitato, focus su quality individual page
3. **Programmatic SEO site (1000+ page)** → sample 50 random + cluster analysis instead of full
4. **JS-heavy site no SSR** → audit limited (scrape no full DOM) → suggest Playwright MCP o Vercel SSR
5. **Multi-language site** → audit per lingua separato
6. **Boilerplate >70%** → flag Helpful Content red flag + unique-value injection suggest

## Tool integration

| Tool | Method | Note |
|------|--------|------|
| Search Console | API `searchanalytics.query` | Best data source. Free. |
| Ahrefs Site Audit | UI export → CSV | Pro plan |
| Screaming Frog | Desktop crawl | 500 URL free, then £199/yr |
| Ubersuggest content idea | Web | Free 3 query/day |
| WebFetch competitor | URL crawl | Rate-limited |

## CLI invocation

```bash
python3 scripts/content_brief_gen.py \
  --domain example.com \
  --competitors competitor1.com,competitor2.com \
  --gsc-export sc-90day.csv \
  --geo italia \
  --output-dir output/
```

## Output downstream

Audit JSON → consumed da:
- Main agent Fase 3 (strategy synthesis) + Fase 6 (reporting)
- `geo-optimizer` skill (pillar identification + GEO layer per top refresh candidate)
- `/document-factory` (PDF report content audit)

## References

- `references/content-audit-methodology.md` — gap analysis methodology, decay detection, refresh ROI
- `references/seo-best-practices-2026.md` — Helpful Content compliance check
- `references/keyword-research-frameworks-2026.md` — cluster mapping integration

## Examples

### Example 1: Content blog plateau (40 page)

Input: domain=blog.example.com, competitors=[a.com, b.com], GSC connected.

Output: inventory 38 URL, 8 decay candidate (top refresh: blog/seo-2024 -52% traffic), 5 gap opportunity (AI marketing not covered), 5 content brief generated.

### Example 2: eCommerce decay post-Core Update

Input: domain=shop.example.com, competitors=[zalando.it, asos.com], GSC connected, decay 40% overall.

Output: 28 category page in decay (root cause `thin_content` + `competitor_outranked`), 12 refresh priority high (>70 score), recovery roadmap 90gg con priorità by score.
