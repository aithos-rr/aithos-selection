---
name: workflow-tester
description: Dry-run workflow JSON con test data injection + assertion check. Genera test fixtures basati su node types, valida output schema, copre golden path + edge cases. Output {test_results, fixtures_used, assertions_passed, coverage}. Usa pre-export o pre-deploy in n8n live.
---

# workflow-tester

Test workflow JSON pre-deploy con fixtures auto-generati + assertion check.

## Input

```json
{
  "workflow_json": { /* validated workflow */ },
  "test_scenarios": [
    {"name": "golden_path", "fixture": {...}, "assertions": [...]}
  ],
  "config": {
    "skip_test": false,
    "live_test_in_n8n": false  // true requires conferma user + n8n-yellowtech MCP
  }
}
```

## Logic

### Step 1 — Generate test fixtures auto

Per trigger node, genera sample input:

#### Webhook trigger

```json
{
  "headers": {
    "content-type": "application/json",
    "x-webhook-signature": "sha256=test_signature"
  },
  "params": {},
  "query": {},
  "body": {
    /* fields inferred from downstream Set node references */
    "email": "test@example.com",
    "name": "Test User",
    "company": "Acme Inc"
  }
}
```

Field inference: scan downstream nodes per `{{$json.body.X}}` pattern → genera field con sample value coerente:
- `email` → `test@example.com`
- `name` → `Test User`
- `amount` → `99.99`
- `id` → `uuid-test-123`
- `timestamp` → `2026-05-01T12:00:00Z`

#### Schedule trigger

```json
{"timestamp": "2026-05-01T12:00:00Z"}
```

#### AI Agent (chat trigger)

```json
{"input": "Test message: how do I reset my password?"}
```

#### Manual trigger

```json
{}
```

### Step 2 — Generate test scenarios

Genera almeno 3 scenari:

1. **Golden path**: tutti i campi presenti, valori validi, expected output success
2. **Missing optional fields**: fields opzionali assenti, expected behavior graceful
3. **Edge case**: empty value, large payload (10KB), unicode, special chars

Per scenari pattern-specifici:

- **Webhook with HMAC**: 1 scenario `valid_signature` + 1 `invalid_signature` (expected reject)
- **AI Agent**: 1 scenario simple Q&A + 1 multi-turn + 1 tool-use
- **Conditional (IF/Switch)**: 1 scenario per branch

### Step 3 — Generate assertions

Per ogni scenario, derive assertions da workflow design:

1. **Trigger fires**: workflow executes (no startup error)
2. **All required nodes have valid input**: each node's input matches schema expected
3. **Conditional logic correct**: IF true branch fires when condition met, false otherwise
4. **Output schema matches**: respond_to_webhook output JSON has expected fields
5. **No errors thrown**: execution status `success`
6. **Idempotency**: re-run with same fixture → same output (per webhook con dedup)

### Step 4 — Execute test

#### Mode A: Dry-run (mental simulation)

Default. Per ogni node:
- Read input (from previous node output o fixture)
- Apply parameters (mentally evaluate expressions)
- Predict output

Limitations: no real API call, no real DB write. OK per architecture validation.

#### Mode B: Live test (MCP n8n-yellowtech)

Solo se `config.live_test_in_n8n=true` E utente ha confermato:

1. Push workflow temp in n8n: `create_workflow` con name `test-{slug}-{timestamp}`
2. Trigger execution: `test_workflow` con fixture
3. Monitor: `get_execution` → check status, output
4. Cleanup: `delete_workflow` se test pass, leave per debug se fail

**Conferma esplicita** richiesta perché crea entità live + chiama API reali (cost, side effects).

### Step 5 — Coverage report

Calcola coverage:

- Nodes touched / total nodes
- Branches covered / total branches (IF/Switch)
- Error paths tested / total error paths

Target: >80% coverage golden path + 100% trigger node + 100% Respond/output node.

## Output

```json
{
  "test_results": {
    "total_scenarios": 3,
    "passed": 2,
    "failed": 1,
    "skipped": 0
  },
  "scenarios": [
    {
      "name": "golden_path",
      "status": "passed",
      "fixture": {/* used fixture */},
      "assertions": [
        {"name": "trigger_fires", "passed": true},
        {"name": "notion_node_valid_input", "passed": true},
        {"name": "respond_200", "passed": true}
      ],
      "execution_id": "exec_abc123" /* if live test */
    },
    {
      "name": "missing_optional_fields",
      "status": "passed",
      "assertions": [/* ... */]
    },
    {
      "name": "invalid_signature",
      "status": "failed",
      "assertions": [
        {"name": "respond_403", "passed": false, "reason": "Code node didn't reject, returned 200"}
      ],
      "fix_suggestion": "Add Code node HMAC verify with conditional Stop and Error if invalid"
    }
  ],
  "fixtures_generated": 3,
  "assertions_passed": 7,
  "assertions_total": 8,
  "coverage": {
    "nodes_touched": "5/6",
    "branches_covered": "1/2",
    "percent": 83
  },
  "ready_to_deploy": false,
  "blockers": ["1 assertion failed: invalid_signature handling"]
}
```

## References

- `references/n8n-validation-guide.md` — validation post-test
- `references/common-integrations-recipes.md` — fixture templates per recipe
- n8n docs `test_workflow` MCP: https://docs.n8n.io/api/

## Tools used

- Bash: `python3 scripts/workflow_test.py <workflow.json> --fixtures auto`
- MCP `n8n-yellowtech.test_workflow` (live mode)
- MCP `n8n-yellowtech.get_execution` (status check)

## Anti-pattern

1. **Skip test without flag** → confirm user intent ("Procedo senza test? --no-test")
2. **Live test in production n8n without conferma** → BLOCK, sempre conferma
3. **Only golden path** → forza almeno 1 edge case scenario
4. **Test pass ma assertion missing** → completa assertion list prima di marking pass
5. **Cleanup workflow temp dimenticato** → schedule cleanup post-test pass

## Esempi fixture per recipe

### Recipe #1 (Webhook → Notion CRM)

```json
{
  "headers": {"content-type": "application/json"},
  "body": {
    "email": "lead@example.com",
    "name": "John Doe",
    "company": "Acme Corp",
    "source": "website_form"
  }
}
```

Assertions: trigger_fires, set_extracts_email, notion_node_input_valid, slack_message_formatted, respond_200_received.

### Recipe #5 (AI Agent + MCP)

```json
{"input": "Search Notion for Q1 OKRs and summarize"}
```

Assertions: agent_invokes_mcp_notion_tool, mcp_returns_results, agent_summarizes, output_contains_summary, max_iterations_not_hit.

### Recipe #7 (Stripe webhook)

Scenario `valid_payment`:
```json
{
  "headers": {"stripe-signature": "t=1234567890,v1=valid_hash"},
  "body": {
    "type": "payment_intent.succeeded",
    "data": {"object": {"id": "pi_123", "amount": 1000}}
  }
}
```

Scenario `invalid_signature`:
```json
{
  "headers": {"stripe-signature": "t=1234567890,v1=invalid_hash"},
  "body": {/* same */}
}
```

Expected: scenario 1 → 200 + DB insert. Scenario 2 → 401 + no DB write.
