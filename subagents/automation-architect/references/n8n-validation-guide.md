# n8n Validation Guide

> Reference for `/automation-architect`. Source: `~/.claude/skills/n8n-validation-expert/` (943 ERROR_CATALOG + 720 FALSE_POSITIVES).

## Validation severity levels

| Level | Action | Example |
|-------|--------|---------|
| **Error** | BLOCK import/activation | `missing_required: channel`, `invalid_value: operation`, `invalid_expression: ...` |
| **Warning** | Suggest fix, allow proceed | `best_practice: missing error handling`, `deprecated: use new operation`, `performance: large payload` |
| **Suggestion** | Optional improvement | `optimization: batch instead of loop`, `alternative: use Set vs Code` |

## Validation tools (MCP)

### Pre-execution validation

- **`n8n-knowledge.validate_node`** — single node config check
- **`n8n-knowledge.validate_workflow`** — full workflow JSON check
- Run BEFORE import o activation

### Post-create validation

- **`n8n-yellowtech.validate_workflow_comprehensive`** — runs after workflow created in n8n
- Includes: node deps, expression validity, credential mapping
- Recommended after `create_workflow` MCP call

## Validation loop pattern

Telemetry-validated (7841 occurrences):

```
1. Configure node
   ↓
2. validate_node (avg 23s thinking errors)
   ↓
3. Read error messages CAREFULLY (don't skim)
   ↓
4. Fix errors (avg 58s)
   ↓
5. validate_node again
   ↓
6. Repeat until valid (typical 2-3 iterations)
```

## Top 10 errors

| # | Error type | Cause | Fix |
|---|-----------|-------|-----|
| 1 | `missing_required` | Required field not set | Add field with value |
| 2 | `invalid_value` | Value not in enum | Use allowed value (check `validate_node` suggestions) |
| 3 | `type_mismatch` | String where number expected | Cast: `{{Number($json.x)}}` |
| 4 | `invalid_reference` | Node referenced doesn't exist | Check spelling, case sensitive |
| 5 | `invalid_expression` | Expression syntax error | Check `{{ }}`, brackets, quotes |
| 6 | `missing_credential` | Credential ID not assigned | Create + assign credential |
| 7 | `circular_reference` | Workflow → sub-workflow → workflow | Refactor: use queue/intermediate |
| 8 | `deprecated_operation` | Old operation name | Rename to current operation |
| 9 | `webhook_path_conflict` | Two webhooks same path | Unique path per webhook |
| 10 | `expression_undefined` | `$json.x` returns undefined | Add fallback: `{{ $json.x || 'default' }}` |

## False positives to ignore

Da `FALSE_POSITIVES.md`:

1. **AI Agent "missing prompt"** — quando il prompt è dinamico via `$json`, validator non lo vede. Sicuro ignorare se prompt è dinamico verificato.
2. **HTTP Request "no error handling"** — se hai Error Workflow assigned, è gestito. Warning ignorabile.
3. **Code node "no return"** — se Code modifica `$input` in-place (Python), warning ignorabile.
4. **Schedule "interval too short"** — se è `*/5` o più frequente, validator warning ma è OK per sub-100/day.

## Pre-export checklist

Prima di esportare workflow JSON:

- [ ] `validate_workflow` PASS (no errors)
- [ ] Warnings reviewed (false positive vs real)
- [ ] All credentials referenced exist (or noted in setup guide)
- [ ] Error Workflow assigned (per workflow critici)
- [ ] Test data fixtures available
- [ ] Dry-run executed (manual trigger con sample data)

## See also

- `~/.claude/skills/n8n-validation-expert/SKILL.md`
- `~/.claude/skills/n8n-validation-expert/ERROR_CATALOG.md` — full 943-line catalog
- `~/.claude/skills/n8n-validation-expert/FALSE_POSITIVES.md`
