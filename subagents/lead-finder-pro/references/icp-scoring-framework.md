# ICP Scoring Framework — `/lead-finder-pro`

> Reference per skill `icp-scoring`. Tre template per industry (SaaS B2B 60/40, Agency 50/50, eCommerce 70/30) + signal decay 50%/mese + grade band fissi (DECISION-006, DECISION-007). Sorgente: NotebookLM Q3 (Breadcrumbs + IntentDepth 2026 frameworks).

## Modello hybrid (rules + ML)

In 2026 il default per SaaS B2B mature è **hybrid scoring**:

- **Rules layer (fit)**: encoded da RevOps; firmografico/demografico stabile
- **ML layer (behavior + timing)**: gradient-boosting su signal high-velocity

Per `/lead-finder-pro` (audience non-developer Learnn) implementiamo solo il **rules layer**: ML è un livello v2, non v1. Behavioral signal vengono trattati come bonus/malus rules-based.

## Le 4 signal bucket

Modello completo richiede 4 signal categories per evitare scoring "asymmetric":

1. **Firmographic** (company fit): industry, revenue, employee count, geo
2. **Technographic** (stack fit): tool che il prospect usa già (Salesforce, HubSpot, ecc.)
3. **Behavioral first-party** (intent diretto): demo request, trial signup, pricing visit
4. **Intent third-party** (research esterna): Bombora, G2 activity, news mentions

## Template 1 — SaaS B2B 60/40 (default sales-led)

**Quando usarlo**: SaaS B2B sales-led motion, target enterprise/mid-market 50-500 employees, ICP basato su title + industry + company size.

| Categoria | Signal | Peso |
|-----------|--------|------|
| **Fit demografico** | VP / C-level title | +15 |
| | Director title | +10 |
| | Manager title | +5 |
| | Individual contributor | +0 |
| **Fit firmografico** | Target industry (SaaS, FinTech, MarTech) | +15 |
| | Adjacent industry (eCommerce, Agency) | +8 |
| | Out-of-ICP industry | -10 |
| | Company size 50-500 | +15 |
| | Company size 10-50 | +10 |
| | Company size 500+ | +5 |
| | Company size <10 (solo SMB-ICP) | +5 |
| **Fit technographic** | Uses target stack (es. Salesforce + HubSpot) | +10 |
| | Uses competitor stack | +5 (potential switcher) |
| | No tech detected | 0 |
| **Behavioral first-party** | Demo request | +25 |
| | Free trial signup | +15 |
| | Pricing page visit (≤7 giorni) | +10 |
| | Multiple page visits same session | +5 |
| **Intent third-party** | Bombora intent spike (high) | +15 |
| | G2 category research | +10 |
| | News mention "hiring marketing" | +5 |
| **Negative** | Competitor employee | -40 |
| | Student / job seeker | -40 |
| | Unsubscribed | -25 |
| | Bounce email | -15 |
| | Job-change <30 giorni (settling in) | -10 |

**Split**: Fit ~60 punti possibili (demo+firmo+techno) / Behavior ~40 punti (1st + 3rd party). Negative malus override.

## Template 2 — Agency 50/50 (relationship-driven)

**Quando usarlo**: digital agency, consultancy, professional services. Lead "fit" matters quanto "relationship signal" (warm intro, mutual contacts, brand fit).

| Categoria | Signal | Peso |
|-----------|--------|------|
| **Fit demografico** | Founder / Owner / CEO | +15 |
| | Marketing leader | +10 |
| | Operational leader | +5 |
| **Fit firmografico** | Service-fit company (es. SaaS for content agency) | +15 |
| | Adjacent fit | +5 |
| | Out-of-fit | -15 |
| | Revenue tier match | +10 |
| **Relationship signal** | Mutual LinkedIn contacts (≥3) | +15 |
| | Same alumni / community | +10 |
| | Mentioned by current client | +20 |
| | Brand alignment (values, mission) | +10 |
| **Behavioral** | Consultation request | +25 |
| | Case study download | +15 |
| | Newsletter subscriber 3+ months | +10 |
| **Negative** | Already client of competitor agency | -30 |
| | Bad culture fit (review research) | -20 |
| | Unsubscribed | -25 |

**Split**: Fit ~50 punti / Relationship+Behavior ~50 punti.

## Template 3 — eCommerce 70/30 (firmografico-driven)

**Quando usarlo**: B2B SaaS che vende a eCommerce merchants, agency eCommerce, marketing platform per shop. Il fit firmografico (volume, platform, revenue tier) domina.

| Categoria | Signal | Peso |
|-----------|--------|------|
| **Fit firmografico** | Volume orders/month tier match | +20 |
| | Revenue tier match | +15 |
| | Platform fit (Shopify, WooCommerce, Magento) | +15 |
| | Geo fit | +10 |
| | Multi-store / Headless | +5 |
| **Fit demografico** | eCommerce manager / Director eCom | +10 |
| | Founder eCommerce | +10 |
| | CMO multi-channel | +5 |
| **Behavioral** | Demo request | +20 |
| | Calculator/ROI tool used | +10 |
| | Pricing page visit | +10 |
| **Intent third-party** | Hiring eCom roles | +5 |
| | Recent platform migration mention | +10 |
| **Negative** | Out-of-platform fit | -20 |
| | Volume below tier | -15 |
| | Unsubscribed | -25 |

**Split**: Firmografico ~70 punti / Behavior+Intent ~30 punti.

## Grade bands (fissi cross-template)

| Grade | Range | Action |
|-------|-------|--------|
| **A — Hot** | 90-100 | Immediate sales intervention. Full personalized outreach + manual review |
| **B — Warm** | 75-89 | Priority follow-up. Automated personalized sequence |
| **C — Cold/Nurture** | 50-74 | Automated nurture sequence (newsletter, content drip) |
| **D — Disqualified** | <50 | Filter out. NO outreach. Suppression list candidate |

## Signal decay 50%/mese (DECISION-007)

Behavioral e intent signal **decadono** col tempo. Default: 50% mensile.

### Formula

```text
score_decayed_signal = original_signal_points × (decay_rate ^ months_elapsed)
```

Dove:

- `decay_rate = 0.5` (50% mensile)
- `months_elapsed = (now - enriched_at) / 30`

### Esempio numerico

Lead Mario Rossi, VP Marketing SaaS B2B:

- Enriched 2026-01-15 con +25 demo request
- Re-scored il 2026-04-29 → 3.5 mesi elapsed
- Decay: 25 × (0.5 ^ 3.5) = 25 × 0.088 = **+2.2 punti** (resto è decayed)

### Quando applicare

- **Sempre**: ad ogni run successivo al primo per lead esistente
- **Subagent**: Fase 3 scoring → check `_enriched_at`, applica decay su signal behavioral/intent
- **Fit signal NON decade**: VP title, industry, company size sono stabili

### Override

User può configurare `signal_decay_monthly` in config (es. 0.7 più conservativo, 0.3 più aggressivo).

## Strategy-change decay (DECISION-007 corollario)

Se utente cambia ICP description in config (es. da "SaaS B2B" a "MarTech only"), il subagent:

1. Detect change tra `icp.description` precedente vs nuovo
2. Warning all'utente: "ICP cambiato. Score storici potrebbero non essere validi. Vuoi full re-score?"
3. Se sì → ricalcola score per tutti i lead con nuovo template
4. Se no → mantieni score esistente ma flag `_score_stale: true`

## Negative signal handling

### Auto-applied

| Signal | Penalty |
|--------|---------|
| Unsubscribed (in suppression list) | -25 |
| Hard bounce email | -15 |
| Job-change <30 giorni | -10 (settling in) |
| Competitor employee detected | -40 |

### User-defined

User può aggiungere in `config.md`:

```yaml
scoring:
  custom_negative_signals:
    - signal: "is_recruiter"
      penalty: -30
    - signal: "company_in_blocklist"
      penalty: -50
```

## Output format scoring (per altri skill)

Skill `icp-scoring` produce per ogni lead:

```json
{
  "lead_id": "uuid",
  "score": 87,
  "grade": "B",
  "score_breakdown": {
    "fit_demo": 15,
    "fit_firmo": 30,
    "fit_techno": 5,
    "behavior_first": 25,
    "behavior_third": 10,
    "negative": 0,
    "decay_applied": 0.5,
    "raw_total": 87
  },
  "template_used": "saas_b2b_60_40",
  "scored_at": "2026-04-30T08:30:00Z"
}
```

## Quando custom invece dei 3 template

Se il business utente non rientra in SaaS/Agency/eCom, può scegliere "Custom" in Q8 discovery → il subagent:

1. Carica template SaaS B2B 60/40 come base
2. Suggerisce all'utente di editare `<memory>/icp_scoring_custom.md` con tabella pesi personalizzata
3. Fornisce skeleton: 5 categorie (fit-demo, fit-firmo, fit-techno, behavior-1st, behavior-3rd) + negative
4. Total target ~100 punti (per coerenza grade band 90-100/75-89/etc.)

## Validation checks

Skill `icp-scoring` esegue prima di applicare template:

- [ ] Somma pesi positivi possibili ≈ 100 (tolerance ±10)
- [ ] Somma pesi negativi total ≥ -50 (per consentire D grade)
- [ ] Almeno 1 signal per ognuna delle 5 categorie (no asymmetric model)
- [ ] Decay rate 0 < x < 1
- [ ] Grade band thresholds monotonic (A>B>C>D)

Se validation fail → warning utente + suggerisci fix.

## Source

- IntentDepth ICP framework 2026: <https://intentdepth.com/blog/b2b-lead-qualification-framework-icp>
- Breadcrumbs lead scoring 2026: <https://breadcrumbs.io/blog/b2b-lead-scoring/>
- NotebookLM `3b40733b` Q3 sintesi
