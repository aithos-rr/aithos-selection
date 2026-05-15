# Test Checklist — `/automation-architect`

> 10 test scenari Fase D. Run prima di marking subagent ready.

## Pre-flight checks

- [x] `python3 scripts/workflow_design.py --pattern webhook_driven --name test-lead-intake --path lead-intake --output /tmp/test-workflow.json` → exit 0, valid JSON output
- [x] `python3 scripts/workflow_validate.py /tmp/test-workflow.json` → exit 0, valid: true, errors: []
- [x] `python3 scripts/workflow_test.py /tmp/test-workflow.json` → exit 0, golden + edge scenarios PASS
- [x] `python3 scripts/workflow_export.py /tmp/test-workflow.json --output /tmp/test-readme.md` → README generato con Mermaid

## Test 1 — Discovery first run

**Setup**: empty `<memory>/config.md`.

**Action**: invoke `/automation-architect`.

**Expected**:
- 8 domande poste via AskUserQuestion
- Config salvato in `<memory>/config.md` con `schema_version: 1`
- Conferma in 1 riga "Config caricata: {role}, n8n {n8n_mode}"

## Test 2 — Re-run (config cached)

**Setup**: `<memory>/config.md` esistente con schema_version=1.

**Action**: invoke `/automation-architect`.

**Expected**:
- Skip discovery
- Conferma in 1 riga config caricata
- Procede con request immediate

## Test 3 — Reconfigure flag

**Setup**: config esistente.

**Action**: utente dice "reconfigure".

**Expected**:
- Backup config.md → config.backup-{timestamp}.md
- Re-run 8 domande
- Salva nuovo config.md

## Test 4 — Requirement parse — webhook

**Input**: "Quando arriva form submit, salva in Notion e notifica Slack"

**Expected**:
- trigger=webhook detected
- actions=[salva, notifica]
- integrations=[notion, slack]
- Match recipe #1
- Conferma con utente prima di procedere

## Test 5 — Validation reject hardcoded secret

**Input**: workflow JSON con `"value": "Bearer sk-abc..."`

**Expected**:
- `validate_workflow` returns `valid: false`
- Error type: `hardcoded_secret`
- BLOCK con message + fix suggerito (n8n credential / env var)
- Exit code 1

**Verified**: ✅ smoke test passed

## Test 6 — Dry-run con fixtures auto

**Input**: validated workflow JSON.

**Action**: `python3 scripts/workflow_test.py <workflow.json>`.

**Expected**:
- Trigger detected (webhook/schedule/ai_agent/manual)
- Fixture generato con sample fields da $json.body.X references
- Almeno 2 scenari (golden + edge)
- Assertions list popolata
- Output JSON valid

**Verified**: ✅ smoke test passed

## Test 7 — MCP fallback graceful

**Setup**: `mcp_available.n8n-knowledge=false` in config.

**Action**: invoke validation step.

**Expected**:
- Comunica fallback all'utente: "n8n-knowledge MCP non risponde — uso WebFetch fallback"
- Static check via `workflow_validate.py` runs
- No silent fail

## Test 8 — GDPR mode active enforcement

**Setup**: config `gdpr.mode_active=true`.

**Input**: requirement webhook con email + phone + name + tax_id.

**Expected**:
- credential-mapper detect PII fields
- Auto-add Set node KEEP fields specificati
- Article 9 check (no health/religion/politics)
- README include retention 30gg + DSAR procedure note

## Test 9 — AI Agent pattern + cost guard

**Input**: "Bot Slack che risponde a domande consultando Notion"

**Expected**:
- Pattern AI Agent matched (recipe #5)
- Skeleton include max iterations=10
- Memory configured (Window Buffer, k=10)
- README include cost estimate (model + tokens × volume)

## Test 10 — Multi-step workflow + sub-workflow split

**Input**: requirement con 60+ steps inferred.

**Expected**:
- Detect node count >50
- Suggerisce sub-workflow split
- BLOCK fino a conferma split strategy
- Genera master + 3 sub-workflow JSON

## Negative tests (added)

### Test N1 — Hardcoded Bearer detected ✅

```bash
echo '{...workflow with Bearer sk-...}' > /tmp/bad.json
python3 scripts/workflow_validate.py /tmp/bad.json
# Expected: exit 1, errors=[hardcoded_secret]
```

### Test N2 — Missing top-level fields

```bash
echo '{"name":"x"}' > /tmp/bad.json
python3 scripts/workflow_validate.py /tmp/bad.json
# Expected: exit 1, errors include missing nodes/connections
```

### Test N3 — Duplicate node names

Workflow JSON con 2 nodi entrambi `name: "Webhook"`.
- Expected: exit 1, errors include `duplicate_name`

### Test N4 — Invalid connection reference

Workflow con connection a node non esistente.
- Expected: exit 1, errors include `invalid_reference`

## Coverage

- ✅ Static validation: 4/4 scripts smoke test PASS
- ✅ Negative cases: 4/4 PASS
- ✅ Pattern generators: 4/4 (webhook, scheduled, ai_agent, data_pipeline)
- ⏸ Live MCP integration test: requires n8n-yellowtech MCP running (manual test by Filippo)
- ⏸ Discovery interaction: requires interactive run (manual test by Filippo)

**Static + smoke test PASS** ✅ — pre-deploy bar met.
