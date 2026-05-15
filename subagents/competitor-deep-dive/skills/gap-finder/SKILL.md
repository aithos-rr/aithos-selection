---
name: gap-finder
description: Costruisce gap matrix 6-dim (feature/segment/geo/ToV/format/pricing) tra cliente baseline e N competitor analizzati. Mining Love-Hate-Want vs JTBD da reviews. Apply ranking formula gap_score = (impact × ease × evidence_strength) / max(1, complexity_penalty). Top 5-10 gap rankati con narrative actionable. Auto-routing framework per user.role (founder=SWOT+Porter5F+StrategyCanvas, marketing=StrategyCanvas+PositioningMap+ToVDiff, pm=JTBD+FeatureMatrix+ReviewsMining, sales=FeatureMatrix+CPM+battlecard, analyst=CPM+JTBD+overlay). BLOCK se baseline incompleta. Da usare dopo positioning+tov+reviews per tutti competitor.
when_to_use: Pipeline `/competitor-deep-dive` Fase 4 (gap analysis cross-competitor + baseline). Anche standalone con baseline + 1 competitor JSON pre-existing per quick gap snapshot. Anche per pre-roadmap planning input.
allowed-tools: Read Write Bash(python:*)
---

# Gap Finder

Trasforma N positioning/tov/reviews JSON + cliente baseline in gap matrix 6-dim rankata. Mining Love-Hate-Want vs JTBD. Output `gap-matrix.json` (machine-readable) + `gap-narrative.md` (storia actionable).

## When to use

Attivare quando:

- Pipeline `/competitor-deep-dive` Fase 4 — input: tutti gli artefatti per N competitor + cliente baseline
- Standalone con baseline + 1 competitor JSON pre-existing (snapshot rapido)
- Pre-roadmap planning: identificare top 5 feature gap che il PM deve discutere
- Pre-fundraising: identificare 3 strategic bet defendable per pitch investor
- Pre-content brief: identificare keyword + ToV gap per repositioning

Non attivare se:

- `business.baseline` incompleto (manca tagline OR value_prop OR icp) — BLOCK
- 0 competitor analizzati (gap analysis impossibile)
- Profondità `quick` (skip cross-competitor gap, solo single dossier)

## Prerequisiti

- `<memory>/config.md` con `business.baseline` completo (tagline + value_prop + icp)
- Tutti `output/positioning_<slug>.json` per N competitor disponibili
- Tutti `output/tov_<slug>.json` per N competitor (skip se Quick scan)
- Tutti `output/reviews_<slug>.json` per N competitor (skip se insufficient_evidence flag)
- `<memory>/config.md` con `analysis.framework_routing[]` (auto-derived da user.role)

## Instructions

### Fase 1 — Validate baseline

```python
def validate_baseline(config):
    baseline = config.get("business", {}).get("baseline", {})
    required = ["tagline", "value_prop", "icp"]
    missing = [f for f in required if not baseline.get(f) or baseline[f].strip() == ""]
    if missing:
        return {"valid": False, "missing": missing,
                "error": f"Baseline mancante: {missing}. Definisci tutti 3 campi prima di procedere — gap analysis senza baseline è fake-news."}
    return {"valid": True, "baseline": baseline}
```

Se invalid → BLOCK + prompt utente. Anti-pattern #6 enforce.

### Fase 2 — Load artefatti

```bash
python scripts/gap_matrix_build.py \
  --baseline-from-config \
  --positioning-glob "output/positioning_*.json" \
  --tov-glob "output/tov_*.json" \
  --reviews-glob "output/reviews_*.json" \
  --output-matrix output/gap-matrix.json \
  --output-narrative output/gap-narrative.md
```

Lo script:
1. Legge config baseline
2. Carica tutti positioning/tov/reviews JSON
3. Filtra competitor con `stealth_detected: true` o `insufficient_evidence: true` su tutti i 3 dataset → segnalali ma non includere in matrix
4. Costruisce matrice 6-dim

### Fase 3 — Build matrix 6-dim

Per ogni dimensione, mappa cliente baseline + N competitor:

#### Dim 1: Feature

- Da positioning.json `differentiators[]`
- Da reviews.json `top_strengths[].theme` + `love[]`
- Inferisci feature set per ogni competitor
- Confronta con baseline (anche feature implicit)
- Output: lista feature per competitor + flag "Cliente ha?" Y/N

#### Dim 2: Segment

- Da positioning.json `icp_inferred` + `icp_evidence`
- Estrai segments serviti (Mid-market, Enterprise, SMB, Solopreneur, etc.)
- Confronta con baseline ICP
- Output: lista segment × competitor + match con baseline

#### Dim 3: Geo

- Da positioning.json `pricing_summary` (USD vs EUR, geo-fenced)
- Da config `competitors_input[].domain` (.com vs .eu vs .it)
- Output: geo coverage per competitor + gap vs cliente target

#### Dim 4: ToV

- Da tov.json `scores` + `derived_metrics`
- Calcola distance vs baseline ToV (se baseline ha ToV scorato — opzionale)
- Identifica ToV "blue ocean" (dim dove tutti competitor convergono → opportunità altra dim)
- Output: ToV map + suggested differentiator

#### Dim 5: Format

- Da positioning.json scrape detect content format dominante
- Cerca: `/blog`, `/podcast`, `/youtube`, `/docs`, `/community`, webinar landing
- Output: format mix per competitor + gap

#### Dim 6: Pricing

- Da positioning.json `pricing_summary`
- Modello (subscription / usage / hybrid / call-only)
- Fascia (lowest_tier_usd, highest visibile)
- Confronta con baseline pricing strategy (se in config)

### Fase 4 — Mining Love-Hate-Want vs JTBD

Da reviews.json di tutti i competitor:

```python
all_love = [item for c in competitors for item in c.reviews.love_hate_want.love]
all_hate = [item for c in competitors for item in c.reviews.love_hate_want.hate]
all_want = [item for c in competitors for item in c.reviews.love_hate_want.want]

# Cluster cross-competitor
clustered_love = cluster_themes(all_love)  # cosa tutti adorano
clustered_hate = cluster_themes(all_hate)  # cosa tutti odiano (opportunità)
clustered_want = cluster_themes(all_want)  # cosa tutti chiedono (blue ocean)

all_jtbd = [j for c in competitors for j in c.reviews.top_jtbd]
clustered_jtbd = cluster_themes(all_jtbd)  # outcome dominanti
```

Identifica:
- **Universal Love** (cosa tutti hanno e customer adorano) → minimum bar per cliente
- **Universal Hate** (cosa tutti hanno e customer odiano) → opportunità "fix what they break"
- **Universal Want** (cosa nessuno offre e customer chiedono) → blue ocean
- **JTBD primary** (outcome più frequente) → check coerenza con baseline value_prop

### Fase 5 — Apply framework routing

Da config `analysis.framework_routing[]` (auto da user.role):

| user.role | Frameworks |
|-----------|-----------|
| `founder` | SWOT (per competitor + per cliente) + Porter 5F (industry-level) + Strategy Canvas (value curve) |
| `marketing` | Strategy Canvas (factor scoring) + Positioning Map 2x2 (visual) + ToV Diff |
| `pm` | JTBD comparison + Feature Matrix + Reviews mining (Love-Hate-Want primary) |
| `sales` | Feature Matrix + CPM (weighted) + Battlecard format |
| `analyst` | CPM (weighted) + JTBD + Multi-framework overlay |

Routing:
```python
if "swot" in framework_routing:
    swot = build_swot(competitors, baseline)
if "strategy_canvas" in framework_routing:
    canvas = build_strategy_canvas(competitors, baseline, factors=infer_factors(positioning, reviews))
if "positioning_map" in framework_routing:
    map_2x2 = build_positioning_map_2x2(competitors, baseline, axes=["Feature breadth", "Pricing"])
if "feature_matrix" in framework_routing:
    matrix = build_feature_matrix(competitors, baseline)
if "cpm" in framework_routing:
    cpm = build_cpm(competitors, baseline, csf=infer_csf(reviews))
if "jtbd" in framework_routing:
    jtbd_comp = build_jtbd_comparison(competitors, baseline)
```

### Fase 6 — Score gaps + ranking

Per ogni gap identificato (5-15 candidati):

```python
gap_score = (impact * ease * evidence_strength) / max(1, complexity_penalty)
```

Scale 1-5 per ogni componente:

- **impact**: quanto sposta lead/revenue per cliente se chiudo gap
  - 5 = transformational (es. blue ocean reco)
  - 4 = significant
  - 3 = moderate
  - 2 = marginal
  - 1 = trivial
- **ease**: quanto è facile chiuderlo
  - 5 = quick win <30gg
  - 4 = 30-90gg
  - 3 = 3-6 mesi
  - 2 = 6-12 mesi
  - 1 = 1+ anno
- **evidence_strength**: quanto è forte l'evidence (review count + JTBD frequency + cross-competitor consistency)
  - 5 = ≥3 source independent + cross-competitor consistent + JTBD primary
  - 4 = ≥2 source + 1 platform reviews ≥30 evidence
  - 3 = single source + reviews ≥10
  - 2 = inferred from positioning, no reviews evidence
  - 1 = speculative
- **complexity_penalty**: moltiplicatore se richiede stack overhaul
  - 1 = no overhaul (pure messaging change)
  - 2 = moderate (new feature + UX)
  - 3 = heavy (re-platform / new geo / new model)

Top gap (sort by `gap_score` descending). Categorize:

- **Quick wins** (impact ≥3 + ease ≥4): ranking 1-3
- **Strategic bets** (impact ≥4 + ease ≤3): ranking 4-7
- **Ignore** (impact ≤2 OR evidence_strength ≤2): drop dal report

### Fase 7 — Build gap-matrix.json

```json
{
  "client_baseline": {"tagline": "...", "value_prop": "...", "icp": "..."},
  "competitors_analyzed": ["Make", "n8n", "Zapier"],
  "framework_used": ["Strategy Canvas", "Positioning Map 2x2", "ToV Diff"],
  "matrix_6_dim": {
    "feature": {...},
    "segment": {...},
    "geo": {...},
    "tov": {...},
    "format": {...},
    "pricing": {...}
  },
  "love_hate_want_aggregated": {
    "universal_love": [{"theme": "Drag-drop UI", "competitors": ["Make", "n8n", "Zapier"], "frequency_total": 134}],
    "universal_hate": [...],
    "universal_want": [...]
  },
  "jtbd_primary_aggregated": [...],
  "gaps": [
    {
      "id": "gap-001",
      "dimension": "feature",
      "title": "AI-assisted workflow builder",
      "description": "AI suggestion engine per next module mancante in cliente, presente in 2/3 competitor (Make, Zapier) ma debole",
      "impact": 5, "ease": 3, "evidence_strength": 5, "complexity_penalty": 2,
      "gap_score": 37.5,
      "love_hate_want": "want",
      "jtbd_primary": "build automation 10x faster than manual",
      "category": "strategic_bet",
      "evidence": [
        {"competitor": "Make", "source": "make.com/ai", "quote": "..."},
        {"competitor": "Zapier", "review_id": "g2-9999", "quote": "Want AI to suggest next step automatically"}
      ],
      "next_step_7_days": "Internal workshop product team — define AI scope MVP entro venerdì"
    }
  ],
  "ranking": ["gap-001", "gap-007", "gap-003", "gap-005", "gap-002"],
  "categorized": {
    "quick_wins": ["gap-007", "gap-005"],
    "strategic_bets": ["gap-001", "gap-003"],
    "ignore": ["gap-008", "gap-009"]
  }
}
```

### Fase 8 — Write gap-narrative.md

Output narrativo (~1500 parole, leggibile):

```markdown
# Gap Analysis — <Cliente> vs <N> competitor

## Quick wins (impact ≥3 + ease ≥4)

### 1. <Gap title>
- **Score**: 25 (impact 5 × ease 5 / 1)
- **Cosa**: ...
- **Why**: evidence + JTBD context
- **7-day step**: cosa fare lunedì mattina
- **Owner suggerito**: Marketing / PM / Eng

### 2. ...

## Strategic bets (impact ≥4 + ease ≤3)

### 3. <Gap title>
- ...

## Ignore (low impact / low evidence)

- gap-008: speculative, no review evidence — ignora
- gap-009: trivial impact — ignora
```

## Output examples

Vedi gap-matrix.json sopra (success case con 3 competitor).

## Anti-pattern

- **NO gap analysis senza cliente baseline completo** — BLOCK + prompt
- **NO gap inventato senza evidence_strength score** — sempre score 1-5
- **NO ranking subjective** — sempre formula deterministic
- **NO category "ignore" silently** — sempre log motivo (low impact / low evidence)
- **NO mining Love-Hate-Want senza review_id** — propaga anti-hallucination da reviews-sentiment
- **NO framework forzato non in routing** — solo framework definiti per user.role

## Edge cases

- **0 competitor con reviews valide** (tutti `insufficient_evidence`): skip Love-Hate-Want, fallback positioning + ToV only
- **Baseline ToV non scorato** (cliente non ha ancora analyzed proprio ToV): skip dim ToV diff, suggest "run ToV su cliente prima"
- **Industry niche con 1 solo competitor**: gap matrix monolitica (no cross-competitor pattern), flag `single_competitor_warning`
- **Conflicting evidence cross-competitor**: flag `evidence_conflict` se 2 source diverse danno claim opposti
- **Geo mismatch**: cliente USA vs competitor EU-only → flag `geo_overlap_partial`, considera competitor secondario
- **JTBD primary baseline missing** (cliente non ha JTBD definito in config): infer da value_prop + suggest "definisci JTBD per validation"

## Reference

- `references/gap-analysis-methodology.md` — matrice 6-dim + ranking formula + Love-Hate-Want vs JTBD overlay
- `references/competitor-analysis-frameworks-2026.md` — when-to-use 7 framework
- `research/research-summary.md` RQ5 — gap methodology fonte
