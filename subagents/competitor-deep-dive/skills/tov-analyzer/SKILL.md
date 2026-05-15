---
name: tov-analyzer
description: Analizza Tone of Voice di un competitor su 4 dimensioni Nielsen Norman (Formal↔Casual, Funny↔Serious, Respectful↔Irreverent, Enthusiastic↔Matter-of-fact) con scoring 1-5 + 4 metriche derivate (jargon density %, pronoun ratio I-we/you, avg sentence length, CTA style imperativo vs invitante). Per ogni dim 3 evidence quotes obbligatori dal corpus. Anti-hallucination MANDATORY — se corpus <200 parole o <3 quotes per dim, output insufficient_evidence. Da usare in parallel a reviews-sentiment dopo positioning-mapper.
when_to_use: Pipeline `/competitor-deep-dive` Fase 2b (parallel a reviews-sentiment). Anche standalone per audit ToV cliente proprio (passa cliente come "competitor" per snapshot voice). Anche per A/B test pre-launch (compara variante A vs B di copy).
allowed-tools: Read Write Bash(python:*)
---

# Tone of Voice Analyzer

Estrae ToV di 1 competitor da corpus testuale (homepage + about + 5 blog post) e scora 4 dimensioni Nielsen Norman su scala 1-5 + 4 metriche derivate quantitative. Output `tov.json` deterministico, ogni score con 3 evidence quotes verbatim.

## When to use

Attivare quando:

- Pipeline `/competitor-deep-dive` Fase 2b — input: corpus aggregato da `positioning-mapper`
- Audit ToV cliente proprio (passa baseline come input) per consistency check
- A/B test pre-launch copy (compara 2 variant come 2 "competitor")
- Audit messaging dopo rebrand (re-run baseline vs nuovo corpus)

Non attivare se:

- `corpus_size_words < 200` → output `insufficient_evidence: true, reason: "corpus too small"`
- Profondità analisi `quick` in config (skip ToV per Quick scan)
- Competitor stealth flag (positioning-mapper ha già flagged)

## Prerequisiti

- Output `positioning-mapper` disponibile (`output/corpus_<slug>.txt`)
- Reference `references/tov-rubric-nielsen-norman.md` accessibile per rubric scoring
- Python script `tov_score.py` available per metriche quantitative

## Instructions

### Fase 1 — Load corpus

```bash
python scripts/tov_score.py --corpus output/corpus_<slug>.txt --output output/tov_<slug>.json
```

Lo script:
1. Legge corpus (testo aggregato homepage + about + blog post)
2. Conta parole totali
3. Se `< 200` → output `insufficient_evidence: true, reason: "corpus too small"` e exit
4. Tokenize sentence + words (NLTK-lite o regex)

### Fase 2 — Compute derived metrics (deterministic)

#### Jargon density %

```python
jargon_terms = ["API", "SDK", "SaaS", "B2B", "ROI", "KPI", "OKR", "SOC2", "GDPR", "OAuth", ...]  # ~50 acronyms tech business
jargon_count = sum(1 for w in words if w.upper() in jargon_terms)
jargon_density_pct = (jargon_count / total_words) * 100
```

Range: 0-100%. Casual: <5%, Formal/tech: >10%.

#### Pronoun ratio I-we / you

```python
i_we_count = sum(1 for w in words if w.lower() in ["i", "we", "us", "our"])
you_count = sum(1 for w in words if w.lower() in ["you", "your", "yours"])
pronoun_ratio_we_you = i_we_count / max(1, you_count)
```

Range: 0-∞. Customer-centric: <0.5. Brand-centric/Irreverent: >1.

#### Avg sentence length

```python
sentences = re.split(r'[.!?]+', corpus)
avg_sentence_length_words = sum(len(s.split()) for s in sentences) / len(sentences)
```

Range: typical 8-25. Casual: <15. Formal: >20.

#### CTA style

```python
cta_pattern_imperative = ["Sign up", "Get started", "Try", "Buy now", "Download", "Start", "Book"]
cta_pattern_invitante = ["Learn more", "See how", "Discover", "Explore", "Want to"]
# Find CTA via <button>, <a class="cta">, <a href> ending in /signup, /start, /demo
imperative_count, invitante_count = ...
cta_style = "imperative" if imperative_count > invitante_count else "invitante" if invitante_count > 0 else "neutral"
```

#### Exclamation density per 100 words

```python
exclamation_count = corpus.count("!")
exclamation_density_per_100w = (exclamation_count / total_words) * 100
```

Enthusiastic: ≥3 per 100 words. Matter-of-fact: <0.5.

### Fase 3 — Score 4-dim Nielsen Norman (1-5)

Per ogni dimensione, applicare rubric da `references/tov-rubric-nielsen-norman.md`:

#### Formal↔Casual (1=Very formal, 5=Very casual)

Indicators casual (push score → 5):
- Contractions ("we're", "don't") count
- Casual lexicon ("hi", "hey", "stuff", "kinda")
- Avg sentence length <15
- Jargon density <5%

Indicators formal (push score → 1):
- No contractions
- Formal lexicon ("herewith", "subsequently")
- Avg sentence length >20
- Jargon density >10%

**Score calc**: weighted avg + rounding to integer 1-5.

**Evidence quotes**: trova 3 frasi nel corpus che riflettono lo score (più chiare). Verbatim.

#### Funny↔Serious (1=Funny, 5=Very serious)

Indicators funny:
- Interjections ("Oops!", "Whoa", "Hi there")
- Self-deprecating lexicon
- Pun / wordplay
- Memes references

Indicators serious:
- No interjections
- Subject treated literally
- No humor attempts

#### Respectful↔Irreverent (1=Respectful, 5=Very irreverent)

Indicators irreverent:
- Provocative lexicon ("damn", "screw", "kill", "smash")
- Self pronouns ("I/we") > you ratio (brand-centric)
- Ironizing the subject (not the audience)

Indicators respectful:
- No provocative words
- Customer-centric (you > I/we)
- Subject treated with dignity

#### Enthusiastic↔Matter-of-fact (1=Very enthusiastic, 5=Matter-of-fact)

Indicators enthusiastic:
- Exclamation density ≥3 per 100w
- Emoji usage
- Adjective superlatives ("the best", "the most amazing")
- Adverb intensifiers ("absolutely", "incredibly")

Indicators matter-of-fact:
- Exclamation density <0.5
- No emoji
- Neutral adjectives

### Fase 4 — Find evidence quotes (3 per dim, MANDATORY)

Per ogni dimensione score, find 3 verbatim quotes nel corpus che esemplificano lo score:

```python
def find_evidence(corpus, dim, score, target_count=3):
    candidates = []
    for sentence in corpus_sentences:
        if matches_dim_indicator(sentence, dim, score):
            candidates.append({"quote": sentence, "url": detect_url_for_sentence(sentence), "metric": indicator_matched})
    return candidates[:target_count]
```

**Block**: se `len(evidence) < 3` per qualsiasi dim → output `insufficient_evidence_per_dim: [<dim>]` + suggerimento "espandere corpus".

### Fase 5 — Build tov.json

```json
{
  "competitor": "Make",
  "scrape_date": "2026-04-30",
  "corpus_sources": ["make.com", "make.com/about", "make.com/blog/post1", ...],
  "corpus_size_words": 1247,
  "scores": {
    "formal_casual": {
      "score": 2,
      "label": "Casual",
      "evidence": [
        {"quote": "We're rebuilding the internet of stuff.", "url": "make.com/about", "metric": "contraction"},
        {"quote": "Drag, drop, done.", "url": "make.com", "metric": "short_imperative"},
        {"quote": "10,000+ apps, zero coding hell.", "url": "make.com/integrations", "metric": "casual_lexicon"}
      ]
    },
    "funny_serious": {
      "score": 4,
      "label": "Serious",
      "evidence": [
        {"quote": "Build automations of any size, with confidence.", "url": "make.com", "metric": "subject_serious"},
        {"quote": "Enterprise-grade reliability for mission-critical workflows.", "url": "make.com/enterprise", "metric": "literal_treatment"},
        {"quote": "Production-ready integrations vetted for scale.", "url": "make.com/security", "metric": "no_humor"}
      ]
    },
    "respectful_irreverent": {
      "score": 3,
      "label": "Neutral",
      "evidence": [...]
    },
    "enthusiastic_matter_of_fact": {
      "score": 2,
      "label": "Enthusiastic",
      "evidence": [...]
    }
  },
  "derived_metrics": {
    "jargon_density_pct": 4.2,
    "pronoun_ratio_we_you": 0.78,
    "avg_sentence_length_words": 12.4,
    "cta_style": "imperative",
    "cta_examples": ["Get started free", "Try Make", "Book a demo"],
    "exclamation_density_per_100w": 1.8,
    "contractions_count": 23,
    "emoji_count": 0
  },
  "tov_summary_label": "Casual + Serious + Neutral + Enthusiastic",
  "blue_ocean_hint": "If your competitors are all Casual + Enthusiastic, going Formal + Matter-of-fact may differentiate (e.g. enterprise serious target).",
  "insufficient_evidence": false
}
```

### Fase 6 — Validate output

Pre-write validation:
- [ ] `corpus_size_words >= 200` (else flag insufficient)
- [ ] 4 dim scores all integer 1-5
- [ ] Each dim has `evidence[]` length == 3 (else flag per-dim)
- [ ] All quotes verbatim from corpus (regex check substring match)
- [ ] All `derived_metrics` present (no null)

## Output examples

Vedi JSON Make sopra (success case).

Caso insufficient_evidence:
```json
{
  "competitor": "Linear",
  "corpus_size_words": 87,
  "insufficient_evidence": true,
  "reason": "corpus too small (87 words, min 200 required)",
  "suggestion": "Espandi corpus con: about page + 5 latest blog posts + LinkedIn 'About' company section"
}
```

## Anti-pattern

- **NO score senza 3 evidence quotes** — output blocked, fail loud
- **NO claim ToV su corpus <200 parole** — flag e exit
- **NO derived_metrics inventate** — solo computed da script (deterministic)
- **NO score outside [1,5]** — clamp + log warning
- **NO evidence quote non-verbatim** — substring check mandatory
- **NO ToV su pagina sola homepage** se <200 parole — sempre aggrega about + blog

## Edge cases

- **Multi-language corpus** (es. site EN + IT): split per lingua, score solo lingua dominante (>70% words)
- **Marketing copy vs technical doc**: TOV può differire — flag se 2 corpus sources hanno score >2 differenza, output `tov_inconsistent: true`
- **Brand voice vs spokesperson voice** (es. founder Twitter vs corporate site): scope solo corporate (`make.com`), no Twitter individual
- **Trade press citation vs original copy**: filtra citation in `<blockquote>` o `cite=""` (non rappresenta brand voice)
- **A/B variant in same page**: usa `:visible` Playwright check, scrape solo variant servita all'utente

## Reference

- `references/tov-rubric-nielsen-norman.md` — rubric completa 1-5 per dim con esempi reali
- [Nielsen Norman Group — Four Dimensions of Tone of Voice](https://www.nngroup.com/articles/tone-of-voice-dimensions/)
- `research/research-summary.md` RQ2 — derivazione metriche
