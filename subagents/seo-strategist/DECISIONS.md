# DECISIONS — `/seo-strategist`

> Append-only log di decisioni importanti (architectural, scope, trade-off). Immutable per default — non riscrivere, solo aggiungere.

## Format entry

```markdown
## YYYY-MM-DD HH:MM — [DECISION-N] Titolo decisione

**Contesto**: cosa stavamo affrontando
**Decisione**: cosa abbiamo scelto
**Alternative considerate**: cosa abbiamo scartato e perché
**Trade-off**: pro e contro
**Reversibilità**: facile/media/difficile
```

## Decisioni iniziali (coordinator, 2026-05-01)

### [DECISION-001] Pattern Auto-Onboarding

**Contesto**: serve che ogni subagent diventi specifico per ruolo/stack/output utente.

**Decisione**: discovery interattiva al first run via AskUserQuestion (8 domande), salvataggio config in `<memory>/config.md`, re-prime config su run successivi.

**Alternative considerate**:

- Config tramite ENV vars → scartato: troppo developer-oriented per audience Learnn
- Config statica file pre-compilato → scartato: friction alta
- CLI flag → scartato: utente non ricorda flag

**Trade-off**: 2-3 min onboarding al first run, ma agent diventa "tuo".

**Reversibilità**: facile (cambia config.md o "reconfigure").

### [DECISION-002] Naming inglese kebab-case

**Contesto**: scelta lingua nomi subagent/skill.

**Decisione**: nomi tecnici inglese (kebab-case), messaggi utente italiano.

**Alternative considerate**:

- Tutto italiano → scartato: incoerente con ecosistema Anthropic
- Prefisso `/yt-` → scartato: meno pulito

**Trade-off**: nomi inglese da ricordare, ma sono standard.

### [DECISION-003] Topic SEO+GEO dual focus

**Contesto**: SEO 2026 evolution post-AI Overviews + ChatGPT/Perplexity citation. GEO è topic emergente (non c'era pack v1).

**Decisione**: subagent copre dual SEO classico (Google/Bing) + GEO (ChatGPT/Perplexity/Claude/Gemini citation). Discovery Q6 permette user di prioritizzare uno dei due o entrambi.

**Alternative considerate**:

- Solo SEO classico → scartato: 2026 trend GEO troppo importante per skip
- Solo GEO → scartato: SEO Google ancora 60-70% traffic per maggior parte siti
- 2 subagent separati → scartato: scope mismatch, GEO è strato sopra SEO

**Trade-off**: scope ampio = system prompt più denso. Compensato da skill modulari (SEO core in `keyword-research`+`content-audit`, GEO in `geo-optimizer` skill dedicata).

**Reversibilità**: facile (skill switch).

### [DECISION-004] Memory scope = project

**Contesto**: dove salvare config persistente per `/seo-strategist`.

**Decisione**: `memory: project` di default — config legata al cliente/progetto specifico (1 progetto = 1 dominio = 1 ICP = 1 stack tool).

**Alternative considerate**:

- `memory: user` → utile se user fa SEO per più clienti diversi con stesso stack. Ma normalmente domain + ICP + content type cambiano per cliente
- `memory: local` → solo locale al working dir, non sincronizzabile

**Trade-off**: scope project = config riusabile per re-run incrementali (re-audit dopo 90gg, refresh content cluster). Cross-project bisogna ripetere discovery.

**Reversibilità**: facile (cambia frontmatter).

## Decisioni emergent (worker chat, 2026-05-01)

### [DECISION-005] NotebookLM SKIP per `/seo-strategist`

**Contesto**: BUILD-BRIEF Phase A suggerisce creare NotebookLM dedicato "SEO + GEO Strategy 2026" con 10 sources.

**Decisione**: SKIP NotebookLM dedicated. Research consolidata via 8 WebSearch query + 4 WebFetch primary (Google Search Central, web.dev INP blog, llmstxt.org, Google FAQPage doc) = 4 primary sources + 16 secondary citations tracciate inline in `research/research-summary.md`.

**Alternative considerate**:
- Crea NotebookLM con 10 sources + ask 7 RQ → scartato: 3-5 min indexing per query + ground già raccolto da fonti primary autorevoli (Google docs)
- Mix WebSearch + NotebookLM → scartato: overhead non giustificato per topic con primary docs accessibili

**Trade-off**: pro = velocità Phase A, ground sufficient per Tier 2 agent. Contro = se claim controversa emerge in build, devo re-WebFetch invece di riusare contesto NotebookLM.

**Reversibilità**: facile — se serve more depth in build, posso creare NotebookLM ad-hoc su sub-topic specifico.

**Pattern**: coerente con DECISION-009 di `/outbound-orchestrator` (NotebookLM skip se grounded sufficiente).

### [DECISION-006] FAQPage schema dual-purpose (Google rich result vs LLM citation)

**Contesto**: Google primary doc 2026 stringe FAQPage rich result eligibility a «well-known, authoritative websites that are government-focused or health-focused». Per resto siti, schema FAQPage non triggera rich result.

**Decisione**: skill `schema-generator` propone FAQPage solo se site_type ∈ {government, health, education_authority}. Per altri site types, output schema FAQPage MA con warning esplicito: "Google rich result NON eligible per il tuo site type. Schema mantenuto per LLM citation (ChatGPT/Perplexity/Claude)."

**Alternative considerate**:
- Skip FAQPage sempre per site non-eligible → scartato: perde valore GEO (FAQPage è Tier 1 schema per AI citation)
- Output FAQPage senza warning → scartato: utente poi vede no rich result e dà colpa allo agent

**Reversibilità**: facile.

### [DECISION-007] HowTo schema NEVER as default

**Contesto**: HowTo rich result deprecated da Google 2023 (multi-source).

**Decisione**: skill `schema-generator` NON propone mai HowTo come default. Se utente esplicitamente richiede HowTo, output con warning + suggest fallback a Article + nested ItemList (better preserved).

**Reversibilità**: facile.

### [DECISION-008] GDPR mode auto-attivo se geo Italy/EU detected

**Contesto**: Garante 2024 enforcement strict. Discovery Q5 = "Italia" o "Europa" → user è esposto.

**Decisione**: GDPR mode auto-attiva (no opt-in) se Q5 ∈ {italia, europa, multi_paese} → carica `references/gdpr-privacy-seo-2026.md` + warning utente "🇮🇹 GDPR mode attivo: cookie consent v2 mandatory + GA4 strict config + Garante checklist enforced".

**Pattern**: coerente con `/competitor-deep-dive` DECISION-005 (GDPR auto-attivo) e `/lead-finder-pro`.

**Reversibilità**: facile (utente può manual override "skip-gdpr-mode" comando).

### [DECISION-009] INP audit non automatic — guidance only

**Contesto**: INP è metrica field-only (CrUX, Search Console). Agent non può misurare INP da Bash o WebFetch — serve real user data.

**Decisione**: skill `technical-seo-audit` NON tenta INP measurement. Output: link Search Console URL property + Google PageSpeed Insights API (per LCP/CLS lab) + interpretation guidance + recommendation "fammi sapere il valore INP da Search Console e ti suggerisco fix specifici".

**Trade-off**: agent meno "magico" ma honest. No false numbers.

**Reversibilità**: facile.

### [DECISION-010] Tool tier strict per budget

**Contesto**: BUILD-BRIEF emergent #2 — tool recommendation budget-respecting.

**Decisione**: skill recommendation tool stack tier-locked basato su Q8 budget:
- <€100 → Search Console + Ubersuggest free + Ahrefs Webmaster Tools (own site only)
- €100-500 → Ahrefs Lite OR Moz Pro (one or the other, no double-spend)
- €500-2k → Ahrefs Standard + SEMrush Pro
- €2k+ → full agency stack (Ahrefs Advanced + SEMrush Business + Scrunch + Profound)

Mai consigliare tool sopra tier user (rispetto budget reale).

**Reversibilità**: facile (utente upgrade tier in reconfigure).

### [DECISION-011] GEO priority gating skill load

**Contesto**: BUILD-BRIEF emergent #1 — GEO priority dual SEO+GEO o solo SEO classico.

**Decisione**: Q6 governs:
- `priority` → carica `geo-optimizer` skill in ogni content piece audit
- `secondary` → carica `geo-optimizer` solo per pillar pages (top 5-10 per cluster)
- `skip` → skip skill `geo-optimizer` totalmente, focus su SEO classico

**Trade-off**: skip GEO = agent meno completo per AI search era, ma rispetta scope user.

**Reversibilità**: facile (Q6 modificabile in reconfigure).
