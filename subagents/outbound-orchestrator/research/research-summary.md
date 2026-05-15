# Research Summary — `/outbound-orchestrator`

> **Output Fase A** del build. Risponde alle 7 research question di `BUILD-BRIEF.md` con citazione fonti. Sintesi strutturata per consumo nelle Fasi B-C-D.
>
> **Data**: 2026-04-30 · **Worker chat sessione 1** · **Metodo**: WebSearch + parallel-cli search + skill `heyreach-api` (grounded, testata 27/04/2026) + skill v1 `outbound-campaign` (Webinar 2 Learnn) come spunto. NotebookLM dedicato non creato (DECISION-009: timing-driven, fonti dirette sufficienti per saturare le 7 RQ).
>
> **Volumi**: ~30 fonti consultate, 7 RQ coperte, 8 signal-hook templates derivati, 4 sequence template structure, 12 edge case mappati.

## 0. Executive summary — top 5 finding

1. **Sequence cadence "widening gap" è lo standard 2026**: gap crescente tra step (2-3d, 4-5d, 7+d) batte modello daily/aggressivo. Reply rate gap-based 8-12% vs reply rate dense 3-4%. Multi-channel (email + LinkedIn) genera +40% engagement vs single-channel. [Allegrow, Salesmotion, 11x]
2. **Reply rate 2026 è data-driven, non copy-driven**: media B2B 3.43%, top performer 10-18%, ma il delta non viene da subject lines bensì da **data quality + signal recency** (24-48h dopo trigger = 3-5x reply rate). [Instantly, Landbase, Sapience]
3. **Anti-LLM detection è già operativo**: Gmail e Microsoft usano transformer trained su miliardi di email per detectare pattern templated. **69% decision-maker US flag negativamente email AI-generated**. Mitigation: AI per research/draft, output SHORT (15 word max) con vincoli specifici, no marker stilistici (em-dashes excessive, "I hope this finds you well", ecc.). [Sendr.ai, Autobound, Mailshake]
4. **Email deliverability 2026 = autentica O muori**: SPF + DKIM + DMARC `p=quarantine`/`p=reject` mandatory (BIMI optional ma +5-10% open rate). Warmup 4-6 settimane prima di volume. Daily cap warmed mailbox ≤50/day per ramping period. Postmaster Tools spam rate <0.3% (top performer <0.1%). [Apollo, Amplemarket, Warmy]
5. **GDPR cold email B2B EU è legittimo MA condizionato**: LIA documentato per ogni campagna PRE-send, opt-out in <30d via suppression cross-stack, **Italia richiede attenzione speciale a Garante Privacy + ePrivacy** (alcune interpretazioni richiedono soft-consent per email marketing diretto B2C; B2B "professional contacts" più permessivo). [DLA Piper IT 2025, LiteMail, Prospeo]

## 1. RQ1 — Cadence & sequence length & multi-channel timing

### Sequence length

| Target | Touchpoints | Window | Source |
|--------|-------------|--------|--------|
| **Enterprise** (>500 employee) | 7-10 touch | 45-60 giorni | Allegrow, 11x |
| **Mid-market** (50-500) | 5-7 touch | 21-35 giorni | Autobound, HubSpot |
| **SMB** (<50) | 4-5 touch | 14-21 giorni | Salesmotion, Mailshake |

**Default `/outbound-orchestrator`**: 5 step (mid-market sweet spot) → BUILD-BRIEF Q5 propone 3/5/7/Custom, scelta utente.

### Widening gap cadence (NEW 2026)

```
Step 1 → Step 2: 2-3 giorni
Step 2 → Step 3: 4-5 giorni
Step 3 → Step 4: 7-10 giorni
Step 4 → Step 5+: 10-14 giorni (break-up)
```

**Razionale**: imitare comportamento umano (dense early, sparse late). Gmail/Outlook trasformer detection flagga "velocity pattern" robotic come spam signal [Allegrow, 11x]. Modello `daily bump` = ban risk.

### Multi-channel timing default

```
Day 0: Email step 1 (opening + signal hook)
Day 2: LinkedIn connection request + nota 280 char (mention dello stesso signal)
Day 5: Email step 2 (value drop) — solo se NO reply email day 0
Day 7: LinkedIn message #1 — solo se connection accepted
Day 10: Email step 3 (social proof)
Day 14: LinkedIn message #2 (soft) — opzionale
Day 21: Email step 4 (break-up)
```

**Stop conditions**: reply detected (5-class) → pause sequence; bounce → suppress; out-of-office → snooze 7d; unsubscribe → suppress + cross-campaign.

### Send time optimization

- **Window**: martedì-giovedì 9-13 timezone prospect [HubSpot, Autobound]
- **Email length**: <125 parole, subject <7 parole, single CTA
- **Opening**: signal-specific (NO generic "I hope this finds you well")

## 2. RQ2 — SmartLead API capabilities 2026

### Key endpoints (per `references/api-recipes.md`)

| Endpoint | Method | Purpose | MCP tool |
|----------|--------|---------|----------|
| `/campaigns/create` | POST | Crea campagna vuota | `smartlead_create_campaign` |
| `/campaigns/<id>/sequences` | POST/PUT | Salva sequence multi-step | `smartlead_save_campaign_sequence` |
| `/campaigns/<id>/leads` | POST | Bulk import leads + merge fields | `smartlead_add_leads_to_campaign` |
| `/campaigns/<id>/email-accounts` | POST | Assigna mailbox sender | `smartlead_add_email_account_to_campaign` |
| `/campaigns/<id>/schedule` | POST | Configura timing send | `smartlead_update_campaign_schedule` |
| `/webhooks` | POST | Real-time event hooks | (curl, no MCP wrapper) |
| `/leads/<id>/category` | PATCH | Mark interested/not-interested/OOO | `smartlead_update_lead_category` |
| `/campaigns/<id>/statistics` | GET | Reply/open/click/bounce | `smartlead_get_campaign_statistics` |

### Webhook events utili per reply detection

- `LEAD_REPLIED` (positive/negative inferred via category)
- `LEAD_BOUNCED` (auto-suppress)
- `LEAD_UNSUBSCRIBED` (cross-campaign suppress)
- `EMAIL_OPENED` (engagement scoring)
- `EMAIL_CLICKED` (intent boost)

Webhook attivabili a 3 livelli: **Client / Campaign / User** (default = User per evitare miss). [SmartLead Help Center]

### Lead categories (5+)

`Interested`, `Not-Interested`, `Out-of-Office`, `Wrong-Person`, `Do-Not-Contact`, `Information-Request`, `Sender-Originated-Bounce`. Mapping → 5-class reply classification (RQ6).

### Daily limit & rate-limiting

- API rate: 100 req/min default, 1000 req/min su Pro plan
- Send limit: dipende da mailbox warmup (vedi RQ4)
- Bulk lead import: chunked a 500 leads/request raccomandato

### MCP wrapper LeadMagic

GitHub `LeadMagic/smartlead-mcp-server` (113 tools). **Già configurato in env Filippo** — `mcp__smartlead__*` namespace.

## 3. RQ3 — HeyReach API capabilities 2026

**Fonte primaria**: skill `~/.claude/skills/heyreach-api/SKILL.md` (testata 27/04/2026 da Filippo, valida).

### Key endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/campaign/Create` | POST | Crea campagna LinkedIn | Doc'd |
| `/campaign/UpdateSequence` | POST | Modifica template campagna esistente | **Non doc'd ma funziona** (only PAUSED/SCHEDULED/DRAFT/IN_PROGRESS) |
| `/campaign/Pause` | POST | Pausa campagna | Doc'd |
| `/campaign/Resume` | POST | Riprende campagna | Doc'd |
| `/campaign/StopLeadInCampaign` | POST | Stop lead specifico in campagna | Doc'd |
| `/campaign/AddLeadsToCampaignV2` | POST | Bulk import leads | Doc'd |
| `/campaign/GetCampaignSequence` | GET | Read sequence tree | Doc'd |
| `/campaign/GetById` | GET | Metadata campagna | Doc'd |
| `/list/GetLeadsFromList` | POST | Read lead+customFields | Doc'd |
| `/inbox/GetConversationsV2` | POST | Read conversations + lastMessage | Doc'd (no full thread) |

### Sintassi placeholder CRITICA

**HeyReach usa SINGLE brace** `{first_name}`, **NON** double brace. Bug subdolo: `{{var}}` invia letterali `{` `}` nel messaggio.

```python
# Auto-fix se trovato {{var}} in sequence
import re
DOUBLE = re.compile(r"\{\{([A-Za-z][A-Za-z0-9_-]*)\}\}")
def fix(s): return DOUBLE.sub(r"{\1}", s) if isinstance(s, str) else s
```

### Sequence shape (tree ricorsivo)

```json
{
  "nodeType": "CONNECTION_REQUEST",  // | MESSAGE | INMAIL | VIEW_PROFILE | LIKE_POST | CHECK_IS_CONNECTION | END
  "actionDelay": 2,
  "actionDelayUnit": "DAYS",
  "payload": {
    "messages": ["Ciao {first_name}, ho visto che {company_name}..."],
    "fallbackMessage": "Ciao {first_name}, ho visto..."
  },
  "conditionalNode": {...},   // se condizione (es. is_connection) vera
  "unconditionalNode": {...}  // default fallback
}
```

### Trick edit campagna FINISHED

`Resume → Pause → UpdateSequence` (FINISHED non accetta UpdateSequence direct, HTTP 400).

### Edge case

- **Liste condivise**: 2 campaign possono usare stessa `linkedInUserListId` → stop su una si riflette su entrambe. **Sempre stop cross-campaign** se shared list.
- **Lead in `Failed` state**: `StopLeadInCampaign` ritorna no-op message — già fermo.
- **Workspace-scoped API key**: ogni workspace HeyReach ha la sua key dedicata. MCP `heyreach` configurato globalmente punta a 1 workspace alla volta.
- **No campaign DELETE via API**: una volta creata si può solo Pausare. Attenzione a non spammare campagne test.

### Daily limit LinkedIn

- 80 connection request/day (organic account)
- 100/day con Sales Navigator
- 50/day raccomandato safety baseline

## 4. RQ4 — Email deliverability 2026

### Authentication mandatory

| Protocol | Setup | Compliance level | Source |
|----------|-------|------------------|--------|
| **SPF** | TXT record `v=spf1 include:... -all` | Mandatory | Apollo |
| **DKIM** | Selector record con CNAME provider | Mandatory | Apollo |
| **DMARC** | `v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@...` | Mandatory `p=quarantine` minimum, `p=reject` ideale | Amplemarket, Egen |
| **BIMI** | TXT + VMC certificate (~$1500/year) | Optional, +5-10% open rate | Warmy, Mailmunch |
| **MTA-STS** | TXT + policy file HTTPS | Optional ma raccomandato | Apollo |

**Threshold compliance Fortune 500 in 2026**: 75% domains con DMARC, solo 35% con `p=reject`.

### Warmup days/volume

| Mailbox age | Daily cap raccomandato | Send volume strategy |
|-------------|----------------------|---------------------|
| **0-14 giorni** (cold) | **5-10 / day** | Warmup tool only (Smartsenders, Lemwarm, Warmy), NO real outbound |
| **14-30 giorni** (warming) | 10-20 / day | Mixed warmup + small batch real outbound |
| **30-90 giorni** (warmed) | 30-50 / day | Real outbound ramping |
| **90+ giorni** (aged) | 80-150 / day | Production volume |
| **6+ mesi** (seasoned) | 200-300 / day | Max safe volume |

**Rule "blocca bulk se warmup <14d"**: hardcoded gate in `deliverability-check` skill (DECISION-008).

### Spam triggers 2026

- **Velocity**: 50+ emails in 1 ora = bot signal
- **Density**: stessa email a >100 contatti = template signal (anche se dynamic fields)
- **Markers stylistic AI**: em-dash excessive, "delve into", "navigate the landscape", "I hope this email finds you well"
- **Subject ALL CAPS or punteggiatura ripetuta** ("FREE!!!", "URGENT!!")
- **Links shortened** (bit.ly, t.co): increase spam score
- **Image-only email**: filtrato come spam
- **No plain-text alternative**: HTML-only flagga

### Postmaster Tools threshold (Gmail)

- Spam rate target: **<0.3%** (top: <0.1%)
- IP reputation: High obbligatorio per inbox placement
- Domain reputation: idem
- Authentication pass rate: >99%

### Inbox placement benchmark

- Global average: **83-85% inbox**
- Cold outreach typical: 70-75% (ramping)
- Top sender: 90%+

## 5. RQ5 — Personalization patterns 2026 (signal-driven)

### 8 signal-hook templates (derivati da research + skill v1)

| # | Signal type | Trigger source | Hook template (italiano + inglese) |
|---|-------------|----------------|-----------------------------------|
| 1 | **Job change** | LinkedIn `posizione cambiata <30d` | "Vidi che sei passato a {new_role} a {new_company} a {month}. Congratulazioni!" / "Saw you joined {new_company} as {new_role} in {month} — congrats!" |
| 2 | **Funding round** | Crunchbase/PitchBook/news | "Ho letto del round {round_type} di {company} — congratulazioni!" / "Read about {company}'s {round} — congrats!" |
| 3 | **Hiring surge** | LinkedIn job posts >5 in 30d | "Vedo che state cercando {role} a {company} — sembra crescita rapida." / "{company} is hiring {n} {role}s — looks like a growth phase." |
| 4 | **Podcast/content guest** | Podcast feed RSS, YouTube, blog | "Ho ascoltato il tuo intervento su {podcast} re {topic} — punto interessante su {specific}." |
| 5 | **Recent post LinkedIn/X** | LinkedIn API feed | "Il tuo post su {topic} mi ha colpito — specialmente {specific quote}." |
| 6 | **Conference attended/speaker** | Event landing pages | "Ti ho visto a {conference} — il tuo talk su {topic} è stato il highlight della giornata." |
| 7 | **Tool stack change** | BuiltWith / Wappalyzer | "Ho notato che state usando {new_tool} — interessante shift da {old_tool}." |
| 8 | **Geo/event** | Event/news geo | "Sono a {city} per {event} {date} — sarebbe un'opportunità di un caffè?" |

### Anti-LLM-detection rules (mandatory)

1. **Constraint prompt**: 15-25 word max per first line, signal-specific
2. **Variability**: 3+ variants per template, random selection
3. **Banned markers**: "delve into", "navigate the landscape", "I hope this email finds you well", em-dashes excessive, "—" doppio, "leverage", "synergy"
4. **Stylistic match brand voice**: direct/friendly/educational/bold definito in config
5. **Signal recency check**: trigger <30d obbligatorio (decay completo dopo 90d)
6. **No template "Mad Lib"**: `{generic_phrase} {company} {role}` rilevabile da Gmail Trasformer
7. **First-line UNIQUE**: hash-check su last 100 first-line generate, reject duplicates
8. **Output check**: passa risultato attraverso 1 LLM call seconda "rendi questo più conversazionale, max 25 parole"

### A/B test variants

- 2 variants subject + 2 variants first-line = 4 combo
- Min 30 lead per variant per significance (rule of thumb)
- Test 1 variabile alla volta (subject OR first-line, NOT both)
- Winning criterion: reply rate (NOT open rate, manipulato da iOS Mail privacy)

### Reply rate boost evidence

- Personalized subject: 3% → 7% (+133%) [Instantly]
- Signal-based hook: 3% → 15-25% (+5x) [Apollo, Sendr]
- Hyper-relevant + <80 word + single CTA: top quartile 18% [Cleanlist]

## 6. RQ6 — Reply detection & 5-class handling

### 5-class taxonomy

| Class | Indicators | Auto-action |
|-------|-----------|-------------|
| **Positive** | "interested", "demo", "schedule", "tell me more", "calendly" | Pause sequence, forward to user inbox, mark `Interested` in SmartLead |
| **Negative** | "not interested", "remove me", "stop", "we have it" | Pause + suppress lead, mark `Not-Interested`, NOT cross-campaign suppress |
| **Out-of-Office** | "OOO", "vacation", "out until", "annual leave", "ferie" | Snooze 7-14d, then resume sequence |
| **Unsubscribe** | "unsubscribe", "remove from list", explicit opt-out keyword | Suppress lead **cross-campaign** (mandatory GDPR), mark `Do-Not-Contact` |
| **Bounce** | DSN bounce header, "delivery failed", "550", "address not found" | Suppress hard bounce immediato, soft bounce retry 24h max 3 |

### Detection method (rule-based + LLM)

1. **Rule-based pre-filter** (regex + DSN headers): catch 70-80% case ovvi (OOO, bounce, explicit unsubscribe)
2. **LLM fallback** per casi ambigui: prompt "Classify this reply as one of {5 classes}. Reply: <body>. Output JSON {class, confidence, action}"
3. **Confidence threshold**: >0.85 auto-action, <0.85 → manual triage queue

### SmartLead webhook integration

- Subscribe `LEAD_REPLIED` → `reply_classify.py` → SmartLead `update_lead_category` API call
- Forward positive reply via Gmail MCP (per Filippo: `claude_ai_Gmail` MCP) o smtp
- Pause sequence via SmartLead API on negative/positive

### Cross-campaign suppression

Mantieni `<memory>/suppression.csv` con email + reason + timestamp. Ogni nuova campagna check suppression list **prima** di add leads (DECISION-002 dei /lead-finder-pro: idem qui).

## 7. RQ7 — GDPR EU outbound + Italy Garante Privacy

### LIA — Legitimate Interest Assessment

3 step mandatory PRIMA di campagna:

1. **Identify**: cosa vuoi (es. "B2B targeted outreach to {ICP}")
2. **Necessity**: dimostra che email è proporzionata vs alternative (call/event)
3. **Balance**: rispetto privacy → only professional email, opt-out chiaro, content relevant to role, no Article 9 sensitive data

LIA documentato per ogni campagna (NON retroattivo). Template in `references/gdpr-outbound-eu.md`.

### Opt-out + suppression cross-stack

- Footer mandatory: opt-out link + identity sender + indirizzo fisico (CAN-SPAM)
- Processing time: **<24h ideale, <30d obbligatorio GDPR**
- Suppression list cross-stack: SmartLead + HeyReach + Lemlist + CRM Attio sync
- Re-add a suppression list: blocca permanente, no exception

### Italy Garante Privacy specifics

**Fonte: DLA Piper Privacy Matters luglio 2025**: Garante Italia sta orientandosi verso "double opt-in mandatory" per email marketing **B2C**. Per **B2B contacts professionali (work email)** legitimate interest resta valido se LIA documentato.

Best practice IT 2026:
- Privacy Policy linkata in footer email (italiano + inglese se EU mix)
- "Source documented": come hai trovato il contatto (es. "LinkedIn profile pubblico", "evento <name>", "lista commerciale acquisita da <vendor>")
- Data minimization: solo nome + cognome + email + role + company (no foto, no preferenze personali)
- Article 9 exclusion: NO health, race, religion, political, sexual orientation, biometric
- Retention: 12 mesi max post-contact (default), reset al re-engagement
- Negative scoring: lead unsubscribed → -25, competitor → -40 (prevent re-engagement)

### Footer bilingue (IT + EN) se EU mix detected

```html
<p style="font-size: 11px; color: #888;">
Stai ricevendo questa email in qualità di [role] presso [company] — fonte: [source].
Se non desideri ricevere ulteriori comunicazioni, <a href="{unsubscribe_url}">disiscriviti qui</a>.
Inviato da [Sender Name] · [Sender Address] · [Privacy Policy](privacy_url).
<br>
You are receiving this email as [role] at [company] — source: [source].
To opt out, <a href="{unsubscribe_url}">unsubscribe here</a>.
</p>
```

### ePrivacy Directive nuance

ePrivacy si sovrappone a GDPR. Implementazione varia per Stato membro. **Italia recepita con "prior consent for direct marketing email" (Codice Privacy art. 130)** — ma per B2B contacts professionali Garante ha confermato in più provvedimenti che l'art. 6(1)(f) GDPR (legitimate interest) prevale se LIA solido + opt-out attivo. [Garante FAQ + Provv. n. 230/2020]

## 8. Tool capabilities matrix

| Feature | SmartLead | HeyReach | Lemlist | Instantly |
|---------|-----------|----------|---------|-----------|
| **Email cold outreach** | ✅ Best-in-class | ❌ | ✅ | ✅ |
| **LinkedIn outreach** | ❌ | ✅ Best-in-class | ✅ | ❌ |
| **Multi-channel native** | ❌ (HeyReach native) | ❌ (Smartlead native) | ✅ | ✅ |
| **AI Reply Agent** | Limited | ❌ | ❌ | ✅ Best |
| **API access** | ✅ Robust | ✅ Robust | ⚠️ Limited | ✅ |
| **Webhook native** | ✅ 3-level (client/campaign/user) | ⚠️ Limited | ✅ | ✅ |
| **Warmup native** | ✅ Smartsenders | ❌ (LinkedIn no warmup) | ✅ Lemwarm | ✅ |
| **Pricing entry** | $94/mo | $79/mo | $55/mo | $97/mo |
| **MCP server** | ✅ LeadMagic 113 tools | ✅ Filippo-tested | ❌ | ❌ |

**Default `/outbound-orchestrator`**: SmartLead (email primary) + HeyReach (LinkedIn complement) — stack Filippo già attivo.

## 9. 4 sequence template structures

### Template A — Direct Demo (5 step, mid-market SaaS)

```
Day 0 — Email step 1: Signal hook + value prop + soft CTA "vale 15 min?"
Day 2 — LinkedIn connect + nota (mention same signal)
Day 5 — Email step 2: case study + harder CTA "ti chiamo martedì 15:00?"
Day 10 — Email step 3: social proof + soft CTA
Day 14 — LinkedIn message #1 (post-acceptance) — soft follow-up
Day 21 — Email step 4: break-up "chiudi tu o continuo?"
```

### Template B — Education-First (7 step, enterprise complex sale)

```
Day 0 — Email: insight industry-specific (no pitch)
Day 5 — LinkedIn connect
Day 7 — Email: case study same industry
Day 14 — Email: framework/template downloadable
Day 21 — LinkedIn message: comment recent post
Day 30 — Email: data point recente + soft CTA
Day 45 — Email: break-up
```

### Template C — Pain Discovery (5 step, mid-market)

```
Day 0 — Email: domanda diagnostica (NO pitch) — "sto vedendo X pain in {industry}, succede anche a {company}?"
Day 3 — Email: condividi case study correlato
Day 7 — LinkedIn connect + reference reply (se ha replicato)
Day 14 — Email: hard CTA call
Day 21 — Email: break-up
```

### Template D — Multi-threading (5 step parallel su 3 stakeholder)

```
Account-based: 3 lead per account targeting (Champion + Decision-Maker + User).
Sequence per lead: 4-5 step normale, MA messaggi cross-reference ("ho scritto anche al tuo collega {name}").
Coordinamento timing: tutti day 0 stesso giorno (NOT staggered).
Aggregation reply: se 1 reply → pause altri 2 stessa account.
```

## 10. Edge case scoperti (12 case)

| # | Edge case | Handler |
|---|-----------|---------|
| 1 | Mailbox warmup <14d | BLOCK bulk send + warning |
| 2 | DKIM/DMARC missing | BLOCK + suggerisci setup, link guide |
| 3 | Spam rate >0.3% Postmaster | BLOCK + alert "decay reputation" |
| 4 | Lead role-based (info@, sales@) | Reject in `validate_input.py` |
| 5 | Lead in suppression list | Skip + warning, NO error |
| 6 | Reply ambigua (confidence <0.85 LLM) | Manual triage queue |
| 7 | OOO reply | Snooze 7-14d → resume |
| 8 | Bounce hard | Suppress immediato cross-campaign |
| 9 | HeyReach `{{var}}` double brace | Auto-fix via regex prima di UpdateSequence |
| 10 | Campaign FINISHED edit needed | Resume → Pause → UpdateSequence (HeyReach trick) |
| 11 | Italy lead + GDPR mode | Footer bilingue mandatory + LIA documentato + retention 12mo |
| 12 | A/B test variant under-sample (<30 lead) | Statistical warning "results not significant" |

## 11. Decisioni emergent flagged per Fase B (DECISIONS.md)

Ricomprendono le 5 emergent del BUILD-BRIEF + 4 nuove dalla research:

- **DECISION-005** — Confirm soglia 50 lead (>50 = explicit yes, ≤50 = dry-run preview poi procede)
- **DECISION-006** — Multi-channel timing: email day 0 → LinkedIn connect day 2 → LinkedIn msg day 7 (post-acceptance) → email day 5/10/14 (paralleli)
- **DECISION-007** — API key env vars only (`SMARTLEAD_API_KEY`, `HEYREACH_API_KEY`), NO storage in config (security)
- **DECISION-008** — Daily cap matrix per mailbox age: 5-10 (cold 0-14d) → 30-50 (warmed 30-90d) → 200-300 (seasoned 6+ mo)
- **DECISION-009** — NotebookLM skip in Fase A (research consolidata via WebSearch + parallel-cli + skill heyreach-api esistente)
- **DECISION-010** — Sequence widening gap default (2-3d, 4-5d, 7-10d, 10-14d) vs daily/aggressive
- **DECISION-011** — Anti-LLM-detection mandatory: 8 banned markers + 3+ variant random + first-line uniqueness hash
- **DECISION-012** — Reply classification 5-class hybrid (rule-based pre-filter 70-80%, LLM fallback 20-30%, threshold confidence 0.85)
- **DECISION-013** — GDPR Italy: B2B legitimate interest valid + LIA docs + footer bilingue se EU mix detected; B2C = no scope (skip)

## 12. Sources

### RQ1-2 — Cadence & SmartLead

- [Allegrow — Cold Email Sequence Guide 2026](https://www.allegrow.co/knowledge-base/cold-email-sequences)
- [Autobound — Cold Email Guide 2026](https://www.autobound.ai/blog/cold-email-guide-2026)
- [Salesmotion — Cold Outreach 2026 B2B](https://salesmotion.io/blog/cold-outreach-best-practices)
- [11x — Sales Cadence 2026](https://www.11x.ai/tips/sales-cadence-best-practices)
- [SmartLead Help Center — API & Webhooks](https://helpcenter.smartlead.ai/en/articles/125-full-api-documentation)
- [SmartLead — API Introduction](https://api.smartlead.ai/introduction)
- [LeadMagic SmartLead MCP server](https://github.com/LeadMagic/smartlead-mcp-server)

### RQ3 — HeyReach

- Skill `~/.claude/skills/heyreach-api/SKILL.md` (testata 27/04/2026)
- [HeyReach — Custom Variables](https://help.heyreach.io/en/articles/9879182-how-to-import-and-use-custom-variables)

### RQ4 — Deliverability

- [Apollo — Email Deliverability Checklist 2026](https://21165194.fs1.hubspotusercontent-na1.net/hubfs/21165194/Checklists_Apollo%E2%80%99s%20Cold%20Email%20Deliverability%20Checklist.pdf)
- [Amplemarket — Deliverability Guide 2026](https://www.amplemarket.com/blog/email-deliverability-guide-2026)
- [Egen — SPF DKIM DMARC Checklist 2026](https://www.egenconsulting.com/blog/email-deliverability-2026.html)
- [Warmy — Sender Reputation 2026](https://www.warmy.io/blog/email-sender-reputation-score/)

### RQ5 — Personalization & anti-LLM

- [Sendr.ai — Humanize Cold Outreach 2026](https://www.sendr.ai/blog/what-are-the-best-ways-to-humanize-cold-outreach-using-ai-in-2026)
- [Instantly — Future of Cold Email 2026-2027](https://instantly.ai/blog/future-of-cold-email-ai-personalization-automation-trends-shaping-2026-2027/)
- [Landbase — Data Quality 2026](https://www.landbase.com/blog/cold-email-2026-data-quality-matters-more-than-copy)
- [Sapience — Reply Rate Benchmarks 2026](https://sapience.systems/blog/cold-email-response-rate-benchmarks)
- [Cleanlist — Response Rate Stats 2026](https://www.cleanlist.ai/blog/2026-02-18-cold-email-response-rate-statistics)

### RQ6 — Reply Classification

- [Instantly — Automate Email Triage AI](https://instantly.ai/blog/automate-email-triage-classification-ai/)
- [Apollo — Email Reply Classification Done Right](https://www.apollo.io/tech-blog/email-reply-classification-done-right)
- [AiSDR — Teaching Generative AI Classify Replies](https://aisdr.com/blog/leadership-nuggets-teaching-generative-ai-to-classify-email-responses/)

### RQ7 — GDPR EU + Italy

- [DLA Piper — Italy Marketing Privacy Consent 2025](https://privacymatters.dlapiper.com/2025/07/italy-marketing-privacy-consent-is-double-opt-in-now-mandatory/)
- [LiteMail — GDPR LIA Cold Email 2026](https://litemail.ai/blog/gdpr-legitimate-interest-cold-email-2026)
- [Prospeo — GDPR Cold Email Rules 2026](https://prospeo.io/s/gdpr-cold-email)
- [GrowthList — GDPR 7 Rules 2026](https://growthlist.co/gdpr-cold-email/)
- [Mailshake — Cold Email Compliance 2026](https://mailshake.com/blog/cold-email-compliance/)
- [Garante Privacy — English section](https://www.garanteprivacy.it/web/garante-privacy-en)
- GDPR Recital 47 (Direct Marketing Legitimate Interest)
