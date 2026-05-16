# n8n Integration 2026 — Reference

> Output Fase A research RQ7 → reference per skill `n8n-bridge`. Webhook handler Next.js + n8n workflow template + HMAC pattern.

## Quando usare n8n vs Convex Action

| Caso | Soluzione | Reasoning |
|---|---|---|
| Send email transactional | Convex Action + Resend | Server-side TS, no webhook overhead |
| Scrape sito esterno | n8n (Apify integration) | n8n has Apify node nativo |
| Sync dati 3 service esterni | n8n (Composio o native nodes) | Multi-service orchestration |
| Cron daily digest | Convex Cron | Built-in cron, TS-only |
| Workflow con human approval step | n8n | n8n has wait/approval nodes |
| Webhook Stripe billing | Convex Action | Stripe → Convex direct |
| LinkedIn outreach automation | n8n | n8n LinkedIn nodes |
| AI agent chain con tool calling | Vercel AI SDK | Convex Action invoca AI SDK |

**Regola**: se la logica può essere TS-only, prefer Convex Action. Se serve integration multi-service o nodes esistenti n8n, usa n8n.

## Pattern direzioni

### IN: n8n → app web

n8n triggera webhook su Next.js endpoint. App processa.

### OUT: app web → n8n

App fa POST a webhook n8n. n8n processa async.

### Bidirezionale

Entrambi simultaneamente. Esempio: signup → POST n8n (welcome email + CRM sync) → n8n risponde con CRM ID → POST back a app.

## HMAC SHA-256 pattern (raccomandato)

### Perché HMAC

- Verifica origin + integrity payload
- No public key infrastructure (PKI complex)
- Secret condiviso tra app e n8n
- Standard adottato da Stripe, Shopify, GitHub

### Setup

1. Generate secret: `openssl rand -hex 32` (32 byte / 64 char)
2. Salva in env vars sia app (`N8N_WEBHOOK_SECRET`) che n8n (env var n8n)

### Verify in Next.js (handler IN)

```typescript
// app/api/webhook/<event>/route.ts
import crypto from "crypto";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  // 1. Read raw body (CRITICAL: bytes received, not parsed)
  const rawBody = await req.text();

  // 2. Get signature header
  const signature = req.headers.get("x-n8n-signature");
  if (!signature) return NextResponse.json({ error: "Missing signature" }, { status: 401 });

  // 3. Compute expected HMAC
  const secret = process.env.N8N_WEBHOOK_SECRET!;
  const expected = crypto.createHmac("sha256", secret).update(rawBody).digest("hex");

  // 4. Timing-safe compare
  if (
    signature.length !== expected.length ||
    !crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))
  ) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  // 5. Parse + handle
  const payload = JSON.parse(rawBody);
  // TODO: business logic

  return NextResponse.json({ ok: true });
}
```

### Compute in n8n (Code node — outgoing)

```javascript
// n8n Code node, runs after Webhook trigger
const crypto = require('crypto');
const secret = $env.N8N_WEBHOOK_SECRET;
const rawBody = JSON.stringify($input.item.json);
const signature = crypto.createHmac('sha256', secret).update(rawBody).digest('hex');

return [{
  json: $input.item.json,
  headers: { 'x-n8n-signature': signature },
  body: rawBody,
}];
```

### Verify in n8n (Code node — incoming)

```javascript
// n8n Code node, after Webhook receives request from app
const crypto = require('crypto');
const secret = $env.N8N_WEBHOOK_SECRET;
const rawBody = $input.first().json.body;  // Configure Webhook node "rawBody: true"
const signature = $input.first().json.headers['x-n8n-signature'];

const expected = crypto.createHmac('sha256', secret).update(rawBody).digest('hex');

if (signature !== expected) {
  throw new Error('Invalid signature');
}

return [{ json: JSON.parse(rawBody) }];
```

## Critical best practices

1. **Raw body**: HMAC computed on bytes received, NOT re-serialized JSON. Use `req.text()` in Next.js, configure n8n Webhook con `"rawBody": true`.
2. **Timing-safe compare**: `crypto.timingSafeEqual()` per evitare timing attack che leak signature byte-by-byte. NEVER `===`.
3. **Secret management**: env var only, NEVER hardcoded in workflow JSON o committed. Rotate yearly.
4. **Idempotency**: include `event_id` in payload, verifica `if (already_processed) return 200;` per gestire retry n8n.
5. **Quick ack**: respond 200 entro 30s (timeout n8n). Per work lunghi: ack immediate, processa async (queue Convex Action).

## Workflow JSON template

File: `n8n-workflows/<event_name>.json`

```json
{
  "name": "<event_name>",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "<event_name>",
        "responseMode": "responseNode",
        "options": { "rawBody": true }
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [240, 300]
    },
    {
      "parameters": {
        "jsCode": "// HMAC verify (incoming) or compute (outgoing)\n// See full code in references/n8n-integration-2026.md"
      },
      "name": "HMAC Code",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Webhook Trigger": { "main": [[{ "node": "HMAC Code", "type": "main", "index": 0 }]] }
  },
  "active": false,
  "settings": {},
  "versionId": "GENERATE_AT_IMPORT"
}
```

## Edge cases

### Webhook timeout

Default n8n: 30s. Per task lunghi:

```typescript
// app/api/webhook/<event>/route.ts
export async function POST(req: NextRequest) {
  // 1. Verify HMAC (synchronous, fast)
  // 2. Parse payload
  // 3. Enqueue async work
  await convex.mutation(api.tasks.enqueue, { type: "process_<event>", payload });

  // 4. Return 200 immediately
  return NextResponse.json({ ok: true, queued: true });
}
```

### Retry logic

n8n auto-retry su 5xx response. Idempotency check:

```typescript
const eventId = payload.event_id;
const existing = await ctx.db.query("processedEvents").withIndex("byEventId", q => q.eq("eventId", eventId)).first();
if (existing) return NextResponse.json({ ok: true, idempotent: true });

// Process + record
await ctx.db.insert("processedEvents", { eventId, processedAt: Date.now() });
```

### Multiple endpoints

Stesso secret per tutti webhook? OK se trust boundary uguale. Otherwise: separate secrets per endpoint, env vars `N8N_WEBHOOK_SECRET_<EVENT>`.

## Sources

- [n8n.io workflows — Validate Seatable webhooks HMAC](https://n8n.io/workflows/3439-validate-seatable-webhooks-with-hmac-sha256-authentication/)
- [logicworkflow.com — Secure n8n Webhooks](https://logicworkflow.com/blog/n8n-webhook-security/)
- [codehooks.io — Secure Automation Webhooks Signature Verification](https://codehooks.io/blog/secure-zapier-make-n8n-webhooks-signature-verification)
- [Authentication for Next.js + Convex + Clerk Webhook — gist CS-Martin](https://gist.github.com/CS-Martin/5f34ff6219a01259c9ccdc87405bdf6a)
