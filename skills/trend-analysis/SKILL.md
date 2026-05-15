---
name: "trend-analysis"
description: "Analizza trend di mercato e competitor sui social con Agent Teams paralleli. Per ogni competitor, estrae i top post 30gg, identifica topic che funzionano (engagement per topic), segnala pattern e opportunità. Output: report evidence-based con citazioni ai post originali. Da usare per intelligence competitiva, discovery topic trend, analisi social. Skill del Webinar 2 Claude Code per il GTM."
when_to_use: "Intelligence competitiva, social listening, trend discovery, analisi contenuti competitor, brief marketing, content strategy"
argument-hint: "\"<competitor-list-or-keyword>\""
allowed-tools: "Read Write Bash"
---
# Trend Analysis

5 Agent Teams paralleli scandagliano LinkedIn/Twitter/YouTube dei competitor, estraggono top post/video engagement, classificano per topic, producono report con insight azionabili + citazioni verificabili.

## When to use

Attiva quando:
- Content strategy: "cosa sta funzionando nel nostro settore?"
- Competitor intelligence: "cosa stanno facendo X e Y?"
- Brief cliente: serve context market prima di proposta
- Product strategy: feature request trend

**Non attivare** se:
- Lista competitor ignota (→ `/research-notebook` prima per scoprirli)
- Richiesta troppo generica ("tutto quello che c'è sul mercato")
- Nicchia troppo piccola (<5 competitor → manual review meglio)

## Prerequisiti

- Apify account (per LinkedIn scraping)
- parallel-cli installato
- Lista competitor (o keyword per scoprirli)

## Instructions

### Fase 1 — Define scope

Chiedi all'utente (AskUserQuestion):

1. **Competitor**: lista (min 3, max 15) o keyword per scoprire
2. **Piattaforme**: LinkedIn / Twitter / YouTube / tutte
3. **Orizzonte**: 30gg / 90gg / 6 mesi
4. **Focus**: topic trending / messaging / format (video vs text) / frequency

### Fase 2 — Discovery (se serve)

Se l'utente ha solo keyword:
```bash
parallel-cli research "top competitors for <keyword>" --depth deep
```
→ lista 5-10 competitor candidati, utente conferma via AskUserQuestion.

### Fase 3 — Agent Teams parallel

Spawna 1 agent per competitor (max 5 paralleli per rate limit):

```python
for competitor in competitors:
    agent.spawn(
        task=f"Analyze {competitor} social presence",
        tools=[apify_scraper, parallel_cli, youtube_api],
        timeframe="<orizzonte>"
    )
```

Ogni agent raccoglie:
- **LinkedIn**: top 20 post per reactions/comments
- **Twitter**: top 20 tweet per retweet/likes
- **YouTube**: top 10 video per views
- **Metadata**: frequency posting, tempo di vita engagement, audience response

### Fase 4 — Topic clustering

Aggregati tutti i contenuti (~100-300 items):

```python
topics = cluster_by_theme(contents, method="semantic_embedding")
# Output: lista {topic_name, items: [...], engagement_total, engagement_avg}
```

Esempi topic emergenti:
- "AI productivity hacks"
- "Founder journey storytelling"
- "B2B SaaS pricing transparency"
- "Remote work culture"
- "Hiring process democratization"

### Fase 5 — Evidence-based insight

Per ogni top-N topic (>15% engagement):

- **What**: descrizione 1 frase
- **Who**: quali competitor stanno su questo topic
- **How**: format preferito (video/text/carosello)
- **When**: cadenza (daily/weekly/occasional)
- **Why it works**: 2-3 motivi basati su engagement pattern
- **Evidence**: 3 post esempio con link originale
- **Opportunità per te**: 1-2 angoli differenziati da adottare

### Fase 6 — Report con citazioni

```markdown
# Trend Analysis — <settore/keyword>
Periodo: <start> → <end>
Competitor analizzati: <lista>

## Executive summary
<3 insight principali — 1 riga ciascuno>

## Top 5 Topic trending

### 1. <Topic name> (engagement X% totale)
- **Who**: [Competitor A](link-profilo), [Competitor B](link)
- **Best format**: video 60-90sec
- **Cadenza**: 2-3/settimana
- **Why works**: <3 motivi>
- **Evidence**:
  - [Post A: "..."](<link>) — 2.3k reaction
  - [Post B: "..."](<link>) — 1.8k reaction
  - [Post C: "..."](<link>) — 1.5k reaction
- **Opportunità per te**: <angolo>

### 2. ...

## Format analysis
| Format | Avg engagement | Best performer |
|---|---|---|
| Carosello LI | 450 | Competitor X |
| Video <1min | 890 | Competitor Y |
| ... | ... | ... |

## Cadenza
<chi posta quando, gap di mercato — es. "weekend undercovered">

## Raccomandazioni azionabili
1. <concreto con priorità>
2. ...
3. ...
```

## Examples

### Esempio 1: Filippo — GTM Engineering competitor

Competitor: Clay, Apollo, Outreach, Gong, HubSpot, Reply.io
Orizzonte: 90gg
Output: 5 topic (AI sales agents, RevOps stack, data enrichment, outreach orchestration, revenue attribution)
Insight: "Nessun competitor italiano dominant su topic — opportunità per YT branding"

### Esempio 2: Learnn — EdTech italiano

Competitor: Talent Garden, Ninja Academy, Start2Impact, Onepiece
Focus: quali corsi AI stanno lanciando
Output: trend "AI for marketers" mainstream, "Claude specifico" underserved (validazione per Claude Week)

## Gotchas

- 🔴 **Scraping LinkedIn diretto = ban**: usa Apify o Sales Nav API ufficiale. Mai scraping anonimo.
- 🔴 **Evidence obbligatorie**: ogni insight deve linkare post originale. Senza evidence = opinione, non analisi.
- 🟡 **Bias del recente**: post recenti hanno meno engagement accumulato. Normalizza per età (engagement/gg).
- 🟡 **Vanity metrics**: like != interesse commerciale. Comment depth + save > like puro.
- 🟢 **Update quarterly**: trend shiftano. Re-run ogni 3 mesi per tracking longitudinale.
- 🟢 **Cross con /outbound-campaign**: topic trending → hook outbound rilevante.

## Scripts

- `scripts/discover_competitors.py`: se keyword → lista competitor
- `scripts/scrape_competitor.py`: Apify LinkedIn + Twitter + YouTube
- `scripts/cluster_topics.py`: semantic clustering contents
- `scripts/extract_insights.py`: evidence + opportunità
- `scripts/generate_report.py`: markdown report

## References

- `references/topic-taxonomy.md`: 50 topic comuni per settore B2B/B2C
- `references/engagement-normalization.md`: formule per normalizzare metriche cross-platform
- `references/evidence-rubric.md`: criteri per citare evidence affidabili

## Crediti

Skill originale Claude Week Learnn — Webinar 2 (Code GTM). Ispirato a [daymade/competitors-analysis](https://github.com/daymade/claude-code-skills) (evidence-based methodology).
