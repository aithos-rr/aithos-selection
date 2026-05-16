# Prompt Patterns — First-Line Generation 2026

> Reference doc per `/outbound-orchestrator` skill `personalization-engine`. 8 signal-hook templates italiano + inglese, A/B variant generation, anti-LLM-detection rules, first-line uniqueness hash.
>
> Fonte: `research/research-summary.md` RQ5 + skill v1 `outbound-campaign` + sendr.ai 2026 + Apollo.

## Filosofia

> "La differenza tra 3% e 15% reply rate non viene da subject lines. Viene da data quality + signal recency."

Hook structure: **specific signal + recency proof + curiosity hook**. Non "vidi la vostra azienda" mai. NEVER.

## 8 signal-hook templates

### 1. Job change (signal: posizione cambiata <30d)

**Italiano**:
```
"Ciao {first_name}, vidi che sei passato a {new_role} a {new_company} a {month}. Congrats!"
"Ciao {first_name}, complimenti per il nuovo ruolo a {new_company} — il move da {old_company} è stato un upgrade interessante."
"Ciao {first_name}, il salto da {old_role} a {new_role} mi è saltato all'occhio — auguri!"
```

**English**:
```
"Hi {first_name}, saw you joined {new_company} as {new_role} in {month} — congrats!"
"Hi {first_name}, congrats on the move from {old_company} to {new_company}!"
"Hi {first_name}, the jump from {old_role} to {new_role} caught my eye — congrats!"
```

**Bridge to value prop**:
```
"Nei primi 90 giorni a {new_company}, la sfida tipica per {role} è {pain_hypothesis}. Posso condividere come {similar_lead} l'ha gestita?"
```

### 2. Funding round (signal: Series A/B/C announcement <60d)

**Italiano**:
```
"Ciao {first_name}, ho letto del round {round_type} di {company} a {month} — congratulazioni!"
"Ciao {first_name}, complimenti per il {round_type} chiuso a {month} — visto su {source}."
"Ciao {first_name}, il round {round_type} di {company} è arrivato in un timing interessante — congrats!"
```

**Bridge**:
```
"Nelle SaaS post-{round_type}, la priorità GTM tipica è {scaling_pain}. Lavoriamo con altri founder simili — vale 15 min?"
```

### 3. Hiring surge (signal: 5+ job posts in 30d, ruoli chiave)

**Italiano**:
```
"Ciao {first_name}, vedo che state cercando {n} {role} a {company} — sembra fase di crescita rapida."
"Ciao {first_name}, ho notato {n} job posts aperti a {company} per ruoli {role}. Crescita?"
"Ciao {first_name}, il piano hiring di {company} su {role} è ambizioso — congrats sul ramping."
```

**Bridge**:
```
"Quando si scala il team {role}, il pain comune è {pain}. Ho visto {n_companies} altre aziende risolverlo con {solution_briefly}. Vuoi vedere come?"
```

### 4. Podcast/content guest (signal: tu parlato a podcast/podcast/intervento)

**Italiano**:
```
"Ciao {first_name}, ho ascoltato il tuo intervento su {podcast} re {topic} — il punto su {specific} mi ha colpito."
"Ciao {first_name}, complimenti per il talk a {podcast} — la parte su {topic} è la migliore sintesi che ho sentito."
"Ciao {first_name}, ho riascoltato due volte il tuo episodio {podcast} su {topic}. {specific_takeaway}."
```

**Bridge**:
```
"Volevo chiederti se {hypothesis_specific} è quello che state vedendo voi a {company}? Lavoriamo nello spazio."
```

### 5. Recent post LinkedIn/X (signal: post pubblico <14d)

**Italiano**:
```
"Ciao {first_name}, il tuo post su {topic} mi ha colpito — specialmente {specific_quote}."
"Ciao {first_name}, ho fatto un commento mentale al tuo post su {topic}. La parte {specific} è esattamente quello che noi vediamo lavorando con {industry}."
```

**Bridge**:
```
"Curioso: quanto del problema {pain} è tech vs process per voi a {company}?"
```

### 6. Conference attended/speaker (signal: speaker o attendee evento <30d)

**Italiano**:
```
"Ciao {first_name}, ti ho visto a {conference} — il tuo talk su {topic} è stato il highlight della mia giornata."
"Ciao {first_name}, ero a {conference} pure io. {specific_observation_session_yours}."
"Ciao {first_name}, ho preso un sacco di note dal tuo talk a {conference}. Ne uso una in particolare: {takeaway}."
```

**Bridge**:
```
"Volevo continuare la conversazione che hai aperto su {topic}. Lavoriamo con {industry} su {related_topic}, hai 15 min?"
```

### 7. Tool stack change (signal: BuiltWith/Wappalyzer detect new tool <30d)

**Italiano**:
```
"Ciao {first_name}, ho notato che {company} sta usando {new_tool} adesso — interessante shift da {old_tool}."
"Ciao {first_name}, il move su {new_tool} dimostra che {hypothesis_workflow_change}."
"Ciao {first_name}, il roll-out {new_tool} a {company} è recente — come sta andando?"
```

**Bridge**:
```
"Lavoriamo con {industry} sul layer {related_layer} — quando si setup {new_tool}, il next step tipico è {recommendation}. Posso condividere il framework?"
```

### 8. Geo/event (signal: tu sei in città X per evento Y stessi giorni)

**Italiano**:
```
"Ciao {first_name}, sono a {city} per {event} {date} — sarebbe l'occasione di un caffè?"
"Ciao {first_name}, sarò a {city} dal {date_start} al {date_end}. Ti va un quick chat in persona?"
"Ciao {first_name}, vedo che siete based a {city}. Sarò lì per {event} a {date} — caffè?"
```

**Bridge**:
```
"Niente sales call — solo 30 min veloci per parlare di {topic_relevant_to_them}. Funziona?"
```

## Anti-LLM-detection rules (mandatory — DECISION-011)

### 8 banned markers stilistici

```yaml
banned_markers:
  - "delve into"
  - "navigate the landscape"
  - "I hope this email finds you well"
  - "leverage"  # come verbo "to leverage"
  - "synergy"
  - "seamlessly"
  - "cutting-edge"
  - "—"  # em-dash multiple in same sentence

also_avoid:
  - "unlock the potential"
  - "robust solution"
  - "in today's fast-paced world"
  - "at the end of the day"
  - "moving forward"
  - "circle back"
```

### 5 vincoli prompt LLM

1. **Length constraint**: 15-25 word max per first-line
2. **Signal-specific**: must reference signal trovato, NO generic placeholder
3. **No greeting filler**: skip "I hope this finds you well"
4. **Conversational tone**: come scriveresti a collega, no "linguistic puff"
5. **Ban list enforcement**: regex check pre-output, reject + regenerate se markers found

### Variant count (DECISION-011)

Min 3 variants per signal-hook combo:
- Variant A: structure "saw + signal + congrats"
- Variant B: structure "noticed + signal + observation"
- Variant C: structure "specific quote/detail + opinion"

Random selection per lead, 33% each. Distribuzione monitorata via report.

### First-line uniqueness hash check

```python
import hashlib
last_100_hashes = []  # rolling window from <memory>/first_line_hashes.txt

def is_unique(first_line, threshold=0.85):
    fl_hash = hashlib.md5(first_line.lower().encode()).hexdigest()[:16]

    # Esatto duplicate
    if fl_hash in last_100_hashes:
        return False, "exact_duplicate"

    # Fuzzy similarity check (rapidfuzz)
    from rapidfuzz import fuzz
    for prev in last_100_first_lines[-100:]:
        if fuzz.ratio(first_line.lower(), prev.lower()) > 90:
            return False, f"too_similar_to: '{prev[:50]}...'"

    last_100_hashes.append(fl_hash)
    last_100_first_lines.append(first_line)
    return True, "unique"
```

## A/B variant generation pattern

### Subject lines (per step)

Genera 2 variants subject:

```
Variant A: pattern "Domanda su {company}"
Variant B: pattern "{first_name}, {topic}"
```

A/B mode in `sequence-builder` produce 2 sequence specifiche con flag `is_split_test: true`. SmartLead split test attivato via API.

### Body first-line

Genera 3 variants per signal (vedi sopra). Random distribution 33% each.

### Significance threshold

- Min 30 lead per variant
- Min 100 reply per significance robusta
- Default mode: warning "results not significant" se <30/variant

## Output structure (skill `personalization-engine`)

```python
def generate_first_line(lead, brand_voice, value_prop, signal_used):
    """Returns dict with all 3 variants + metadata."""
    return {
        "lead_id": lead["lead_id"],
        "signal_used": signal_used,  # 1-8
        "hook_template_id": signal_used,  # references this doc section
        "first_line_variants": [
            {"variant": "A", "text": "Ciao Marco, vidi che sei passato a CMO ad Acme a marzo. Congrats!", "uniqueness_hash": "..."},
            {"variant": "B", "text": "Ciao Marco, complimenti per il nuovo ruolo ad Acme — il move da Beta è stato un upgrade.", "uniqueness_hash": "..."},
            {"variant": "C", "text": "Ciao Marco, il salto da VP Marketing a CMO mi è saltato all'occhio — auguri!", "uniqueness_hash": "..."}
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

## Brand voice modulation

### Direct/concise

```
Word count target: 50-80 word body
First-line: 12-18 word
Tone: factual, no filler
Banned: emoji, exclamation marks excessive
```

Esempio:
```
"Ciao Marco, vidi che sei passato a CMO ad Acme. Congrats!

Lavoriamo con SaaS Series A su scaling GTM. Ti sembrerebbe utile vedere come?

Filippo"
```

### Friendly/casual

```
Word count: 80-130 word body
First-line: 15-22 word
Tone: conversational, può usare 1-2 emoji se appropriate
Banned: jargon corporate, "synergy"
```

Esempio:
```
"Ciao Marco! Complimenti per il nuovo ruolo a Acme — sicuramente un bel salto. 🎯

Mi capita di lavorare con CMO che sono entrati in fase Series A e mi accorgo che spesso il primo trimestre è caotico (capita anche a te?).

Ho un framework di onboarding GTM in 30-60-90 giorni. Te lo mando? È un PDF di 4 pagine.

A presto,
Filippo"
```

### Educational/expert

```
Word count: 100-150 word body
First-line: 18-25 word, dato concreto
Tone: industry authority, data-first
Banned: opinion senza dato, "I think"
```

Esempio:
```
"Ciao Marco, vidi che sei passato a CMO ad Acme — congrats sul move da Beta.

Stavo guardando i benchmark Marketing Ops 2026: il 67% dei CMO Series A Saas dice che il primo bottleneck è "lead-to-MQL conversion" (vs 23% che dicono "demand gen").

Curioso di sapere se a Acme stai vedendo lo stesso pattern.

Ho un report 12 pagine che dettaglia per ICP. Te lo mando se utile.

Filippo"
```

### Bold/provocative

```
Word count: 70-110 word body
First-line: 15-25 word, contrarian
Tone: provocatorio, contrarian view, hook forte
Banned: aggressivo personale, no-evidence claim
```

Esempio:
```
"Ciao Marco, vidi che sei diventato CMO di Acme.

Non-popular take: il 90% dei CMO nei primi 100 giorni butta soldi in demand gen senza fixare attribution. Ho dati che mostrano +40% ROI invertendo l'ordine.

Tu in che camp sei?

Filippo"
```

## Reference esterni

- [Sendr.ai — Humanize Cold Outreach AI 2026](https://www.sendr.ai/blog/what-are-the-best-ways-to-humanize-cold-outreach-using-ai-in-2026)
- [Apollo — Email Reply Classification & Personalization](https://www.apollo.io/tech-blog/email-reply-classification-done-right)
- [Instantly — Future of Cold Email AI 2026-2027](https://instantly.ai/blog/future-of-cold-email-ai-personalization-automation-trends-shaping-2026-2027/)
- [Mailshake — AI Will Cold Email Still Work 2026](https://mailshake.com/blog/will-cold-email-still-work-in-2026/)
- Skill v1 `<pack-root>/skills/webinar-2/outbound-campaign/SKILL.md` (segmentation per intent + copy templates)
