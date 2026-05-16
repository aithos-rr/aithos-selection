# Keyword Research Frameworks 2026

> Reference doc per skill `keyword-research`. Pillar+cluster, search intent classification, semantic clustering, long-tail post AI Overview.

## Pillar + Cluster — modello dominante

### Definizione

[secondary, [brafton.com](https://www.brafton.com/blog/strategy/topic-cluster-content-strategy/)]:

> «A topic cluster content strategy organizes written content around a main idea using a central pillar page and supporting cluster articles»

Origine: HubSpot 2017 [Mintz/Halligan]. Evoluzione 2026: integrato con semantic search + topical authority signal.

### Performance signal

> «Websites with clear topic cluster architecture see 34% more organic traffic growth than those stuck with traditional blog structures» [secondary]

### Anatomia

```
Pillar Page (3000-5000 word)
├── Cluster Article 1 (1200-2000 word)
├── Cluster Article 2
├── Cluster Article 3
... (8-15 cluster ideale)
└── Cluster Article N
```

Reciprocal linking:
- Pillar links a tutti i cluster (TOC sezione)
- Cluster links back to pillar (anchor text varied)
- Cluster cross-link tra fratelli (where contextual)

### Pillar identification criteria

Pillar candidato:
- Search volume head (es. ≥1k/mese)
- Difficulty media (KD 30-60)
- Intent informational broad ("ecommerce analytics guide")
- Coverage 360° con sub-topic

### Supporting article criteria

Cluster item:
- Search volume long-tail (es. 50-500/mese)
- Difficulty bassa (KD <30 ideale)
- Intent specifico ("shopify analytics dashboard setup")
- Linkability back to pillar naturale

## Hub + Spoke — variant

Hub generale + spoke specialistici, no pillar singolo:
- Hub = entry-point con TOC link a sezioni
- Spoke = specialized content
- Cross-linking aggressivo

Use case: media/publisher con coverage broad multipli niche.

## Glossary + Pillar — variant

Glossary di 50-200 term entries (entity-rich) + pillar deep-dive.

Boost AI citation via entity density (sopratutto per ChatGPT entity matching).

Use case: B2B technical SaaS, education, complex domain (legal, medical, finance).

## Programmatic SEO — variant

Template + dataset → pagine generate.

Esempio: "[X] in [city]" template → 100+ city pages.

⚠ Linee rosse Helpful Content:
- Ogni pagina deve avere unique value (no duplicate boilerplate)
- Boilerplate% <70% threshold
- User benefit chiaro per page
- No thin content masquerade

Use case: marketplace, directory, listing site.

## Search intent classification

[primary, [Google Search Quality Rater Guidelines](https://services.google.com/fh/files/misc/hsw-sqrg.pdf)]:

| Intent | Pattern signal | Esempio | Strategy |
|--------|----------------|---------|----------|
| `informational` | "how to", "what is", "guide", "tutorial" | "what is google analytics" | Content depth, schema Article |
| `navigational` | brand+name, domain | "ahrefs login" | Brand SERP, schema Organization |
| `transactional` | "buy", "discount", "trial", "signup" | "ahrefs free trial" | Landing page conversion |
| `commercial` | "best", "vs", "review", "alternative" | "ahrefs vs semrush" | Listicle + comparison |

### Intent disambiguation algorithm

Per query ambigua (es. "google analytics"):
1. SERP analysis top 10 — quale intent dominato?
2. AI Overview presence — informational signal
3. Featured snippet — informational
4. Shopping pack / Ads heavy — commercial/transactional
5. Local pack — local intent

→ Mirror SERP intent dominante.

## Semantic clustering — methodology

### Approach 1: Embedding-based

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(keyword_list)
clustering = DBSCAN(eps=0.3, min_samples=3, metric='cosine').fit(embeddings)
```

Output: cluster ID per ogni keyword. Centroid identification: keyword closest to cluster mean.

### Approach 2: Cosine similarity manual (fallback no ML lib)

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(keyword_list)
similarity = cosine_similarity(matrix)
# threshold 0.65 per cluster member
```

### Approach 3: SERP overlap

[advanced, secondary]:

Due keyword nello stesso cluster se le SERP overlap >40% (top 10 results condivisi).

Tool: SERP comparison via Ahrefs Keyword Explorer "Parent Topic".

## Long-tail post-AI Overview

AI Overview ha eroso traffic informational (Google studio Search Console interna mostra -8% to -25% CTR su query head — pattern emergente, no claim numerico esatto).

Risposta strategica 2026:

### Pivot verso commercial + transactional

AI Overview risponde meno volentieri a:
- "best X for Y" — Google non risk "endorsement" via AI
- "buy X discount" — transactional, Google preferisce ads/shopping
- "X review honest" — bias risk

### Long-tail super-specifico

Query 4+ word:
- "come misurare conversion rate ecommerce shopify italiano" (5 word, super-specific)
- AI Overview spesso non triggherato

### Brand + use-case

- "[product] for [persona]" — es. "ahrefs for content writer"
- "[product] vs [alternative] for [use-case]"

### Local intent

- "near me", "[city] [service]"
- Map pack + GBP boost

## Volume estimation senza API

Fallback methodology:

### Tier 1: Search Console (own data)

- Query data 90gg → impressions per keyword
- Reflect pattern domain-specific

### Tier 2: Google Trends

- Trend relativo (no absolute volume)
- Geo-specific, time-specific
- Bucketing: high/medium/low

### Tier 3: Bucketing manuale

- Heuristic basato su query length + commerciality
- "low <100", "medium 100-1k", "high >1k"
- Flag: `volume_estimated_no_api: true`

## Difficulty estimation senza API

Fallback methodology:

### SERP analysis

- Top 10 ranking domains:
  - Hubris brand (NYT, Forbes, Wikipedia) → high difficulty
  - Niche bloggers / forums → low difficulty
  - Mixed → medium

### Backlink count manual

- Top 3 ranking URL backlink count via Ubersuggest free
- High (>1000) → difficulty high
- Medium (100-1000) → difficulty medium
- Low (<100) → difficulty low

## Opportunity score formula

```
opportunity_score = (
  log10(volume + 1) * 20 *           # volume importance
  (100 - difficulty) / 100 *          # easier = better
  intent_weight                       # commercial+transactional bonus
)
```

`intent_weight`:
- transactional/commercial = 1.5
- informational = 1.0
- navigational = 0.3 (low ROI per non-brand owner)

Score buckets:
- 80-100: priority high — quick win likely
- 60-79: priority medium — stable opportunity
- 40-59: priority low — long-term play
- <40: skip o re-evaluate

## Anti-pattern keyword research

1. **Keyword stuffing in body** — over-optimization
2. **Exact-match domain abuse** — algorithmic detection
3. **Cluster overlap excessive** — multiple page same intent → cannibalization
4. **Mismatch intent** — content informational ranking commercial query (no user satisfaction)
5. **Hyper-targeting low-volume** — diminishing return effort/result
6. **Branded competitor abuse** — paid keyword on competitor brand → trademark issue

## Sources

### Primary

- [Google Search Quality Rater Guidelines](https://services.google.com/fh/files/misc/hsw-sqrg.pdf)
- [Google Search Central — keyword guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)

### Secondary

- [HubSpot — topic cluster origin](https://blog.hubspot.com/marketing/topic-clusters-seo)
- [brafton.com — topic cluster strategy 2026](https://www.brafton.com/blog/strategy/topic-cluster-content-strategy/)
- [searchengineland.com — topic clusters guide](https://searchengineland.com/guide/topic-clusters)
- [Ahrefs Blog — keyword research](https://ahrefs.com/blog/keyword-research/)
- [SEMrush Blog — keyword research](https://www.semrush.com/blog/keyword-research/)
- [stackmatix.com — pillar+cluster structure](https://www.stackmatix.com/blog/pillar-page-topic-cluster-strategy)
