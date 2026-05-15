# Apollo API Recipes — `/lead-finder-pro`

> Reference per `apollo_search.py` script + skill `waterfall-enrichment` Tier 2 fallback. Pattern di chiamata efficaci, JSON request/response examples, rate limit handling. Source: docs.apollo.io + NotebookLM Q2 2026.

## Endpoints principali

| Endpoint | Use case | Cost (1 contatto = 1 credit) |
|----------|----------|------------------------------|
| `POST /v1/mixed_people/search` | People search con filtri | 1 credit per result |
| `POST /v1/organizations/search` | Company search | 1 credit per result |
| `POST /v1/people/match` | Enrichment via email/LinkedIn URL | 1 credit per match |
| `POST /v1/contact_stages` | List stage CRM-style | 0 credit (read) |
| `POST /v1/people/bulk_match` | Bulk enrichment (max 10/call) | 1 credit per match |

Base URL: `https://api.apollo.io/v1/`

## Authentication

API key in header `X-Api-Key: <YOUR_KEY>` o query param `api_key=<YOUR_KEY>`.

Best practice: env var `APOLLO_API_KEY`, mai committed in repo.

## Recipe 1 — People search per ICP target

**Use case**: trovare 25 VP Marketing in SaaS USA, 50-200 employees.

**Request**:

```bash
curl -X POST "https://api.apollo.io/v1/mixed_people/search" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -d '{
    "person_titles": ["VP Marketing", "Head of Marketing", "VP of Marketing"],
    "person_locations": ["United States"],
    "person_seniorities": ["vp", "head"],
    "organization_locations": ["United States"],
    "organization_num_employees_ranges": ["51,200"],
    "q_organization_keyword_tags": ["SaaS", "B2B SaaS"],
    "page": 1,
    "per_page": 25
  }'
```

**Response (essential fields)**:

```json
{
  "people": [
    {
      "id": "abc123",
      "first_name": "Sara",
      "last_name": "Bianchi",
      "name": "Sara Bianchi",
      "title": "VP Marketing",
      "email": "sara@nimbusfintech.com",
      "email_status": "verified",
      "linkedin_url": "https://linkedin.com/in/sarabianchi",
      "twitter_url": null,
      "city": "New York",
      "country": "United States",
      "organization": {
        "id": "org_xyz",
        "name": "Nimbus FinTech",
        "website_url": "https://nimbusfintech.com",
        "estimated_num_employees": 150,
        "industry": "Financial Services",
        "founded_year": 2020,
        "linkedin_url": "https://linkedin.com/company/nimbus-fintech"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total_entries": 1234,
    "total_pages": 50
  }
}
```

**Pattern in `/lead-finder-pro`**:

1. Costruisci query JSON da ICP description user (Q5 discovery)
2. Loop pagine fino a `total_entries` o `max_leads` config
3. Per ogni `person` → estrai `email`, `linkedin_url`, `title`, `organization.name + estimated_num_employees`
4. Pass output a skill `email-verification` (waterfall) prima di score
5. **NON fidarti di `email_status: verified`** Apollo — bounce 15-25% reportato. Verification waterfall mandatory (DECISION-005).

## Recipe 2 — Organization search per account-based prospecting

**Use case**: trovare 50 SaaS B2B post-Series A in EU.

**Request**:

```bash
curl -X POST "https://api.apollo.io/v1/organizations/search" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -d '{
    "organization_locations": ["Italy", "France", "Germany", "Spain", "Netherlands"],
    "organization_num_employees_ranges": ["11,50", "51,200"],
    "q_organization_keyword_tags": ["SaaS", "B2B"],
    "organization_funding_stage_cd": ["Series A"],
    "page": 1,
    "per_page": 25
  }'
```

**Response**:

```json
{
  "organizations": [
    {
      "id": "org_abc",
      "name": "Acme SaaS",
      "website_url": "https://acme.io",
      "estimated_num_employees": 75,
      "industry": "Computer Software",
      "founded_year": 2021,
      "total_funding": 12000000,
      "latest_funding_stage": "Series A",
      "latest_funding_date": "2025-11-15",
      "technologies": ["Salesforce", "HubSpot", "Stripe"],
      "city": "Milan",
      "country": "Italy"
    }
  ],
  "pagination": {...}
}
```

**Pattern**:

1. Filtra company first
2. Per ogni org → trova "decision maker" tramite secondary call `mixed_people/search` con `organization_ids: [org.id]` + `person_seniorities: ["c_suite", "vp"]`
3. Extract intent signal da `total_funding`, `latest_funding_date` (recente = Hot signal)
4. `technologies` → input per technographic scoring (skill `icp-scoring` template SaaS B2B)

## Recipe 3 — People match (enrichment by email or LinkedIn)

**Use case**: hai email "mario@acme.com", vuoi arricchire con role + company size + LinkedIn.

**Request**:

```bash
curl -X POST "https://api.apollo.io/v1/people/match" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -d '{
    "email": "mario@acme.com",
    "reveal_personal_emails": false,
    "reveal_phone_number": false
  }'
```

**Response**: stesso schema di people search, single `person` object.

**Pattern**:

- Usalo come Tier 2 di waterfall (Hunter MCP miss → Apollo match)
- Set `reveal_personal_emails: false` e `reveal_phone_number: false` per default GDPR-safe (richiedere personal data costa extra credit + GDPR Article 9-adjacent)

## Recipe 4 — Bulk match (efficient batching)

**Use case**: hai 50 lead già enriched parzialmente, vuoi completare via Apollo in 1 call.

**Request** (max 10 records per call):

```bash
curl -X POST "https://api.apollo.io/v1/people/bulk_match" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $APOLLO_API_KEY" \
  -d '{
    "details": [
      {"email": "mario@acme.com"},
      {"linkedin_url": "https://linkedin.com/in/sarabianchi"},
      {"first_name": "Luca", "last_name": "Verdi", "domain": "nimbus.io"}
    ]
  }'
```

**Pattern**:

- Batch da 10 = 1 chiamata HTTP, 10 credit
- Loop con `time.sleep(0.5)` tra batch (rate limit 60 req/min standard)
- Errors per record nel response field `errors[]` — handle gracefully

## Rate limit handling

Apollo restituisce header:

- `X-RateLimit-Limit`: max calls
- `X-RateLimit-Remaining`: residue
- `X-RateLimit-Reset`: epoch reset

**Pattern Python** (in `apollo_search.py`):

```python
import time
import requests

def apollo_call(endpoint, payload, api_key, max_retries=3):
    url = f"https://api.apollo.io/v1/{endpoint}"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    for attempt in range(max_retries):
        resp = requests.post(url, json=payload, headers=headers)

        if resp.status_code == 429:
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait_seconds = max(reset - time.time(), 5)
            time.sleep(min(wait_seconds, 60))
            continue

        if resp.status_code >= 500:
            time.sleep(2 ** attempt)  # exponential backoff
            continue

        resp.raise_for_status()
        return resp.json()

    raise Exception(f"Apollo API failed after {max_retries} retries")
```

## Error code mapping

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 401 | Invalid API key | Stop + error message all'utente |
| 403 | No permission for endpoint | Verificare tier subscription |
| 422 | Invalid query params | Fix query schema |
| 429 | Rate limit | Backoff + retry |
| 500-503 | Apollo down | Exponential backoff retry, max 3 |

## Filter cheatsheet (people search)

| Filtro | Valori esempio | Note |
|--------|----------------|------|
| `person_titles` | `["VP Marketing", "Director Sales"]` | OR semantics |
| `person_seniorities` | `["c_suite", "vp", "director", "manager", "ic"]` | Apollo enum |
| `person_locations` | `["United States", "Italy"]` | Country-level |
| `person_seniorities` | Vedi sopra | Combinabile con titles |
| `organization_num_employees_ranges` | `["1,10", "11,50", "51,200", "201,500", "501,1000", "1001,5000", "5001,10000", "10001+"]` | Apollo predefiniti |
| `organization_industry_tag_ids` | Apollo tag IDs (richiede lookup) | Più precisi di keyword |
| `q_organization_keyword_tags` | `["SaaS", "B2B"]` | Keyword search libera |
| `organization_locations` | Lista paesi azienda | OR |
| `organization_funding_stage_cd` | `["Seed", "Series A", "Series B", "Series C+"]` | |
| `organization_funding_year_min` | `2024` | Filter su funding year |
| `currently_using_any_of_technology_uids` | Apollo tech UIDs | Filter su tech stack |

Per la lista completa: <https://docs.apollo.io/reference/people-search>

## Best practice GDPR-aware

Quando lead EU detected (DECISION-011):

1. **Set `reveal_personal_emails: false`** sempre
2. **Set `reveal_phone_number: false`** sempre (mobile = personal data heavy)
3. **Filter Article 9 fields**: ignora qualsiasi field health/political/religious
4. **Document source**: salva `_source: "apollo_v1_mixed_people_search"` + timestamp

## Cost optimization

- **Cache aggressive**: salva response 30 giorni in `<memory>/apollo_cache/<query_hash>.json` per evitare re-fetch identici
- **Page wisely**: di solito i primi 50-100 lead sono sufficienti (ranked by Apollo internal score), non scrappare 1000 pagine
- **Use organization-search prima di people-search**: filtra a livello company, poi entra nei contact specifici → 5x credit reduction tipica

## Cross-reference

- Skill `waterfall-enrichment` invoca questo script per Tier 2
- Script `apollo_search.py` è il wrapper CLI
- Cache directory `<memory>/apollo_cache/` (gitignored)
- Rate limit handler condiviso in `apollo_search.py`

## Source ufficiale

<https://docs.apollo.io/> (Apollo API V1 Reference, 2026)
