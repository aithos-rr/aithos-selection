# API Recipes — SmartLead + HeyReach

> Reference doc per `/outbound-orchestrator` scripts `smartlead_upload.py` + `heyreach_upload.py`. Recipes pronti, code esempi, MCP tool wrapper, fallback curl.
>
> Fonte: `research/research-summary.md` RQ2 + RQ3 + skill `~/.claude/skills/heyreach-api/SKILL.md` (testata 27/04/2026).

## SmartLead API recipes

### Base info

- Base URL: `https://server.smartlead.ai/api/v1/`
- Auth: query param `api_key=<KEY>` (NO header)
- Rate limit: 100 req/min (Pro: 1000)
- MCP: `mcp__smartlead__*` namespace (LeadMagic 113 tools)

### Recipe 1 — Crea campagna + sequence + leads

```python
# 1. Create campaign
campaign = mcp__smartlead__smartlead_create_campaign(
    name="Yellow Tech — Series A SaaS — Q2 2026",
    client_id=None  # or specific client_id se Agency mode
)
campaign_id = campaign["id"]

# 2. Add email accounts (sender mailbox)
mcp__smartlead__smartlead_add_email_account_to_campaign(
    campaign_id=campaign_id,
    email_account_ids=[12345, 12346]  # IDs from list_email_accounts
)

# 3. Save sequence (multi-step)
sequence = [
    {
        "seq_number": 1,
        "seq_delay_days": 0,
        "subject": "Domanda su {{company}}",  # NOTE: SmartLead usa double brace
        "email_body": "Ciao {{first_name}},\n\n{{first_line}}\n\n...",
        "send_as_new_thread": False
    },
    {
        "seq_number": 2,
        "seq_delay_days": 5,
        "subject": "Re: Domanda su {{company}}",
        "email_body": "...",
        "send_as_new_thread": False
    },
    # ...
]
mcp__smartlead__smartlead_save_campaign_sequence(
    campaign_id=campaign_id,
    sequences=sequence
)

# 4. Add leads (chunked 500 per request)
leads = [
    {
        "first_name": "Marco",
        "last_name": "Rossi",
        "email": "marco.rossi@company.com",
        "company_name": "Acme Inc",
        "custom_fields": {
            "first_line": "Vidi che sei passato a CMO ad Acme...",
            "signal_used": "job_change"
        }
    },
    # ...
]
mcp__smartlead__smartlead_add_leads_to_campaign(
    campaign_id=campaign_id,
    lead_list=leads,
    settings={
        "ignore_global_block_list": False,
        "ignore_unsubscribe_list": False,
        "ignore_duplicate_leads_in_other_campaigns": False
    }
)

# 5. Setup webhook (optional, ricordo: SmartLead webhook NO native MCP)
# Use direct curl/requests:
import requests
requests.post(
    f"https://server.smartlead.ai/api/v1/campaigns/{campaign_id}/webhooks?api_key={SMARTLEAD_API_KEY}",
    json={
        "name": "outbound-orchestrator-replies",
        "webhook_url": "https://your-handler.com/smartlead-webhook",
        "event_types": ["LEAD_REPLIED", "LEAD_BOUNCED", "LEAD_UNSUBSCRIBED"],
        "categories": ["Interested", "Not-Interested", "Out-of-Office"]
    }
)

# 6. Update status (start campaign)
mcp__smartlead__smartlead_update_campaign_status(
    campaign_id=campaign_id,
    status="START"  # | "PAUSED" | "STOPPED"
)
```

### Recipe 2 — Schedule (timing + timezone)

```python
mcp__smartlead__smartlead_update_campaign_schedule(
    campaign_id=campaign_id,
    timezone="Europe/Rome",  # IANA timezone
    days_of_the_week=[1, 2, 3, 4, 5],  # Mon-Fri (1-7 with Sun=7)
    start_hour="09:00",
    end_hour="13:00",
    min_time_btw_emails=10,  # min minutes between emails
    max_new_leads_per_day=50,  # daily cap
    schedule_start_time="2026-05-01T09:00:00Z"  # campaign go-live
)
```

### Recipe 3 — Read campaign statistics

```python
stats = mcp__smartlead__smartlead_get_campaign_statistics(
    campaign_id=campaign_id
)
# Returns: {sent_count, opened_count, clicked_count, replied_count, bounced_count, unsubscribed_count, ...}

# By date range
stats_range = mcp__smartlead__smartlead_get_campaign_statistics_by_date_range(
    campaign_id=campaign_id,
    start_date="2026-04-01",
    end_date="2026-04-30"
)
```

### Recipe 4 — Update lead category (post reply classification)

```python
mcp__smartlead__smartlead_update_lead_category(
    lead_id=lead_id,
    campaign_id=campaign_id,
    category="Interested"  # | "Not-Interested" | "Out-of-Office" | "Wrong-Person" | "Do-Not-Contact"
)
```

### Recipe 5 — Pause/Resume single lead

```python
# Pause specifico lead in campaign
mcp__smartlead__smartlead_pause_lead_by_campaign(
    lead_id=lead_id,
    campaign_id=campaign_id
)

# Resume
mcp__smartlead__smartlead_resume_lead_by_campaign(
    lead_id=lead_id,
    campaign_id=campaign_id
)
```

### Recipe 6 — Suppress lead (cross-campaign)

```python
mcp__smartlead__smartlead_add_lead_to_global_blocklist(
    domain_or_email="marco.rossi@company.com"  # Exact email or domain
)

# Or unsubscribe from all campaigns
mcp__smartlead__smartlead_unsubscribe_lead_from_all_campaigns(
    lead_id=lead_id
)
```

### Recipe 7 — Reply forward (chain Gmail MCP)

Quando reply classification = `positive`:

```python
# 1. Get reply content
history = mcp__smartlead__smartlead_fetch_lead_message_history(
    lead_id=lead_id,
    campaign_id=campaign_id
)
last_reply = history["messages"][-1]

# 2. Forward to user inbox via Gmail draft
mcp__claude_ai_Gmail__create_draft(
    to=USER_INBOX_EMAIL,
    subject=f"[Outbound positive reply] {last_reply['lead_email']}",
    body=f"""Lead {last_reply['lead_email']} ha risposto positivamente alla campagna {campaign_name}.

Reply:
{last_reply['body']}

Lead profile: {lead_profile_summary}
Action raccomandata: rispondi a {last_reply['lead_email']} entro 24h.
"""
)
```

## HeyReach API recipes

### Base info

- Base URL: `https://api.heyreach.io/api/public/`
- Auth: header `X-API-KEY: <KEY>`
- **NON usare `/v2/`** nel path
- Workspace-scoped key (ogni workspace HeyReach = key diversa)
- MCP: `mcp__heyreach__*` namespace (configurato globalmente, default workspace Yellow Tech)

### Sintassi placeholder CRITICA

**HeyReach usa SINGLE brace** `{first_name}`, **NON double**. Bug noto: `{{var}}` invia letterali. Auto-fix regex obbligatorio.

```python
import re
DOUBLE = re.compile(r"\{\{([A-Za-z][A-Za-z0-9_-]*)\}\}")

def fix_double_brace(s):
    """Fix {{var}} → {var} per HeyReach."""
    return DOUBLE.sub(r"{\1}", s) if isinstance(s, str) else s
```

### Recipe 1 — Crea campagna LinkedIn

```python
# 1. Create empty list (lead container) se nuova
list_data = mcp__heyreach__create_empty_list(
    name="Outbound Q2 2026 — SaaS Series A USA"
)
list_id = list_data["listId"]

# 2. Add leads to list
leads_payload = [
    {
        "linkedInUrl": "https://www.linkedin.com/in/marco-rossi/",
        "firstName": "Marco",
        "lastName": "Rossi",
        "company": "Acme Inc",
        "customFields": [
            {"name": "li_message1", "value": "Ciao {first_name}, vidi che sei passato a CMO ad Acme..."},
            {"name": "li_message2", "value": "Riprendo brevemente, ho mandato 2 email..."},
            {"name": "signal_used", "value": "job_change"}
        ]
    }
]
mcp__heyreach__add_leads_to_list_v2(
    listId=list_id,
    leads=leads_payload
)

# 3. Create campaign (linka list + sender)
campaign = mcp__heyreach__create_workflow(  # Note: API potrebbe esporlo come create_workflow nel MCP
    name="Outbound Q2 2026 SaaS LinkedIn",
    linkedInAccountIds=[186644],  # sender LinkedIn account IDs
    linkedInUserListId=list_id
)
campaign_id = campaign["campaignId"]

# 4. Build sequence (tree ricorsivo) — usa Update Sequence
sequence_obj = build_sequence_tree(steps_definition)

# AUTO-FIX double brace prima di POST
sequence_obj_fixed = recursive_fix_double_brace(sequence_obj)

# Update via direct API (no MCP wrapper diretto per UpdateSequence)
import requests
HEYREACH_API_KEY = os.environ["HEYREACH_API_KEY"]
requests.post(
    "https://api.heyreach.io/api/public/campaign/UpdateSequence",
    headers={"X-API-KEY": HEYREACH_API_KEY, "Content-Type": "application/json"},
    json={"campaignId": campaign_id, "sequence": sequence_obj_fixed}
)

# 5. Resume to start
mcp__heyreach__resume_campaign(campaign_id=campaign_id)
```

### Recipe 2 — Sequence shape (tree ricorsivo)

```python
def build_sequence_tree(steps_definition):
    """Build tree ricorsivo HeyReach.

    nodeType: CHECK_IS_CONNECTION | MESSAGE | CONNECTION_REQUEST | INMAIL | VIEW_PROFILE | LIKE_POST | END
    """
    return {
        "nodeType": "CONNECTION_REQUEST",
        "actionDelay": 0,
        "actionDelayUnit": "DAYS",
        "payload": {
            "messages": ["Ciao {first_name}, ho visto del round Series A — congrats!"],
            "fallbackMessage": "Ciao {first_name}, ho visto interesse nel tuo profilo."
        },
        "conditionalNode": {
            "nodeType": "CHECK_IS_CONNECTION",
            "actionDelay": 5,
            "actionDelayUnit": "DAYS",
            "conditionalNode": {
                "nodeType": "MESSAGE",
                "actionDelay": 0,
                "actionDelayUnit": "DAYS",
                "payload": {
                    "messages": ["{first_name}, grazie per la conn! Volevo chiederti..."],
                    "fallbackMessage": "Grazie per la conn!"
                }
            },
            "unconditionalNode": {
                "nodeType": "END"
            }
        },
        "unconditionalNode": {
            "nodeType": "END"
        }
    }
```

### Recipe 3 — Trick edit FINISHED campaign

Se campaign è FINISHED, `UpdateSequence` ritorna HTTP 400. Workaround:

```python
import requests, time

# 1. Resume from FINISHED → IN_PROGRESS (no real send se no pending lead)
requests.post(
    f"https://api.heyreach.io/api/public/campaign/Resume?campaignId={campaign_id}",
    headers={"X-API-KEY": HEYREACH_API_KEY}
)
time.sleep(2)

# 2. Pause → PAUSED
requests.post(
    f"https://api.heyreach.io/api/public/campaign/Pause?campaignId={campaign_id}",
    headers={"X-API-KEY": HEYREACH_API_KEY}
)
time.sleep(2)

# 3. Now UpdateSequence works
requests.post(
    "https://api.heyreach.io/api/public/campaign/UpdateSequence",
    headers={"X-API-KEY": HEYREACH_API_KEY, "Content-Type": "application/json"},
    json={"campaignId": campaign_id, "sequence": new_sequence}
)
```

Source: skill `heyreach-api` testata 27/04/2026 in produzione su 6 campagne real-world.

### Recipe 4 — Stop lead (single)

```python
import requests
requests.post(
    "https://api.heyreach.io/api/public/campaign/StopLeadInCampaign",
    headers={"X-API-KEY": HEYREACH_API_KEY, "Content-Type": "application/json"},
    json={"campaignId": campaign_id, "leadUrl": "https://www.linkedin.com/in/marco-rossi/"}
)
# 404 if not in campaign (no error, just info — utile per "stop in tutte le campagne, una sola attecchirà")
# "Cannot perform the action because the workflow is in FAILED state." = già fermo
```

### Recipe 5 — Read conversations

```python
conversations = mcp__heyreach__get_conversations_v2(
    limit=50,
    offset=0
)
# Returns: {items: [{lastMessageText, lastMessageSender, leadUrl, ...}], total: N}
# NOTE: messages array NON popolato qui. Per full thread serve mcp__heyreach__get_chatroom
```

### Recipe 6 — Read sender LinkedIn accounts

```python
accounts = mcp__heyreach__get_all_linked_in_accounts()
# Returns: [{id, email, fullName, authIsValid, ...}]

# authIsValid = false → re-auth richiesto, no send possibile
for acc in accounts:
    if not acc["authIsValid"]:
        warn(f"Account {acc['id']} ({acc['email']}) auth invalid — re-link in HeyReach UI")
```

### Recipe 7 — Lead list management

```python
# Read leads from list (incluso customFields)
leads = mcp__heyreach__get_leads_from_list(
    list_id=list_id,
    limit=100,
    offset=0
)
# Returns: [{id, linkedInUrl, firstName, customFields: [{name, value}], ...}]

# Read customFields per-lead
for lead in leads:
    li_message1 = next((f["value"] for f in lead.get("customFields", []) if f["name"] == "li_message1"), None)
```

### Recipe 8 — Edge case: shared list

Se 2 campaigns condividono `linkedInUserListId`:

- Stop su una list = riflesso su entrambe
- Sempre stop cross-campaign se shared list
- Per identificare list shared: query `mcp__heyreach__get_list_by_id(list_id)` → check `usedInCampaigns: [...]`

```python
def stop_lead_cross_campaign(lead_url, list_id):
    """Stop lead in TUTTE le campaigns che usano questa list."""
    list_info = mcp__heyreach__get_list_by_id(list_id=list_id)
    for campaign_id in list_info.get("usedInCampaigns", []):
        try:
            requests.post(
                "https://api.heyreach.io/api/public/campaign/StopLeadInCampaign",
                headers={"X-API-KEY": HEYREACH_API_KEY},
                json={"campaignId": campaign_id, "leadUrl": lead_url}
            )
        except Exception as e:
            log(f"Stop lead {lead_url} in campaign {campaign_id}: {e}")
```

## Curl fallback (se MCP missing)

Idem pattern via `requests` o `curl`:

```bash
# SmartLead — create campaign
curl -X POST "https://server.smartlead.ai/api/v1/campaigns/create?api_key=$SMARTLEAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test campaign", "client_id": null}'

# HeyReach — get all campaigns
curl -X POST "https://api.heyreach.io/api/public/campaign/GetAll" \
  -H "X-API-KEY: $HEYREACH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"limit": 50, "offset": 0}'
```

## API key check at runtime

Skill all'avvio:

```python
import os, sys

required_keys = []
if config["stack"]["outbound_primary"] == "smartlead":
    required_keys.append("SMARTLEAD_API_KEY")
if config["stack"]["outbound_secondary"] == "heyreach":
    required_keys.append("HEYREACH_API_KEY")

missing = [k for k in required_keys if not os.environ.get(k)]
if missing:
    print(f"❌ Missing env vars: {', '.join(missing)}")
    print("Add to ~/.zshrc:")
    for k in missing:
        print(f"  export {k}='your_key_here'")
    sys.exit(1)
```

## Reference esterni

- [SmartLead API Introduction](https://api.smartlead.ai/introduction)
- [SmartLead Help Center — Full API Documentation](https://helpcenter.smartlead.ai/en/articles/125-full-api-documentation)
- [SmartLead Webhooks Guide](https://helpcenter.smartlead.ai/en/articles/35-webhook-guide)
- [LeadMagic SmartLead MCP Server (113 tools)](https://github.com/LeadMagic/smartlead-mcp-server)
- [HeyReach Public API Postman Collection](https://documenter.getpostman.com/view/24067770/2sA3JT1QvX)
- [HeyReach Custom Variables (single-brace)](https://help.heyreach.io/en/articles/9879182-how-to-import-and-use-custom-variables)
- Skill grounded `~/.claude/skills/heyreach-api/SKILL.md` (testata 27/04/2026)
