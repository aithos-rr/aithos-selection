---
name: geo-optimizer
description: Generative Engine Optimization (GEO) per page/site — ottimizzazione content per essere citato da ChatGPT, Perplexity, Claude, Gemini. Genera llms.txt + llms-full.txt protocol-compliant (Jeremy Howard spec, 2024-09-03), schema FAQPage Tier 1 (con caveat eligibility Google rich result vs LLM citation), citation density check, source authority signals review, format optimization platform-specific (ChatGPT single-paragraph, Perplexity bulleted, Claude question-format H2). Anti-hallucination — citation pattern data sono `secondary` source (no primary stat dai vendor LLM), output con disclaimer trasparente.
when_to_use: Aggiungere layer GEO a pillar pages esistenti, creare llms.txt per dominio nuovo, audit citation potential pre-publication, GEO score per content piece, GEO citation tracking setup
---

# GEO Optimizer

Skill che applica patterns GEO (Generative Engine Optimization) 2026 per massimizzare LLM citation across ChatGPT, Perplexity, Claude, Gemini.

## Scope

- **In scope**: llms.txt + llms-full.txt generation (Jeremy Howard spec), schema FAQPage Tier 1, citation density audit, source authority audit, format optimization platform-specific, GEO score calculation
- **Out of scope**: full content rewrite (suggerisce modifiche, non rigenera articolo), keyword research (vedi `keyword-research`), backlink strategy

## Context grounded

Citation patterns (research-summary RQ2):

| Platform | Top source pattern | Format preference |
|----------|---------------------|---------------------|
| ChatGPT | Wikipedia 47.9% top sources | Single-paragraph definitions |
| Perplexity | Reddit 46.7% + freshness <90gg | Bulleted form |
| Claude | Synthesizes vs quote | Question-format H2 |
| Gemini | Pattern simile Google AI Overview | Schema markup weight high |

⚠ **Disclaimer**: % citation pattern dati sono `secondary` source via Previsible report + aimagicx aggregator. Nessun vendor LLM pubblica primary citation stat. Output skill include disclaimer.

## Input contract

```yaml
target_url: https://example.com/blog/topic  # required
target_topic: "ecommerce analytics guide"
geo_priority_level: priority | secondary  # da Q6 discovery, skip se Q6=skip
target_platforms: [chatgpt, perplexity, claude, gemini]  # multi-select default all
existing_content_html: optional path  # se non scrape automatic
```

## Methodology

### Step 1 — Page audit

Fetch target URL (WebFetch o Playwright se JS-heavy):
1. Extract title, h1, h2, h3 hierarchy
2. Word count
3. Content date (dateModified schema or <time> tag)
4. Existing schema (Article? FAQPage? Author?)
5. Author byline presence
6. Citation count (a tags external to authoritative sources)
7. Internal link count

### Step 2 — GEO score calculation

Score 0-100 multi-dimension:

```
geo_score = (
  q_format_h2 * 15 +           # question-format H2 presence (Claude/Perplexity)
  citation_density * 20 +       # 1 citation / 250 word ideal
  schema_completeness * 20 +    # Article + FAQPage + Author + dateModified
  author_authority * 15 +       # byline + bio + sameAs LinkedIn/Twitter
  freshness * 10 +              # dateModified <90gg = full point (Perplexity)
  llms_txt_presence * 10 +      # site has /llms.txt
  bulleted_content * 10         # bulleted lists per Perplexity
)
```

Score buckets:
- 80-100: GEO-optimized (likely citable)
- 60-79: good baseline, minor gaps
- 40-59: moderate gaps, focused fix needed
- <40: significant gaps, major rewrite suggested

### Step 3 — Recommendation generation

Output prioritized list of fix:

```markdown
## GEO Recommendations — <URL>

**Score**: 62/100 (good baseline)

### High priority
1. **Add Question-format H2** (current: 0/8 H2 question-format) — boost Claude/Perplexity citation
   - Suggest: convert "Pillars of analytics" → "Quali sono i pillar dell'analytics ecommerce?"
2. **Increase citation density** (current: 1/1200 word, target 1/250) — boost ChatGPT credibility
   - Suggest: add 3 authoritative source link (industry report, primary research)

### Medium priority
3. **Add author bio with sameAs** (currently no author byline)
4. **Update dateModified** — content 14 mesi vecchio, refresh per Perplexity freshness window

### Low priority
5. **Add llms.txt to site root** (see llms.txt generation below)
```

### Step 4 — llms.txt generation

Format Jeremy Howard spec (2024-09-03) [primary, llmstxt.org]:

```markdown
# <Site name>

> <Site summary 1-2 sentence>

<Detail context>

## Docs

- [Pillar 1 title](https://example.com/pillar-1.md): description
- [Pillar 2 title](https://example.com/pillar-2.md): description

## Optional

- [Lower priority resource](https://example.com/x.md): description
```

Output `llms.txt` placed at `https://example.com/llms.txt` root.

Companion `.md` versions per pillar pages: `https://example.com/pillar-1.html.md` (markdown rendering of HTML).

### Step 5 — Schema FAQPage Tier 1 (con caveat)

DECISION-006: schema FAQPage utile per LLM citation anche se site non eligible Google rich result.

Genera schema FAQPage da Q&A nel content:
1. Detect Q&A structure (H2 question + paragraph answer)
2. Output JSON-LD FAQPage
3. Validate via `schema_generator.py --validate`
4. Include warning se site_type ∉ {government, health, education_authority}: «Google rich result NON eligible per il tuo site type. Schema mantenuto per LLM citation (ChatGPT/Perplexity/Claude).»

### Step 6 — Format optimization per platform

Platform-specific suggestions:

| Platform | Recommendation |
|----------|----------------|
| ChatGPT | Single-paragraph definitions ai inizio sezione |
| Perplexity | Bulleted lists frequenti + freshness <90gg + Reddit niche presence (off-page) |
| Claude | H2 question-format consistent + structured answer paragraphs |
| Gemini | Schema markup heavy (Article + Organization + Author) |

## Output JSON schema

```json
{
  "target_url": "https://example.com/blog/topic",
  "target_topic": "ecommerce analytics guide",
  "audit_date": "2026-05-01",
  "geo_score": 62,
  "score_buckets": {
    "q_format_h2": 0.4,
    "citation_density": 0.3,
    "schema_completeness": 0.7,
    "author_authority": 0.5,
    "freshness": 0.6,
    "llms_txt_presence": 0,
    "bulleted_content": 0.7
  },
  "recommendations": [
    {"priority": "high", "category": "q_format", "fix": "..."},
    {"priority": "medium", "category": "author", "fix": "..."}
  ],
  "llms_txt_generated": "output/llms.txt",
  "schema_faqpage_generated": "output/schema-faqpage.json",
  "platform_optimization": {
    "chatgpt": ["..."],
    "perplexity": ["..."],
    "claude": ["..."],
    "gemini": ["..."]
  },
  "anti_hallucination_disclaimer": "Citation pattern % sono secondary source aggregati (Previsible report + aimagicx). Nessun vendor LLM pubblica primary citation stat ufficialmente."
}
```

## Anti-hallucination contract

- Citation pattern % (47.9% Wikipedia ChatGPT, 46.7% Reddit Perplexity) sono **secondary** — disclaimer obbligatorio in output
- Mai claim "garantito citato" o "+X% citation" — GEO è probabilistic, non deterministic
- llms.txt adoption status: «not yet read by major LLMs ufficialmente per ranking, low-risk strato defensive» — quote in output
- HowTo schema MAI default (deprecated 2023)
- FAQPage warning per non-eligible site type mandatory

## Edge cases

1. **Page <500 word** → GEO score limitato, suggest content expansion prima di optimization
2. **JS-heavy SPA no SSR** → fetch fallback PSI API + warning
3. **No author byline** → high priority fix (E-E-A-T critical signal)
4. **content >18 mesi vecchio** → freshness penalty + suggest re-write
5. **Q6=skip** → skill not loaded (gated da main agent, DECISION-011)
6. **Site no robots.txt allow GPTBot/PerplexityBot/anthropic-ai** → flag + suggest update robots.txt

## Tool integration

| Tool | Method | Note |
|------|--------|------|
| Scrunch | UI dashboard | $99-499/mese, GEO tracking ufficiale |
| LLMrefs | UI dashboard | Citation tracking |
| Profound | UI dashboard | Enterprise |
| Quattr | UI dashboard | AI search visibility |
| Manual prompting | ChatGPT/Perplexity browser | Free, qualitative testing |

Default: manual prompt testing (free) + recommendation list output.

## CLI invocation

```bash
python3 scripts/audit_onpage.py \
  --url https://example.com/blog/topic \
  --geo-mode \
  --target-platforms chatgpt,perplexity,claude,gemini \
  --output output/geo-audit-001.json
```

## Output downstream

GEO audit JSON → consumed da:
- Main agent Fase 5 (technical fix + GEO layer)
- `/document-factory` (PDF GEO recommendation report)
- Schema files → injection in CMS template

## References

- `references/geo-generative-engine-optimization-2026.md` — citation patterns + llms.txt + 8 GEO patterns + platform-specific
- `references/schema-markup-guide-2026.md` — schema FAQPage caveat + Article gold standard

## Examples

### Example 1: Pillar page existing

Input: target_url=https://shop.example.com/guide/analytics-ecommerce, geo_priority_level=priority.

Output: GEO score 58, 7 recommendation (high: q-format H2 + citation density; medium: author bio + dateModified refresh; low: llms.txt site root). llms.txt generato per dominio root con 5 pillar listed. Schema FAQPage extracted da 6 Q&A in body.

### Example 2: New site greenfield + GEO priority

Input: target_url=https://example.com (homepage), target_topic="ecommerce analytics SaaS".

Output: GEO score 35 (significant gaps), recommendation prioritize: schema Organization + Author profiles + create llms.txt prima di publish 1° pillar + setup robots.txt allow GPTBot/PerplexityBot.
