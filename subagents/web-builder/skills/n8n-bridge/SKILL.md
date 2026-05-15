---
name: n8n-bridge
description: Genera webhook handler Next.js (app/api/webhook/[event]/route.ts) con HMAC verification scaffold + workflow n8n template (.json) companion per integrare app web con n8n via webhook bidirezionale. Pattern HMAC SHA-256 con raw body + timing-safe comparison. Da usare in Phase 7 della methodology /web-builder, condizionale a Q7=Sì n8n integration.
when_to_use: Phase 7 di /web-builder, integrazione n8n webhook in Next.js app, generazione HMAC verify handler, scaffold workflow template
---

# n8n Bridge

Skill di Phase 7 della methodology `/web-builder`. Attivata solo se `config.integrations.n8n == true`. Genera coppia di file: route handler Next.js + workflow template n8n.

## When to use

Attiva quando:
- Phase 6 (deploy) completata o skipped
- `config.integrations.n8n == true`
- `config.build.n8n_bridge_done != true`

**Non attivare se**:
- Q7 = No o "Più tardi"
- Utente non ha n8n attivo (ask conferma se ha account/instance accessibile)

## Input contract

```yaml
event_name: signup_welcome | stripe_webhook | crm_sync | <custom>
direction: in | out | both
webhook_secret_strategy: hmac | api_key | basic_auth
project_path: /path/to/project
n8n_url: https://n8n.example.com  # opzionale, per generate full URL in workflow template
```

## Output contract

```yaml
status: success | partial | failed
files_written:
  - app/api/webhook/<event_name>/route.ts
  - n8n-workflows/<event_name>.json
  - lib/webhook-verify.ts (utility, una volta)
env_vars_added:
  - N8N_WEBHOOK_SECRET (se direction=in or both)
  - N8N_API_KEY (se direction=out, optional)
  - N8N_WEBHOOK_URL (se direction=out)
documentation_added:
  - section "Integrazioni" in CLAUDE.md
checkpoint_message: "Webhook handler generato. Importa workflow JSON in n8n manualmente."
```

## Workflow

### Step 1 — Validate event_name

- kebab-case, no spaces, no caratteri speciali
- Lowercase
- Esempi validi: `signup-welcome`, `stripe-webhook`, `crm-sync`, `daily-digest`

Se invalid: prompt utente con suggestion fix.

### Step 2 — Generate route handler (direction=in or both)

File: `app/api/webhook/<event_name>/route.ts`

```typescript
import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

const WEBHOOK_SECRET = process.env.N8N_WEBHOOK_SECRET!;

export async function POST(req: NextRequest) {
  // 1. Read raw body (HMAC computed on bytes received)
  const rawBody = await req.text();

  // 2. Verify HMAC signature
  const signature = req.headers.get("x-n8n-signature");
  if (!signature) return NextResponse.json({ error: "Missing signature" }, { status: 401 });

  const expected = crypto.createHmac("sha256", WEBHOOK_SECRET).update(rawBody).digest("hex");

  // 3. Timing-safe comparison
  if (
    signature.length !== expected.length ||
    !crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))
  ) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  // 4. Parse + handle
  const payload = JSON.parse(rawBody);

  // TODO: business logic — replace this with your handler
  console.log(`[<event_name>] Received:`, payload);

  // 5. Return 200 ack (n8n attende response)
  return NextResponse.json({ ok: true, event: "<event_name>" });
}
```

**Critical points**:
- Raw body via `req.text()` (NOT `req.json()` che parses)
- `crypto.timingSafeEqual()` per evitare timing attack (mai `===`)
- Return 200 entro 30s (n8n timeout default), altrimenti retry

### Step 3 — Generate workflow template n8n (direction=in)

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
        "options": {
          "rawBody": true
        }
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [240, 300],
      "webhookId": "GENERATED_AT_IMPORT"
    },
    {
      "parameters": {
        "jsCode": "// Compute HMAC signature for outgoing call to Next.js\nconst crypto = require('crypto');\nconst secret = $env.N8N_WEBHOOK_SECRET;\nconst rawBody = JSON.stringify($input.item.json);\nconst signature = crypto.createHmac('sha256', secret).update(rawBody).digest('hex');\n\nreturn [{\n  json: $input.item.json,\n  headers: {\n    'x-n8n-signature': signature\n  },\n  body: rawBody\n}];"
      },
      "name": "Compute HMAC",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "url": "https://<your-app>.vercel.app/api/webhook/<event_name>",
        "method": "POST",
        "headerParametersUi": {
          "parameter": [{ "name": "x-n8n-signature", "value": "={{$json.headers['x-n8n-signature']}}" }]
        },
        "jsonParameters": true,
        "bodyParametersJson": "={{$json.body}}"
      },
      "name": "POST to Next.js",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [680, 300]
    }
  ],
  "connections": {
    "Webhook Trigger": { "main": [[{ "node": "Compute HMAC", "type": "main", "index": 0 }]] },
    "Compute HMAC": { "main": [[{ "node": "POST to Next.js", "type": "main", "index": 0 }]] }
  }
}
```

**Note utente**:
- Replace `<your-app>.vercel.app` con URL prod dopo deploy Phase 6
- Set env var `N8N_WEBHOOK_SECRET` in n8n: Credentials → Generic Credentials → Header Auth (NO, use env var direttamente in Code node)
- `webhookId` rigenerato all'import in n8n (NON copiare da template)

### Step 4 — Generate utility lib (one-time)

File: `lib/webhook-verify.ts` (riutilizzabile per multiple webhooks)

```typescript
import crypto from "crypto";

export function verifyHmac(rawBody: string, signature: string | null, secret: string): boolean {
  if (!signature) return false;
  const expected = crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
  if (signature.length !== expected.length) return false;
  try {
    return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
  } catch {
    return false;
  }
}
```

### Step 5 — Update .env.local.example

```
N8N_WEBHOOK_SECRET=<random-strong-secret-32-chars>
# Generate via: openssl rand -hex 32
N8N_WEBHOOK_URL=https://n8n.example.com/webhook/<event_name>  # se direction=out
N8N_API_KEY=                                                   # opzionale, per API n8n diretta
```

Suggest utente: `openssl rand -hex 32` per generare secret robusto.

### Step 6 — Update CLAUDE.md sezione Integrazioni

Append a CLAUDE.md:

```markdown
## Integrazioni

### n8n webhook bridge

- **Route handler**: `app/api/webhook/<event_name>/route.ts` (HMAC SHA-256 verify)
- **Workflow template**: `n8n-workflows/<event_name>.json` (importare in n8n manualmente)
- **Env vars**:
  - `N8N_WEBHOOK_SECRET` — HMAC secret condiviso tra app e n8n
- **Test**: `curl -X POST https://<app>/api/webhook/<event_name> -H "x-n8n-signature: <hmac>" -d '{"test": true}'`
```

### Step 7 — Output user

```
✅ n8n bridge configurato per evento `<event_name>`

📁 File scritti:
  - app/api/webhook/<event_name>/route.ts (HMAC verify handler)
  - n8n-workflows/<event_name>.json (workflow template)
  - lib/webhook-verify.ts (utility riusabile)

🔑 Env vars aggiunte a .env.local.example:
  - N8N_WEBHOOK_SECRET (genera con `openssl rand -hex 32`)

📋 Prossimi passi:
1. Genera secret: `openssl rand -hex 32` → copy → `.env.local`
2. Apri n8n, Import → File → seleziona `n8n-workflows/<event_name>.json`
3. n8n auto-genera webhookId. Copy webhook URL n8n.
4. Update `N8N_WEBHOOK_URL` in `.env.local` con URL n8n
5. Test end-to-end: trigger webhook da n8n, verifica log Next.js

Vuoi aggiungere altro evento webhook? [Sì/No, deploy adesso]
```

## Edge cases

- **Multiple webhook events**: skill può essere chiamata N volte per N event. Utility `lib/webhook-verify.ts` generata solo prima volta.
- **Bidirectional (direction=both)**: genera sia route handler IN sia client OUT. Aggiunge `lib/n8n-trigger.ts` per fire-and-forget POST verso n8n.
- **HMAC differente da SHA-256**: alcune integrations (Stripe, GitHub) usano formato diverso. Skill default = SHA-256, override possibile via input `algorithm: "sha512"`.
- **Webhook secret rotation**: documenta in CLAUDE.md che rotation richiede update sia env var che n8n credentials simultaneamente.

## Pattern sync vs async

- **Sync** (utente aspetta): NON usare n8n. Usa Convex Action diretta (run server-side, ritorna immediato).
- **Async**: n8n perfect — webhook fire-and-forget, n8n processa background, response immediate.
- **Cron schedule**: preferisci Convex Cron (built-in) per task TS-only. Usa n8n cron solo se serve integration multi-service.

## References

- `references/n8n-integration-2026.md` — pattern completo HMAC + sync vs async + when use Convex Action
- [n8n.io/workflows/3439 — Validate Seatable webhooks HMAC](https://n8n.io/workflows/3439-validate-seatable-webhooks-with-hmac-sha256-authentication/)
- [logicworkflow.com — Secure n8n Webhooks](https://logicworkflow.com/blog/n8n-webhook-security/)

## Gotchas

- 🔴 **Raw body è critical**: `req.text()` NOT `req.json()`. Se usi `await req.json()` poi serializzi di nuovo per HMAC compute, ottieni signature DIVERSA per spaces/order JSON.
- 🔴 **Timing-safe compare obbligatorio**: `===` permette timing attack che leak signature. Sempre `crypto.timingSafeEqual()`.
- 🟡 **Webhook timeout n8n default 30s**: handler deve respond < 30s. Per task lunghi: ack immediate, processa async (Convex Action / queue).
- 🟢 **n8n MCP YT**: per Filippo, può usare `n8n-default` MCP per creare workflow programmaticamente invece di import manuale. Skill non lo usa di default (audience generale Learnn) ma documenta come power-user feature.

## Crediti

Skill creata per `/web-builder` (Pack v2 Learnn). Pattern HMAC + raw body da research RQ7 (vedi `research/research-summary.md`).
