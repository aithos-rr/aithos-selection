# BUILD-BRIEF — `/competitor-deep-dive`

> **Per la worker chat**: leggi questo file all'inizio. Tutto il contesto necessario per buildare l'agent è qui. Non serve leggere conversazioni precedenti.
>
> **Quick start**: leggi BUILD-BRIEF → leggi PROGRESS.md (se esiste) → leggi DECISIONS.md (se esiste) → esegui Fase A → B → C → D → E.
> Aggiorna PROGRESS.md ad ogni milestone (almeno ogni 25% context fill).

## Identità del subagent

- **Nome**: `/competitor-deep-dive`
- **Cosa fa (1 frase)**: Da 1-5 nomi competitor produce un dossier strategico markdown deterministico (1 file per competitor + synthesis cross-competitor + 3 opportunità rankate), evidence-first, multi-source.
- **Per chi**: SDR, Marketing manager, Founder, PM, Analyst (audience non-developer Learnn — community business)
- **Use case slide W2**: "Analizzare i competitor in profondità" (uno degli 8 use case del W2 GTM)
- **Skill v1 base da riusare come spunto**: `<pack-root>/skills/webinar-2/trend-analysis/SKILL.md` (copre solo trend social, NON sostituirla — `/competitor-deep-dive` la estende a positioning + reviews + tech + funding)
- **Tier**: 🥇 (subagent #2 del Pack v2, dopo `/lead-finder-pro`)
- **Tempo stimato**: 1 giorno research + 6-8 ore build = ~12-14 ore totali

## Differenziazione rispetto a `/lead-finder-pro` (importante)

- `/lead-finder-pro` è **data-driven** → input ICP, output lista lead enriched
- `/competitor-deep-dive` è **output-driven** → input nomi competitor, output dossier sintetizzato

Il valore di `/competitor-deep-dive` non è "raccogliere dati", è **sintetizzare evidenza in raccomandazioni actionable**. Sentiment/positioning/ToV NON devono mai essere allucinati: ogni claim ha una citazione (review_id + quote, source URL).

## Vincoli di livello "spaventoso"

Filippo ha esplicitamente chiesto agent **"fatti veramente bene, profondi, perfetti, che fanno dire wow"**. Vincoli minimi:

- System prompt **300-500 righe** (non 50)
- **5 skills companion** in `skills/` (positioning-mapper, tov-analyzer, reviews-sentiment, gap-finder, dossier-writer)
- **5+ references docs** (best practice framework, ToV rubric NN, tool ecosystem, GDPR scraping, dossier anatomy)
- **Discovery interattiva** al first run (8 domande mirate)
- **MCP detection automatica** + fallback grazioso se MCP non disponibili
- **Memory persistente** via `memory: project` (competitor analizzati restano nel progetto utente)
- **Almeno 3 esempi reali** documentati nel README utente
- **Italiano** per messaggi utente, **inglese** per nomi tecnici

## Fase A — Deep Research (1 giorno)

### Research questions (rispondere TUTTE prima di passare a B)

1. **Stato dell'arte 2026 framework competitor analysis B2B**: quali sono i 7 framework consolidati (SWOT, Porter 5 Forces, JTBD, Strategy Canvas, Positioning Map 2x2, Competitive Profile Matrix, Feature Matrix)? When-to-use ognuno (per ruolo: Founder vs Marketing vs PM vs Sales)?
2. **Tone of Voice — extraction deterministica**: Nielsen Norman 4-dim (Funny↔Serious, Formal↔Casual, Respectful↔Irreverent, Enthusiastic↔Matter-of-fact) come si misura programmaticamente? Quali metriche derivate (jargon density, pronoun ratio I/we vs you, sentence avg length, CTA style imperativo vs invitante)? Esempio rubric scorabile 1-5 per ogni dim?
3. **Tool ecosystem 2026**: capabilities + pricing + access mode (UI/API/MCP/scraping) per: SimilarWeb, SemRush, Ahrefs, BuiltWith, Crunchbase, G2, Trustpilot, Capterra, LinkedIn Sales Navigator, Apify (actors specifici), parallel-cli (search/extract/research/enrich)?
4. **Reviews scraping + sentiment grounded 2026**: quali Apify actors maintained per G2/Trustpilot/Capterra? Anti-hallucination pattern: come strutturare prompt sentiment per garantire citazione review_id + quote per ogni claim? Esempio output schema?
5. **Gap analysis methodology**: come costruire matrice 6-dim (feature/segment/geo/ToV/format/pricing) partendo da N competitor + cliente baseline? Overlay Love-Hate-Want vs JTBD? Ranking gap per (impact × ease × evidence_strength)?
6. **GDPR / legal scraping public web 2026**: cosa è lecito scrapare (homepage, about, product page, public reviews G2/Trustpilot)? Cosa NO (LinkedIn senza Sales Nav account, dati behind login)? Rate-limit safe defaults per ogni source? Documentation pattern per cliente EU (LIA + source list)?
7. **Anatomia di un dossier "wow"**: analisi 3-5 dossier reali eccellenti (es. da agency competitive intelligence, founder Twitter threads, Substack analyst). Structure ricorrenti (TL;DR, evidence, 3 raccomandazioni). Signal/noise (max parole utili). Actionability (cosa il reader deve fare nei prossimi 7 giorni)?

### Fonti da consultare

**NotebookLM dedicato**:

- Notebook ID: `competitor-deep-dive-2026` (creare con `notebooklm create` se non esiste; titolo "Competitor Deep Dive - Research 2026")
- Sources da aggiungere (usa `notebooklm source add`):
  1. https://www.madx.digital/learn/saas-competitor-analysis
  2. https://genesysgrowth.com/blog/product-positioning-frameworks-complete-guide
  3. https://prospeo.io/s/saas-competitor-analysis
  4. https://www.reviewflowz.com/blog/b2b-saas-competitive-analysis
  5. https://www.octoparse.com/blog/competitor-analysis-tools
  6. https://trafficthinktank.com/semrush-vs-similarweb/
  7. https://www.redbricklabs.io/blog/best-competitive-intelligence-tools
  8. https://www.nngroup.com/articles/tone-of-voice-dimensions/
- Aspetta indicizzazione 3-5 min, poi `notebooklm ask` per ognuna delle 7 research questions

**WebSearch query** (cross-check con fonti recenti):

- "B2B competitor analysis framework 2026"
- "Tone of voice analysis Nielsen Norman SaaS 2026"
- "G2 reviews scraping sentiment analysis 2026"
- "Apify G2 Trustpilot Capterra actor 2026"
- "Competitive intelligence tools comparison 2026"
- "Strategy canvas Blue Ocean B2B SaaS examples 2026"
- "GDPR public web scraping legal EU 2026"

**WebFetch URL specifici** (estrai dettagli tecnici):

- https://docs.apify.com/platform/actors (Apify actor model)
- https://www.builtwith.com/api (BuiltWith tech stack API)
- https://docs.crunchbase.com/reference (Crunchbase REST API)
- https://www.nngroup.com/articles/tone-of-voice-dimensions/ (ToV rubric source)

**parallel-cli** per ricerca approfondita:

- `parallel-cli research "B2B competitor positioning framework 2026"`
- `parallel-cli research "tone of voice analysis automated SaaS 2026"`
- `parallel-cli search "site:reddit.com/r/SaaS competitor analysis tools"`
- `parallel-cli search "site:news.ycombinator.com competitive intelligence"`

### Output research

Salva in `research/research-summary.md` (questa cartella):

- 1 sezione per ogni research question (1-7)
- Ogni claim con citazione fonte (URL + quote)
- Top 5 finding più rilevanti per il subagent
- Edge case scoperti (lista — es. competitor stealth mode, no public reviews, ToV non extractable da homepage minimalista)
- Tool/API capabilities mappate (tabella comparativa con pricing 2026)
- Anti-pattern identificati (es. dossier monolite >5000 parole = signal/noise pessimo)

Salva sintesi finale anche in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/competitor-deep-dive_2026-04-30.md` con frontmatter standard (vedi `~/Dev/obsidian-vault/CLAUDE.md`).

## Fase B — Architecture Design (2-3 ore)

### Discovery questionnaire (proposta — affina basato su research)

Salva la versione finale in `discovery/questions.md`. Questa è la proposta iniziale:

| # | Question | Header | Options |
|---|----------|--------|---------|
| 1 | Qual è il tuo ruolo? | Ruolo | Marketing · Founder · PM · Sales · Analyst · Other |
| 2 | In quale settore opera il tuo business? | Settore | (free text) |
| 3 | Quali competitor analizzare? (1-5 nomi + domain) | Competitor | (free text — list of "Name @ domain.com") |
| 4 | Profondità analisi desiderata? | Profondita | Quick scan (2h) · Standard dossier (1 day) · Deep strategic (3 day) |
| 5 | Output format preferito? | Output | Markdown locale · Google Doc · Notion · Slack summary |
| 6 | Cliente baseline da confrontare (tagline + value-prop + ICP) | Baseline | (free text 3 lines) |
| 7 | Geo target prioritario? | Geo | USA · EU · Italia · EMEA · Worldwide |
| 8 | Reviews focus? | Reviews | G2 · Trustpilot · Capterra · All |

Logica conseguente:

- Se Q4 = "Quick scan" → skip ToV deep + reviews scraping, solo positioning + 1 gap
- Se Q4 = "Deep strategic" → aggiungi tech stack BuiltWith + funding Crunchbase + LinkedIn signals
- Se Q5 = "Google Doc" → usa `google-personal` MCP per output
- Se Q5 = "Slack summary" → usa `slack` MCP per post in canale
- Se Q7 in {EU, Italia, EMEA} → carica `references/gdpr-scraping-compliance.md` + warning EU mode
- Se Q8 = "All" → triple scrape (G2 + Trustpilot + Capterra) — flag costo Apify più alto

### MCP mapping

| MCP | Tipo | Uso | Fallback se mancante |
|-----|------|-----|----------------------|
| `apify` | Required (primary) | Scraping G2/Trustpilot/Capterra reviews, BuiltWith tech, Crunchbase funding | parallel-cli search + WebFetch (degraded — no structured reviews) |
| `playwright` | Required | Scraping homepage/about/product per positioning + ToV corpus | Bash + curl + html parsing (degraded, no JS rendering) |
| `parallel-cli` | Recommended | Research mode per long-tail signals (Reddit, HN, blog mentions) | WebSearch (meno preciso) |
| `google-personal` | Recommended | Output Google Doc/Sheet quando richiesto | Markdown locale |
| `slack` | Optional | Post summary in canale team | Stdout markdown |
| `attio-mcp` | Optional | Salva competitor come record CRM "Account" tipo Competitor | Skip CRM linkage |

Pattern di detection (pseudo):

```
verify_mcp("apify") -> if missing, warn "Reviews scraping degradato, output limited"
verify_mcp("playwright") -> if missing, fallback curl + parse, log "ToV analysis qualità ridotta"
verify_mcp("parallel-cli") -> if missing, fallback WebSearch
verify_mcp("google-personal") -> if missing, output markdown locale
verify_mcp("slack") -> if missing, skip Slack post
```

### Skills companion (da buildare in `skills/`)

**5 skill confermate (NON ridurre)**:

1. **`positioning-mapper/`**
   - **Input**: competitor name + domain
   - **Output**: `positioning.json` (tagline, value-prop, ICP, segments, 3 differentiators, source quotes con URL)
   - **Quando l'agent la richiama**: per ogni competitor, prima fase di analisi

2. **`tov-analyzer/`**
   - **Input**: corpus testuale (homepage + 5 blog/LinkedIn post recenti)
   - **Output**: `tov.json` con 4-dim Nielsen Norman scores 1-5 + metriche derivate (jargon density %, pronoun ratio I-we/you, sentence avg length, CTA style imperativo/invitante) + 3 evidence quotes per dim
   - **Quando l'agent la richiama**: dopo positioning, su corpus raccolto via Playwright

3. **`reviews-sentiment/`**
   - **Input**: competitor name + G2/Trustpilot/Capterra URL
   - **Output**: `reviews.json` con sentiment breakdown evidence-backed (top 5 strengths/weaknesses/use cases/JTBD descritti dai customer)
   - **Anti-hallucination MANDATORY**: review_id + quote per ogni claim. Se Apify fallisce → output "no reviews available" (no fake)
   - **Quando l'agent la richiama**: in parallel a ToV (entrambe servono al gap-finder)

4. **`gap-finder/`**
   - **Input**: tutti i positioning/tov/reviews JSON + cliente baseline
   - **Output**: `gap-matrix.json` (6-dim: feature/segment/geo/ToV/format/pricing) + `gap-narrative.md` con 5-10 gap rankati per (impact × ease × evidence_strength)
   - **Quando l'agent la richiama**: dopo TUTTI i competitor analizzati + cliente baseline acquisito

5. **`dossier-writer/`**
   - **Input**: tutti gli artefatti (positioning, tov, reviews, gap)
   - **Output**: deterministic markdown report:
     - `dossier_<competitor>.md` × N (1 per competitor, max 1500 parole ognuno)
     - `synthesis.md` (cross-competitor patterns, max 1000 parole)
     - `opportunities.md` (top 3 raccomandazioni rankate per impact/ease, max 800 parole)
   - **Anti-pattern enforced**: NO claim senza citazione, NO dossier monolite >5000 parole, ogni numero ha source URL
   - **Quando l'agent la richiama**: ultimo step, dopo gap-finder

### Config schema (`<memory>/config.md`)

```yaml
---
agent: competitor-deep-dive
created: 2026-MM-DD
last_updated: 2026-MM-DD
---

user:
  role: marketing  # marketing | founder | pm | sales | analyst

business:
  industry: "SaaS B2B - workflow automation"
  baseline:
    tagline: "Automate workflows without code"
    value_prop: "10x faster than Zapier for technical teams"
    icp: "Mid-market SaaS, 50-500 employees, technical PMs"
  geo_target: EU  # USA | EU | Italia | EMEA | Worldwide

analysis:
  depth: standard  # quick | standard | deep
  output_format: google_doc  # markdown | google_doc | notion | slack
  reviews_focus: [G2, Trustpilot]  # subset di [G2, Trustpilot, Capterra, All]

competitors_analyzed:
  - name: "Make"
    domain: "make.com"
    analyzed_at: 2026-MM-DD
    dossier_path: "research/dossier_make.md"
  - name: "n8n"
    domain: "n8n.io"
    analyzed_at: 2026-MM-DD
    dossier_path: "research/dossier_n8n.md"

mcp_available:
  apify: true
  playwright: true
  parallel-cli: true
  google-personal: true
  slack: false
  attio-mcp: true

mcp_fallbacks_active:
  slack: stdout
```

### References docs (da scrivere in `references/`)

Lista minima:

1. `competitor-analysis-frameworks-2026.md` (output Fase A — 7 framework + when-to-use)
2. `tov-rubric-nielsen-norman.md` (4-dim scoring 1-5 + metriche derivate + esempi reali)
3. `tool-ecosystem-2026.md` (SimilarWeb/SemRush/Ahrefs/BuiltWith/Crunchbase/G2/Trustpilot/Capterra/Apify/parallel-cli — pricing, access, recipes)
4. `gdpr-scraping-compliance.md` (cosa è lecito, rate-limit safe, LIA documentation EU)
5. `dossier-anatomy.md` (anatomia dossier "wow" — structure, signal/noise, actionability)
6. `gap-analysis-methodology.md` (matrice 6-dim + Love-Hate-Want vs JTBD overlay + ranking formula)
7. `apify-actors-recipes.md` (actor IDs maintained 2026 per G2/Trustpilot/Capterra/BuiltWith/Crunchbase + input schema esempi)

### Output Fase B

Salva tutto in `ARCHITECTURE.md` nella cartella dell'agent.

## Fase C — Build (4-6 ore)

### Subagent file principale

`<pack-root>/.claude/agents/competitor-deep-dive/competitor-deep-dive.md`

Frontmatter (esempio iniziale — adatta in base a research):

```yaml
---
name: competitor-deep-dive
description: Da 1-5 nomi competitor produce dossier strategico evidence-first (positioning + tone of voice misurabile + reviews sentiment grounded + tech + funding). Multi-source intelligence, GDPR-aware. Output deterministico - 1 file per competitor + synthesis cross-competitor + 3 opportunità rankate. Per Marketing/Founder/PM/Sales/Analyst. Self-configuring al first run.
when_to_use: Lancio nuovo prodotto, repositioning, fundraising deck, sales battlecard, market entry nuovo segmento, due diligence M&A leggera, audit competitive periodica
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, AskUserQuestion
mcpServers:
  - apify
  - playwright
  - parallel-cli
  - google-personal
  - slack
  - attio-mcp
skills:
  - positioning-mapper
  - tov-analyzer
  - reviews-sentiment
  - gap-finder
  - dossier-writer
memory: project
model: sonnet
color: purple
---

[SYSTEM PROMPT 300-500 righe — vedi struttura sotto]
```

### Struttura system prompt (sezioni minime)

1. **Identità + ruolo** (~20 righe) — sintetizzatore evidence-first, NON enricher
2. **Discovery flow al first run** (~50 righe) — check `<memory>/config.md`, se mancante → 8 AskUserQuestion + salva config
3. **MCP detection logic** (~30 righe) — verifica disponibilità + fallback graceful (apify mandatory warn, altri opzionali)
4. **Methodology principal** (~80 righe) — 6 fasi operative:
   - (1) Ingest competitor list + cliente baseline
   - (2) Per competitor: positioning-mapper + tov-analyzer + reviews-sentiment in parallel
   - (3) Cross-competitor: pattern detection
   - (4) Gap-finder con cliente baseline overlay
   - (5) Dossier-writer: dossier × N + synthesis + opportunities
   - (6) Output sync (Google Doc / Notion / Slack / markdown)
5. **Tool usage rules** (~40 righe) — quando usare apify vs parallel-cli vs playwright vs WebFetch
6. **Output format atteso** (~30 righe) — schema markdown deterministico per dossier/synthesis/opportunities
7. **Edge cases handling** (~40 righe) — competitor stealth (no public site), no reviews G2, ToV non extractable, conflicting positioning between sources, EU geo + GDPR mode auto
8. **Examples input → output** (~50 righe) — 2-3 esempi reali end-to-end (es. "Make vs n8n vs Zapier" con dossier sintetico)
9. **Anti-patterns** (~25 righe) — cosa l'agent NON fa MAI:
   - Mai claim sentiment senza review_id + quote
   - Mai inventare dati funding/pricing
   - Mai bulk scrape senza rate-limit
   - Mai dossier >5000 parole
   - Mai gap analysis senza cliente baseline
   - Mai analizzare competitor LinkedIn behind-login (Sales Nav richiesto)
   - Mai claim ToV senza evidence quotes

### Skills companion

Per ogni skill in `skills/<skill-name>/SKILL.md`, formato standard. Vedi `skills/meta/skill-builder/SKILL.md` per pattern di scrittura skill.

**Contratto chiaro**: ogni skill ha input/output JSON schema esplicito + esempio. Chain di skill è deterministico (output skill N = input skill N+1).

### References

In `references/`, file markdown ben strutturati. **Output Fase A si converte in references** (frameworks, ToV rubric, tool ecosystem vengono da research-summary).

### Scripts

Almeno questi (in `scripts/`):

- `discovery_check.py` — verifica esistenza config, ritorna stato
- `mcp_detect.py` — check disponibilità MCP server (apify, playwright, parallel-cli, google-personal, slack, attio-mcp)
- `positioning_extract.py` — wrapper Playwright per scrape homepage/about/product
- `tov_score.py` — calcola 4-dim Nielsen Norman + metriche derivate da corpus
- `reviews_apify.py` — wrapper Apify actor per G2/Trustpilot/Capterra
- `gap_matrix_build.py` — costruisce matrice 6-dim + ranking
- `dossier_render.py` — renderer markdown deterministico (template Jinja2)

### README utente-facing

`README.md` user-friendly:

- Cosa fa in 2 paragrafi (sintetizzatore evidence-first, NON enricher)
- Installazione (3 step max)
- Esempi (almeno 3 reali con prompt → output):
  - Es. 1: Founder analizza 3 competitor pre-fundraising
  - Es. 2: Marketing manager fa repositioning analysis vs 5 competitor
  - Es. 3: PM valuta entry in nuovo segmento (2 competitor)
- FAQ (5-7 domande tipiche)
- Troubleshooting (5 problemi comuni: Apify rate limit, no reviews trovate, ToV su homepage minimalista, competitor stealth, EU GDPR warning)

## Fase D — Test (1-2 ore)

Test checklist:

1. **Discovery flow**: in progetto pulito, invoca `/competitor-deep-dive` → verifica 8 domande, salvataggio config in `<memory>/config.md`
2. **Re-run**: invoca di nuovo → verifica skip discovery, conferma "Config trovata, sono pronto. Quali competitor analizzare adesso?"
3. **Real task small**: dai 1 competitor (es. "Make @ make.com", baseline "Zapier") → verifica positioning.json + tov.json + reviews.json + dossier_make.md generati
4. **Real task standard**: dai 3 competitor → verifica 3 dossier + synthesis.md + opportunities.md (max 3 raccomandazioni)
5. **MCP fallback**: simula `apify` non disponibile → verifica messaggio "Reviews scraping degradato" + uso parallel-cli + warning chiaro su qualità ridotta
6. **Edge case stealth competitor**: dai competitor con homepage vuota/coming-soon → verifica skip graceful + flag "insufficient evidence"
7. **GDPR EU**: cliente con `geo_target: EU` → verifica auto-load `gdpr-scraping-compliance.md` + warning "Modalità GDPR attiva, rate-limit safe enforced"
8. **Anti-hallucination**: ispeziona reviews.json → verifica ogni claim ha review_id + quote (no fake)
9. **Reconfigure**: prompt "reconfigure" → verifica reset e nuova discovery

Salva risultati in `TEST-RESULTS.md`.

## Fase E — Documentation + Bundle (1 ora)

1. Aggiorna `MASTER-PROGRESS.md` (path `<pack-root>/.claude/agents/MASTER-PROGRESS.md`): cambia stato `/competitor-deep-dive` da 🟡 a ✅
2. Aggiungi sezione in `dist/CLAUDE_WEEK_SKILL_PACK.md` con descrizione + install + esempi
3. (Opzionale) Screencast 3-5 min — solo se hai tempo
4. Notifica al coordinator chat (ping Filippo): "competitor-deep-dive DONE, ready per test"

## Definition of Done

- [ ] Tutte le 5 fasi completate
- [ ] PROGRESS.md aggiornato a "Done"
- [ ] MASTER-PROGRESS.md aggiornato (✅)
- [ ] Test checklist 9/9 pass
- [ ] README utente comprensibile da non-tech (test mentale: lo darei a un Marketing manager non-developer?)
- [ ] System prompt > 300 righe e sostanzioso
- [ ] 5 skills companion + 7 references docs
- [ ] 3+ esempi reali documentati
- [ ] research-summary.md > 2500 parole con citazioni
- [ ] Anti-hallucination test verificato (ogni reviews claim ha citazione)

## Anti-pattern critici (riassunto enforce nel system prompt)

L'agent NON deve MAI:

1. **Claim senza citazione** — ogni statement (sentiment, ToV score, positioning, gap) ha source URL + quote/review_id
2. **Sentiment analysis senza evidence reali** — se Apify fallisce, output "insufficient data" (no fake sentiment)
3. **Bulk scrape senza rate-limit safe** — default delay configurato per source (G2: 5s, Trustpilot: 3s, Capterra: 5s, BuiltWith: 2s)
4. **Inventare dati su funding/pricing** — se Crunchbase/pricing page non disponibili, output "data not verified"
5. **Dossier monolite >5000 parole** — signal/noise pessimo, dossier per competitor max 1500 parole
6. **Analizzare competitor senza cliente baseline** — gap analysis impossibile senza, blocca con prompt "Definisci baseline prima di procedere"
7. **Scrape LinkedIn behind login** — solo Sales Nav account utente esplicitamente concesso
8. **Auto-pubblicare in Slack/Notion senza preview** — sempre conferma utente prima di publish

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

- **Skill v1 base (spunto, NON overwrite)**: `<pack-root>/skills/webinar-2/trend-analysis/SKILL.md`
- **Pattern subagent ufficiale**: https://code.claude.com/docs/en/sub-agents
- **Pattern skill ufficiale**: https://code.claude.com/docs/en/skills
- **Skill builder pattern**: `<pack-root>/skills/meta/skill-builder/SKILL.md`
- **Subagent #1 reference (validation pattern)**: `<pack-root>/.claude/agents/lead-finder-pro/` (BUILD-BRIEF + lead-finder-pro.md + skills/ + references/ + scripts/)
- **NotebookLM dedicato**: `competitor-deep-dive-2026` (creare in Fase A)
- **CLAUDE.md progetto**: `<pack-root>/CLAUDE.md`
- **Master plan**: `<pack-root>/.claude/agents/MASTER-PROGRESS.md`
- **CLAUDE.md utente globale**: `~/.claude/CLAUDE.md` (regole engineering, persona, stack operativo)
