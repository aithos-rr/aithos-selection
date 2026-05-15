# Sequence Templates 2026

> Reference doc per `/outbound-orchestrator` skill `sequence-builder`. 4 template (Direct Demo, Education-First, Pain Discovery, Multi-threading) con JSON example portable + step structure dettagliata + widening gap default.
>
> Fonte: `research/research-summary.md` RQ1 + skill v1 `outbound-campaign` + best practice 2026.

## Selection guide — quale template usare?

| ICP | Sequence length | Best template | Reply rate target |
|-----|-----------------|---------------|-------------------|
| Mid-market SaaS, ICP chiaro, value prop concreta | 5 step | **Direct Demo** | 8-12% |
| Enterprise complex sale, awareness building | 7 step | **Education-First** | 10-15% |
| Pain-first ICP (loro hanno problema noto) | 5 step | **Pain Discovery** | 8-15% |
| Account-based, multi-stakeholder | 5 step × 3 lead | **Multi-threading** | 12-18% |

## Template A — Direct Demo (5 step)

### Use case

ICP chiaro, value prop concreta, sales cycle 14-30d. SaaS B2B mid-market sweet spot.

### Structure

```
Day 0  — Email step 1: signal hook + value prop + soft CTA
Day 2  — LinkedIn connection request + nota 280 char
Day 5  — Email step 2: case study + harder CTA (call meeting)
Day 7  — LinkedIn message #1 (post-acceptance only)
Day 10 — Email step 3: social proof + soft CTA
Day 14 — LinkedIn message #2 (opzionale, soft)
Day 21 — Email step 4: break-up "chiudi tu o continuo?"
```

### JSON example portable

```json
{
  "campaign_name": "Yellow Tech — Series A SaaS USA — Q2 2026",
  "sequence_name": "direct_demo_5step_v1",
  "channels": ["email", "linkedin"],
  "steps": [
    {
      "step_n": 1,
      "channel": "email",
      "delay_days": 0,
      "subject_variants": [
        "Domanda su {company}",
        "{first_name}, {company} + GTM scaling"
      ],
      "body_variants": [
        "Ciao {first_name},\n\n{first_line_variant_a}\n\nLavoriamo con SaaS Series A su scaling GTM dopo round. Ti sembrerebbe utile vedere come?\n\n{signature}\n\n{footer_html}",
        "Ciao {first_name},\n\n{first_line_variant_b}\n\n3 founder Series A simili ci hanno detto che il primo collo di bottiglia è X. Ho un framework, vale 15 min?\n\n{signature}\n\n{footer_html}"
      ],
      "signal_used": "funding_series_a",
      "send_window": "tue_thu_9_13"
    },
    {
      "step_n": 2,
      "channel": "linkedin",
      "node_type": "CONNECTION_REQUEST",
      "delay_days": 2,
      "messages": [
        "Ciao {first_name}, ho visto del round Series A di {company} a {month} — congrats! Mi piacerebbe connetterci."
      ],
      "fallback_message": "Ciao {first_name}, mi piacerebbe connetterci.",
      "signal_used": "funding_series_a"
    },
    {
      "step_n": 3,
      "channel": "email",
      "delay_days": 5,
      "subject_variants": [
        "Re: Domanda su {company}",
        "Re: {first_name}, {company} + GTM scaling"
      ],
      "body_variants": [
        "Ciao {first_name},\n\nRiprendo brevemente. Ho condiviso il framework GTM con altri founder Series A di {industry} — mediamente recuperano 2 settimane di onboarding rep.\n\nTi mando il case study di {similar_company}? È 4 pagine.\n\n{signature}\n\n{footer_html}"
      ]
    },
    {
      "step_n": 4,
      "channel": "linkedin",
      "node_type": "MESSAGE",
      "delay_days": 7,
      "messages": [
        "Grazie per la conn! Ho mandato 2 email — non importa se sei in fase 0 GTM o già rolling, posso mandare il framework PDF gratis. Dici di sì?"
      ],
      "conditional": "is_connection_accepted"
    },
    {
      "step_n": 5,
      "channel": "email",
      "delay_days": 10,
      "subject_variants": [
        "Ultimo: {company} GTM"
      ],
      "body_variants": [
        "Ciao {first_name},\n\nIn 2 righe: founder Series A che hanno applicato il framework hanno chiuso il primo $1M ARR in 4 mesi vs 7 baseline.\n\nTi va una call mercoledì 15:00 timezone tuo? Se non è priorità ora, no problem — chiudo io.\n\n{signature}\n\n{footer_html}"
      ]
    }
  ]
}
```

## Template B — Education-First (7 step)

### Use case

Enterprise complex sale, sales cycle 60-90d, awareness/trust building. Buyer non sa che ha il problema.

### Structure

```
Day 0  — Email: insight industry-specific (NO pitch)
Day 5  — LinkedIn connect
Day 7  — Email: case study same industry (NO pitch)
Day 14 — Email: framework/template downloadable
Day 21 — LinkedIn message: comment recent post target
Day 30 — Email: data point recente + soft CTA
Day 45 — Email: break-up
```

### Step 1 example body

```
Ciao {first_name},

Ho visto il post di {company} su {topic} la settimana scorsa.

Stavo guardando i dati sull'industria {industry} 2026: il 67% dei {role} sta passando da {old_approach} a {new_approach}, ma solo il 23% è soddisfatto del transition.

Curioso di sapere — voi siete tra i 23% o tra i 77%?

(Niente pitch, sono solo curioso. Lavoriamo nel settore.)

{signature}
{footer_html}
```

### Pattern

- No CTA hard fino a step 5+
- Risorse free: framework, case study, template, calculator
- Reply rate baseline 4-6%, top 12-18% se ICP focused
- Costo per reply alto ma ACV enterprise giustifica

## Template C — Pain Discovery (5 step)

### Use case

Pain-first ICP (loro hanno problema noto, tu hai soluzione). Mid-market 14-21d cycle.

### Structure

```
Day 0 — Email: domanda diagnostica (NO pitch)
Day 3 — Email: condividi case study correlato + diagnostico
Day 7 — LinkedIn connect + reference reply (se ha replicato)
Day 14 — Email: hard CTA call
Day 21 — Email: break-up
```

### Step 1 example body

```
Ciao {first_name},

Domanda da curioso: state vedendo X pain in {industry}? Sto chiedendo perché lavoriamo con {role} simili a te e il pattern emerge sempre.

(Se "no, problema risolto" → ti lascio in pace. Se "sì, è un casino" → posso condividere come 5 {industry} l'hanno fixato.)

{signature}
{footer_html}
```

### Pattern

- Step 1 = diagnostico, NO pitch
- Reply soglia bassa ("dimmi solo sì o no") aumenta reply rate
- Step 2 condiziona su step 1 reply (ramo divergente)
- Best per pain-driven ICP (es. CTO con tech debt, VP Sales con churn rate alto)

## Template D — Multi-threading (5 step × 3 lead)

### Use case

Account-based outbound. Target 1 account = 3 lead (Champion + Decision-Maker + User). Sales cycle 30-60d.

### Structure

```
Account-based: 3 lead per account, ognuno con sequence 5-step parallel.
Sequence ognuno: simile a Direct Demo MA con cross-reference.
```

### Cross-referencing pattern

Step 1 lead Champion (es. VP Marketing):
```
Ciao {first_name},
{first_line_signal}
Ho scritto anche al tuo collega {dm_name} — pensavo che sia il caso di tenervi entrambi nel loop.
...
```

Step 1 lead Decision-Maker (es. CMO):
```
Ciao {dm_name},
{first_line_signal}
Ho scritto anche al tuo team a {champion_name} — voglio essere trasparente nell'approccio.
...
```

### Coordinamento

- Tutti 3 lead day 0 stesso giorno (NOT staggered)
- Aggregation reply: se 1 reply (any lead), pause altri 2 stessa account → forward all to user
- Alternative: continue altri 2 con messaging "ho parlato con X"

### Tooling

- SmartLead `add_leads_to_campaign` con tag `account_id_<X>` per grouping
- Dashboard: filter per `account_id` per vedere multi-lead behavior
- Reply detection: aggregate logic (1 reply → action all 3)

## Step structure JSON portable (DECISION-015)

### Email step

```json
{
  "step_n": int,
  "channel": "email",
  "delay_days": int,
  "subject_variants": ["...", "..."],
  "body_variants": ["...", "..."],
  "signal_used": "funding_series_a | hiring_surge | ...",
  "send_window": "tue_thu_9_13 | mon_fri_anytime | ...",
  "stop_conditions": ["reply", "bounce", "unsubscribe"],
  "ab_test": true
}
```

### LinkedIn step

```json
{
  "step_n": int,
  "channel": "linkedin",
  "node_type": "CONNECTION_REQUEST | MESSAGE | INMAIL | VIEW_PROFILE | LIKE_POST",
  "delay_days": int,
  "messages": ["..."],
  "fallback_message": "...",
  "conditional": "is_connection_accepted | always",
  "signal_used": "..."
}
```

## Widening gap defaults (DECISION-010)

```yaml
default_gaps_email:
  step_1_to_2: 2-3 giorni
  step_2_to_3: 4-5 giorni
  step_3_to_4: 7-10 giorni
  step_4_to_5: 10-14 giorni

multi_channel_offset:
  email_to_linkedin: 2 giorni  # email day 0 → LinkedIn day 2
  linkedin_to_linkedin_msg: 5 giorni  # connect day 2 → message day 7
```

## Personalization fields (placeholder available)

Email body:

- `{first_name}` (from input)
- `{last_name}`
- `{company}`
- `{role}`
- `{industry}` (from enrichment)
- `{first_line_variant_a}` / `{first_line_variant_b}` / `{first_line_variant_c}` (from personalization-engine)
- `{signal_phrase}` (es. "round Series A", "joined as VP Marketing")
- `{similar_company}` (case study match by industry+size)
- `{signature}` (from config `brand.signature`)
- `{footer_html}` (from gdpr-opt-out skill)
- `{unsubscribe_url}` (auto-injected)

LinkedIn:

- `{first_name}` (mandatory)
- `{company}`
- `{li_message1}`, `{li_message2}`, `{li_message3}` (custom fields HeyReach upload)
- HeyReach syntax: **single brace** `{first_name}` (DECISION-011 enforce + auto-fix `{{var}}` regex)

## A/B test variant generation

Per template selezionato, `personalization-engine` genera:
- 2 subject variants (per email step)
- 3 first-line variants (per email step) — selezione random per lead, 33% each
- A/B test mode: combo subject_a + body_a vs subject_b + body_b

Min 30 lead totali per significance, 60+ raccomandato.

## Test sequence prima di full-send

Sample 10 lead random:
1. Render full sequence per ognuno
2. Manual review: signal-specific opening? variant diversity? no banned markers?
3. Send a 1 mailbox test (proprio o teammate)
4. Check rendering Gmail/Outlook/iPhone
5. Solo dopo: full upload + execute

Skill `sequence-builder` espone `--sample 10 --test-mailbox <addr>` flag.

## Reference esterni

- [Allegrow — Cold Email Sequence Guide 2026](https://www.allegrow.co/knowledge-base/cold-email-sequences)
- [Mailshake — Cold Email Sequence Templates 2026](https://mailshake.com/blog/cold-email-sequence/)
- [Salesleadagent — Email Sequences 2026](https://salesleadagent.com/blog/email-sequences-cold-outreach-2026)
- Skill v1 `<pack-root>/skills/webinar-2/outbound-campaign/SKILL.md` (template original)
- Skill v1 inspiration `~/.claude/skills/heyreach-api/SKILL.md` (HeyReach sequence shape)
