# Error Handling Patterns

> Reference for `/automation-architect`. Per workflow production-grade.

## Error handling stack (priority decreasing)

### 1. Per-node error handling

Configure on each node:

```json
{
  "onError": "continueRegularOutput",  // continue with empty output
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 2000   // ms, exponential ideal
}
```

**Options**:
- `stopWorkflow` (default) — fail entire workflow
- `continueRegularOutput` — proceed with empty $json
- `continueErrorOutput` — branch to error path

### 2. Workflow-level Error Workflow

Assign in Workflow Settings → Error Workflow → select centralized error handler.

**Error Workflow receives**:
```json
{
  "execution": {
    "id": "exec_id",
    "error": {
      "message": "...",
      "stack": "...",
      "node": "Node Name"
    },
    "workflow": {
      "id": "wf_id",
      "name": "..."
    }
  }
}
```

### 3. Dead Letter Queue (DLQ)

Failed items → stored for manual review.

**Pattern**:
```
[Action] → IF ($json.error)
            → Postgres (INSERT dlq_table: workflow_id, payload, error, timestamp)
            → Slack (alert)
```

DLQ replay workflow: scheduled, reads DLQ, retries each, marks resolved/permanent-fail.

### 4. Alert routing by priority

```
Error Workflow → Switch (priority detection)
                  ├── critical → Slack#alerts + PagerDuty + SMS
                  ├── standard → Slack#warnings + email digest (daily)
                  └── best-effort → Postgres log only
```

**Priority detection**:
- Workflow name regex (`-critical$`, `-prod$`)
- Tag-based (n8n workflow tags)
- Explicit field in error payload

## Retry strategies

### Exponential backoff

```javascript
// Wait formula in Code node
const attempt = $json.attempt || 1;
const baseMs = 2000;
const maxMs = 60000;
const waitMs = Math.min(baseMs * Math.pow(2, attempt - 1), maxMs);
return [{json: {waitMs, attempt: attempt + 1}}];
```

| Attempt | Wait |
|---------|------|
| 1 | 2s |
| 2 | 4s |
| 3 | 8s |
| 4 | 16s |
| 5 | 32s |
| 6+ | 60s (cap) |

### Idempotent retry (safe)

Pre-action check: lookup by idempotency_key. If exists → skip. Else → proceed.

### Non-idempotent (unsafe)

- Send email, Stripe charge, DB INSERT (not UPSERT) → DON'T retry blindly
- Use idempotency token (Stripe Idempotency-Key header)
- Or: track operation in DB, retry only if `status='pending'`

## Monitoring 2026

### n8n Insights (built-in cloud)

- Execution timeline graph
- Error rate per workflow
- p95 latency
- Cost per workflow (cloud only)

Access: Cloud UI → Insights tab.

### External monitoring

- **Sentry**: HTTP node in Error Workflow → POST to Sentry
- **Custom dashboard**: Postgres node read `execution_entity` table (self-hosted)
- **Grafana / Datadog**: read n8n Prometheus metrics endpoint (self-hosted)

## Alert payload templates

### Slack critical

```
🚨 *CRITICAL ERROR* in `{{$json.execution.workflow.name}}`

*Node*: `{{$json.execution.error.node}}`
*Message*: {{$json.execution.error.message}}
*Execution*: <{{$env.N8N_URL}}/workflow/{{$json.execution.workflow.id}}/executions/{{$json.execution.id}}|View execution>

*Time*: {{$now.toFormat('yyyy-MM-dd HH:mm:ss')}} UTC
```

### Email digest standard

Aggregate errors over 24h, group by workflow, send once daily:

```
Subject: [n8n] Daily error digest - {{$today.toFormat('yyyy-MM-dd')}}

Workflows with errors: 3
- WorkflowA: 12 errors (most: timeout)
- WorkflowB: 3 errors (most: 403 auth)
- WorkflowC: 1 error (one-off)

View all: {{$env.N8N_URL}}/executions
```

## Error handling decision matrix

| Workflow priority (Q6) | Per-node retry | Error Workflow | DLQ | Alert |
|------------------------|----------------|----------------|-----|-------|
| Critical | 3x exp | ✅ assigned | ✅ | Slack + PagerDuty |
| Standard | 3x exp | ✅ assigned | optional | Slack digest |
| Best-effort | 0-1x | optional | no | log only |

## Anti-patterns

1. **No error handling at all** → workflow fails silent in production
2. **Retry non-idempotent without check** → duplicate side effects (double charge, double email)
3. **Error Workflow that itself errors** → infinite loop. Test it manually.
4. **Alert spam** → throttle: max 1 alert per workflow per 5min
5. **Ignored DLQ** → DLQ becomes graveyard. Schedule replay/review.

## See also

- `references/n8n-workflow-patterns-2026.md` — Error Handler Pattern
- `references/common-integrations-recipes.md` — Recipe #10 Error Monitor
