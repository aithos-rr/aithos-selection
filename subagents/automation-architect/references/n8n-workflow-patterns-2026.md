# n8n Workflow Patterns 2026

> Reference doc for `/automation-architect`. Source: `~/.claude/skills/n8n-workflow-patterns/` (grounded, 5 pattern + 4 reference files).

## 6 Archetype Pattern

### 1. Webhook-driven

**When**: real-time integration, external trigger.

```
Webhook (POST endpoint, HMAC verify) → Set (validate + extract body) → [Action nodes] → Respond to Webhook (200 + body)
```

**Anti-pattern**:
- No HMAC → endpoint scrapeable
- Slow processing > 30s sync → Respond to Webhook before action (async pattern)
- Webhook body access errato (`$json.email` vs `$json.body.email`)

**Skeleton JSON**: vedi `n8n-workflow-patterns/webhook_processing.md`

---

### 2. Scheduled

**When**: periodic, no external trigger.

```
Schedule Trigger (cron) → [Fetch source] → [Transform] → [Deliver] → [Log result]
```

**Cron tips**:
- Daily 8am: `0 8 * * *`
- Hourly: `0 * * * *`
- Mon-Fri only: `0 8 * * 1-5`
- Avoid `* * * * *` (every minute) — use `*/5` minimum

**Anti-pattern**:
- Schedule + heavy fetch all-data ogni run → use `last_run_at` watermark
- No timezone awareness → schedule UTC, convert in display

---

### 3. AI Agent

**When**: conversational, multi-step reasoning, tool use.

```
Trigger (chat / webhook / manual) → AI Agent
                                      ├── Chat Model (Anthropic / OpenAI)
                                      ├── Memory (Window Buffer / Postgres)
                                      └── Tools (HTTP / MCP / Code / Workflow)
```

**Cost guards**:
- `maxIterations: 10` (default)
- Kill switch: `IF($json.iterations > 15) → Stop and Error`
- Timeout per tool call: 30s

**MCP Client Tool 2026**: connect any MCP server as tool. Transport: http (remote), stdio (local-only).

---

### 4. Data Pipeline (ETL)

**When**: sync data between systems.

```
Schedule → Source (DB / API) → Code (transform) → Validation → Target (DB / API) → Verify (count match)
```

**Patterns**:
- **Full sync**: Read all → Write all (small datasets <10k rows)
- **Incremental**: Watermark `last_modified > $lastRun` (recommended)
- **CDC** (Change Data Capture): trigger su DB change → propagate

---

### 5. Multi-tenant

**When**: SaaS workflow per cliente, isolation required.

```
Webhook (with tenant_id) → Switch (route by tenant) → [Sub-workflow per tenant] → Respond
```

**Isolation**:
- Credentials per tenant (n8n credential per tenant_id)
- Sub-workflow `executeWorkflow` con `inputData` filtrato
- Audit log con `tenant_id` mandatory

---

### 6. Queue Mode (high-scale)

**When**: >1k executions/day, parallel processing needed.

**Self-hosted only**: requires Redis + worker processes.

```
Webhook → Queue (Redis) → Worker pool → Process → Aggregate
```

**Setup**:
```bash
# Main n8n
EXECUTIONS_MODE=queue n8n start

# Workers (separate processes)
n8n worker --concurrency=5
```

**Anti-pattern**:
- Cloud plan → queue mode non disponibile fino Pro tier
- No worker → main process bottleneck

---

## Pattern Selection Decision Tree

```
External trigger?
├── Yes (webhook/event) → Webhook-driven
└── No
    ├── Periodic? → Scheduled
    ├── User chat? → AI Agent
    ├── Bulk data move? → Data Pipeline
    └── Multi-customer? → Multi-tenant + (one of above)

Volume > 1k/day AND self-hosted? → Add Queue Mode
```

## See also

- `~/.claude/skills/n8n-workflow-patterns/SKILL.md` — pattern details with full JSON examples
- `references/error-handling-patterns.md` — error workflow integration
- `references/common-integrations-recipes.md` — 10 ready recipes
