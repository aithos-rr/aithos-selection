# ARCHITECTURE — `/outbound-orchestrator`

> **Output Fase B** del build. Definisce identità, discovery, MCP detection, skills, references, schema config, system prompt skeleton, methodology, output format, edge case, anti-pattern, test plan. Tutte le decisioni hanno reference a `DECISIONS.md`.
>
> **Data**: 2026-04-30 · **Worker chat sessione 1** · **Input**: `BUILD-BRIEF.md`, `DECISIONS.md` (15 decisioni post-Fase A), `research/research-summary.md`

## 1. Identità + frontmatter

```yaml
---
name: outbound-orchestrator
description: Da output /lead-finder-pro (CSV/JSON enriched + scored A/B) a sequenza outbound multi-channel personalizzata via AI first-line, caricata su SmartLead/HeyReach via API, con reply detection 5-class + auto-pause. Action-driven (esegue invii reali). Safety contract stringente — dry-run default + confirm step. Per SDR/BDR/Founder che fanno outreach. Audience non-developer Learnn — italiano user-facing, inglese tecnico.
when_to_use: Lancio campagna outbound da lista lead Hot/Warm, multi-channel email + LinkedIn, personalizzazione AI first-line signal-driven, reply triage 5-class, GDPR EU compliance, A/B test subject + first-line, audit campagne attive
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, AskUserQuestion
mcpServers:
  - smartlead
  - heyreach
  - attio-mcp
  - google-personal
  - claude_ai_Gmail
skills:
  - personalization-engine
  - deliverability-check
  - reply-classification
  - sequence-builder
  - gdpr-opt-out
memory: project
model: sonnet
color: blue
---
```

Note:

- `claude_ai_Gmail` MCP aggiunto per forward positive reply (DECISION-012)
- `model: sonnet` (allineato a `/lead-finder-pro`, costo/qualità ottimale)
- `memory: project` (DECISION-004 originale, brand voice + ICP per progetto)
- `color: blue` (vs `lead-finder-pro` orange — distinguere chain output)

## 2. Discovery questionnaire (8 domande)

Definitivo in `discovery/questions.md`. Logica conseguente integrata nel system prompt sezione 2.

| # | Question | Header | Options | Save in | Conseguenza |
|---|----------|--------|---------|---------|-------------|
| 1 | Quale tool email outbound? | Outbound | SmartLead · Lemlist · Instantly · Manuale | `stack.outbound_primary` | smartlead → MCP path; manual → CSV export |
| 2 | LinkedIn outreach? | LinkedIn | HeyReach · Lemlist multi · Solo email | `stack.outbound_secondary` | heyreach → multi_channel=true |
| 3 | Brand voice? | ToV | Direct · Friendly · Educational · Bold | `brand.voice` | adatta personalization-engine prompt |
| 4 | Value prop (free text) | ValueProp | (text) | `brand.value_prop` | input first-line generation |
| 5 | Sequenza length? | SeqLen | 3 · 5 · 7 · Custom | `sequence.default_length` | carica template A/B/C/D |
| 6 | ICP description | ICP | (text) | `icp.description` | EU detect → GDPR mode |
| 7 | A/B test? | ABTest | On · Off | `sequence.ab_test_enabled` | 2× variants se on |
| 8 | GDPR mode? | GDPR | Auto · Always · Off | `gdpr.mode` | suppression + footer policy |

**Save target**: `<memory>/config.md` (project scope) — schema in sezione 6.

## 3. MCP detection table + fallback

| MCP server | Tipo | Required for | Fallback se mancante |
|------------|------|--------------|----------------------|
| `smartlead` | **Recommended primary** | Email campaign create + sequence + lead import + webhook | CSV export "ready for SmartLead manual import" |
| `heyreach` | Recommended se multi-channel | LinkedIn campaign + sequence + UpdateSequence | CSV export con LinkedIn URLs + manual import HeyReach UI |
| `attio-mcp` | Optional | Lead status sync bidirectional con `/lead-finder-pro` | Skip sync, log only in report |
| `google-personal` | Optional | Output report Google Sheet/Doc | Markdown locale `output/report_<ts>.md` |
| `claude_ai_Gmail` | Optional | Forward positive reply to user inbox | Log only "forward manualmente" |

### Pattern detection (pseudocode per system prompt)

```python
mcp_status = {}
for mcp in ["smartlead", "heyreach", "attio-mcp", "google-personal", "claude_ai_Gmail"]:
    mcp_status[mcp] = verify_mcp(mcp)
```

Save in `<memory>/config.md`: `mcp_available` + `mcp_fallbacks_active`.

Display summary in italiano:

```text
Tool disponibili:
✓ SmartLead MCP (email primary)
✓ HeyReach MCP (LinkedIn)
✓ Attio MCP (CRM sync opzionale)
✓ Gmail MCP (positive reply forward)
✗ Google Personal → fallback Markdown locale

Pronto a procedere.
```

## 4. Skills companion (5 skill, contratto chiaro)

### 4.1 `personalization-engine/SKILL.md`

- **Cosa fa**: AI first-line generation da signal extraction. 8 hook templates (job-change, funding, hiring, podcast, content, conference, tool-stack, geo). Anti-LLM-detection enforcement (DECISION-011): 8 banned markers + 3+ variant + 15-25 word constraint + uniqueness hash.
- **Input**: lead enriched JSON (incluso `intent_signals` JSON list) + brand voice + value prop
- **Output**: `{first_line: str, signal_used: str, hook_template_id: int, variant_n: int, confidence: 0-1}`
- **References**: `prompt-patterns.md` (8 hook templates), `tool-integrations.md` (n/a — wrapper only)
- **Activation**: per ogni lead in sequence build (Fase 3 methodology)
- **Target righe**: ~220

### 4.2 `deliverability-check/SKILL.md`

- **Cosa fa**: pre-flight check DKIM/DMARC/SPF (DNS query) + warmup status (mailbox age) + daily cap remaining (matrix DECISION-008) + blacklist scan + spam-trigger word check
- **Input**: sender mailbox config + lead list size + scheduled send time
- **Output**: `{ready: bool, issues: [], warnings: [], daily_cap_remaining: int, mailbox_age_days: int, dns_status: {spf, dkim, dmarc, bimi}}`
- **References**: `deliverability-2026.md`
- **Activation**: gate prima di ogni invio bulk (Fase 4 methodology)
- **Target righe**: ~190

### 4.3 `reply-classification/SKILL.md`

- **Cosa fa**: 5-class classify (positive/negative/OOO/unsubscribe/bounce) hybrid rule-based + LLM fallback (DECISION-012). Action per class: pause/forward/unsubscribe/snooze/suppress. Integrazione webhook SmartLead `LEAD_REPLIED`.
- **Input**: reply content + lead context (sequence step, signal_used) + DSN headers se bounce
- **Output**: `{class: str, confidence: 0-1, action: str, snooze_until: ISO ts | null, manual_triage: bool}`
- **References**: `outbound-best-practices-2026.md` (sezione reply handling)
- **Activation**: webhook handler + manual triage on demand
- **Target righe**: ~210

### 4.4 `sequence-builder/SKILL.md`

- **Cosa fa**: genera sequenza JSON `output/sequence_<...>.json` (DECISION-015 schema portable) da template (A/B/C/D) + value prop + brand voice + signals leads. Include widening gap default (DECISION-010) + multi-channel timing (DECISION-006).
- **Input**: lead segment + sequence template selected + brand voice + value prop + a/b test on/off
- **Output**: JSON sequence schema portable (channels, steps, variants, leads array, gdpr_footer_html)
- **References**: `sequence-templates.md` (4 template), `prompt-patterns.md` (variant generation)
- **Activation**: core methodology Fase 3
- **Target righe**: ~250

### 4.5 `gdpr-opt-out/SKILL.md`

- **Cosa fa**: suppression list cross-stack management (DECISION-013). Footer bilingue mandatory IT+EN se EU detected. LIA template generation. Italy Garante specifics. Retention 12 mesi enforcement. Article 9 reject. Reject lead role-based + B2C personal email.
- **Input**: lead list + ICP geo + suppression list path + LIA template path
- **Output**: `{compliant_leads: [], excluded: [{lead, reason}], footer_html: {it, en, bilingue}, lia_doc_path: str}`
- **References**: `gdpr-outbound-eu.md`
- **Activation**: auto se EU detected, manual per audit
- **Target righe**: ~200

## 5. References docs (6 file)

| File | Sorgente | Content map | Target righe |
|------|----------|-------------|--------------|
| `outbound-best-practices-2026.md` | RQ1 + RQ6 research | 7 best practice + cadence widening gap + multi-channel timing + send time + reply rate benchmark + reply handling 5-class | ~220 |
| `deliverability-2026.md` | RQ4 research | SPF/DKIM/DMARC/BIMI mandatory + warmup days/volume table + daily cap matrix + spam triggers + Postmaster threshold + blacklist scan | ~240 |
| `sequence-templates.md` | RQ1 + skill v1 outbound-campaign | 4 template (Direct Demo, Education-First, Pain Discovery, Multi-threading) con JSON example portable + step structure dettaglio | ~260 |
| `prompt-patterns.md` | RQ5 research | 8 signal-hook templates italiano+inglese + A/B variant generation + anti-LLM-detection 8 banned + first-line uniqueness hash | ~250 |
| `gdpr-outbound-eu.md` | RQ7 research + skill `/lead-finder-pro/gdpr-compliance` | LIA template B2B cold email + suppression cross-stack + Italy Garante specifics + retention 12mo + footer bilingue + Article 9 reject | ~200 |
| `api-recipes.md` | RQ2 + RQ3 + skill heyreach-api | SmartLead MCP recipes (create_campaign, save_sequence, add_leads, webhook) + HeyReach recipes (Create, UpdateSequence trick FINISHED, single-brace, sequence shape) + curl fallback examples | ~230 |

## 6. Schema config (`<memory>/config.md`)

```yaml
---
agent: outbound-orchestrator
created: 2026-04-30
last_updated: 2026-04-30
schema_version: 1
---

# Stack tools
stack:
  outbound_primary: smartlead    # smartlead | lemlist | instantly | manual
  outbound_secondary: heyreach   # heyreach | lemlist_multi | none

# Brand voice
brand:
  voice: direct                  # direct | friendly | educational | bold
  value_prop: "GTM Engineering audit gratuito per SaaS B2B post-Series A"
  signature: "Filippo Greco — Yellow Tech"
  signature_url: "https://yourdomain.com"

# ICP
icp:
  description: "SaaS B2B 10-50 employee, USA + EU"
  geo_eu_detected: true
  segments:
    - "FinTech early-stage USA"
    - "MarTech Europe"

# Sequence
sequence:
  default_length: 5              # 3 | 5 | 7 | custom
  multi_channel: true
  template: direct_demo          # direct_demo | education_first | pain_discovery | multi_threading | custom
  ab_test_enabled: true
  widening_gap: true             # DECISION-010

# Safety contract
safety:
  dry_run_default: true          # DECISION-014
  confirm_required_above: 50     # DECISION-005
  daily_cap_per_mailbox:
    cold_0_14d: 5                # DECISION-008
    warming_14_30d: 15
    warmed_30_90d: 50
    aged_90d_6mo: 100
    seasoned_6mo_plus: 250
  warmup_days_minimum: 14        # block bulk se mailbox <14d
  spam_rate_threshold: 0.3       # block se Postmaster >0.3%
  blacklist_scan: true

# Personalization
personalization:
  signal_recency_days: 30        # signal age <30d, decay 90d
  variant_count: 3               # min 3 variant per template (DECISION-011)
  first_line_max_words: 25       # constraint
  banned_markers:
    - "delve into"
    - "navigate the landscape"
    - "I hope this email finds you well"
    - "leverage"
    - "synergy"
    - "seamlessly"
    - "cutting-edge"
    - "—"   # em-dash sequenze multiple
  uniqueness_hash_window: 100    # last 100 first-line hash check

# Reply classification
reply_classification:
  classes: [positive, negative, OOO, unsubscribe, bounce]
  confidence_threshold: 0.85     # DECISION-012
  llm_fallback_enabled: true
  ooo_snooze_days: 10
  bounce_soft_retry_max: 3

# GDPR
gdpr:
  mode: auto                      # auto | always | off
  mode_active: true               # derived from icp.geo_eu_detected
  lia_documented: false           # set true after user confirms LIA created
  suppression_list_path: <memory>/suppression.csv
  footer_bilingue: true           # IT + EN se EU detected
  retention_months: 12
  reject_b2c_personal_email: true # gmail/yahoo/hotmail/libero personal

# MCP availability
mcp_available:
  smartlead: true
  heyreach: true
  attio-mcp: true
  google-personal: true
  claude_ai_Gmail: true

mcp_fallbacks_active:
  google-personal: markdown_local

# API key flags (NO storage, just presence — DECISION-007)
api_keys:
  smartlead_present: true        # env SMARTLEAD_API_KEY rilevato
  heyreach_present: true
  apollo_present: false           # se needed for cross-check email verify
```

## 7. System prompt skeleton (9 sezioni)

Target totale: **400 righe** (range BUILD-BRIEF: 350-500). Sezioni numerate per facile review.

| # | Sezione | Righe | Content |
|---|---------|-------|---------|
| 1 | Identità + ruolo | 25 | Chi sei, audience non-developer Learnn, italiano user-facing, **safety-first** vs lead-finder-pro |
| 2 | Discovery flow | 60 | Check `<memory>/config.md`. Se mancante → 8 AskUserQuestion (vedi `discovery/questions.md`) → save config. Logica conseguente per ogni Q |
| 3 | MCP detection logic | 40 | Verify per ogni server, save in config, mostra summary "Tool disponibili: X. Fallback attivi: Y" |
| 4 | Methodology principal (6 fasi) | 110 | Ingest → Validate → Personalize → Pre-flight check → Confirm/Dry-run → Execute → Monitor reply |
| 5 | Tool usage rules | 50 | Quando SmartLead vs HeyReach vs Attio vs Gmail; quando dry-run mandatory; quando confirm |
| 6 | Output format | 35 | Schema sequence JSON portable (DECISION-015), naming convention, report markdown structure |
| 7 | Edge cases handling | 45 | 12 edge case da Fase A research (warmup <14d, single-brace, FINISHED edit, GDPR Italy, ecc.) |
| 8 | Examples input → output | 50 | 3 esempi reali end-to-end: (a) 80 lead Hot SaaS USA email-only, (b) 30 lead EU multi-channel GDPR, (c) 200 lead enterprise multi-threading 7-step |
| 9 | Anti-patterns | 25 | 10 anti-pattern critici da BUILD-BRIEF + 2 da research (no `{{var}}` HeyReach, no Italy B2C) |

## 8. Methodology operativa (6 fasi del subagent)

### Fase 1 — Ingest e validate input

- Detect source: CSV path output `/lead-finder-pro` | JSON intermedio | manual paste
- Run `scripts/validate_input.py --csv <path>` → check schema 17 colonne (riprende da `/lead-finder-pro` ARCHITECTURE sez 9)
- Filter: `grade in [A, B]` default; reject lead `email_confidence < 0.80`; reject role-based; reject `gdpr_status: excluded`
- Output `output/leads_validated_<ts>.json`

### Fase 2 — Pre-flight deliverability check

- Skill `deliverability-check` invoke su sender mailbox config
- DNS query SPF + DKIM + DMARC (require `p=quarantine` minimum)
- Mailbox age check vs DECISION-008 matrix
- Daily cap remaining (call SmartLead API `get_warmup_stats_by_email_account_id`)
- Postmaster spam rate (manual prompt user "verifica spam rate <0.3%")
- BLOCK + warning chiaro se issue critical → utente fixa prima di proseguire

### Fase 3 — Personalization (skill `personalization-engine`)

Per ogni lead:

1. Extract `intent_signals` JSON list (output `/lead-finder-pro`)
2. Match a 1 di 8 hook templates (recency check <30d)
3. Generate first-line: 3+ variants per ogni signal-template combo (DECISION-011)
4. Anti-LLM-detection: scan banned markers + uniqueness hash check
5. Output: `{lead, first_line_variants: [...], signal_used, hook_template_id}`

### Fase 4 — Sequence build (skill `sequence-builder`)

- Apply template selezionato (A/B/C/D, da config `sequence.template`)
- Multi-channel timing widening gap (DECISION-006, DECISION-010)
- A/B test branching se `sequence.ab_test_enabled`
- GDPR footer enforce (skill `gdpr-opt-out`) → footer_html bilingue
- Output: `output/sequence_<campaign_name>_<ts>.json` portable schema (DECISION-015)

### Fase 5 — Confirm + Dry-run

- **DRY-RUN MANDATORY** (DECISION-014): preview 3 sequence sample + JSON schema check
- Display: campaign name, sequence steps, lead count, daily cap usage estimate, dry-run path
- Se `lead_count > confirm_required_above` (50, DECISION-005) → require explicit "yes confirm" testuale
- Se `lead_count <= 50` → procede dopo user "ok" (semplice)
- Override `--no-dry-run` solo se user specifica esplicitamente

### Fase 6 — Execute upload + monitor

#### 6a. SmartLead upload (se `outbound_primary = smartlead`)

```bash
python scripts/smartlead_upload.py \
  --sequence-json output/sequence_<...>.json \
  --campaign-name "<...>" \
  --confirm
```

Internamente: `mcp__smartlead__create_campaign` → `save_campaign_sequence` → `add_email_account_to_campaign` → `add_leads_to_campaign` → `update_campaign_status` (start). Webhook setup `LEAD_REPLIED` + `LEAD_BOUNCED` + `LEAD_UNSUBSCRIBED`.

#### 6b. HeyReach upload (se `outbound_secondary = heyreach`)

```bash
python scripts/heyreach_upload.py \
  --sequence-json output/sequence_<...>.json \
  --campaign-name "<...>" \
  --confirm
```

Internamente: `mcp__heyreach__add_leads_to_list_v2` (lista LinkedIn URL) → `mcp__heyreach__create_empty_list` se nuova → `campaign/Create` → `UpdateSequence` (single-brace enforcement, regex auto-fix) → `Resume` start.

#### 6c. Sync Attio (se `attio-mcp` available e user opt-in)

- Per ogni lead: `mcp__attio__update_record` `outbound_status = sequenced`
- Tag `campaign_id_smartlead`, `campaign_id_heyreach`

#### 6d. Monitor reply (asynchronous)

- Webhook handler chiamato da SmartLead → trigger `scripts/reply_classify.py`
- Skill `reply-classification` → mapping action
- Action `pause`: `mcp__smartlead__pause_lead_by_campaign`
- Action `unsubscribe`: append `<memory>/suppression.csv` cross-stack + `mcp__smartlead__add_lead_to_global_blocklist`
- Action `forward` (positive): `mcp__claude_ai_Gmail__create_draft` to user

### Fase 7 — Report

Output `output/report_<campaign_name>_<ts>.md` con:

- Campaign summary (name, total leads, sequence length, daily cap)
- Pre-flight check results (DKIM/DMARC/SPF, warmup, daily cap remaining)
- Personalization: variant distribution, signal-hook match rate
- Confirm + dry-run trace (path JSON dry-run)
- Execute trace (campaign_id SmartLead/HeyReach, webhook URLs setup)
- Next steps suggested (monitor 7d → first reply review)

## 9. Output format

### Sequence JSON portable (DECISION-015)

```json
{
  "campaign_name": "Yellow Tech — Series A SaaS USA — Q2 2026",
  "sequence_name": "direct_demo_5step_v1",
  "channels": ["email", "linkedin"],
  "steps": [
    {
      "step_n": 1,
      "channel": "email",
      "delay_days": 0,
      "subject_variants": ["{first_name}, {company} + GTM scaling", "Domanda su {company}"],
      "body_variants": ["Ciao {first_name},\n\n{first_line_variant_a}...", "Ciao {first_name},\n\n{first_line_variant_b}..."],
      "signal_used": "funding_series_a",
      "send_window": "tue_thu_9_13"
    },
    {
      "step_n": 2,
      "channel": "linkedin",
      "node_type": "CONNECTION_REQUEST",
      "delay_days": 2,
      "messages": ["Ciao {first_name}, ho visto del round Series A — congrats! Mi piacerebbe connetterci."],
      "fallback_message": "Ciao {first_name}, mi piacerebbe connetterci.",
      "signal_used": "funding_series_a"
    },
    {
      "step_n": 3,
      "channel": "email",
      "delay_days": 5,
      "subject_variants": ["Re: ..."],
      "body_variants": ["Ho condiviso il framework GTM con altri founder Series A..."]
    }
  ],
  "leads": [
    {"email": "...", "first_name": "...", "company": "...", "linkedin_url": "...", "signal_used": "funding_series_a", "first_line_variants": ["...", "...", "..."]}
  ],
  "ab_test": true,
  "gdpr_footer_html": "<p>...</p>",
  "lia_doc_path": "<memory>/lia_<campaign>_<date>.md",
  "_meta": {
    "created_at": "2026-04-30T11:00:00Z",
    "agent": "outbound-orchestrator",
    "schema_version": 1,
    "config_snapshot": {...}
  }
}
```

### Naming convention output

- Sequence JSON: `output/sequence_<campaign_name_kebab>_<YYYYMMDD_HHMM>.json`
- Dry-run preview: `output/dry_run_<campaign_name_kebab>_<ts>.json`
- Report: `output/report_<campaign_name_kebab>_<ts>.md`
- Suppression list: `<memory>/suppression.csv` (append-only)

## 10. Edge case map (12 edge case → handler)

Riprende da `research/research-summary.md` sezione 10:

| # | Edge case | Handler |
|---|-----------|---------|
| 1 | Mailbox warmup <14d | BLOCK bulk send via deliverability-check, warning user "fai warmup" |
| 2 | DKIM/DMARC missing | BLOCK + suggerisci setup, link `references/deliverability-2026.md` sezione setup |
| 3 | Spam rate >0.3% Postmaster | BLOCK + alert "decay reputation, fix prima" |
| 4 | Lead role-based (info@, sales@) | Reject in `validate_input.py` skip + log |
| 5 | Lead in suppression list | Skip + warning "X lead in suppression, esclusi", continua flow |
| 6 | Reply ambigua (LLM confidence <0.85) | Manual triage queue, append `<memory>/triage_queue.md` |
| 7 | OOO reply | Snooze 10d (default DECISION-012) → resume sequence |
| 8 | Bounce hard | Suppress immediato cross-campaign, mark `Do-Not-Contact` |
| 9 | HeyReach `{{var}}` double brace | Auto-fix regex prima di UpdateSequence (skill heyreach-api pattern) |
| 10 | Campaign HeyReach FINISHED edit needed | Resume → Pause → UpdateSequence (skill heyreach-api trick) |
| 11 | Italy lead + GDPR mode | Footer bilingue + LIA documentato + retention 12mo + Article 9 reject |
| 12 | A/B test variant <30 lead | Statistical warning "results not significant", ask continue |

## 11. Anti-pattern (cosa l'agent NON fa MAI)

10 da BUILD-BRIEF + 2 da research:

1. Mai bulk send su domain non-warmup (>14 giorni warmup minimum, DECISION-008)
2. Mai inviare a role-based (`info@`, `sales@`, `support@`, `noreply@`)
3. Mai skip suppression/opt-out lista (cross-campaign cross-stack)
4. Mai overshoot daily limit account (matrix DECISION-008)
5. Mai personalization stampata da template senza company-specific signal (anti-LLM-detection DECISION-011)
6. Mai eseguire batch >50 lead senza confirm step + dry-run preview (DECISION-005, DECISION-014)
7. Mai bypassare GDPR mode se geo EU detected (DECISION-013)
8. Mai inviare email senza unsubscribe link (CAN-SPAM + GDPR)
9. Mai sovrascrivere campagna esistente SmartLead/HeyReach senza confirm
10. Mai conservare API key in config.md (env vars only, DECISION-007)
11. Mai usare `{{var}}` double brace su HeyReach sequence (auto-fix obbligatorio)
12. Mai inviare a Italy B2C personal email (gmail/yahoo/hotmail/libero personal — Garante Italia restrittivo, DECISION-013)

## 12. Test plan (per Fase D)

10 test BUILD-BRIEF mappati a step concreti:

| # | Test | Setup | Pass criteria |
|---|------|-------|---------------|
| 1 | Discovery flow end-to-end | Dir test pulita senza config.md | 8 AskUserQuestion mostrate, config.md salvato con tutti i field |
| 2 | Re-run skip discovery | Stessa dir con config.md presente | Nessuna AskUserQuestion, conferma "Config trovata, sono pronto" |
| 3 | Input validation reject | CSV `test-fixtures/leads_invalid_schema.csv` | Reject con messaggio chiaro "schema non conforme /lead-finder-pro" |
| 4 | Input chain valid | CSV `test-fixtures/leads_sample_hot.csv` (10 lead grade A) | Procede, filter applicato, output `leads_validated_<ts>.json` |
| 5 | Personalization diversity | 5 lead diversi → 5 first-line | Verifica: signal usage diversity ≥3 hook templates, no banned markers, uniqueness hash check pass |
| 6 | Deliverability gate | `mailbox_not_warmed.json` (10d age) | BLOCK + warning, no execute |
| 7 | Confirm step >50 | 100 lead fixture | Require explicit "yes confirm", no execute prima |
| 8 | Dry-run mandatory | `--dry-run` flag default | Output JSON sequence senza chiamata API reale, salvato in `output/dry_run_<ts>.json` |
| 9 | MCP fallback SmartLead | SmartLead MCP missing | CSV export "ready for manual import", continua flow |
| 10 | GDPR EU enforce | `leads_sample_hot.csv` con 3 EU lead | Footer bilingue + LIA enforce, no Article 9 sensitive data |

Fixtures da creare in `test-fixtures/` (Fase D):

- `leads_sample_hot.csv` — 10 lead grade A in formato `/lead-finder-pro` (17 colonne)
- `leads_sample_warm.csv` — 15 lead grade B
- `leads_invalid_schema.csv` — schema diverso (per test 3)
- `mailbox_not_warmed.json` — fake mailbox config per test 6

## 13. Build order Fase C (parallelizzabile)

Ordine esecuzione (early ones unlock later):

1. **References docs** (parallel-buildable, zero dipendenze interne):
   - `outbound-best-practices-2026.md`
   - `deliverability-2026.md`
   - `sequence-templates.md`
   - `prompt-patterns.md`
   - `gdpr-outbound-eu.md`
   - `api-recipes.md`
2. **Skills companion** (depend su references, parallel-buildable tra loro):
   - `personalization-engine/SKILL.md`
   - `deliverability-check/SKILL.md`
   - `reply-classification/SKILL.md`
   - `sequence-builder/SKILL.md`
   - `gdpr-opt-out/SKILL.md`
3. **Scripts** (parallel-buildable):
   - `validate_input.py`, `personalize_first_line.py`, `deliverability_precheck.py`
   - `smartlead_upload.py`, `heyreach_upload.py`, `reply_classify.py`
   - `mcp_detect.py` (adapt da `/lead-finder-pro`)
   - `requirements.txt`
4. **Subagent main file** `outbound-orchestrator.md` (depend su tutto sopra; assembla riferimenti)
5. **README.md** (depend su tutto, user-facing)

## 14. Verification Fase B done

- [x] ARCHITECTURE.md scritto e review-ready
- [x] Frontmatter agent definito (mcpServers + skills + memory)
- [x] 8 discovery questions con logica conseguente in `discovery/questions.md`
- [x] MCP detection table + 5 fallback documentati
- [x] 5 skills companion con contratto + target righe
- [x] 6 references docs con content map
- [x] Schema config.md completo (15+ field principali)
- [x] System prompt skeleton 9 sezioni con conta righe target (400 totali)
- [x] Methodology 6 fasi operative
- [x] Output schema sequence JSON portable + naming convention
- [x] 12 edge case → handler chiaro
- [x] 12 anti-pattern documentati (10 BUILD-BRIEF + 2 research)
- [x] 10 test plan mappati per Fase D
- [x] Build order Fase C ottimizzato (parallelizzabile)
- [x] DECISIONS.md update con 11 decisioni emergent (4 originali + 11 nuove = 15 totali)
