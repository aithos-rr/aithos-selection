# Discovery questions — `/competitor-deep-dive`

> **8 domande** poste al first run via AskUserQuestion. Salvate in `<memory>/config.md` (project scope per DECISION-004). Re-run skip se config presente — eccetto user dice "reconfigure" o equivalente.
>
> **Reference**: `ARCHITECTURE.md` sezione 2 + `DECISIONS.md` per logica + `research/research-summary.md` RQ1 per routing framework.

## Format AskUserQuestion (per il system prompt)

Ogni domanda è un singolo `AskUserQuestion` con:

- `question`: testo italiano completo
- `header`: chip ≤12 char
- `options`: 2-4 options (esclusa "Other" automatica)
- `multiSelect`: false eccetto Q3 (lista competitor) e Q8 (reviews focus)

## Q1 — Ruolo

```
question: "Qual è il tuo ruolo principale in questa analisi?"
header: "Ruolo"
options:
  - label: "Founder / CEO"
    description: "Decisione strategica: positioning, fundraising, pivot, market entry"
  - label: "Marketing Manager (Recommended)"
    description: "Repositioning, messaging, content gap, campagne competitive"
  - label: "Product Manager"
    description: "Feature gap, roadmap input, JTBD comparison"
  - label: "Sales / SDR"
    description: "Battlecard, obiezioni, deal-level positioning"
  - label: "Analyst / Consultant"
    description: "Multi-cliente competitive intelligence, due diligence"
```

**Conseguenza**: salva in `user.role`. Routing framework auto in `gap-finder`:

- `founder` → SWOT + Porter 5F + Strategy Canvas
- `marketing` → Strategy Canvas + Positioning Map + ToV diff
- `pm` → JTBD + Feature Matrix + Reviews mining
- `sales` → Feature Matrix + CPM + battlecard
- `analyst` → CPM + JTBD + multi-framework overlay

## Q2 — Settore

```
question: "In quale settore opera il tuo business o il cliente che stai analizzando?"
header: "Settore"
options:
  - label: "SaaS B2B (Recommended)"
    description: "Audience tipica, Apify actor maintained, reviews G2 disponibili"
  - label: "eCommerce / DTC"
    description: "Reviews Trustpilot prioritari, ToV consumer-facing"
  - label: "Agency / Servizi B2B"
    description: "Reviews Clutch + LinkedIn case study"
  - label: "Marketplace / Platform"
    description: "Network effect signal, ecosystem mapping"
```

**Conseguenza**: salva in `business.industry`. Se SaaS B2B → reviews focus default `[G2, Trustpilot]`. Se eCommerce → reviews focus `[Trustpilot, Capterra]`. Agency → fallback a parallel-cli mention (Clutch non in Apify maintained).

## Q3 — Competitor list

```
question: "Quali competitor vuoi analizzare? (1-5 nomi + dominio, formato 'Make @ make.com')"
header: "Competitor"
options:
  - free_text: true
  - example: "Make @ make.com, n8n @ n8n.io, Zapier @ zapier.com"
  - constraint: "min 1, max 5 — più di 5 = analisi superficiale, suggerisci batch separato"
```

**Conseguenza**: salva in `competitors_input[]` (lista oggetti `{name, domain}`). Se >5 → warning "Analisi profonda max 5; ne aggiungo 5 ora, gli altri in batch successivo". Se <1 → block.

## Q4 — Profondità analisi

```
question: "Profondità analisi desiderata? (impatto su tempo + costo Apify)"
header: "Profondita"
options:
  - label: "Quick scan (~2h, ~$5)"
    description: "Solo positioning Playwright + 1 review platform. Per battlecard rapidi"
  - label: "Standard dossier (~1d, ~$15-20) (Recommended)"
    description: "Positioning + ToV + Reviews G2/Trustpilot + Gap matrix. Sweet spot"
  - label: "Deep strategic (~3d, ~$50+)"
    description: "+ BuiltWith tech stack + Crunchbase funding + LinkedIn signals + parallel-cli long-tail"
```

**Conseguenza**: salva in `analysis.depth`. Se Quick → skip ToV + reviews multi-platform, output single dossier. Se Standard → full pipeline 5 skill. Se Deep → carica tier deep tools (Crunchbase API, BuiltWith) — flag costi + chiedi conferma stack disponibile.

## Q5 — Output format

```
question: "Dove vuoi il dossier finale?"
header: "Output"
options:
  - label: "Markdown locale (Recommended)"
    description: "File in research/ — controllo totale, no dependency"
  - label: "Google Doc"
    description: "Richiede google-personal MCP. Convivenza con team"
  - label: "Notion"
    description: "Database structured. Richiede notion MCP (non disponibile default)"
  - label: "Slack summary"
    description: "Post sintesi in canale team. Richiede slack MCP"
```

**Conseguenza**: salva in `analysis.output_format`. Se Google Doc → verify `google-personal` MCP available. Se Notion → fallback markdown + warning "Notion MCP non disponibile, output markdown". Se Slack → verify `slack` MCP + chiedi canale target.

## Q6 — Cliente baseline

```
question: "Definisci il cliente baseline (chi confronti vs i competitor). 3 righe: tagline, value prop, ICP"
header: "Baseline"
options:
  - free_text: true
  - example: |
      Tagline: "Automate workflows without code"
      Value prop: "10x faster than Zapier for technical teams"
      ICP: "Mid-market SaaS, 50-500 employees, technical PMs"
  - constraint: "Tutti 3 campi obbligatori — gap analysis impossibile senza"
```

**Conseguenza**: salva in `business.baseline.{tagline, value_prop, icp}`. Se mancante uno dei 3 → block + prompt "Questo campo serve per gap analysis, non posso procedere senza". Anti-pattern: gap senza baseline → fake-news (anti-pattern #5 system prompt).

## Q7 — Geo target

```
question: "Geo prioritario per l'analisi? (impatta GDPR mode + reviews focus)"
header: "Geo"
options:
  - label: "Italia"
    description: "GDPR mode ON + LIA template + rate-limit safe"
  - label: "EU (multi-paese) (Recommended se EU)"
    description: "GDPR mode ON + warning EU mode attivo"
  - label: "EMEA"
    description: "GDPR mode ON ma lighter (cross-border ok)"
  - label: "USA / Worldwide"
    description: "GDPR mode OFF, scrape standard"
```

**Conseguenza**: salva in `business.geo_target`. Se ∈ {Italia, EU, EMEA} → set `gdpr.mode_active = true` + auto-load `references/gdpr-scraping-compliance.md` + warning utente "🇪🇺 GDPR mode attivo, rate-limit safe enforced + LIA template generato". USA/Worldwide → no LIA, rate-limit standard.

## Q8 — Reviews focus

```
question: "Su quali platform reviews focalizzare? (multi-select, costo Apify aumenta con multi)"
header: "Reviews"
multiSelect: true
options:
  - label: "G2 (Recommended per SaaS B2B)"
    description: "Best per software B2B, sub-rating sezionati"
  - label: "Trustpilot"
    description: "Best per consumer/eCommerce, volume alto"
  - label: "Capterra"
    description: "Best per SMB software, cross-link a GetApp/Software Advice"
  - label: "Tutti e 3 (costo +30%)"
    description: "Triple scrape — flag costo Apify ~$10-15 per competitor"
```

**Conseguenza**: salva in `analysis.reviews_focus[]` (array). Default in Q2 SaaS B2B = `[G2, Trustpilot]`. Se "Tutti e 3" → confirm cost + scelta actor `zen-studio/software-review-scraper` (multi-platform 1 chiamata). Se incompatibile con industry (es. Agency + G2) → warning "G2 raro per agency, suggerisci Clutch via parallel-cli fallback".

## Output discovery (post 8 domande)

Dopo le 8 risposte, salva `<memory>/config.md` (schema in `ARCHITECTURE.md` sezione 6). Mostra summary in italiano:

```text
Config salvata. Riepilogo:
- Ruolo: <user.role>
- Settore: <business.industry>
- Competitor target: <N> (<lista nomi>)
- Profondità: <analysis.depth> (<costo stimato>)
- Output: <analysis.output_format>
- Baseline cliente: <business.baseline.tagline>
- Geo: <business.geo_target> → <gdpr_mode_indicator>
- Reviews focus: <analysis.reviews_focus[]>
- Tool disponibili: <mcp_summary>

Pronto per iniziare. Confermi?
```

Se utente conferma → start pipeline 5 skill chain.

## Reconfigure trigger

Se utente dice "reconfigure", "reset", "ricomincia config", "cambia ruolo", o equivalenti → re-run 8 domande, sovrascrivi `<memory>/config.md`. Mantieni `competitors_analyzed[]` (history) tra le configurazioni.
