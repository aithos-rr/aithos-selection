---
name: reply-classification
description: 5-class auto-classification reply email cold outbound (positive/negative/OOO/unsubscribe/bounce) hybrid rule-based + LLM fallback. Action per class: pause/forward/snooze/suppress. Integrazione SmartLead webhook `LEAD_REPLIED`. Per `/outbound-orchestrator` skill companion. Threshold confidence 0.85, manual triage queue per ambigui.
when_to_use: Webhook handler SmartLead reply, manual triage reply ambigui, batch classification reply storiche, audit reply handling quality, retraining se accuracy <90%
---

# Reply Classification

Auto-classifica reply email cold outbound in 5 classi: positive, negative, OOO, unsubscribe, bounce. Hybrid rule-based (70-80% case ovvi) + LLM fallback (ambigui). Action automatica per ogni classe.

**Lingua**: italiano user-facing. Inglese per nomi tecnici (positive, OOO, ecc.).

## When to use

Attiva quando:
- Webhook handler SmartLead `LEAD_REPLIED` event
- Manual triage di reply ambigua flagged in queue
- Batch classification reply storiche (audit campagna chiusa)
- Audit accuracy classifier (sample 50 reply random, hand-label, compare)
- Retraining rule-based regex se accuracy degrada

**Non attivare** se:
- Reply è da self/teammate (test) — skip
- Reply > 30 giorni dalla send (stale) — manual triage
- DSN bounce header presente — direct route a `bounce` (skip LLM)

## Prerequisites

- Reply content (testo email + headers se DSN)
- Lead context (sequence step, signal_used, campaign_id)
- LLM access (Claude Sonnet via Claude Code)
- Reference `references/outbound-best-practices-2026.md` sezione reply handling

## Inputs

```json
{
  "reply": {
    "from_email": "marco.rossi@company.com",
    "subject": "Re: Domanda su Acme",
    "body": "Ciao, grazie per il messaggio. Sono interessato — possiamo schedulare una call mercoledì alle 15?",
    "headers": {
      "Date": "2026-05-02T10:30:00Z",
      "Message-ID": "...",
      "References": "..."
    }
  },
  "lead_context": {
    "lead_id": "uuid",
    "campaign_id": 12345,
    "sequence_step": 1,
    "signal_used": "job_change"
  }
}
```

## Outputs

```json
{
  "class": "positive",
  "confidence": 0.94,
  "method": "rule_based",  // or "llm_fallback"
  "action": "pause_sequence_and_forward",
  "snooze_until": null,
  "manual_triage": false,
  "smartlead_category": "Interested",
  "details": {
    "matched_keywords": ["interessato", "schedulare", "call"],
    "sentiment": "positive",
    "intent_detected": "meeting_request"
  },
  "_meta": {
    "classified_at": "2026-05-02T10:35:00Z",
    "model": "rule_based_v1"
  }
}
```

## Methodology

### 1. Rule-based pre-filter (catch 70-80% case ovvi)

#### Bounce detection (DSN headers)

```python
DSN_HEADERS = ["X-Failed-Recipients", "Diagnostic-Code", "Status: 5."]
DSN_PATTERNS = [r"550\s", r"5\.\d\.\d", r"recipient.*not\s*found", r"mailbox.*full", r"address.*does\s*not\s*exist"]

def is_bounce(reply):
    for header in DSN_HEADERS:
        if header in reply.get("headers", {}):
            return True
    for pattern in DSN_PATTERNS:
        if re.search(pattern, reply["body"], re.IGNORECASE):
            return True
    return False
```

If bounce → `class=bounce`, `action=suppress_hard`, skip LLM.

#### Out-of-Office detection

```python
OOO_KEYWORDS_IT = ["fuori ufficio", "in vacanza", "in ferie", "rientro il", "tornerò il"]
OOO_KEYWORDS_EN = ["out of office", "ooo", "vacation", "annual leave", "returning on", "be back on"]

def is_ooo(reply):
    body_lower = reply["body"].lower()
    if any(kw in body_lower for kw in OOO_KEYWORDS_IT + OOO_KEYWORDS_EN):
        return True
    return False
```

If OOO → `class=OOO`, extract return date if possible, `action=snooze_until_return`.

#### Unsubscribe explicit

```python
UNSUBSCRIBE_KEYWORDS_IT = ["disiscrivimi", "rimuovere", "non scrivere", "non più", "smetti"]
UNSUBSCRIBE_KEYWORDS_EN = ["unsubscribe", "remove me", "stop sending", "do not contact", "take me off"]

def is_unsubscribe(reply):
    body_lower = reply["body"].lower()
    if any(kw in body_lower for kw in UNSUBSCRIBE_KEYWORDS_IT + UNSUBSCRIBE_KEYWORDS_EN):
        return True
    return False
```

If unsubscribe → `class=unsubscribe`, `action=suppress_cross_stack`.

#### Negative explicit

```python
NEGATIVE_KEYWORDS_IT = ["non interessa", "non interessato", "abbiamo già", "non è il momento", "no grazie"]
NEGATIVE_KEYWORDS_EN = ["not interested", "we have", "no thanks", "wrong person", "not now", "pass"]

def is_negative(reply):
    body_lower = reply["body"].lower()
    matches = sum(1 for kw in NEGATIVE_KEYWORDS_IT + NEGATIVE_KEYWORDS_EN if kw in body_lower)
    return matches >= 1, matches
```

If negative match → `class=negative`, confidence based on match count.

#### Positive explicit

```python
POSITIVE_KEYWORDS_IT = ["interessato", "interessante", "schedulare", "call", "demo", "incontriamoci", "calendly"]
POSITIVE_KEYWORDS_EN = ["interested", "schedule", "demo", "meeting", "call", "calendly", "let's chat"]
POSITIVE_PHRASES = ["yes please", "sounds good", "tell me more", "let's set up"]

def is_positive(reply):
    body_lower = reply["body"].lower()
    matches = sum(1 for kw in POSITIVE_KEYWORDS_IT + POSITIVE_KEYWORDS_EN if kw in body_lower)
    matches += sum(1 for p in POSITIVE_PHRASES if p in body_lower)
    return matches >= 2, matches  # need 2+ for confidence
```

### 2. LLM fallback (ambigui)

Se rule-based confidence <0.85 OR no rule matched, escalate to LLM:

System prompt:

```
Sei un classificatore di reply email cold outbound. Classifica la reply in UNA delle 5 classi:

- positive: lead esprime interesse, vuole demo/meeting, chiede info per buying intent
- negative: lead esplicitamente rifiuta, "not interested", "wrong fit", "we have a vendor"
- OOO: out-of-office auto-reply, vacanza, ferie, rientro a data
- unsubscribe: lead chiede explicit di non essere più contattato
- bounce: delivery failure (probabilmente già detected da DSN, ma verifica)

Output JSON:
{
  "class": "positive|negative|OOO|unsubscribe|bounce",
  "confidence": 0.0-1.0,
  "intent_detected": "string",
  "reasoning": "1-2 sentences"
}
```

User prompt:

```
Reply email:
From: <from_email>
Subject: <subject>
Body: <body>

Lead context:
Sequence step: <N>
Signal used: <signal_type>

Classifica.
```

LLM output parse JSON. Confidence threshold 0.85.

### 3. Manual triage queue

Se confidence final <0.85 (rule-based + LLM both ambiguous):

```python
def add_to_triage_queue(reply, classification):
    triage_path = "<memory>/triage_queue.md"
    with open(triage_path, "a") as f:
        f.write(f"""
## {datetime.now().isoformat()} — {reply['from_email']}

**Subject**: {reply['subject']}
**Body excerpt**: {reply['body'][:200]}...
**Auto-classification**: {classification['class']} (conf {classification['confidence']:.2f})
**Reasoning**: {classification['details']['reasoning']}

**Action richiesta**: review e reclassify manualmente.

---
""")
    return triage_path
```

User reviews queue manually periodically.

### 4. Action mapping

```python
ACTION_MAPPING = {
    "positive": {
        "smartlead_category": "Interested",
        "smartlead_action": "pause_lead",
        "forward": True,
        "suppress": False,
        "cross_stack": False
    },
    "negative": {
        "smartlead_category": "Not-Interested",
        "smartlead_action": "pause_lead",
        "forward": False,
        "suppress": "this_campaign_only",
        "cross_stack": False
    },
    "OOO": {
        "smartlead_category": "Out-of-Office",
        "smartlead_action": "snooze",
        "forward": False,
        "suppress": False,
        "snooze_days": 10,  # extracted from body if possible, default 10
        "cross_stack": False
    },
    "unsubscribe": {
        "smartlead_category": "Do-Not-Contact",
        "smartlead_action": "unsubscribe_all_campaigns",
        "forward": False,
        "suppress": True,
        "cross_stack": True  # MANDATORY GDPR
    },
    "bounce": {
        "smartlead_category": "Hard-Bounce",
        "smartlead_action": "suppress",
        "forward": False,
        "suppress": True,
        "cross_stack": True  # always suppress hard bounces
    }
}
```

### 5. Execute action

```python
def execute_action(classification, lead_context):
    action_def = ACTION_MAPPING[classification["class"]]

    # 1. Update SmartLead lead category
    mcp__smartlead__smartlead_update_lead_category(
        lead_id=lead_context["lead_id"],
        campaign_id=lead_context["campaign_id"],
        category=action_def["smartlead_category"]
    )

    # 2. Pause/snooze/unsubscribe via SmartLead API
    if action_def["smartlead_action"] == "pause_lead":
        mcp__smartlead__smartlead_pause_lead_by_campaign(...)
    elif action_def["smartlead_action"] == "unsubscribe_all_campaigns":
        mcp__smartlead__smartlead_unsubscribe_lead_from_all_campaigns(lead_id=...)

    # 3. Cross-stack suppress (if needed)
    if action_def["cross_stack"]:
        append_to_suppression_list(lead.email, reason=classification["class"])
        # HeyReach: stop_lead_in_campaign for active campaigns

    # 4. Forward positive reply (if needed)
    if action_def["forward"]:
        mcp__claude_ai_Gmail__create_draft(
            to=USER_INBOX,
            subject=f"[Outbound positive reply] {lead_context['lead_email']}",
            body=format_forward(reply, lead_context)
        )
```

### 6. OOO snooze date extraction

```python
def extract_return_date(ooo_body):
    """Try to extract return date from OOO body."""
    patterns = [
        r"return(?:ing|s)?\s+(?:on\s+)?(\d{1,2}[\/\-\s][a-zA-Z]+(?:\s+\d{2,4})?)",
        r"back\s+(?:on\s+)?(\d{1,2}[\/\-\s][a-zA-Z]+)",
        r"rientro(?:\s+il)?\s+(\d{1,2}[\/\-\s][a-zA-Z]+)",
        r"tornerò\s+(?:il\s+)?(\d{1,2}[\/\-\s][a-zA-Z]+)"
    ]
    for p in patterns:
        match = re.search(p, ooo_body, re.IGNORECASE)
        if match:
            try:
                return parse_date(match.group(1))
            except:
                continue
    return datetime.now() + timedelta(days=10)  # fallback default 10d
```

## Examples

### Example 1 — Positive reply (rule-based catch)

**Input**:
```
"Ciao Filippo, grazie per il messaggio! Sono molto interessato. Possiamo schedulare una call mercoledì alle 15?"
```

**Output**:
```json
{
  "class": "positive",
  "confidence": 0.96,
  "method": "rule_based",
  "action": "pause_sequence_and_forward",
  "smartlead_category": "Interested",
  "details": {
    "matched_keywords": ["interessato", "schedulare", "call"],
    "intent_detected": "meeting_request"
  }
}
```

### Example 2 — OOO with return date (rule-based + extraction)

**Input**:
```
"Sono in ferie fino al 15 maggio. Per urgenze contattare giulia@company.com."
```

**Output**:
```json
{
  "class": "OOO",
  "confidence": 0.93,
  "method": "rule_based",
  "action": "snooze",
  "snooze_until": "2026-05-15",
  "smartlead_category": "Out-of-Office",
  "details": {
    "return_date_extracted": "2026-05-15",
    "alternate_contact": "giulia@company.com"
  }
}
```

Bonus action: log alternate contact in lead notes for future reference.

### Example 3 — Ambiguous reply (LLM fallback)

**Input**:
```
"Non sono la persona giusta per questa cosa. Te lo ridirigo a Luca."
```

**Output**:
```json
{
  "class": "negative",
  "confidence": 0.78,  // borderline
  "method": "llm_fallback",
  "action": "pause_lead",
  "smartlead_category": "Wrong-Person",
  "details": {
    "reasoning": "Wrong person, redirect indicated. Treated as negative for current lead, manual review for redirect target.",
    "manual_triage_recommended": true
  },
  "manual_triage": true  // flagged for user review
}
```

User-facing alert:
```
⚠️ Reply ambigua flagged per manual review:
Lead: marco.rossi@company.com
Auto-class: negative (wrong person), conf 0.78
Reply: "Non sono la persona giusta... Te lo ridirigo a Luca."
Action presa: pause lead.
Manual review: aggiungi Luca come nuovo lead in /lead-finder-pro?
```

### Example 4 — Hard bounce (DSN auto-detect)

**Input**:
```
Headers: X-Failed-Recipients: marco@invalid-domain.xyz
Body: "550 5.1.1 Recipient address rejected: User unknown"
```

**Output**:
```json
{
  "class": "bounce",
  "confidence": 1.0,
  "method": "rule_based_dsn",
  "action": "suppress_hard",
  "smartlead_category": "Hard-Bounce",
  "details": {
    "bounce_type": "user_unknown",
    "smtp_code": "550 5.1.1"
  }
}
```

## Anti-pattern

1. **Mai skip rule-based pre-filter** (LLM costoso + slow per case ovvi)
2. **Mai accept LLM confidence <0.85** senza manual triage queue
3. **Mai forward negative/unsubscribe** a user (rumore inbox)
4. **Mai unsubscribe single-campaign** (sempre cross-stack se class=unsubscribe — GDPR)
5. **Mai bounce soft retry >3 volte** (fail permanent dopo 3, suppress)
6. **Mai assumere OOO snooze 10d** se return date estratto disponibile
7. **Mai update SmartLead category** se manual_triage=true (let user decide)
8. **Mai class=bounce** senza DSN headers/SMTP code (could be fake reply)

## Scripts

- `../../scripts/reply_classify.py` — CLI wrapper rule-based + LLM hybrid

## References

- `../../references/outbound-best-practices-2026.md` sezione reply handling
- `../../research/research-summary.md` RQ6

## Output destination

- Webhook handler: append `<memory>/replies_log.jsonl` (audit trail)
- Manual triage: `<memory>/triage_queue.md` (user reviews)
- Suppression sync: append `<memory>/suppression.csv` (cross-stack ref `gdpr-opt-out` skill)
