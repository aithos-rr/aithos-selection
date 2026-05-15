# Common Integrations Recipes

> 10 production-ready recipes for `/automation-architect`. Each recipe = use case + node chain + key gotchas + JSON skeleton hint.

## 1. Webhook → Notion CRM

**Use case**: form submission → CRM record.

**Chain**:
```
Webhook (POST /lead-intake, HMAC verify)
  → Set (extract body.email, body.name, body.company)
  → Notion (Append database row, properties: Name, Email, Company, Status="New")
  → Slack (Send message #sales-leads, "New lead: {{ $json.name }}")
  → Respond to Webhook (200, {received: true})
```

**Gotchas**:
- Notion property type matching (text vs select vs relation) — pre-create database schema
- HMAC: header `x-webhook-signature` + secret in n8n credential
- Respond BEFORE Slack to keep webhook response fast (move Slack to async pattern)

---

## 2. Slack alert con thread reply

**Use case**: monitoring alert con context aggregati nel thread.

**Chain**:
```
Schedule (every 5min) → HTTP (status check API)
  → IF (status != "ok")
    → Postgres (SELECT alert_thread_ts WHERE alert_key='X')
    → IF (existing thread)
      → Slack (Reply in thread, "Still failing - {{$now.toFormat('HH:mm')}}")
    → ELSE
      → Slack (Send Message, store ts in DB)
```

**Gotchas**:
- Slack rate limit Tier 1: 1 msg/sec. Use `retryOnFail: true`.
- Thread `ts` storage critico per reply (lose thread → spam channel)
- Token: Bot Token (`xoxb-...`), scope `chat:write` + `chat:write.public`

---

## 3. Gmail digest scheduled

**Use case**: daily email summary.

**Chain**:
```
Schedule (daily 8am UTC)
  → Gmail (Search messages, query: 'after:{{$today.toFormat("yyyy/MM/dd")}}')
  → Code (group by sender, count)
  → AI Agent (Anthropic, summarize themes)
  → Gmail (Send digest to self with summary + top 5 senders)
```

**Gotchas**:
- Gmail OAuth refresh: setup credential con `gmail.readonly` + `gmail.send`
- Pagination: `pageToken` se >100 results
- AI cost: limit input to top 50 emails (truncate body to 200 chars each)

---

## 4. Google Sheets ↔ DB sync

**Use case**: bidirectional sync DB ↔ Sheet (team edits Sheet, DB updates).

**Chain**:
```
Schedule (every 15min)
  → Postgres (SELECT * WHERE updated_at > {{$node.PrevRun.json.lastRun}})
  → Google Sheets (Update sheet, key=id, values from DB)

Webhook (Sheets onEdit, via Apps Script trigger)
  → Code (parse change)
  → IF (column tracked)
    → Postgres (UPDATE WHERE id, set field=value, updated_at=NOW())
```

**Gotchas**:
- Race condition: stesso row edit DB+Sheet in 1min → use `last_modified` timestamp tie-breaker
- Sheet format: header row required, fixed columns
- Apps Script trigger: needs deployment + permission grant by Sheet owner

---

## 5. AI Agent + MCP Client Tool

**Use case**: chatbot accessing Notion + Slack via MCP servers.

**Chain**:
```
Chat Trigger (n8n hosted chat URL) → AI Agent
                                       ├── Anthropic Chat Model (claude-sonnet-4-6)
                                       ├── Memory (Window Buffer, k=10)
                                       └── Tools
                                            ├── MCP Client Tool (notion-mcp, http://...)
                                            ├── MCP Client Tool (slack-mcp, http://...)
                                            └── HTTP Request Tool (custom API)
```

**Gotchas**:
- MCP server reachability: localhost MCP non funziona in cloud. Use HTTPS public URL.
- Auth: Bearer token in MCP config header
- Tool timeout: 30s per call (longer = abort)
- Cost: Anthropic API ~$0.003/msg sonnet → set max iterations 10

---

## 6. HubSpot deal flow

**Use case**: deal closed-won → invoice + notification.

**Chain**:
```
HubSpot Trigger (deal stage change, polling 1min)
  → IF ($json.dealstage == 'closedwon')
    → Stripe (Create invoice, customer_email from deal)
    → Email (Send invoice link)
    → Slack (#sales: "🎉 New won: {{$json.dealname}} - €{{$json.amount}}")
    → Notion (Update CRM mirror: status='Closed Won')
```

**Gotchas**:
- HubSpot polling 1min minimum. Per Enterprise plan, use Webhook trigger.
- Stripe customer match: lookup by email first, create if missing
- Idempotency: track `dealId + stage` combo to avoid double-invoice

---

## 7. Stripe webhook → DB + alert

**Use case**: payment events → audit log + Slack.

**Chain**:
```
Webhook (POST /stripe, verify signature)
  → Code (HMAC verify with STRIPE_WEBHOOK_SECRET)
  → Switch (event.type)
    ├── 'payment_intent.succeeded' → Postgres INSERT + Slack#payments
    ├── 'payment_intent.failed' → Slack#alerts (urgent) + Email finance
    ├── 'customer.subscription.created' → Notion (new sub)
    └── default → Postgres (audit_log)
  → Respond to Webhook (200)
```

**Gotchas**:
- HMAC verification MANDATORY (Stripe rejects unsigned). Use `crypto.createHmac('sha256', secret)`.
- Idempotency: Stripe sends events 2-3 times. Track `event.id` in DB.
- Respond 200 fast (Stripe retry if no 200 in 5s).

---

## 8. Webhook → DB con dedup

**Use case**: idempotent webhook processing.

**Chain**:
```
Webhook → Code (compute idempotency_key = sha256(body))
  → Postgres (SELECT FROM idempotency_log WHERE key=$1)
  → IF (exists)
    → Respond (200, {duplicate: true})
  → ELSE
    → Postgres (INSERT idempotency_log)
    → [Action chain]
    → Respond (200)
```

**Gotchas**:
- TTL idempotency_log: 24h (cleanup job needed)
- Hash deve includere relevant fields (no timestamp)
- Concurrent same key → DB unique constraint catches it

---

## 9. Scheduled scraper → Sheet

**Use case**: monitor competitor pricing.

**Chain**:
```
Schedule (hourly)
  → HTTP Request (target site, User-Agent: 'Mozilla/5.0...')
  → HTML Extract (CSS selector .price)
  → Set (parse price to number)
  → Google Sheets (Append row: timestamp, price, status)
```

**Gotchas**:
- Respect robots.txt
- Rate limit: max 1 req/min per target
- User-Agent realistic (no `node-fetch/2.0`)
- IP rotation se >100 req/day (use proxy)

---

## 10. Error monitor (multi-workflow)

**Use case**: centralized error workflow per ALL workflows.

**Chain**:
```
Error Trigger (assigned as Error Workflow in Settings)
  → Set (workflow_name = $json.execution.workflow.name, error = $json.execution.error.message)
  → Switch (severity from workflow name regex)
    ├── /-critical$/ → Slack#alerts + PagerDuty
    ├── /-prod$/ → Slack#warnings + email digest queue
    └── default → Postgres (error_log)
```

**Gotchas**:
- Error Workflow assignment: Settings → Error Workflow → select. Must be ACTIVE.
- `$json` in Error Trigger has structure: `{execution: {error: {...}, workflow: {...}}}`
- Don't process huge payload — extract only error message + workflow name

## Recipe selection by config

| User stack (Q4) | Suggest recipes |
|-----------------|-----------------|
| Notion + Slack | 1, 2, 5 |
| Google Workspace | 3, 4 |
| CRM (HubSpot/Attio) | 1, 6 |
| AI providers | 5 |
| Database | 4, 8 |
| Custom HTTP | 7, 9 |
