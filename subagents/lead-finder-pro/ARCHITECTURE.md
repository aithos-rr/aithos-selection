# ARCHITECTURE — `/lead-finder-pro`

> **Output Fase B** del build. Definisce identità, discovery, MCP detection, skills, references, schema config, system prompt skeleton, methodology, output format, edge case, anti-pattern, test plan. Tutte le decisioni hanno reference a `DECISIONS.md`.
>
> **Data**: 2026-04-29 · **Worker chat sessione 1** · **Input**: `BUILD-BRIEF.md`, `DECISIONS.md` (12 decisioni), `research/research-summary.md`

## 1. Identità + frontmatter

```yaml
---
name: lead-finder-pro
description: Da definizione ICP a lista lead arricchiti scorati e segmentati, pronti per outbound. Multi-vendor waterfall enrichment + Hunter MCP + email verification + GDPR-aware. Per SDR/BDR/Founder/Marketer GTM. Self-configuring al first run con discovery interattiva (8 domande), poi memoria persistente per tutti i run successivi. Audience non-developer Learnn.
when_to_use: Lista lead grezza da arricchire, nuova lista post-evento o conferenza, export CRM con campi vuoti, preparation campagna outbound, ricerca prospect ICP, audit qualità contatti CRM, segmentazione lead per priority bucket
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, AskUserQuestion
mcpServers:
  - hunter
  - attio-mcp
  - explorium
  - smartlead
  - heyreach
  - google-personal
  - playwright
skills:
  - icp-scoring
  - email-verification
  - gdpr-compliance
  - waterfall-enrichment
  - linkedin-safe-scraping
memory: project
model: sonnet
color: orange
---
```

Note:

- `hunter` MCP server aggiunto rispetto al BUILD-BRIEF iniziale (DECISION-005)
- `model: sonnet` confermato (DECISION-012)
- `memory: project` (DECISION-004 originale)

## 2. Discovery questionnaire (8 domande)

Salvato in `discovery/questions.md` come reference. Logica conseguente integrata nel system prompt sezione 2.

| # | Question | Header chip | Options | Conseguenza logica |
|---|----------|-------------|---------|--------------------|
| 1 | Qual è il tuo ruolo? | Ruolo | SDR · BDR · Marketing manager · Founder · Freelancer GTM | Adatta tono e profondità default |
| 2 | Quale tool di lead enrichment hai già attivo? | Enrichment | Hunter · Apollo · Clay · Cognism · Nessuno | Se Hunter → carica `apollo-api-recipes.md` SKIP; usa Hunter MCP. Se Apollo → carica `apollo-api-recipes.md`. Se Nessuno → suggerisci Hunter free tier |
| 3 | Quale CRM usi? | CRM | HubSpot · Pipedrive · Attio · Salesforce · Custom · Nessuno | Se Attio → usa `attio-mcp`. Se Nessuno → output CSV/Sheet only |
| 4 | Tool outbound? | Outbound | SmartLead · Lemlist · HeyReach · Instantly · Manuale | Chain con `/outbound-orchestrator` se SmartLead/HeyReach. Se Manuale → output CSV ready |
| 5 | Qual è il tuo ICP? (settore + dimensione + geo) | ICP | (free text) | Se contains "EU"/"Europa"/"Italia"/"EMEA" o paese EU → auto-load `gdpr-compliance.md` come priority + warning GDPR mode (DECISION-011) |
| 6 | Top 3 segmenti prioritari | Segmenti | (free text 3 lines) | Default ranking per scoring; salvato in config |
| 7 | Volume target lead/mese | Volume | <50 · 50-200 · 200-500 · 500+ | Se 500+ → suggerisci batch processing parallelo. Se <50 → conferma "manuale è più rapido?" |
| 8 | Quale industry pattern ICP scoring? | Pattern | SaaS B2B (60/40 fit/behavior) · Agency (50/50 relationship) · eCommerce (70/30 firmografico) · Custom | Carica template scoring corrispondente (DECISION-006) |

**Save target**: `<memory>/config.md` (project scope) — schema definitivo in sezione 6.

## 3. MCP detection table + fallback

| MCP server | Tipo | Required for | Fallback se mancante |
|------------|------|--------------|----------------------|
| `hunter` (mcp.hunter.io) | **Recommended primary** | Email finder + verifier nativo via LLM | Apollo API REST (skill `email-verification` switch); se anche Apollo mancante → manual SMTP via `smtplib` Python script |
| `attio-mcp` | Recommended se utente Attio | CRM sync (DECISION-011) | Skip CRM sync, output CSV/Sheet only + suggest manual import |
| `explorium` | Optional | Enrichment alternative | Use parallel-cli `enrich --type business` |
| `smartlead` | Optional | Chain con outbound campaign | Skip campaign upload, esporta CSV "ready for SmartLead import" |
| `heyreach` | Optional | LinkedIn outbound chain | Idem, esporta CSV LinkedIn URL list |
| `google-personal` | Recommended | Output Google Sheet | Output CSV locale in `output/leads_<timestamp>.csv` |
| `playwright` | Required (LinkedIn) | Sales Nav search, scraping | Bash + curl + html parsing (degraded mode), warning utente |

### Pattern detection (pseudocode per system prompt)

```python
# All'avvio del subagent, dopo discovery:
mcp_status = {}
for mcp in ["hunter", "attio-mcp", "explorium", "smartlead", "heyreach", "google-personal", "playwright"]:
    mcp_status[mcp] = verify_mcp(mcp)  # ping minimal call

# Save in config.md mcp_available + mcp_fallbacks_active
# Show user summary: "Tool disponibili: Hunter ✓, Attio ✓, Google Sheet ✓. Fallback attivi: explorium → parallel-cli, playwright → bash+curl (degraded)."
```

## 4. Skills companion (5 skill, contratto chiaro)

### 4.1 `icp-scoring/SKILL.md`

- **Cosa fa**: scora ogni lead 0-100 secondo template industry (60/40, 50/50, 70/30) + signal decay 50%/mese (DECISION-006, DECISION-007)
- **Input**: lead JSON arricchito + ICP description user + industry pattern selezionato
- **Output**: lead JSON con field `score`, `grade` (A/B/C/Disqualified), `score_breakdown`
- **References**: `icp-scoring-framework.md` (3 template + decay logic + grade band)
- **Activation**: prompted automaticamente da `/lead-finder-pro` Fase 3 methodology
- **Target righe SKILL.md**: ~180

### 4.2 `email-verification/SKILL.md`

- **Cosa fa**: verifica email waterfall — Hunter MCP → Apollo API → manual SMTP (DECISION-005)
- **Input**: email address + opzionali (nome, company per cross-check)
- **Output**: `{verified: bool, confidence: 0-1, method: hunter|apollo|smtp, notes: str}`
- **References**: `tool-integrations.md` (Hunter MCP usage, Apollo API recipe)
- **Activation**: prompted da `/lead-finder-pro` Fase 2 methodology + manualmente per single check
- **Target righe**: ~150

### 4.3 `gdpr-compliance/SKILL.md`

- **Cosa fa**: checklist GDPR pre-outreach (LIA documentation, opt-out handling, Article 9 sensitive data, data minimization). Auto-attiva se ICP EU (DECISION-011)
- **Input**: lead list + ICP description
- **Output**: report compliance (`compliant: bool, issues: [], lia_template: path`)
- **References**: `gdpr-compliance.md` (LIA template, 8-point checklist, sensitive data list)
- **Activation**: auto se EU detected, manual per audit
- **Target righe**: ~180

### 4.4 `waterfall-enrichment/SKILL.md`

- **Cosa fa**: orchestrazione multi-vendor enrichment chain Hunter → Apollo → Clay → manual; coverage threshold 85% (DECISION-008); conflict-flag policy (DECISION-009); manual-field protection (DECISION-010)
- **Input**: lead list (CSV/JSON) con almeno `name + company`
- **Output**: lead enriched JSON con campi standard (`email, role, linkedin, company_size, industry, intent_signals, _conflicts, _enriched_at`)
- **References**: `lead-enrichment-best-practices-2026.md`, `tool-integrations.md`
- **Activation**: core methodology Fase 2
- **Target righe**: ~220

### 4.5 `linkedin-safe-scraping/SKILL.md`

- **Cosa fa**: signal-based extraction LinkedIn (Sales Nav search via playwright, non bulk static); soft daily limit configurabile (default 80 organic / 1000 dedicated); job-change trigger pattern
- **Input**: ICP query (industry, size, role) + max_leads
- **Output**: lista LinkedIn URL + base profile data → input per waterfall-enrichment
- **References**: `linkedin-safe-patterns.md` (consolidata in `prompt-patterns.md` cross-reference)
- **Activation**: Fase 1 methodology se source = LinkedIn
- **Target righe**: ~160

## 5. References docs (6 file)

| File | Sorgente | Content map |
|------|----------|-------------|
| `lead-enrichment-best-practices-2026.md` | Fase A research-summary Q1 + Q4 + Q7 | 7 best practice, edge case, case study reali, citation tracking |
| `tool-integrations.md` | Fase A Q2 + WebFetch Hunter API V2 + Apollo docs | Hunter MCP usage, Apollo API recipes, Clay (skip per v1), Cognism (EMEA mode), comparison table |
| `gdpr-compliance.md` | Fase A Q5 + Recital 47 testo integrale | LIA template, 8-point checklist, sensitive data Article 9, opt-out workflow, retention guidance |
| `icp-scoring-framework.md` | Fase A Q3 | 3 template (SaaS/Agency/eCommerce), tabella pesi numerica, signal decay, grade band, decay strategy |
| `prompt-patterns.md` | Knowledge interna + skill-builder pattern | Esempi prompt eccellenti per il modello quando user chiede cose specifiche (es. "scrivimi message per Hot lead VP marketing SaaS"); template di output |
| `apollo-api-recipes.md` | WebFetch docs.apollo.io + Q2 research | Pattern call efficaci con esempio JSON request/response (people-search, organization-search, bulk-enrich); rate limit handling |

## 6. Schema config (`<memory>/config.md`)

```yaml
---
agent: lead-finder-pro
created: 2026-04-29
last_updated: 2026-04-29
schema_version: 1
---

# Identità utente

user:
  role: founder  # SDR | BDR | Marketing | Founder | Freelancer GTM | Other
  experience_level: intermediate  # beginner | intermediate | advanced (auto-detected da Q1)

# Stack tools

stack:
  enrichment_primary: hunter  # hunter | apollo | clay | cognism | none
  enrichment_fallback: [apollo, manual]
  crm: attio  # hubspot | pipedrive | attio | salesforce | custom | none
  outbound: smartlead  # smartlead | lemlist | heyreach | instantly | manual

# ICP

icp:
  description: "SaaS B2B, 10-50 employees, USA + EU"
  geo_includes: [USA, EU]
  geo_eu_detected: true  # auto-flag → GDPR mode active
  segments:
    - "FinTech early-stage USA"
    - "MarTech Europe"
    - "AI tools mid-stage"
  industry_pattern: saas_b2b_60_40  # saas_b2b_60_40 | agency_50_50 | ecommerce_70_30 | custom

# Preferenze

preferences:
  monthly_volume: "200-500"  # <50 | 50-200 | 200-500 | 500+
  intent_signals: high  # high | medium | low

# Scoring config

scoring:
  template: saas_b2b_60_40
  signal_decay_monthly: 0.5  # default 50%/mese (DECISION-007)
  thresholds:
    hot: 90
    warm: 75
    cold: 50
    disqualified_below: 50

# Waterfall config

waterfall:
  coverage_threshold: 0.85  # 85% match rate target (DECISION-008)
  conflict_policy: flag  # flag | auto_first | auto_highest_confidence (DECISION-009)
  manual_fields_protected: [email, phone, role]  # DECISION-010

# GDPR

gdpr:
  mode_active: true  # auto-set da geo_eu_detected
  lia_documented: false  # set true after user confirms LIA created
  opt_out_handling: immediate  # immediate | scheduled

# MCP availability

mcp_available:
  hunter: true
  attio-mcp: true
  explorium: false
  smartlead: true
  heyreach: false
  google-personal: true
  playwright: true

mcp_fallbacks_active:
  explorium: parallel-cli
  heyreach: csv_export
```

## 7. System prompt skeleton (9 sezioni)

Target totale: **350-450 righe** (range BUILD-BRIEF: 300-500). Sezioni numerate per facile review.

| # | Sezione | Righe target | Content |
|---|---------|--------------|---------|
| 1 | Identità + ruolo | 20 | Chi sei, per chi lavori, audience non-developer Learnn, italiano user-facing |
| 2 | Discovery flow | 60 | Check `<memory>/config.md`. Se mancante → 8 AskUserQuestion sequence (vedi `discovery/questions.md`) → save config. Logica conseguente per ogni Q |
| 3 | MCP detection logic | 40 | `verify_mcp()` per ogni server, save status in config, mostra summary "Tool disponibili: X. Fallback attivi: Y" |
| 4 | Methodology principal (6 fasi) | 90 | Ingest → Enrich (waterfall) → Score (icp-scoring) → Segment (Hot/Warm/Cold) → Output (CSV/Sheet/Attio) → Sync (CRM if avail) |
| 5 | Tool usage rules | 50 | Quando Hunter MCP vs Apollo vs Clay vs scraping; quando playwright vs parallel-cli; mcp__attio__ rules |
| 6 | Output format | 35 | Schema CSV/Sheet, colonne required, JSON intermedio, naming convention file output |
| 7 | Edge cases handling | 50 | 14 edge case da Fase A (greylisting, catch-all, EU GDPR auto-load, signal decay, conflict, manual-field, ecc.) |
| 8 | Examples input → output | 50 | 3 esempi reali end-to-end: (a) 200 lead conferenza SaaStr, (b) audit Attio 500 contatti, (c) Sales Nav 100 lead nuova ICP |
| 9 | Anti-patterns | 20 | Cosa NON fa MAI: spammy bulk con bounce >5%, scrape sensitive data, overwrite manual fields, skip LIA su EU lead, hardcoded prezzi tool |

## 8. Methodology operativa (6 fasi del subagent)

### Fase 1 — Ingest e validate

- Source detect: CSV path | Sheet URL | LinkedIn Sales Nav URL | Attio export | manual paste
- Normalize: `{name, company, [optional: email, role, linkedin, ...]}`
- Dedupe (`name + company` lowercase normalized)
- Validate min schema (Name + Company), skip + warn lead invalidi

### Fase 2 — Enrichment (skill `waterfall-enrichment`)

- Per ogni lead non già completo:
  1. Hunter MCP `email-finder` (DECISION-005)
  2. Fallback Apollo API se Hunter miss
  3. Fallback Clay (se MCP) o manual SMTP
  4. LinkedIn URL via parallel-cli search se non presente
  5. Company info via Attio MCP se nel CRM, altrimenti `parallel-cli research <company>`
  6. Intent signals: `parallel-cli search "<company> funding 2026 OR hiring 2026 OR job-change"`
- Apply manual-field protection (DECISION-010)
- Track conflicts (DECISION-009)
- Coverage check 85% threshold (DECISION-008) — se sotto, suggerisci aggiunta vendor

### Fase 3 — Scoring (skill `icp-scoring`)

- Apply industry template (60/40, 50/50, 70/30) — DECISION-006
- Signal decay 50%/mese applicato a behavioral signals (DECISION-007)
- Output `score 0-100`, `grade A/B/C/Disqualified`, `score_breakdown JSON`

### Fase 4 — Segmentation

- Group by grade band: Hot (90-100), Warm (75-89), Cold/Nurture (50-74), Disqualified (<50)
- Apply negative signals (-25 unsubscribe, -40 competitor)
- Optional: tag manual review se `_conflicts` non vuoto

### Fase 5 — Output (CSV / Sheet)

- Schema standard (vedi sezione 9)
- Output path: `output/leads_<YYYYMMDD_HHMM>_<grade>.csv` o Sheet new tab via `google-personal` MCP
- Anche export JSON intermedio in `output/leads_raw_<timestamp>.json` per re-processing

### Fase 6 — Sync CRM (opzionale)

- Se `attio-mcp` disponibile e user opt-in:
  - Hot leads → `mcp__attio__create_record` (con dedup `mcp__attio__search_records` first)
  - Warm leads → suggest manual review
  - Cold/Disqualified → skip
- Se SmartLead/HeyReach disponibile e user opt-in: chain a `/outbound-orchestrator` (futuro)
- Sempre: log final report in `output/report_<timestamp>.md`

## 9. Output format

### CSV / Sheet schema standard

| Colonna | Type | Required | Source |
|---------|------|----------|--------|
| `name` | str | yes | input |
| `company` | str | yes | input |
| `email` | str | yes (after enrich) | waterfall |
| `email_confidence` | float 0-1 | yes | email-verification |
| `email_verified_at` | ISO timestamp | yes | email-verification |
| `linkedin` | URL | optional | parallel-cli/playwright |
| `role` | str | optional | LinkedIn / Apollo |
| `role_confidence` | float 0-1 | optional | enrichment |
| `company_size` | str (50-100) | optional | Apollo/Clay |
| `industry` | str | optional | Apollo/Clay |
| `intent_signals` | str (JSON list) | optional | parallel-cli |
| `score` | int 0-100 | yes | icp-scoring |
| `grade` | A\|B\|C\|D | yes | icp-scoring |
| `score_breakdown` | str (JSON) | yes | icp-scoring |
| `_conflicts` | str (JSON list) | optional | waterfall |
| `_enriched_at` | ISO timestamp | yes | waterfall |
| `gdpr_status` | compliant\|review\|excluded | yes if EU | gdpr-compliance |
| `notes` | str | optional | user/system |

### JSON intermedio

```json
{
  "lead_id": "uuid",
  "input": {"name": "...", "company": "..."},
  "enriched": {"email": "...", "...": "..."},
  "scoring": {"score": 87, "grade": "B", "breakdown": {...}, "decay_applied": 0.5},
  "gdpr": {"status": "compliant", "lia_ref": "lia-2026-04.md"},
  "_meta": {"enriched_at": "...", "conflicts": [], "manual_fields_protected": [...]}
}
```

## 10. Edge case map (14 edge case → handler)

Riprende da `research-summary.md` sezione "Edge case scoperti". Ogni edge case ha handler chiaro nel system prompt sezione 7:

| # | Edge case | Handler |
|---|-----------|---------|
| 1 | Greylisting (SMTP temp fail) | Polling backoff: retry dopo 5/15/60 min, max 3 retry |
| 2 | Catch-all false positive | Activate solo se Hunter confidence ≥0.80, altrimenti skip + flag |
| 3 | Disposable email | Detect via Hunter MCP `disposable: true` field → exclude |
| 4 | Gibberish address | Regex check (entropy > soglia) → flag manual review |
| 5 | Job-change event | Re-enrich + flag opportunity at new company (BOTH actions) |
| 6 | Signal decay 50%/mese | `score_recalc(lead, decay)` se `_enriched_at` > 30 giorni |
| 7 | Strategy-change decay | Warning se ICP description cambiata in config rispetto a precedente run; suggest full re-score |
| 8 | Provider data conflict | Flag in `_conflicts`, mark `needs_review` se conflict su email/phone |
| 9 | Manual-field protection | Write-only-to-empty su `manual_fields_protected` |
| 10 | Mass scraping LinkedIn flag | Soft daily limit warning se richiesta > 80 organic / giorno |
| 11 | Negative signal scoring | Apply -25 unsubscribe, -40 competitor automaticamente |
| 12 | EU lead context | Auto-load `gdpr-compliance.md`, set `gdpr_mode=true`, schema validation Article 9 |
| 13 | LinkedIn limit disclaimer | Mostrare reminder a inizio run "Verifica i tuoi limit per account" |
| 14 | Article 9 sensitive data | Schema validation reject se field include health/race/political/religious |

## 11. Anti-pattern (cosa l'agent NON fa)

1. **Mai bulk send email senza verification** (bounce >5% = domain reputation killer)
2. **Mai overwrite manual-verified fields** (DECISION-010)
3. **Mai scrape Article 9 sensitive data** (health, race, political, religious)
4. **Mai skip LIA su EU lead** (DECISION-011)
5. **Mai hardcoded pricing** dei tool nel system prompt (cambia, va in references)
6. **Mai assumere static list** valida >90 giorni senza re-enrichment
7. **Mai auto-pick first vendor in conflict** se policy = flag (DECISION-009)
8. **Mai inviare a `info@`/`sales@`/`support@`** in personalized sequence
9. **Mai dichiarare verified email senza confidence ≥0.80** quando catch-all
10. **Mai chiedere all'utente cosa fare se la domanda ha già risposta in config**

## 12. Test plan (per Fase D)

7 test checklist da BUILD-BRIEF, mappati a step concreti:

| # | Test | Setup | Pass criteria |
|---|------|-------|---------------|
| 1 | Discovery flow end-to-end | Dir test pulita senza config.md | 8 AskUserQuestion mostrate, config.md salvato con tutti i field |
| 2 | Re-run skip discovery | Stessa dir con config.md presente | Nessuna AskUserQuestion, conferma "Config trovata, sono pronto" |
| 3 | Real task small | CSV 20 lead `test-fixtures/leads-20.csv` | Output Sheet (o CSV se Google Sheet missing) con tutte 20 lead, score+grade per ognuno, no errori |
| 4 | MCP fallback | Disabilita `attio-mcp` (rinomina temporaneamente) | Warning "Attio non disponibile, output solo CSV", continua flow, no crash |
| 5 | Reconfigure | User dice "voglio cambiare config" | Config.md backup, nuova discovery 8 Q, nuovo config salvato |
| 6 | Edge case duplicati + parziali | CSV `test-fixtures/leads-edge.csv` con 5 dup + 2 parziali | Dedupe = 3 lead unici processati, parziali skipped con warning, log show |
| 7 | GDPR EU | CSV `test-fixtures/leads-eu-3.csv` con 3 lead EU | `gdpr_mode=true` attivato, LIA template suggested, output ha campo `gdpr_status` per ogni lead |

Fixtures da creare in `test-fixtures/` (Fase D).

## 13. Build order Fase C (dipendenze risolte)

Ordine esecuzione (early ones unlock later ones):

1. **References docs** (parallel-buildable, zero dipendenze interne)
   - `lead-enrichment-best-practices-2026.md` (riusa research-summary)
   - `tool-integrations.md`
   - `gdpr-compliance.md`
   - `icp-scoring-framework.md`
   - `prompt-patterns.md`
   - `apollo-api-recipes.md`
2. **Skills companion** (dipendono da references, parallel-buildable tra loro)
   - `icp-scoring/SKILL.md`
   - `email-verification/SKILL.md`
   - `gdpr-compliance/SKILL.md`
   - `waterfall-enrichment/SKILL.md`
   - `linkedin-safe-scraping/SKILL.md`
3. **Scripts** (parallel-buildable)
   - `discovery_check.py`
   - `mcp_detect.py`
   - `apollo_search.py`
   - `email_verify_waterfall.py`
   - `csv_to_sheet.py`
   - `attio_sync.py`
4. **Subagent main file** `lead-finder-pro.md` (depend su tutto sopra; assembla riferimenti)
5. **README.md** (depend su tutto, user-facing)

→ Posso usare `general-purpose` agent per scripts deterministici in parallelo (Fase C ottimization).

## 14. Verification Fase B done

- [x] ARCHITECTURE.md scritto e review-ready
- [x] Frontmatter agent definito (mcpServers + skills + memory)
- [x] 8 discovery questions con logica conseguente
- [x] MCP detection table + 7 fallback documentati
- [x] 5 skills companion con contratto + target righe
- [x] 6 references docs con content map
- [x] Schema config.md completo (16 field principali)
- [x] System prompt skeleton 9 sezioni con conta righe target (350-450 totali)
- [x] Methodology 6 fasi operative
- [x] Output schema CSV/Sheet (17 colonne) + JSON intermedio
- [x] 14 edge case → handler chiaro
- [x] 10 anti-pattern documentati
- [x] 7 test plan mappati per Fase D
- [x] Build order Fase C ottimizzato (parallelizzabile)
