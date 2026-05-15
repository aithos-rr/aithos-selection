---
name: workflow-designer
description: Pattern matching su requisiti utente in linguaggio naturale → architecture proposal (webhook-driven, scheduled, AI Agent, data pipeline) + workflow JSON skeleton da popolare. Usa per primo step della pipeline `/automation-architect` o standalone per ricevere design proposta da requirement.
---

# workflow-designer

Match requisiti naturali a archetype pattern + genera workflow JSON skeleton da popolare.

## Input

Natural language requirement. Es: "Quando arriva form submit, salva lead in Notion e notifica Slack."

Optional context:
- `primary_integrations` from config
- `archetype_default` from config
- `gdpr.mode_active` flag

## Logic

### Step 1 — Parse requirement

Estrai:
- **Trigger** (obbligatorio): webhook? schedule? manual? AI agent (chat trigger)?
  - Keyword: "quando arriva" / "ogni" / "se" → webhook
  - "ogni X ore/giorni" / "alle Y ogni Z" → schedule
  - "chatbot" / "assistente" / "rispondi a domande" → AI agent
- **Source data**: cosa contiene il payload o la query
- **Action(s)** (1+): ordered list verbi → "salva", "notifica", "aggiorna", "invia"
- **Conditions** (optional): "se importo > X", "solo se PDF allegato"
- **Output**: cosa restituire (webhook response, email, log)

### Step 2 — Pattern selection

Apply decision tree (`references/n8n-workflow-patterns-2026.md`):

```
External trigger?
├── Yes (webhook/event) → Webhook-driven
└── No
    ├── Periodic? → Scheduled
    ├── User chat? → AI Agent
    └── Bulk data move? → Data Pipeline
```

Volume hint da config `scale.daily_execution`. Se >1k/day AND self-hosted → add Queue Mode note.

### Step 3 — Recipe match

Cerca recipe match in `references/common-integrations-recipes.md`:

- Notion + form/webhook → Recipe #1
- Monitoring + Slack thread → Recipe #2
- Gmail digest → Recipe #3
- Sheets bidirectional → Recipe #4
- AI Agent + MCP → Recipe #5
- HubSpot deal → Recipe #6
- Stripe webhook → Recipe #7
- Webhook dedup → Recipe #8
- Scraper → Recipe #9
- Error monitor → Recipe #10

Se match parziale, adapta. Se no match → genera custom design.

### Step 4 — Generate skeleton JSON

Skeleton template per pattern:

#### Webhook-driven skeleton

```json
{
  "name": "<workflow-name>",
  "nodes": [
    {
      "id": "1",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [240, 300],
      "parameters": {
        "path": "<path>",
        "responseMode": "responseNode",
        "options": {}
      }
    },
    {
      "id": "2",
      "name": "Set",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [460, 300],
      "parameters": {
        "fields": {"values": []}
      }
    },
    {
      "id": "999",
      "name": "Respond to Webhook",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [880, 300],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ {received: true} }}"
      }
    }
  ],
  "connections": {
    "Webhook": {"main": [[{"node": "Set", "type": "main", "index": 0}]]},
    "Set": {"main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]}
  },
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": true,
    "saveManualExecutions": true
  }
}
```

#### Scheduled skeleton

```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "parameters": {
        "rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}
      }
    }
  ]
}
```

#### AI Agent skeleton

```json
{
  "nodes": [
    {
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.5,
      "parameters": {
        "agent": "openAiFunctionsAgent",
        "options": {"maxIterations": 10}
      }
    },
    {
      "name": "Anthropic Chat Model",
      "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
      "typeVersion": 1,
      "parameters": {"model": "claude-sonnet-4-6"}
    },
    {
      "name": "Window Memory",
      "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      "typeVersion": 1,
      "parameters": {"contextWindowLength": 10}
    }
  ]
}
```

### Step 5 — Populate skeleton with parsed requirements

Per ogni Action estratta in Step 1, aggiungi node corrispondente:
- "salva in Notion" → `n8n-nodes-base.notion` con operation "databasePage:create"
- "notifica Slack" → `n8n-nodes-base.slack` con operation "message:post"
- "invia email" → `n8n-nodes-base.gmail` con operation "message:send"
- "HTTP API call" → `n8n-nodes-base.httpRequest`

Use `n8n-knowledge.search_nodes` MCP se disponibile per node ufficiale + parametri.

### Step 6 — GDPR check

Se `gdpr.mode_active=true`:
- Aggiungi Set node DOPO trigger con KEEP only fields specificati dall'utente
- Aggiungi commento JSON: `"// GDPR: data minimization applied"`

## Output

```json
{
  "design": {
    "pattern": "webhook-driven",
    "recipe_match": "#1 (Webhook → Notion CRM)",
    "trigger": "Webhook POST /lead-intake",
    "nodes": [
      {"name": "Webhook", "purpose": "Receive form submit"},
      {"name": "Set", "purpose": "Extract & validate fields"},
      {"name": "Notion", "purpose": "Append CRM database row"},
      {"name": "Slack", "purpose": "Notify #sales-leads"},
      {"name": "Respond to Webhook", "purpose": "Confirm receipt"}
    ],
    "error_handling": "per-node retry 3x exp + Error Workflow",
    "gdpr_notes": "Set node drops phone/address, keeps email/name/company"
  },
  "skeleton_json": { /* ... */ },
  "rationale": "Match con recipe #1: pattern webhook-driven + Notion + Slack è canonico."
}
```

## References

- `references/n8n-workflow-patterns-2026.md` — pattern decision tree + 6 archetype
- `references/common-integrations-recipes.md` — 10 recipes
- `references/n8n-node-configuration.md` — node parametri
- `~/.claude/skills/n8n-workflow-patterns/` (grounded ecosystem)

## Anti-pattern

1. **Skeleton vuoto** (no nodes oltre trigger) → BLOCK, chiedi più dettaglio requirement
2. **Pattern wrong-fit** (es. AI Agent per simple form save) → suggest webhook-driven più semplice
3. **No connections defined** → invalido, auto-add connections trigger → first action
4. **Missing settings.executionOrder** → auto-add `'v1'`
