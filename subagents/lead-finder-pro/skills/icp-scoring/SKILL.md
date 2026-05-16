---
name: icp-scoring
description: Scora ogni lead 0-100 secondo template industry (SaaS B2B 60/40 fit/behavior, Agency 50/50, eCommerce 70/30) + signal decay 50%/mese. Assegna grade A/B/C/D (Hot/Warm/Cold/Disqualified) con thresholds 90-100/75-89/50-74/<50. Auto-applica negative signal (-25 unsubscribe, -40 competitor). Da usare quando hai lead enriched e devi prioritizzare per outbound, audit qualità lista esistente, segmentation campagna.
when_to_use: Lead enriched JSON pronto per scoring, audit qualità lista CRM esistente, segmentation campaign outbound, recalc score lead vecchi (signal decay), output skill waterfall-enrichment da scorare
allowed-tools: Read Write Bash(python:*)
---

# ICP Scoring

Trasforma lead enriched in lead scorati con grade priority bucket. Modello hybrid rules + decay logic, configurabile per 3 industry pattern + custom.

## When to use

Attivare quando:

- Lead list arricchito JSON pronto per scoring (output skill `waterfall-enrichment`)
- Audit qualità lista CRM esistente (re-scoring lead vecchi)
- Segmentation campaign outbound (Hot vs Warm vs Cold buckets)
- Recalculation score con signal decay (lead `_enriched_at` > 30 giorni)
- User chiede "perché questo lead è Hot/Cold?"

Non attivare se:

- Lead non sono ancora enriched (manca `email`, `role`, `industry`, `company_size`)
- ICP description vuoto in config (chiedi prima `/lead-finder-pro` discovery)
- Volume <10 lead (manuale è più rapido)

## Prerequisiti

- `<memory>/config.md` esiste con `icp.industry_pattern` + `icp.description`
- Lead JSON con almeno campi: `name, company, role, email, industry, company_size`
- Reference `references/icp-scoring-framework.md` accessibile

## Instructions

### Fase 1 — Load template

Leggi config:

```bash
python scripts/discovery_check.py --memory-path "<memory>/config.md"
```

Estrai `scoring.template` (saas_b2b_60_40 | agency_50_50 | ecommerce_70_30 | custom).

Carica template corrispondente da `references/icp-scoring-framework.md`. Se "custom", carica `<memory>/icp_scoring_custom.md` (l'utente l'ha editato).

### Fase 2 — Validate template

Check sui pesi del template:

- [ ] Somma pesi positivi possibili ≈ 100 (tolerance ±10)
- [ ] Pesi negativi total ≥ -50
- [ ] Almeno 1 signal per categoria (fit-demo, fit-firmo, fit-techno, behavior-1st, behavior-3rd)
- [ ] Decay rate 0 < x < 1
- [ ] Grade band thresholds monotonic

Se fail → warning utente + skip scoring.

### Fase 3 — Score per lead (loop)

Per ogni lead:

1. Calcola **fit signals** (firmografico + demografico + technographic):
   - Match rule per role/title → punti
   - Match rule per industry → punti
   - Match rule per company_size → punti
   - Match rule per technographic stack se presente → punti

2. Calcola **behavior signals** (1st-party + 3rd-party):
   - Demo request +25 (se presente in `intent_signals`)
   - Pricing visit ≤7 giorni +10
   - Newsletter subscriber ≥3 mesi +10
   - Bombora intent +15 / G2 research +10

3. **Apply signal decay**:

   ```python
   months_elapsed = (now - lead._enriched_at) / 30
   for signal in behavior_signals:
       signal.points *= (decay_rate ** months_elapsed)
   ```

   Solo behavior+intent decay. Fit signal NO decay.

4. Calcola **negative signals**:
   - `-25` se unsubscribed
   - `-40` se competitor employee
   - `-15` se hard bounce email
   - `-10` se job-change <30 giorni

5. **Total score** = sum(fit) + sum(behavior_decayed) + sum(negative)
6. Cap range [0, 100] (truncation)
7. Assegna **grade**:
   - 90-100 → A (Hot)
   - 75-89 → B (Warm)
   - 50-74 → C (Cold)
   - <50 → D (Disqualified)

### Fase 4 — Output

Aggiungi a ogni lead JSON:

```json
{
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

### Fase 5 — Report

Stampa summary:

```text
Scoring done. 200 lead → 25 Hot (A), 60 Warm (B), 80 Cold (C), 35 Disqualified (D).
Template: saas_b2b_60_40. Decay applied: 50%/mese.
Average score: 64. Recommended outreach: tutti Hot + Warm prioritari (85 lead).
```

## Examples

### Esempio 1 — SaaS B2B Hot lead

**Input**:

```json
{
  "name": "Sara Bianchi",
  "company": "Nimbus FinTech",
  "role": "VP Marketing",
  "industry": "FinTech B2B SaaS",
  "company_size": "51-200",
  "country": "Italy",
  "intent_signals": ["Series A €15M Feb 2026", "hiring 3 marketing roles"],
  "_enriched_at": "2026-04-29T10:00:00Z"
}
```

**Template**: `saas_b2b_60_40`

**Score breakdown**:

- VP title → +15
- Target industry FinTech → +15
- Company size 51-200 → +15
- Series A funding intent → +15 (3rd-party intent)
- Hiring marketing roles → +10 (3rd-party intent)
- No demo/trial/pricing visit → 0 behavior 1st-party
- No technographic data → 0 (skip)
- No negative signals → 0
- **Total raw**: 70

Wait: 70 → grade C? Sì. Senza behavior 1st-party (demo/trial/pricing), il score resta solo su fit + 3rd-party intent. Per arrivare a Hot, il lead dovrebbe aver fatto un'azione first-party.

**Output**: Grade C (Cold/Nurture). Suggerimento subagent: "Lead 'Sara' è ICP-fit perfetto, ma manca segnale first-party (demo/trial/pricing visit). Suggerisco nurture sequence content-driven prima di outreach diretto."

### Esempio 2 — Stesso lead 3 mesi dopo (decay applied)

Stesso lead ma `_enriched_at: 2026-01-29` (3 mesi fa). Decay rate 0.5.

- Behavior+intent points = 25 (era 15+10) → decayed: 25 × (0.5^3) = 25 × 0.125 = **3.1**
- Fit points unchanged: 45
- **Total**: 45 + 3 = **48** → Grade D (Disqualified)

Subagent: "Lead 'Sara' decayed da score 70 a 48. Re-enrichment necessario per refresh signal. Attiva job-change check."

### Esempio 3 — eCommerce template

**Input**:

```json
{
  "name": "Marco Rossi",
  "company": "ShopFast IT",
  "role": "eCommerce Manager",
  "industry": "Retail eCommerce",
  "company_size": "11-50",
  "country": "Italy",
  "platform": "Shopify",
  "monthly_orders": 5000,
  "intent_signals": ["Demo request 2026-04-25"],
  "_enriched_at": "2026-04-29"
}
```

**Template**: `ecommerce_70_30`

- Volume orders 5000/mese → tier match +20
- Platform Shopify → +15
- Geo Italy (target EU) → +10
- eCom Manager → +10
- Demo request → +20
- **Total**: 75 → Grade B (Warm)

## Gotchas

- 🔴 **Decay calculation senza `_enriched_at`**: se field manca, no decay applied → score può essere over-stated. Subagent fa fallback `_enriched_at = scored_at` (no decay) e flag warning.
- 🔴 **Custom template non validato**: se utente edita `<memory>/icp_scoring_custom.md` con somma >100 o thresholds non-monotonic → validation fail. Mostra error preciso.
- 🔴 **Mancanza technographic data**: per template SaaS B2B 60/40 il signal `fit_techno` può essere 0 spesso (non sempre disponibile da Hunter/Apollo). Documentato come "expected", non bug.
- 🟡 **Score fluctuation tra run**: applicando decay ad ogni run, lo score di stesso lead cambia. NON è bug — è feature. Il subagent stampa "score changed from X to Y due to signal decay" per trasparenza.
- 🟡 **Negative signal override**: -40 competitor può non bastare a portare score sotto 50 se fit è 90+. Cap negative a sum(positive) per evitare score >100. Segnala via `_grade_override` se applicato.
- 🟢 **3-template coverage**: se utente è eg. industria diversa (Legal SaaS, Health B2B), suggerisci "Custom" + skeleton SaaS B2B come base.
- 🟢 **Re-scoring batch**: per recalc su 500+ lead, esegui in batch 50 con checkpoint, evita timeout.

## Scripts

- `scripts/score.py` (TODO Fase C.3): wrapper CLI per scoring batch (`python scripts/score.py --input leads.json --template saas_b2b_60_40 --output scored.json`). Implementa decay + validation.

## References

- [references/icp-scoring-framework.md](../../references/icp-scoring-framework.md): 3 template completi + decay formula + grade band

## Crediti

Skill v1 originale `<pack-root>/skills/webinar-2/lead-enrichment/SKILL.md` Fase 3 (scoring) → questa è la versione v2 estesa con 3 template, decay, custom support.
