# Email Deliverability 2026

> Reference doc per `/outbound-orchestrator` skill `deliverability-check`. SPF/DKIM/DMARC/BIMI mandatory + warmup days/volume + daily cap matrix + spam triggers + Postmaster threshold + blacklist scan.
>
> Fonte: `research/research-summary.md` RQ4 + Apollo 2026 Checklist + Amplemarket guide + Warmy + Egen.

## TL;DR

1. **Autentica O muori**: SPF + DKIM + DMARC `p=quarantine` minimum (`p=reject` ideale). Senza non passi neanche per il portone.
2. **Warmup 4-6 settimane**: 5-10 email/day giorni 0-14, ramping graduale. NO bulk send su domain non-warmato.
3. **Daily cap matrix age-aware**: 5-10 (cold) → 30-50 (warmed) → 200-300 (seasoned).
4. **Postmaster spam <0.3%**: monitor weekly, reazione <24h se threshold superato.
5. **Plain-text alt + unsubscribe link + identity sender**: mandatory non-negotiable.

## 1. Authentication setup (mandatory)

### SPF (Sender Policy Framework)

DNS TXT record sul domain mittente. Specifica chi è autorizzato a inviare email per il domain.

```
v=spf1 include:_spf.google.com include:smartlead.ai -all
```

- `-all` = hard fail (raccomandato per outbound)
- `~all` = soft fail (default safe)
- Max 10 DNS lookups (count each `include:`)

Check: `dig +short TXT yourdomain.com | grep spf`

### DKIM (DomainKeys Identified Mail)

Firma criptografica pubblica/privata. Verifica integrità e ownership.

```
selector1._domainkey.yourdomain.com  TXT  v=DKIM1; k=rsa; p=<public_key>
```

Selector typically `google` (Workspace), `smartlead` (SmartLead Smartsenders), `s1` o `default` (custom). Provider-specific.

Check: `dig +short TXT smartlead._domainkey.yourdomain.com`

### DMARC (Domain-based Message Authentication)

Policy layer su SPF + DKIM. Cosa fare se SPF/DKIM falliscono.

```
_dmarc.yourdomain.com  TXT  "v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@yourdomain.com; sp=quarantine; aspf=s; adkim=s"
```

Policy progression:
- `p=none` → monitoring only (start qui per 30d, leggi report rua)
- `p=quarantine` → mette in spam mail non auth
- `p=reject` → blocca mail non auth (ideale, ma richiede DKIM+SPF perfetto)

**Per outbound 2026**: minimum `p=quarantine`. `p=reject` per BIMI eligibility.

Check: `dig +short TXT _dmarc.yourdomain.com`

### BIMI (Brand Indicators for Message Identification) — opzionale

Logo brand visibile in inbox Gmail/Yahoo. Boost open rate +5-10%.

Requisiti:
- DMARC `p=quarantine` o `p=reject` con `pct=100`
- VMC (Verified Mark Certificate) — costa ~$1500/anno (Entrust, DigiCert)
- Logo SVG hosted HTTPS

```
default._bimi.yourdomain.com  TXT  "v=BIMI1; l=https://yourdomain.com/bimi/logo.svg; a=https://yourdomain.com/bimi/vmc.pem"
```

Check: BIMI Inspector (validatore online).

### MTA-STS — opzionale ma raccomandato

TLS enforcement per inbound. Migliora trust score.

```
_mta-sts.yourdomain.com  TXT  "v=STSv1; id=2026...."
mta-sts.yourdomain.com    A    <pointing-to-policy-https>
```

## 2. Warmup days/volume table

Strategia ramping per nuovo domain o nuova mailbox:

| Mailbox age | Daily volume real | Warmup tool volume | Strategy |
|-------------|-------------------|-------------------|----------|
| 0-7d | 0 | 5-10/day | Tool warmup ONLY, no real outbound |
| 7-14d | 0-5 | 10-15/day | Tool + small batch internal/known recipients |
| 14-21d | 5-15 | 20-30/day | Mixed, low-volume real outbound |
| 21-30d | 15-25 | 30-50/day | Ramping, monitor reply rate |
| 30-60d | 30-50 | 50/day | **Production volume safe** |
| 60-90d | 50-80 | 50/day | Increase if engagement healthy |
| 90d-6mo | 80-150 | 50/day | Aged mailbox, max value |
| 6+mo | 200-300 | 50/day | Seasoned, max safe production |

**Rule "blocca bulk se warmup <14d"**: hardcoded gate in skill `deliverability-check`. Override esplicito utente solo via `--force-no-warmup-check` con warning.

### Warmup tools

- **Smartsenders** (SmartLead native, included in plan)
- **Lemwarm** (Lemlist native)
- **Warmy** (standalone, $99/mo)
- **Mailwarm** (standalone)

Pattern: tool simula reply scambi tra mailbox warmuppate, build sender reputation gradualmente.

## 3. Daily cap matrix per mailbox age (DECISION-008)

Per `safety.daily_cap_per_mailbox` config:

```yaml
daily_cap_per_mailbox:
  cold_0_14d: 5
  warming_14_30d: 15
  warmed_30_90d: 50      # default subagent baseline
  aged_90d_6mo: 100
  seasoned_6mo_plus: 250
```

Tre source per calcolare age mailbox:
1. SmartLead API: `mcp__smartlead__get_warmup_stats_by_email_account_id` → field `warmup_days`
2. Manual config user (Q discovery aggiuntivo se utente specifica)
3. Default: assume `warmed_30_90d` (50/day) se non specificato

## 4. Spam triggers 2026

### Velocity-based

- 50+ email in 1 ora da stesso mailbox = bot signal
- Volume spike >2x baseline giornaliero = anomaly detection
- Identical content a >100 contatti = template signal (anche con dynamic fields)

### Content-based

#### Stylistic AI markers (banned 2026)

```
delve into
navigate the landscape
I hope this email finds you well
leverage
synergy
seamlessly
cutting-edge
unlock the potential
robust solution
```

Em-dash multipli (`—`) flag. Replace con `,` o `.` o `-`.

#### Subject patterns

- ALL CAPS → spam filter
- Punteggiatura ripetuta (`!!!`, `???`) → spam
- "FREE", "URGENT", "ACT NOW", "100% guaranteed" → spam
- "[FW:]" o "[Re:]" fake (NO real reply thread) → spam + trust killer

#### Body patterns

- Image-only (no text alt) → filtrato
- HTML-only senza plain-text alt → flag
- Link shortener (bit.ly, t.co, ow.ly) → +spam score
- Multi-CTA con button colorati → "salesy"
- Tabelle complesse con CSS inline → render issue

### Sender behavior

- High bounce rate (>5%) → reputation tank
- High spam complaint rate (>0.3% Gmail Postmaster) → progressive penalty
- Low engagement (open <20%, reply <1%) → ISP signal "unwanted"
- Unsubscribe rate >0.5% → list quality flag

## 5. Postmaster Tools threshold

### Gmail Postmaster Tools

Free, ma verifica domain ownership. Track:

| Metric | Target | Action threshold |
|--------|--------|------------------|
| Spam rate | <0.1% | >0.3% = STOP, reputation decay imminent |
| IP reputation | High | Medium = warning, Low = blocked Gmail |
| Domain reputation | High | Bad = ban Gmail |
| Authentication pass rate | >99% | <95% = SPF/DKIM/DMARC issue |
| Encryption (TLS) | >99% | <95% = MTA-STS issue |
| Delivery errors | <0.5% | >2% = invalid recipients in list |

### Microsoft Smart Network Data Services (SNDS)

Microsoft Postmaster equivalent. Check:
- Complaint rate <0.3%
- Trap hits (spam trap detection)

## 6. Inbox placement benchmark 2026

| Sender tier | Inbox placement | Spam folder | Missing |
|-------------|-----------------|-------------|---------|
| **Elite (top 1%)** | 95-98% | 1-3% | <1% |
| **Top quartile** | 90-95% | 3-5% | <2% |
| **Average B2B** | 83-87% | 8-12% | 3-5% |
| **Below average** | 70-80% | 15-20% | 5-10% |
| **Tank reputation** | <60% | 30%+ | 10%+ |

Test inbox placement: GlockApps, Mail-Tester (free), Lockify, Litmus.

## 7. Blacklist scan

Pre-flight check su lista RBL (Real-time Blacklist):

- Spamhaus SBL/CSS/PBL (most authoritative)
- Spamcop
- Barracuda
- Sorbs
- SURBL

Tool: MXToolbox blacklist check, MultiRBL.valli.org.

Se blacklisted → fix root cause (warmup, content, complaint), poi delisting request via provider portal.

## 8. Pre-flight checklist (skill `deliverability-check`)

```python
checks = {
    "spf_record": dns_query_spf(sender_domain),
    "dkim_record": dns_query_dkim(sender_domain, selector),
    "dmarc_record": dns_query_dmarc(sender_domain),
    "dmarc_policy": parse_dmarc_policy(),  # require >= "quarantine"
    "mailbox_age_days": query_mailbox_age(mailbox),
    "warmup_active": query_warmup_status(mailbox),
    "daily_cap_remaining": query_daily_cap(mailbox, today_sent),
    "blacklist_scan": query_rbl(sender_domain),
    "spam_rate_postmaster": query_postmaster(sender_domain),  # se accessible
    "unsubscribe_link_in_template": grep_template("{unsubscribe_url}"),
    "footer_identity": grep_template_for_sender_address(),
    "plain_text_alt_present": check_email_template_has_text_alt()
}
```

Output: `{ready: bool, issues: [{check, status, recommendation}], warnings: []}`

Esempio output blocking:

```json
{
  "ready": false,
  "issues": [
    {"check": "dmarc_policy", "status": "p=none", "recommendation": "Set DMARC p=quarantine minimum before sending"},
    {"check": "mailbox_age_days", "status": "8d", "recommendation": "Mailbox too new (<14d). Continue warmup tool only."}
  ],
  "warnings": [],
  "daily_cap_remaining": 0,
  "mailbox_age_days": 8,
  "dns_status": {"spf": "ok", "dkim": "ok", "dmarc": "p=none ⚠️", "bimi": "absent"}
}
```

## 9. Recovery se reputation tanked

### Sintomi

- Inbox placement <70%
- Spam rate >0.3% Postmaster
- Reply rate halved senza change
- Complaints/unsubscribe spike

### Recovery protocol (4 settimane)

1. **Settimana 1**: STOP outbound. Identify root cause (warmup, content, list quality, volume spike). Run blacklist scan. Check Postmaster.
2. **Settimana 2**: List hygiene — remove email <0.80 confidence, role-based, suppression. Domain warmup tool 50/day.
3. **Settimana 3**: Restart small batch — 5-10 lead/day Hot grade A only. Monitor reply rate + bounce.
4. **Settimana 4**: Ramp gradualmente — 15-30/day. Postmaster check daily. Continua se inbox >85%.

Tempo recovery medio: 4-8 settimane. Permanent ban: rare ma possibile (>1% spam rate sustained).

## 10. Reference esterni

- [Apollo's 2026 Email Deliverability Checklist (PDF)](https://21165194.fs1.hubspotusercontent-na1.net/hubfs/21165194/Checklists_Apollo%E2%80%99s%20Cold%20Email%20Deliverability%20Checklist.pdf)
- [Amplemarket — Email Deliverability Guide 2026](https://www.amplemarket.com/blog/email-deliverability-guide-2026)
- [Egen — SPF DKIM DMARC Checklist 2026](https://www.egenconsulting.com/blog/email-deliverability-2026.html)
- [Warmy — Sender Reputation Score 2026](https://www.warmy.io/blog/email-sender-reputation-score/)
- [Mailmunch — Mastering Deliverability 2026](https://www.mailmunch.com/blog/mastering-email-deliverability)
- Gmail Postmaster Tools: https://postmaster.google.com/
- Microsoft SNDS: https://sendersupport.olc.protection.outlook.com/snds/
- MXToolbox blacklist: https://mxtoolbox.com/blacklists.aspx
- Mail-Tester: https://www.mail-tester.com/
