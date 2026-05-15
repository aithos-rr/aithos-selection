---
name: email-verification
description: Verifica email waterfall multi-tier — Hunter MCP (primary, ha MCP nativo) → Apollo API (fallback) → manual SMTP (last resort). Detecta catch-all, role-based, disposable, gibberish. Soglia confidence ≥0.80 per attivare email in sequence outbound. Costo per verifica e cap configurabile. Da usare prima di OGNI invio outbound, audit email lista CRM, batch verification post-enrichment.
when_to_use: Email da verificare prima di sequence outbound, audit qualità email lista esistente CRM, output skill waterfall-enrichment da validare, single email check ad-hoc, batch verification 50-500 email, dubbio su email "info@" o catch-all
allowed-tools: Read Bash(python:*) Bash(curl:*)
---

# Email Verification

Trasforma email "raw" (da scraping, enrichment, lista import) in email "safe to send" via waterfall verifier multi-tier. Soglia 0.80 confidence prima di attivare in sequence.

## When to use

Attivare quando:

- Email batch da inserire in sequence outbound (mandatory pre-send)
- Audit lista email CRM esistente (pre-campaign)
- Single email check ad-hoc (mid-conversation: "questa email è valida?")
- Output enrichment waterfall da validare prima di scoring
- Re-verification email lead vecchi (>90 giorni) prima di re-engagement

Non attivare se:

- Email già verificata <30 giorni (cache hit)
- Email è chiaramente role-based `info@`, `sales@`, `support@` e già taggata
- Già confirmed bounce in suppression list

## Prerequisiti

- Hunter MCP server registrato OPPURE Hunter API key in env `HUNTER_API_KEY`
- (Optional) Apollo API key in env `APOLLO_API_KEY` per Tier 2 fallback
- Reference `references/tool-integrations.md` per MCP usage

## Instructions

### Fase 1 — Detect Hunter availability

Check via `mcp_detect.py`:

```bash
python scripts/mcp_detect.py --check hunter
```

Se `hunter.available: true` → tier 1 = Hunter MCP. Altrimenti → tier 1 = Hunter REST API V2 via `email_verify_waterfall.py --hunter-key $HUNTER_API_KEY`.

### Fase 2 — Pre-validation (cheap checks first)

Per ogni email, esegui in ordine:

1. **Syntax check** (regex base): `^[\w.+-]+@[\w-]+\.[\w.-]+$` → reject se fail (cost 0)
2. **Domain blacklist** check: lista in `<memory>/email_blocklist.md` (es. `tempmail.org`, `mailinator.com`) → reject se match
3. **Role-based detection**: prefix `info@`, `sales@`, `support@`, `admin@`, `noreply@`, `no-reply@`, `team@`, `hello@`, `contact@` → flag `role: true`, exclude da personalized

### Fase 3 — Tier 1: Hunter (MCP or REST)

Per ogni email passata syntax+blacklist+role check:

```bash
# Via Hunter MCP (preferito)
hunter.email_verifier(email="mario@acme.com")

# OPPURE via REST V2
curl "https://api.hunter.io/v2/email-verifier?email=mario@acme.com&api_key=$HUNTER_API_KEY"
```

**Parse response**:

- `data.status` = `valid` | `invalid` | `accept_all` | `webmail` | `disposable` | `unknown`
- `data.score` = 0-100 confidence
- `data.smtp_check` = bool
- `data.mx_records` = bool
- `data.disposable` = bool
- `data.role` = bool
- `data.regexp` = bool
- `data.result` = `deliverable` | `undeliverable` | `risky`

**Decision logic**:

- `status: valid + score ≥80` → ACCEPT (verified=true)
- `status: accept_all + score ≥80` → ACCEPT con flag `catch_all_warning`
- `status: accept_all + score <80` → SKIP, suggesti Tier 2
- `status: webmail` → ACCEPT con flag `personal_email_warning` (gmail/yahoo/etc., low priority B2B)
- `status: disposable` → REJECT
- `status: invalid` → REJECT (segnale per `_conflicts` se altro provider dice valid)
- `status: unknown` → escalate Tier 2

### Fase 4 — Tier 2: Apollo enrichment fallback

Solo se Tier 1 = `unknown` o `accept_all <0.80`.

```bash
python scripts/email_verify_waterfall.py --email "mario@acme.com" --tier 2 --apollo-key $APOLLO_API_KEY
```

Apollo `people/match` restituisce `email_status: verified | unverified`. Soglia confidence Apollo: `verified` only.

NB: Apollo bounce 15-25% reportato — il `verified` di Apollo NON è equivalente a Hunter `valid + score ≥80`. Quindi se Tier 1 dice `invalid`, Tier 2 dice `verified` → flag `_conflicts` (DECISION-009).

### Fase 5 — Tier 3: Manual SMTP (last resort)

Solo se opt-in via flag `--enable-smtp` (default false). Connessione `smtplib` per `MAIL FROM` + `RCPT TO` simulato:

```bash
python scripts/email_verify_waterfall.py --email "mario@acme.com" --tier 3 --enable-smtp
```

NB: molti server bloccano questa pratica (anti-harvesting). Use solo per debug, non bulk.

### Fase 6 — Output JSON

Per ogni email:

```json
{
  "email": "mario@acme.com",
  "verified": true,
  "confidence": 0.92,
  "method": "hunter_mcp",
  "tier_used": 1,
  "flags": ["webmail_warning"],
  "raw_response": {...},
  "verified_at": "2026-04-30T08:30:00Z"
}
```

### Fase 7 — Cache + report

- Cache result 30 giorni in `<memory>/email_verify_cache/<hash>.json`
- Report finale: total checked, valid, accept_all, disposable, invalid, unknown, role-based skipped
- Costo stimato: `total_credits_used` (Hunter 1 credit/check, Apollo idem)

## Examples

### Esempio 1 — Batch 200 email post-enrichment

**Input**: lista 200 email da skill `waterfall-enrichment`.

**Workflow**:

1. Pre-validation → 18 role-based excluded, 2 syntax invalid → 180 ready
2. Tier 1 Hunter → 145 valid+0.80+, 12 accept_all+0.80+, 8 disposable, 5 unknown, 10 invalid
3. Tier 2 Apollo (su 5 unknown) → 3 verified, 2 still unknown
4. **Result**: 160 verified-safe-to-send, 20 reject/skip, 18 role-flagged
5. Cost: 180 Hunter credits + 5 Apollo credits = $1.85 (stima)

### Esempio 2 — Catch-all dubbioso

**Input**: `mario@bigcorp.com` (BigCorp ha catch-all server)

**Tier 1 Hunter**:

- `status: accept_all`
- `score: 65` (sotto threshold 80)

**Action**: skip + flag `catch_all_low_confidence`. Suggerimento utente: "BigCorp domain accept-all, confidence basso. Suggerisco verifica via LinkedIn URL diretto + outreach DM invece di email."

### Esempio 3 — Conflict tra provider

**Input**: `sara@nimbus.io`

- Hunter: `invalid` (score 30, no SMTP response)
- Apollo: `verified`

**Action**: flag `_conflicts: [{field: 'email', providers: ['hunter', 'apollo'], values: ['invalid', 'verified']}]`. Mark `needs_review: true`. NO auto-pick first (DECISION-009 conflict policy). Subagent suggerisce: "Conflict trovato. Verifica manualmente: prova LinkedIn DM a Sara, se risponde da business email confirma quale è giusta."

## Gotchas

- 🔴 **NON fidarti di `email_status: verified` di Apollo**: bounce 15-25%. Hunter è il primary verifier (DECISION-005). Apollo solo come signal incrociato.
- 🔴 **Catch-all false positive**: server "accept-all" restituisce `valid` per email inesistenti. Solo `score ≥80` di Hunter è safe (DECISION).
- 🔴 **Disposable detection**: `tempmail.org`, `10minutemail.com`, etc. → exclude (no business intent).
- 🔴 **Greylisting**: server temp-fail (codici 202/222) richiedono retry dopo 5/15/60 min. `email_verify_waterfall.py` retry automatico, max 3.
- 🟡 **Cost spike senza cache**: bulk re-verification senza cache hit → costo lineare. Cache 30 giorni mandatory.
- 🟡 **Webmail (gmail/yahoo)**: `valid` ma low B2B priority. Flag `webmail_warning`, suggest se possibile cercare business email via Hunter Email Finder (alternative).
- 🟡 **Personal vs business email**: `mario.rossi@gmail.com` (probabile personal) vs `mario@acme.com` (business). Per outbound B2B, sempre preferisci business. Se solo personal disponibile → flag `personal_only` + decisione utente.
- 🟢 **Hunter rate limit**: 5 req/sec free, 15 req/sec premium. Script gestisce throttle.
- 🟢 **Apollo bulk_match**: max 10 record/call → batch.

## Scripts

- `scripts/email_verify_waterfall.py` (Fase C.3): wrapper CLI multi-tier verification con cache + retry + cost tracking.
- `scripts/mcp_detect.py` (Fase C.3): check hunter MCP availability.

## References

- [references/tool-integrations.md](../../references/tool-integrations.md): Hunter MCP details, REST V2 endpoint, Apollo people/match API
- [references/lead-enrichment-best-practices-2026.md](../../references/lead-enrichment-best-practices-2026.md): waterfall pattern + threshold

## Crediti

Pattern email verification waterfall consolidato 2026 (Hunter, Amplemarket, SyncGTM frameworks via NotebookLM `3b40733b`).
