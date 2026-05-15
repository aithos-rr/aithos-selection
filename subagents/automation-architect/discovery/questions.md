# Discovery Questions — `/automation-architect`

> 8 domande mirate al **first run** per personalizzare l'agent. Salvate in `<memory>/config.md`.
> Audience: non-developer Learnn — italiano user-facing, opzioni multiple-choice quando possibile.

## Q1 — Ruolo

**Header**: `Ruolo`

**Italiano**: "Qual è il tuo ruolo principale?"

**Options**:
- Founder / solo-builder
- Automation engineer / RevOps
- Agency che vende automazioni a clienti
- SDR / Marketer (workflow GTM)
- Curious / sto imparando

**Conseguenza config**: `user.role` → adatta tono (founder = pragmatico, engineer = preciso, agency = client-facing docs, SDR = focus GTM, curious = explain-first).

---

## Q2 — Automation Platform

**Header**: `Platform`

**Italiano**: "Quale automation platform usi?"

**Options**:
- n8n Cloud (managed, URL `*.app.n8n.cloud`)
- n8n Self-hosted (Docker / VPS / k8s)
- Make (ex Integromat, scenario-based)
- Zapier (zap-based, no MCP ufficiale → fallback JSON)
- Pipedream (workflow Python/Node, REST API)
- Workato (enterprise, REST API)
- Custom (Python/Node code, no platform)
- Sto valutando (modalità learning, output JSON pedagogico + comparison guide)

**Conseguenza config**: `stack.platform` (string) + `stack.platform_mode` (cloud/self-hosted/managed) → triggera **Fase Platform Detection** post-discovery:

1. **Probe MCP** per platform scelta:
   - n8n → MCP nativi (`n8n-knowledge`, `n8n-yellowtech`/`n8n-filippo`/user instance)
   - Make → community MCP partial (probe)
   - Pipedream → community MCP (probe)
   - Zapier / Workato / Custom → no MCP ufficiale, salta a step 2
2. **Se MCP found** → use directly, default output mode = `create_live_workflow`.
3. **Se MCP missing** → invoca skill `platform-adapter-generator`:
   - Studia API docs via WebFetch + context7
   - Genera adapter skill custom in `<memory>/skills-generated/<platform>/SKILL.md` + `adapter.py`
   - Setup env var richiesta in `<memory>/credentials.example.md`
   - Smoke test pre-attivazione
4. **Se Custom (Python/Node)** → mode = scaffold project (workflow-as-code), output cartella deployabile.
5. **Se Sto valutando** → mode = learning, output JSON pedagogico + comparison guide multi-platform.

**Default output mode**: `create_live_workflow` direct nella platform. **JSON export** (file `.json`/`.blueprint.json`) diventa fallback solo se MCP+API entrambi missing, o utente chiede flag esplicito `--json-only`.

---

## Q3 — Use Case Primario

**Header**: `UseCase`

**Italiano**: "Che tipo di workflow costruisci più spesso?"

**Options**:
- Webhook → action (trigger esterno → automazione)
- Scheduled job (cron-based, report periodici)
- AI Agent (chatbot, agent multi-step)
- Data pipeline (ETL, sync DB)
- Mix vari (no pattern dominante)

**Conseguenza config**: `workflow.archetype_default` → carica template skeleton primario in `workflow-designer` skill, MCP node pre-fetch.

---

## Q4 — Stack Integrations

**Header**: `Stack`

**Italiano**: "Quali tool integri più spesso? (puoi scegliere multipli)"

**Options** (multiple):
- Notion + Slack
- Google Workspace (Sheets, Gmail, Calendar)
- CRM (HubSpot, Attio, Pipedrive)
- AI providers (OpenAI, Anthropic, Mistral)
- Database (Postgres, MySQL, MongoDB)
- Custom HTTP / API third-party

**Conseguenza config**: `stack.primary_integrations` → carica recipes specifiche da `common-integrations-recipes.md`, pre-fetch credential patterns.

---

## Q5 — Scale

**Header**: `Scale`

**Italiano**: "Quante esecuzioni/giorno prevedi sui workflow critici?"

**Options**:
- <100 (workflow occasionali)
- 100-1k (medium volume)
- 1k-10k (high volume)
- 10k+ (production scale)

**Conseguenza config**: `scale.daily_execution` → architecture: <1k = single instance OK, 1k-10k = retry+monitoring serio, 10k+ = queue mode + workers (self-hosted only).

---

## Q6 — Error Handling Priority

**Header**: `ErrorH`

**Italiano**: "Quanto è critico l'error handling per i tuoi workflow?"

**Options**:
- Critical — ogni errore deve allertare immediatamente (es. payment processing)
- Standard — retry + log + daily digest
- Best-effort — skip on fail, no alert

**Conseguenza config**: `error_handling.priority` → adatta default error workflow (critical = Slack #alerts + PagerDuty, standard = Slack digest, best-effort = log only), retry strategy (3x/2x/0x).

---

## Q7 — AI Agent Usage

**Header**: `AIAgent`

**Italiano**: "Usi AI Agent (LLM) nei tuoi workflow?"

**Options**:
- Sì frequente (è il core)
- Sì occasionale
- No

**Conseguenza config**: `workflow.ai_agent_usage` → activate `workflow-designer` AI patterns (Anthropic Chat + MCP Client Tool + Memory), cost guard rails (max iterations).

---

## Q8 — GDPR / EU PII

**Header**: `GDPR`

**Italiano**: "I tuoi workflow processano dati personali UE?"

**Options**:
- Sì molto (CRM EU, B2C EU, employee data)
- Sì occasionale (lead enrichment, contact form)
- No (B2B US/global, no PII)

**Conseguenza config**: `gdpr.process_eu_pii` + `gdpr.mode_active` → activate data minimization (Set node KEEP only needed), retention 30gg, EU host check, audit log mandatory, no Article 9.

---

## Salvataggio config

Dopo discovery, salvare in `<memory>/config.md`:

```yaml
---
agent: automation-architect
created: YYYY-MM-DD
schema_version: 1
---

user:
  role: founder

stack:
  n8n_mode: cloud
  n8n_url: https://example.app.n8n.cloud
  primary_integrations: [notion, slack, openai]

workflow:
  archetype_default: webhook_driven
  ai_agent_usage: occasional

scale:
  daily_execution: 100_1k
  queue_mode_recommended: false

error_handling:
  priority: standard
  alert_destination: slack
  retry_max: 3
  retry_backoff: exponential

gdpr:
  process_eu_pii: occasional
  mode_active: true

mcp_available: { n8n-knowledge: true, n8n-yellowtech: true, context7: true, parallel-cli: true }
mcp_fallbacks_active: {}

api_keys:
  n8n_api_key_present: true
```

## Re-run / Reconfigure

Su run successivi, leggi `<memory>/config.md`. Se utente dice **"reconfigure"**, ripeti discovery e sovrascrive. Se config incompleta (missing key), chiedi solo le mancanti.
