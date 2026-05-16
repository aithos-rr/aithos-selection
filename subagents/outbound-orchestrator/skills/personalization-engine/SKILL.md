---
name: personalization-engine
description: AI first-line generation per cold email outbound da signal extraction. 8 hook templates (job-change, funding, hiring, podcast, content, conference, tool-stack, geo). Anti-LLM-detection enforcement (8 banned markers, 3+ variants, 15-25 word constraint, uniqueness hash check). Per `/outbound-orchestrator` skill companion.
when_to_use: Generate first-line per ogni lead in sequence build, A/B variants subject + first-line, audit personalization quality, batch re-generation se signal updated
---

# Personalization Engine

Genera first-line personalizzata per cold email da signal extraction. Output: 3 variants per lead, signal-aware, anti-LLM-detection compliant.

**Lingua**: italiano per messaggi utente. Inglese per nomi tecnici (signal_used, hook_template_id).

## When to use

Attiva quando:
- Sequence build per nuova campagna outbound (Fase 4 metodologia `/outbound-orchestrator`)
- Re-generation first-line dopo signal update (es. funding announcement)
- A/B test variants subject + first-line
- Audit qualità sequence pre-execute (sample 10 lead)
- Batch update template per testing

**Non attivare** se:
- Lead senza `intent_signals` JSON popolato (chain `/lead-finder-pro` mancante)
- Brand voice + value prop non in config
- Signal age >90 giorni (decay completo, no relevance)

## Prerequisites

- Lead enriched JSON con field `intent_signals` (output `/lead-finder-pro`)
- Config `<memory>/config.md` con `brand.voice` + `brand.value_prop`
- LLM access (Anthropic Claude via Claude Code, no API key needed)
- Reference `references/prompt-patterns.md` caricata

## Inputs

```json
{
  "lead": {
    "lead_id": "uuid",
    "first_name": "Marco",
    "last_name": "Rossi",
    "company": "Acme Inc",
    "role": "VP Marketing",
    "industry": "SaaS B2B",
    "intent_signals": [
      {"type": "job_change", "value": "VP Marketing → CMO", "date": "2026-04-15", "source": "linkedin"},
      {"type": "funding_round", "value": "Series A $5M", "date": "2026-03-20", "source": "crunchbase"}
    ]
  },
  "brand_voice": "direct",  // direct | friendly | educational | bold
  "value_prop": "GTM Engineering audit gratuito per SaaS B2B post-Series A",
  "config": {
    "variant_count": 3,
    "first_line_max_words": 25,
    "banned_markers": ["delve into", "navigate the landscape", ...]
  }
}
```

## Outputs

```json
{
  "lead_id": "uuid",
  "signal_used": "job_change",
  "hook_template_id": 1,
  "first_line_variants": [
    {
      "variant": "A",
      "text": "Ciao Marco, vidi che sei passato a CMO ad Acme a marzo. Congrats!",
      "uniqueness_hash": "abc123def456",
      "word_count": 13
    },
    {
      "variant": "B",
      "text": "Ciao Marco, complimenti per il nuovo ruolo ad Acme — il move è stato un upgrade.",
      "uniqueness_hash": "789xyz",
      "word_count": 16
    },
    {
      "variant": "C",
      "text": "Ciao Marco, il salto da VP Marketing a CMO mi è saltato all'occhio — auguri!",
      "uniqueness_hash": "456abc",
      "word_count": 15
    }
  ],
  "banned_markers_check": "passed",
  "uniqueness_check": "all_unique",
  "confidence": 0.92,
  "_meta": {
    "generated_at": "2026-04-30T11:30:00Z",
    "model": "claude-sonnet-4-6",
    "input_token": 450,
    "output_token": 120
  }
}
```

## Methodology

### 1. Signal selection

Da `intent_signals` array, select **most recent + highest priority**:

Priority order:
1. job_change (<30d) — sempre top priority
2. funding_round (<60d)
3. hiring_surge (<30d, 5+ posts)
4. tool_stack_change (<30d)
5. recent_post (<14d)
6. podcast_guest (<60d)
7. conference (<30d, ongoing or recent)
8. geo_event (<14d, time-sensitive)

Se multiple, top-1 selected. Salva `signal_used` per tracking.

### 2. Hook template match

Map signal to hook template (1-8 in `references/prompt-patterns.md`).

```python
SIGNAL_TO_HOOK = {
    "job_change": 1,
    "funding_round": 2,
    "hiring_surge": 3,
    "podcast_guest": 4,
    "recent_post": 5,
    "conference": 6,
    "tool_stack_change": 7,
    "geo_event": 8
}
hook_template_id = SIGNAL_TO_HOOK[signal_type]
```

Load template variants (italiano default, English se lead geo USA/UK) da `references/prompt-patterns.md`.

### 3. LLM prompt (Claude Sonnet)

System prompt:

```
Sei un copywriter esperto di cold email B2B. Genera SOLO la prima riga di un email cold outreach in italiano.

VINCOLI MANDATORY:
- Max 25 parole
- Riferisci il signal specifico fornito (NO generic)
- Tone: <brand_voice>
- NO marker stilistici banned: delve into, navigate the landscape, I hope this finds you well, leverage, synergy, seamlessly, cutting-edge
- NO em-dash multipli (max 1 per frase)
- Conversational, come scriveresti a collega

OUTPUT: SOLO il testo first-line, nessuna spiegazione.
```

User prompt per lead:

```
Lead: {first_name} {last_name}, {role} a {company}, industry {industry}.
Signal: {signal_type} = "{signal_value}" ({signal_date_human})
Brand voice: {brand_voice}
Genera variant {A|B|C} basata su template hook #{hook_template_id}.
```

3 LLM call (1 per variant), in parallel se possibile.

### 4. Banned markers check

```python
def check_banned_markers(text, banned_list):
    text_lower = text.lower()
    found = [m for m in banned_list if m.lower() in text_lower]
    em_dashes = text.count("—")
    if em_dashes > 1:
        found.append(f"em_dash_x{em_dashes}")
    return {"passed": len(found) == 0, "found": found}
```

Se found → regenerate variant (max 3 retry, then escalate to user).

### 5. Word count check

```python
def word_count_check(text, max_words=25):
    n = len(text.split())
    return {"passed": n <= max_words, "actual": n}
```

Se >max → instruction LLM "shorten to 20 words", regenerate.

### 6. Uniqueness hash check

```python
import hashlib
from rapidfuzz import fuzz

def uniqueness_check(text, last_100_history):
    text_hash = hashlib.md5(text.lower().encode()).hexdigest()[:16]

    # Esatto duplicate
    if text_hash in [h["hash"] for h in last_100_history]:
        return {"passed": False, "reason": "exact_duplicate"}

    # Fuzzy similarity (rapidfuzz)
    for prev in last_100_history:
        ratio = fuzz.ratio(text.lower(), prev["text"].lower())
        if ratio > 90:
            return {"passed": False, "reason": f"too_similar (ratio={ratio}) to: '{prev['text'][:50]}...'"}

    return {"passed": True, "hash": text_hash}
```

Se not passed → regenerate with "make it more different from previous". Save passed variant to `<memory>/first_line_history.jsonl` (rolling window).

### 7. Brand voice modulation

Vedi `references/prompt-patterns.md` sezione "Brand voice modulation". Word count target + tone descriptor + banned filler differiscono per voice.

| Voice | Word count | Style |
|-------|------------|-------|
| direct | 12-18 word | factual, no filler |
| friendly | 15-22 word | conversational, 1-2 emoji ok |
| educational | 18-25 word | data-first, dato concreto in apertura |
| bold | 15-25 word | contrarian view, hook forte |

## Examples

### Example 1 — Job change signal, voice=direct

**Input**:
```json
{
  "lead": {"first_name": "Marco", "company": "Acme", "intent_signals": [{"type": "job_change", "value": "VP Marketing → CMO", "date": "2026-04-15"}]},
  "brand_voice": "direct"
}
```

**Output**:
```json
{
  "first_line_variants": [
    {"variant": "A", "text": "Ciao Marco, vidi che sei passato a CMO ad Acme a aprile. Congrats!", "word_count": 13},
    {"variant": "B", "text": "Ciao Marco, complimenti per il nuovo ruolo ad Acme — un upgrade interessante.", "word_count": 13},
    {"variant": "C", "text": "Ciao Marco, il move da VP Marketing a CMO mi è saltato all'occhio. Auguri!", "word_count": 14}
  ],
  "signal_used": "job_change",
  "banned_markers_check": "passed",
  "uniqueness_check": "all_unique"
}
```

### Example 2 — Funding signal, voice=educational

**Input**:
```json
{
  "lead": {"first_name": "Giulia", "company": "FinTechCo", "intent_signals": [{"type": "funding_round", "value": "Series B $20M", "date": "2026-03-15"}]},
  "brand_voice": "educational"
}
```

**Output**:
```json
{
  "first_line_variants": [
    {"variant": "A", "text": "Ciao Giulia, complimenti per il Series B di FinTechCo — secondo Crunchbase è il 23° round chiuso in Italia 2026.", "word_count": 23},
    {"variant": "B", "text": "Ciao Giulia, ho letto del Series B $20M — il 67% delle FinTech post-B fatica su unit economics nei primi 12 mesi.", "word_count": 22},
    {"variant": "C", "text": "Ciao Giulia, il round Series B di FinTechCo è arrivato in un timing interessante per il segmento Italian FinTech.", "word_count": 19}
  ],
  "signal_used": "funding_round"
}
```

### Example 3 — Hiring signal, voice=friendly

**Input**:
```json
{
  "lead": {"first_name": "Luca", "company": "GrowCo", "intent_signals": [{"type": "hiring_surge", "value": "8 SDR posts in 30d", "date": "2026-04-01"}]},
  "brand_voice": "friendly"
}
```

**Output**:
```json
{
  "first_line_variants": [
    {"variant": "A", "text": "Ciao Luca! Vedo che state cercando 8 SDR a GrowCo — bella crescita 🚀", "word_count": 13},
    {"variant": "B", "text": "Ciao Luca, ho notato che GrowCo sta scalando il team SDR rapidamente — congrats sul ramping.", "word_count": 16},
    {"variant": "C", "text": "Ciao Luca, 8 job posts SDR a GrowCo in 30 giorni — il team sta crescendo forte!", "word_count": 16}
  ],
  "signal_used": "hiring_surge"
}
```

## Error handling

### LLM regenerate fail (>3 retry)

Escalate to user:
```
⚠️ Personalization failed per lead {lead_id}: banned markers / word count / uniqueness fail dopo 3 retry.
First-line generato:
- {variant_A_failed}
- {variant_B_failed}
Signal usato: {signal_type}
Suggerimento: skip questo lead o manual override first-line.
```

### Signal not found / signal age >90d

Skip lead da campaign + log warning:
```
Lead {lead_id} skipped — no recent signal (latest: {signal_date}, age {N}d > 90d threshold).
Suggerimento: re-enrich via /lead-finder-pro o exclude da grade A/B segmentation.
```

### Brand voice conflict con signal

Es. signal = "podcast guest spirituale", brand voice = "bold" → conflict warning. Default fallback: voice=friendly per signal sensitive.

## Anti-pattern

1. **Mai personalizzare senza signal specifico** ("vidi la vostra azienda" generic = banned)
2. **Mai usare {{var}}** double brace (HeyReach single-brace, SmartLead double-brace — gestire differenze in `sequence-builder`, NON qui)
3. **Mai accettare LLM output >25 word**, regenerate
4. **Mai accettare banned markers**, regenerate
5. **Mai usare signal age >90d**, skip lead
6. **Mai single variant** se A/B test on (mandatory 3+ variants)
7. **Mai LLM call senza brand voice context** (output diverge dal brand)
8. **Mai dimenticare uniqueness check** rolling window (anti-detection critical)

## Scripts

- `../../scripts/personalize_first_line.py` — CLI wrapper LLM call

## References

- `../../references/prompt-patterns.md` — 8 hook templates italiano + English
- `../../references/outbound-best-practices-2026.md` — reply rate boost evidence
- `../../research/research-summary.md` RQ5 — anti-LLM-detection rules

## Output destination

Skill output salvato in `output/personalization_<campaign_name>_<ts>.json` (per re-processing) + appending `<memory>/first_line_history.jsonl` (rolling window 1000 entries per uniqueness check).
