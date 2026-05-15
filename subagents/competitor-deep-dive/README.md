# Competitor Deep Dive — Subagent Pack v2 Learnn

> Da 1-5 nomi competitor → dossier strategico markdown evidence-first in 1 day. Per Marketing manager, Founder, PM, Sales, Analyst — community Learnn audience non-developer.

## Cosa fa in 2 paragrafi

**`/competitor-deep-dive`** trasforma una lista di 1-5 nomi competitor in un dossier strategico markdown deterministico, multi-source, evidence-first. Per ogni competitor estrae positioning (Playwright scrape homepage/about/product), Tone of Voice misurabile (Nielsen Norman 4-dim + 5 metriche derivate), reviews sentiment grounded (Apify zen-studio actor su G2/Trustpilot/Capterra con review_id + verbatim quote per ogni claim — anti-hallucination MANDATORY), gap matrix 6-dim vs cliente baseline, e top 3 raccomandazioni rankate per impact × ease.

**Cosa NON fa**: lead enrichment (vedi `/lead-finder-pro`), outbound campaign (vedi `/outbound-orchestrator`), web app build (vedi `/web-builder`). Sintetizzatore evidence-first, NON enricher. Non inventa sentiment, non allucina ToV, non bypass GDPR su EU. Word budget hard-cap (1500 dossier / 1000 synthesis / 800 opportunities) — dossier monolite >5000 parole = signal/noise pessimo.

## Installazione (3 step)

### Step 1: Clona o scarica il subagent

```bash
# Da repository pack v2 (futuro)
git clone https://github.com/filippogreco/claude-skills-learnn.git
cp -r claude-skills-learnn/agents/competitor-deep-dive ~/.claude/agents/
```

### Step 2: Verifica MCP server disponibili

`/competitor-deep-dive` richiede:

- **Required**: `apify` (reviews scraping), `playwright` (positioning + ToV corpus)
- **Recommended**: `parallel-cli` CLI Bash (long-tail signal), `google-personal` (output Google Doc), `attio-mcp` (CRM linkage)
- **Optional**: `slack` (post sintesi), `notebooklm` CLI (cross-check ground)

Verifica setup:

```bash
cd ~/.claude/agents/competitor-deep-dive/
pip install -r scripts/requirements.txt
python scripts/mcp_detect.py
```

Output JSON con stato ogni MCP + fallback attivi se mancanti.

### Step 3: Lancia il subagent

```bash
# In Claude Code, qualsiasi cartella progetto
claude
> /competitor-deep-dive
```

Al first run, 8 domande discovery (~3-5 min). Dopo, lavoro continuo con config persistente.

## 3 esempi reali end-to-end

### Esempio 1 — Founder pre-fundraising, 3 competitor

**Setup**:
- Filippo è founder di una startup workflow automation
- Va da investor seed in 6 settimane, vuole defendable positioning
- Discovery: role=founder, depth=standard, baseline=tagline "Automate workflows for technical PMs", competitors=Make+n8n+Zapier

**Prompt**:
```
> /competitor-deep-dive
> Analizza Make, n8n, Zapier per il mio fundraise.
```

**Output**:
- `dossier_make.md` 870 parole — ToV Casual+Serious, 142 G2 reviews mining "love drag-drop, hate steep curve"
- `dossier_n8n.md` 820 parole — "love self-host, hate UI clunky"
- `dossier_zapier.md` 920 parole — "love simplicity, hate pricing"
- `synthesis.md` 850 parole — Tutti claim "no-code", tutti enterprise pivot 2024-2025, gap su "AI-assisted workflow building"
- `opportunities.md` 750 parole — Top reco: "Position around AI-first workflow building per technical PM mid-market" (impact 5 × ease 4)

**Costo**: ~$18 Apify + 2.5h tempo

---

### Esempio 2 — Marketing manager repositioning, 5 competitor

**Setup**:
- Sara è Marketing Manager di un PaaS B2B EU
- Discovery: role=marketing, industry=SaaS B2B, depth=standard, geo=EU (GDPR mode ON), reviews_focus=[G2, Trustpilot]

**Prompt**:
```
> /competitor-deep-dive
> Analizza Vercel, Netlify, Heroku, Render, Railway. Voglio capire cosa scrivere in homepage.
```

**Output highlights**:
- 5 dossier per competitor + synthesis cross-platform
- ToV diff insight: 4/5 sono "Casual+Irreverent+Enthusiastic" (Vercel super-irriverente). Sara può andare BLUE OCEAN su "Formal+Respectful+Matter-of-fact" per target enterprise
- Gap "format": 5/5 hanno blog tech-deep, NESSUNO ha podcast → opportunità content
- LIA template auto-generato per cliente EU in `<memory>/lia_template.md`

**Costo**: ~$22 Apify + 4h tempo

---

### Esempio 3 — PM market entry nuovo segmento, 2 competitor

**Setup**:
- Gianluca è PM di un product analytics tool, vuole entrare segmento "session replay"
- Discovery: role=pm, industry=SaaS B2B, depth=quick (battlecard rapido), geo=USA, reviews_focus=[G2]

**Prompt**:
```
> /competitor-deep-dive
> Quick scan FullStory + Hotjar, voglio capire feature gap e JTBD prima di pitcharlo al CEO venerdì.
```

**Output highlights**:
- `dossier_fullstory.md` 750 parole — JTBD "debug user friction without engineering ticket"
- `dossier_hotjar.md` 720 parole — JTBD "validate UX hypothesis cheap"
- `opportunities.md` 600 parole — Reco: "Position around Mid-market SOC2 + Pricing transparency" (gap entrambi)
- Skip synthesis (Quick scan)

**Costo**: ~$8 Apify + 1.5h tempo

## FAQ

### Q1: Quanti competitor posso analizzare in 1 run?

Max 5 a run. Più di 5 = analisi superficiale (signal/noise pessimo). Suggerimento: batch separato.

### Q2: Cosa succede se Apify rate limit hit?

Checkpoint + retry exponential backoff (5s → 30s → 5min). Dopo 3 retry fail → output `insufficient_evidence` + fallback parallel-cli.

### Q3: Posso usare se non ho Apify account?

Sì ma degraded. Reviews scraping non disponibile, sostituito da parallel-cli search Reddit/HN. Dossier sezione Reviews avrà flag `> WARNING: Reviews fallback`. Per analisi completa Apify free tier $5 credit/mese basta.

### Q4: GDPR EU compliance — cosa fa il subagent?

Se `geo_target ∈ {Italia, EU, EMEA}`:
- Auto-load `references/gdpr-scraping-compliance.md`
- Genera LIA template in `<memory>/lia_template.md` (compilabile dal cliente)
- Rate-limit safe enforced (G2 5s, Trustpilot 3s, Capterra 5s)
- Anonimizzazione PII reviewer post-raccolta
- Retention 90gg max sui file output
- Cross-border flag se reviews source USA

### Q5: Posso re-fresh dossier vecchi dopo 90 giorni?

Sì. Config mantiene `competitors_analyzed[]` history. Comando: `re-analyze [competitor_name]` o `audit periodico` → re-run pipeline su competitor noti.

### Q6: Output Google Doc / Slack / Notion — come funziona?

Configura al discovery (Q5 — Output format):
- **Google Doc**: richiede `google-personal` MCP. Genera 1 doc per competitor + 1 synthesis.
- **Slack**: richiede `slack` MCP. Post sintesi opportunities in canale specificato. Sempre preview prima di publish.
- **Notion**: NO MCP default → fallback markdown locale + warning.

### Q7: Posso configurare un altro user.role dopo discovery?

Sì. Comando: `reconfigure` → re-run 8 domande con valori precedenti come hint default. Mantieni `competitors_analyzed[]` history.

## Troubleshooting (5 problemi comuni)

### Problema 1: Apify rate limit hit dopo 50 reviews

**Sintomo**: skill `reviews-sentiment` output `insufficient_evidence: true, reason: "rate_limit_persistent"`

**Fix**:
1. Aspetta 1h, poi retry single platform alla volta
2. Riduci `max-reviews-per-platform` da 100 a 50 in config
3. Switch actor a fallback `taroyamada/g2-capterra-review-intelligence`

### Problema 2: No reviews trovate per competitor very new

**Sintomo**: `total_reviews_scraped < 10` su tutte le platform

**Fix**:
1. Fallback parallel-cli search Reddit/HN: `parallel-cli search "site:reddit.com/r/SaaS <competitor>"`
2. Fallback Twitter/LinkedIn mention via parallel-cli
3. Se proprio zero → flag insufficient_evidence + skip Reviews section nel dossier

### Problema 3: ToV su homepage minimalista (Linear, Apple, etc.)

**Sintomo**: `corpus_size_words < 200`, output `tov_unmeasurable`

**Fix**:
1. Espandi corpus: aggiungi `/about` + 5 latest blog post
2. Scrape LinkedIn company "About" section
3. Se ancora insufficient → flag e skip ToV section

### Problema 4: Competitor stealth (homepage 404 o coming-soon)

**Sintomo**: `stealth_detected: true` da `positioning-mapper`

**Fix**:
1. Verifica spelling dominio
2. Schedule re-analysis 30gg dopo (potrebbe essere pre-launch)
3. Fallback parallel-cli search per news/funding press release

### Problema 5: EU GDPR warning bloccante

**Sintomo**: warning "GDPR mode attivo, rate-limit safe enforced" + LIA template required

**Fix**:
1. Compila LIA template in `<memory>/lia_template.md` (preventivo legal review)
2. Conferma esclusione siti sensibili (Article 9)
3. Set `retention_days` esplicito in config (default 90)
4. Se cliente non-EU → cambia `geo_target` in `USA` con `reconfigure` comando

## Anatomia file deliverable

```
.claude/agents/competitor-deep-dive/
├── BUILD-BRIEF.md             # brief originale Filippo
├── PROGRESS.md                # log milestone (external brain)
├── DECISIONS.md               # decisioni immutable
├── ARCHITECTURE.md            # design completo
├── README.md                  # (questo file) user-friendly
├── competitor-deep-dive.md    # system prompt main agent (477 righe)
├── discovery/
│   └── questions.md           # 8 domande discovery
├── skills/
│   ├── positioning-mapper/SKILL.md
│   ├── tov-analyzer/SKILL.md
│   ├── reviews-sentiment/SKILL.md   # anti-hallucination MANDATORY
│   ├── gap-finder/SKILL.md
│   └── dossier-writer/SKILL.md
├── references/
│   ├── competitor-analysis-frameworks-2026.md
│   ├── tov-rubric-nielsen-norman.md
│   ├── tool-ecosystem-2026.md
│   ├── gdpr-scraping-compliance.md
│   ├── dossier-anatomy.md
│   ├── gap-analysis-methodology.md
│   └── apify-actors-recipes.md
├── scripts/
│   ├── discovery_check.py     # config check
│   ├── mcp_detect.py          # MCP availability
│   ├── positioning_extract.py # Playwright wrapper
│   ├── tov_score.py           # ToV 4-dim NN scoring
│   ├── reviews_apify.py       # Apify wrapper
│   ├── gap_matrix_build.py    # gap matrix builder
│   ├── dossier_render.py      # markdown renderer
│   └── requirements.txt
├── research/
│   └── research-summary.md    # Fase A research output (3887 parole)
├── memory/
│   └── config.md              # user config (post-discovery)
└── output/                    # runtime artefatti (positioning_*.json, tov_*.json, reviews_*.json, gap-matrix.json)
```

## Anti-pattern enforced (8 critical)

L'agent NON fa MAI:

1. Claim sentiment senza review_id + quote → output blocked
2. ToV score senza ≥3 evidence quotes per dim → output blocked
3. Inventare funding/pricing data → flag `data_not_verified`
4. Bulk scrape senza rate-limit safe → default delay enforced
5. Dossier monolite >5000 parole → word budget hard-cap
6. Gap analysis senza cliente baseline → block + prompt
7. Scrape LinkedIn behind login → skip + log
8. Auto-publish Slack/Notion senza preview → conferma utente

## Crediti & Licenza

Build: Filippo Greco — AI Training & Solutions Manager @ Yellow Tech, GTM Engineer.
Subagent #2 di 8 nel Pack v2 Learnn — community 10k+ iscritti.
Validation pattern reference: `/lead-finder-pro` (subagent #1).

License: MIT.

Built with Claude Sonnet 4.6 (worker chat) + Opus 4.7 (coordinator). Filosofia: ogni claim ha evidence, ogni evidence ha source URL, mai allucinazioni, word budget hard-cap, output deterministic.

## Reference

- BUILD-BRIEF: `BUILD-BRIEF.md` (definitivo)
- ARCHITECTURE: `ARCHITECTURE.md`
- Research: `research/research-summary.md` (3887 parole, 18 sources)
- Master plan: `../MASTER-PROGRESS.md`
- Pack v2 GitHub: https://github.com/filippogreco/claude-skills-learnn (futuro)
- Issue / domande: your-email@example.com
