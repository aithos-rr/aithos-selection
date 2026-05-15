# BUILD-BRIEF — `/automation-architect`

> **Per la worker chat**: leggi questo file all'inizio. Tutto il contesto necessario per buildare l'agent è qui. Non serve leggere conversazioni precedenti.
>
> **Quick start**: leggi BUILD-BRIEF → leggi PROGRESS.md (se esiste) → leggi DECISIONS.md (se esiste) → esegui Fase A → B → C → D → E.
> Aggiorna PROGRESS.md ad ogni milestone (almeno ogni 25% context fill).

## Identità del subagent

- **Nome**: `/automation-architect`
- **Cosa fa (1 frase)**: Da requisiti utente in linguaggio naturale ("voglio quando arriva email X allora Y") a workflow n8n production-grade con architettura validata, JSON pronto per import, documentazione auto-generata, error handling, e best-practice n8n 2026 enforced.
- **Per chi**: Founder che usa n8n, automation engineer, agency che vende automazioni, SDR/RevOps che costruisce workflow GTM (audience non-developer Learnn — italiano user-facing).
- **Use case slide W2**: "Automazioni n8n end-to-end" (#7 dei 8 use case)
- **Skill v1 base da riusare come spunto**: `~/Dev/clients/learnn/skills/n8n/n8n-quickstart/SKILL.md` (skill esistente, da estendere). Inoltre **ecosistema skill globale ricco**: `n8n-workflow-patterns`, `n8n-node-configuration`, `n8n-expression-syntax`, `n8n-code-javascript`, `n8n-code-python`, `n8n-validation-expert`, `n8n-mcp-tools-expert` — tutti già grounded e testati. Questo è il subagent **più favorito** del Tier 2 per fonti pre-validate.
- **Tier**: 🥈
- **Tempo stimato**: 0.5-1 giorno research (light grazie skill ecosystem) + 6-8 ore build = ~8-10 ore totali

## Vincoli di livello "spaventoso"

Filippo ha esplicitamente chiesto agent **"fatti veramente bene, profondi, perfetti, che fanno dire wow"**. Vincoli minimi:

- System prompt **300-450 righe**
- **5 skills companion** in `skills/`
- **6 references docs** (workflow patterns, node config, expressions, validation, integrations recipes, error handling)
- **Discovery interattiva** al first run (8 domande mirate)
- **MCP detection automatica** + fallback grazioso (n8n-knowledge per docs, n8n MCP per write workflow)
- **Memory persistente** via `memory: project`
- **Almeno 3 esempi reali** documentati nel README (es. webhook → Notion, AI agent + Slack, scheduled scraping → Sheet)
- **Italiano** per messaggi utente, **inglese** per nomi tecnici
- **Output workflow**: JSON valido n8n + import-ready (no manual fix), documentation auto-generata

## Fase A — Deep Research (0.5-1 giorno, light)

**NOTA**: skill ecosystem già grounded → research lighter del solito. Focus su patterns nuovi 2026 + integrations recipes + validation gotchas.

### Research questions (rispondere TUTTE prima di passare a B)

1. **n8n architecture patterns 2026**: webhook-driven vs scheduled vs AI Agent-driven, sub-workflows, error workflow, retry+fallback patterns, queue mode for scale, Single-Tenant vs Multi-Tenant cloud
2. **Node configuration best practice 2026**: HTTP Request modes (raw vs predefined), Code node JS vs Python tradeoff, Set vs Edit Fields, expression `{{}}` vs Code, AI Agent + Tools pattern
3. **Validation patterns**: how to catch config errors pre-execution (n8n-validation-expert skill grounded), expression syntax pitfalls (`$json` vs `$node` vs `_input`), credential mapping
4. **Error handling 2026**: error workflow patterns, retry+exponential backoff, dead letter queue, alert routing (Slack/Telegram/email), monitoring (Sentry, n8n insights)
5. **Common integrations recipes**: Notion, Airtable, Google Sheets, Slack, Gmail, OpenAI/Anthropic, Stripe, HubSpot, Webhook → DB. 8-10 recipes pronti.
6. **AI Agent workflows 2026**: Anthropic Chat Model, MCP Client Tool integration, memory (Buffer/Window/Postgres), tool selection logic, structured output, streaming
7. **Security + GDPR**: credential storage, secrets management, env vars vs n8n credentials, data minimization in webhook payload, GDPR for workflow processing EU data

### Fonti da consultare

**NotebookLM dedicato** (worker chat crea in Fase A — nessun ID pre-allocato):

- Comando: `notebooklm create "n8n Workflow Architecture 2026"`
- Sources da aggiungere:
  - https://docs.n8n.io (full docs)
  - https://community.n8n.io (top discussions 2026)
  - https://blog.n8n.io (latest articles)
  - https://github.com/n8n-io/n8n (release notes 2026)
  - https://n8n.io/workflows (template library)
  - Anthropic MCP Protocol docs (per AI Agent + MCP Client Tool)
- **Skill esistenti grounded** (priority over web research):
  - `~/.claude/skills/n8n-workflow-patterns/` — pattern architetturali validati
  - `~/.claude/skills/n8n-node-configuration/` — node config guide
  - `~/.claude/skills/n8n-expression-syntax/` — expression validation
  - `~/.claude/skills/n8n-validation-expert/` — error interpretation
  - `~/.claude/skills/n8n-mcp-tools-expert/` — MCP tools usage
  - `~/.claude/skills/n8n-code-javascript/` — JS in Code node
  - `~/.claude/skills/n8n-code-python/` — Python in Code node

### WebSearch query

- "n8n best practice 2026 production workflow"
- "n8n AI agent MCP client tool 2026"
- "n8n error handling exponential backoff retry"
- "n8n queue mode scale 2026"

### parallel-cli

- `parallel-cli research "n8n workflow patterns AI agent 2026"`
- `parallel-cli research "n8n credential security best practice 2026"`

### Output research

Salva in `research/research-summary.md`:

- 1 sezione per RQ (Q1-Q7) con citation
- 8-10 integration recipes pronti (Notion/Airtable/Google/Slack/Gmail/AI/Stripe/HubSpot/Webhook→DB)
- 6 architecture patterns (webhook-driven, scheduled, AI agent, multi-tenant, queue, error)
- Edge case scoperti (10+: rate limit, large payload, expression debug, credential rotation, version migration)

Salva sintesi anche in Obsidian: `~/Dev/obsidian-vault/02 - Ricerca/automation-architect_2026-MM-DD.md`

## Fase B — Architecture Design (2-3 ore)

### Discovery questionnaire (8 domande)

| # | Header | Q (italiano) | Options | Conseguenza |
|---|--------|--------------|---------|-------------|
| 1 | Ruolo | Ruolo principale | Founder · Automation engineer · Agency · SDR/RevOps · Curious | Adatta tono e profondità default |
| 2 | n8nMode | n8n hosting | Cloud · Self-hosted · Embedded · Non ho ancora | Adatta credential + deployment advice |
| 3 | UseCase | Tipo workflow tipico | Webhook → action · Scheduled job · AI Agent · Data pipeline · Mix | Carica template archetype |
| 4 | Stack | Tool integrations primary | Notion+Slack · Google Workspace · CRM (HubSpot/Attio) · AI (OpenAI/Anthropic) · Custom HTTP | Carica recipes specifiche |
| 5 | Scale | Volume execution/giorno | <100 · 100-1k · 1k-10k · 10k+ | Architecture: single instance vs queue mode |
| 6 | ErrorH | Error handling priorità | Critical (alert immediate) · Standard (retry+log) · Best-effort (skip on fail) | Define error workflow + retry strategy |
| 7 | AIAgent | Usi AI Agent in workflow? | Sì frequente · Sì occasionale · No | Activate skill `workflow-designer` AI patterns |
| 8 | GDPR | Process EU PII data? | Sì molto · Sì occasionale · No | Activate GDPR mode (data minimization, retention, EU host) |

Salva in `discovery/questions.md`.

### MCP mapping (con fallback)

| MCP | Tipo | Required for | Fallback |
|-----|------|--------------|----------|
| `n8n-knowledge` | **Recommended primary** | Search nodes, get node info, validate workflow JSON | WebFetch n8n docs (slower) |
| `n8n-yellowtech` o equivalent user n8n | Recommended | Create/update/test workflow direct in n8n | JSON file output, manual import user |
| `context7` | Optional | Library docs (Anthropic SDK, OpenAI, integrations) | WebFetch direct |
| `parallel-cli` | Optional | Research recent patterns | WebSearch |

### Skills companion (5 skill)

1. **`workflow-designer/`** (~250 righe)
   - **Cosa fa**: pattern matching su requisiti utente → architecture proposal (webhook-driven / scheduled / AI agent / data pipeline). Output workflow JSON skeleton da popolare.
   - **Input**: natural language requirements + integrations target + scale
   - **Output**: workflow JSON skeleton + design rationale + node selection
   - **References**: `n8n-workflow-patterns-2026.md`

2. **`node-validator/`** (~200 righe)
   - **Cosa fa**: validate node configuration pre-execution (expression syntax, required fields, credential mapping). Hybrid rule-based + n8n-validation-expert skill chain.
   - **Input**: workflow JSON
   - **Output**: `{valid: bool, errors: [], warnings: [], fixes: []}`
   - **References**: `n8n-node-configuration.md` + `n8n-expression-syntax.md`

3. **`credential-mapper/`** (~190 righe)
   - **Cosa fa**: security check su credential — env vars vs n8n credentials, secrets in expression detection, rotation reminder, GDPR data flow check
   - **Input**: workflow JSON + credential list
   - **Output**: `{security_issues, env_vars_recommended, gdpr_concerns, rotation_alerts}`
   - **References**: `n8n-credential-security.md`

4. **`workflow-tester/`** (~210 righe)
   - **Cosa fa**: dry-run + test data injection + assertion check. Genera test fixtures basati su node types. Valida output schema.
   - **Input**: workflow JSON + test scenarios
   - **Output**: `{test_results, fixtures_used, assertions_passed, coverage}`
   - **References**: `n8n-testing-patterns.md`

5. **`workflow-documenter/`** (~190 righe)
   - **Cosa fa**: auto-doc README + Mermaid diagram + node-by-node explanation, README.md per workflow ready for handoff
   - **Input**: workflow JSON
   - **Output**: `README.md` markdown + Mermaid diagram + setup guide
   - **References**: `documentation-standards.md`

### Schema config (`<memory>/config.md`)

```yaml
---
agent: automation-architect
created: 2026-MM-DD
schema_version: 1
---

user:
  role: founder

stack:
  n8n_mode: cloud  # cloud | self_hosted | embedded
  n8n_url: https://yourname.app.n8n.cloud
  primary_integrations: [notion, slack, openai]

workflow:
  archetype_default: webhook_driven  # webhook_driven | scheduled | ai_agent | data_pipeline
  ai_agent_usage: occasional  # frequent | occasional | none

scale:
  daily_execution: 100_1k  # <100 | 100_1k | 1k_10k | 10kplus
  queue_mode_recommended: false

error_handling:
  priority: standard  # critical | standard | best_effort
  alert_destination: slack  # slack | email | telegram
  retry_max: 3
  retry_backoff: exponential

gdpr:
  process_eu_pii: occasional  # always | occasional | never
  mode_active: true

mcp_available: { n8n-knowledge: true, n8n-yellowtech: true, context7: true, parallel-cli: true }
mcp_fallbacks_active: {}

api_keys:
  n8n_api_key_present: true  # env N8N_API_KEY
```

### References docs (6 file)

| File | Content | Source |
|------|---------|--------|
| `n8n-workflow-patterns-2026.md` | 6 archetype: webhook-driven, scheduled, AI agent, data pipeline, multi-tenant, queue mode | Skill `n8n-workflow-patterns` esistente |
| `n8n-node-configuration.md` | Node config best practice, HTTP Request, Code JS/Python, Set/Edit Fields, expressions | Skill `n8n-node-configuration` esistente |
| `n8n-expression-syntax.md` | `{{}}`, `$json`, `$node`, `$input`, common pitfalls | Skill `n8n-expression-syntax` esistente |
| `n8n-validation-guide.md` | Validation profile, error interpretation, false positive patterns | Skill `n8n-validation-expert` esistente |
| `common-integrations-recipes.md` | 10 recipes: Notion CRM, Slack alert, Gmail digest, Google Sheets sync, AI agent + MCP, HubSpot deal flow, Stripe webhook, Webhook → DB, scheduled scraper, error monitor | Research Q5 |
| `error-handling-patterns.md` | Error workflow, retry exponential, dead letter, alert routing, monitoring (Sentry, n8n insights) | Research Q4 |

## Fase C — Build (6-8 ore)

### Subagent file principale

`automation-architect.md` con frontmatter + system prompt 350-450 righe (9 sezioni: identità, discovery, MCP detection, methodology 6 fasi: Requirements parse → Design → Build skeleton → Validate → Test dry-run → Document, tool usage, output, edge case, examples 3 reali, anti-pattern).

### Skills companion + Scripts

- 5 SKILL.md (vedi sopra)
- 6 scripts: `validate_input.py`, `workflow_design.py`, `workflow_validate.py`, `workflow_test.py`, `workflow_export.py`, `mcp_detect.py` + `requirements.txt`

### README utente-facing

3-5 esempi reali (Webhook → Notion CRM, AI Agent Slack bot, scheduled scraper Google Sheet), 8 FAQ, troubleshooting (n8n cloud vs self-hosted, credential migration, expression debug), anti-pattern.

## Fase D — Test (1-2 ore)

10 test checklist (discovery, re-run, requirements parse, design output, validation reject invalid JSON, dry-run, MCP fallback, GDPR EU mode, AI agent pattern, multi-step workflow), test fixtures (sample requirements, sample workflow JSON valid+invalid, test scenarios).

## Fase E — Documentation + Bundle (1 ora)

1. Update `MASTER-PROGRESS.md` (#7 → ✅)
2. Sezione `dist/CLAUDE_WEEK_SKILL_PACK.md`
3. Nota Obsidian
4. Final PROGRESS.md update

## Definition of Done

- [ ] 5 fasi A→E completate
- [ ] System prompt ≥350 righe
- [ ] 5 skills + 6 references + 6 scripts + README + 3 esempi
- [ ] Static + smoke test PASS (workflow JSON validation core)
- [ ] PROGRESS + MASTER-PROGRESS aggiornati

## Anti-pattern critici (da includere nel system prompt)

1. **Mai workflow senza error handling** (production = error workflow mandatory)
2. **Mai credential hardcoded in expression** (always n8n credentials o env vars)
3. **Mai expression `$json.field` quando può essere `$input.first().json.field`** (debug clarity)
4. **Mai workflow >50 nodes** senza sub-workflows split (manutenibilità)
5. **Mai webhook senza authentication** (HMAC signature o token)
6. **Mai AI Agent loop senza max iteration limit** (cost runaway)
7. **Mai HTTP Request senza timeout esplicito** (default 5min troppo lungo)
8. **Mai Code node per cosa che Set node può fare** (over-engineering)
9. **Mai `IF` node deeply nested** invece di Switch (readability)
10. **Mai data minimization skip** se GDPR mode (process EU PII = data minimization mandatory)

## 5 Decisioni emergent flagged per worker chat (Architecture phase)

1. **Output JSON portable**: schema standard n8n cloud (compatible self-hosted via `n8n import:workflow`).
2. **Validation strictness**: warning by default, BLOCK solo per errori che non permettono import (JSON malformed, missing required field).
3. **Test mode default**: dry-run con sample fixtures pre-export. User può `--no-test` per skip.
4. **Skill chain pattern**: workflow-designer chain → node-validator chain → workflow-tester (sequential), poi workflow-documenter come finalizzazione.
5. **NotebookLM creation**: lasciata a worker chat in Fase A.

## Chain con altri subagent

Input: requirements natural language. Output può chainare a:
- `/document-factory` per generare client-facing documentation del workflow
- `/lead-finder-pro` se workflow è GTM
- `/outbound-orchestrator` se workflow è outbound

## Context management

### Update PROGRESS.md ad ogni 25% context
- ✅ Cosa è stato fatto · 🚧 Cosa sto facendo · 📋 Prossimi step · 🐛 Edge case

### A 50% context
1. Update finale PROGRESS + DECISIONS
2. User chiama `/compact`
3. Re-prime: "Leggi PROGRESS.md e DECISIONS.md. Continua."

### File da NON perdere mai
- BUILD-BRIEF.md, PROGRESS.md, DECISIONS.md, ARCHITECTURE.md, research/research-summary.md
