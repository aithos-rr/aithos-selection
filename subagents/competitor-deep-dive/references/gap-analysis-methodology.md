# Gap Analysis Methodology — 6-dim Matrix + Love-Hate-Want vs JTBD + Ranking Formula

> Methodology completa per gap analysis cross-competitor + cliente baseline. Used by `gap-finder` skill. Source: Fase A research RQ5.

## I 6 dimensioni di analisi

### Dim 1 — Feature

**Cosa**: feature funzionali / capabilities che il prodotto offre.

**Source**:
- `positioning.json` `differentiators[]`
- `reviews.json` `top_strengths[].theme` (cosa customer Love)
- Feature explicit page se presente
- (Deep tier) BuiltWith integration list

**Output gap**: cliente ha feature X? competitor sì/no.

**Esempio**:
- Feature "Self-host" → n8n ✓, Make ✗, Zapier ✗, Cliente ✗ → segment opportunity
- Feature "AI auto-suggest" → Make partial, n8n ✗, Zapier partial, Cliente ✗ → universal want

### Dim 2 — Segment

**Cosa**: ICP servito (Mid-market vs Enterprise vs SMB vs Solopreneur).

**Source**:
- `positioning.json` `icp_inferred` + `icp_evidence`
- Pricing tier names (es. "Enterprise" tier → enterprise ICP)
- Reviews `reviewer_company_size`

**Output gap**: cliente serve segmento X? competitor sì/no.

**Esempio**:
- Mid-market: tutti i 3 competitor servono
- Enterprise: tutti hanno tier dedicato, cliente ha solo Pro tier → gap
- SMB: solo Zapier ottimizza per SMB con free tier — cliente potrebbe non servire (intentional skip)

### Dim 3 — Geo

**Cosa**: geografie servite (USA / EU / Italia / EMEA / Worldwide).

**Source**:
- `competitors_input[].domain` (.com vs .eu vs .it)
- `positioning.json` `pricing_summary` (USD vs EUR pricing)
- Localized blog/content presence

**Output gap**: cliente target X geo? competitor presente?

**Esempio**:
- Cliente target Italia: Make ha .com only (no IT localization), n8n self-host (geo-agnostic), Zapier ha .it landing — Zapier vantaggio geo

### Dim 4 — ToV (Tone of Voice)

**Cosa**: voice differentiation (Casual vs Formal, Funny vs Serious, etc.).

**Source**:
- `tov.json` `scores` + `derived_metrics`
- Cliente baseline ToV (se scorato)

**Output gap**: ToV cliente differentia? convergenza competitor → blue ocean opportunity.

**Esempio**:
- Tutti 3 competitor: Casual + Enthusiastic
- Cliente baseline: Casual + Enthusiastic → convergence! Blue ocean: pivot a Formal + Matter-of-fact per target enterprise serious
- Cliente baseline: Formal + Respectful → già differenziato, mantieni

### Dim 5 — Format

**Cosa**: content format dominante (long-form blog vs video vs podcast vs docs vs community).

**Source**:
- Scrape detect: `/blog`, `/podcast`, `/youtube`, `/docs`, `/community`, `/webinars`
- Reviews mention format ("loved their YouTube tutorials")

**Output gap**: cliente investe in format X? competitor sì/no.

**Esempio**:
- Tutti 3 competitor: blog tech-deep + docs estesi
- Nessuno: podcast settimanale → format gap (potenziale opportunità content)

### Dim 6 — Pricing

**Cosa**: modello (subscription / usage / hybrid / call-only) + fascia ($ vs $$$$).

**Source**:
- `positioning.json` `pricing_summary`

**Output gap**: cliente differenzia su pricing strategy?

**Esempio**:
- Tutti 3 competitor: subscription tier-based
- Nessuno: usage-based pure ("pay per execution")
- Cliente potrebbe pivotare a usage-based per defensibility

## Love-Hate-Want vs JTBD overlay

Mining cross-competitor da `reviews.json`:

```python
all_love_themes = aggregate([c.reviews.love_hate_want.love for c in competitors])
all_hate_themes = aggregate([c.reviews.love_hate_want.hate for c in competitors])
all_want_themes = aggregate([c.reviews.love_hate_want.want for c in competitors])
all_jtbd = aggregate([c.reviews.top_jtbd for c in competitors])

clustered_love = cluster_themes(all_love_themes)  # cosa tutti hanno e customer adorano
clustered_hate = cluster_themes(all_hate_themes)  # cosa tutti hanno e customer odiano
clustered_want = cluster_themes(all_want_themes)  # cosa nessuno offre
clustered_jtbd = cluster_themes(all_jtbd)  # outcome dominanti
```

### Insight estraibili

| Theme | Love (Universal) | Hate (Universal) | Want (Universal) | JTBD primary |
|-------|------------------|------------------|------------------|--------------|
| Strategic interpretation | Minimum bar — cliente DEVE avere | Opportunità "fix what they break" | Blue ocean — nessuno offre | Coerenza con baseline value_prop |
| Action | Match feature minimum | Differentiate on this feature | Build first — first-mover | Verify cliente serve stesso JTBD |

## Ranking formula

```python
gap_score = (impact × ease × evidence_strength) / max(1, complexity_penalty)
```

### Componenti — scale 1-5

#### Impact (1-5)

Quanto sposta lead/revenue per cliente se chiudo gap.

- **5 transformational**: blue ocean reco, target ARR +20%+
- **4 significant**: nuovo segment / nuovo geo, ARR +10%+
- **3 moderate**: feature gap importante, ARR +5%
- **2 marginal**: nice-to-have, ARR <5%
- **1 trivial**: cosmetic, no ARR impact direct

#### Ease (1-5)

Quanto è facile chiuderlo.

- **5 quick win <30gg**: messaging update, content piece
- **4 30-90gg**: campaign + landing page revamp
- **3 3-6 mesi**: feature build mid-complexity
- **2 6-12 mesi**: feature heavy / new segment GTM
- **1 1+ anno**: re-platform, M&A, fundraise

#### Evidence Strength (1-5)

Quanto è forte l'evidence (review count + JTBD frequency + cross-competitor consistency).

- **5 strong**: ≥3 source independent + cross-competitor consistent + JTBD primary
- **4 good**: ≥2 source + 1 platform reviews ≥30 evidence
- **3 moderate**: single source + reviews ≥10
- **2 weak**: inferred from positioning, no reviews evidence
- **1 speculative**: no evidence, intuition

#### Complexity Penalty (1-3)

Moltiplicatore se richiede stack overhaul.

- **1 no overhaul**: pure messaging change, content piece
- **2 moderate**: new feature + UX, A/B test
- **3 heavy**: re-platform / new geo / new pricing model

### Esempio applicato

Gap: "AI-assisted workflow building"

- Impact: 5 (transformational, blue ocean lato)
- Ease: 3 (3-6 mesi build mid-complexity)
- Evidence_strength: 5 (universal want, 3/3 competitor reviews segnalano)
- Complexity_penalty: 2 (new feature + UX)

`gap_score = (5 × 3 × 5) / max(1, 2) = 75 / 2 = 37.5`

Top ranking. Categoria: **Strategic bet**.

### Categorizzazione

Sort gaps by `gap_score` descending. Categorize:

| Category | Threshold | Selection |
|----------|-----------|-----------|
| **Quick wins** | impact ≥3 + ease ≥4 | Top 1-3 (sezione 1 opportunities.md) |
| **Strategic bets** | impact ≥4 + ease ≤3 | Top 2 (sezione 2-3 opportunities.md) |
| **Backlog** | impact ≥3 + ease 2-3 | Documentati ma non in opportunities |
| **Ignore** | impact ≤2 OR evidence_strength ≤2 | Drop dal report |

## Pattern detection cross-competitor

Cluster su 6 dim:

### Convergence pattern (tutti uguali)

- Tutti hanno feature X → minimum bar (Cliente DEVE avere)
- Tutti hanno ToV Casual → blue ocean opportunity Formal
- Tutti pricing $9-29 → potenziale opportunity premium $99+
- Tutti format blog only → opportunity podcast/video

### Divergence pattern (1 outlier)

- 2/3 self-host ✗, 1/3 self-host ✓ (n8n) → niche segment con auto-selection
- 2/3 USD pricing only, 1/3 EUR localization → geo opportunity

### Universal Want (nessuno offre, customer chiedono)

- AI auto-suggest workflow → first-mover advantage
- SOC2 Type II audit report public → trust differentiator

## Output `gap-matrix.json` schema

Vedi `skills/gap-finder/SKILL.md` Fase 7 per schema completo.

## Anti-pattern

- **NO gap analysis senza cliente baseline** — BLOCK
- **NO ranking subjective** — sempre formula deterministic
- **NO gap senza evidence_strength score**
- **NO category "ignore" silently** — sempre log motivo
- **NO Love-Hate-Want senza review_id** — propaga anti-hallucination

## Reference

- `research/research-summary.md` RQ5 — fonte methodology
- `skills/gap-finder/SKILL.md` — implementazione
- `references/competitor-analysis-frameworks-2026.md` — framework routing per user.role
- `references/dossier-anatomy.md` — output rendering downstream
