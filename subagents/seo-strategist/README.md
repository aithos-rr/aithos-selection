# `/seo-strategist` — Strategia SEO + GEO 2026 actionable

> Subagent #5 del Pack v2 Learnn. Trasforma un dominio + obiettivi business in audit + keyword cluster + content plan + schema markup + technical fix list + tracking plan, evidence-first, con citation autorevole.

## Cosa fa in 1 frase

Sei un Founder, Marketing manager, SEO specialist, Content strategist o Agency. Hai un sito (o ne stai per lanciare uno). Vuoi una strategia SEO **e** GEO (per essere citato da ChatGPT, Perplexity, Claude, Gemini) che funzioni nel 2026 — non template generici copiati da blog del 2019. Lanci `/seo-strategist`, rispondi a 8 domande di discovery, e ottieni roadmap 90gg actionable, content brief queue, schema markup validato, e tool stack basato sul tuo budget reale.

## Come iniziare (3 minuti)

### 1. Lancia l'agent

```
/seo-strategist
```

Al **first run** ti farà 8 domande (ruolo, tool stack, tipo sito, stadio, geo, GEO priority, volume content, budget). Le risposte vengono salvate in `<memory>/config.md` e l'agent diventa "tuo".

### 2. Esegui un audit

```
audit
```

L'agent gira la pipeline 6-fase (audit baseline → keyword research → strategy → content plan → technical fix → reporting) e produce:

- `output/audit-summary-YYYY-MM-DD.md` — executive summary 1 page
- `output/audit-detailed-YYYY-MM-DD.md` — detailed report
- `output/cluster-keyword-YYYY-MM-DD.json` — keyword cluster
- `output/content-plan-YYYY-MM-DD.md` — content plan + briefs
- `output/schema-markup-YYYY-MM-DD/` — JSON-LD per page type
- `output/llms.txt` — se hai Q6=`priority` (GEO priority)
- `output/technical-fix-list-YYYY-MM-DD.md` — fix priorityied P0/P1/P2

### 3. Comandi successivi

| Comando | Cosa fa |
|---------|---------|
| `audit` | Audit completo dominio (default) |
| `keyword-research <topic>` | Cluster keyword targeted |
| `content-audit` | Gap analysis vs competitor + decay detection |
| `geo-audit` | Audit GEO citation potential per page |
| `schema-fix <url>` | Schema generator/fix per URL specifico |
| `technical-audit` | Technical SEO checklist run |
| `reconfigure` | Re-run discovery 8 domande |
| `status` | Mostra config corrente + last run date |

## I 3 esempi reali

### 🚀 Esempio 1: SaaS B2B greenfield + GEO priority

**Tu**: «Sono founder di un SaaS B2B per analytics e-commerce. Sito nuovo, voglio essere citato da ChatGPT.»

**Discovery output**:
- role=founder, stack=none, type=saas_b2b, stage=greenfield
- geo=italia, GEO=priority, volume=5_15, budget=100_500

**Cosa l'agent fa**:

1. Tech foundation audit (sitemap + robots + schema Organization)
2. Keyword research seed "ecommerce analytics" → 4 cluster identified (analytics features, BI tools comparison, KPI guide, integration recipes)
3. Pillar #1 "ecommerce analytics guide 2026" + 6 cluster supporting
4. llms.txt creation + schema FAQPage Tier 1
5. Digital PR plan: 1 data study Q3 + 3 expert quote outreach

**Output**: executive summary + content brief queue (12 pieces, ognuno con outline + GEO patterns + schema) + llms.txt + schema markup + tool recommendation Ahrefs Lite + Scrunch trial.

**Quanto tempo**: ~10 min discovery + audit, ~30 min review output.

---

### 🩺 Esempio 2: eCommerce decay recovery post Core Update

**Tu**: «Ho eCommerce moda, traffic -40% post Marzo 2026 Core Update. SOS.»

**Discovery output**:
- role=marketing_manager, stack=ahrefs, type=ecommerce, stage=decay
- geo=europa, GEO=secondary, volume=15_50, budget=500_2k

**Cosa l'agent fa**:

1. Google update timing audit: Marzo 2026 Core Update confermato (data source: Search Engine Land update tracker)
2. Decay pages list: top 30 page con -30%+ traffic loss → category pages "scarpe donna", "borse pelle"
3. Root cause analysis:
   - Thin content category pages
   - AI-generated description in mass (Helpful Content red flag)
   - Schema Product malformato 80% pagine
4. Recovery plan:
   - Fix schema Product (review, AggregateRating, offer)
   - Re-write top category pages: 800-1200 word unique content + buying guide section + UGC review embed
   - Internal linking audit (broken links + over-optimization fix)
   - Disclosure AI-assist boilerplate
5. GEO secondary: pillar pages "guida acquisto X" optimized per Perplexity + ChatGPT

**Output**: recovery roadmap 90gg + schema markup fix list batch + content rewrite priority queue + tracking plan recovery KPI.

**Risultato atteso**: 50%+ recovery a 12 settimane (target realistic, no promesse "+200%").

---

### 📝 Esempio 3: Content blog freelance + GDPR Italia + budget low

**Tu**: «Ho blog content marketing freelance, voglio sblocco crescita organica + cito ChatGPT. Budget zero.»

**Discovery output**:
- role=content_strategist, stack=search_console_only, type=content_blog, stage=plateau
- geo=italia, GEO=priority, volume=lt5, budget=lt100

**Cosa l'agent fa**:

1. Audit foundation con Search Console + Ubersuggest free + Screaming Frog 500 URL free
2. Keyword research seed "content marketing italia" → cluster discovery via cosine similarity (no Ahrefs, fallback semantic clustering manual)
3. Gap analysis vs 3 competitor (manual via WebFetch SERP top 10)
4. Plan refresh top 10 article + 2 pillar new
5. GEO priority: schema FAQPage + Article Tier 1 + llms.txt + author bio refresh
6. Digital PR low-budget: HARO + Featured + Italian Twitter network outreach
7. **GDPR mode auto-attivo** (geo=italia detected): cookie banner Garante-compliant check + Consent Mode v2 + GA4 strict config

**Output**: budget-respectful plan (€0 tool tier oltre Search Console) + content brief 12 piece + GEO checklist per piece + GDPR Garante banner audit.

**Tool consigliati per il tuo budget**:
- Search Console (free)
- Ubersuggest free (3 query/day)
- Ahrefs Webmaster Tools (free, own site only)
- Screaming Frog 500 URL free
- Manual GEO testing (ChatGPT/Perplexity browser, free)

---

## Cosa rende `/seo-strategist` diverso

| Feature | Altri tool/agent | `/seo-strategist` |
|---------|------------------|---------------------|
| **Anti-hallucination** | Stima volumi/difficulty inventati | Solo numeri da API o flag `qualitative_bucketing` esplicito |
| **GEO native** | "GEO" come buzzword | Skill dedicata + llms.txt + 8 patterns + platform-specific |
| **Budget-aware** | Consigliano sempre $300+/mese tool | Tier strict basato su Q8 — mai consigli sopra budget |
| **GDPR auto-attivo** | Opzionale o ignorato | Auto-attivo se geo Italia/EU + Garante 2024 specifics |
| **Schema gotcha** | HowTo "raccomandato", FAQPage senza warning | HowTo bloccato (deprecated 2023), FAQPage warning eligibility |
| **INP guidance** | "Misuriamo INP" (impossibile lab) | Guida onesta a Search Console + interpretation |
| **Citation grounded** | "Best practice generic" | Ogni claim ha source URL primary o secondary flagged |

## FAQ

### Q1. Posso usare `/seo-strategist` se non sono SEO specialist?

**Sì**. È pensato per audience non-developer (founder, marketer, content strategist). Le 8 domande di discovery adattano il livello di dettaglio al tuo ruolo (es. founder → high-level + ROI; SEO specialist → deep technical).

### Q2. Devo avere Ahrefs/SEMrush per usarlo?

**No**. Funziona anche con solo Search Console + Ubersuggest free. La skill `keyword-research` ha fallback `qualitative_bucketing` (low/medium/high invece di numeri esatti). Vedi Esempio 3.

### Q3. Quanto costa runare l'agent?

**€0** se usi free tier (Search Console + Ubersuggest free + Screaming Frog 500 URL). L'agent rispetta il budget Q8 e non consiglia tool sopra il tuo tier.

### Q4. Posso skippare il GEO se voglio solo SEO Google classico?

**Sì**. Q6=`skip` durante discovery → skill `geo-optimizer` non viene caricata. Focus 100% SEO classico.

### Q5. L'agent garantisce traffic +X%?

**No, e mai dovrebbe**. Promesse traffic specifiche ("+200% in 3 mesi") sono red flag. L'agent fornisce **roadmap actionable + KPI tracking plan** con range realistic (es. "+15% organic in 12 settimane se execution Plan A").

### Q6. Cosa succede se ho EU-only e GDPR strict?

GDPR mode si attiva automaticamente se Q5 ∈ {italia, europa, multi_paese} → carica reference doc `gdpr-privacy-seo-2026.md` + warning utente + checklist Garante 2024 (cookie banner, Consent Mode v2, GA4 strict).

### Q7. Come si aggiorna la config?

```
reconfigure
```

Re-runa le 8 domande. La config corrente viene sovrascritta in `<memory>/config.md`.

### Q8. Posso chainare con altri subagent?

Sì:
- `/document-factory` → PDF executive summary o content brief
- `/social-content-engine` → repurposing pillar content social
- `/automation-architect` → workflow content publishing automation
- `/competitor-deep-dive` → competitor cross-research

## Troubleshooting

### "Domain unreachable"

Lo script `validate_input.py` fa check HTTPS reachability. Se fail:
- Verifica DNS + SSL cert
- Domain serve root path → 200/301 status
- Cloudflare anti-bot? Allow IP del runtime

### "No sitemap found"

Provider candidates: `/sitemap.xml`, `/sitemap_index.xml`. Se diverso, passa esplicito `--sitemap https://...`.

### "INP value null"

INP è metrica field-only — non misurabile via Bash. Connetti Search Console (`stack.search_console_connected: true` in config) o passa Search Console export CSV.

### "Schema validation fail"

Tier 1 validation rule-based identifica required field mancanti. Fix → re-run. Per validation Tier 2 (rich result eligibility), usa link in output a Schema.org Validator + Google Rich Results Test.

### "MCP missing"

L'agent ha fallback graceful per ogni MCP missing:
- `parallel-cli` → WebSearch + WebFetch
- `playwright` → Bash + curl + readability parser
- `apify` → manual user export
- `google-personal` → markdown locale
- `context7` → WebFetch fallback

## Anti-pattern (DO NOT DO)

L'agent enforce 10 anti-pattern automaticamente:

1. ❌ Mai claim SEO non groundato (sempre source autorevole)
2. ❌ Mai keyword stuffing
3. ❌ Mai PBN, link farms, paid links (penalty risk)
4. ❌ Mai duplicate content cross-page
5. ❌ Mai schema markup invalid
6. ❌ Mai promesse traffic specifiche
7. ❌ Mai consigliare tool sopra budget Q8
8. ❌ Mai skip GDPR cookie consent se EU
9. ❌ Mai over-optimization on-page
10. ❌ Mai AI-generated content in mass senza disclosure

## Architettura interna (per developer/curious)

Vedi `ARCHITECTURE.md` per:
- Pipeline 6-fase data flow
- Skill orchestration matrix
- Config schema YAML
- MCP detection + fallback chain
- Output format specs

## Decisioni progettuali

Vedi `DECISIONS.md` per il log append-only delle 11 decisioni:
- DECISION-001: Pattern auto-onboarding
- DECISION-002: Naming inglese kebab-case
- DECISION-003: SEO+GEO dual focus
- DECISION-004: Memory project
- DECISION-005: NotebookLM SKIP
- DECISION-006: FAQPage dual-purpose
- DECISION-007: HowTo MAI default
- DECISION-008: GDPR auto-attivo EU
- DECISION-009: INP guidance only
- DECISION-010: Tool tier strict
- DECISION-011: GEO priority gating

## Research grounding

Vedi `research/research-summary.md` per le 7 research questions risposte con citation:
- RQ1: SEO 2026 evolution post-Helpful Content + Core Updates 2024-2026
- RQ2: GEO citation patterns + llms.txt + 8 patterns
- RQ3: Keyword research framework 2026
- RQ4: Technical SEO 2026 (CWV INP)
- RQ5: Schema markup JSON-LD 2026
- RQ6: Backlink strategy 2026
- RQ7: GDPR + privacy SEO 2026

20+ citations primary + secondary, ogni claim grounded.

## Quick reference per Filippo (autore)

- Repo target: `filippogreco/claude-skills-learnn`
- Tier: 🥈 (Pack v2 #5)
- Status: A→E completed (vedi `PROGRESS.md`)
- Webinar W2: «Marketing strategy» use case #3
- Audience: Learnn community (non-developer, marketer/founder)
- Lingua: italiano user-facing, inglese tecnico

## License

Stesso scheme del Pack v2 Learnn (TBD, probabilmente MIT o Creative Commons).

---

*Generated by `/seo-strategist` worker chat #5 — May 2026 — Pack v2 Learnn*
