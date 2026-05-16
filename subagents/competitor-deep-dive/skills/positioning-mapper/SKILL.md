---
name: positioning-mapper
description: Estrae positioning di un competitor (tagline, value prop, ICP inferred, 3 differentiators, pricing summary) da homepage + about + product + pricing pages. Output JSON deterministico con source quote + URL per ogni claim. Anti-hallucination MANDATORY — se evidence insufficiente flag stealth_detected o insufficient_evidence. Da usare prima di tov-analyzer e reviews-sentiment, output input per gap-finder.
when_to_use: Per ogni competitor in lista, prima fase pipeline. Anche standalone per snapshot rapido positioning su 1 competitor. Anche per audit periodico 90gg (re-scrape per detect repositioning).
allowed-tools: Read Write Bash(python:*) Bash(curl:*)
---

# Positioning Mapper

Trasforma 1 competitor (`name + domain`) in positioning structured JSON con tagline, value prop, ICP inferred, 3 differentiators e pricing — ognuno con source URL + verbatim quote. Anti-hallucination by design.

## When to use

Attivare quando:

- Pipeline `/competitor-deep-dive` ingerisce competitor list (Fase 2a)
- Audit periodico 90gg per detect repositioning competitor noto
- Snapshot rapido pre-meeting (singolo competitor)
- Pre-input per `tov-analyzer` (corpus condiviso) e `reviews-sentiment`

Non attivare se:

- Competitor stealth confermato (homepage 404 o coming-soon) → output `stealth_detected: true`
- Domain invalid (DNS fail) → output error + suggest verify spelling
- Competitor è subsidiary di parent company analizzata (ridondante)

## Prerequisiti

- `<memory>/config.md` esiste con `business.geo_target` (per GDPR mode awareness)
- `playwright` MCP available (primary) o fallback `Bash(curl:*)` + html parsing
- Reference `references/gdpr-scraping-compliance.md` accessibile (rate-limit safe defaults)

## Instructions

### Fase 1 — Validate domain

```bash
curl -sI -L --max-time 10 "https://<domain>" | head -1
```

Check:
- HTTP 200 / 301 / 302 → ok
- HTTP 404 / 503 → flag `stealth_detected: true`, output `{competitor, domain, stealth_detected: true, scrape_date}`, exit
- DNS fail → output error + suggest spelling check

### Fase 2 — Detect competitor language + scope

```bash
python scripts/positioning_extract.py --domain <domain> --pages homepage,about,product,pricing --max-words-per-page 1500
```

Lo script Playwright:
1. Naviga homepage, attende JS render (1.5s)
2. Estrae `<h1>`, `<h2>` (primi 3), `<meta name="description">`, blocchi `<p>` primi 5
3. Naviga `/about` se trovato (link in nav o footer)
4. Naviga `/product` o `/features` se trovato
5. Naviga `/pricing` se trovato
6. Aggrega corpus testuale, salva in `output/corpus_<slug>.txt`
7. Output JSON intermediate `output/scrape_<slug>.json` con HTML excerpts + URL per ogni claim trovato

**Rate limit**: 2 secondi tra richieste (default safe per ogni dominio).

**Edge case**: se homepage `<200 parole` → flag `homepage_minimalistic: true` + suggerimento "espandere corpus con LinkedIn + 5 blog post per ToV downstream".

### Fase 3 — Extract positioning fields

Da corpus aggregato:

#### Tagline

- Primary: `<h1>` homepage (più grande, più alto)
- Fallback: `<meta name="description">` se h1 generico ("Welcome", "Home")
- Esclusioni: cookie banner, marketing pop-up

#### Value prop

- Primary: primo `<p>` sotto h1 homepage (claim sintetico)
- Fallback: 3-5 bullet "Why choose <brand>" se presenti
- Esclusioni: testimonial generici

#### ICP inferred

- Cerca pattern: "for <role>", "designed for <company-size>", "built for <industry>", "perfect for <use-case>"
- Estrai 1-3 ICP signal con verbatim quote
- Inferenza implicita da pricing tier ("Enterprise" → enterprise ICP)

#### 3 differentiators

- Cerca pattern: "Unlike <competitor>", "10x <metric>", "The only <X> that <Y>", "Our <feature> means <benefit>"
- Estrai 3 claim più visibili (homepage > about > product)
- Per ognuno: claim text + source URL + verbatim quote

#### Pricing summary

- Naviga `/pricing` page se trovata
- Estrai modello: subscription | usage-based | one-time | freemium
- Estrai tier names + prezzi visibili (USD, EUR)
- Se "Contact us" / "Custom" → `pricing_call_only: true`

### Fase 4 — Build positioning.json

```json
{
  "competitor": "Make",
  "domain": "make.com",
  "scrape_date": "2026-04-30",
  "scrape_pages_visited": ["make.com", "make.com/about", "make.com/integrations", "make.com/pricing"],
  "stealth_detected": false,
  "homepage_minimalistic": false,
  "tagline": "Automate work, anywhere — visually",
  "tagline_source": {"url": "make.com", "selector": "h1", "quote": "Automate work, anywhere — visually"},
  "value_prop": "Build, run, and scale automations of any size with our visual builder",
  "value_prop_source": {"url": "make.com", "selector": "h1+p"},
  "icp_inferred": "Mid-market SaaS, technical operators, RevOps teams",
  "icp_evidence": [
    {"url": "make.com/about", "quote": "Built for technical operators who scale beyond 100 workflows"},
    {"url": "make.com/pricing", "quote": "Enterprise plan for teams of 50+ users"}
  ],
  "differentiators": [
    {
      "claim": "Visual no-code workflow builder",
      "evidence": [{"url": "make.com", "quote": "Drag, drop, done. Build automations visually without writing code."}]
    },
    {
      "claim": "10,000+ apps integrated",
      "evidence": [{"url": "make.com/integrations", "quote": "Connect 10,000+ apps in one platform"}]
    },
    {
      "claim": "Free tier with 1,000 ops/month",
      "evidence": [{"url": "make.com/pricing", "quote": "Free forever — 1,000 operations / month"}]
    }
  ],
  "pricing_summary": {
    "model": "subscription",
    "tiers": [
      {"name": "Free", "price_usd": 0, "ops_month": 1000},
      {"name": "Core", "price_usd": 9, "ops_month": 10000},
      {"name": "Pro", "price_usd": 16, "ops_month": 10000, "additional_features": ["custom variables", "priority support"]},
      {"name": "Teams", "price_usd": 29, "ops_month": 10000},
      {"name": "Enterprise", "price_usd": "Contact us", "ops_month": "custom"}
    ],
    "lowest_tier_usd": 0,
    "pricing_call_only": false,
    "pricing_url": "make.com/pricing"
  },
  "positioning_inconsistent": false,
  "scraper_used": "playwright",
  "fallback_active": null
}
```

### Fase 5 — Validate output

Pre-write validation:
- [ ] Tagline + value_prop entrambi presenti (no `null`) — altrimenti `homepage_minimalistic: true`
- [ ] Almeno 2 differentiators con evidence — altrimenti flag `differentiators_insufficient`
- [ ] Almeno 1 ICP evidence quote — altrimenti `icp_inferred: null` + flag
- [ ] Pricing model definito o `pricing_call_only: true` — mai `null`
- [ ] Tutti `evidence[].quote` non vuoti — verbatim dal corpus
- [ ] Tutti `evidence[].url` valid (regex match domain)

Se validation fail → output JSON con flag specifici, log warning, NON output `null` silently.

### Fase 6 — Save

```bash
# Salva output JSON
write output/positioning_<slug>.json

# Append corpus aggregato (per tov-analyzer downstream)
write output/corpus_<slug>.txt

# Update <memory>/config.md → competitors_analyzed[]
```

## Output examples

Caso success completo: vedi blocco JSON sopra (Make).

Caso stealth:
```json
{
  "competitor": "StealthCo",
  "domain": "stealthco.io",
  "scrape_date": "2026-04-30",
  "stealth_detected": true,
  "reason": "homepage returns 404 / coming-soon page",
  "fallback_suggestion": "Wait for product launch, schedule re-analysis 30 days"
}
```

Caso homepage minimalista:
```json
{
  "competitor": "Linear",
  "domain": "linear.app",
  "homepage_minimalistic": true,
  "homepage_corpus_words": 87,
  "fallback_suggestion": "Espandi corpus con about + 5 latest blog post per ToV downstream",
  "tagline": "Linear is a purpose-built tool for planning and building products",
  "tagline_source": {...},
  ...
}
```

## Anti-pattern

- **NO claim senza evidence** — ogni field con `_source` o `evidence[]` obbligatorio
- **NO inventare ICP** — se nessun signal nel corpus, `icp_inferred: null` + flag
- **NO scrape oltre 4 pagine** in 1 run senza warning costo
- **NO ignorare rate-limit** — sempre 2s tra request stesso dominio
- **NO output `null` silently** — sempre flag specifici (stealth_detected, insufficient_evidence, etc.)
- **NO scrape forum / siti sensibili** anche se linkati
- **NO bypass robots.txt** se Disallow su path richiesto

## Edge cases

- **Domain redirect**: catch redirect chain, log final URL, scrape final
- **Multi-language site**: prefer `/en` o `<html lang="en">`, log `language: "en"` in output
- **Anti-bot detection** (Cloudflare challenge): retry con delay 30s, se fallisce → flag `bot_protection_detected` + fallback parallel-cli
- **JS-render mandatory** (SPA Next.js, React): Playwright primary; fallback curl only se Playwright miss
- **Multi-product competitor** (es. Atlassian con Jira+Confluence+Trello): user deve specificare quale linea (AskUserQuestion upstream)
- **Geo-fenced site** (es. eu.brand.com vs com.brand.com): scrape entrambi, log `geo_split_detected`
