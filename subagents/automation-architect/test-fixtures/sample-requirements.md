# Sample Requirements (Test Fixtures)

> Sample user inputs per testare requirement parsing.

## R1 — Webhook → Notion CRM

```
Quando arriva un form submit dal sito, salva il lead in Notion CRM e notifica
#sales su Slack
```

Expected parse:
- trigger: webhook
- actions: [salva, notifica]
- integrations: [notion, slack]
- recipe match: #1

## R2 — AI Agent + MCP

```
Voglio un bot Slack che risponde a domande sul prodotto. Deve consultare la
documentazione su Notion e creare ticket Linear se la domanda richiede
escalation a un umano.
```

Expected parse:
- trigger: ai_agent
- actions: [rispondere, consultare, creare]
- integrations: [slack, notion, linear]
- recipe match: #5
- AI Agent + MCP Client Tool

## R3 — Scheduled scraper

```
Ogni ora prendi i prezzi dai siti dei nostri 3 competitor (URL: A, B, C) e
aggiungi una riga su Google Sheet con timestamp e prezzo.
```

Expected parse:
- trigger: schedule (hourly)
- actions: [prendi, aggiungi]
- integrations: [google sheets]
- recipe match: #9

## R4 — Stripe webhook handler

```
Quando ricevo un webhook Stripe per payment_intent.succeeded, salva la
transazione in Postgres e notifica #payments su Slack. Se è failed, alert
su #alerts e email al team finance.
```

Expected parse:
- trigger: webhook
- conditions: switch on event type
- actions: [salva, notifica, alert, email]
- integrations: [stripe, postgres, slack, gmail]
- recipe match: #7

## R5 — Sync DB ↔ Sheet

```
Sincronizza una tabella Postgres con un Google Sheet ogni 15 minuti. Se il
team modifica righe nello Sheet, aggiorna anche Postgres.
```

Expected parse:
- pattern: data_pipeline + bidirectional
- 2 workflow needed (push + pull)
- integrations: [postgres, google sheets]
- recipe match: #4

## R6 — Error monitor centralizzato

```
Quando un workflow critico fallisce, alert su Slack #alerts. Workflow
standard: digest email giornaliero. Best-effort: solo log in Postgres.
```

Expected parse:
- pattern: error monitor (recipe #10)
- trigger: Error Trigger node
- routing: switch by severity from workflow name regex
- integrations: [slack, gmail, postgres]

## R7 — Ambiguous (deve chiedere)

```
Voglio automatizzare il processo di onboarding clienti.
```

Expected:
- BLOCK + chiedere: trigger? source events? actions specifiche?
- 1 domanda focalizzata: "Da dove parte? Form? Email? Tool CRM?"

## R8 — Edge case: too many nodes

```
Quando arriva un nuovo lead, fai enrichment, scoring, route per regione,
GDPR check, segment (10+ rules), email primary, fallback secondary, log
audit, sync CRM, slack notify, Linear ticket if high-value, calendar invite,
GDrive folder create, Notion CRM update, HubSpot sync, ...
```

Expected:
- Detect >50 nodes inferred
- Suggest sub-workflow split: master + [enrichment, scoring, routing, comms]
- BLOCK fino a confirm split strategy

## R9 — GDPR PII multiple sensitive

```
Quando arriva candidate application via form, salva nome, email, telefono,
codice fiscale, salary expectations, e diagnosi mediche per accomodation
request.
```

Expected:
- GDPR check trigger
- Article 9 BLOCK: "diagnosi mediche" detected (health data)
- Required: explicit consent + DPIA before proceed
- Suggest: store medical data in separate workflow with tighter access control

## R10 — Cost runaway risk

```
AI Agent che chiama tools senza limite, deve cercare ovunque e rispondere
nei dettagli più completi possibili.
```

Expected:
- BLOCK su missing maxIterations
- Auto-set maxIterations=10
- Add kill switch: `IF($json.iterations > 15) → Stop and Error`
- README include cost cap warning
