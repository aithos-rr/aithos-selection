# `/outbound-orchestrator` — Cold Outbound Multi-Channel B2B

> Subagent Claude Code che trasforma lista lead enriched in sequenze email + LinkedIn personalizzate, le carica via API SmartLead/HeyReach, gestisce reply 5-class + GDPR. Action-driven con safety contract stringente. Pack v2 Learnn.

## Cosa fa

Da output `/lead-finder-pro` (CSV 17 colonne, lead Hot/Warm grade A+B), `/outbound-orchestrator`:

1. **Valida** input schema + filtra (no role-based, no suppression, no GDPR-excluded)
2. **Pre-flight check** deliverability (SPF/DKIM/DMARC, warmup, daily cap, RBL blacklist)
3. **Personalizza** first-line per ogni lead via signal-driven AI (8 hook templates: job-change, funding, hiring, podcast, content, conference, tool-stack, geo)
4. **Build** sequenza multi-channel email + LinkedIn da template (Direct Demo, Education-First, Pain Discovery, Multi-threading) con widening gap timing + A/B test
5. **Dry-run preview** mandatory primo run + confirm step >50 lead
6. **Upload** via API SmartLead (email) + HeyReach (LinkedIn) con single-brace enforce + auto-fix
7. **Monitor reply** webhook 5-class auto-classification (positive/negative/OOO/unsubscribe/bounce) + auto-pause + cross-stack suppression
8. **GDPR EU** auto-mode: footer bilingue, LIA, suppression, Italy Garante specifics, retention 12mo

Audience: SDR, BDR, Founder, Marketer GTM. NON developer — italiano user-facing, inglese tecnico.

## Installazione

### 1. Pre-requisiti

- Claude Code installato
- Python 3.10+
- Dipendenze:

```bash
cd .claude/agents/outbound-orchestrator
pip install -r scripts/requirements.txt
```

### 2. API key in env vars (`~/.zshrc`)

```bash
# Required (almeno SmartLead se outbound primary)
export SMARTLEAD_API_KEY='your_smartlead_key'

# Required se LinkedIn outreach
export HEYREACH_API_KEY='your_heyreach_key'

# Optional (per cross-check email verify)
export APOLLO_API_KEY='your_apollo_key'
```

Reload: `source ~/.zshrc`.

### 3. MCP servers (già configurati in env Filippo)

Verifica:

```bash
python .claude/agents/outbound-orchestrator/scripts/mcp_detect.py
```

Atteso:
```
✓ smartlead
✓ heyreach
✓ attio-mcp
✓ google-personal
✓ claude_ai_Gmail
```

Se ✗, vedi sezione [Troubleshooting](#troubleshooting).

### 4. First run

In Claude Code:

```
/outbound-orchestrator
```

Il subagent eseguirà discovery 8 domande → salva config in `<memory>/config.md` → pronto.

## Esempi d'uso

### Esempio 1 — Lancio campagna chain dopo `/lead-finder-pro`

```
User: ho appena finito /lead-finder-pro, output `output/leads_20260430_0830_hot.csv` con 80 lead grade A. Lancia campagna outbound email-only.

Subagent:
1. validate_input.py → 80 compliant
2. Pre-flight check yourdomain.com → ✓ ready
3. Personalization 80 × 3 variants → completed
4. Sequence build Direct Demo 5-step
5. Dry-run preview 3 sample → user review → "ok"
6. SmartLead upload + START
7. Report `output/report_<...>.md`
```

### Esempio 2 — Multi-channel EU GDPR

```
User: campagna multi-channel per 30 lead Italia + Francia da CSV `leads_eu_warm.csv`. Email + LinkedIn.

Subagent:
1. validate → 30 input → 27 compliant (3 personal email rejected gmail/libero)
2. GDPR EU detected → footer bilingue auto, LIA template generato (review utente)
3. Personalization italiano + first-line variants
4. Sequence build multi-channel (email + LinkedIn day 0/2/5/7/10)
5. Dry-run + execute (sotto 50, no confirm explicit ma dry-run preview required)
6. SmartLead + HeyReach upload (single-brace enforced)
7. Webhook setup
8. Report con GDPR section dettagliata
```

### Esempio 3 — Audit campagna esistente

```
User: audit la campagna SmartLead "Yellow Tech Q2 2026 SaaS USA". Voglio sapere reply rate + suppression health.

Subagent:
1. mcp__smartlead__smartlead_get_campaign_statistics → reply rate 7.2%, bounce 1.1%, unsubscribe 0.4%
2. Cross-check suppression list locale vs SmartLead global blocklist → sync 3 nuove entry
3. Reply classification breakdown: 12 positive (forwarded), 8 negative, 5 OOO (snoozed), 2 unsubscribe (cross-stack), 1 bounce
4. Report markdown con benchmark + recommendation
```

### Esempio 4 — Suppress lead manualmente

```
User: mario.rossi@company.com mi ha chiesto di rimuoverlo. Sync su tutti i tool.

Subagent:
1. Append <memory>/suppression.csv
2. mcp__smartlead__smartlead_add_lead_to_global_blocklist
3. Loop active HeyReach campaigns → stop_lead
4. mcp__attio_mcp__update_record → do_not_contact = true
5. Confirm: "Lead suppressed cross-stack."
```

### Esempio 5 — Reconfigure per nuovo cliente

```
User: voglio cambiare config, sto lavorando su nuovo cliente. ICP diversa, value prop diversa.

Subagent:
1. Backup <memory>/config.md → config_backup_<ts>.md
2. Discovery 8 domande con default = valori precedenti
3. User aggiorna fields (ICP, value prop, voice)
4. Save nuovo config + summary "rispetto a prima è cambiato: ICP, value prop, voice"
```

## FAQ

### Q: Quanto costa lanciare una campagna 100 lead?

- SmartLead Pro: $94/mese (incluso warmup)
- HeyReach: $79/mese (1 LinkedIn account)
- LLM cost personalization (300 first-line gen): ~$5
- Total ricorrente: ~$180/mese setup

A reply rate 8% (top quartile) = 8 reply, 30% positive = ~2.4 demo booked. ROI break-even a 1 deal ogni 5 mesi per ACV $20k.

### Q: Posso skippare il dry-run?

Sì ma sconsigliato. Override esplicito: passa `--no-dry-run --confirm` ai script. Il dry-run preview è il check finale per beccare bug content-side prima di invio reale.

### Q: GDPR — devo davvero scrivere LIA per ogni campagna?

Sì. GDPR Recital 47 + Garante Italia richiedono LIA documentato pre-send (NON retroattivo). Il subagent genera template auto in `<memory>/lia_<campaign>.md` — tu compili campo "expected outcome" + sign-off, salvi.

### Q: Cosa succede se mailbox è in warmup <14d?

Pre-flight check BLOCKA bulk send. Warning chiaro + suggerimento "continua warmup tool 6 giorni più, re-run check". Override `--force-no-warmup-check` disponibile ma sconsigliato (reputation risk).

### Q: A/B test funziona davvero?

Sì se hai >30 lead per variant (60+ raccomandato). Subagent genera 2 subject + 2 body variants, SmartLead split-test 50/50. Reply rate variant winner deve battere baseline +25% relative O 5% absolute.

### Q: Come gestisce reply ambigui?

Hybrid rule-based (catch 70-80% case ovvi) + LLM fallback per ambigui (Claude Sonnet con prompt 5-class). Confidence threshold 0.85 — sotto → manual triage queue `<memory>/triage_queue.md`.

### Q: Posso usare con Lemlist/Instantly invece di SmartLead?

Sì in modalità CSV export (no API path nativo per Lemlist/Instantly). Discovery Q1 = "Lemlist" → output sequence JSON portable + CSV "ready for manual import".

### Q: HeyReach `{{first_name}}` non funziona?

Bug noto. HeyReach usa SINGLE-brace `{first_name}`, NON double. Subagent enforce single-brace + auto-fix `{{var}}` regex pre-UpdateSequence (testato 27/04/2026 da Filippo, fixato in produzione su 6 campagne). Vedi `references/api-recipes.md` HeyReach section.

## Troubleshooting

### "MCP server not detected"

```bash
# Check ~/.claude.json + .claude/settings.local.json mention server
grep -l smartlead ~/.claude.json .claude/settings*.json

# Re-add if missing — see Anthropic MCP docs
claude --add-mcp smartlead
```

### "DMARC policy is none"

DMARC `p=none` = monitoring only. Update DNS:

```
_dmarc.yourdomain.com TXT "v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@yourdomain.com"
```

Dopo 24-48h re-run `deliverability_precheck.py`.

### "Mailbox warmup <14d, BLOCKED"

Continua warmup tool (Smartsenders/Lemwarm) per altri X giorni. NON forzare `--force-no-warmup-check` — rischio domain reputation tank irreversibile.

### "Italy Garante GDPR uncertainty"

Italy Garante è restrittivo per **B2C** (email personal libero/gmail). Per **B2B professional contacts** (work email) legitimate interest valido se LIA solido + opt-out attivo + footer bilingue. Vedi `references/gdpr-outbound-eu.md` sezione Italy specifics.

### "Reply rate sotto 1%"

Diagnostic checklist:
1. Data quality: lead enriched + verified (>0.80 confidence)? Re-run `/lead-finder-pro` con waterfall completo
2. Signal recency: <30d? Older signals = decay reply rate
3. Anti-LLM-detection: scan first-line per banned markers
4. Deliverability: Postmaster spam rate <0.1%?
5. ICP focus: troppo broad? Restringi segmentation

### "HeyReach campagna FINISHED, voglio editarla"

Trick: `Resume` → `Pause` → `UpdateSequence` (testato `references/api-recipes.md`). Resume da FINISHED non riavvia invii (no pending lead), serve solo per scongelare stato.

## Anti-pattern (cosa l'agent NON fa)

1. Mai bulk send su domain non-warmup (>14d minimum)
2. Mai inviare a role-based (`info@`, `sales@`, `support@`, `noreply@`)
3. Mai skip suppression cross-stack (GDPR violation)
4. Mai overshoot daily limit (matrix age-aware)
5. Mai personalization templated senza signal-specific (anti-LLM-detection)
6. Mai batch >50 senza confirm + dry-run
7. Mai bypassare GDPR EU mode
8. Mai inviare email senza unsubscribe link
9. Mai sovrascrivere campagna esistente senza confirm
10. Mai conservare API key in config.md (env vars only)
11. Mai usare `{{var}}` su HeyReach (single-brace mandatory)
12. Mai inviare a Italy B2C personal email senza override esplicito

## Riferimenti

- `BUILD-BRIEF.md` — vincoli + requisiti coordinator
- `ARCHITECTURE.md` — design completo (14 sezioni)
- `DECISIONS.md` — 15 decisioni architectural (4 originali + 11 emergent)
- `research/research-summary.md` — 7 RQ research output (340 righe)
- `discovery/questions.md` — 8 domande discovery
- `skills/<skill>/SKILL.md` — 5 skills companion
- `references/<topic>.md` — 6 references docs
- `scripts/<script>.py` — 6 scripts Python + requirements

Skill v1 base (NON modificare): `<pack-root>/skills/webinar-2/outbound-campaign/SKILL.md` — kept in pack v1, /outbound-orchestrator espande con angolo action-driven.

## Crediti

Subagent del Pack v2 Learnn — Claude Week (mag 2026). Worker chat #4. Stack: SmartLead + HeyReach + Attio + Claude orchestration. Pattern source: `/lead-finder-pro` (worker chat #1 validated).
