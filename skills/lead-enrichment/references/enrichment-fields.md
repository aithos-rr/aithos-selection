# Enrichment Fields — catalogo 20 campi prioritizzati

## Core (must have per outreach)

1. **email** — professional email verificata
2. **email_confidence** — 0.0-1.0 (soglia >0.8 per hot outreach)
3. **first_name** + **last_name** — parsed da "name" input
4. **company** — ragione sociale normalizzata
5. **role** — current role (da LinkedIn, non self-reported)

## Qualifying (score tier)

6. **company_size** — employees (range: 1-10, 11-50, 51-200, 201-500, 501-1k, 1k+)
7. **company_industry** — vertical (SaaS B2B, Ecommerce, EdTech, ecc.)
8. **company_revenue** — ARR stimato (se disponibile)
9. **company_country** — HQ country (GDPR compliance)
10. **seniority_level** — IC / Manager / Director / VP / CxO / Founder

## Intent signals (caldo vs freddo)

11. **recent_funding** — "Series A $15M Feb 2026"
12. **recent_hires** — ruoli aperti correlati al tuo offering
13. **recent_news** — launch, pivot, acquisition
14. **job_change_recent** — nuovo ruolo <90gg (triggers interesse)
15. **tech_stack_signal** — usa stack compatibile con il tuo tool

## Touchpoints (quali canali)

16. **linkedin_url** — profilo LinkedIn
17. **twitter_handle** — @handle (se pubblico)
18. **github_url** — per target tecnici
19. **phone** — se pubblico (rare, solo per alto valore)
20. **company_website** — URL ufficiale

## Priorità per use case

| Use case | Campi essenziali |
|----------|------------------|
| **Cold email** | 1, 2, 3, 4, 5 |
| **LinkedIn outreach** | 3, 4, 5, 16 |
| **Account-based marketing** | 4, 6, 7, 8, 11, 12 |
| **Intent-based outbound** | 1-5, 11-13 |
| **CRM hygiene** | 1, 2, 4, 5, 10 |

## Source mapping

Quale tool produce quale campo:

| Campo | Source primaria | Fallback |
|-------|-----------------|----------|
| email | parallel-cli enrich | clearbit.com, hunter.io |
| email_confidence | bouncer.io verify | neverbounce |
| role | LinkedIn Sales Nav scrape | apollo.io |
| company_size | Clearbit Enrich | LinkedIn company |
| company_industry | LinkedIn company | manual tag |
| recent_funding | Crunchbase API | parallel-cli research |
| recent_hires | LinkedIn Jobs scrape | company career page |
| linkedin_url | LinkedIn search via parallel-cli | manual |

## Compliance GDPR

Per lead EU:
- **Lawful basis** obbligatoria: contract / legitimate interest / consent
- **Opt-out in ogni email** (SmartLead lo gestisce automaticamente)
- **No scraping identitario sensibile** (religione, salute, orientamento)
- **Cancellazione su richiesta**: entro 30gg delete record + tutte le email

Documenta fonte di ogni campo nel CRM (Attio custom field `enrichment_source`).

## Scoring formula

```python
score = 0
if email and email_confidence > 0.8: score += 30
if linkedin_url: score += 15
if role_seniority in ('director', 'vp', 'cxo', 'founder'): score += 20
if recent_funding: score += 20
if recent_hires > 0: score += 15
if company_industry in TARGET_INDUSTRIES: score += 10
if company_size in TARGET_SIZE_RANGE: score += 10

tier = 'hot' if score >= 80 else 'warm' if score >= 50 else 'cold'
```

Adattare pesi alla tua ICP.
