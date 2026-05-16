---
name: deliverability-check
description: Pre-flight check email deliverability prima di bulk send. DKIM/DMARC/SPF DNS query + warmup status + daily cap remaining (matrix age-aware) + blacklist scan + spam-trigger word check + Postmaster Tools spam rate. Gate mandatory in `/outbound-orchestrator` Fase 2 methodology. BLOCK se issue critico, warning se issue minore.
when_to_use: Pre-flight check prima invio bulk SmartLead/HeyReach, audit setup nuovo dominio, check warmup status, troubleshooting reputation drop, weekly review reputation
---

# Deliverability Check

Pre-flight check email deliverability — gate mandatory prima di ogni invio bulk via `/outbound-orchestrator`. BLOCK se issue critico, warning se minore.

**Lingua**: italiano user-facing, inglese tecnico (DKIM, SPF, DMARC).

## When to use

Attiva quando:
- Pre-flight check Fase 2 metodologia `/outbound-orchestrator` (mandatory gate)
- Audit setup nuovo dominio (post-warmup ramp-up)
- Weekly review reputation (proactive monitoring)
- Troubleshooting reputation drop (reactive)
- Onboarding nuovo cliente (audit current setup)

**Non attivare** se:
- Solo dry-run (no real send) — skip check, proceed simulation
- Single test send (1 mailbox a self) — skip warmup gate
- Già checkato in last 24h (cache hit, leggi `<memory>/deliverability_cache.json`)

## Prerequisites

- Domain mittente noto (config `brand.signature_domain`)
- Mailbox sender list (config `stack.mailbox_accounts` — array di email)
- API access SmartLead (per `get_warmup_stats_by_email_account_id`)
- DNS resolver disponibile (default OS)
- Reference `references/deliverability-2026.md`

## Inputs

```json
{
  "sender_domain": "yourdomain.com",
  "mailbox_accounts": [
    {"email": "you@yourdomain.com", "smartlead_id": 12345}
  ],
  "lead_list_size": 100,
  "scheduled_send_time": "2026-05-01T09:00:00Z",
  "send_window": "tue_thu_9_13",
  "config": {
    "warmup_days_minimum": 14,
    "spam_rate_threshold": 0.3,
    "daily_cap_per_mailbox": {
      "cold_0_14d": 5,
      "warmed_30_90d": 50,
      "seasoned_6mo_plus": 250
    },
    "blacklist_scan": true
  }
}
```

## Outputs

```json
{
  "ready": false,
  "issues": [
    {
      "severity": "critical",
      "check": "dmarc_policy",
      "status": "p=none",
      "description": "DMARC policy is 'none', mailbox providers won't enforce auth",
      "recommendation": "Update DMARC record to p=quarantine or p=reject before sending. See references/deliverability-2026.md"
    },
    {
      "severity": "critical",
      "check": "mailbox_age",
      "status": "8 days",
      "mailbox": "you@yourdomain.com",
      "description": "Mailbox <14 days warmup",
      "recommendation": "Continue warmup tool only for 6+ more days before bulk send"
    }
  ],
  "warnings": [
    {
      "severity": "warning",
      "check": "bimi_record",
      "status": "absent",
      "description": "BIMI not configured (optional, +5-10% open rate)",
      "recommendation": "Optional. Setup BIMI if budget for VMC certificate ($1500/yr)"
    }
  ],
  "daily_cap_remaining": {
    "you@yourdomain.com": 0
  },
  "mailbox_age_days": {
    "you@yourdomain.com": 8
  },
  "dns_status": {
    "spf": {"present": true, "policy": "-all", "lookups": 7},
    "dkim": {"present": true, "selector": "smartlead", "key_length": 2048},
    "dmarc": {"present": true, "policy": "none", "alignment": "relaxed"},
    "bimi": {"present": false}
  },
  "blacklist_scan": {
    "spamhaus": "clean",
    "spamcop": "clean",
    "barracuda": "clean",
    "sorbs": "clean",
    "surbl": "clean"
  },
  "_meta": {
    "checked_at": "2026-04-30T11:00:00Z",
    "cache_valid_until": "2026-05-01T11:00:00Z"
  }
}
```

## Methodology

### 1. DNS query SPF/DKIM/DMARC/BIMI

```python
import dns.resolver

def check_spf(domain):
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt = b"".join(rdata.strings).decode()
            if txt.startswith("v=spf1"):
                policy = "hard_fail" if "-all" in txt else "soft_fail" if "~all" in txt else "neutral"
                return {"present": True, "policy": policy, "raw": txt}
        return {"present": False}
    except Exception as e:
        return {"present": False, "error": str(e)}

def check_dmarc(domain):
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        for rdata in answers:
            txt = b"".join(rdata.strings).decode()
            if txt.startswith("v=DMARC1"):
                policy = parse_dmarc_p(txt)  # "none" | "quarantine" | "reject"
                return {"present": True, "policy": policy, "raw": txt}
        return {"present": False}
    except Exception:
        return {"present": False}
```

DMARC policy threshold:
- `p=none` → critical issue, BLOCK
- `p=quarantine` → ok, proceed
- `p=reject` → ideal, proceed

### 2. Mailbox age check

Via SmartLead API:

```python
warmup_stats = mcp__smartlead__smartlead_get_warmup_stats_by_email_account_id(
    email_account_id=mailbox["smartlead_id"]
)
warmup_days = warmup_stats.get("warmup_active_days", 0)
```

Gate logic:
- `warmup_days < 14` → BLOCK bulk (critical issue)
- `14 <= warmup_days < 30` → WARNING + lower daily cap (15)
- `30+` → OK, daily cap matrix applies (DECISION-008)

### 3. Daily cap remaining

```python
today = date.today().isoformat()
sent_today = get_sent_count_today(mailbox, smartlead_api)
mailbox_age_band = age_to_band(warmup_days)  # cold | warming | warmed | aged | seasoned
daily_cap = config["daily_cap_per_mailbox"][mailbox_age_band]
remaining = max(0, daily_cap - sent_today)
```

Se `lead_list_size > sum(daily_cap_remaining for all mailboxes)` → WARNING "lista esuberante daily cap, scaglionare in più giorni".

### 4. Blacklist scan (RBL)

```python
def check_rbl(domain_ip):
    """Reverse DNS query against major RBL."""
    rbls = ["zen.spamhaus.org", "bl.spamcop.net", "b.barracudacentral.org",
            "dnsbl.sorbs.net", "multi.surbl.org"]
    results = {}
    for rbl in rbls:
        try:
            reversed_ip = ".".join(reversed(domain_ip.split(".")))
            dns.resolver.resolve(f"{reversed_ip}.{rbl}", "A")
            results[rbl] = "listed"  # found = blacklisted
        except dns.resolver.NXDOMAIN:
            results[rbl] = "clean"
        except Exception as e:
            results[rbl] = f"error: {str(e)[:50]}"
    return results
```

Se any `listed` → CRITICAL ISSUE, BLOCK + recommendation "delist via provider".

### 5. Postmaster Tools spam rate (manual)

Postmaster Tools richiedono OAuth + interactive setup. Skip auto-check, ma prompt user:

```
⚠️ Verifica manualmente Gmail Postmaster Tools (https://postmaster.google.com):
- Spam rate: deve essere <0.3% (target <0.1%)
- IP reputation: High raccomandato
- Domain reputation: High raccomandato

Hai checkato? (y/n)
```

Se user "n" → soft warning (no block).

### 6. Spam-trigger word check

Sample sequence body content, scan for spam triggers:

```python
SPAM_TRIGGERS = {
    "high": ["FREE", "URGENT", "ACT NOW", "100% guaranteed", "RISK-FREE"],
    "medium": ["limited time", "bonus", "click here", "buy now", "save up to"],
    "low": ["winner", "selected", "congratulations", "exclusive offer"]
}

def scan_template(template_text):
    issues = []
    text_upper = template_text.upper()
    for severity, words in SPAM_TRIGGERS.items():
        for word in words:
            if word.upper() in text_upper:
                issues.append({"severity": severity, "trigger": word, "context_excerpt": "..."})
    return issues
```

If `high` triggers found → WARNING (not block, may be intentional).

### 7. Unsubscribe link check

Mandatory CAN-SPAM + GDPR. Scan template:

```python
def has_unsubscribe(template_text):
    return bool(re.search(r'\{unsubscribe_url\}|\{\{unsubscribe\}\}|unsubscribe', template_text, re.IGNORECASE))
```

If missing → CRITICAL ISSUE, BLOCK.

### 8. Identity sender check (CAN-SPAM)

Scan footer for physical address:

```python
def has_physical_address(footer_text):
    """Check footer has at least street/PO Box + city."""
    address_patterns = [r"\b\d+\s+[A-Z][a-zA-Z]+\s+(Street|St|Road|Rd|Via|Viale)",
                       r"P\.O\.\s*Box\s+\d+", r"PO Box \d+"]
    return any(re.search(p, footer_text) for p in address_patterns)
```

If missing → WARNING.

## Examples

### Example 1 — Mailbox warmup <14d (BLOCK)

**Input**: 100 lead, mailbox `you@yourdomain.com` 8d age.

**Output** (truncated):
```json
{
  "ready": false,
  "issues": [
    {"severity": "critical", "check": "mailbox_age", "status": "8 days", "recommendation": "..."}
  ]
}
```

User-facing message:
```
❌ Pre-flight check FAILED. Issue critico:

🛑 Mailbox warmup insufficient: you@yourdomain.com è in warmup da 8 giorni, minimum 14d.

Cosa fare:
1. Continua warmup tool (Smartsenders/Lemwarm) per altri 6 giorni
2. Re-run check fra 6 giorni
3. Override forzato: --force-no-warmup-check (NON raccomandato — reputation risk)

Suggerimento: schedule lancio campagna per 2026-05-07 (post-warmup).
```

### Example 2 — Tutto OK (ready=true)

**Input**: 50 lead, mailbox warmed 45d, DMARC `p=quarantine`, all RBL clean.

**Output** (truncated):
```json
{
  "ready": true,
  "issues": [],
  "warnings": [{"check": "bimi_record", "status": "absent", ...}],
  "daily_cap_remaining": {"you@yourdomain.com": 35}
}
```

User-facing:
```
✅ Pre-flight check PASSED.

Setup verified:
✓ SPF: -all (hard fail)
✓ DKIM: smartlead selector, RSA 2048
✓ DMARC: p=quarantine
✓ Mailbox warmup: 45 giorni
✓ Daily cap remaining: 35/50
✓ Blacklist scan: clean (5/5 RBL)

Warning minore:
⚠️ BIMI: assente (opzionale, +5-10% open rate). Setup VMC se budget.

Pronto a procedere con 50 lead.
```

### Example 3 — Blacklist hit (BLOCK)

**Input**: 100 lead, dominio listed Spamhaus SBL.

**Output**:
```json
{
  "ready": false,
  "issues": [
    {"severity": "critical", "check": "blacklist_spamhaus", "status": "listed_sbl", "recommendation": "Delist via Spamhaus removal portal: https://www.spamhaus.org/lookup/"}
  ]
}
```

User-facing:
```
🛑 Pre-flight check FAILED. CRITICAL: Domain blacklisted.

Spamhaus SBL ha listato yourdomain.com.
Causa probabile: spam complaint spike o list hygiene fail recente.

Cosa fare:
1. NON inviare bulk fino a delisting
2. Identifica root cause (volume spike, content issue, list quality)
3. Fix issue (warmup, list cleaning, content review)
4. Submit delisting request: https://www.spamhaus.org/lookup/
5. Wait 24-72h, re-check

Recovery time stimato: 7-14 giorni.
```

## Cache strategy

Per evitare DNS query spam su run successivi:

```python
def get_cached_check(domain):
    cache_path = "<memory>/deliverability_cache.json"
    if exists(cache_path):
        cache = json.load(open(cache_path))
        if cache.get("domain") == domain and \
           datetime.fromisoformat(cache["valid_until"]) > datetime.now():
            return cache
    return None
```

Cache validità: 24h (DNS records cambiano poco).

## Anti-pattern

1. **Mai bypass warmup gate** senza warning utente esplicito
2. **Mai send se DMARC `p=none`** (ignora policy = inbox spam)
3. **Mai send se domain blacklisted** (reputation tank irreversibile)
4. **Mai assumere mailbox warmed** senza check (DECISION-008 matrix)
5. **Mai skip unsubscribe link check** (CAN-SPAM + GDPR violation)
6. **Mai cache >24h** (DNS records evolve)
7. **Mai check senza domain config** (errore silent)
8. **Mai trust user-claimed warmup** (always API check)

## Scripts

- `../../scripts/deliverability_precheck.py` — CLI wrapper DNS + RBL + warmup query

## References

- `../../references/deliverability-2026.md` — full SPF/DKIM/DMARC/BIMI guide + warmup table + Postmaster threshold
- `../../research/research-summary.md` RQ4

## Output destination

`<memory>/deliverability_check_<domain>_<ts>.json` (audit trail) + cache 24h.
