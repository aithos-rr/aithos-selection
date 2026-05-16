---
name: waterfall-enrichment
description: Orchestra enrichment multi-vendor waterfall — Hunter MCP (primary, ha MCP nativo) → Apollo API → Clay (se MCP) → manual SMTP. Coverage threshold 85% match rate prima break. Conflict-flag policy (no auto-pick first). Manual-field protection (write-only-to-empty su email/phone/role). Output JSON enriched standard. Da usare quando hai lista lead con campi vuoti, post-evento conferenza con dati parziali, audit qualità CRM, batch 50-500 lead.
when_to_use: Lista lead con campi vuoti (email, role, linkedin), post-evento conferenza CSV parziale, audit qualità CRM con coverage <85%, output skill linkedin-safe-scraping da arricchire, batch enrichment 50-500 lead, re-enrichment 90-day cycle
allowed-tools: Read Write Bash(python:*) Bash(curl:*)
---

# Waterfall Enrichment

Orchestratore multi-vendor che trasforma lista "name + company" in lead JSON enriched completo (email + role + LinkedIn + company size + industry + intent signals). Pattern 2026: Hunter primary, fallback chain, threshold coverage 85%.

## When to use

Attivare quando:

- Lead list con campi vuoti (typically `email`, `role`, `linkedin`)
- Post-evento conferenza: CSV con `name + company` only
- Audit CRM: contatti con coverage <85% sui campi standard
- Output da skill `linkedin-safe-scraping` (lista LinkedIn URL) da arricchire con email
- Batch 50-500 lead da preparare per outreach
- Re-enrichment 90-day cycle (data decay 30%/anno)

Non attivare se:

- Lead list già completa (>95% coverage)
- Single lead lookup (use direct skill `email-verification` invece)
- Volume <10 lead (manuale è più rapido)

## Prerequisiti

- Stack tools configurato in `<memory>/config.md` (`stack.enrichment_primary`, `stack.enrichment_fallback`)
- Almeno UNO di: Hunter MCP available, Apollo API key, parallel-cli authenticated
- Reference `references/tool-integrations.md` accessibile

## Instructions

### Fase 1 — Validate input

Per ogni lead:

- [ ] Required: `name` + `company` (almeno uno dei due, idealmente entrambi)
- [ ] Skip se entrambi vuoti → log "skipped: insufficient data"
- [ ] Normalize: lowercase trim per dedup
- [ ] Detect already-enriched: se `_enriched_at` < 30 giorni → skip o re-enrich solo missing fields

### Fase 2 — Manual-field protection setup (DECISION-010)

Leggi `config.waterfall.manual_fields_protected` (default: `[email, phone, role]`).

Per ogni lead, marca quali campi NON overwriteable (campi già popolati in input).

### Fase 3 — Tier 1: Hunter (primary)

```bash
# Via Hunter MCP (preferito)
hunter.email_finder(first_name="Sara", last_name="Bianchi", domain="nimbusfintech.com")

# Risultato:
{
  "data": {
    "email": "sara@nimbusfintech.com",
    "score": 92,
    "first_name": "Sara",
    "last_name": "Bianchi",
    "position": "VP Marketing",
    "linkedin_url": "https://linkedin.com/in/sarabianchi",
    "twitter": null
  }
}
```

Hunter restituisce email + position + LinkedIn in 1 call. Salva i campi (rispettando manual-field protection).

Se Hunter MCP not available, usa REST V2:

```bash
curl "https://api.hunter.io/v2/email-finder?domain=nimbusfintech.com&first_name=Sara&last_name=Bianchi&api_key=$HUNTER_API_KEY"
```

### Fase 4 — Tier 2: Apollo (fallback se Hunter miss)

Se Hunter ritorna `email: null` o score <70:

```bash
python scripts/apollo_search.py --query '{"first_name":"Sara","last_name":"Bianchi","organization_name":"Nimbus FinTech"}' --per-page 1
```

Apollo `people/match` o `mixed_people/search` restituisce dati simili. Mark `_source: "apollo"` per tracking.

**Conflict detection**:

- Se Hunter ha restituito email "x@y.com" score 60 (sotto threshold)
- Apollo restituisce email "z@y.com" verified
- → Flag in `_conflicts: [{field: 'email', providers: ['hunter', 'apollo'], values: ['x@y.com', 'z@y.com']}]`
- Mark `needs_review: true` (DECISION-009)

### Fase 5 — Tier 3: Clay/parallel-cli (fallback Apollo)

Se entrambi miss:

```bash
parallel-cli enrich --type business --name "Sara Bianchi" --company "Nimbus FinTech"
```

Lower confidence, ma può recuperare lead difficili (founder small company senza Apollo presence).

### Fase 6 — Tier 4: Manual SMTP (last resort)

Solo se opt-in via flag:

```bash
python scripts/email_verify_waterfall.py --email <derived> --enable-smtp --tier 3
```

Email candidates da provare: `firstname.lastname@domain`, `firstname@domain`, `f.lastname@domain`. Cap a 3 candidate, no brute force.

### Fase 7 — Email verification (mandatory)

OGNI email enriched (da qualsiasi tier) → pass through skill `email-verification` waterfall:

```text
email_verification.verify(email=lead.email, threshold=0.80)
```

Solo email con `verified: true + confidence ≥0.80` sopravvivono al filtro. Le altre → flag `email_verified: false` (lead resta in lista ma marked).

### Fase 8 — Company info enrichment

Per ogni unique `company`:

1. **Attio MCP** (se utente Attio user e company già nel CRM): `mcp__attio__search_records` per company → estrae industry, size, ecc.
2. **Hunter MCP `enrichment`**: company size, industry, technology stack
3. **Apollo organization-search**: total_funding, latest_funding_date, technologies
4. **parallel-cli**: `parallel-cli research <company>` per intent signal news/hiring

Combina i risultati. Conflict policy come Fase 4.

### Fase 9 — Intent signals layer

Per ognuna company:

```bash
parallel-cli search "<company> funding 2026 OR Series OR hiring marketing OR job-change"
```

Estrai signal recenti (≤90 giorni):

- Funding round
- Hiring (specifically marketing/sales/eng)
- Job change leadership
- Product launch
- News mentions

Aggiungi a lead `intent_signals: [list]`.

### Fase 10 — Coverage check (DECISION-008)

```python
total_leads = len(leads)
fully_enriched = sum(1 for lead in leads if all(lead.get(f) for f in ['email', 'role', 'linkedin']))
coverage = fully_enriched / total_leads
print(f"Coverage: {coverage:.0%}")

if coverage < 0.85:
    log_warning(f"Coverage {coverage:.0%} below 85% threshold. Suggested: aggiungi vendor (Cognism per EMEA, ZoomInfo per enterprise) or accept lower coverage.")
```

### Fase 11 — Output JSON standard

```json
{
  "lead_id": "uuid",
  "name": "Sara Bianchi",
  "company": "Nimbus FinTech",
  "email": "sara@nimbusfintech.com",
  "email_confidence": 0.92,
  "email_verified_at": "2026-04-30T08:30:00Z",
  "linkedin": "https://linkedin.com/in/sarabianchi",
  "role": "VP Marketing",
  "role_confidence": 0.95,
  "company_size": "51-200",
  "industry": "FinTech B2B SaaS",
  "intent_signals": ["Series A €15M Feb 2026", "hiring 3 marketing roles"],
  "_source": "hunter_mcp",
  "_enriched_at": "2026-04-30T08:30:00Z",
  "_conflicts": [],
  "_manual_fields_protected": []
}
```

### Fase 12 — Report finale

```text
Waterfall enrichment done.

Input: 200 lead
Tier 1 (Hunter): 145 enriched (72%)
Tier 2 (Apollo): 38 enriched (19%) — Hunter miss
Tier 3 (parallel-cli): 12 enriched (6%) — Apollo miss
Tier 4 (manual SMTP): 3 enriched (1.5%) — fallback chain
Failed: 2 (1%) — insufficient data, skipped

Coverage: 198/200 = 99% ✅ above 85% threshold

Conflicts flagged: 5 (need manual review)
Manual fields protected: 0 (no input pre-filled fields)
GDPR mode: active (3 lead EU detected) → gdpr-compliance check next

Total cost: ~$8 (200 Hunter credits + 20 Apollo credits)
```

## Examples

### Esempio 1 — Conferenza SaaStr 200 lead

**Input**: CSV `saastr_leads.csv` con `Name + Company` only (no email, no role).

**Workflow**:

1. Tier 1 Hunter: 140/200 trovate via email-finder
2. Tier 2 Apollo: 35 fallback su Hunter miss
3. Tier 3 parallel-cli: 15 fallback (founder small company)
4. Tier 4 manual SMTP: 3 (last resort, opt-in)
5. Failed: 7 (skipped: bad data input)
6. Coverage: 193/200 = 96% ✅

**Cost**: ~$10 (200 Hunter + 35 Apollo + 15 parallel-cli + 3 SMTP)

### Esempio 2 — Audit Attio CRM 500 contatti

**Input**: 500 contatti Attio con campo email vuoto.

**Workflow**:

1. Pre-load via `attio-mcp.search_records` per contesto (company info già present)
2. Tier 1 Hunter: 350 enriched
3. Tier 2 Apollo: 100 fallback
4. Tier 3 parallel-cli: 30 fallback
5. Failed: 20 (no enriched possibile, suggerito manuale)
6. **Sync back Attio**: skill `attio_sync` post-enrichment per update record

### Esempio 3 — Re-enrichment 90-day cycle

**Input**: 100 lead enriched 4 mesi fa, attivi nella sequence.

**Workflow**:

1. Detect `_enriched_at` > 90 giorni → mark for re-enrichment
2. Tier 1 Hunter: re-verify email (potrebbero essere bouncate ora)
3. parallel-cli: check intent signal recenti (funding nuovo, hiring, job-change)
4. Skill `icp-scoring`: recalc score con decay (signal vecchi -50%)
5. Output: 25 lead score down (decayed), 8 lead score up (new intent), 5 lead job-change detected (FLAG opportunity new company)

## Gotchas

- 🔴 **Manual-field overwrite bug**: bug v1 era overwrite anche con manual-field protection set. v2 verify mandatory: pre-Fase 3 marca campi `not_overwriteable` esplicitamente, post-enrichment check NO write su campi marked.
- 🔴 **Conflict silently ignored**: se non flagghi conflict, finisci con email mix Hunter+Apollo non-coerenti. Default policy = `flag` (DECISION-009), MAI auto-pick first.
- 🔴 **Hunter rate limit 5 req/sec free**: bulk 200 lead in <40 sec → throttle. Script gestisce backoff. Premium tier 15 req/sec.
- 🟡 **Coverage 85% non sempre achievable**: ICP nicchia (es. Founder solo-employee small company) può avere 60-70% max. Documento all'utente come "expected", non bug.
- 🟡 **Apollo bounce 15-25%**: NON skippare email-verification (Fase 7) anche se Apollo dice `email_status: verified`.
- 🟡 **Cross-tier latency**: tier 1+2+3+4 chain può prendere 5-10 min per 200 lead. Display progress bar all'utente.
- 🟢 **Cache hit warm**: re-enrichment lead già processed <30 giorni → cache hit, no API call.
- 🟢 **Job-change detection**: se Hunter restituisce diverso `position` rispetto a quanto avevamo, flag `job_change_detected: true` + signal "opportunity at new company".
- 🟢 **GDPR auto-mode**: se 1+ lead EU detected, skill `gdpr-compliance` auto-invocata post-enrichment.

## Scripts

- `scripts/apollo_search.py`: Tier 2 wrapper
- `scripts/email_verify_waterfall.py`: Fase 7 verification
- `scripts/mcp_detect.py`: detect Hunter/Attio MCP availability

## References

- [references/lead-enrichment-best-practices-2026.md](../../references/lead-enrichment-best-practices-2026.md): waterfall pattern + threshold + edge case
- [references/tool-integrations.md](../../references/tool-integrations.md): Hunter MCP, Apollo, Clay, fallback chain spec
- [references/apollo-api-recipes.md](../../references/apollo-api-recipes.md): Apollo API recipes per Tier 2

## Crediti

Pattern waterfall consolidato 2026 (SyncGTM, Amplemarket, Hunter MCP) via NotebookLM `3b40733b`. Skill v1 `lead-enrichment` (Webinar 2 Learnn) come baseline → estesa con Tier 4, conflict policy, manual-field protection, coverage threshold check.
