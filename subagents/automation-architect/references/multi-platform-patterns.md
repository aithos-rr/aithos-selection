# Multi-Platform Patterns

> Reference per `/automation-architect`. Portabilità delle 10 recipes canoniche (n8n-first) verso altre automation platform.
> Default agent: n8n. Per Make/Zapier/Pipedream/Workato la skill `platform-adapter-generator` produce adapter custom.

## Platform support matrix

| Platform | MCP nativo | REST API | Recipe coverage | Output mode default |
|----------|-----------|----------|-----------------|---------------------|
| n8n cloud | ✅ `n8n-knowledge` + user MCP | ✅ Full | 10/10 (first-class) | `create_live` |
| n8n self-hosted | ✅ `n8n-knowledge` + user MCP | ✅ Full | 10/10 | `create_live` |
| Make (Integromat) | 🟡 community partial | ✅ Full | 8/10 (no AI Agent + MCP Tool, no Error Workflow native) | `create_live` via REST |
| Zapier | ❌ no MCP | 🟡 limited public API (NLA experimental) | 6/10 (no AI Agent rich, limited DB ops) | JSON export + manual zap creation |
| Pipedream | 🟡 community MCP | ✅ Full | 9/10 (good AI Agent support, no native AI tool MCP yet) | `create_live` via REST |
| Workato | ❌ no MCP | ✅ Full | 9/10 (enterprise features, AI agent OK) | `create_live` via REST |
| Custom (Python/Node) | N/A | N/A | scaffold-as-code | scaffold project |

## Recipe portability detail

### Recipe #1 — Webhook → Notion CRM

| Platform | Native equivalent |
|----------|-------------------|
| n8n | Webhook node → Notion node |
| Make | Webhook trigger → Notion module |
| Zapier | Webhooks by Zapier → Notion zap |
| Pipedream | HTTP trigger → Notion action |
| Workato | HTTP webhook → Notion connector |

✅ Tutti supportati.

### Recipe #2 — Slack alert con thread

| Platform | Status |
|----------|--------|
| n8n | ✅ native |
| Make | ✅ native |
| Zapier | ✅ ma threading limitato (no reply preserve nativo) |
| Pipedream | ✅ |
| Workato | ✅ |

### Recipe #3 — Gmail digest scheduled

| Platform | Status |
|----------|--------|
| n8n | ✅ native (Schedule + Gmail) |
| Make | ✅ |
| Zapier | ✅ |
| Pipedream | ✅ |
| Workato | ✅ |

### Recipe #4 — Google Sheets ↔ DB sync (bidirectional)

| Platform | Status |
|----------|--------|
| n8n | ✅ |
| Make | ✅ |
| Zapier | 🟡 1-way OK, bidirectional richiede 2 zap |
| Pipedream | ✅ |
| Workato | ✅ |

### Recipe #5 — AI Agent + MCP Client Tool ⚡

| Platform | Status |
|----------|--------|
| n8n | ✅ first-class (LangChain Agent node + MCP Client Tool 2026) |
| Make | 🟡 OpenAI module ma no agent loop nativo, MCP non supportato |
| Zapier | 🟡 ChatGPT integration ma limited tool use, no MCP |
| Pipedream | ✅ AI workflow OK, no MCP nativo (ma può chiamare HTTP MCP server custom) |
| Workato | ✅ AI Workflow product (premium), no MCP nativo |

**Best fit: n8n.** Per altre platform → recipe semplificata (HTTP API call to LLM senza agent loop) o suggest n8n setup.

### Recipe #6 — HubSpot deal flow

| Platform | Status |
|----------|--------|
| n8n | ✅ |
| Make | ✅ |
| Zapier | ✅ (HubSpot first-party) |
| Pipedream | ✅ |
| Workato | ✅ first-class |

### Recipe #7 — Stripe webhook (HMAC verify)

| Platform | Status |
|----------|--------|
| n8n | ✅ Code node HMAC verify |
| Make | ✅ Crypto module o Custom JS |
| Zapier | 🟡 HMAC custom richiede Code Steps (paid plan) |
| Pipedream | ✅ Native HTTP + crypto JS |
| Workato | ✅ |

### Recipe #8 — Webhook → DB con dedup (idempotent)

| Platform | Status |
|----------|--------|
| n8n | ✅ |
| Make | ✅ |
| Zapier | ✅ |
| Pipedream | ✅ |
| Workato | ✅ |

### Recipe #9 — Scheduled scraper → Google Sheet

| Platform | Status |
|----------|--------|
| n8n | ✅ HTTP + HTML Extract + Sheets |
| Make | ✅ |
| Zapier | 🟡 limited HTML parsing, suggerisci HTTP + JSON only |
| Pipedream | ✅ Code Step + axios + cheerio |
| Workato | ✅ |

### Recipe #10 — Error monitor centralizzato

| Platform | Status |
|----------|--------|
| n8n | ✅ Error Workflow built-in |
| Make | 🟡 Error handler module ma scope per scenario, non centralizzato |
| Zapier | ❌ no error workflow concept, monitoring esterno richiesto |
| Pipedream | 🟡 try/catch nei step, no global handler |
| Workato | ✅ Error monitoring built-in (job logs) |

**Best fit per "monitor centralizzato": n8n.**

## Quando usare quale platform (decision tree)

```
Volume execution > 10k/day?
├── Sì → n8n self-hosted (queue mode) o Workato enterprise
└── No
    ├── AI Agent + MCP critico? → n8n cloud (only first-class)
    ├── No-code purissimo, team marketing? → Zapier
    ├── Logica visual ricca, conditional pesante? → Make
    ├── Code-first, team dev? → Pipedream o n8n self-hosted
    └── Enterprise compliance + SOC2? → Workato
```

## Cost comparison (approx, 2026)

| Platform | Free tier | Mid plan | Heavy use |
|----------|-----------|----------|-----------|
| n8n cloud | 14d trial | $20/mo (Pro) | $50+ self-hosted unlimited |
| Make | 1k ops/mo free | $9/mo (Core 10k) | $29 (Pro 50k) |
| Zapier | 100 tasks/mo | $20/mo (Pro 750) | $103 (Team 50k) |
| Pipedream | 10k credits | $19/mo | $49 (Advanced) |
| Workato | none | quote (~$10k+/yr) | enterprise |

## Anti-pattern cross-platform

1. **Assume n8n features in Zapier** → AI Agent loop, MCP, Error Workflow non esistono
2. **Use Zapier per high-volume** → cost esplode (per-task billing)
3. **Use Workato per startup small** → minimum spend troppo alto
4. **Mix platform senza orchestratore** → debug nightmare (use n8n come master se serve cross)
5. **Custom code (Pipedream / scaffold) senza error monitoring** → silent failures

## Output adapter generation flow

Vedi `skills/platform-adapter-generator/SKILL.md` per dettaglio. Schema:

```
Q2 platform → MCP probe
              ├── found → use MCP
              └── missing → API docs research → adapter.py + SKILL.md generated → smoke test → activate
```
