# Tool Ecosystem SEO 2026

> Reference doc per main agent + skill consumer. Ahrefs vs SEMrush vs Moz vs SE Ranking + budget tier + when to use what.

## Pricing snapshot (May 2026)

⚠ Prezzi indicativi USD (€ approssimativo). Verificare current prezzi sul sito vendor.

| Tool | Free tier | Lite | Standard | Pro | Enterprise |
|------|-----------|------|----------|-----|------------|
| **Ahrefs** | Webmaster Tools (own site) | $129 | $249 | $449 | $1499+ |
| **SEMrush** | 10 query/day | $139 | $249 | $499 | $999+ |
| **Moz Pro** | 10 query/day | $99 | $179 | $299 | $599+ |
| **SE Ranking** | trial 14gg | $55 | $109 | $239 | $499+ |
| **Ubersuggest** | 3 query/day | $29 | — | $49 | $99+ |
| **Search Console** | Free | Free | Free | Free | Free |
| **Screaming Frog** | 500 URL free | £199/anno | — | — | — |
| **Scrunch (GEO)** | trial | $99 | $299 | $499+ | Custom |
| **LLMrefs (GEO)** | trial | $99 | — | $299 | Custom |
| **Profound (GEO)** | — | — | — | — | Enterprise quote |

## Strengths comparison

### Ahrefs

**Strengths**:
- Backlink data più completo (industry leader)
- Site Explorer + Content Explorer ricco
- Rank Tracker accurato
- Keyword Explorer "Parent Topic" (cluster-friendly)
- API solid

**Weak**:
- Pricey vs alternatives
- Free tier ristrettissimo (Webmaster Tools own site only)

**Best for**: SEO specialist + agency multi-client + content team con budget.

### SEMrush

**Strengths**:
- All-in-one (SEO + ads + social + content)
- Competitor analysis robust
- Keyword Magic Tool ampio
- Position Tracking detailed
- Marketing API for integration

**Weak**:
- UI cluttered (many feature)
- Backlink index meno completo Ahrefs
- Price escalation per feature unlock

**Best for**: marketing manager all-in-one + multi-channel team.

### Moz Pro

**Strengths**:
- Domain Authority (DA) pioneer metric
- Page Authority (PA)
- MozBar Chrome extension free (great for quick check)
- Community + content educational solid

**Weak**:
- Backlink index più piccolo
- Less competitive vs Ahrefs/SEMrush in raw data

**Best for**: SEO specialist tradizionale + DA-based reporting (still industry-standard).

### SE Ranking

**Strengths**:
- Cost-effective
- Agency-friendly multi-project
- White-label reports
- Position Tracker accurato

**Weak**:
- Index gap regional (some markets meno coperti)
- Less ecosystem feature

**Best for**: agency con multipli clienti budget-conscious.

### Ubersuggest

**Strengths**:
- Cheap entry ($29/mese vs $99+ alternative)
- Neil Patel content + recipe
- Simple UI per beginner

**Weak**:
- Data quality variabile
- Index meno completo
- Free tier ristretto (3 query/day)

**Best for**: founder solo + freelancer SEO con budget <€50/mese.

### Search Console (Google)

**Strengths**:
- Free
- Owned data ground truth
- Coverage report critical
- Performance data 16 mesi

**Weak**:
- Solo own site
- 1000 row limit export
- No competitor data

**Best for**: TUTTI (mandatory). Fonte primaria own site.

### Screaming Frog SEO Spider

**Strengths**:
- Technical audit gold standard
- 500 URL free
- Full feature £199/anno
- Custom extraction (CSS selector)

**Weak**:
- Desktop-only
- Setup curve learning

**Best for**: technical audit deep + agency.

### GEO tools (categoria nuova 2026)

#### Scrunch

- $99-499/mese
- AI search visibility tracking (ChatGPT, Perplexity, Google AI Overview)
- First-mover, dashboard mature

#### LLMrefs

- $99/mese
- GEO citation tracking dedicated
- Limited language coverage

#### Profound

- Enterprise quote
- Ent-grade GEO tracking
- Multi-platform integration

#### Quattr

- Free trial + paid
- All-in-one AI search visibility
- Less specialized

## Budget tier recommendation (DECISION-010)

### Tier `lt100` (<€100/mese)

Stack:
- **Search Console** (free) — primary data source own site
- **Ubersuggest free** (3 query/day) — keyword expansion
- **Ahrefs Webmaster Tools** (free, own site only) — basic backlink data
- **Screaming Frog** (free 500 URL)
- **GA4** (free) — analytics
- **Manual GEO testing** (ChatGPT/Perplexity browser, free)

Workflow:
- Keyword research: Ubersuggest free + GSC own queries + Google Autosuggest manual
- Technical audit: Screaming Frog free + GSC URL Inspection
- Content audit: GSC export + manual analysis

### Tier `100_500` (€100-500/mese)

Stack option A (Ahrefs path):
- **Ahrefs Lite** ($129) — primary
- Search Console + GA4
- Screaming Frog full ($259/anno)

Stack option B (Moz path):
- **Moz Pro** ($99) — primary
- Search Console + GA4
- Screaming Frog full

⚠ **No double-spend**: Ahrefs OR Moz, non entrambi (DECISION-010 enforce).

### Tier `500_2k` (€500-2k/mese)

Stack:
- **Ahrefs Standard** ($249) — primary
- **SEMrush Pro** ($249-499) — secondary (competitor + ads insights)
- Screaming Frog full
- **Scrunch trial** ($99 trial 30gg) per GEO tracking
- GA4 + Search Console

### Tier `2kplus` (€2k+/mese)

Stack:
- **Ahrefs Advanced** ($449)
- **SEMrush Business** ($499+)
- Screaming Frog
- **Scrunch / LLMrefs / Profound** (GEO dedicated, $99-499)
- **Conductor / BrightEdge** enterprise (optional)
- Custom dashboards (Looker Studio + BigQuery)
- Analytics: GA4 + Mixpanel + custom

## When to use what

| Need | Best tool |
|------|-----------|
| Backlink analysis | Ahrefs > SEMrush > Moz |
| Keyword research | Ahrefs Keyword Explorer or SEMrush Keyword Magic |
| Position tracking | Ahrefs Rank Tracker or SE Ranking |
| Technical audit | Screaming Frog (gold) or Ahrefs Site Audit |
| Content gap | Ahrefs Content Gap or SEMrush Topic Research |
| Competitor analysis | SEMrush Competitive Research or Ahrefs Site Explorer |
| Local SEO | BrightLocal or SEMrush Local |
| GEO tracking | Scrunch or LLMrefs |
| Reporting | SE Ranking white-label or Looker Studio |
| Page speed | PageSpeed Insights API (free) + WebPageTest |
| Analytics | GA4 + Plausible/Matomo (cookieless) |

## API integration (per skill `keyword-research`)

### Ahrefs API

```bash
curl -H "Authorization: Bearer $AHREFS_API_KEY" \
  "https://api.ahrefs.com/v3/keywords-explorer/overview?country=it&keyword=ecommerce%20analytics"
```

Endpoint: `/keywords-explorer/overview`, `/site-explorer/overview`, `/site-audit/issues`.

Pricing: API plan dedicato, no free tier API. Rate limit per plan tier.

### SEMrush API

```bash
curl "https://api.semrush.com/?type=phrase_kdi&key=$SEMRUSH_API_KEY&phrase=ecommerce+analytics&database=it"
```

Endpoint: `phrase_kdi`, `phrase_related`, `phrase_organic`. Pro plan minimum.

### Moz API

```bash
curl -u "$MOZ_ACCESS_ID:$MOZ_SECRET" \
  "https://lsapi.seomoz.com/v2/keyword_metrics" \
  -d '{"keywords": ["ecommerce analytics"], "geographic_area": "italy"}'
```

Pro plan + API access.

## Free alternative workflow

Quando budget `lt100` + no API key:

1. **Keyword research**:
   - Google Autosuggest scrape (10-20 keyword per seed, free)
   - Search Console queries own site (90gg)
   - Ubersuggest 3 query/day rotation
   - AnswerThePublic (free 3 search/day)
   - Google Trends (relative volume)

2. **Backlink analysis**:
   - Ahrefs Webmaster Tools own site (free)
   - Search Console > Links report
   - OpenLinkProfiler (free, limited)

3. **Position tracking**:
   - Search Console queries (own site, 16 mesi)
   - Manual check top 10 keyword via incognito browser

4. **Technical audit**:
   - Screaming Frog 500 URL free
   - GSC URL Inspection
   - PageSpeed Insights free
   - Schema.org Validator free

5. **Content audit**:
   - Manual sitemap parse + GSC export
   - Manual competitor crawl (rate-limited)

## Tool fatigue warning

Anti-pattern: tool stacking eccessivo (5+ tool subscription) → overhead operativo + duplicate data + decision paralysis.

Best practice: 1 primary tool (Ahrefs OR SEMrush) + Search Console + Screaming Frog. Tutto il resto è specializzazione.

## Sources

- [Ahrefs](https://ahrefs.com/)
- [SEMrush](https://www.semrush.com/)
- [Moz](https://moz.com/)
- [SE Ranking](https://seranking.com/)
- [Ubersuggest](https://neilpatel.com/ubersuggest/)
- [Screaming Frog](https://www.screamingfrog.co.uk/seo-spider/)
- [Scrunch](https://scrunch.com/)
- [LLMrefs](https://llmrefs.com/)
- [Profound](https://www.tryprofound.com/)
