# BUILD-BRIEF — `/outbound-orchestrator`

> **Per la worker chat**: leggi questo file all'inizio. Tutto il contesto necessario per buildare l'agent è qui. Non serve leggere conversazioni precedenti.
>
> **Quick start**: leggi BUILD-BRIEF → leggi PROGRESS.md (se esiste) → leggi DECISIONS.md (se esiste) → esegui Fase A → B → C → D → E.
> Aggiorna PROGRESS.md ad ogni milestone (almeno ogni 25% context fill).

## Identità del subagent

- **Nome**: `/outbound-orchestrator`
- **Cosa fa (1 frase)**: Da output `/lead-finder-pro` (CSV/JSON enriched + scored, filtro grade A+B) a sequenza outbound multi-channel personalizzata via AI first-line, caricata su SmartLead/HeyReach via API, con reply detection + auto-pause.
- **Per chi**: SDR, BDR, Founder che fanno outreach manualmente o con SmartLead/HeyReach (audience non-developer Learnn)
- **Use case slide W2**: "Gestione campagne marketing" (#4 dei 8 use case)
- **Skill v1 base da riusare come spunto**: `<pack-root>/skills/webinar-2/outbound-campaign/SKILL.md` (leggila per pattern, MA vai molto più in profondità — qui devi essere ACTION-driven, non solo template)
- **Tier**: 🥇 (chain con #1 lead-finder-pro)
- **Tempo stimato**: 1 giorno research + 6-8 ore build = ~10-12 ore totali

## Vincoli di livello "spaventoso"

Filippo ha esplicitamente chiesto agent **"fatti veramente bene, profondi, perfetti, che fanno dire wow"**. Vincoli minimi:

- System prompt **300-500 righe** (non 50)
- **5 skills companion** in `skills/`
- **5-6 references docs** (best practice, deliverability, sequence patterns, GDPR, prompt patterns, API recipes)
- **Discovery interattiva** al first run (8 domande mirate)
- **MCP detection automatica** + fallback grazioso (CSV export se SmartLead/HeyReach API down)
- **Memory persistente** via `memory: project`
- **Almeno 3 esempi reali** documentati nel README utente
- **Italiano** per messaggi utente, **inglese** per nomi tecnici
- **Safety contract stringente**: questo agent ESEGUE invii reali via API → rischio reale di spammare 500 email per errore. Confirm step + dry-run obbligatori.

## Fase A — Deep Research (1 giorno)

### Research questions (rispondere TUTTE prima di passare a B)

1. **Best practice outbound 2026**: cadence, sequence length 3/5/7 step, multi-channel timing email+LinkedIn, send time optimization, A/B test design
2. **SmartLead API capabilities 2026**: create campaign, save sequence, lead import bulk, reply tracking, webhook events, lead categories, daily limits
3. **HeyReach API capabilities 2026**: LinkedIn campaign, sequence multi-step, conversation read, sender multi-account, single-brace placeholder syntax (vedi skill `heyreach-api` di Filippo per pattern già testati)
4. **Email deliverability 2026**: warmup days/volume, DKIM/DMARC/SPF/BIMI setup, daily cap by stage (new/warmed/aged mailbox), spam triggers, blacklist scan, BIMI requirements
5. **Personalization patterns 2026**: AI first-line con company context (signal extraction → hook), 8 signal-hook templates (job-change, funding, hiring, podcast guest, content posted, conference attended, tool-stack-detected, geo-event), A/B test variants subject + first-line, anti-LLM-detection (variability, no markers obvi)
6. **Reply detection + handling**: 5-class taxonomy (positive/negative/OOO/unsubscribe/bounce), auto-pause + forward, SmartLead lead categories integration, webhook handler patterns
7. **GDPR considerations outbound EU 2026**: LIA per cold email B2B, opt-out enforcement (one-click unsubscribe), suppression list cross-campaign, Italy Garante Privacy specifics, Article 9 exclusion, retention 12 mesi, soft-opt-in

### Fonti da consultare

**NotebookLM dedicato** (worker chat crea in Fase A — nessun ID pre-allocato):

- Comando: `notebooklm create "Outbound Orchestrator - Sequence & Deliverability 2026"`
- Sources da aggiungere (`notebooklm source add`):
  - https://www.smartlead.ai/help (SmartLead help center)
  - https://api.smartlead.ai/docs (SmartLead API reference)
  - https://documenter.getpostman.com/view/24067770/2sA3JT1QvX (HeyReach Public API postman)
  - https://www.lemlist.com/blog/cold-email-deliverability (deliverability deep dive)
  - https://www.lemlist.com/blog/cold-email-sequence (sequence patterns)
  - https://blog.smartlead.ai/cold-email-personalization-2026 (AI first-line)
  - https://www.amplemarket.com/blog/cold-email-reply-rates-benchmarks-2026 (reply rate benchmarks)
  - https://gdpr-info.eu/recitals/no-47/ (Recital 47 — riusa)
- Aspetta indicizzazione 3-5 min, poi `notebooklm ask` per le 7 research questions

**WebSearch query** (cross-check con fonti recenti):

- "cold email sequence cadence 2026 best practice"
- "SmartLead API tutorial 2026"
- "HeyReach LinkedIn campaign automation 2026"
- "email warmup DKIM DMARC 2026"
- "AI first-line personalization cold email 2026"
- "GDPR cold email B2B Italia 2026"

**WebFetch URL specifici**:

- SmartLead API quickstart
- HeyReach Public API docs (Postman)
- Lemlist deliverability guide
- Garante Privacy direct marketing guidance

**parallel-cli**:

- `parallel-cli research "cold email reply rate benchmarks B2B SaaS 2026"`
- `parallel-cli research "anti-LLM-detection cold email patterns 2026"`

### Output research

Salva in `research/research-summary.md`:

- 1 sezione per ogni research question (Q1-Q7)
- Ogni claim con citazione fonte
- Top 5 finding più rilevanti per l'agent
- Edge case scoperti (lista)
- Tool/API capabilities mappate (tabella SmartLead vs HeyReach vs Lemlist vs Instantly)
- 8 signal-hook templates pronti
- 4 sequence template structure (Direct Demo, Education-First, Pain Discovery, Multi-threading)

Salva sintesi finale anche in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/outbound-orchestrator_2026-MM-DD.md`

## Fase B — Architecture Design (2-3 ore)

### Discovery questionnaire (8 domande)

Definire 8 domande per il first-run discovery. Per ogni domanda: question (italiano), header (max 12 char), options (2-4 + "Other"), logica conseguente.

**Bozza coordinator** (raffina in Fase B):

| # | Header | Q (italiano) | Options | Conseguenza |
|---|--------|--------------|---------|-------------|
| 1 | Outbound | Tool outbound primary | SmartLead · HeyReach · Lemlist · Instantly · Manuale | Carica recipe API specifica |
| 2 | ToV | Brand voice | Direct/concise · Friendly/casual · Educational/expert · Bold/provocative | Adatta personalization-engine prompt |
| 3 | ICP | Top 3 segmenti (free text) | — | Salvato in config, usato per signal extraction |
| 4 | ValueProp | Value prop (1-2 frasi free text) | — | Input per first-line generation |
| 5 | SeqLen | Lunghezza sequenza | 3 step · 5 step · 7 step · Custom | Carica template structure |
| 6 | Channel | Multi-channel? | Solo email · Email+LinkedIn · Solo LinkedIn · Email→LinkedIn fallback | Coordinazione timing day 0/2/5 |
| 7 | ABTest | A/B test on/off | On (subject+first-line) · Off | Genera 2 variants se on |
| 8 | GDPR | GDPR mode | Auto-detect EU · Always on · Off | Suppression list policy + footer bilingue |

Salva in `discovery/questions.md`.

### MCP mapping (con fallback)

| MCP | Tipo | Required for | Fallback |
|-----|------|--------------|----------|
| `smartlead` | Recommended primary | Campaign create + lead import + reply track | CSV export "ready for SmartLead manual import" |
| `heyreach` | Recommended | LinkedIn campaign + sequence | CSV export con LinkedIn URL list |
| `attio-mcp` | Optional | Lead status sync (bidirectional con `/lead-finder-pro`) | Skip sync, log only |
| `google-personal` | Optional | Output report Google Sheet/Doc | Markdown locale |

### Skills companion (5 skill)

1. **`personalization-engine/`** (~220 righe)
   - **Cosa fa**: AI first-line generation da signal extraction
   - **Input**: lead enriched (incluso `intent_signals` JSON) + brand voice + value prop
   - **Output**: `{first_line: str, signal_used: str, confidence: float}`
   - **References**: `prompt-patterns.md` (8 hook templates), `tool-integrations.md`
   - **Activation**: per ogni lead in sequence build

2. **`deliverability-check/`** (~180 righe)
   - **Cosa fa**: pre-flight check DKIM/DMARC/SPF + warmup status + daily cap remaining + blacklist scan + spam-trigger word
   - **Input**: sender mailbox + lead list size + scheduled send time
   - **Output**: `{ready: bool, issues: [], warnings: [], daily_cap_remaining: int}`
   - **References**: `deliverability-2026.md`
   - **Activation**: gate prima di ogni invio bulk

3. **`reply-classification/`** (~200 righe)
   - **Cosa fa**: 5-class auto-classify (positive/negative/OOO/unsubscribe/bounce), action per class, integrazione webhook SmartLead
   - **Input**: reply content + lead context
   - **Output**: `{class: str, confidence: float, action: pause|forward|unsubscribe|delete}`
   - **References**: `reply-handling-patterns.md`
   - **Activation**: webhook handler + manual triage on demand

4. **`sequence-builder/`** (~250 righe)
   - **Cosa fa**: genera sequenza 3/5/7 step multi-channel JSON da template + value prop + signal
   - **Input**: lead segment + sequence template + value prop + brand voice
   - **Output**: JSON sequence pronto per upload SmartLead/HeyReach API
   - **References**: `sequence-templates.md` (4 template: Direct Demo, Education-First, Pain Discovery, Multi-threading)
   - **Activation**: core methodology Fase 3

5. **`gdpr-opt-out/`** (~190 righe)
   - **Cosa fa**: suppression list cross-campaign management, footer bilingue mandatory, LIA template, Italy Garante specifics, retention 12 mesi
   - **Input**: lead list + ICP geo + suppression list path
   - **Output**: `{compliant_leads: [], excluded: [{lead, reason}], footer_html: str}`
   - **References**: `gdpr-outbound-eu.md`
   - **Activation**: auto se EU detected, manual per audit

### Schema config (`<memory>/config.md`)

```yaml
---
agent: outbound-orchestrator
created: 2026-MM-DD
last_updated: 2026-MM-DD
schema_version: 1
---

stack:
  outbound_primary: smartlead  # smartlead | heyreach | lemlist | instantly | manual
  outbound_secondary: heyreach  # se multi-channel
  attio_sync: true

brand:
  voice: direct  # direct | friendly | educational | bold
  value_prop: "..."
  signature: "Filippo Greco — Yellow Tech"

icp:
  segments: ["...", "...", "..."]
  geo_eu_detected: true

sequence:
  default_length: 5  # 3 | 5 | 7 | custom
  multi_channel: email_plus_linkedin
  ab_test_enabled: true

safety:
  dry_run_default: true     # primo run sempre dry, esegui solo dopo confirm
  confirm_required_above: 50  # soglia lead per confirm step esplicito
  daily_cap_per_mailbox: 50  # warmed mailbox baseline conservativa
  warmup_days_minimum: 14    # blocco bulk se mailbox <14 giorni warmup

gdpr:
  mode_active: true
  suppression_list_path: <memory>/suppression.csv
  footer_bilingue: true  # IT + EN se EU detected

mcp_available: { smartlead: true, heyreach: false, attio-mcp: true, google-personal: true }
mcp_fallbacks_active: { heyreach: csv_export }

api_keys:
  # NO storage in config — solo flag presenza
  smartlead_present: true   # env SMARTLEAD_API_KEY rilevato
  heyreach_present: false
```

### References docs (6 file da scrivere in `references/`)

| File | Content |
|------|---------|
| `outbound-best-practices-2026.md` | 7 best practice + cadence + multi-channel timing |
| `deliverability-2026.md` | DKIM/DMARC/SPF, warmup, daily cap by stage, spam triggers, BIMI |
| `sequence-templates.md` | 4 template (Direct Demo, Education-First, Pain Discovery, Multi-threading) con JSON example |
| `prompt-patterns.md` | 8 signal-hook templates per first-line, A/B variants, anti-LLM-detection |
| `gdpr-outbound-eu.md` | LIA cold email B2B, suppression cross-campaign, Italy Garante, retention 12 mesi |
| `api-recipes.md` | SmartLead create_campaign + save_sequence + add_leads + HeyReach equivalents, code esempi |

### Output Fase B

Salva tutto in `ARCHITECTURE.md` nella cartella dell'agent.

## Fase C — Build (4-6 ore)

### Subagent file principale

`outbound-orchestrator.md` con:

```yaml
---
name: outbound-orchestrator
description: <descrizione + when_to_use, max 1024 char>
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, AskUserQuestion
mcpServers: [smartlead, heyreach, attio-mcp, google-personal]
skills: [personalization-engine, deliverability-check, reply-classification, sequence-builder, gdpr-opt-out]
memory: project
model: sonnet
color: blue
---

[SYSTEM PROMPT 350-450 righe]:
- Identità + ruolo
- Discovery flow (8 AskUserQuestion)
- MCP detection logic
- Methodology (6 fasi: Ingest lead from /lead-finder-pro → Validate input → Personalize → Pre-flight check → Confirm + Dry-run → Execute upload → Monitor reply)
- Safety contract (dry-run default, confirm >50 lead, no role-based, no domain non-warmed)
- Tool usage rules
- Output format atteso (sequence JSON + report)
- Edge cases handling (10+)
- Examples input → output (3 reali)
- Anti-patterns (8+)
```

### Skills companion

In `skills/<skill-name>/SKILL.md` per le 5 skill (vedi Fase B).

### Scripts (in `scripts/`)

- `validate_input.py` — valida che input CSV sia output `/lead-finder-pro` (schema 17 colonne)
- `personalize_first_line.py` — wrapper LLM call per first-line gen
- `deliverability_precheck.py` — DKIM/DMARC/SPF + cap remaining
- `smartlead_upload.py` — campaign create + save sequence + add leads via API
- `heyreach_upload.py` — LinkedIn campaign equivalente
- `reply_classify.py` — 5-class classifier (LLM-based + rule-based fallback)
- `requirements.txt`

### README utente-facing

In root agent dir, `README.md` con:

- Cosa fa (1 paragrafo)
- Installazione (step-by-step, env var setup SmartLead/HeyReach API key)
- Esempi d'uso (3-5 reali — chain dopo `/lead-finder-pro`)
- FAQ (8+: cost stimato, GDPR, daily limit, A/B test, reply handling, ecc.)
- Troubleshooting (5+: API down, deliverability fail, GDPR EU mode, ecc.)
- Anti-pattern (cosa NON fa l'agent)

## Fase D — Test (1-2 ore)

### Test checklist (10 test)

1. **Discovery flow**: invoca da progetto pulito → 8 AskUserQuestion + salvataggio config
2. **Re-run**: invoca di nuovo → skip discovery, carica config
3. **Input validation**: passa CSV non-`/lead-finder-pro` schema → reject con messaggio chiaro
4. **Input chain**: passa output reale `/lead-finder-pro` (fixture `output/leads_sample_hot.csv`) → procede
5. **Personalization**: genera 5 first-line per 5 lead diversi → verifica diversità + signal usage
6. **Deliverability check**: simula mailbox non-warmed → block + warning chiaro
7. **Confirm step**: try execute con 100 lead → confirm step richiesto, no execute prima di "yes"
8. **Dry-run**: dry-run mode → output JSON sequence senza chiamata API reale
9. **MCP fallback**: SmartLead MCP missing → CSV export "ready for manual import"
10. **GDPR EU**: lead EU detected → suppression check + footer bilingue, LIA enforcement

### Test fixtures da creare

In `test-fixtures/`:

- `leads_sample_hot.csv` — 10 lead grade A in formato output `/lead-finder-pro` (17 colonne)
- `leads_sample_warm.csv` — 15 lead grade B
- `leads_invalid_schema.csv` — schema diverso (per test 3)
- `mailbox_not_warmed.json` — fake mailbox config per test 6

### Salva test results

In `TEST-RESULTS.md`: cosa funziona, cosa rompe, fix applicati, runtime test pending Filippo.

## Fase E — Documentation + Bundle (1 ora)

1. Aggiorna `MASTER-PROGRESS.md` (cambia stato `/outbound-orchestrator` a ✅ Done)
2. Aggiungi sezione in `dist/CLAUDE_WEEK_SKILL_PACK.md`
3. Crea nota Obsidian `~/Dev/obsidian-vault/02 - Ricerca/outbound-orchestrator_2026-MM-DD.md`
4. Annuncio al coordinator chat (Filippo)

## Definition of Done

- [ ] Tutte le 5 fasi completate
- [ ] PROGRESS.md aggiornato a "Done"
- [ ] MASTER-PROGRESS.md aggiornato (✅)
- [ ] Test checklist 10/10 statici PASS, runtime pending Filippo
- [ ] README utente-facing comprensibile da non-tech
- [ ] System prompt > 350 righe
- [ ] 5 skills companion + 6 references docs + 6 scripts
- [ ] Almeno 3 esempi reali documentati
- [ ] Chain con `/lead-finder-pro` testata via `validate_input.py`

## Anti-pattern critici (da includere nel system prompt)

1. **Mai bulk send su domain non-warmup** (>14 giorni warmup minimum)
2. **Mai inviare a role-based** (`info@`, `sales@`, `support@`, `noreply@`)
3. **Mai skip suppression/opt-out lista** (cross-campaign)
4. **Mai overshoot daily limit account** (default 50/mailbox warmed, configurabile)
5. **Mai personalization stampata** da template senza company-specific signal (anti-LLM-detection)
6. **Mai eseguire batch >50 lead** senza confirm step + dry-run preview
7. **Mai bypassare GDPR mode** se geo EU detected
8. **Mai inviare email senza unsubscribe link** (CAN-SPAM + GDPR)
9. **Mai sovrascrivere campagna esistente** SmartLead/HeyReach senza confirm
10. **Mai conservare API key in config.md** (solo flag presenza, env vars per security)

## 5 Decisioni emergent flagged per worker chat (Architecture phase)

Worker chat raffini queste 5 decisioni in DECISIONS.md durante Fase B:

1. **Confirm step soglia**: default `confirm_required_above: 50`. Sotto = procede dopo dry-run preview. Sopra = explicit "yes confirm". Da validare se vuoi sempre confirm anche sotto 50.
2. **Multi-channel timing default**: email day 0 → LinkedIn day 2 (research-driven). Da confermare in DECISION emergent dopo Fase A research.
3. **API key handling**: env vars (`~/.zshrc`) primary, fallback prompt at first run, NO salvataggio config (security). Solo flag presenza.
4. **Daily cap default 50/mailbox warmed**: conservativo. Per warmed mailbox aged (>30 giorni) può salire 100-200. Da validare in Fase A research.
5. **NotebookLM creation**: lasciata a worker chat in Fase A (no ID pre-allocato).

## Chain con `/lead-finder-pro`

Input atteso: file CSV `output/leads_<YYYYMMDD>_<grade>.csv` da `/lead-finder-pro` (schema 17 colonne, vedi `<pack-root>/.claude/agents/lead-finder-pro/lead-finder-pro.md` sezione 6).

Validation via `scripts/validate_input.py`:

- Reject se mancano colonne required (`name`, `company`, `email`, `email_confidence`, `score`, `grade`)
- Filtro `grade in [A, B]` per default (Hot/Warm)
- Skip lead con `email_confidence < 0.80` (verification soglia)
- Skip lead con `gdpr_status: excluded`
- Skip lead con email role-based (regex check ridondante per safety)

## Context management (per worker chat)

### Update PROGRESS.md ad ogni 25% context

- ✅ Cosa è stato fatto (file path, decisioni)
- 🚧 Cosa sto facendo ora
- 📋 Prossimi step specifici
- 🐛 Edge case scoperti

### A 50% context fill

1. Update finale PROGRESS.md + DECISIONS.md
2. User chiama `/compact`
3. Re-prime: "Leggi PROGRESS.md e DECISIONS.md. Continua da dove eravamo."

### File da NON perdere mai (re-leggi sempre dopo compact)

- BUILD-BRIEF.md (questo file)
- PROGRESS.md
- DECISIONS.md
- ARCHITECTURE.md (se Fase B completata)
- research/research-summary.md (se Fase A completata)
