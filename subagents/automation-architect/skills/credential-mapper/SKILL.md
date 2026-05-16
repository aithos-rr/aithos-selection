---
name: credential-mapper
description: Security check su credential di un workflow — env vars vs n8n credentials, secrets in expression detection, rotation reminder, GDPR data flow check. Output {security_issues, env_vars_recommended, gdpr_concerns, rotation_alerts}. Block-level se hardcoded secrets detected. Usa pre-export workflow.
---

# credential-mapper

Security check su credential di un workflow n8n. Block hardcoded secrets, raccomanda env vars, flag GDPR concerns.

## Input

```json
{
  "workflow_json": { /* full workflow */ },
  "config": {
    "gdpr_mode_active": true,
    "n8n_mode": "cloud"
  }
}
```

## Logic

### Step 1 — Detect hardcoded secrets

Scan tutti i valori string in `parameters` per pattern:

| Pattern regex | Risk | Action |
|---------------|------|--------|
| `Bearer [a-zA-Z0-9_\-]{20,}` | API key in header | BLOCK |
| `sk-[a-zA-Z0-9]{40,}` | OpenAI key | BLOCK |
| `xoxb-` o `xoxp-` | Slack bot/user token | BLOCK |
| `ghp_` o `github_pat_` | GitHub PAT | BLOCK |
| `Bot [A-Za-z0-9._\-]+` | Discord bot token | BLOCK |
| `:[a-f0-9]{40}@` (URL embed) | Basic auth in URL | BLOCK |
| `password\s*[:=]\s*["'][^"']{6,}` | Plaintext password | BLOCK |
| `[A-Za-z0-9+/=]{40,}` (base64-like) in expression body | Possible secret | WARN |

**Block action**: report node + property + redacted preview (`Bearer ***...***`). Suggest:
- Move to n8n Credential (managed, encrypted)
- O env var via `{{$env.NAME}}`

### Step 2 — Credential reference check

Per ogni node con `credentials` field:

1. `credentialId` referenced — verifica che credential esista (se MCP available, `n8n-yellowtech.list_credentials`)
2. Se `credentialId` placeholder (es. `"REPLACE_ME"`) → WARN, listalo in setup checklist
3. Se node richiede credential ma `credentials` field manca → BLOCK + suggest

### Step 3 — Env vars recommendation

Se workflow usa `{{$env.X}}`:

1. List env vars referenced
2. Output a setup section: "Aggiungi a `.env` (o n8n env vars settings):"
3. Per cloud: spiega che env vars vanno in Settings → Variables (Pro plan only)
4. Per self-hosted: docker-compose `environment` o k8s ConfigMap

### Step 4 — GDPR data flow check

Se `gdpr_mode_active=true`:

1. Detect PII fields nel payload (Set node values, HTTP Request body con `email|phone|name|address|tax_id|fiscal_code|ssn`)
2. Verify data minimization:
   - Webhook trigger + downstream Set node che KEEP solo subset → OK
   - Webhook trigger SENZA Set node intermedio → WARN "PII passes through, no minimization"
3. Detect Article 9 sensitive data (health, religion, politics, sexual orientation):
   - Field names regex: `health|religion|politics|orientation|biometric|genetic|union`
   - Se trovato → BLOCK "Article 9 GDPR sensitive data detected. DPIA + explicit consent required."
4. Detect non-EU destination per EU PII:
   - HTTP Request URL con dominio US/non-EU + payload PII → WARN "Cross-border transfer to non-EU. SCC required."

### Step 5 — Rotation reminder

Per ogni credential referenced:

1. Calcola età credential (se MCP fornisce metadata, `n8n-yellowtech.list_credentials`)
2. Se età > 90 giorni → reminder "Credential X is N days old, consider rotation"
3. Output rotation_alerts list

## Output

```json
{
  "security_issues": [
    {
      "severity": "block",
      "node": "HTTP Request",
      "property": "headerParameters",
      "issue": "Hardcoded Bearer token detected",
      "preview": "Bearer ***...***xyz",
      "fix": "Replace with n8n credential (httpHeaderAuth) or {{$env.API_TOKEN}}"
    }
  ],
  "env_vars_recommended": [
    {"name": "STRIPE_WEBHOOK_SECRET", "used_in": ["Webhook HMAC verify Code"]},
    {"name": "SLACK_BOT_TOKEN", "used_in": ["Slack node credential"]}
  ],
  "gdpr_concerns": [
    {
      "type": "no_data_minimization",
      "severity": "warn",
      "node": "Webhook → HTTP Request (chain)",
      "issue": "PII (email, phone, name) passes through with no Set node KEEP",
      "fix": "Add Set node after Webhook keeping only necessary fields"
    }
  ],
  "article_9_block": [],
  "cross_border_warnings": [],
  "rotation_alerts": [
    {"credential": "Notion API", "age_days": 124, "action": "Rotate within 30 days"}
  ],
  "block": true,
  "block_reason": "1 hardcoded Bearer token in HTTP Request node"
}
```

## References

- `references/error-handling-patterns.md` — alert routing su credential failure
- `~/.claude/skills/n8n-node-configuration/DEPENDENCIES.md` — credential per node
- n8n docs: https://docs.n8n.io/credentials/

## Tools used

- Bash: `python3 scripts/workflow_validate.py --check credentials <path>`
- MCP `n8n-yellowtech.list_credentials` (se disponibile)
- Regex scan in workflow JSON

## Anti-pattern flagged

1. **Bearer token literal** in expression → BLOCK
2. **password=plaintext** in URL or body → BLOCK
3. **PII passa senza Set drop** + GDPR active → WARN
4. **Article 9 sensitive data** detected → BLOCK con DPIA requirement
5. **Cross-border PII** without SCC → WARN
6. **Credential age >90 days** → reminder rotate

## Esempi

### Hardcoded Bearer detected

```json
{
  "node": "HTTP Request",
  "parameters": {
    "headerParameters": {
      "parameters": [
        {"name": "Authorization", "value": "Bearer sk-abc123..."}  // ❌ BLOCK
      ]
    }
  }
}
```

Fix:
```json
{
  "node": "HTTP Request",
  "parameters": {
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth"
  },
  "credentials": {"httpHeaderAuth": {"id": "REPLACE_ME", "name": "My API"}}
}
```

### GDPR data minimization fix

Add Set node after Webhook:

```json
{
  "name": "Set (GDPR drop)",
  "type": "n8n-nodes-base.set",
  "parameters": {
    "fields": {
      "values": [
        {"name": "email", "value": "={{$json.body.email}}"},
        {"name": "name", "value": "={{$json.body.name}}"},
        {"name": "company", "value": "={{$json.body.company}}"}
      ]
    },
    "options": {"includeOtherFields": false}  // KEEP only listed
  }
}
```
