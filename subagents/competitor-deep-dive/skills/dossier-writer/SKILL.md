---
name: dossier-writer
description: Renderizza output finale deterministico — dossier_<slug>.md per N competitor (max 1500 parole, target 700-900) + synthesis.md cross-competitor (max 1000) + opportunities.md top 3 raccomandazioni rankate (max 800). Word budget hard-cap, anti-monolite enforced. Ogni numero ha source URL, ogni claim ha citazione (review_id + quote). Template Jinja2 deterministico. Da usare ULTIMO step pipeline, dopo positioning+tov+reviews+gap-finder.
when_to_use: Pipeline `/competitor-deep-dive` Fase 5 (rendering finale). Anche standalone se hai pre-existing JSON artefatti da render. Anche per re-render con word budget diverso (es. exec summary 500 parole vs deep dive 1500).
allowed-tools: Read Write Bash(python:*)
---

# Dossier Writer

Trasforma tutti gli artefatti pipeline in markdown report deterministico — 1 dossier per competitor + synthesis cross-competitor + opportunities. Word budget hard-cap, anti-pattern enforced.

## When to use

Attivare quando:

- Pipeline `/competitor-deep-dive` Fase 5 — input: positioning + tov + reviews + gap-matrix per N competitor
- Standalone re-render: hai già artefatti JSON, vuoi solo nuovo render markdown (es. word budget diverso)
- Multi-output: stesso dataset → 1× exec brief + 1× deep technical
- Update incrementale: re-run dossier per 1 competitor (positioning aggiornato)

Non attivare se:

- Mancano artefatti per ≥1 competitor (errore upstream — completa pipeline prima)
- `gap-matrix.json` mancante (synthesis + opportunities richiedono gap insights)
- Solo Quick scan + 1 competitor (synthesis vuota — skip synthesis, render solo dossier)

## Prerequisiti

- `output/positioning_<slug>.json` per N competitor
- `output/tov_<slug>.json` per N competitor (può avere `insufficient_evidence` per alcuni)
- `output/reviews_<slug>.json` per N competitor (idem)
- `output/gap-matrix.json` (output gap-finder)
- `output/cross_competitor_patterns.json` (output Fase 3 main agent)
- Reference `references/dossier-anatomy.md` accessibile

## Instructions

### Fase 1 — Load artefatti + validate

```python
def load_artifacts(slug):
    return {
        "positioning": json.load(open(f"output/positioning_{slug}.json")),
        "tov": json.load(open(f"output/tov_{slug}.json")) if exists else None,
        "reviews": json.load(open(f"output/reviews_{slug}.json")) if exists else None
    }

def validate_artifacts(artifacts):
    if not artifacts["positioning"]: return {"valid": False, "reason": "positioning required"}
    return {"valid": True, "completeness": calc_completeness(artifacts)}
```

`calc_completeness`: ritorna `100` se tutti i 3 sono valid + non insufficient_evidence; `66` se manca tov OR reviews; `33` se solo positioning.

### Fase 2 — Render dossier per competitor

```bash
python scripts/dossier_render.py \
  --slug make \
  --positioning output/positioning_make.json \
  --tov output/tov_make.json \
  --reviews output/reviews_make.json \
  --gap-matrix output/gap-matrix.json \
  --baseline-from-config \
  --word-budget-dossier 1500 \
  --output-md research/dossier_make.md
```

Lo script (Jinja2 template inline):

```jinja2
# {{ competitor.name }}

> **TL;DR (50-75 parole)**: {{ tldr_oneliner }}
> - {{ tldr_bullet_1 }}
> - {{ tldr_bullet_2 }}
> - {{ tldr_bullet_3 }}

## Positioning + Value Prop

- **Tagline**: "{{ positioning.tagline }}" ([source]({{ positioning.tagline_source.url }}))
- **Value prop**: "{{ positioning.value_prop }}" ([source]({{ positioning.value_prop_source.url }}))
- **ICP inferred**: {{ positioning.icp_inferred }}
  - Evidence: {% for e in positioning.icp_evidence %}"{{ e.quote }}" ([{{ e.url }}]({{ e.url }})){% if not loop.last %}; {% endif %}{% endfor %}

**3 differentiators**:
{% for d in positioning.differentiators[:3] %}
{{ loop.index }}. **{{ d.claim }}** — "{{ d.evidence[0].quote }}" ([{{ d.evidence[0].url }}]({{ d.evidence[0].url }}))
{% endfor %}

## Tone of Voice

{% if tov.insufficient_evidence %}
> ⚠️ ToV unmeasurable — corpus too small ({{ tov.corpus_size_words }} words, min 200 required). Suggerimento: {{ tov.suggestion }}
{% else %}
**Scores 1-5 (Nielsen Norman 4-dim)**:

| Dim | Score | Label |
|-----|-------|-------|
| Formal↔Casual | {{ tov.scores.formal_casual.score }} | {{ tov.scores.formal_casual.label }} |
| Funny↔Serious | {{ tov.scores.funny_serious.score }} | {{ tov.scores.funny_serious.label }} |
| Respectful↔Irreverent | {{ tov.scores.respectful_irreverent.score }} | {{ tov.scores.respectful_irreverent.label }} |
| Enthusiastic↔Matter-of-fact | {{ tov.scores.enthusiastic_matter_of_fact.score }} | {{ tov.scores.enthusiastic_matter_of_fact.label }} |

**Evidence (sample 1 quote per dim)**:
{% for dim, data in tov.scores.items() %}
- **{{ dim }}**: "{{ data.evidence[0].quote }}" ({{ data.evidence[0].metric }}, [{{ data.evidence[0].url }}]({{ data.evidence[0].url }}))
{% endfor %}

**Derived metrics**:
- Jargon density: {{ tov.derived_metrics.jargon_density_pct }}%
- Pronoun ratio (we/you): {{ tov.derived_metrics.pronoun_ratio_we_you }}
- Avg sentence length: {{ tov.derived_metrics.avg_sentence_length_words }} parole
- CTA style: {{ tov.derived_metrics.cta_style }}
- Exclamation density: {{ tov.derived_metrics.exclamation_density_per_100w }} per 100 parole
{% endif %}

## Reviews Sentiment

{% if reviews.insufficient_evidence %}
> ⚠️ Reviews insufficient — {{ reviews.reason }}. Fallback suggerito: {{ reviews.fallback_suggestion }}
{% else %}
**Sentiment breakdown** ({{ reviews.total_reviews_scraped.total }} reviews scraped via {{ reviews.actor_used }}):

- Positive: {{ reviews.sentiment_breakdown.weighted_avg.positive_pct }}%
- Neutral: {{ reviews.sentiment_breakdown.weighted_avg.neutral_pct }}%
- Negative: {{ reviews.sentiment_breakdown.weighted_avg.negative_pct }}%

**Top 5 strengths**:
{% for s in reviews.top_strengths[:5] %}
{{ loop.index }}. **{{ s.theme }}** ({{ s.frequency }} mentions) — "{{ s.evidence[0].quote }}" ([{{ s.evidence[0].review_id }}]({{ s.evidence[0].url }}))
{% endfor %}

**Top 5 weaknesses**:
{% for w in reviews.top_weaknesses[:5] %}
{{ loop.index }}. **{{ w.theme }}** ({{ w.frequency }}) — "{{ w.evidence[0].quote }}" ([{{ w.evidence[0].review_id }}]({{ w.evidence[0].url }}))
{% endfor %}

**Top 3 JTBD**:
{% for j in reviews.top_jtbd[:3] %}
- {{ j.outcome }} ({{ j.frequency }} mentions)
{% endfor %}

**Love / Hate / Want**:
- Love: {% for l in reviews.love_hate_want.love[:3] %}{{ l.text }}{% if not loop.last %}, {% endif %}{% endfor %}
- Hate: {% for h in reviews.love_hate_want.hate[:3] %}{{ h.text }}{% if not loop.last %}, {% endif %}{% endfor %}
- Want: {% for w in reviews.love_hate_want.want[:3] %}{{ w.text }}{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}

{% if config.analysis.depth == 'deep' %}
## Tech & Funding

- **Tech stack** (BuiltWith): {{ tech.stack | join(', ') }}
- **Last funding round**: {{ funding.last_round.type }} {{ funding.last_round.amount_usd }}M ({{ funding.last_round.date }})
- **Total raised**: {{ funding.total_raised_usd }}M
- Source: [Crunchbase]({{ funding.crunchbase_url }})
{% endif %}

## Gap vs cliente baseline

{% for gap in gap_matrix.gaps_for_competitor(competitor.name)[:5] %}
{{ loop.index }}. **{{ gap.title }}** (score {{ gap.gap_score }}, category {{ gap.category }}) — {{ gap.description }}
{% endfor %}
```

### Fase 3 — Word budget hard-cap enforce

Dopo render template:

```python
def enforce_word_budget(md_content, max_words):
    word_count = len(md_content.split())
    if word_count > max_words * 1.05:  # 5% tolerance
        log.warning(f"Dossier exceeds budget ({word_count} > {max_words}). Truncating...")
        md_content = truncate_smart(md_content, max_words)  # truncate optional sections (Tech&Funding) first
        return md_content + f"\n\n> ⚠️ Truncated to fit {max_words}-word budget. Full data in artefatti JSON."
    return md_content
```

Hard cap (anti-pattern #5):
- Dossier per competitor: 1500
- Synthesis: 1000
- Opportunities: 800

### Fase 4 — Render synthesis.md

Da `cross_competitor_patterns.json` + `gap-matrix.json`:

```markdown
# Synthesis — Pattern Cross-Competitor

> Analisi {{ N }} competitor: {{ competitors_list }}.
> Cliente baseline: {{ baseline.tagline }}

## Common positioning tropes

{% for trope in patterns.common_positioning %}
- {{ trope.theme }} (presente in {{ trope.frequency }}/{{ N }} competitor)
{% endfor %}

## Common Tone of Voice pattern

{{ patterns.tov_convergence_summary }}

> **Blue ocean ToV hint**: {{ patterns.tov_blue_ocean_hint }}

## Common gap (cosa nessuno fa)

{% for gap in gap_matrix.universal_want %}
- {{ gap.theme }} ({{ gap.frequency_total }} customer mentions across {{ gap.competitors_with_no_solution | length }} competitor senza soluzione)
{% endfor %}

## Customer Love-Hate-Want overlap cross-competitor

| Theme | Universal Love | Universal Hate | Universal Want |
|-------|----------------|----------------|----------------|
{% for theme in patterns.lhw_overlap %}
| {{ theme.name }} | {{ theme.love_count }} | {{ theme.hate_count }} | {{ theme.want_count }} |
{% endfor %}

## Implicazioni strategiche per cliente

1. {{ implication_1 }}
2. {{ implication_2 }}
3. {{ implication_3 }}
```

### Fase 5 — Render opportunities.md

Top 3 da `gap-matrix.json` `categorized.quick_wins[:1] + strategic_bets[:2]`:

```markdown
# Top 3 Opportunità Strategiche

> Selezionate da gap-finder: 1 quick win + 2 strategic bet, rankate per impact × ease.

## 1. {{ reco_1.title }} (Quick Win)

**Score**: {{ reco_1.gap_score }} (impact {{ reco_1.impact }} × ease {{ reco_1.ease }} × evidence {{ reco_1.evidence_strength }} / {{ reco_1.complexity_penalty }})

**Cosa fare**: {{ reco_1.description }}

**Owner suggerito**: {{ reco_1.owner_suggested }}

**Success metric**: {{ reco_1.success_metric }}

**Due date**: {{ reco_1.due_date }}

**7-day next step**: {{ reco_1.next_step_7_days }}

**Evidence**:
{% for e in reco_1.evidence %}
- {{ e.competitor }}: "{{ e.quote }}" ({{ e.source_or_review_id }})
{% endfor %}

## 2. {{ reco_2.title }} (Strategic Bet)

...

## 3. {{ reco_3.title }} (Strategic Bet)

...
```

### Fase 6 — Anti-pattern check

Pre-write final validation:

```python
def antipattern_check(md_content, artifacts):
    issues = []
    # Check 1: claim senza citazione
    sentences = re.split(r'[.!?]+', md_content)
    for s in sentences:
        if has_factual_claim(s) and not has_citation(s):  # heuristic
            issues.append(f"Claim senza citazione: {s[:100]}")
    # Check 2: word budget
    if len(md_content.split()) > word_budget * 1.05:
        issues.append(f"Word budget exceeded: {len(md_content.split())} > {word_budget}")
    # Check 3: review_id presence (per claim sentiment)
    if "sentiment" in md_content.lower() and not re.search(r'g2-\d+|tp-\d+|cap-\d+', md_content):
        issues.append("Sentiment claim senza review_id reference")
    return issues
```

Se issues → log warning + return content con `> ⚠️ ANTI-PATTERN ISSUES DETECTED:` block all'inizio.

### Fase 7 — Output sync (delegata a main agent)

`dossier-writer` produce solo markdown locale in `research/`. Il main agent gestisce sync verso google-personal / slack / notion (Fase 6 main agent).

## Output examples

Vedi blocco template Jinja2 sopra. Esempio dossier renderizzato:

```markdown
# Make

> **TL;DR (62 parole)**: Make si posiziona come visual no-code workflow builder per technical operators mid-market, con free tier aggressivo (1000 ops/month). Casual+Serious tone, 62% review positive. Strength: drag-drop UI; Weakness: pricing scaling. Want primary: AI-assisted suggestion. Gap vs cliente: AI engine debole, Mid-market sweet spot conteso.
> - Visual no-code builder, 10,000+ apps integration
> - Free tier 1k ops/month, paid $9-29
> - Top JTBD: build automation 10x faster than manual

## Positioning + Value Prop
- **Tagline**: "Automate work, anywhere — visually" ([source](make.com))
- ...
```

## Anti-pattern

- **NO claim senza citazione** — check pre-write enforce
- **NO dossier monolite >5000 parole** — word budget hard-cap forced
- **NO numero senza source URL** — heuristic check
- **NO copy-paste da artefatti senza filtering** — sempre top 5 strengths/weaknesses (no top 100)
- **NO synthesis vuota** se cross_competitor_patterns.json esiste — sempre output
- **NO opportunities senza 7-day step** — sempre actionable
- **NO render se gap-matrix mancante** — error + suggest run gap-finder

## Edge cases

- **1 competitor only** (Quick scan): skip synthesis.md, render solo dossier + opportunities (single-competitor opportunities)
- **Insufficient evidence per competitor**: render dossier comunque con sezioni `> ⚠️` placeholder + suggerimento espansione
- **Word count exceeds 1.05× budget**: truncate smart (drop Tech&Funding section first se non Deep tier; poi drop ICP evidence beyond 1; poi shrink Reviews top 3 instead of 5)
- **Gap-matrix con 0 universal want**: skip "blue ocean" section synthesis
- **Tutti competitor `insufficient_evidence` reviews**: synthesis senza Reviews insights, fallback solo positioning + ToV (warn utente)
- **Multi-language output requirement** (cliente IT vuole IT): translate template Jinja2 output (Italian variant) — feature future v1.1

## Reference

- `references/dossier-anatomy.md` — structure "wow" + word budget + signal/noise
- `research/research-summary.md` RQ7 — anatomia dossier 700-900 parole pattern
