---
name: linkedin-safe-scraping
description: Estrazione lead LinkedIn signal-based (non bulk static), via Sales Navigator search + LinkedIn URL → enrichment chain. Soft daily limit configurabile (default 80 organic / 100 Sales Nav / 1000 dedicated). Pattern anti-detection (human-paced, no mass connection request, no automated commenting). GDPR Recital 47 legitimate interest. Da usare quando ICP richiede sourcing prospect non già in CRM/lista, ricerca per industry+role+geo specifico, signal trigger detection (job change).
when_to_use: Sourcing prospect nuovi non in CRM, ricerca Sales Nav per ICP specifico, job-change trigger detection, fallback se Apollo/Hunter coverage insufficiente per nicchia, signal-based extraction
allowed-tools: Read Bash(python:*) mcp__playwright__browser_*
---

# LinkedIn Safe Scraping

Estrazione lead LinkedIn rispettando ToS, rate limit, anti-detection. Pattern 2026: signal-based + multi-account distribution + human-in-the-loop approval per send.

## When to use

Attivare quando:

- Sourcing prospect NUOVI non già nel CRM o lista esistente
- Ricerca Sales Nav per ICP specifico (filtri: industry + role + geo + company size)
- Job-change trigger detection (lead lascia ruolo → opportunity new company)
- Fallback se Hunter/Apollo coverage insufficiente per nicchia (founder small company, geographies under-covered)
- Signal-based extraction batch (es. "trovami 50 VP Marketing FinTech che hanno cambiato ruolo negli ultimi 30 giorni")

Non attivare se:

- Lead list già completa con email/role/LinkedIn (chain solo `waterfall-enrichment` invece)
- Volume >200 lead/giorno (rischio account ban)
- User non ha Sales Navigator subscription (organic search più limitato)
- Bulk static list building (anti-pattern 2026)

## Prerequisiti

- `mcp__playwright__browser_*` MCP server disponibile (per Sales Nav browser automation)
- LinkedIn account autenticato in Playwright session
- (Optional) Sales Navigator subscription per advanced filters
- Reference `references/lead-enrichment-best-practices-2026.md` sezione LinkedIn safe

## Instructions

### Fase 1 — Verify session + limits

Check `mcp_detect.py` per playwright availability:

```bash
python scripts/mcp_detect.py --check playwright
```

Read soft daily limits from config:

```yaml
linkedin:
  daily_limit_organic: 80  # search results clicked/extracted/giorno
  daily_limit_salesnav: 100
  daily_limit_dedicated_account: 1000
  current_account_type: salesnav  # organic | salesnav | dedicated
```

Track `<memory>/linkedin_quota_<date>.json` con current usage. Block se quota exceeded.

### Fase 2 — Build search query

Da ICP description + segment del config:

```python
icp_segment = "FinTech early-stage USA"
# Translate to Sales Nav filters:
filters = {
    "industry": ["Financial Services", "Banking"],
    "company_size": ["11-50", "51-200"],
    "geographies": ["United States"],
    "seniorities": ["VP", "Head", "Director"],
    "functions": ["Marketing"],
    "years_at_company": ["less_than_2"]  # post-funding signal
}
```

### Fase 3 — Sales Nav search via Playwright

```python
mcp__playwright__browser_navigate(url="https://www.linkedin.com/sales/search/people")
# Apply filters via UI interaction
mcp__playwright__browser_type(element="industry filter", text="Financial Services")
# ... etc
mcp__playwright__browser_wait_for(text="results", timeout=10)
```

**Anti-detection patterns**:

- Human-paced: 3-7 sec delay tra azioni
- Random offsets nei click
- No backwards navigation rapid
- Session duration max 2h, poi pause 4h+

### Fase 4 — Extract LinkedIn URL list (NOT full profile scrape)

Per ogni risultato:

```python
# Estrai SOLO:
{
    "name": "Sara Bianchi",
    "linkedin_url": "https://linkedin.com/in/sarabianchi",
    "headline": "VP Marketing | Building Nimbus FinTech",
    "company_name_visible": "Nimbus FinTech"
}
```

NON scrappare full profile: contact info, education, experience details, recommendations. Quei dati richiedono visit profile = anti-pattern (bulk profile visit triggera detection).

### Fase 5 — Signal-based filter

Per ogni LinkedIn URL estratto, applica signal filter (se requested):

- **Job-change ≤30 giorni**: filtra solo se headline contiene "Recently joined", `years_at_company: less_than_2`, o `position_started: <30 days ago`
- **Hiring signal**: visit company page once → check job postings count → filter aziende con ≥3 ruoli aperti rilevanti
- **Funding signal**: cross-check via parallel-cli `<company> funding 2026`

Filtra a ≤100 lead/run. Se >100, suggest split in batch giornalieri.

### Fase 6 — Pass output a waterfall-enrichment

Output skill = lista LinkedIn URL + base data. Subagent passa a `waterfall-enrichment` per email + role completion + company info:

```json
[
  {
    "name": "Sara Bianchi",
    "linkedin_url": "https://linkedin.com/in/sarabianchi",
    "company_visible": "Nimbus FinTech",
    "_source": "linkedin_salesnav",
    "_extracted_at": "2026-04-30T08:30:00Z"
  }
]
```

### Fase 7 — Update quota + log

```bash
python scripts/linkedin_quota_update.py --extracted 50 --date 2026-04-30
```

Update `<memory>/linkedin_quota_<date>.json`:

```json
{"date": "2026-04-30", "extracted": 50, "limit": 100, "remaining": 50, "account_type": "salesnav"}
```

### Fase 8 — Disclaimer reminder

Mostra all'utente all'avvio:

```text
⚠️ LinkedIn extraction limit advisory:
- Current account: Sales Navigator
- Soft daily limit: 100 lead/giorno
- Today extracted: 50/100 (50 remaining)
- LinkedIn ToS: signal-based extraction = legitimate; mass scraping = ban risk
- Verifica i tuoi limit ufficiali per account type
```

## Examples

### Esempio 1 — Sourcing 50 VP Marketing FinTech USA

**Input**: ICP "VP Marketing in FinTech B2B SaaS, USA, 50-200 employees".

**Workflow**:

1. Build Sales Nav filter: industry=FinTech+Banking, geo=USA, seniority=VP, function=Marketing, size=51-200
2. Run search → 200 results visible
3. Filter signal: only `years_at_company: less_than_2` (post-funding signal) → 60 results
4. Extract first 50 LinkedIn URL + name + headline
5. Pass to `waterfall-enrichment` → email + role confirmation + company funding data
6. Score via `icp-scoring` SaaS B2B 60/40 template

### Esempio 2 — Job-change trigger 30 giorni

**Input**: "Trovami VP Marketing che hanno cambiato lavoro negli ultimi 30 giorni in SaaS."

**Workflow**:

1. Sales Nav search: VP Marketing, SaaS, geo=any
2. Filter UI: `position_started_in_last_30_days` (Sales Nav advanced filter)
3. Extract 25 LinkedIn URL
4. Per ognuno: cross-check old company (deve essere SaaS o adjacent) → if true, doppia opportunity
5. Pass enrichment chain
6. Output: 18 verified job-change SaaS, 7 false positive (filtered out)

### Esempio 3 — Fallback nicchia (founder small)

**Input**: "Founder Italia, eCommerce 1-10 employees" (nicchia, Apollo coverage low)

**Workflow**:

1. Sales Nav coverage migliore di Apollo per founder small company
2. Search: Italy + Founder + eCommerce + size 1-10
3. Extract 30 LinkedIn URL
4. Waterfall enrichment: Hunter low coverage (small company), Apollo zero, parallel-cli per email guess + verify
5. Coverage finale 60% → sotto threshold 85% → warning all'utente "nicchia coverage limitata, accettato come expected"

## Gotchas

- 🔴 **Mass profile visit detection**: NON visitare full profile per ogni search result. Solo headline + name + URL. Bulk profile visit (>30/giorno) trigga LinkedIn captcha + temp restriction.
- 🔴 **Mass connection request**: NON inviare connection request automatici. Pattern di outbound LinkedIn = manual review + send via HeyReach (multi-account distribution se necessario), NON via questo skill.
- 🔴 **Bulk static list**: NO output 1000+ URL one-shot. Cap a 100 lead/giorno, suggest multi-day batch. Decay 30%/anno → static list building anti-pattern.
- 🔴 **Anti-detection blunders**: NO rapid action (>1/sec), NO backwards navigation rapid, NO same-IP+account from multiple devices simultanee.
- 🟡 **Sales Nav vs organic**: organic search ha limit lower (~50/giorno raccomandato), filtri meno potenti. Per volume serio → Sales Navigator.
- 🟡 **LinkedIn ToS update**: limit ufficiali cambiano. Disclaimer all'utente "verifica per il tuo account type / region". Non hardcoded come legge.
- 🟡 **Privacy mode profili**: alcuni profili hanno privacy off → no headline visibile. Skip + log "private_profile".
- 🟢 **Job-change signal alta priorità**: pattern 2026 è oro. Lead in transizione = buying window all'arrivo nuova company. Score boost +10 timing.
- 🟢 **Multi-account distribution**: per volume >100/giorno, NON usare un solo account. Setup HeyReach pattern team-based (NON in scope di questa skill, in scope di `/outbound-orchestrator` futuro).

## Scripts

- `scripts/linkedin_quota_update.py` (TODO Fase C.3): track quota giornaliera
- `scripts/mcp_detect.py`: check playwright availability

## References

- [references/lead-enrichment-best-practices-2026.md](../../references/lead-enrichment-best-practices-2026.md): sezione LinkedIn safe extraction patterns 2026

## Crediti

Pattern signal-based extraction 2026 (Wiza, SyncGTM URL-as-signal, HeyReach multi-account, Amplemarket Duo human-in-loop) via NotebookLM `3b40733b`. Limiti numerici sono indicative consensus 2026, da verificare ufficialmente per account specifico.
