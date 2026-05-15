# Tool Ecosystem 2026 — Competitive Intelligence Stack

> Reference completa con pricing 2026, access mode, capability matrix e recipes per ogni tool del competitive intelligence stack. Verificato Aprile 2026.

## Quick comparison tabella

| Tool | Tier (Quick/Standard/Deep) | Pricing 2026 | Access mode | Coverage |
|------|----------------------------|--------------|-------------|----------|
| **Playwright MCP** | Quick + | Free (self-host) | MCP nativo | Homepage scrape JS-render |
| **Apify zen-studio actor** | Standard | $3.99/1000 reviews | API + MCP nativo | G2 + Trustpilot + Capterra + TrustRadius + Gartner |
| **parallel-cli** | Standard | API key Filippo (~$0.5/query) | CLI Bash | Long-tail Reddit + HN + blog mention |
| **WebSearch / WebFetch** | Standard | Built-in Claude Code | Tool builtin | Cross-check public info |
| **NotebookLM CLI** | Optional | Free (Google) | CLI | Cross-check ground citations |
| **SimilarWeb** | Deep | $129.95/mo Starter | Web UI + API enterprise | Traffic intelligence |
| **SemRush** | Deep | $139.95-499.95/mo | Web UI + API | Keyword + content gap |
| **Ahrefs** | Deep | $129+/mo | Web UI + API enterprise | Backlink + content gap |
| **Crunchbase** | Deep | $29-49/user/mo (Starter/Pro) | API REST | Funding + M&A + hiring |
| **BuiltWith** | Deep | Premium custom (high) | API | Tech stack detection |
| **LinkedIn Sales Navigator** | Deep | $99/mo per seat | API + UI | Hiring trends + key people |

## Detail per tool

### Playwright MCP (Required primary)

**Cosa fa**: scrape pagine JS-rendered (SPA Next.js, React, Vue) per estrarre testo + struttura DOM.

**Use case nel pipeline**:
- Homepage / About / Product / Pricing scrape per `positioning-mapper`
- Corpus aggregato per `tov-analyzer`
- Anti-bot detection (Cloudflare challenge bypass via real browser)

**Pricing 2026**: Free (self-host MCP server).

**Setup**:
```bash
# MCP server già installato in ambiente Filippo (verifica .claude.json)
npx @playwright/mcp@latest
```

**Recipes**:

```python
# Esempio 1 — Scrape homepage Make
mcp.call("browser_navigate", {"url": "https://make.com"})
mcp.call("browser_wait_for", {"time": 1.5})  # JS render wait
snapshot = mcp.call("browser_snapshot")  # DOM accessibility tree
text = mcp.call("browser_evaluate", {"function": "() => document.body.innerText"})
```

```python
# Esempio 2 — Scrape pricing con structured extraction
mcp.call("browser_navigate", {"url": "https://make.com/pricing"})
pricing_text = mcp.call("browser_evaluate", {"function": "() => Array.from(document.querySelectorAll('.pricing-tier')).map(el => ({name: el.querySelector('h3')?.innerText, price: el.querySelector('.price')?.innerText}))"})
```

**Rate limit safe**: 2 secondi tra navigate stesso dominio.

**Fallback**: se Playwright non disponibile → `Bash(curl:*)` + html parsing (degraded, no JS render, log warning).

### Apify zen-studio actor (Required primary per reviews)

**Actor ID**: `zen-studio/software-review-scraper`

**Cosa fa**: scrape G2 + Trustpilot + Capterra + Gartner + TrustRadius in 1 chiamata, output dataset structured.

**Pricing 2026**: $3.99 / 1.000 reviews. Apify usage cost addizionale (~$0.25/CU).

**Maintenance**: ultima mod 8gg fa al 2026-04-30. 51 utenti totali / 27 attivi mensili. Rating 4.0/5.

**Input schema**:
```json
{
  "query": "Make",
  "platforms": ["G2", "Trustpilot"],
  "maxResults": 100,
  "includeProsAndCons": true,
  "sortBy": "most_recent"
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
  "content": "intuitive drag-drop UI saved me hours weekly",
  "pros": "Easy to use, 10000+ integrations",
  "cons": "Pricing scales steep for enterprise",
  "reviewer_role": "VP Operations",
  "reviewer_company_size": "500-1000",
  "verified": true,
  "date": "2026-03-15",
  "url": "https://g2.com/products/make/reviews/g2-12345"
}
```

**Rate limit defaults safe**:
- G2: 5s tra request
- Trustpilot: 3s
- Capterra: 5s
- Gartner: 10s (more strict)

**Fallback chain ordered**:
1. `zen-studio/software-review-scraper` (primary)
2. `focused_vanguard/multi-platform-reviews-scraper`
3. `taroyamada/g2-capterra-review-intelligence`
4. `samstorm/g2-capterra-review-scraper`
5. ❌ `lanky_quantifier/b2b-review-intelligence` (DEPRECATED — non usare)

### parallel-cli

**Cosa fa**: research + extract + search + enrich CLI per long-tail signal.

**Pricing 2026**: API key Filippo (in `~/.zshrc`), pay-per-query (~$0.5).

**Setup**: già installato (`~/.npm-global/bin/parallel-cli`).

**Recipes**:

```bash
# Long-tail Reddit r/SaaS mention
parallel-cli search "site:reddit.com/r/SaaS Make automation" --max 10

# Deep research su topic
parallel-cli research run "Make.com pricing change 2026 customer reaction"

# Enrich business info
parallel-cli enrich --type business --name "Make" --domain "make.com"
```

**Use case**: per claim non in homepage, non in reviews G2 (e.g., founder pivot story, recent layoffs, blog mention non-corp).

### Crunchbase API (Deep tier)

**Cosa fa**: funding rounds + M&A + leadership hires.

**Pricing 2026**:
- Free basic search (limited)
- Starter: $29/user/mo
- Pro: $49/user/mo
- Enterprise: custom

**API endpoint**: `https://api.crunchbase.com/api/v4/`

**Recipes**:

```python
import requests

# Get funding rounds for "Make"
r = requests.get(
    "https://api.crunchbase.com/api/v4/searches/funding_rounds",
    params={"user_key": API_KEY,
            "field_ids": "name,announced_on,money_raised_usd,investor_identifiers",
            "query": [{"type": "predicate", "field_id": "funded_organization_identifier", "operator_id": "includes", "values": ["make-com"]}]}
)
```

**Output**: list of {round_type (Seed, Series A, B, etc.), amount_usd, date, investors}.

### BuiltWith API (Deep tier)

**Cosa fa**: tech stack detection (analytics, hosting, marketing automation, payment, security tools).

**Pricing 2026**: premium custom enterprise (caro). Free limited tier disponibile.

**API endpoint**: `https://api.builtwith.com/v20/api.json?KEY=<>&LOOKUP=make.com`

**Output**: list of technologies con first/last detected date.

### SimilarWeb / SemRush / Ahrefs (Deep tier)

Tutti e 3 hanno API enterprise, pricing $129-499/mo. Usati solo se cliente già ha account (no setup nuovo per single analisi).

**Use case nel pipeline**: solo Deep tier strategic analysis (3+ giorni). Non default.

## Pricing total stimato per analisi

### Quick scan (1-3 competitor, 2h)

- Playwright: $0
- Apify (1 platform × N comp × ~50 reviews): $3-5
- parallel-cli (~5 query): $2.50
- **Total**: ~$5-8

### Standard dossier (3 competitor, 1d)

- Playwright: $0
- Apify (2 platform × 3 comp × ~80 reviews): $15-20
- parallel-cli (~15 query): $7.50
- WebFetch / WebSearch: built-in
- **Total**: ~$22-28

### Deep strategic (5 competitor, 3d)

- Playwright: $0
- Apify (3 platform × 5 comp × ~100 reviews): $40-50
- parallel-cli (~30 query): $15
- BuiltWith API (5 lookup): ~$10 (free tier limit)
- Crunchbase Pro (1 mese seat): $49
- LinkedIn Sales Nav (assume cliente già ha): $0 marginal
- **Total**: ~$115-130

## Anti-pattern

- **NO bulk scrape senza rate-limit safe** — sempre default delay
- **NO usare actor DEPRECATED** — sempre fallback chain
- **NO setup nuovo SemRush/Ahrefs** per single analisi (over-cost) — solo se cliente già ha
- **NO LinkedIn Sales Nav scrape behind login** senza account utente esplicito — anti-pattern #7

## Reference

- [Apify Store — zen-studio actor](https://apify.com/zen-studio/software-review-scraper/api)
- [Crunchbase API docs](https://docs.crunchbase.com/reference)
- [BuiltWith API docs](https://www.builtwith.com/api)
- [SemRush API docs](https://developer.semrush.com)
- [Riff Analytics — 12 Best Competitive Analysis Tools 2026](https://www.riffanalytics.ai/blog/best-competitive-analysis-tools)
- [Octoparse — 8 Competitor Analysis Tools 2026](https://www.octoparse.com/blog/competitor-analysis-tools)
- `research/research-summary.md` RQ3 — fonte derivazione pricing
