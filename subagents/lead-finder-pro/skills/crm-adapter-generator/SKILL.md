---
name: crm-adapter-generator
description: Genera dinamicamente un adapter CRM custom quando il CRM scelto dall'utente non ha MCP server nativo. Studia API docs (WebFetch + context7), produce skill markdown + Python helper script con `create_record`, `search_record`, `update_record`. Salva in `<memory>/skills-generated/<crm-name>/`. Usato in Fase Platform Detection di `/lead-finder-pro` se CRM scelto in Q3 non ha MCP available.
---

# crm-adapter-generator

Auto-extension capability per `/lead-finder-pro`: l'agente non assume più Attio come default CRM, ma si adatta al CRM scelto in Q3 generando skill custom on-demand.

## Quando attivarmi

In Fase Platform Detection (subito dopo discovery), se:

- `stack.crm` NOT IN supported list (Attio MCP, HubSpot MCP, Pipedrive MCP)
- AND `<memory>/skills-generated/<crm-name>/SKILL.md` NOT EXISTS
- AND utente fornisce API key del CRM (in `.env` o discovery follow-up)

Skip se:

- CRM ha MCP nativo (use it directly)
- Già generato in run precedente (re-use cached skill)
- Utente sceglie "Nessuno (CSV/Sheet only)" — output CSV-first

## Input

```json
{
  "crm_name": "Pipedrive",
  "api_key_env_var": "PIPEDRIVE_API_KEY",
  "config": { "user_role": "founder", "icp_geo": "EU" }
}
```

## Logic flow

### Step 1 — MCP registry probe

Prima cosa: cerca MCP esistente per quel CRM. Sources:

- `~/.claude.json` — local user MCPs
- `.mcp.json` (project scope) — project MCPs
- MCP registry public (https://mcpservers.org or https://github.com/topics/mcp-server)
- Common name patterns: `<crm>-mcp`, `mcp-<crm>`, `@<crm>/mcp-server`

Se trovato MCP → return early con `{action: "use_mcp", server_name: "<x>-mcp"}`.

### Step 2 — API docs research

Se no MCP, use WebFetch + context7 (se disponibile) per studiare API:

1. WebFetch root API docs URL (es. `https://developers.pipedrive.com/docs/api/v1`)
2. Identifica endpoint critici:
   - `POST /persons` o equivalent (create lead/contact)
   - `GET /persons/search` o equivalent
   - `PUT /persons/{id}` o equivalent
3. Estrai auth method (API key header, Bearer token, OAuth)
4. Estrai field mapping (CRM field name → standard `email|name|company|...`)

### Step 3 — Generate adapter skill

Crea file `<memory>/skills-generated/<crm-name>/SKILL.md` con template:

```yaml
---
name: <crm-name>-adapter
description: Auto-generated adapter for <CRM Name>. Provides create_record, search_record, update_record via REST API.
generated_by: crm-adapter-generator
generated_at: YYYY-MM-DD
api_docs: <docs URL>
---

# <crm-name>-adapter (auto-generated)

## Auth

Header: `Authorization: Bearer {{$env.<API_KEY_ENV_VAR>}}`
o equivalent (header name + value pattern).

## Operations

### create_record (lead/contact)

Endpoint: `POST <base_url>/<resource>`

Field mapping (lead-finder-pro standard → CRM field):
- `email` → `<crm field>`
- `name` → `<crm field>`
- `company` → `<crm field>`
- `phone` → `<crm field>`
- `role` → `<crm field>`
- `linkedin_url` → `<crm field>` (custom field se non native)

Example call:
\`\`\`bash
curl -X POST <base_url>/<resource> \
  -H "Authorization: Bearer ${<API_KEY>}" \
  -H "Content-Type: application/json" \
  -d '{"<email_field>": "lead@example.com", "<name_field>": "John Doe", ...}'
\`\`\`

### search_record (dedup check)

Endpoint: `GET <base_url>/<resource>/search?term=<email>`

### update_record

Endpoint: `PUT <base_url>/<resource>/{id}`

## Rate limits

<from API docs>

## Custom fields (manual setup checklist)

Se CRM non ha campi `linkedin_url`, `icp_score`, `icp_grade`, `signal_type` nativi:
- [ ] Crea custom field "LinkedIn URL" (text)
- [ ] Crea custom field "ICP Score" (number 0-100)
- [ ] Crea custom field "ICP Grade" (select A/B/C/D)
- [ ] Crea custom field "Signal Type" (text)
```

### Step 4 — Generate Python helper

`<memory>/skills-generated/<crm-name>/adapter.py`:

```python
"""Auto-generated <CRM> adapter for /lead-finder-pro."""
import os
import requests

BASE_URL = "<from API docs>"
API_KEY = os.environ.get("<ENV_VAR>")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def create_record(lead: dict) -> dict:
    """Push lead into CRM. Lead schema: {email, name, company, phone, role, ...}"""
    payload = {
        # field mapping from API docs
        "<crm_email>": lead["email"],
        "<crm_name>": lead["name"],
        "<crm_company>": lead.get("company", ""),
    }
    r = requests.post(f"{BASE_URL}/<resource>", headers=HEADERS, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def search_record(email: str) -> dict | None:
    """Dedup check. Returns existing record dict or None."""
    r = requests.get(f"{BASE_URL}/<resource>/search", headers=HEADERS,
                     params={"term": email, "field": "email"}, timeout=10)
    if r.ok and r.json().get("data"):
        return r.json()["data"][0]
    return None

def update_record(record_id: str, updates: dict) -> dict:
    r = requests.put(f"{BASE_URL}/<resource>/{record_id}",
                     headers=HEADERS, json=updates, timeout=10)
    r.raise_for_status()
    return r.json()
```

### Step 5 — Validation smoke test

1. Test API key: `GET <base>/me` o equivalent → expect 200
2. Test search (read-only): random email → expect 200 (anche con 0 results)
3. Test create dry-run: se API ha `?dry_run=true` o staging, use it; altrimenti skip
4. Update config `<memory>/config.md`: `crm.adapter_skill_generated: true`, `crm.adapter_path: <memory>/skills-generated/<crm-name>/`

### Step 6 — Confirm con utente

```
✓ Generato adapter <CRM> custom in <memory>/skills-generated/<crm-name>/

Adesso /lead-finder-pro può:
- Creare lead nel tuo CRM <CRM> direttamente (default mode)
- Dedup via email lookup
- Update lead esistenti

Setup richiesto da te:
- [ ] Aggiungi <ENV_VAR>=... in .env
- [ ] (Opzionale) Crea i 4 custom field elencati nello skill, per metadata enrichment

Procedo a fare un test write su un record di test? (1 lead solo, dry-run se possibile)
```

## Output

```json
{
  "action": "skill_generated",
  "crm_name": "Pipedrive",
  "skill_path": "<memory>/skills-generated/pipedrive-adapter/SKILL.md",
  "adapter_script": "<memory>/skills-generated/pipedrive-adapter/adapter.py",
  "operations_supported": ["create_record", "search_record", "update_record"],
  "auth_method": "API key header",
  "rate_limit": "100 req/min",
  "custom_fields_required": ["LinkedIn URL", "ICP Score", "ICP Grade"],
  "smoke_test": "passed"
}
```

## CRM supported (priority order)

| CRM | MCP nativo | API key required | Notes |
|-----|-----------|------------------|-------|
| Attio | ✅ `attio-mcp` | ATTIO_API_KEY | First class — default MCP path |
| HubSpot | 🟡 community MCP | HUBSPOT_API_KEY | Check community MCP first, fallback API |
| Pipedrive | ❌ | PIPEDRIVE_API_KEY | Always API path → generate skill |
| Salesforce | ❌ | SF_USER + SF_PASS + SF_TOKEN | OAuth complex, generate skill |
| Zoho CRM | ❌ | ZOHO_TOKEN | OAuth refresh, generate skill |
| Notion DB (as CRM) | ✅ `notion-mcp` (community) | NOTION_API_KEY | Use Notion MCP if avail |
| Airtable (as CRM) | 🟡 | AIRTABLE_API_KEY | Schema-flexible, generate skill |
| Custom (any REST API) | ❌ | (user-provided) | Ask user for API docs URL → generate skill |

## Anti-pattern

1. **No mass create senza dedup** — sempre `search_record` first
2. **No hardcoded credential** — sempre `os.environ.get(...)` con error guard
3. **No ignore rate limit** — respect API docs limits
4. **No skip smoke test** — sempre validate adapter before activating
5. **No overwrite custom fields** — write-only-to-empty pattern (DECISION-010 di /lead-finder-pro)
6. **No skill regeneration ogni run** — cache in `<memory>/skills-generated/`, regenerate solo se utente dice "regenerate <crm>" o config cambia

## Ricovery se MCP / API entrambi non disponibili

Fallback: output CSV import-ready in `output/leads_<crm>_<timestamp>.csv` con header standard CRM. Doc `references/csv-import-guide-<crm>.md` se reference esiste.
