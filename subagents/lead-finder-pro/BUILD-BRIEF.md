# BUILD-BRIEF — `/lead-finder-pro`

> **Per la worker chat**: leggi questo file all'inizio. Tutto il contesto necessario per buildare l'agent è qui. Non serve leggere conversazioni precedenti.
>
> **Quick start**: leggi BUILD-BRIEF → leggi PROGRESS.md (se esiste) → leggi DECISIONS.md (se esiste) → esegui Fase A → B → C → D → E.
> Aggiorna PROGRESS.md ad ogni milestone (almeno ogni 25% context fill).

## Identità del subagent

- **Nome**: `/lead-finder-pro`
- **Cosa fa (1 frase)**: Da definizione ICP a lista lead arricchiti, segmentati e scorati, sincronizzati nel CRM e pronti per outbound.
- **Per chi**: SDR, BDR, Marketing manager, Founder, Freelancer GTM (audience non-developer Learnn)
- **Use case slide W2**: "Creare liste di possibili lead e segmentazione" (#7 dei 8 use case)
- **Skill v1 base da riusare come spunto**: `<pack-root>/skills/webinar-2/lead-enrichment/SKILL.md` (170 righe — leggila per capire pattern, MA vai molto più in profondità)
- **Tier**: 🥇 (validation pattern — primo del pack v2)
- **Tempo stimato**: 1-1.5 giorni research + 6-8 ore build = ~12 ore totali

## Vincoli di livello "spaventoso"

Filippo ha esplicitamente chiesto agent **"fatti veramente bene, profondi, perfetti, che fanno dire wow"**. Vincoli minimi:

- System prompt **300-500 righe** (non 50)
- **3-5 skills companion** in `skills/`
- **3-5 references docs** (best practice, tool integrations, GDPR, prompt patterns)
- **Discovery interattiva** al first run (6-8 domande mirate)
- **MCP detection automatica** + fallback grazioso se MCP non disponibili
- **Memory persistente** via `memory: project`
- **Almeno 3 esempi reali** documentati nel README utente
- **Italiano** per messaggi utente, **inglese** per nomi tecnici

## Fase A — Deep Research (1-1.5 giorni)

### Research questions (rispondere TUTTE prima di passare a B)

1. **Stato dell'arte 2026 lead enrichment B2B**: quali sono le 5-7 best practice consolidate? (waterfall enrichment, email verification, re-enrichment cycles, ICP hybrid scoring, etc.)
2. **Tool ecosystem mappato**: quali sono i top 10 tool del mercato (Apollo, Clay, ZoomInfo, Hunter, Cognism, Lusha, Lead411, Adapt, RocketReach, Snov.io)? API capabilities, pricing tier, MCP/integration disponibili?
3. **ICP scoring framework**: qual è il framework decisionale per scorare un lead (fit + intent + timing)? Hybrid model rules+ML come funziona? Esempi numerici (es. score 0-100 con pesi)?
4. **Email verification techniques**: come si fa SMTP check, MX check, catch-all detection, role-based detection? Tool top (NeverBounce, ZeroBounce, Bouncer, Kickbox)?
5. **GDPR compliance per lead enrichment EU**: lawful basis (legitimate interest vs contract), documentation requirements, opt-out handling, dati sensibili da NON scrapare?
6. **LinkedIn scraping anti-detection**: tecniche legittime (Sales Nav, LinkedIn API), tool wrapper (Apify, PhantomBuster), rate limit safe, evitare ban account?
7. **Esempi reali eccellenti**: 3-5 case study di lead gen ops che fanno questo bene (founder/SDR famosi, articoli dettagliati, video YouTube top)?

### Fonti da consultare

**NotebookLM dedicato**:
- Notebook ID: `3b40733b-3fc1-4c63-8dfd-e2566a06fe37` ("Lead Finder Pro - Deep Research 2026")
- Sources da aggiungere (usa `notebooklm source add`):
  - https://syncgtm.com/blog/b2b-lead-enrichment (best practice 2026)
  - https://breadcrumbs.io/blog/b2b-lead-scoring/ (scoring framework 2026)
  - https://www.amplemarket.com/blog/best-ai-lead-generation-tools (tool review)
  - https://intentdepth.com/blog/b2b-lead-qualification-framework-icp (ICP framework)
  - https://www.amplemarket.com/blog/best-b2b-data-enrichment-tools (waterfall vs real-time)
  - https://docs.apollo.io/ (Apollo API docs)
  - https://www.clay.com/blog (Clay use case)
  - GDPR docs lawful basis: https://gdpr-info.eu/recitals/no-47/
- Aspetta indicizzazione 3-5 min, poi `notebooklm ask` per ognuna delle 7 research questions

**WebSearch query** (cross-check con fonti recenti):
- "B2B lead enrichment waterfall pattern 2026"
- "Apollo API lead search best practices 2026"
- "Clay enrichment workflows GTM 2026"
- "ICP scoring hybrid model B2B SaaS 2026"
- "GDPR legitimate interest lead generation EU 2026"
- "LinkedIn Sales Navigator scraping legal 2026"
- "Email verification waterfall NeverBounce ZeroBounce 2026"

**WebFetch URL specifici** (estrai dettagli tecnici):
- https://docs.apollo.io/reference/people-search (Apollo people search API)
- https://docs.apollo.io/reference/organization-search (Apollo company API)
- https://www.clay.com/learn (Clay learning hub)
- https://hunter.io/api-documentation (Hunter API)
- https://docs.attio.com/rest-api (Attio MCP context)

**parallel-cli** per ricerca approfondita:
- `parallel-cli research "B2B lead enrichment best practices 2026 waterfall"`
- `parallel-cli research "ICP scoring framework B2B SaaS 2026"`
- `parallel-cli search "site:reddit.com/r/sales lead enrichment Apollo Clay"`

### Output research

Salva in `research/research-summary.md` (questa cartella):
- 1 sezione per ogni research question (1-7)
- Ogni claim con citazione fonte (URL)
- Top 5 finding più rilevanti
- Edge case scoperti (lista)
- Tool/API capabilities mappate (tabella)

Salva sintesi finale anche in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/lead-finder-pro_2026-04-29.md` con frontmatter standard (vedi `~/Dev/obsidian-vault/CLAUDE.md` per regole vault).

## Fase B — Architecture Design (2-3 ore)

### Discovery questionnaire (proposta — affina basato su research)

Salva la versione finale in `discovery/questions.md`. Questa è la proposta iniziale:

| # | Question | Header | Options |
|---|----------|--------|---------|
| 1 | Qual è il tuo ruolo? | Ruolo | SDR · BDR · Marketing manager · Founder · Freelancer · Other |
| 2 | Quale tool di lead enrichment hai? | Enrichment | Apollo · Clay · Hunter · ZoomInfo · Cognism · Nessuno · Other |
| 3 | Quale CRM usi? | CRM | HubSpot · Pipedrive · Attio · Salesforce · Custom · Nessuno |
| 4 | Tool outbound? | Outbound | SmartLead · Lemlist · HeyReach · Instantly · Manuale |
| 5 | Qual è il tuo ICP? (settore + dimensione + geo) | ICP | (free text) |
| 6 | Top 3 segmenti prioritari | Segmenti | (free text 3 lines) |
| 7 | Volume target lead/mese | Volume | <50 · 50-200 · 200-500 · 500+ |
| 8 | Ti interessa anche scoring intent (hiring, funding, news)? | Intent | Sì alta · Sì media · No basta firmographic |

Logica conseguente:
- Se Q2 = "Apollo" → carica `references/apollo-api-recipes.md`
- Se Q3 = "Attio" → usa `attio-mcp` se disponibile
- Se Q5 contains "EU" → carica `references/gdpr-compliance.md` come prioritario
- Se Q7 = "500+" → suggerisci Agent Teams parallelizzazione

### MCP mapping

| MCP | Tipo | Fallback se mancante |
|-----|------|----------------------|
| `attio-mcp` | Recommended (se utente usa Attio) | Skip CRM sync, output solo CSV |
| `mcp__explorium__*` | Optional | parallel-cli enrich |
| `mcp__smartlead__*` | Optional (per chain con outbound) | Skip campaign upload, esporta CSV |
| `mcp__heyreach__*` | Optional (LinkedIn outbound) | Idem |
| `mcp__google-personal__*` (Sheet) | Recommended | Output CSV locale |
| `mcp__playwright__browser_*` | Required (scraping) | Bash + curl + html parsing |

Pattern di detection (pseudo):
```
verify_mcp("attio-mcp") -> if missing, log warning, set skip_crm_sync=true
verify_mcp("explorium") -> if missing, fall back to parallel-cli
...
```

### Skills companion (da buildare in `skills/`)

1. **`icp-scoring/`** — Framework hybrid (rules + behavior signals) per scorare lead 0-100 con buckets Hot/Warm/Cold. Include 3 template ICP per industry (SaaS B2B, Agency, eCommerce).
2. **`email-verification/`** — Waterfall verification: SMTP → MX → catch-all → role detection. Threshold confidence + costo per lead.
3. **`gdpr-compliance/`** — Checklist lawful basis EU lead, opt-out handling, data minimization, source documentation.
4. **`waterfall-enrichment/`** — Pattern multi-vendor: prima Apollo, fallback Clay, fallback Hunter. Coverage threshold 85%.
5. **`linkedin-safe-scraping/`** — Sales Nav patterns sicuri, rate limit (max 100/giorno organic, max 1000/giorno con account dedicato).

### Config schema (`<memory>/config.md`)

```yaml
---
agent: lead-finder-pro
created: 2026-04-29
last_updated: 2026-04-29
---

user:
  role: founder

stack:
  enrichment_tools: [Apollo, Clay]
  crm: Attio
  outbound: SmartLead

icp:
  description: "SaaS B2B, 10-50 employees, USA + EU"
  segments:
    - "FinTech early-stage USA"
    - "MarTech Europe"
    - "AI tools mid-stage"

preferences:
  monthly_volume: "200-500"
  intent_signals: high

mcp_available:
  attio-mcp: true
  explorium: false
  smartlead: true
  heyreach: false
  google-personal: true
  playwright: true

mcp_fallbacks_active:
  explorium: parallel-cli
```

### References docs (da scrivere in `references/`)

Lista minima:
1. `lead-enrichment-best-practices-2026.md` (output Fase A)
2. `tool-integrations.md` (Apollo, Clay, Hunter, ZoomInfo API specifics)
3. `gdpr-compliance.md` (checklist EU, lawful basis)
4. `icp-scoring-framework.md` (hybrid model + 3 template per industry)
5. `prompt-patterns.md` (esempi prompt eccellenti per il modello)
6. `apollo-api-recipes.md` (pattern call efficaci)

### Output Fase B

Salva tutto in `ARCHITECTURE.md` nella cartella dell'agent.

## Fase C — Build (4-6 ore)

### Subagent file principale

`<pack-root>/.claude/agents/lead-finder-pro/lead-finder-pro.md`

Frontmatter (esempio iniziale — adatta in base a research):

```yaml
---
name: lead-finder-pro
description: Da definizione ICP a lista lead arricchiti scorati e segmentati, pronti per outbound. Multi-vendor waterfall enrichment + LinkedIn safe + email verification + GDPR-aware. Per SDR/BDR/Founder/Marketer GTM. Self-configuring al first run con discovery interattiva.
when_to_use: Lista lead grezza da arricchire, nuova lista post-evento, export CRM con campi vuoti, preparation campagna outbound, ricerca prospect ICP
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, AskUserQuestion
mcpServers:
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

[SYSTEM PROMPT 300-500 righe — vedi struttura sotto]
```

### Struttura system prompt (sezioni minime)

1. **Identità + ruolo** (~20 righe)
2. **Discovery flow al first run** (~50 righe) — logica per check `<memory>/config.md`, se mancante → AskUserQuestion sequence + salva config
3. **MCP detection logic** (~30 righe) — verifica disponibilità + fallback graceful
4. **Methodology principal** (~80 righe) — 6 fasi operative (ingest → enrich → score → segment → output → sync)
5. **Tool usage rules** (~40 righe) — quando usare Apollo vs Clay vs scraping, quando usare playwright vs parallel-cli
6. **Output format** (~30 righe) — schema CSV/Sheet, colonne required, formato JSON intermedio
7. **Edge cases handling** (~40 righe) — duplicati, dati parziali, rate limit, GDPR EU, blacklist domini
8. **Examples input → output** (~50 righe) — 2-3 esempi reali end-to-end
9. **Anti-patterns** (~20 righe) — cosa l'agent NON fa mai

### Skills companion

Per ogni skill in `skills/<skill-name>/SKILL.md`, formato standard. Vedi `skills/meta/skill-builder/SKILL.md` per pattern di scrittura skill.

### References

In `references/`, file markdown ben strutturati. **Output Fase A si converte in references** (best-practices viene da research-summary).

### Scripts

Almeno questi (in `scripts/`):
- `discovery_check.py` — verifica esistenza config, ritorna stato
- `mcp_detect.py` — check disponibilità MCP server
- `apollo_search.py` — wrapper Apollo people-search API
- `email_verify_waterfall.py` — verifica email multi-tier
- `csv_to_sheet.py` — output Google Sheet via google-personal MCP
- `attio_sync.py` — sync Hot leads in Attio CRM

### README utente-facing

`README.md` user-friendly:
- Cosa fa in 2 paragrafi
- Installazione (3 step max)
- Esempi (almeno 3 reali con prompt → output)
- FAQ
- Troubleshooting (5 problemi comuni)

## Fase D — Test (1-2 ore)

Test checklist:

1. **Discovery flow**: in progetto pulito, invoca `/lead-finder-pro` → verifica 6-8 domande, salvataggio config in `<memory>/config.md`
2. **Re-run**: invoca di nuovo → verifica skip discovery, conferma "Config trovata, sono pronto"
3. **Real task small**: dai lista test 20 lead (CSV con 20 nomi+azienda) → verifica output Sheet con email/role/score
4. **MCP fallback**: simula `attio-mcp` non disponibile (rinomina o disabilita) → verifica messaggio "Attio non disponibile, output solo CSV"
5. **Reconfigure**: prompt "reconfigure" o "voglio cambiare config" → verifica reset e nuova discovery
6. **Edge case**: dai lista con 5 duplicati + 2 dati parziali → verifica dedup + skip with warning
7. **GDPR**: dai lista con 3 lead EU → verifica check lawful basis + warning

Salva risultati in `TEST-RESULTS.md`.

## Fase E — Documentation + Bundle (1 ora)

1. Aggiorna `MASTER-PROGRESS.md` (path `<pack-root>/.claude/agents/MASTER-PROGRESS.md`): cambia stato `/lead-finder-pro` da 🟡 a ✅
2. Aggiungi sezione in `dist/CLAUDE_WEEK_SKILL_PACK.md` con descrizione + install + esempi
3. (Opzionale) Screencast 3-5 min — solo se hai tempo
4. Notifica al coordinator chat (ping Filippo): "lead-finder-pro DONE, ready per test"

## Definition of Done

- [ ] Tutte le 5 fasi completate
- [ ] PROGRESS.md aggiornato a "Done"
- [ ] MASTER-PROGRESS.md aggiornato (✅)
- [ ] Test checklist 7/7 pass
- [ ] README utente comprensibile da non-tech (test mentale: lo darei a un freelancer marketer?)
- [ ] System prompt > 300 righe e sostanzioso
- [ ] 5 skills companion + 6 references docs
- [ ] 3+ esempi reali documentati
- [ ] research-summary.md > 2000 parole con citazioni

## Context management (per worker chat)

### Update PROGRESS.md (ogni 25% context, MINIMO ogni fase)

Template entry:
```markdown
## YYYY-MM-DD HH:MM — Milestone X

### ✅ Cosa è stato fatto
- Fase X completata
- File creati: <lista path>
- Decisioni prese: <link a DECISIONS.md riga N>

### 🚧 Cosa sto facendo ora
- <step corrente>

### 📋 Prossimi step
1. ...
2. ...

### 🐛 Edge case scoperti
- <problema>: <fix proposto>

### 🔗 File esterni rilevanti
- <path file letto/scritto>
```

### A 50% context fill

1. Update finale PROGRESS.md + DECISIONS.md
2. User chiama `/compact` (o tu lo suggerisci)
3. Re-prime: "Leggi BUILD-BRIEF.md, PROGRESS.md, DECISIONS.md. Continua da dove eravamo."

### File da NON perdere mai (re-leggi sempre dopo compact)

- BUILD-BRIEF.md (questo file)
- PROGRESS.md
- DECISIONS.md (decisioni immutabili)
- ARCHITECTURE.md (se Fase B completata)
- research/research-summary.md (se Fase A completata)

### Update MASTER-PROGRESS.md
Aggiorna anche `<pack-root>/.claude/agents/MASTER-PROGRESS.md` quando:
- Inizi build (cambia stato a 🟡 In progress)
- Completi una fase (aggiungi entry log)
- Termini (✅ Done)

## Riferimenti incrociati

- **Skill v1 base (spunto, non overwrite)**: `<pack-root>/skills/webinar-2/lead-enrichment/SKILL.md`
- **Pattern subagent ufficiale**: https://code.claude.com/docs/en/sub-agents
- **Pattern skill ufficiale**: https://code.claude.com/docs/en/skills
- **Skill builder pattern**: `<pack-root>/skills/meta/skill-builder/SKILL.md`
- **NotebookLM dedicato**: `3b40733b-3fc1-4c63-8dfd-e2566a06fe37`
- **CLAUDE.md progetto**: `<pack-root>/CLAUDE.md`
- **Master plan**: `~/.claude/plans/analizza-attentamente-il-progetto-glowing-taco.md`
- **CLAUDE.md utente globale**: `~/.claude/CLAUDE.md` (regole engineering, persona, stack operativo)
