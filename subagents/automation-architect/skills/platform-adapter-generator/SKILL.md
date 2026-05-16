---
name: platform-adapter-generator
description: Genera dinamicamente un adapter per la automation platform scelta dall'utente (n8n, Make, Zapier, Pipedream, Workato, custom). Detect MCP availability, fallback su REST API research via WebFetch + context7, produce skill markdown + Python helper con `create_workflow_live`, `update_workflow`, `test_workflow`. Salva in `<memory>/skills-generated/<platform>/`. Usato in Fase Platform Detection di `/automation-architect`. Permette default mode = create live workflow, JSON export solo come fallback.
---

# platform-adapter-generator

Auto-extension capability per `/automation-architect`: l'agente non assume più solo n8n, ma rileva la platform scelta in Q2 e genera l'adapter giusto on-demand. Default output diventa **"workflow creato live nella platform"**, non più "JSON file da importare".

## Quando attivarmi

In Fase Platform Detection (subito dopo discovery), per ogni run:

1. Check `stack.platform` da config (popolato da Q2)
2. Probe MCP availability per quella platform
3. Se MCP found → use it directly (skip generation)
4. Se MCP missing AND API key available → generate adapter skill custom
5. Se entrambi missing → fallback "JSON export only" mode + setup guide

Skip se:

- Platform già supportata via MCP nativo (n8n via `n8n-knowledge` + `n8n-yellowtech`/`n8n-filippo`)
- Adapter già generato in run precedente per stessa platform (cache check)
- Utente sceglie "Sto valutando" — modalità learning, output JSON pedagogico

## Input

```json
{
  "platform_name": "Make",
  "platform_mode": "cloud|self_hosted",
  "api_key_env_var": "MAKE_API_KEY",
  "api_base_url_optional": "https://eu1.make.com/api/v2",
  "config": { "user_role": "founder", "scale": "100_1k" }
}
```

## Logic flow

### Step 1 — MCP registry probe

```bash
# Probe order
1. ~/.claude.json mcpServers section → look for <platform>-mcp or mcp-<platform>
2. .mcp.json project scope
3. Common community MCPs (knowledge):
   - n8n: n8n-knowledge, n8n-yellowtech, n8n-filippo, n8n-mcp ✅ first-class support
   - Make: make-mcp (community, partial coverage 2026)
   - Zapier: NO official MCP, use REST API only
   - Pipedream: pipedream-mcp (community, 2026)
   - Workato: NO MCP, REST API only
4. WebFetch https://mcpservers.org search per platform name (best-effort)
```

Output: `{action: "use_mcp", server: "<x>"}` o `{action: "generate_adapter"}`.

### Step 2 — API docs research

Se MCP missing, study API docs:

| Platform | Docs URL |
|----------|----------|
| Make | https://developers.make.com/api-documentation |
| Zapier | https://platform.zapier.com/build/api (limited public API for Zaps) |
| Pipedream | https://pipedream.com/docs/api/rest |
| Workato | https://docs.workato.com/oem/oem-api.html |
| n8n | https://docs.n8n.io/api/ |

Use WebFetch + (se context7 disponibile) `mcp__context7__resolve-library-id` + `query-docs` per pull esempi codice ufficiali.

Estrai:

1. Auth method (API key, OAuth, Bearer)
2. Endpoint create scenario/zap/workflow
3. Endpoint test/run scenario
4. Endpoint update scenario
5. Endpoint list scenarios (per dedup check)
6. Format payload (JSON shape — Make scenario blueprint, Zapier zap definition, Pipedream workflow YAML, n8n workflow JSON, Workato recipe JSON)
7. Limit + quota

### Step 3 — Generate adapter skill

Crea `<memory>/skills-generated/<platform>/SKILL.md`:

```yaml
---
name: <platform>-adapter
description: Auto-generated adapter for <Platform Name>. Provides create_workflow_live, update_workflow, test_workflow, list_workflows via REST API.
generated_by: platform-adapter-generator
generated_at: YYYY-MM-DD
api_docs: <docs URL>
auth_method: API key | OAuth | Bearer
rate_limit: <from docs>
---

# <platform>-adapter (auto-generated)

## Auth setup

Env var required: `<API_KEY_ENV_VAR>` in `.env` o `<memory>/credentials.example.md`

## Operations

### create_workflow_live(config: dict) -> dict

Endpoint: `POST <base_url>/<resource>`

Map standard archetype → platform native:
- `webhook_driven` → <platform native trigger>
- `scheduled` → <platform native cron>
- `ai_agent` → <platform native AI step>
- `data_pipeline` → <platform native chain>

Returns: `{id, url, status}`

### test_workflow(workflow_id, fixture)

### update_workflow(workflow_id, patch)

### list_workflows(filter)

## Native payload schema

<platform-specific JSON shape pulled from API docs>

## Recipe mapping (from /automation-architect 10 standard recipes)

Per ogni recipe canonica di /automation-architect:
- recipe #1 (Webhook → Notion CRM) → <platform pattern>
- recipe #2 (Slack alert thread) → <platform pattern>
...

## Anti-pattern <platform-specific>

<error patterns from API docs>
```

### Step 4 — Generate Python helper

`<memory>/skills-generated/<platform>/adapter.py`:

```python
"""Auto-generated <Platform> adapter for /automation-architect."""
import os
import requests

BASE_URL = "<from docs>"
API_KEY = os.environ.get("<ENV_VAR>")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def create_workflow_live(workflow_payload: dict) -> dict:
    """Push workflow into platform. Returns {id, url}.
    Args:
        workflow_payload: native platform JSON (e.g. n8n workflow JSON, Make blueprint, Zapier zap definition)
    """
    r = requests.post(f"{BASE_URL}/<resource>", headers=HEADERS, json=workflow_payload, timeout=15)
    r.raise_for_status()
    return r.json()

def test_workflow(workflow_id: str, fixture: dict) -> dict:
    r = requests.post(f"{BASE_URL}/<resource>/{workflow_id}/run",
                      headers=HEADERS, json=fixture, timeout=30)
    return r.json() if r.ok else {"error": r.text}

def update_workflow(workflow_id: str, patch: dict) -> dict:
    r = requests.patch(f"{BASE_URL}/<resource>/{workflow_id}",
                       headers=HEADERS, json=patch, timeout=10)
    r.raise_for_status()
    return r.json()
```

### Step 5 — Validation smoke test

1. Test API key valid: `GET <base>/me` o equivalent → expect 200
2. Test list workflows (read-only): expect 200 list (anche vuoto)
3. Test create dry-run: se platform supporta `?validate=true` o staging — use it
4. Update config `<memory>/config.md`:
   - `platform.adapter_skill_generated: true`
   - `platform.adapter_path: <memory>/skills-generated/<platform>/`
   - `output_mode_default: "create_live"`

### Step 6 — Confirm con utente

```
✓ Generato adapter <Platform> custom in <memory>/skills-generated/<platform>/

Adesso /automation-architect può:
- Creare workflow direttamente nel tuo <Platform> (default)
- Test execution con fixture
- Update workflow esistenti
- JSON export disponibile come fallback con flag --json-only

Setup richiesto da te:
- [ ] Aggiungi <ENV_VAR>=... in .env
- [ ] Verifica scope token (deve includere create/update/run)

Procedo a creare un workflow di test (semplice ping → echo) per validare l'adapter?
```

## Output

```json
{
  "action": "skill_generated",
  "platform_name": "Make",
  "skill_path": "<memory>/skills-generated/make/SKILL.md",
  "adapter_script": "<memory>/skills-generated/make/adapter.py",
  "operations_supported": ["create_workflow_live", "test_workflow", "update_workflow", "list_workflows"],
  "default_output_mode": "create_live",
  "auth_method": "Bearer token",
  "rate_limit": "60 req/min",
  "smoke_test": "passed"
}
```

## Platforms supported (priority order)

| Platform | MCP nativo | API status | Output mode default |
|----------|-----------|-----------|---------------------|
| n8n cloud | ✅ `n8n-knowledge` + `n8n-yellowtech` | REST API + MCP | create_live (recommended) |
| n8n self-hosted | ✅ `n8n-knowledge` + user MCP | REST API + MCP | create_live |
| Make | 🟡 community MCP partial | REST API ufficiale | create_live via REST |
| Zapier | ❌ NO MCP | Public API limited (NLA experimental) | JSON export + manual import (constraint) |
| Pipedream | 🟡 community MCP | REST API ufficiale | create_live via REST |
| Workato | ❌ NO MCP | REST API ufficiale | create_live via REST |
| Custom (Python/Node) | ❌ NO MCP | Custom code | Generate scaffold project |
| Sto valutando | N/A | N/A | JSON pedagogical export + comparison guide |

## Recipe portability (from 10 standard recipes)

Le 10 recipes canoniche di `/automation-architect` (`references/common-integrations-recipes.md`) sono **n8n-first**. Per altre platform:

- Webhook → DB con dedup (recipe #8): portabile a Make/Zapier/Pipedream/Workato (tutti supportano webhook + DB)
- AI Agent + MCP Client Tool (recipe #5): **n8n-only** (Make/Zapier limited AI agent native, Pipedream sì)
- Stripe webhook (recipe #7): portabile (HMAC verify funziona ovunque)
- Scheduled scraper (recipe #9): portabile
- Error monitor (recipe #10): n8n-only Error Workflow concept; per altri platform usa monitoring esterno

`references/multi-platform-patterns.md` (creato a parte) elenca portabilità per ognuna.

## Anti-pattern

1. **No assume n8n-only** — discovery Q2 must precede design
2. **No hardcoded credential** — sempre env var
3. **No skip smoke test** — sempre validate adapter pre-activation
4. **No skill regeneration ogni run** — cache in `<memory>/`, only regenerate on user "regenerate <platform>" or config change
5. **No fail silently se MCP + API both missing** — explicit error + fallback to JSON export with setup guide
6. **No mix recipes cross-platform senza check** — alcune recipes (AI Agent, Error Workflow) sono platform-specific

## Recovery se nemmeno API disponibile

Fallback grazioso: output workflow native JSON in `output/workflow-<name>-<platform>.<ext>` (es. `.n8n.json`, `.make-blueprint.json`, `.zapier-zap.json`) + step-by-step import guide in `output/setup-<platform>.md`.
