# GEO — Generative Engine Optimization 2026

> Reference doc per skill `geo-optimizer` + main agent. Citation patterns ChatGPT/Perplexity/Claude/Gemini, llms.txt protocol (Jeremy Howard, 2024-09-03), schema FAQPage caveat, 8 GEO-specific patterns.

## Definizione

GEO = «practice of optimizing your content to appear as sources and citations in AI-generated responses from platforms like ChatGPT, Perplexity, Google AI Overviews, and Claude» [secondary, [frase.io](https://www.frase.io/blog/what-is-generative-engine-optimization-geo)].

## Citation patterns per platform

[secondary, [aimagicx.com](https://www.aimagicx.com/blog/generative-engine-optimization-chatgpt-perplexity-2026), Previsible 2025 AI Traffic Report]:

| Platform | Top sources | Format preference | Key signal |
|----------|-------------|---------------------|------------|
| **ChatGPT** | Wikipedia 47.9%, news, edu | Single-paragraph definitions | Authority + factual density |
| **Perplexity** | Reddit 46.7%, recent (<90gg) | Bulleted form | Freshness + community signal |
| **Claude** | Synthesizes vs quote diretto, less documented | Question-format H2 | Structured answers paragraphs |
| **Gemini** | Pattern simile Google AI Overview | Schema markup heavy | Article + Organization + Author |

⚠ **Disclaimer**: % citation pattern dati sono `secondary` source (aggregated by aimagicx, Previsible). Nessun vendor LLM pubblica primary citation stat ufficialmente. Output skill include disclaimer.

## Crescita del canale

«AI-referred sessions jumped 527% YoY in the first five months of 2025» [secondary, Previsible 2025 AI Traffic Report].

→ Trend non ignorabile per chiunque pubblica content.

## llms.txt — primary spec

[primary, [llmstxt.org](https://llmstxt.org/)]:

Proposta da **Jeremy Howard, 3 settembre 2024**.

### Format

File markdown a `<domain>/llms.txt`:

1. **H1 heading** (required) — project/site name
2. **Blockquote** (optional) — summary key info
3. **Detail sections** (optional) — paragrafi/liste contesto
4. **H2-delimited file lists** (optional) — markdown links + descriptions
5. **"Optional" section** — secondary resources skippabili in context corti

Companion file: `.md` versions di HTML pages al stesso URL + `.md` appeso (es. `page.html.md`). Tool CLI: `llms_txt2ctx` per generare `llms-ctx-full.txt`.

### Adoption status (April 2026)

[secondary, multi-source aggregated]:

- Adopters: **Anthropic, Stripe, Zapier, Cloudflare, Mintlify**
- **GPTBot e Microsoft crawlers** fetcham attivamente llms.txt + llms-full.txt
- **Caveat critico**: «crawling a file doesn't mean using it for anything meaningful» [aeoengine.ai]
- Nessun major (OpenAI, Google, Anthropic) ha pubblicamente confermato di leggerlo per ranking
- Standard status: «community convention with no backing from W3C, IETF, or any recognised standards body»

### Tactical recommendation

Implement llms.txt come **"low risk, potential upside"**:
- Costo implementation: ~30 min one-time
- Manutenzione: aggiorna quando aggiungi pillar nuovo
- Risk: zero (file ignorato silenziosamente se non usato)
- Upside: positioning defensive per AI search era

## 8 GEO-specific patterns

Sintesi multi-fonte:

### 1. Q&A heading structure

H2 in formato domanda diretta:

❌ Bad: `## Pillars of analytics`
✅ Good: `## Quali sono i pillar dell'analytics ecommerce?`

Boost: Claude (question-format H2 preference) + Perplexity citation.

### 2. Citation density

1 citation autorevole ogni 200-300 parole.

Formato preferred:
- Inline link `[anchor](URL)` con anchor descriptive
- Citation a primary source (research papers, government, industry leader)
- Avoid generic "click here", "read more"

Boost: ChatGPT credibility signal + E-E-A-T.

### 3. Original data publication

- Tabelle stats (proprietary)
- Sondaggi (1k+ respondents ideale)
- Benchmark (es. "industry benchmark X = Y")
- Case study con metric reali (anonimizzati se confidential)

Boost: Wikipedia-grade content potential, citation magnet.

### 4. Schema FAQPage + Article + HowTo nesting

Entity depth 2026:

```
Article {
  author: Person {
    sameAs: [LinkedIn, Twitter, Wikidata]
  }
  publisher: Organization {
    sameAs: [...]
  }
  mainEntity: FAQPage {
    Question[] { acceptedAnswer: Answer }
  }
}
```

Tier 1 schema per AI Overview citation [secondary, wpriders].

⚠ **HowTo deprecated** — fallback Article + nested ItemList.
⚠ **FAQPage rich result eligibility ristretta** — vedi schema-markup-guide-2026.md DECISION-006.

### 5. Author bio + bylines

Mandatory per E-E-A-T (Google) ed eredità GEO:
- Author name visibile
- Bio breve (50-150 word) con credentials
- LinkedIn / Twitter / Wikidata sameAs link
- Author archive page (1 author = 1 dedicated page)

Boost: Google E-E-A-T + LLM citation trust signal.

### 6. Reddit niche presence

[secondary, citation pattern Perplexity 46.7%]:

- Identifica r/<niche> rilevanti (3-5 subreddit)
- Top contributor presence (post non-promo, AMA, helpful answers)
- Brand mention organic + community trust
- NO posting promotional spam (mod ban risk)

Boost: Perplexity citation + organic referral traffic.

### 7. Update timestamp visibile

- `dateModified` schema field aggiornato
- Visible "Updated YYYY-MM-DD" in UI (sopra/sotto title)
- Refresh cycle 90gg per pillar (Perplexity freshness window)

Boost: Perplexity freshness <90gg signal.

### 8. llms.txt + llms-full.txt

Defensive layer (vedi sezione llms.txt sopra).

## GEO vs Traditional SEO

| Dimensione | SEO classico | GEO |
|------------|--------------|-----|
| Target | Google SERP top 10 | LLM citation in answer |
| Metrica | Traffic, position, CTR | Mention rate, citation count |
| Tool | Ahrefs, SEMrush, GSC | Scrunch, LLMrefs, Profound, Quattr |
| KPI primario | Organic sessions | AI-referred sessions (UTM custom) |
| Update frequency | Rank tracking weekly | AI mention tracking weekly/daily |

## Tool ecosystem GEO 2026

[secondary, [scrunch.com](https://scrunch.com/blog/best-answer-engine-optimization-aeo-generative-engine-optimization-geo-tools-2026)]:

| Tool | Pricing | Strengths | Weak |
|------|---------|-----------|------|
| **Scrunch** | $99-499/mese | First-mover, dashboard mature | Categoria nuova |
| **LLMrefs** | $99/mese | GEO citation tracking dedicated | Limited language |
| **Profound** | Enterprise | Ent-grade tracking | Pricey |
| **Quattr** | Free trial + paid | All-in-one AI search visibility | Less specialized |
| **Manual prompting** | Free | Qualitative testing | Non scalabile |

Default per `lt100` budget: manual prompting + recommendation list output.

## AI-referred sessions tracking

UTM tagging custom:
- `?utm_source=chatgpt.com`
- `?utm_source=perplexity.ai`
- `?utm_source=claude.ai`

⚠ **Caveat**: molti LLM strippano UTM. Workaround:
- Referrer header check (non sempre disponibile, privacy mode strips)
- Custom analytics setup (server-side detection)
- Brand search increase post-AI-citation (proxy metric)

## Robots.txt for AI crawlers

User-agents da considerare per allow/disallow:

```
User-agent: GPTBot
User-agent: ChatGPT-User
User-agent: PerplexityBot
User-agent: anthropic-ai
User-agent: Claude-Web
User-agent: Bytespider
User-agent: Google-Extended  # Google AI training opt-out
```

Decisione strategica:
- **Allow tutti** = max GEO opportunity
- **Allow selettivi** (es. allow GPTBot, disallow Google-Extended) = GEO ma opt-out Google AI training
- **Block tutti** = legacy SEO only, skip GEO totalmente

Default per `/seo-strategist` se Q6=`priority` o `secondary`: suggest allow GPTBot + ChatGPT-User + PerplexityBot + anthropic-ai + Claude-Web.

## Sources

### Primary

- [llmstxt.org — official spec](https://llmstxt.org/)
- [Anthropic robots.txt — anthropic-ai user-agent](https://docs.anthropic.com/en/docs/build-with-claude/agents-and-tools/web-search-tool)
- [OpenAI GPTBot user-agent](https://platform.openai.com/docs/gptbot)
- [Perplexity PerplexityBot crawler](https://docs.perplexity.ai/guides/bots)

### Secondary

- [frase.io — GEO definition](https://www.frase.io/blog/what-is-generative-engine-optimization-geo)
- [aimagicx.com — GEO citation patterns](https://www.aimagicx.com/blog/generative-engine-optimization-chatgpt-perplexity-2026)
- [derivatex.agency — llms.txt guide](https://derivatex.agency/blog/llms-txt-guide/)
- [aeoengine.ai — llms.txt adoption analysis](https://aeoengine.ai/blog/llms-txt-zero-usage-ai-bots-ignore)
- [scrunch.com — GEO/AEO tools 2026](https://scrunch.com/blog/best-answer-engine-optimization-aeo-generative-engine-optimization-geo-tools-2026)
- [almcorp.com — GEO complete guide](https://almcorp.com/blog/generative-engine-optimization-complete-guide/)
- [llmrefs.com — GEO 2026 guide](https://llmrefs.com/generative-engine-optimization)
