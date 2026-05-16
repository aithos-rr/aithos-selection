# Discovery Questionnaire — `/outbound-orchestrator`

> 8 domande sequenziali via `AskUserQuestion`. Eseguite SOLO al first run (se `<memory>/config.md` non esiste). Ogni domanda ha `header` ≤12 char, 2-4 options + "Other" auto-aggiunta dal harness.
>
> **Output**: salva risposte in `<memory>/config.md` (schema in `ARCHITECTURE.md` sez 6).
>
> **Tempo target**: 2-3 minuti onboarding totale.

## Q1 — Tool outbound primary

**Header chip**: `Outbound`

**Question (italiano)**:
> Quale tool email outbound usi (o vuoi usare)?

**Options**:
- **SmartLead** — Best for API-heavy + raw volume + native warmup. Default raccomandato.
- **Lemlist** — Best for multichannel native + creative. Premium per-seat.
- **Instantly** — Best for AI Reply Agent + flat-fee scaling.
- **Manuale** — No tool API, output CSV + invio manuale.

**Save in config**: `stack.outbound_primary` ∈ {smartlead, lemlist, instantly, manual}

**Conseguenza logica**:
- `smartlead` → carica `references/api-recipes.md` SmartLead section, attiva MCP path `mcp__smartlead__*`
- `lemlist` o `instantly` → warning "MCP non disponibile in env attuale, output CSV", carica fallback path
- `manual` → skip API path, sempre CSV export

---

## Q2 — Tool outbound secondary (LinkedIn)

**Header chip**: `LinkedIn`

**Question (italiano)**:
> Vuoi includere LinkedIn outreach (multi-channel)?

**Options**:
- **HeyReach** — Best LinkedIn outreach, native MCP. Default raccomandato se multi-channel.
- **Lemlist multichannel** — Già copre LinkedIn se Q1 = Lemlist.
- **Solo email** — No LinkedIn, sequenza email-only.

**Save in config**: `stack.outbound_secondary` ∈ {heyreach, lemlist_multi, none}

**Conseguenza logica**:
- `heyreach` → carica `references/api-recipes.md` HeyReach section, attiva MCP path `mcp__heyreach__*`, force `multi_channel=true`
- `lemlist_multi` → solo se Q1 era Lemlist (consistency check)
- `none` → `multi_channel=false`, skip LinkedIn step in sequence builder

---

## Q3 — Brand voice

**Header chip**: `ToV`

**Question (italiano)**:
> Quale tone of voice usi per outreach?

**Options**:
- **Direct/concise** — diretto, no fronzoli, 80 word max.
- **Friendly/casual** — amichevole, conversazionale, emoji ok.
- **Educational/expert** — autorità industry, dato/insight first.
- **Bold/provocative** — provocatorio, contrarian view, hook forte.

**Save in config**: `brand.voice` ∈ {direct, friendly, educational, bold}

**Conseguenza logica**:
- Adatta `personalization-engine` skill prompt: voice descriptor + banned markers per voice
- `direct` → output 60-80 word
- `friendly` → output 100-130 word, può usare 1-2 emoji (no spam)
- `educational` → opening con dato concreto + statistic
- `bold` → opening con contrarian claim, attenzione anti-LLM-detection più stretta

---

## Q4 — Value proposition

**Header chip**: `ValueProp`

**Question (italiano)**:
> In 1-2 frasi: qual è la tua value proposition?

**Options**: (free text — passa "Other" sempre, multiSelect=false)

Esempi suggeriti nel placeholder:
- "GTM Engineering audit gratuito per SaaS B2B post-Series A"
- "Corso n8n + AI agents per founder solo-dev"
- "Done-for-you cold email infrastructure setup"

**Save in config**: `brand.value_prop` (string, max 250 char)

**Conseguenza logica**:
- Input mandatory per `personalization-engine` first-line generation
- Validation lunghezza: <50 char → warning "value prop troppo generica, riformulala"
- >250 char → truncate suggerito

---

## Q5 — Sequence length

**Header chip**: `SeqLen`

**Question (italiano)**:
> Quanti step vuoi nella sequenza outbound default?

**Options**:
- **3 step** — short SMB sequence (14 giorni). Reply rate baseline 5-7%.
- **5 step** — mid-market sweet spot (21-30 giorni). **Default raccomandato**, reply rate 8-12%.
- **7 step** — enterprise complex sale (45-60 giorni). Reply rate 12-18% se ben fatta.
- **Custom** — user-defined.

**Save in config**: `sequence.default_length` ∈ {3, 5, 7, custom}

**Conseguenza logica**:
- Carica template structure corrispondente da `references/sequence-templates.md` (Template A/B/C/D)
- `custom` → ulteriore prompt per definire steps
- Sotto step 5 + multi-channel = warning "sequenza corta + multi-channel funziona meno bene"

---

## Q6 — ICP description

**Header chip**: `ICP`

**Question (italiano)**:
> Descrivi il tuo ICP: settore + dimensione + geografia (free text)

**Options**: free text

Esempi:
- "SaaS B2B 10-50 employee, USA + EU"
- "Marketing agency Italia + UK, 5-30 dipendenti"
- "FinTech early-stage USA, Series A-B"

**Save in config**: `icp.description` (string)

**Conseguenza logica**:
- Auto-detect EU keyword (`EU`, `Europa`, `Italia`, `EMEA`, `Italy`, `France`, `Germany`, `Spain`, ...) → set `gdpr.mode_active = true`, warning "🇪🇺 GDPR mode attivo, footer bilingue obbligatorio"
- Save `icp.geo_eu_detected` per cross-validation con lead-finder-pro output
- Input per `personalization-engine` industry-context prompt

---

## Q7 — A/B test on/off

**Header chip**: `ABTest`

**Question (italiano)**:
> Vuoi attivare A/B test su subject + first-line?

**Options**:
- **On (subject + first-line)** — genera 2 variants per ogni step. Min 30 lead per variant per significance.
- **Off** — single variant, più semplice ma no learning loop.

**Save in config**: `sequence.ab_test_enabled` ∈ {true, false}

**Conseguenza logica**:
- `true` → `sequence-builder` skill produce 2× variants, `smartlead_upload.py` setta `is_split_test: true` su API call
- `false` → single variant
- Warning se lista <60 lead totale (under-sample per A/B)

---

## Q8 — GDPR mode

**Header chip**: `GDPR`

**Question (italiano)**:
> Modalità GDPR/privacy?

**Options**:
- **Auto-detect EU** — basato su Q6 ICP. Default raccomandato.
- **Always on** — sempre footer bilingue + LIA + suppression cross-stack, anche per lead non-EU.
- **Off** — solo CAN-SPAM US footer (lead solo-USA).

**Save in config**: `gdpr.mode` ∈ {auto, always, off}

**Conseguenza logica**:
- `auto` → `gdpr.mode_active` derivato da `icp.geo_eu_detected`
- `always` → `gdpr.mode_active = true` hardcoded
- `off` → solo se `icp.geo_eu_detected = false` (consistency check), altrimenti reject "EU detected, GDPR cannot be off"
- Activate skill `gdpr-opt-out` come gate pre-execute

---

## Output discovery — config summary template

```text
✅ Config salvata. Riepilogo:
- Outbound primary: <stack.outbound_primary>
- LinkedIn: <stack.outbound_secondary>
- Brand voice: <brand.voice>
- Value prop: <brand.value_prop>
- Sequenza default: <sequence.default_length> step
- ICP: <icp.description> → <gdpr_mode_indicator>
- A/B test: <sequence.ab_test_enabled>
- GDPR mode: <gdpr.mode> (active=<gdpr.mode_active>)
- Tool disponibili: <mcp_summary>
- Fallback attivi: <mcp_fallbacks>

Sono pronto. Dammi il tuo input lead (CSV path da /lead-finder-pro / lista paste / Sheet URL).
```

## Reconfigure trigger

Se utente dice `reconfigure`, `voglio cambiare config`, `reset`, `cambio configurazione`, `nuovo cliente`:

1. Backup: `<memory>/config.md` → `<memory>/config_backup_<timestamp>.md`
2. Ripeti 8 domande con valori precedenti come hint default
3. Salva nuovo config + summary diff "rispetto a prima è cambiato: X, Y, Z"
