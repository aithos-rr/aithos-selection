# `/automation-architect` — README

> Subagent action-driven per costruire workflow n8n production-grade.
> Da requisito naturale → workflow JSON valido + README + test fixtures + auto-validation.

## Cosa fa

Trasformi una frase tipo:

> "Quando arriva un form submit dal sito, salva il lead in Notion CRM e notifica #sales su Slack"

In:

- ✅ Workflow JSON pronto per import in n8n
- ✅ README.md con Mermaid diagram + setup checklist
- ✅ Test fixtures auto-generati
- ✅ Validation report (errors / warnings / fixes)
- ✅ Anti-pattern check (10 rule enforced)

## Per chi

- **Founder** che usa n8n e vuole workflow production-grade senza diventare expert n8n
- **Automation engineer / RevOps** che costruisce molti workflow simili (cliente→cliente)
- **Agency** che vende automazioni e vuole quality bar coerente
- **SDR / RevOps** che costruisce workflow GTM (lead capture, enrichment, dispatch)

Audience: **non-developer Learnn** — italiano user-facing, inglese tecnico.

## Setup richiesto

### 1. n8n instance

Devi avere n8n attivo:

- **Cloud**: account su `*.app.n8n.cloud` (più semplice)
- **Self-hosted**: Docker o VPS (più controllo, queue mode)

### 2. MCP servers (raccomandato)

| MCP | Tier | Cosa fa |
|-----|------|---------|
| `n8n-knowledge` | **Primary** | Search nodi, validation, docs lookup |
| `n8n-yellowtech` o equivalent | Recommended | Push workflow live, test, monitoring |
| `context7` | Optional | Library docs lookup |
| `parallel-cli` | Optional | Recent pattern research |

Setup MCP n8n-knowledge:
```bash
# Via npx
npx @n8n/mcp-server-knowledge install
```

Setup MCP user n8n instance: vedi docs n8n MCP.

### 3. Skill ecosystem n8n (raccomandato)

Se hai già le skill globali in `~/.claude/skills/n8n-*/`, l'agent le riusa:
- `n8n-workflow-patterns` (pattern grounded)
- `n8n-node-configuration` (config best practice)
- `n8n-expression-syntax` (expression rules)
- `n8n-validation-expert` (error catalog)
- `n8n-mcp-tools-expert` (MCP tools usage)
- `n8n-code-javascript`, `n8n-code-python`

Senza queste, fallback a docs WebFetch (più lento, no auto-validation).

## First run

Al **primo invocazione in un progetto**, l'agent fa **discovery interattiva** (~2 min):

1. Ruolo (founder/engineer/agency/SDR/curious)
2. n8n hosting (cloud/self-hosted/embedded/none)
3. Use case primario (webhook/scheduled/AI agent/data pipeline/mix)
4. Stack integrations (Notion+Slack/Google Workspace/CRM/AI/Custom)
5. Scale (<100 / 100-1k / 1k-10k / 10k+)
6. Error handling priority (critical/standard/best-effort)
7. AI Agent usage (frequent/occasional/none)
8. GDPR EU PII (yes-much/yes-occasional/no)

Config salvata in `<memory>/config.md`. Re-run successivi: skip discovery (cached).

Per riconfigurare: dì "reconfigure" o "riconfigura".

## Esempi reali

### Esempio 1 — Webhook → Notion CRM (lead intake)

**Tu**: "Quando arriva form submit dal sito, salva lead in Notion CRM e notifica #sales su Slack"

**Agent**:
1. Parse: trigger=webhook, action=Notion+Slack, integrations=[notion, slack]
2. Match recipe #1 (Webhook → Notion CRM)
3. Design: 6 nodi (Webhook, Code HMAC, Set, Notion, Slack, Respond)
4. Build skeleton JSON + populate
5. Validate → PASS, 1 warning ("aggiungi Error Workflow")
6. Test dry-run → 3 assertions PASS
7. Genera README con curl test, setup Notion DB, HMAC secret

**Output**:
- `workflow-lead-intake-2026-05-01.json`
- `workflow-lead-intake-README.md`
- `workflow-lead-intake-fixtures.json`

### Esempio 2 — AI Agent Slack bot

**Tu**: "Bot Slack che risponde a domande sul prodotto consultando Notion docs e creando ticket Linear se serve escalation"

**Agent**:
1. Parse: trigger=chat (Slack), AI=yes, integrations=[slack, notion-mcp, linear-mcp]
2. Match recipe #5 (AI Agent + MCP Client Tool)
3. Design: AI Agent (Anthropic Sonnet + Window Memory + 2 MCP Client Tools)
4. Cost guard: maxIterations=10, kill switch >15
5. Validate → PASS
6. Test dry-run con sample question → tool selection logic verified
7. Genera README con setup MCP servers, prompt template, cost estimate

**Output**: workflow JSON con AI Agent ricco, README con cost analysis.

### Esempio 3 — Scheduled scraper → Google Sheet

**Tu**: "Ogni ora prendi prezzi da [3 competitor URL] e aggiungi riga su Google Sheet"

**Agent**:
1. Parse: trigger=schedule (hourly), source=HTML scrape, target=Google Sheets
2. Match recipe #9 (Scheduled scraper → Sheet)
3. Design: Schedule + 3x HTTP Request (parallel) + HTML Extract + Set + Google Sheets Append
4. Compliance check: User-Agent realistic, robots.txt menzionato in README
5. Validate → PASS
6. Test dry-run su 1 URL → extraction logic verified
7. Genera README con setup OAuth Sheets

**Output**: workflow + README + warning robots.txt compliance.

## FAQ

### 1. Posso usare l'agent senza MCP n8n attivo?

Sì. Fallback: workflow JSON viene salvato in file, importi manualmente in n8n UI (drag & drop o `n8n import:workflow`). Validation usa solo regex static check.

### 2. L'agent può modificare workflow esistenti?

Sì, ma solo se gli passi il JSON esistente come input ("aggiorna questo workflow per aggiungere step Y"). Per debugging workflow rotti, usa skill `n8n-validation-expert` o `analyze_execution_errors_comprehensive` MCP.

### 3. Differenza tra `/automation-architect` e skill `n8n-quickstart`?

- `n8n-quickstart` (skill) = quick start, recipes singoli, no orchestration
- `/automation-architect` (subagent) = full pipeline parse → design → validate → test → document, multi-skill chain, memory persistente per progetto

### 4. Cosa succede se requirement è ambiguo?

L'agent chiede 1 domanda focalizzata (no waterfall di 10 domande). Se manca trigger O action → block + chiedi. Se entrambi presenti, procede con default ragionevole + flag assumptions.

### 5. Output JSON è compatibile self-hosted?

Sì. Schema standard n8n cloud è retro-compatibile self-hosted. Usa `n8n import:workflow path/to/workflow.json` da CLI.

### 6. Come gestisce GDPR per EU PII?

Se config `gdpr.mode_active=true`:
- Aggiunge auto Set node KEEP only fields necessari (data minimization)
- Block su Article 9 sensitive data (health, religion, politics)
- Warn su cross-border transfer non-EU
- README include retention policy e DSAR procedure

### 7. Cost estimate per AI Agent workflows?

Auto-calcolato in README:
- Modello + max iterations
- Tokens stimati per execution
- Cost @ daily volume from config

### 8. Posso fare push live in n8n direttamente?

Sì se MCP `n8n-yellowtech`/`n8n-filippo` configurato. Sempre con conferma esplicita user (crea entità live). Default: JSON file output, push manuale.

## Troubleshooting

### "n8n-knowledge MCP not responding"

Fallback automatico a WebFetch n8n docs. Workflow build proceeds, validation usa regex static. Per restore: verifica MCP config in `~/.claude.json`, test con `npx @n8n/mcp-server-knowledge`.

### "Hardcoded secret detected" block

Hai una stringa tipo `Bearer abc123` in expression. Sostituisci con:
- n8n credential (managed, encrypted) — best
- Env var: `{{$env.MY_API_KEY}}` — OK per shared

### "Workflow >50 nodes" warning

Splittalo in sub-workflow. Master workflow chiama sub-workflow via `Execute Workflow` node.

### Expression error "undefined"

99% volte è webhook body access shallow:
```
❌ {{$json.email}}
✅ {{$json.body.email}}
```

Vedi `references/n8n-expression-syntax.md`.

### Workflow non si attiva in n8n

Checklist:
1. Tutte le credentials assigned (controlla nodes con icon ⚠)
2. Webhook path unique (no conflitto)
3. Settings → Error Workflow valid (esiste e attivo)
4. Test execution manuale: `executeWorkflow` con sample data

## Anti-pattern enforced (top 10)

L'agent BLOCCA o WARNS su:

1. Workflow senza error handling (production)
2. Credential hardcoded in expression
3. `$json.field` ambiguo in multi-item flow
4. Workflow >50 nodi senza split
5. Webhook senza HMAC/auth
6. AI Agent senza max iterations
7. HTTP Request senza timeout esplicito
8. Code node per cosa che Set fa
9. IF node nested >3 (use Switch)
10. GDPR mode active + no data minimization

## File del subagent

```
.claude/agents/automation-architect/
├── automation-architect.md        # Main subagent (488 lines)
├── BUILD-BRIEF.md                 # Build spec
├── PROGRESS.md                    # Build progress log
├── DECISIONS.md                   # Architectural decisions
├── README.md                      # This file
├── discovery/
│   └── questions.md               # 8 discovery questions
├── references/
│   ├── n8n-workflow-patterns-2026.md
│   ├── n8n-node-configuration.md
│   ├── n8n-expression-syntax.md
│   ├── n8n-validation-guide.md
│   ├── common-integrations-recipes.md
│   └── error-handling-patterns.md
├── research/
│   └── research-summary.md        # Phase A research output
├── skills/
│   ├── workflow-designer/SKILL.md
│   ├── node-validator/SKILL.md
│   ├── credential-mapper/SKILL.md
│   ├── workflow-tester/SKILL.md
│   └── workflow-documenter/SKILL.md
└── scripts/
    ├── validate_input.py          # Parse user requirement
    ├── workflow_design.py         # Generate skeleton JSON
    ├── workflow_validate.py       # Static validation
    ├── workflow_test.py           # Dry-run + fixtures
    ├── workflow_export.py         # README + Mermaid generator
    ├── mcp_detect.py              # MCP availability probe
    └── requirements.txt
```

## Chain con altri subagent

Output di `/automation-architect` può chainare a:

- `/document-factory` → genera client-facing PDF/slide del workflow
- `/lead-finder-pro` → se workflow è GTM lead capture
- `/outbound-orchestrator` → se workflow è outbound sequence dispatch

## Versioning

- v1.0 (2026-05-01) — initial release
- Skill ecosystem grounded: `n8n-*` 7 skill globali

## Crediti

- Skill ecosystem n8n by daymade / czlonkowski / community (forked + adapted)
- Recipe library: 10 recipes from real production workflows analyzed
- Validation patterns: telemetry-validated 7841 occurrences
