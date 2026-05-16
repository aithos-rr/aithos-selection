---
name: outbound-campaign
description: Crea sequenze outbound multi-touch (email SmartLead + LinkedIn HeyReach) personalizzate dai dati arricchiti dei lead. Produce draft pronto per import nei tool, con messaggi iper-personalizzati sui segnali intent reali. Da usare dopo /lead-enrichment quando hai lista Hot pronta. Skill del Webinar 2 Claude Code per il GTM.
when_to_use: Lancio campagna outbound, sequenza email + LinkedIn, personalizzazione messaggi, dopo lead enrichment, preparazione cold outreach
argument-hint: "<enriched-leads-source>"
allowed-tools: Read Write Bash
---

# Outbound Campaign

Crea sequenze outbound iper-personalizzate basate sui dati arricchiti (intent signals, role, company size). Output: file import-ready per SmartLead (email) + HeyReach (LinkedIn).

## When to use

Attiva quando:
- Lista lead 🟢 Hot da `/lead-enrichment` pronta
- Evento/release che giustifica outreach
- Nuova ICP da testare

**Non attivare** se:
- Lead non arricchiti (→ `/lead-enrichment` prima)
- Lista < 20 (non statisticamente utile per sequenza)
- Pubblico già in campagna attiva (evita fatigue)

## Prerequisiti

- Lista lead arricchita da `/lead-enrichment` (tsv/csv/sheet)
- Account SmartLead + API key (in `~/.config/claude-skills/smartlead.yaml`)
- Account HeyReach + API key
- CLAUDE.md progetto con sezione `## Offer` (cosa vendi, value prop, differentiator)

## Instructions

### Fase 1 — Strategy setup

Chiedi all'utente (AskUserQuestion):

1. **Obiettivo**: demo booked, reply interessato, trial signup, brand awareness
2. **Sequenza**: quanti touch? (raccomandato: 5 email + 3 LinkedIn over 21 days)
3. **Angolo**: value prop primario (pain, opportunity, news hook)
4. **Tono**: confident-direct / casual-friendly / industry-authority

### Fase 2 — Segmentazione

Divide lista in segmenti per personalizzazione massima:

```python
segments = {
    "raised_funding": [leads with intent_signal "raised"],
    "hiring_roles": [leads with signal "hiring"],
    "industry_saas": [leads in industry "SaaS"],
    "role_marketing": [leads role ~ "marketing"],
    "default": [rest]
}
```

Ogni segmento ha sequenza con hook dedicato.

### Fase 3 — Copy generation per segmento

Per ogni segmento, genera sequenza:

**Email 1 — Opening (day 0)**:
```
Subject: <1 keyword + domanda curiosa>

Ciao <FirstName>,

<hook personalizzato: riferimento SPECIFICO al signal — "vidi che Acme ha raised
Series A a febbraio" vs generico "Vidi la tua azienda">

<bridge to offer — 1 frase>

<soft CTA: domanda aperta, non demo call>

<signature>
```

**Email 2 — Value add (day 3)**:
```
Subject: Re: <stesso>

<invio risorsa utile gratis: case study, template, article>
<menzione breve offer>
<soft CTA>
```

**Email 3 — Social proof (day 7)**:
```
<case study simile a loro company size/industry>
<1 numero specifico (es. "abbiamo aiutato 15 SaaS B2B a...")>
<CTA: "15 min mercoledì?">
```

**Email 4 — Break-up (day 14)**:
```
Subject: Chiuso?

<2 righe honest: "Immagino non sia priorità adesso, se fossi interessato/a qui
rimango">
<soft CTA: "risposta 1-parola basta (sì / no / forse più avanti)">
```

**Email 5 — Final (day 21)**: silenzio reply → archivia.

**LinkedIn parallel**:
- Day 1: connection request + nota 280 char
- Day 7: se accetta connessione, primo messaggio (soft)
- Day 14: follow-up con contenuto utile

### Fase 4 — Personalizzazione profonda

Per ogni lead, fill-in campi dinamici:

- `{firstName}`, `{company}`, `{role}` — basic
- `{intent_hook}` — riferimento specifico al signal (funding/hiring/news)
- `{pain_hypothesis}` — mapping role → pain comune (es. VP Marketing SaaS B2B → "lead gen scalabile")
- `{relevant_case_study}` — match industry/size con case library

### Fase 5 — Export

Output pronto per import:

**SmartLead**:
```csv
email,first_name,last_name,company,email_1_subject,email_1_body,email_2_subject,email_2_body,...
```
Salva `outbound-<campaign-name>-smartlead.csv`.

**HeyReach**:
```json
{
  "campaign_name": "...",
  "messages": [
    {"profile_url": "...", "first_name": "...", "connection_note": "...", "message_1": "...", ...}
  ]
}
```
Salva `outbound-<campaign-name>-heyreach.json`.

### Fase 6 — QA pre-lancio

**MANUAL REVIEW MANDATORY**:
- Campiona 10 lead random
- Leggi ogni sequenza end-to-end: sembra scritta a mano?
- Verifica no `{firstName}` rimasti non filled
- Verifica GDPR footer
- Verifica opt-out link

Solo dopo QA → utente importa manualmente in SmartLead/HeyReach.

### Fase 7 — Monitoring setup

Proponi:
- Dashboard reply rate (via SmartLead stats)
- Alert se bounce rate > 5% (indica email non ben verified → torna a `/lead-enrichment`)
- Weekly check con `/weekly-report` campaign-scoped

## Examples

### Esempio 1: Yellow Tech — campagna "Series A SaaS"

Segmento: `raised_funding` (30 lead)
Hook: "Vidi [Company] ha raised Series A a [month] — congrats!"
Bridge: "Le SaaS post-Series A spesso faticano su GTM scaling..."
Offer: GTM Engineering audit gratuito
Sequenza: 5 email + 3 LinkedIn

### Esempio 2: Learnn — corso AI (pubblico HR/L&D)

Segmento: `role_hr_training`
Hook: reference a recent post LinkedIn su AI training
Offer: preview 10 min del corso
Sequenza: 4 email (più soft, no pushy)

## Gotchas

- 🔴 **QA manuale NON opzionale**: sequenze AI-generated con field errori = disastro brand. Sempre campiona 10 prima di import.
- 🔴 **GDPR compliance**: footer con opt-out, policy privacy, legitimate interest chiaro. Tool SmartLead gestisce footer, ma verifica.
- 🔴 **Email provider throttling**: lancio di 500 email same day → bounce. Spread over 3-5 giorni.
- 🟡 **LinkedIn rate limits**: HeyReach rispetta limits, ma 50 connection request/day è tetto. Pianifica.
- 🟡 **Replies veri vs auto-out**: alcuni reply sono "I'm on vacation" autoresponders. Filtra prima di stats.
- 🟢 **Chain /lead-enrichment → /outbound-campaign**: flow ottimale, lista Hot direct to campaign.
- 🟢 **A/B test angoli**: lancia 2 segmenti con hook diversi, monitora reply rate, raddoppia su vincitore.

## Scripts

- `scripts/segment.py`: segmentazione per intent signals
- `scripts/generate_copy.py`: copy multi-touch con campi dinamici
- `scripts/export_smartlead.py`, `scripts/export_heyreach.py`: export pronti
- `scripts/qa_sample.py`: sampling 10 sequenze per review

## References

- `references/copy-templates.md`: 20 template email testati per segmento
- `references/linkedin-connection-notes.md`: 15 note connection a 280 char
- `references/gdpr-checklist.md`: compliance EU outbound

## Crediti

Skill originale Claude Week Learnn — Webinar 2 (Code GTM). Stack: SmartLead + HeyReach + Claude orchestration.
