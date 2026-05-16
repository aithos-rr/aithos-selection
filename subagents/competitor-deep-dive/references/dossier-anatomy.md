# Dossier Anatomy — Structure "Wow" + Word Budget + Signal/Noise

> Pattern verificato su agency competitive intelligence (Octopus, MADX, Olushad). Output di Fase A research RQ7. Used by `dossier-writer` skill.

## Word budget hard-cap

Anti-pattern #5 enforce: **dossier monolite >5000 parole = signal/noise pessimo**.

| Output file | Max words | Target | Note |
|-------------|-----------|--------|------|
| `dossier_<slug>.md` per competitor | 1500 | 700-900 | Hard cap, truncate se overflow |
| `synthesis.md` cross-competitor | 1000 | 600-800 | Skip se 1 solo competitor |
| `opportunities.md` top 3 reco | 800 | 500-650 | Sempre 3 reco max (no top 5+) |

## Structure "wow" — dossier per competitor (target 700-900 parole)

### Sezione 1: TL;DR Executive (50-75 parole)

**Cosa contiene**:
- 1 frase snapshot (chi è, posizionamento dominante)
- 3 bullet che il reader può tweetare / dire a una call

**Esempio**:
> **TL;DR (62 parole)**: Make si posiziona come visual no-code workflow builder per technical operators mid-market, con free tier aggressivo (1000 ops/month). Casual+Serious tone, 62% review positive. Strength: drag-drop UI; Weakness: pricing scaling. Want primary: AI-assisted suggestion. Gap vs cliente: AI engine debole, mid-market sweet spot conteso.
> - Visual no-code builder, 10,000+ apps integration
> - Free tier 1k ops/month, paid $9-29
> - Top JTBD: build automation 10x faster than manual

### Sezione 2: Positioning + Value Prop (100-150 parole)

**Cosa contiene**:
- Tagline + value prop con `[source URL]`
- ICP inferred + 1-2 evidence quotes
- 3 differentiators con verbatim quote

**Anti-pattern**: tagline senza source URL → block.

### Sezione 3: Tone of Voice (100-150 parole)

**Cosa contiene**:
- 4-dim NN scores 1-5 con label (tabella)
- 1 evidence quote per dim (3 in `tov.json` ma 1 in dossier per brevità)
- Derived metrics tabella (jargon%, pronoun ratio, sentence avg, CTA style, exclamation density)

**Anti-pattern**: ToV claim su corpus <200 parole → flag `> ⚠️ ToV unmeasurable`.

### Sezione 4: Reviews Sentiment (150-200 parole)

**Cosa contiene**:
- Sentiment breakdown % (positive / neutral / negative)
- Top 5 strengths (theme + frequency + 1 evidence quote con review_id)
- Top 5 weaknesses (idem)
- Top 3 JTBD (outcome + frequency)
- Love / Hate / Want bullets (3 per categoria max)

**Anti-pattern**: claim sentiment senza `review_id + quote` → block.

### Sezione 5: Tech & Funding (100-150 parole, **deep tier only**)

**Cosa contiene**:
- BuiltWith stack (analytics, hosting, CRM, payment)
- Crunchbase last round (type + amount + date)
- Total raised + key investors

**Skip se**: tier `quick` o `standard`.

### Sezione 6: Gap vs cliente baseline (100-150 parole)

**Cosa contiene**:
- 3-5 gap rankati per `gap_score` (top 5 da gap-matrix.json)
- Per ogni gap: 1 frase + score numerico + categoria (quick win / strategic bet)

**Anti-pattern**: gap senza baseline → BLOCK upstream.

### Sezione 7: Sources (footer, ~5 righe)

- URL homepage scraped
- URL pricing page
- Apify actor used + run ID
- Reviews scraped count
- Scrape date

## Structure synthesis.md (max 1000 parole, target 600-800)

```markdown
# Synthesis — Pattern Cross-Competitor

> Analisi {{ N }} competitor: <lista>. Cliente baseline: <tagline>.

## 1. Common positioning tropes (~150 parole)
{tropes con frequenza, es. "tutti claim 'no-code'"}

## 2. Common Tone of Voice pattern (~150 parole)
{ToV convergence summary + blue ocean hint}

## 3. Common gap — cosa nessuno fa (~200 parole)
{universal_want themes da gap-matrix}

## 4. Customer Love-Hate-Want overlap (~200 parole)
{tabella con frequency cross-competitor}

## 5. Implicazioni strategiche (~100 parole)
{3 implications per cliente baseline}
```

## Structure opportunities.md (max 800 parole, target 500-650)

```markdown
# Top 3 Opportunità Strategiche

> Selezionate da gap-finder: 1 quick win + 2 strategic bet, rankate per impact × ease.

## 1. <Quick Win Title> (~200 parole)

- **Score**: {{gap_score}} (impact × ease × evidence / complexity)
- **Cosa fare**: {description}
- **Owner suggerito**: Marketing / PM / Eng
- **Success metric**: {misura quantitativa, es. "+15% conversion homepage entro Q3"}
- **Due date**: {data concreta}
- **7-day next step**: {cosa fare lunedì mattina}
- **Evidence**: {2-3 evidence con URL/review_id}

## 2. <Strategic Bet 1> (~250 parole)

...

## 3. <Strategic Bet 2> (~200 parole)

...
```

## Signal vs Noise — cosa enfatizzare vs evitare

### ✅ High-signal (enfatizzare)

1. **Customer JTBD evidence** review-mined con review_id → "le persone hire questo prodotto per fare X"
2. **Keyword gap quantificato** (rank diff con tool, es. "competitor rank #3, noi #45")
3. **Backlink source duplication** (overlap %)
4. **Pricing strategy** (modello + fascia + transparency)
5. **ToV differentiation** con quote concrete + scores 1-5
6. **Universal Want** customer (3 fonti reviews indipendenti chiedono lo stesso)
7. **Funding round signal** (Series B 2026 → push enterprise)
8. **Hiring trend** (es. "10 hire SDR Q1" → push outbound aggressive)

### ❌ Noise (escludere)

1. **Vanity metrics social** (followers, like senza engagement context)
2. **UI screenshots** non connesse a conversion
3. **About us bio founder** senza analytical insight
4. **Speculation** ("they might launch X next year") — solo se evidence forte
5. **Competitor logo gallery** senza analisi
6. **Lengthy quote dump** (3+ quote per claim) — sempre 1-2 sample, full quote in JSON intermediate
7. **Feature checklist exhaustive** (50+ features) — focus 3-5 differentiators

## Actionability checklist (il dossier deve abilitare)

Per ogni dossier completo, il reader deve poter:

- [ ] Sales: identificare 3 obiezioni typical → battlecard counter
- [ ] Marketing: identificare 3 keyword gap → editorial brief
- [ ] PM: identificare 3 feature gap → roadmap prioritization input
- [ ] Founder: identificare 3 strategic bet → board update
- [ ] Per ogni gap: assegnare owner + due date + success metric

Test: leggi il dossier, scrivi su un post-it 5 azioni concrete che farai nei prossimi 7 giorni. Se non puoi → dossier ha fallito (signal/noise pessimo).

## Esempio dossier scoring (rubric qualità)

| Criterio | Score 1-5 |
|----------|-----------|
| Word count entro budget | 5 (≤900 word) → 1 (>1500) |
| Citazioni inline (URL + review_id) | 5 (ogni claim citato) → 1 (<50% cited) |
| ToV scores con 3+ evidence per dim | 5 (full evidence) → 1 (no evidence) |
| Reviews evidence con review_id | 5 (every claim) → 1 (no review_id) |
| Gap score formula applied | 5 (deterministic) → 1 (subjective) |
| 7-day actionability | 5 (concrete steps) → 1 (vague) |

Target: dossier deve scorare ≥4 su tutti criteri (≥24/30 totale). Sotto soglia → re-render.

## Anti-pattern dossier (8 critical)

> "The standard approach — a spreadsheet with feature checkboxes, a few pricing screenshots, and a SWOT template — produces an output that looks like research but rarely generates insights you can act on." — [Olushad Global Solutions](https://www.olushad.com/insights/saas-competitor-analysis-framework)

1. Dossier monolite >5000 parole
2. Claim senza citazione URL / review_id
3. Vanity metrics social senza context
4. Feature checklist exhaustive (no top 5 selection)
5. Speculation senza evidence forte
6. ToV senza evidence quotes
7. Reviews senza review_id (allucinazione)
8. Gap senza score (subjective ranking)

## Reference

- [MADX Digital — How to Do SaaS Competitive Analysis 2026](https://www.madx.digital/learn/saas-competitor-analysis)
- [Olushad Global Solutions — SaaS Competitor Analysis Framework](https://www.olushad.com/insights/saas-competitor-analysis-framework)
- [Octopus Intelligence — SaaS Competitor Analysis Case Study](https://www.octopusintelligence.com/saas-competitor-analysis-case-study-how-a-competitor-was-trying-to-beat-them/)
- `research/research-summary.md` RQ7 — fonte derivazione
- `skills/dossier-writer/SKILL.md` — implementazione template Jinja2
