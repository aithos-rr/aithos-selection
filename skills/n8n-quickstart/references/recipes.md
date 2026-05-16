# n8n Recipes — 3 workflow pronti per non-dev

## Contents

- [Recipe 1: Lead Gen Pipeline](#recipe-1-lead-gen-pipeline)
- [Recipe 2: Email Nurture Loop](#recipe-2-email-nurture-loop)
- [Recipe 3: Social Monitor](#recipe-3-social-monitor)
- [Come adattare le ricette](#come-adattare-le-ricette)
- [Template n8n JSON (roadmap)](#template-n8n-json-roadmap)

## Recipe 1: Lead Gen Pipeline

**Use case business**: "Quando arriva un lead (form, referral, LinkedIn), arricchiscilo e mettilo in CRM con score di qualità".

**Architettura** (pattern: AI Agent):

```
Typeform Trigger
    ↓
HTTP Request (parallel-cli enrich)
    ↓
Code node (scoring rules)
    ↓
IF score > 80
  ├── Attio Create Record (tier=hot)
  ├── Slack notify #sales-hot
  └── SmartLead add to campaign
IF score 50-80
  └── Attio Create Record (tier=warm)
IF score < 50
  └── Slack notify #sales-review
```

**Nodi n8n coinvolti**:
- Webhook trigger (Typeform → n8n)
- HTTP Request (`POST https://api.parallel.ai/enrich`, auth Bearer)
- Code (JavaScript):
  ```javascript
  const lead = $input.first().json;
  let score = 0;
  if (lead.email_confidence > 0.8) score += 30;
  if (lead.linkedin) score += 20;
  if (lead.intent_signals?.length) score += 30;
  if (lead.role?.match(/VP|Director|Head/i)) score += 20;
  return [{json: {...lead, score, tier: score >= 80 ? 'hot' : score >= 50 ? 'warm' : 'cold'}}];
  ```
- Switch node (routing per tier)
- Attio HTTP Request per create record
- Slack Webhook per notify

**Credenziali necessarie**: Typeform OAuth, Parallel API key, Attio API key, Slack Webhook URL, SmartLead API key.

**Template n8n JSON**: `scripts/recipe-1-lead-gen.json` (TODO: esportalo da n8n una volta costruito il primo flow).

---

## Recipe 2: Email Nurture Loop

**Use case**: "Dopo 3 giorni senza risposta da un lead caldo, invia email di follow-up. Dopo altri 5, ultimo tentativo. Poi marca come churned".

**Architettura** (pattern: Scheduled + State):

```
Cron (ogni giorno 10:00)
    ↓
HTTP Request (Attio query: lead status='contacted' AND last_outreach < NOW-3d)
    ↓
Loop each lead
    ├── Code: determina touch (2nd/3rd/final)
    ├── HTTP Request (SmartLead enqueue email template-X)
    ├── Attio update (last_outreach=now, touch_count+1)
    └── IF touch_count >= 5 → Attio update (status='churned')
```

**Nodi n8n**:
- Cron trigger (schedule)
- HTTP Request Attio (GET /records, filter)
- Split In Batches (1 lead alla volta)
- Switch (touch_count 1/2/3/4/5)
- HTTP Request SmartLead (enqueue sequence)
- HTTP Request Attio (update record)

**Gotcha**: rate limit Attio API = 100 req/min. Se lista > 100 lead, Split In Batches con wait 60s.

---

## Recipe 3: Social Monitor

**Use case**: "Ogni 4h, controlla menzioni della tua brand su LinkedIn + Twitter. Se negative, alert a owner. Se positive, thank-you auto".

**Architettura** (pattern: Scheduled + AI Agent):

```
Cron (ogni 4h)
    ↓
HTTP Request Apify (actor LinkedIn mentions)
    ↓
HTTP Request Apify (actor Twitter search)
    ↓
Merge
    ↓
AI Agent (Claude via HTTP, classify sentiment + category)
    ↓
Switch
    ├── IF negative → Slack alert CEO
    ├── IF positive → auto-thank-you via LinkedIn API
    └── IF neutral → Sheet append (monitoring log)
```

**Nodi n8n**:
- Cron trigger (every 4h)
- HTTP Request (Apify async run + wait for results)
- Merge node (union di LI + Twitter results)
- HTTP Request ad Anthropic API (claude-sonnet-4-6 classify):
  ```javascript
  // System prompt
  "Classifica il post in sentiment (positive/neutral/negative) + category (customer feedback / praise / complaint / spam). Output JSON: {sentiment, category, key_phrase}"
  ```
- Switch per sentiment
- Actions specifiche per branch

**Credenziali**: Apify Token, Anthropic API key, Slack Webhook, LinkedIn API OAuth, Google Sheets OAuth.

---

## Come adattare le ricette

1. Identifica **quale pattern** applica il tuo use case (Lead Gen, Nurture, Monitor, altro)
2. Copia la recipe base
3. **Sostituisci nodi specifici** con i tuoi tool (HubSpot al posto di Attio, Instantly al posto di SmartLead, ecc.)
4. Adatta la **logica di scoring / classificazione** al tuo business
5. Testa con 1 record prima di attivare cron

## Template n8n JSON (roadmap)

Prossimo milestone: export template JSON direttamente importabili in n8n.
File placeholder in `scripts/`:
- `recipe-1-lead-gen.json`
- `recipe-2-email-nurture.json`
- `recipe-3-social-monitor.json`

Da produrre dopo il primo ciclo di test live.
