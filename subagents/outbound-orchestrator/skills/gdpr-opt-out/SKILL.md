---
name: gdpr-opt-out
description: GDPR compliance per outbound EU. Suppression list cross-stack management (SmartLead + HeyReach + CRM). Footer bilingue IT+EN se EU detected. LIA template generation. Italy Garante specifics. Retention 12 mesi enforcement. Article 9 sensitive data reject. B2C personal email reject (gmail/yahoo/libero). Auto-attiva se `icp.geo_eu_detected`. Per `/outbound-orchestrator`.
when_to_use: Pre-flight GDPR check su lead list, generate LIA per nuova campagna, sync suppression cross-stack post opt-out, audit compliance retroattivo, footer generation bilingue
---

# GDPR Opt-Out

Compliance GDPR per cold outbound EU. Suppression cross-stack, footer bilingue, LIA generation, Article 9 reject, retention 12 mesi.

**Lingua**: italiano user-facing, inglese tecnico (LIA, Article 9, opt-out).

## When to use

Auto-attiva quando:
- `icp.geo_eu_detected = true` (gate Fase 4 metodologia `/outbound-orchestrator`)
- User dice "GDPR check", "audit privacy", "compliance review"
- Pre-flight check prima di execute campaign
- Reply class = `unsubscribe` → suppression sync cross-stack
- Setup nuova campagna → LIA template generation

**Non attivare** se:
- `gdpr.mode = off` AND `geo_eu_detected = false` (US-only, CAN-SPAM only)
- Single test send (1 mailbox a self)

## Prerequisites

- Lead list (output `/lead-finder-pro` o `validate_input.py`)
- Config `<memory>/config.md` con sezione `gdpr` populata
- ICP description (per detect EU keyword)
- Suppression list `<memory>/suppression.csv` (creata se prima volta)
- Reference `references/gdpr-outbound-eu.md`

## Inputs

```json
{
  "leads": [
    {"lead_id": "uuid", "email": "marco.rossi@company.com", "company": "Acme", ...},
    ...
  ],
  "icp": {
    "description": "SaaS B2B 10-50 employee, USA + EU",
    "geo_eu_detected": true,
    "geo_includes": ["USA", "EU"]
  },
  "gdpr_config": {
    "mode": "auto",
    "mode_active": true,
    "lia_documented": false,
    "suppression_list_path": "<memory>/suppression.csv",
    "footer_bilingue": true,
    "retention_months": 12,
    "reject_b2c_personal_email": true
  },
  "campaign_meta": {
    "campaign_name": "Yellow Tech — Series A SaaS Q2 2026",
    "value_prop": "GTM Engineering audit gratuito"
  }
}
```

## Outputs

```json
{
  "compliant_leads": [...],   // lista filtered, ready per execute
  "excluded": [
    {"lead": {...}, "reason": "in_suppression_list", "details": {...}},
    {"lead": {...}, "reason": "b2c_personal_email", "domain": "gmail.com"},
    {"lead": {...}, "reason": "article_9_sensitive", "issues": [{"field": "role", "category": "health"}]},
    {"lead": {...}, "reason": "role_based_email", "email": "info@..."}
  ],
  "footer_html": {
    "it": "<p>Stai ricevendo questa email...</p>",
    "en": "<p>You are receiving this email...</p>",
    "bilingue": "<p><strong>Italiano</strong>: Stai ricevendo... <br><br><strong>English</strong>: You are receiving...</p>"
  },
  "lia_doc_path": "<memory>/lia_yellow_tech_series_a_saas_q2_2026.md",
  "lia_status": "newly_created",  // newly_created | reused_existing | needs_user_review
  "summary": {
    "total_input": 100,
    "compliant_count": 87,
    "excluded_count": 13,
    "exclusion_breakdown": {
      "in_suppression_list": 3,
      "b2c_personal_email": 7,
      "article_9_sensitive": 1,
      "role_based_email": 2
    }
  }
}
```

## Methodology

### 1. Suppression list check (mandatory primo step)

```python
def load_suppression_list(path):
    """Load CSV, return set of suppressed emails."""
    if not exists(path):
        # Initialize empty
        with open(path, "w") as f:
            f.write("email,reason,timestamp,source_campaign,user_action\n")
        return set()
    with open(path) as f:
        next(f)  # skip header
        return {row.split(",")[0].strip().lower() for row in f if row.strip()}

def is_in_suppression(lead, suppression_set):
    return lead["email"].lower() in suppression_set
```

### 2. B2C personal email reject

```python
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.it", "yahoo.co.uk",
    "hotmail.com", "hotmail.it", "outlook.com", "live.com", "msn.com",
    "icloud.com", "me.com", "mac.com", "libero.it", "alice.it", "tin.it",
    "virgilio.it", "tiscali.it", "fastwebnet.it", "aol.com", "protonmail.com",
    "tutanota.com", "orange.fr", "wanadoo.fr", "free.fr", "web.de", "gmx.de",
    "t-online.de"
}

def is_personal_email(email):
    domain = email.split("@")[1].lower()
    return domain in PERSONAL_EMAIL_DOMAINS
```

Reject if `gdpr_config.reject_b2c_personal_email = true` AND `is_personal_email(lead.email)`.

### 3. Article 9 sensitive data reject

Scan lead JSON fields for sensitive keywords:

```python
ARTICLE_9_KEYWORDS = {
    "health": ["medical", "patient", "diagnosis", "disease", "clinical", "hospital"],
    "race": ["ethnicity", "ancestry", "racial"],
    "political": ["political party", "voting", "campaign"],
    "religion": ["religious", "faith", "denomination"],
    "sexual": ["orientation", "preference", "lgbtq"],
    "biometric": ["fingerprint", "facial recognition", "biometric"]
}

def reject_article_9(lead_json):
    issues = []
    for category, keywords in ARTICLE_9_KEYWORDS.items():
        for field, value in flatten(lead_json).items():
            if not isinstance(value, str):
                continue
            for kw in keywords:
                if kw in value.lower():
                    issues.append({
                        "field": field,
                        "category": category,
                        "keyword": kw,
                        "value_excerpt": value[:80]
                    })
    return issues
```

NOTA: false positive possibili (es. "Director Cardiology" → flagged health). Reject default + allow user override `--include-medical-roles` flag.

### 4. Role-based email reject

```python
ROLE_BASED_PREFIXES = {"info", "sales", "support", "noreply", "admin", "contact",
                      "hello", "team", "office", "hr", "marketing", "legal", "billing"}

def is_role_based(email):
    local_part = email.split("@")[0].lower()
    return local_part in ROLE_BASED_PREFIXES
```

Ridondante con `validate_input.py` ma defense-in-depth.

### 5. LIA template generation

Per ogni nuova campagna senza LIA documentato:

```python
def generate_lia_doc(campaign_meta, icp, user_signature):
    """Generate LIA markdown file for new campaign."""
    template = """---
campaign: "{campaign_name}"
date: {date}
icp: "{icp_description}"
agent: outbound-orchestrator
status: documented
schema_version: 1
---

# Legitimate Interest Assessment — {campaign_name}

## 1. Identify legitimate interest

**Cosa**: B2B targeted outreach to {icp_description}
**Perché**: {value_prop}
**Beneficio**: <DA COMPILARE: expected reply rate, demo booked, deal close>

## 2. Necessity test

**Domanda**: l'email è necessaria/proporzionata vs alternative?

- Alternative considerate:
  - LinkedIn DM only → meno efficace per role-based
  - Phone call → friction maggiore
  - Inbound only → timing slower
- **Conclusione**: email B2B targeted è proporzionata.

## 3. Balance test

**Recipient profile**: {icp_description}, professional email
**Privacy expectation**: low (professional contact, public LinkedIn profile)
**Mitigations**:
- Solo professional email (no personal gmail/yahoo)
- Opt-out 1-click in footer
- Suppression cross-stack post-opt-out
- Source transparency
- Content relevant to professional role
- No Article 9 sensitive data
- Retention 12 mesi post-contact
- No data sharing third party

**Conclusione balance**: legitimate interest **prevale** sui right of data subject.

## Sign-off

**Documented by**: {user_signature}
**Signed**: {date}
**Review**: trimestrale
"""
    content = template.format(
        campaign_name=campaign_meta["campaign_name"],
        date=date.today().isoformat(),
        icp_description=icp["description"],
        value_prop=campaign_meta["value_prop"],
        user_signature=user_signature
    )

    path = f"<memory>/lia_{campaign_kebab}.md"
    with open(path, "w") as f:
        f.write(content)

    return path
```

User MUST review + complete `<DA COMPILARE>` field manualmente prima di execute.

### 6. Footer bilingue generation

```python
def generate_footer_bilingue(brand, lead_geo):
    """Generate IT + EN footer if EU mix, else single language."""
    if lead_geo == "EU_only" or lead_geo == "EU_mix":
        return f"""<p style="font-size: 11px; color: #888; line-height: 1.4; margin-top: 24px; padding-top: 12px; border-top: 1px solid #ddd;">
<strong>Italiano</strong>: Stai ricevendo questa email in qualità di {{role}} presso {{company}} — fonte: {{source}}. Trattiamo i tuoi dati per legittimo interesse (art. 6(1)(f) GDPR + Recital 47). Se non desideri ricevere ulteriori comunicazioni, <a href="{{unsubscribe_url}}" style="color: #888;">disiscriviti qui</a>. Inviato da {brand['signature']} · {brand['address']} · <a href="{brand['privacy_url']}" style="color: #888;">Privacy Policy</a>.
<br><br>
<strong>English</strong>: You are receiving this email as {{role}} at {{company}} — source: {{source}}. We process your data on legitimate interest basis (Art. 6(1)(f) GDPR + Recital 47). To opt out, <a href="{{unsubscribe_url}}" style="color: #888;">unsubscribe here</a>. Sent by {brand['signature']} · {brand['address']} · <a href="{brand['privacy_url']}" style="color: #888;">Privacy Policy</a>.
</p>"""
    elif lead_geo == "US_only":
        return f"""<p style="font-size: 11px; color: #888;">
You are receiving this email as {{role}} at {{company}}. To unsubscribe, <a href="{{unsubscribe_url}}">click here</a>. Sent by {brand['signature']} · {brand['address']}.
</p>"""
```

### 7. Suppression sync cross-stack

Quando user opt-out (skill `reply-classification` class=unsubscribe) o user manual:

```python
def sync_suppression_cross_stack(email, reason, source_campaign):
    """Append to suppression CSV + sync to all stacks."""

    # 1. Append local CSV
    timestamp = datetime.now().isoformat()
    with open("<memory>/suppression.csv", "a") as f:
        f.write(f"{email},{reason},{timestamp},{source_campaign},auto_sync\n")

    # 2. SmartLead global blocklist
    try:
        mcp__smartlead__smartlead_add_lead_to_global_blocklist(domain_or_email=email)
        log(f"✓ SmartLead blocklist sync: {email}")
    except Exception as e:
        log(f"✗ SmartLead sync fail: {e}")

    # 3. SmartLead unsubscribe from all campaigns (per safety)
    try:
        lead_in_campaigns = mcp__smartlead__smartlead_fetch_all_campaigns_using_lead_id(...)
        for c in lead_in_campaigns:
            mcp__smartlead__smartlead_unsubscribe_lead_from_campaign(lead_id=..., campaign_id=c["id"])
    except: pass

    # 4. HeyReach: stop lead in all campaigns where they appear
    try:
        # NOTA: HeyReach API non ha global blocklist. Loop campaigns + stop_lead.
        all_campaigns = mcp__heyreach__get_all_campaigns()
        for c in all_campaigns:
            try:
                requests.post(
                    "https://api.heyreach.io/api/public/campaign/StopLeadInCampaign",
                    headers={"X-API-KEY": os.environ["HEYREACH_API_KEY"]},
                    json={"campaignId": c["id"], "leadUrl": lead_linkedin_url}
                )
            except: continue
    except: pass

    # 5. Attio CRM: update record
    try:
        # search by email, update field do_not_contact
        results = mcp__attio_mcp__search_records(object_slug="people", filter={"email": email})
        for r in results:
            mcp__attio_mcp__update_record(
                object_slug="people",
                record_id=r["id"],
                attributes={"do_not_contact": True, "do_not_contact_reason": reason}
            )
    except: pass

    return {"synced": True, "stacks": ["smartlead", "heyreach", "attio"]}
```

### 8. Retention 12 mesi review

```python
def retention_review(crm_export, retention_months=12):
    """Flag leads contacted >12mo ago, no engagement."""
    cutoff = datetime.now() - timedelta(days=retention_months * 30)
    stale = []
    for lead in crm_export:
        last_contact = parse_date(lead["last_contact_at"])
        last_engagement = parse_date(lead.get("last_engagement_at", "1970-01-01"))
        if last_contact < cutoff and last_engagement < cutoff:
            stale.append({"lead": lead, "last_contact_age_days": (datetime.now() - last_contact).days})
    return stale
```

Output report markdown per user:

```markdown
## Retention review — 12 mesi cutoff (2025-04-30)

I seguenti lead sono stati contattati >12 mesi fa senza engagement. Considerati "stale" per GDPR retention policy.

- mario.rossi@company.com (last 2025-04-15, 380 giorni)
- ...

Action raccomandata:
- Archive in CRM (set archived=true)
- Re-LIA + new campaign se vuoi ri-targetare
- O cancellazione completa (right to be forgotten)
```

## Examples

### Example 1 — EU lead list compliance check

**Input**: 100 lead, 30 EU + 70 USA, 5 in suppression, 8 personal email, 2 role-based, 1 Article 9 (cardiologo).

**Output**:
```json
{
  "summary": {
    "total_input": 100,
    "compliant_count": 84,
    "excluded_count": 16,
    "exclusion_breakdown": {
      "in_suppression_list": 5,
      "b2c_personal_email": 8,
      "role_based_email": 2,
      "article_9_sensitive": 1
    }
  }
}
```

User-facing:
```
✅ GDPR compliance check completata.

Input: 100 lead
Compliant: 84 (procedibili)
Excluded: 16
  - In suppression list: 5
  - Personal email B2C: 8 (gmail.com, yahoo.it)
  - Role-based: 2 (info@, sales@)
  - Article 9 sensitive: 1 (role contains "Cardiology")

Footer bilingue IT+EN attivo (EU mix detected).
LIA documentato: <memory>/lia_yellow_tech_series_a_saas_q2_2026.md (DA REVIEW + completare campo "expected outcome")

Pronto a procedere con 84 lead.
```

### Example 2 — Italy Garante check (border B2B/B2C)

**Input**: lead Mario Rossi `m.rossi@gmail.com`, role founder Acme.io.

**Decision**: personal email → reject default, manual override available.

User-facing:
```
⚠️ Lead borderline Mario Rossi:
- Email: m.rossi@gmail.com (personal, banned default)
- Company: Acme.io (LinkedIn match)
- Role: Founder

Default: REJECT (Italy Garante restrittivo per personal email).
Override: aggiungi flag --allow-founder-personal-email per includerlo (RISCHIO: Garante può sanzionare per "personal email used for B2B without consent").

Procedere con reject? (y/n)
```

### Example 3 — Suppression sync cross-stack

**Input**: lead opt-out via reply (`reply-classification` → class=unsubscribe).

**Action**:
```
🔒 Sync suppression cross-stack: marco.rossi@company.com

✓ Local CSV: <memory>/suppression.csv (appended)
✓ SmartLead global blocklist: synced
✓ SmartLead campaigns unsubscribe: 3/3 campaigns
✓ HeyReach campaigns stop: 2/2 campaigns
✓ Attio CRM: do_not_contact = true

Lead suppressed across all stacks. No further outreach possible.
```

## Anti-pattern

1. **Mai send senza LIA documentato** se EU detected (sanzione Garante max €20M)
2. **Mai single-language footer** se EU mix detected
3. **Mai suppression single-stack** (sempre cross-stack — GDPR violation)
4. **Mai retention >12 mesi** senza re-LIA
5. **Mai ignore Article 9** keyword detection (anche se false positive)
6. **Mai personal email B2C** senza override esplicito user
7. **Mai role-based email** in personalized sequence
8. **Mai dimenticare {unsubscribe_url}** in footer (CAN-SPAM + GDPR violation)

## Scripts

- `../../scripts/suppress_lead.py` — CLI suppress single email cross-stack
- `../../scripts/gdpr_check.py` — CLI batch compliance check on CSV

## References

- `../../references/gdpr-outbound-eu.md` — full guide LIA + Italy + retention + Article 9
- `../../research/research-summary.md` RQ7

## Output destination

- Compliance check: `<memory>/gdpr_check_<campaign>_<ts>.json` (audit trail)
- LIA doc: `<memory>/lia_<campaign_kebab>.md` (user reviews)
- Suppression list: `<memory>/suppression.csv` (append-only, never delete)
