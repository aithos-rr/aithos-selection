---
name: node-validator
description: Valida workflow JSON pre-execution — expression syntax, required fields, credential mapping, false positive filtering. Hybrid rule-based + n8n-knowledge MCP chain. Output {valid, errors, warnings, fixes}. Auto-fix per errori ovvi (max 3 iterazioni). Usa standalone o come Fase 4 della pipeline `/automation-architect`.
---

# node-validator

Validate workflow JSON pre-execution con severity model errors / warnings / suggestions.

## Input

```json
{
  "workflow_json": { /* full n8n workflow */ },
  "config": {
    "validation_strictness": "warning_by_default",
    "block_on": ["error"],
    "auto_fix": true,
    "max_iterations": 3
  }
}
```

## Logic

### Step 1 — Static checks (no MCP needed)

Apply regex/JSON schema:

1. Valid JSON parse (no trailing comma, no syntax error)
2. Top-level required fields: `name`, `nodes`, `connections`, `settings`
3. Each node has: `id`, `name`, `type`, `typeVersion`, `position`, `parameters`
4. Node types match known prefix: `n8n-nodes-base.*` o `@n8n/n8n-nodes-langchain.*`
5. Connections reference existing node names (case-sensitive)
6. No duplicate node names
7. Settings has `executionOrder: 'v1'` (default)

### Step 2 — Expression syntax validation

Per ogni `parameters.*` value contenente `{{ }}`:

1. Balanced braces
2. No `$json.field with space` (use bracket notation)
3. No `$node.NodeName` con space (use `$node["..."]`)
4. No hardcoded credential pattern (`{{ "Bearer ` o `{{ "sk-`)
5. Webhook body access: per node con type webhook + downstream Set/Code, suggest `$json.body.X` se vede `$json.X`

### Step 3 — MCP-based validation (if available)

Se `mcp_available.n8n-knowledge`:

1. Per ogni node: chiama `n8n-knowledge.validate_node` con node config
2. Collect errors + warnings + suggestions
3. Filter false positives da `references/n8n-validation-guide.md` (sez "False positives to ignore")

Se `mcp_available.n8n-yellowtech` (post-create):

1. Chiama `validate_workflow_comprehensive` su workflow appena pushato
2. Include node deps, expression, credential mapping

### Step 4 — Auto-fix iteration

Per ogni error che ha auto-fix mapping:

| Error type | Auto-fix |
|-----------|----------|
| `missing trailing comma` | Add it |
| `expression missing braces` | Wrap value in `{{ }}` |
| `webhook body access shallow` | Replace `$json.X` with `$json.body.X` (con conferma se ambiguo) |
| `missing settings.executionOrder` | Add `'v1'` |
| `missing typeVersion` | Add latest stable |
| `node name with space referenced via dot` | Convert to bracket notation |

Re-validate dopo fix. Loop max 3 iterations.

### Step 5 — False positive filter

Se warning matches da `references/n8n-validation-guide.md` sez "False positives":

1. AI Agent "missing prompt" + dynamic prompt detected → ignore
2. HTTP Request "no error handling" + Error Workflow assigned → ignore
3. Code node "no return" + Python in-place modify → ignore
4. Schedule "interval too short" + intentional → mark "user-confirmed", ignore

## Output

```json
{
  "valid": false,
  "iterations": 2,
  "errors": [
    {
      "type": "missing_required",
      "node": "Notion",
      "property": "databaseId",
      "message": "Database ID is required",
      "fix": "User must provide Notion database ID after import",
      "severity": "error",
      "auto_fixed": false
    }
  ],
  "warnings": [
    {
      "type": "best_practice",
      "node": "HTTP Request",
      "message": "No timeout set, default 5min too long",
      "suggestion": "Set options.timeout: 5000",
      "auto_fixed": true
    }
  ],
  "suggestions": [
    {
      "type": "optimization",
      "message": "Webhook → Set → Notion could merge Set fields directly in Notion node parameters"
    }
  ],
  "false_positives_filtered": 2,
  "block": true,
  "block_reason": "1 error in Notion node (databaseId required)"
}
```

## Iteration logic

```
iteration 1:
  validate → 5 errors
  auto-fix → 3 fixed

iteration 2:
  validate → 2 errors
  auto-fix → 1 fixed

iteration 3:
  validate → 1 error (user input needed)
  auto-fix → 0 (manual)

RESULT: block=true, errors=1 (manual fix required)
```

Avg iterations from telemetry: 2-3 (validate-fix loop).

## References

- `references/n8n-validation-guide.md` — severity, false positives, auto-fix
- `references/n8n-expression-syntax.md` — expression rules
- `~/.claude/skills/n8n-validation-expert/ERROR_CATALOG.md` (943 lines)
- `~/.claude/skills/n8n-validation-expert/FALSE_POSITIVES.md` (720 lines)

## Tools used

- Bash: `python3 scripts/workflow_validate.py <path>` per static check standalone
- MCP `n8n-knowledge.validate_node` + `validate_workflow`
- MCP `n8n-yellowtech.validate_workflow_comprehensive` (post-create)

## Anti-pattern

1. **Block on warning** → frustra utente. Block solo su `error` level.
2. **Auto-fix without conferma** per ambiguous fix (es. `$json.X` → `$json.body.X` quando trigger non è webhook) → chiedi conferma
3. **Ignora warning silenzioso** → sempre report a utente, anche se non blocca
4. **Iterate forever** → cap a max_iterations (default 3)
