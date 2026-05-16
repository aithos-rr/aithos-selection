---
name: lead-enrichment
description: Arricchisce liste di lead grezzi (nome, azienda) con dati completi — email verificata, ruolo, LinkedIn, segnali intent, dimensione azienda — scrivendo risultato su Google Sheet. Usa parallel-cli + Attio MCP + scraping intelligente. Da usare con lista CSV/Sheet importata da evento/conferenza, export CRM, scraping LinkedIn Sales Navigator. Skill del Webinar 2 Claude Code per il GTM.
when_to_use: Liste lead grezze da enrichment, import CRM da arricchire, nuova lista post-evento, lead da LinkedIn Sales Navigator, outreach preparation
argument-hint: "<input-sheet-url-or-csv>"
allowed-tools: Read Write Bash
---

# Lead Enrichment

Trasforma una lista di 500 "nome + azienda" in una lista ricca con email verificata, ruolo confermato, LinkedIn, segnali intent, pronta per outreach SmartLead/HeyReach.

## When to use

Attiva quando:
- Lista lead con dati parziali (es. solo nome + company)
- Export CRM con >30% campi vuoti
- Nuova lista post-evento conferenza
- Scraping LinkedIn Sales Navigator da arricchire
- Preparazione campagna outbound

**Non attivare** se:
- Lista <10 (→ manuale più veloce)
- Dati già completi
- Lead enterprise (>1000 employees) — richiedono workflow differente

## Prerequisiti

- `parallel-cli` installato (con API key in `~/.zshrc`)
- Attio MCP configurato (per contesto aziendale)
- OAuth Google per scrivere su Sheet
- Lista input: CSV o Google Sheet con almeno colonne `Name`, `Company`

## Instructions

### Fase 1 — Ingest e validate

Leggi input (CSV o Sheet URL):

```bash
# Se CSV locale
python scripts/load_csv.py "<path>"
# Se Sheet URL
python scripts/load_sheet.py "<url>"
```

Output: lista di `{name, company, extra_fields}` normalizzata.

Validazione:
- Rimuovi duplicati (stesso name+company)
- Valida che abbia Name + Company (altrimenti skip con warning)

### Fase 2 — Enrichment batch

Per ogni lead, esegui in parallelo (Agent Teams):

```
Team di 4-5 agenti paralleli, ognuno arricchisce 20 lead.
```

Per lead, le operazioni:

1. **Email finder** via `parallel-cli enrich --type email --name "..." --company "..."`
2. **LinkedIn** via `parallel-cli search "site:linkedin.com/in <name> <company>"`
3. **Azienda** via Attio MCP se già nel CRM, altrimenti `parallel-cli research <company>`
4. **Ruolo** cross-check LinkedIn bio vs lista input
5. **Intent signals** (bonus): recent funding, hiring, job changes → `parallel-cli search "<company> funding 2026 OR hiring 2026"`

Compone lead arricchito:

```yaml
- name: "Mario Rossi"
  company: "Acme Corp"
  email: "mario.rossi@acme.com"   # verified via bouncer
  email_confidence: 0.92
  linkedin: "https://linkedin.com/in/mariorossi"
  role: "VP of Marketing"           # da LinkedIn current role
  role_confidence: 0.95
  company_size: "50-100"
  company_industry: "SaaS B2B"
  recent_signals:
    - "Acme raised Series A $15M in Feb 2026"
    - "Hiring 3 marketing roles"
  enriched_at: "2026-04-24T14:30:00Z"
```

### Fase 3 — Quality scoring

Per ogni lead arricchito, assegna score:

- **🟢 Hot (score 80+)**: email verified high confidence, role clear, signals positivi
- **🟡 Warm (50-79)**: dati completi ma signals incerti
- **🔴 Cold (<50)**: dati parziali, skip per outreach ora

### Fase 4 — Output to Sheet

Scrivi su Google Sheet (new tab o update):

| Name | Company | Email | Email conf | LinkedIn | Role | Company Size | Industry | Intent Signals | Score | Status |
|------|---------|-------|------------|----------|------|--------------|----------|----------------|-------|--------|
| Mario Rossi | Acme | mario@... | 0.92 | https://... | VP Marketing | 50-100 | SaaS | Series A Feb26 | 🟢 85 | Ready |

### Fase 5 — Review batch + Attio sync

Proponi all'utente (AskUserQuestion):
- **Sincronizza lead 🟢 Hot in Attio CRM**? (create_record via Attio MCP)
- **Skip 🔴 Cold** dalla lista outreach?
- **Manual review 🟡 Warm**?

### Fase 6 — Report

```markdown
# Lead Enrichment Report — YYYY-MM-DD

- Input: <N> lead
- Enriched: <N> (% successo)
- 🟢 Hot: <N>
- 🟡 Warm: <N>
- 🔴 Cold: <N>
- Failed: <N> (vedi log)

## Top 10 Hot leads
<lista breve>

## Next: <suggerimento — /outbound-campaign con lista Hot>
```

## Examples

### Esempio 1: 200 lead conferenza SaaStr 2026

Input: CSV con `Name`, `Company`, `Role (self-reported)`, `Email (scarabocchio)`
Processing: 10 agenti paralleli, ~20 min totali
Output: Sheet con 200 lead, 65% email verified, 30 🟢 Hot ready per outreach

### Esempio 2: CRM Attio audit

Lista: 500 contatti Attio con campo email vuoto
Enrichment: per ognuno trova email verificata
Sync: update record Attio con email + confidence

## Gotchas

- 🔴 **Email verification false positive**: confidence 0.8 != 100% verified. Usa bouncer/validator separato prima di inviare (cost: 1 cent/email, saves reputation).
- 🔴 **Rate limit parallel-cli**: oltre 100 call/min = throttling. La skill ha built-in backoff.
- 🔴 **GDPR**: lead EU richiedono lawful basis. Documenta fonte scraping e basis (contract/legitimate interest).
- 🟡 **LinkedIn anti-scraping**: se scraping diretto, usa Apify o Sales Nav ufficiale. Evita blacklist IP.
- 🟡 **Company duplicates**: "Acme Corp" vs "Acme Inc" vs "ACME" → normalize prima.
- 🟢 **Attio dedup**: prima di sync, check if record esiste via `mcp__attio__search_records`. Update vs create.
- 🟢 **Lista Hot → /outbound-campaign**: chain natural per passare da lista arricchita a outreach.

## Scripts

- `scripts/load_csv.py`, `scripts/load_sheet.py`: ingest
- `scripts/enrich_batch.py`: Agent Teams parallel
- `scripts/score.py`: quality scoring
- `scripts/write_sheet.py`: output Google Sheet
- `scripts/attio_sync.py`: sync Hot leads

## References

- `references/enrichment-fields.md`: catalogo 20 campi possibili + priorità
- `references/gdpr-compliance.md`: checklist EU lead
- `references/parallel-cli-recipes.md`: pattern call efficaci per enrichment

## Crediti

Skill originale Claude Week Learnn — Webinar 2 (Code GTM). Stack: parallel-cli + Attio MCP + OAuth Google.
