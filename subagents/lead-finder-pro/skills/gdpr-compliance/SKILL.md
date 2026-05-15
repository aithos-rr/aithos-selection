---
name: gdpr-compliance
description: Verifica compliance GDPR per lead enrichment EU. Auto-attiva se ICP description contains keyword EU/Europa/Italia/EMEA. Genera LIA template editabile, applica 8-point checklist (LIA documentato, Privacy Policy, source documented, no Article 9 sensitive data, data minimization, opt-out infrastructure, retention, negative scoring). Schema validation reject su sensitive data. Workflow opt-out via Hunter Error 451 e suppression list.
when_to_use: Lead EU detected in ICP description, schema validation pre-output Hot leads, audit compliance lista CRM esistente, generate LIA template per nuovo segment, response a Subject Access Request, processing opt-out request, retention review periodico
allowed-tools: Read Write Edit Bash(python:*)
---

# GDPR Compliance

Auto-attiva quando ICP user contains EU markers. Garantisce che il workflow lead enrichment + outreach rispetti GDPR Article 6 (legitimate interest via Recital 47), Article 9 (sensitive data exclusion), Right to Object (opt-out immediato), Data Minimization.

## When to use

Attivare quando:

- Discovery Q5 ICP description contains: `EU`, `Europa`, `Italia`, `EMEA`, paese EU (Germania, Francia, Spagna, ecc.) o estensione (UK, Switzerland)
- Schema validation pre-output (catch sensitive data eventualmente entered)
- User chiede "GDPR check" o "verifica compliance lista"
- User dice "voglio creare LIA per nuovo segment"
- Subject Access Request da prospect ("voglio sapere cosa avete su di me")
- Opt-out request handling (lead richiede deletion / no further processing)
- Retention review (lead inattivo >12 mesi, GDPR check pre-deletion)

Non attivare se:

- ICP è 100% USA / non-EU (no GDPR mode)
- Single email check (non batch list processing)

## Prerequisiti

- `<memory>/config.md` esiste e ha `gdpr.mode_active: true` (auto-set se EU detected) OR explicit user opt-in
- Reference `references/gdpr-compliance.md` accessibile
- (Optional) `<memory>/lia_<segment>_<date>.md` per ogni segment ICP processato

## Instructions

### Fase 1 — EU detection (al run)

Auto-attivata da subagent `/lead-finder-pro` se condizione (DECISION-011):

```python
eu_keywords = ["EU", "Europa", "Italia", "EMEA", "Italy", "Europe", "europea", "europeo", "Unione Europea"]
eu_countries = ["Italy", "France", "Germany", "Spain", "Netherlands", "Belgium", "Austria",
                "Sweden", "Finland", "Denmark", "Ireland", "Portugal", "Greece", "Poland",
                "Czech Republic", "Hungary", "Romania", "Bulgaria", "Croatia", "Slovenia",
                "Slovakia", "Estonia", "Latvia", "Lithuania", "Luxembourg", "Malta",
                "Cyprus", "Iceland", "Liechtenstein", "Norway", "Switzerland", "UK"]

if any(kw.lower() in icp_description.lower() for kw in eu_keywords + eu_countries):
    config.gdpr.mode_active = True
    show_warning("Modalità GDPR attiva: LIA richiesto, opt-out enforcement, dati sensibili filtrati")
    auto_load("references/gdpr-compliance.md")
```

### Fase 2 — LIA template generation

Per ogni nuovo `segment` in `icp.segments`, suggerisci all'utente di creare LIA via:

```bash
# Subagent prompts:
"Vuoi che generi LIA template per segment '<segment>'? (sì/no)"
```

Se sì → crea `<memory>/lia_<segment_slug>_<YYYYMM>.md` con template da `references/gdpr-compliance.md` sezione LIA Template, pre-compilato con:

- Controller = nome utente (da config user)
- ICP target = segment
- Source = stack tools dichiarato (Hunter, Apollo, ecc.)
- Article 9 exclusion = lista standard
- Opt-out infrastructure = unsubscribe link + 24h processing

User può editarlo.

### Fase 3 — Schema validation pre-output

Quando subagent sta per output lead list (Fase 5 methodology), invoca skill GDPR per validation:

```python
sensitive_fields = ["religion", "political_party", "health_condition", "ethnic_origin",
                    "sexual_orientation", "trade_union", "biometric_data", "genetic_data",
                    "private_address", "personal_phone_no_business_indicator"]

for lead in leads:
    detected = [f for f in lead.keys() if f in sensitive_fields]
    if detected:
        block_output()
        error(f"Lead {lead.name}: campi sensibili Article 9 rilevati: {detected}. RIMUOVERE prima di proseguire.")
```

### Fase 4 — 8-point checklist execution

Per ogni run con `gdpr.mode_active=true`, esegui automaticamente:

| # | Check | Pass criteria | Fail action |
|---|-------|---------------|-------------|
| 1 | LIA documentato per segment | File `<memory>/lia_<segment>_*.md` esiste | Warning: "LIA missing per <segment>. Creare?" |
| 2 | Privacy Policy linkabile | `<memory>/config.md` field `gdpr.privacy_policy_url` set | Warning: "Privacy Policy URL mancante" |
| 3 | Source documented | Ogni lead ha `_source` field | Auto-fix: aggiungi `_source: "lead-finder-pro"` |
| 4 | No Article 9 fields | Schema validation Fase 3 pass | Block output |
| 5 | Data minimization | Solo professional fields | Auto-strip non-professional fields |
| 6 | Opt-out infrastructure | `gdpr.opt_out_handling: immediate` in config | Warning: "Conferma opt-out workflow attivo" |
| 7 | Retention policy chiara | Default tabella applied | Display tabella ad utente |
| 8 | Negative scoring | Skill `icp-scoring` apply -25 unsubscribe | Auto-applied (no user action) |

Output report `<memory>/gdpr_check_<timestamp>.md` con esito 8/8 o lista issue.

### Fase 5 — Opt-out request processing

Quando user dice "il lead X ha chiesto opt-out":

1. **Add to suppression list**: append `<lead_email>` a `<memory>/suppression_list.md`
2. **Cessation immediate**: rimuovi da output corrente, flag `gdpr_status: excluded`
3. **Apply -25 score**: skill `icp-scoring` automatic
4. **Audit log**: entry in `<memory>/compliance_register_<year>.md` con timestamp + email + action `opt_out_user_request`
5. **Confirm**: subagent risponde "Lead X aggiunto a suppression. Non sarà più processato in future enrichment."

### Fase 6 — Subject Access Request response

Quando user dice "lead X chiede SAR / cosa abbiamo su di lui":

1. Search lead in tutti i CSV/Sheet/Attio del progetto: `python scripts/query_all_lead_sources.py --email "<email>"`
2. Compila report con: dati raccolti, source, retention policy, processing purpose, decisions log
3. Output `<memory>/sar_response_<email_hash>_<date>.md` editabile
4. Reminder: "Consegnare entro 30 giorni (deadline GDPR)"
5. Se richiede deletion → execute deletion (skill `delete_from_all_sources` se implementata) + add a suppression list

### Fase 7 — Retention review

Skill può essere invocata periodicamente (suggerimento: ogni 3 mesi):

```bash
"GDPR retention review"
```

Esegue:

- Lead inattivi >12 mesi (no touch + grade <B): flag per review
- Lead opted-out: confirm presence in suppression list
- Suppression list size growth: log
- Audit register completeness: check ultimo mese

Output report `<memory>/gdpr_retention_review_<date>.md`.

## Examples

### Esempio 1 — Auto-attivazione EU

**Discovery Q5**: "SaaS B2B, 10-50 employees, Europa + USA"

**Subagent action**:

1. Detect "Europa" → `gdpr.mode_active = true`
2. Warning all'utente: "🇪🇺 GDPR mode attivo. Auto-load gdpr-compliance.md."
3. Suggerisce: "Vuoi creare LIA template per i segment? (Top 3 segmenti da Q6)"
4. Schema validation attivata in Fase 5 output

### Esempio 2 — Article 9 violation block

**Input**: CSV con colonna `political_affiliation` (3 lead con valore "Center-right")

**Subagent action**:

1. Skill schema validation → detect `political_affiliation` in sensitive_fields
2. Block output: error "Article 9 violation. Field 'political_affiliation' = political opinions. RIMUOVERE colonna prima di proseguire."
3. Suggerisce fix: "rimuovi la colonna o riprocessa CSV senza"

### Esempio 3 — Opt-out request

**User**: "Il lead Mario Rossi (mario@acme.com) ha risposto 'tolgimi dai contatti'. Procedi."

**Subagent action**:

1. Add `mario@acme.com` to `<memory>/suppression_list.md`
2. Search current lead list → marca `gdpr_status: excluded` su lead matching email
3. Apply -25 score via skill `icp-scoring`
4. Log in `<memory>/compliance_register_2026.md`
5. Risponde: "Done. Mario Rossi aggiunto a suppression. Compliance register aggiornato."

## Gotchas

- 🔴 **EU detection false negative**: se utente scrive "Europe Continental" senza paese specifico, regex non match. Aggiungere keyword "continent" / "europe-wide" se serve. Default: chiedi conferma all'utente "ICP include EU? (y/n)" come fallback.
- 🔴 **Article 9 violation silent**: se schema CSV ha campi tradotti tipo `religione` (italiano), non match con `religion` inglese. Tradotti aggiunti in regex. Periodicamente review lista sensitive.
- 🔴 **LIA per segment vs global**: ogni segment ICP richiede LIA proprio. Un single LIA "general" non è sufficiente per audit.
- 🟡 **Suppression list crescita**: se >1000 entry, parser lento. Convertire in `.json` o sqlite per perf. v1: testo OK fino a 500 entry.
- 🟡 **Cross-region GDPR conflicts**: lead con `country: USA` ma `linkedin: linkedin.com/...` con citizenship EU. Default: trattare come EU (più conservativo).
- 🟡 **Retention auto-deletion**: NO auto-delete in v1 — solo flag per review. Manual deletion sempre user-confirmed.
- 🟢 **GDPR vs UK GDPR post-Brexit**: trattati come equivalenti per default. ICO ha proprio regime ma allineato.
- 🟢 **Source disclosure in email outbound**: skill `prompt-patterns` Pattern 6 include footer GDPR-safe. Auto-applied se gdpr.mode_active.

## Scripts

- `scripts/gdpr_validate.py` (TODO Fase C.3): schema validation + LIA check + 8-point execution
- `scripts/query_all_lead_sources.py` (TODO Fase C.3): SAR support, search across CSV/Sheet/Attio

## References

- [references/gdpr-compliance.md](../../references/gdpr-compliance.md): LIA template completo, 8-point checklist, sensitive data list, retention table, opt-out workflow

## Crediti

GDPR Recital 47 + Article 9 + best practice 2026 (Cognism EU compliance, Hunter Error 451). Disclaimer: guida operativa, non parere legale. Per production consulta DPO certificato.
