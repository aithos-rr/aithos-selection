# Tone of Voice Rubric — Nielsen Norman 4-dim + Metriche Derivate

> Rubric scorabile 1-5 per ogni dimensione NN + 5 metriche derivate quantitative. Source: [Nielsen Norman Group — The Four Dimensions of Tone of Voice](https://www.nngroup.com/articles/tone-of-voice-dimensions/) + extension Filippo per applicazione SaaS B2B 2026.

## Le 4 dimensioni Nielsen Norman

**Definizioni canoniche**:

1. **Formality**: Formal ↔ Casual
2. **Humor**: Funny ↔ Serious
3. **Respectfulness**: Respectful ↔ Irreverent
4. **Enthusiasm**: Enthusiastic ↔ Matter-of-fact

> "The tone of any piece of content can be analyzed along 4 dimensions: humor, formality, respectfulness, and enthusiasm." — NN/G

## Scoring rubric 1-5

### Dim 1 — Formal ↔ Casual

| Score | Label | Indicators |
|-------|-------|------------|
| 1 | Very formal | No contractions ("we are", "do not"), formal lexicon ("herewith", "subsequently"), avg sentence ≥20 parole, jargon ≥10% |
| 2 | Formal | No contractions, professional lexicon, avg sentence 16-20, jargon 7-10% |
| 3 | Neutral | Mixed: some contractions, neutral lexicon, avg sentence 13-16, jargon 5-7% |
| 4 | Casual | Contractions ("we're", "don't"), casual lexicon ("stuff", "kinda"), avg sentence 10-13 |
| 5 | Very casual | Heavy contractions, slang ("hey there", "what's up"), avg sentence <10, jargon <3% |

**Esempio score 1 (Very formal)** — IBM enterprise white paper:
> "We are pleased to announce the general availability of the IBM watsonx.data platform, designed to facilitate enterprise-grade data integration."

**Esempio score 4 (Casual)** — Make homepage:
> "Drag, drop, done. We're rebuilding the internet of stuff. 10,000+ apps, zero coding hell."

**Esempio score 5 (Very casual)** — DuckDuckGo:
> "Hi! We're DDG. We don't track you. Try us — you'll dig it."

### Dim 2 — Funny ↔ Serious

| Score | Label | Indicators |
|-------|-------|------------|
| 1 | Very funny | Multiple jokes/puns/memes per page, self-deprecating, irony pervasive |
| 2 | Funny | Occasional humor attempts (1-2 per page), wordplay, light self-mockery |
| 3 | Mixed | Subject treated literally with light moments |
| 4 | Serious | Subject treated literally, no humor attempts, professional |
| 5 | Very serious | Solemn tone, subject critical (security, compliance), zero humor |

**Esempio score 1 (Very funny)** — Cards Against Humanity:
> "We're a despicable card game. We hate ourselves. You'll love us."

**Esempio score 4 (Serious)** — Stripe:
> "Stripe is a financial infrastructure platform. We power online businesses globally with a complete suite of products."

**Esempio score 5 (Very serious)** — JPMorgan Chase enterprise:
> "JPMorgan Chase is a leading global financial services firm with operations worldwide."

### Dim 3 — Respectful ↔ Irreverent

| Score | Label | Indicators |
|-------|-------|------------|
| 1 | Very respectful | Customer-centric (you > we), polite, no provocative lexicon, dignified subject treatment |
| 2 | Respectful | Pronoun ratio I-we/you <0.5, polite, neutral lexicon |
| 3 | Neutral | Balanced pronoun ratio (~1.0), no provocative |
| 4 | Irreverent | Pronoun ratio I-we/you >1, occasional provocative ("damn", "screw"), brand-centric |
| 5 | Very irreverent | Heavy provocative, ironizing the subject (not audience), brand-as-personality |

**Esempio score 1 (Very respectful)** — Mailchimp 2010s:
> "You make great content. We help you send it. Together we'll grow your business."

**Esempio score 5 (Very irreverent)** — Cards Against Humanity / Liquid Death:
> "Murder your thirst. We're an aluminum-canned death cult, not a beverage company."

### Dim 4 — Enthusiastic ↔ Matter-of-fact

| Score | Label | Indicators |
|-------|-------|------------|
| 1 | Very enthusiastic | Exclamation ≥3 per 100w, multiple emoji, superlative ("the best ever", "absolutely amazing"), adverb intensifiers |
| 2 | Enthusiastic | Exclamation 1-3 per 100w, occasional emoji, upbeat adjectives |
| 3 | Mixed | Exclamation 0.5-1 per 100w, balanced adjectives |
| 4 | Matter-of-fact | Exclamation <0.5 per 100w, neutral adjectives, no emoji |
| 5 | Very matter-of-fact | Zero exclamation, clinical/technical adjectives, dry tone |

**Esempio score 1 (Very enthusiastic)** — Webflow marketing email:
> "🎉 You're going to LOVE this! Our new feature is INCREDIBLE — try it now! 🚀"

**Esempio score 4 (Matter-of-fact)** — Linear app:
> "Linear is a purpose-built tool for planning and building products."

**Esempio score 5 (Very matter-of-fact)** — Apple legal page:
> "Apple Inc. is incorporated in California. Headquartered in Cupertino."

## 5 Metriche Derivate Quantitative

Calcolabili programmaticamente da `scripts/tov_score.py`:

### 1. Jargon Density %

```python
jargon_terms = ["API", "SDK", "SaaS", "B2B", "ROI", "KPI", "OKR", "SOC2", "GDPR",
                "OAuth", "REST", "GraphQL", "MLOps", "DevOps", "CI/CD", "RBAC",
                "JWT", "SLA", "SLO", "DAU", "MAU", "CRM", "ERP", "BI", ...]  # ~50 acronyms
jargon_count = sum(1 for word in words if word.upper() in jargon_terms)
jargon_density_pct = (jargon_count / total_words) * 100
```

Range tipico:
- **<3%**: casual consumer (Mailchimp, DuckDuckGo)
- **3-7%**: SaaS B2B mid (Make, Notion)
- **7-12%**: SaaS B2B enterprise (Datadog, Snowflake)
- **>12%**: white paper enterprise / RFP

### 2. Pronoun Ratio I-we / you

```python
i_we_count = sum(1 for w in words if w.lower() in ["i", "we", "us", "our", "ourselves"])
you_count = sum(1 for w in words if w.lower() in ["you", "your", "yours", "yourself"])
pronoun_ratio_we_you = i_we_count / max(1, you_count)
```

Range:
- **<0.4**: very customer-centric (Mailchimp 2010s)
- **0.4-0.8**: customer-centric balanced
- **0.8-1.2**: balanced
- **1.2-2**: brand-centric
- **>2**: very brand-centric / irreverent (Liquid Death)

### 3. Avg Sentence Length

```python
sentences = re.split(r'[.!?]+', corpus)
avg_sentence_length_words = sum(len(s.split()) for s in sentences) / len(sentences)
```

Range:
- **<10**: very casual / staccato (Make tagline-style)
- **10-15**: casual SaaS
- **15-20**: balanced professional
- **20-25**: formal
- **>25**: very formal / academic

### 4. CTA Style — Imperativo vs Invitante

```python
imperative_patterns = ["Sign up", "Get started", "Try", "Buy now", "Download",
                       "Start", "Book", "Request", "Claim", "Activate"]
invitante_patterns = ["Learn more", "See how", "Discover", "Explore", "Want to",
                      "Curious about", "Read more", "Find out"]
imperative_count = count_matches(buttons + ctas, imperative_patterns)
invitante_count = count_matches(buttons + ctas, invitante_patterns)
cta_style = "imperative" if imperative_count > invitante_count else \
            "invitante" if invitante_count > 0 else "neutral"
```

Mapping a Formality dim:
- `imperative` → casual side (score 4-5 Formal↔Casual)
- `invitante` → formal side (score 1-3)
- `neutral` → ambiguous

### 5. Exclamation Density per 100 words

```python
exclamation_count = corpus.count("!")
exclamation_density_per_100w = (exclamation_count / total_words) * 100
```

Mapping a Enthusiasm dim:
- **≥3**: Very enthusiastic (score 1)
- **1-3**: Enthusiastic (score 2)
- **0.5-1**: Mixed (score 3)
- **<0.5**: Matter-of-fact (score 4)
- **0**: Very matter-of-fact (score 5)

## Esempi reali scorati end-to-end

### Esempio 1 — Make.com (homepage 2026)

**Corpus** (1247 parole):
> "Automate work, anywhere — visually. Drag, drop, done. We're rebuilding the internet of stuff. 10,000+ apps, zero coding hell. Build, run, and scale automations of any size with our visual builder. ..."

**Scores**:
- Formal↔Casual: **2** (Casual). Evidence: contractions "we're", "drag drop done" frasi corte, jargon 4.2% (sotto soglia 7%).
- Funny↔Serious: **4** (Serious). Evidence: "zero coding hell" è light humor singolo, ma overall subject trattato literally.
- Respectful↔Irreverent: **3** (Neutral). Evidence: pronoun ratio 0.78 (we/you balanced), no provocative lexicon, "internet of stuff" è playful non irreverent.
- Enthusiastic↔Matter-of-fact: **2** (Enthusiastic). Evidence: 1.8 exclamations per 100w, "10,000+" superlative, no emoji.

**Derived metrics**:
- Jargon density: 4.2%
- Pronoun ratio (we/you): 0.78
- Avg sentence: 12.4 words
- CTA style: imperative ("Get started free", "Try Make")
- Exclamation: 1.8 per 100w

**Summary label**: "Casual + Serious + Neutral + Enthusiastic"

### Esempio 2 — Linear.app (homepage 2026)

**Corpus** (87 parole — minimalistic!):

→ **`insufficient_evidence: true`**, output skip + suggerimento "espandi corpus con about + 5 latest blog posts".

### Esempio 3 — JPMorgan Chase enterprise (white paper)

**Scores**:
- Formal↔Casual: **1** (Very formal)
- Funny↔Serious: **5** (Very serious)
- Respectful↔Irreverent: **1** (Very respectful)
- Enthusiastic↔Matter-of-fact: **5** (Very matter-of-fact)

**Summary label**: "Very formal + Very serious + Very respectful + Very matter-of-fact" — classic enterprise B2B.

## Anti-pattern ToV scoring

- **NO score senza ≥3 evidence quotes per dim** — output blocked
- **NO score su corpus <200 parole** — `insufficient_evidence`
- **NO derived metrics inventate** — sempre computed da script
- **NO bias score senza rubric reference** — sempre check rubric prima di scorare

## Reference

- [Nielsen Norman Group — Four Dimensions of Tone of Voice (2016, canonical 2026)](https://www.nngroup.com/articles/tone-of-voice-dimensions/)
- [NN/G — Impact of Tone of Voice on Users' Brand Perception](https://www.nngroup.com/articles/tone-voice-users/)
- `research/research-summary.md` RQ2 — derivazione metriche
- `skills/tov-analyzer/SKILL.md` — implementazione
