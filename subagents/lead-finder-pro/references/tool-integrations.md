# Tool Integrations — `/lead-finder-pro`

> Reference per il subagent. Mappa i 7 tool top + 4 tool secondari del mercato 2026, con focus su capabilities tecniche, MCP/API, autenticazione, rate limit, costi indicativi. Usata da `/lead-finder-pro` quando l'utente chiede "quale tool è meglio per X" o quando configuriamo waterfall chain custom.

## Quick decision matrix

| Use case | Tool consigliato 1° | Fallback | Note |
|----------|---------------------|----------|------|
| Email finder + verifier (LLM-native) | **Hunter** (MCP) | Apollo | Hunter ha unico MCP nativo — DECISION-005 |
| Volume budget enrichment | Apollo | Lusha | Bounce 15-25% → verification mandatory |
| EMEA-focused mobile data | Cognism | n/a | Diamond Data EMEA, GDPR-strong |
| Enterprise org charts + technographic | ZoomInfo | Apollo Pro | Premium-tier, contratti rigidi |
| Multi-provider orchestration | Clay | parallel-cli enrich | Costi credit imprevedibili |
| LinkedIn URL → email | Wiza | Hunter Email Finder | Lightweight, profile-driven |
| All-in-one consolidated | Amplemarket | n/a | Data + AI + multichannel, premium pricing |

## Hunter — Primary path

### MCP server nativo

URL: `mcp.hunter.io`

**Capabilities** (via MCP):

- `email-finder`: cerca email da `name + domain` o `name + company`
- `email-verifier`: SMTP + MX + catch-all detection + role check
- `domain-search`: lista email pubblicamente trovate per dominio
- `enrichment`: full enrichment per `email` (company, role, social, technographic basic)
- `discover`: cerca aziende per filtri (industry, size, location)

**Auth**: API key nel `~/.claude.json` config MCP server entry. Free tier: 25 search/mese + 50 verify/mese. Premium tiers da $49/mese.

**Rate limit**: 5 req/sec free, 15 req/sec premium. Retry on 429 con backoff esponenziale (script `email_verify_waterfall.py` gestisce nativo).

**Output schema email-verifier**:

```json
{
  "data": {
    "status": "valid|invalid|accept_all|webmail|disposable|unknown",
    "result": "deliverable|undeliverable|risky",
    "score": 92,
    "smtp_check": true,
    "mx_records": true,
    "accept_all": false,
    "disposable": false,
    "role": false,
    "regexp": true
  }
}
```

**Trigger di flag** (DECISION-009 conflict):

- `score < 80` → catch-all skip
- `disposable: true` → exclude
- `role: true` → exclude da personalized
- `result: undeliverable` → invalid, segnale per `_conflicts` se Apollo restituisce diversa email

### REST API V2 (alternative, se MCP non disponibile)

Endpoint base: `https://api.hunter.io/v2/`

Chiavi:

- `/email-verifier?email=X&api_key=Y` → verifier (1 credit)
- `/email-finder?domain=X&first_name=A&last_name=B&api_key=Y` → finder (1 credit)
- `/domain-search?domain=X&api_key=Y` → list email per dominio (1 credit per pagina)

## Apollo

### REST API people-search

Endpoint: `https://api.apollo.io/v1/mixed_people/search`

**Auth**: API key in env `APOLLO_API_KEY` o passata via `--api-key` allo script `apollo_search.py`.

**Pricing 2026**:

- Basic: $49/mese ($588/yr) → 200 contatti/mese
- Professional: $99/mese ($1.188/yr) → 12.000 contatti/anno
- Organization: enterprise pricing

**Filtri principali** (vedi `apollo-api-recipes.md` per JSON examples):

- `person_titles`: list (es. `["VP Marketing", "Head of Growth"]`)
- `person_locations`: list paesi
- `organization_locations`: list paesi azienda
- `organization_num_employees_ranges`: list (es. `["10,50", "51,200"]`)
- `person_seniorities`: list (`founder`, `c_suite`, `vp`, `director`, `manager`)
- `q_organization_keyword_tags`: list keyword (industry tag)

**Rate limit**: ~60 req/min standard, 200 req/min Pro. Retry 3x exponential backoff su 429.

**Bounce flag**: 15-25% reportato. **Mandatorio passare email Apollo attraverso skill `email-verification` waterfall** prima di attivare in sequence.

**Output people-search**:

```json
{
  "people": [{
    "id": "...",
    "name": "Mario Rossi",
    "title": "VP Marketing",
    "email": "mario@acme.com",
    "email_status": "verified|unverified",
    "linkedin_url": "...",
    "organization": {"name": "Acme", "id": "...", "estimated_num_employees": 150}
  }],
  "pagination": {"page": 1, "per_page": 25, "total_entries": 1234}
}
```

## ZoomInfo

API enterprise per bulk enrichment + FormComplete (visitor identification).

- Pricing: ~$1.250/mese, contratti annual+ obbligatori
- DB più grande: 320M+ contatti, org charts, hierarchies
- **Bounce**: 15%+ reportato → verification waterfall mandatory anche qui
- No native MCP

**Quando usarlo in `/lead-finder-pro`**: solo se utente già lo ha (Q2 risposta = ZoomInfo). Altrimenti consiglia Apollo + Hunter.

## Cognism

API EMEA-focused.

- Pricing: ~$1.250/mese + per-seat
- "Diamond Data": numeri mobili EMEA verificati telefonicamente (fonte unica)
- GDPR-strong (compliance EU built-in)
- Coverage drop fuori EU (USA limited)

**Quando usarlo**: lead EU prevalenti, focus mobile-first outreach, GDPR rigoroso. `/lead-finder-pro` lo cita come tool consigliato se discovery Q5 ICP = "Europa/EMEA only".

## Clay

Orchestration layer, non enrichment provider singolo.

- $185-495/mese starting
- Connessione native a 100+ provider via `Claygent`
- Visual table-based UI, learning curve steep
- **Costo credit imprevedibile**: 10-step workflow brucia 15-25 credit/contatto

**Quando usarlo in `/lead-finder-pro`**: tier 3 fallback dopo Hunter + Apollo, solo se utente è Clay user power. Altrimenti `parallel-cli enrich` come fallback più predictable.

## Lusha

API + Chrome extension.

- $22-52/mese (consumer-tier)
- Time-to-value veloce: ad-hoc lookup mid-call
- No bulk, no intent, phone credit burn rate alto
- No MCP

**Quando usarlo**: ad-hoc lookup individuale (un VP target specifico). NON per batch volume.

## Amplemarket

Consolidator end-to-end.

- $240-300/mese/user
- Curated managed waterfall, <3% bounce out-of-the-box
- AI personalization + multichannel built-in
- Top score 219/231 nelle 2026 reviews

**Quando usarlo**: all-in-one consolidation se utente vuole ridurre stack (case study Star: 658 ore risparmiate).

## Wiza

Lightweight LinkedIn → email extraction.

- LinkedIn-first workflow
- Verified email da search + profile
- Pricing entry-tier

**Quando usarlo**: skill `linkedin-safe-scraping` Fase 1 ingest, prima di passare a waterfall enrichment per altri campi.

## Tool secondari (citati ma non integrazione full)

| Tool | Note |
|------|------|
| Lead411 | NotebookLM source insufficiente — verifica esterna se utente lo richiede |
| Adapt | NotebookLM source insufficiente |
| RocketReach | Citato come tool che alcuni team hanno **abbandonato** (case study Star) |
| Snov.io | NotebookLM source insufficiente — verifica esterna |
| NeverBounce / ZeroBounce / Bouncer / Kickbox | Email verifiers specializzati. Hunter MCP è già il primary in `/lead-finder-pro`; questi entrano solo se Hunter+Apollo entrambi miss |

## MCP detection priority (per il subagent)

Ordine di check al run via `mcp_detect.py`:

1. `hunter` (priorità massima — DECISION-005)
2. `attio-mcp` (CRM sync se utente Attio)
3. `google-personal` (output Sheet)
4. `playwright` (LinkedIn Sales Nav)
5. `smartlead` (chain outbound)
6. `heyreach` (chain LinkedIn outbound)
7. `explorium` (alternative enrichment)

Output `mcp_detect.py` salvato in `<memory>/config.md` campo `mcp_available` + `mcp_fallbacks_active`.

## Pattern fallback chain

```text
Hunter MCP available → primary path
  ├─ if Hunter miss → Apollo API (env APOLLO_API_KEY)
  │   ├─ if Apollo miss → Clay MCP (se installato)
  │   │   └─ if Clay miss → parallel-cli enrich --type business
  │   │       └─ last resort: manual SMTP via email_verify_waterfall.py --enable-smtp
```

Ogni tier registra in `_conflicts` se restituisce valore differente da tier precedente (DECISION-009).

## Cost budget consigliato (audience freelance/founder)

| Volume target | Budget mensile tools | Stack consigliato |
|---------------|---------------------|-------------------|
| <50 lead/mese | $0-20 | Hunter free + manual |
| 50-200 lead/mese | $50-150 | Hunter Premium + parallel-cli |
| 200-500 lead/mese | $150-400 | Hunter Premium + Apollo Basic + Clay starter |
| 500+ lead/mese | $400-1.000 | Hunter Premium + Apollo Pro + Clay Growth + Cognism EMEA |

NB: pricing 2026 indicative, verifica sempre sul sito ufficiale.
