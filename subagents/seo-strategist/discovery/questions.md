# Discovery Questions — `/seo-strategist`

> 8 domande sequenziali via `AskUserQuestion`. Salvataggio in `<memory>/config.md` schema YAML. Re-prime su run successivi.

## Filosofia discovery

L'agent sa **chi sei**, **dove parti**, **dove vuoi andare**, **con che tool**, **con che vincoli budget/legali**. Ogni domanda ha conseguenza tattica (skill load, framework choice, fallback active).

**Audience**: marketer, founder, PM, content strategist, SEO specialist, freelancer SEO. Linguaggio business-friendly, zero developer jargon.

**Lingua domande**: italiano. **Lingua field tecnici**: inglese (kebab-case).

---

## Q1 — Ruolo

**Header**: `Ruolo`
**Question**: «Qual è il tuo ruolo principale rispetto a questo progetto SEO?»
**Type**: single-select
**Options**:

- `founder` — Founder/CEO che vuole crescita organica per business
- `marketing_manager` — Marketing manager che gestisce SEO + altri canali
- `seo_specialist` — SEO specialist dedicato con expertise tecnica
- `content_strategist` — Content strategist focus pillar+cluster
- `agency` — Agency che lavora su clienti diversi

**Saves to**: `user.role`

**Conseguenze**:

- `founder` → output focus high-level + ROI + opportunity cost. Skip technical jargon profondo.
- `marketing_manager` → output focus pillar+cluster + tracking + reporting per board. Quick-win priority.
- `seo_specialist` → output deep technical + INP analysis + schema validation + competitive gap detail.
- `content_strategist` → focus content gap + topic cluster mapping + brief generation + GEO patterns.
- `agency` → multi-client mode → suggest output template-friendly per replicare su altri client.

---

## Q2 — Stack SEO

**Header**: `Stack`
**Question**: «Qual è il tuo SEO tool primario di lavoro?»
**Type**: single-select
**Options**:

- `ahrefs` — Ahrefs (free webmaster tools o paid)
- `semrush` — SEMrush (free 10 query/day o paid)
- `moz` — Moz Pro
- `se_ranking` — SE Ranking
- `search_console_only` — Solo Google Search Console (no SEO suite)
- `none` — Nessuno, partiamo da zero

**Saves to**: `stack.seo_primary`

**Conseguenze**:

- `ahrefs` → carica `references/tool-ecosystem-seo-2026.md` sezione Ahrefs + saving credit advice (rate limit)
- `semrush` → fallback path se rate limit free (10 query/day)
- `moz` → DA-based scoring instead of DR
- `se_ranking` → cost-effective recipe + agency-friendly multi-project
- `search_console_only` → primary data source = own site SC + Ubersuggest free + workaround per competitor data
- `none` → recommend stack basato su budget Q8

Sub-question implicit: "Search Console connected for own site?" → `stack.search_console_connected: bool`

---

## Q3 — Tipo sito

**Header**: `Site`
**Question**: «Che tipo di sito stiamo ottimizzando?»
**Type**: single-select
**Options**:

- `saas_b2b` — SaaS B2B
- `ecommerce` — eCommerce
- `content_blog` — Blog / publisher / media
- `local` — Local business (ristorante, dentista, agenzia immobiliare)
- `agency` — Agency / consulting site

**Saves to**: `site.type`

**Conseguenze**:

- `saas_b2b` → keyword strategy commercial + comparison + use-case per persona; schema Product + Article
- `ecommerce` → schema Product + AggregateRating + breadcrumb mandatory; programmatic SEO category pages
- `content_blog` → pillar+cluster strategy heavy; schema Article + Author authority focus
- `local` → schema LocalBusiness + GBP optimization + geo modifier keyword
- `agency` → portfolio + case study schema; keyword "agency for [niche]" longtail

---

## Q4 — Stadio SEO

**Header**: `Stage`
**Question**: «In che stadio ti trovi con il tuo SEO?»
**Type**: single-select
**Options**:

- `greenfield` — Sito nuovo, partiamo da zero
- `decay` — Traffic in calo, serve recovery
- `plateau` — Traffic stabile, serve sblocco crescita
- `scaling` — Traffic in crescita, scaliamo content + tecnico

**Saves to**: `site.stage`

**Conseguenze**:

- `greenfield` → priority order: technical foundation → keyword research → pillar 1-3 → backlink seed
- `decay` → priority order: Google update timing check → content audit decay pages → technical regression check → recovery plan
- `plateau` → priority order: gap analysis vs competitor → content refresh top performer → expand cluster → GEO layer
- `scaling` → priority order: scale content production safely → strengthen E-E-A-T signal → expand internal linking → digital PR campaign

---

## Q5 — Geografia target

**Header**: `Geo`
**Question**: «Qual è la geografia target del tuo SEO?»
**Type**: single-select
**Options**:

- `italia` — Italia
- `europa` — Europa (multi-paese EU)
- `usa` — USA
- `worldwide` — Worldwide (con focus EN)
- `multi_paese` — Multi-paese specifico (es. IT+ES+FR)

**Saves to**: `geo.target`

**Conseguenze**:

- `italia` → `geo.geo_eu_detected: true` → GDPR mode auto-attivo (DECISION-008) + Garante 2024 specifics; lingua content IT primary
- `europa` o `multi_paese` con paesi EU → GDPR mode auto-attivo + multi-language hreflang strategy
- `usa` → GDPR skip default; CCPA awareness sub-flag; lingua EN
- `worldwide` → hreflang + canonical strategy + multi-region CDN consideration
- `multi_paese` → trigger `hreflang_required: true` + reciprocal link mapping

---

## Q6 — GEO priority

**Header**: `GEO`
**Question**: «Vuoi ottimizzare per essere citato da AI come ChatGPT, Perplexity, Claude (oltre Google)?»
**Type**: single-select
**Options**:

- `priority` — Sì, priorità alta — voglio essere citato da AI in modo aggressivo
- `secondary` — Sì, secondario — solo per pillar pages principali
- `skip` — No, focus solo SEO Google classico

**Saves to**: `strategy.geo_llm_optimization`

**Conseguenze** (DECISION-011):

- `priority` → skill `geo-optimizer` carica per ogni content piece + suggest llms.txt creation + schema FAQPage tier 1
- `secondary` → skill `geo-optimizer` solo per pillar pages (top 5-10 per cluster)
- `skip` → skill `geo-optimizer` skip totalmente; focus SEO classico Google/Bing

---

## Q7 — Volume content

**Header**: `Volume`
**Question**: «Quanti content piece pubblichi al mese (o pianifichi di pubblicare)?»
**Type**: single-select
**Options**:

- `lt5` — Meno di 5
- `5_15` — 5-15
- `15_50` — 15-50
- `50plus` — 50+ (programmatic SEO o team contenuto strutturato)

**Saves to**: `strategy.content_volume`

**Conseguenze**:

- `lt5` → focus quality over quantity; ogni piece deve essere pillar-grade; refresh strategy aggressive
- `5_15` → balanced cluster strategy; 1 pillar/mese + 4 supporting
- `15_50` → topic cluster scalata; assembly line content brief; QA rigoroso per Helpful Content compliance
- `50plus` → programmatic SEO threshold check; boilerplate% monitor; unique-value enforce per page

---

## Q8 — Budget tool

**Header**: `Budget`
**Question**: «Qual è il tuo budget mensile per tool SEO?»
**Type**: single-select
**Options**:

- `lt100` — <€100/mese (free tier + low-cost)
- `100_500` — €100-500/mese
- `500_2k` — €500-2k/mese
- `2kplus` — €2k+/mese (agency / enterprise)

**Saves to**: `budget.tool_monthly`

**Conseguenze** (DECISION-010):

- `lt100` → Search Console + Ubersuggest free + Ahrefs Webmaster Tools own site only + Screaming Frog 500 URL free
- `100_500` → Ahrefs Lite ($129) OR Moz Pro ($99) — one or the other
- `500_2k` → Ahrefs Standard + SEMrush Pro
- `2kplus` → full agency stack (Ahrefs Advanced + SEMrush Business + Scrunch/LLMrefs + Profound)

**Anti-pattern enforce**: agent NON consiglia tool sopra tier user.

---

## Output discovery

Dopo le 8 risposte, salva `<memory>/config.md` (schema in `ARCHITECTURE.md` sezione 6). Mostra summary in italiano:

```text
Config salvata. Riepilogo:
- Ruolo: <user.role>
- Stack SEO primary: <stack.seo_primary> (<sc_status>)
- Sito: <site.type>, stage <site.stage>
- Geo: <geo.target> → <gdpr_mode_indicator>
- GEO priority: <strategy.geo_llm_optimization>
- Volume content: <strategy.content_volume>/mese
- Budget tool: <budget.tool_monthly>/mese
- Tool disponibili: <mcp_summary>
- Fallback attivi: <fallbacks>

Pronto a procedere. Confermi avvio audit/strategy?
```

## Re-run / reconfigure

Comandi disponibili dopo first run:

- `audit` — esegui audit completo dominio (default action)
- `keyword-research <topic>` — keyword research targeted
- `content-audit` — gap analysis vs competitor
- `geo-audit` — GEO citation tracking
- `schema-fix <url>` — schema generator/fix per URL
- `technical-audit` — technical SEO checklist run
- `reconfigure` — re-run discovery 8 domande
- `status` — mostra config corrente + last run date
