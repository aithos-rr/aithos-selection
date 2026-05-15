# GDPR Scraping Compliance — EU Mode 2026

> Reference legal per scraping competitor data in EU. Source: GDPR Recital 47 + CNIL 2024 Focus Sheet + IAPP 2026. Auto-loaded dal subagent quando `business.geo_target ∈ {Italia, EU, EMEA}`.

## Quick check: cosa è lecito vs no

### ✅ Lecito (public + legitimate interest documentato)

- Homepage, About, Product, Pricing pages (any company)
- Public reviews G2 / Trustpilot / Capterra / TrustRadius / Gartner
- Public blog posts
- LinkedIn company page (no profile-level personal data)
- Crunchbase profili public
- BuiltWith tech stack detection
- Public press releases / news
- Public documentation / API docs

### ❌ Non lecito (behind login / sensitive)

- LinkedIn personal profiles senza Sales Nav account utente concesso
- Forum sanitari (Article 9 sensitive)
- Siti pornografici / gambling
- Private groups social (FB closed groups, Slack workspace, Discord private)
- Email behind login (anche se "public" alla company stessa)
- Dati Article 9: origine etnica, opinioni politiche, religione, salute, orientamento sessuale, biometric, genetic
- Children data (<13 senza parental consent)

## CNIL 2024 — Misure obbligatorie per Legitimate Interest

Da [CNIL Focus Sheet — Web Scraping & Legitimate Interest](https://www.cnil.fr/en/legal-basis-legitimate-interest-focus-sheet-measures-implement-case-data-collection-web-scraping):

### 1. Criteri di raccolta specifici (definiti in anticipo)

NO bulk crawl. Sempre target specifico (es. "G2 reviews per X competitor", "homepage testo per Y").

### 2. Esclusione automatica via filtri

Configurare filtri per categorie irrilevanti (es. esclusi forum sanitari, siti finanziari personali).

### 3. Cancellazione immediata

Se durante scrape raccogli accidentalmente dati irrilevanti / sensibili → cancellazione immediata.

### 4. Rispetto robots.txt + CAPTCHA

CNIL: *"processing cannot fall within reasonable expectations if the controller does not exclude websites that explicitly object through robots.txt or CAPTCHAs."*

Implementazione:
- Check robots.txt prima di scrape (path Disallow → skip)
- Se CAPTCHA challenge → STOP, no bypass via 3rd party CAPTCHA solvers
- Se Cloudflare bot detection → log + retry con delay, no aggressive evasion

### 5. Anonimizzazione / Pseudonimizzazione

Post-raccolta:
- Sostituisci PII (nome reviewer) con hash / pseudonym in analisi aggregata
- Mantieni `review_id` (already pseudonym da G2/Trustpilot)
- Esclusione email reviewer se trovata

### 6. LIA (Legitimate Interest Assessment) documentato

Pattern documentazione obbligatoria per ogni cliente EU:

```markdown
# LIA — Competitor Intelligence per <Cliente>

## 1. Legitimate Interest

- **Controller**: <Cliente Name>, <indirizzo>
- **Interest**: market research per product positioning, pre-roadmap planning, sales battlecard
- **Justification**: necessario per business viability + competitive defensibility

## 2. Necessity

- Public data only (no behind login)
- Scope-limited a competitor analizzati: <lista nomi>
- Sources: <G2, Trustpilot, Capterra, public homepage X-Y-Z>
- Exclusioni: nessun Article 9 data, nessun children data

## 3. Balancing test

- Data subjects (employees / reviewers) hanno **reasonable expectation** che public data sia processed for market research (è esplicitamente standard B2B practice)
- Mitigation: anonimizzazione PII reviewer post-raccolta
- Right to object: opt-out via privacy@<cliente>.com (process within 30gg)

## 4. Retention

- Raw scraped data: 30 giorni
- Analyzed reports: 90 giorni
- Aggregate insights: 12 mesi (no PII)

## 5. Opt-out

Procedure: chiunque può richiedere rimozione propri dati via privacy@<cliente>.com. Process entro 30gg.

## 6. Data Subject Rights respected

- Access: yes (within 30gg)
- Rectification: yes
- Erasure: yes
- Object: yes (immediate stop processing)
- Restriction: yes
```

### 7. Retention max 90 giorni (best practice)

Rotation policy: dossier > 90 giorni → delete from local + flag re-fresh suggested.

## Rate-limit safe defaults per source

| Source | Min delay tra request | Note |
|--------|------------------------|------|
| G2 | 5 secondi | Soggetto a Cloudflare bot detection |
| Trustpilot | 3 secondi | Generalmente più permissivo |
| Capterra | 5 secondi | Cross-link a GetApp/Software Advice (stesso owner) |
| Gartner | 10 secondi | Strictest, paywall partial |
| BuiltWith | 2 secondi | API ufficiale gestisce rate limit |
| Crunchbase API | 1 secondo | Ufficiale rate limit ~120 req/min Pro |
| Homepage generica (Playwright) | 2 secondi | Per dominio singolo |
| Apify (gestito) | Automatic | Apify worker queue gestisce |

## Recital 47 GDPR — Citation

> *"The legitimate interests of a controller, including those of a controller to which the personal data may be disclosed, or of a third party, may provide a legal basis for processing, provided that the interests or the fundamental rights and freedoms of the data subject are not overriding, taking into consideration the reasonable expectations of data subjects based on their relationship with the controller."* — [GDPR Recital 47](https://gdpr-info.eu/recitals/no-47/)

## EU Digital Omnibus (2026) — update

Il [EU Digital Omnibus amendments](https://iapp.org/news/a/eu-digital-omnibus-amendments-to-gdpr-to-facilitate-ai-training-miss-the-mark) (2026) ha tentato di facilitare scraping per AI training, ma critiche IAPP segnalano "miss the mark". Default conservative: **rispetta GDPR pre-Omnibus** salvo guidance EDPB chiarificatrice.

## Cross-border data transfers (EU competitor con reviews USA-hosted)

Se `business.geo_target = EU` ma reviews scrape da G2 (USA-hosted):

1. Flag in LIA: `"cross_border_transfer_detected": true`
2. Verify Standard Contractual Clauses (SCC) applicabili — Apify ha SCC standard
3. Anonymize PII reviewer prima di storage in EU
4. Retention più stretta (60gg vs 90gg standard)

## Anti-pattern legal

- **NO bypass robots.txt / CAPTCHA** — CNIL violation
- **NO scrape Article 9 data** — anche pubblici
- **NO storage PII reviewer non-anonymized** >30gg
- **NO LIA undocumented** per cliente EU
- **NO opt-out request ignorato** >30gg
- **NO rate limit aggressivo** (anche se site permette tecnicamente)
- **NO dark pattern** per ottenere consent — sempre opt-out chiaro

## Cliente non-EU (USA/Worldwide) — comportamento

Se `business.geo_target = USA/Worldwide`:

- **GDPR mode OFF** → no LIA template generato auto
- Comunque rispetta robots.txt + rate-limit safe (best practice anche se non legally required)
- CCPA (California) check se cliente USA west coast → opt-out form simile a GDPR
- Public data scraping legalmente OK in US (hiQ Labs v. LinkedIn precedent)

## Checklist EU mode auto-applied dal subagent

Quando `business.geo_target ∈ {Italia, EU, EMEA}`:

- [ ] `gdpr.mode_active = true` salvato in config
- [ ] `references/gdpr-scraping-compliance.md` auto-loaded (questo file)
- [ ] LIA template generato in `<memory>/lia_template.md` (compilabile dal cliente)
- [ ] Rate-limit safe enforced su tutti scrape
- [ ] Warning utente "🇪🇺 GDPR mode attivo" mostrato
- [ ] Anonimizzazione PII reviewer attiva nel `reviews-sentiment` skill
- [ ] Retention 90gg policy applicata su `output/` files
- [ ] Cross-border flag se reviews source USA

## Reference

- [GDPR Recital 47](https://gdpr-info.eu/recitals/no-47/)
- [CNIL — Legitimate Interest + Web Scraping Focus Sheet (2024)](https://www.cnil.fr/en/legal-basis-legitimate-interest-focus-sheet-measures-implement-case-data-collection-web-scraping)
- [EDPB Guidelines 1/2024 on legitimate interest](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202401_legitimateinterest_en.pdf)
- [IAPP — State of web scraping in EU](https://iapp.org/news/a/the-state-of-web-scraping-in-the-eu)
- [Discover Digital Law — Is web scraping legal under EU](https://discoverdigitallaw.com/is-web-scraping-legal-short-guide-on-scraping-under-the-eu-jurisdiction/)
- `research/research-summary.md` RQ6 — fonte derivazione
