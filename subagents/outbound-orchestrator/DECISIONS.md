# DECISIONS — `/outbound-orchestrator`

> Append-only log di decisioni importanti (architectural, scope, trade-off). Immutable per default — non riscrivere, solo aggiungere.

## Format entry

```markdown
## YYYY-MM-DD HH:MM — [DECISION-N] Titolo decisione

**Contesto**: cosa stavamo affrontando
**Decisione**: cosa abbiamo scelto
**Alternative considerate**: cosa abbiamo scartato e perché
**Trade-off**: pro e contro
**Reversibilità**: facile/media/difficile
```

## Decisioni iniziali (coordinator, 2026-04-30)

### [DECISION-001] Pattern Auto-Onboarding

**Contesto**: serve che ogni subagent diventi specifico per ruolo/stack/output utente.

**Decisione**: discovery interattiva al first run via AskUserQuestion (8 domande), salvataggio config in `<memory>/config.md`, re-prime config su run successivi.

**Alternative considerate**:
- Config tramite ENV vars → scartato: troppo developer-oriented per audience Learnn
- Config statica file pre-compilato → scartato: friction alta
- CLI flag → scartato: utente non ricorda flag

**Trade-off**: 2-3 min onboarding al first run, ma agent diventa "tuo".

**Reversibilità**: facile (cambia config.md o "reconfigure").

### [DECISION-002] Naming inglese kebab-case

**Contesto**: scelta lingua nomi subagent/skill.

**Decisione**: nomi tecnici inglese (kebab-case), messaggi utente italiano.

**Alternative considerate**:
- Tutto italiano → scartato: incoerente con ecosistema Anthropic
- Prefisso `/yt-` → scartato: meno pulito

**Trade-off**: nomi inglese da ricordare, ma sono standard.

### [DECISION-003] Riuso skill v1 outbound-campaign come spunto

**Contesto**: la skill v1 `webinar-2/outbound-campaign` esiste e ha valore (sequence template + brand voice). `/outbound-orchestrator` raddoppia lo scope con angolo ACTION-driven (esegue invii reali via API).

**Decisione**: spunto pattern (sequence templates, brand voice) ma il subagent v2 va molto più in profondità: aggiunge personalization-engine AI, deliverability-check pre-flight, reply-classification 5-class, sequence-builder JSON per API, gdpr-opt-out cross-campaign suppression. Skill v1 resta in pack v1, non viene cancellata.

**Alternative considerate**:
- Riscrivere zero ignorando v1 → scartato: butto via lavoro fatto
- Wrappare skill v1 dentro subagent → scartato: scope mismatch (v1 è solo template, v2 è full pipeline action-driven)

**Trade-off**: alcuni concept della skill v1 ricompaiono (filosofia personalizzazione signal-driven). Coerenza brand.

### [DECISION-004] Memory scope = project

**Contesto**: dove salvare config persistente per `/outbound-orchestrator`.

**Decisione**: `memory: project` di default — config legata al cliente/progetto specifico (1 progetto = 1 brand voice = 1 ICP = 1 set di sequence template).

**Alternative considerate**:
- `memory: user` → utile se l'utente fa outbound per più clienti diversi con stesso stack. Ma normalmente brand voice/value prop cambiano per cliente
- `memory: local` → solo locale al working dir, non sincronizzabile

**Trade-off**: scope project = config riusabile per re-run incrementali (re-launch sequence per nuovi lead, A/B test variants). Cross-project bisogna ripetere discovery. Coverage migliore per use case tipico.

**Reversibilità**: facile (cambia frontmatter).

## Decisioni emergent (worker chat, 2026-04-30 — Fase A research + Fase B architecture)

### 2026-04-30 — [DECISION-005] Confirm step soglia 50 lead

**Contesto**: `/outbound-orchestrator` esegue invii REALI via API SmartLead/HeyReach. Rischio reale di spammare 500 email per errore (BUILD-BRIEF "vincoli spaventosi"). BUILD-BRIEF flagga decisione emergent.

**Decisione**: `safety.confirm_required_above: 50` lead. Sopra soglia → explicit "yes confirm" testuale richiesto pre-execute. Sotto soglia → procede dopo dry-run preview (output JSON sequence senza chiamata API). Dry-run sempre primo step di default per QUALSIASI batch (DECISION-014).

**Alternative considerate**:
- Sempre confirm anche sotto 50 → friction utente per lavori piccoli
- Mai confirm + dry-run mandatory → rischio escalation utente "dai click and go"
- Soglia 100 lead → troppo permissiva per il danno potenziale

**Trade-off**: 50 è arbitrario ma pragmatico (1 mailbox warmed cap). Configurabile via `<memory>/config.md` se utente vuole più conservativo (es. 20).

**Reversibilità**: facile (config field).

### 2026-04-30 — [DECISION-006] Multi-channel timing default email + LinkedIn

**Contesto**: research RQ1 indica multi-channel +40% engagement, ma timing è critico. BUILD-BRIEF flagga emergent.

**Decisione**:
- Day 0: Email step 1 (signal hook + soft CTA)
- Day 2: LinkedIn connection request + nota (mention same signal)
- Day 5: Email step 2 (value drop) — solo se NO reply email day 0
- Day 7: LinkedIn message #1 (post-acceptance) — solo se connection accepted
- Day 10: Email step 3 (social proof)
- Day 14: LinkedIn message #2 — opzionale
- Day 21: Email step 4 (break-up)

Pattern "widening gap" tra email step (2-3, 4-5, 7-10, 10-14 days).

**Alternative considerate**:
- LinkedIn day 0 stesso giorno email → percepito come "carpet bombing" da prospect, banned in best practice 2026
- Email-only senza LinkedIn → -40% engagement medio
- LinkedIn first poi email → minor reply rate (LinkedIn → email funnel meno efficace di reverse)

**Trade-off**: 21 giorni per chiusura = mid-market sweet spot. Enterprise può estendere a 45-60 giorni (template B). SMB short version (template C, 14 giorni) selezionabile via Q5.

**Reversibilità**: facile (config field `sequence.default_length` + custom timing in template).

### 2026-04-30 — [DECISION-007] API key handling env vars only

**Contesto**: storage API key è issue di sicurezza. BUILD-BRIEF flagga emergent.

**Decisione**: API key (`SMARTLEAD_API_KEY`, `HEYREACH_API_KEY`, `APOLLO_API_KEY` se used) lette **solo da env vars** (`~/.zshrc`). Mai salvate in `<memory>/config.md`. Solo flag presenza in config (`api_keys.smartlead_present: true`).

**Alternative considerate**:
- Salvataggio in config encrypted → over-engineering per audience non-developer
- Prompt at first run + storage plain → rischio leak in repo Git
- Solo env vars → friction setup ma security-first

**Trade-off**: utente deve setup `.zshrc` (5 min one-time). Subagent fa check at first run, prompt setup se mancanti.

**Reversibilità**: facile (env var change).

### 2026-04-30 — [DECISION-008] Daily cap matrix per mailbox age

**Contesto**: research RQ4 mostra che daily cap dipende da age mailbox + warmup status. BUILD-BRIEF prop default 50/warmed.

**Decisione**: matrix per age:
- 0-14d (cold): 5-10/day, BLOCK bulk send (warmup tool only)
- 14-30d (warming): 10-20/day, mixed warmup + small batch
- 30-90d (warmed): 30-50/day default
- 90d-6mo (aged): 80-150/day
- 6+mo (seasoned): 200-300/day max safe

Default subagent: `daily_cap_per_mailbox: 50` (warmed safe baseline). Matrix configurabile in `<memory>/config.md`.

**Alternative considerate**:
- Hardcoded 50 sempre → conservativo ma frustrante per seasoned mailbox
- No matrix, ask user → friction
- Auto-detect via SmartLead API mailbox age → ideale ma complica MVP

**Trade-off**: matrix conservativa per safety. Skill `deliverability-check` valida age via DNS lookup + warmup days config field.

**Reversibilità**: facile (config matrix).

### 2026-04-30 — [DECISION-009] NotebookLM skip in Fase A

**Contesto**: BUILD-BRIEF prevede NotebookLM creation per research. 3-5 min indexing × N domande = troppo tempo in sessione live worker chat.

**Decisione**: skip NotebookLM dedicato. Research consolidata via WebSearch (8 query) + parallel-cli search (2 query) + skill `heyreach-api` esistente (testata da Filippo 27/04/2026 = grounded).

**Alternative considerate**:
- Crea notebook + aspetta indexing parallelo a Fase B/C → context switching costoso, pattern non testato
- Crea notebook offline poi prosegui → richiede Filippo manual step
- Salta NotebookLM → coverage research forse meno rigorosa ma sufficiente per saturare 7 RQ

**Trade-off**: research-summary potrebbe avere gap rispetto a NotebookLM (non grounded con citazioni esatte). Compensato da fonti dirette WebFetch + parallel-cli.

**Reversibilità**: media — Filippo può creare notebook post-build per audit qualità.

### 2026-04-30 — [DECISION-010] Sequence widening gap default

**Contesto**: research RQ1 mostra modello "widening gap" supera modello "daily bump" per Gmail/Outlook detection.

**Decisione**: timing default sequenze:
- Step 1 → 2: 2-3 giorni
- Step 2 → 3: 4-5 giorni
- Step 3 → 4: 7-10 giorni
- Step 4 → 5+ (break-up): 10-14 giorni

Hardcoded in `references/sequence-templates.md` per i 4 template (A/B/C/D). Configurabile in custom.

**Alternative considerate**:
- Daily bump 1d/2d/3d → bandito da Gmail trasformer 2026
- Fixed gap 5d → meno human-like, comunque ok ma sub-optimal
- Random gap 2-7d uniform → noisy, non corrisponde a research

**Trade-off**: timing più lungo = sequenza chiusa in 21+ giorni vs 10. Ma reply rate +40% medio.

**Reversibilità**: facile (template per template editabile).

### 2026-04-30 — [DECISION-011] Anti-LLM-detection mandatory

**Contesto**: research RQ5 mostra Gmail/Outlook trasformer detection per pattern templated. 69% decision-maker bothered by AI-generated email evidente.

**Decisione**: skill `personalization-engine` enforce anti-LLM rules:
- 8 banned markers stilistici (`delve into`, `navigate the landscape`, `I hope this email finds you well`, em-dash multipli `—`, `leverage`, `synergy`, `seamlessly`, `cutting-edge`)
- 3+ variant per template, random selection
- Constraint prompt: 15-25 word max per first-line, signal-specific
- First-line uniqueness hash check su last 100 generate
- Output review: secondo LLM call "rendi più conversazionale max 25 parole"

**Alternative considerate**:
- Skip anti-detection → reply rate -50% (research evidence)
- Manual review only → non scala oltre 50 lead
- Banned markers list più lunga → diminishing returns + over-restrictive

**Trade-off**: complessità prompt + 2 LLM call per first-line = costo +30% LLM credit. Compensato da reply rate +5x.

**Reversibilità**: facile (banned list + variant count config).

### 2026-04-30 — [DECISION-012] Reply classification 5-class hybrid

**Contesto**: research RQ6 + BUILD-BRIEF prop 5-class taxonomy.

**Decisione**: `reply_classify.py` hybrid:
1. Rule-based pre-filter (regex + DSN headers) catch 70-80% case ovvi
2. LLM fallback per ambigui: prompt "Classify reply as positive|negative|OOO|unsubscribe|bounce"
3. Confidence threshold 0.85: auto-action sopra, manual triage queue sotto

5 classi: `positive`, `negative`, `OOO`, `unsubscribe`, `bounce`. Mapping esteso a SmartLead lead categories: positive→Interested, negative→Not-Interested, OOO→Out-of-Office, unsubscribe→Do-Not-Contact, bounce→suppress.

**Alternative considerate**:
- LLM-only (no rule-based) → costo + slow
- Rule-based only → miss nuance positive/negative ambigui
- 7+ classi (Apollo style) → over-engineering, non mappa a SmartLead

**Trade-off**: hybrid bilancia costo/qualità. Manual triage queue accettabile per <5% reply.

**Reversibilità**: facile (threshold + class taxonomy).

### 2026-04-30 — [DECISION-013] GDPR Italy B2B legitimate interest

**Contesto**: research RQ7 + DLA Piper update Italia luglio 2025 (double opt-in B2C trend). Filippo opera Italia + EU + USA mix.

**Decisione**: GDPR EU outbound `/outbound-orchestrator` supporta B2B legitimate interest path:
- LIA documentato pre-send (template in `references/gdpr-outbound-eu.md`)
- Footer bilingue IT+EN se EU detected
- Suppression list cross-stack (SmartLead + HeyReach + CRM)
- Retention 12 mesi post-contact
- B2C **fuori scope** (skill `gdpr-opt-out` reject lead con email gmail/yahoo/hotmail/libero/personal)

Italy specifics: Garante FAQ + Provv. n. 230/2020 confermano B2B professional contacts via legitimate interest valid se LIA solido + opt-out attivo.

**Alternative considerate**:
- Double opt-in mandatory per tutto EU → over-restrictive per B2B (spegne use case)
- No GDPR mode → illegale per EU lead, danno reputazionale + sanzione
- Auto-detect EU + warning → balanced, pragmatic

**Trade-off**: alcuni lead B2B "borderline" (es. founder con email personale gmail) potrebbero essere skippati per safety. Filippo può override esplicitamente in `<memory>/config.md` `gdpr.b2c_override: true`.

**Reversibilità**: facile (skill config + suppression list editing).

### 2026-04-30 — [DECISION-014] Dry-run mandatory primo run

**Contesto**: rischio invio reale alto (vincolo BUILD-BRIEF). Confirm step (DECISION-005) gestisce volume >50, ma anche batch piccoli possono nuocere se sequence rotta.

**Decisione**: prima esecuzione di QUALSIASI campagna è **dry-run obbligatorio**: `--dry-run` flag default, output JSON sequence salvato in `output/dry_run_<timestamp>.json` + report markdown con preview 3 sequence sample. Utente review e dice "execute" per chiamata API reale. Override esplicito utente: `--no-dry-run` (bypass solo se utente lo chiede testualmente).

**Alternative considerate**:
- Dry-run on demand → utente skippa, errori passano in produzione
- Dry-run sempre + auto-execute dopo 5min idle → automation insidiosa
- Confirm verbale solo → meno safe, no preview tangibile

**Trade-off**: extra step = +1 min per campagna. Beneficio: zero invii catastrofici.

**Reversibilità**: facile (flag default).

### 2026-04-30 — [DECISION-015] Output schema sequence JSON portable

**Contesto**: `/outbound-orchestrator` deve produrre sequence definition portabile (SmartLead/HeyReach diversi schema).

**Decisione**: schema JSON intermedio `output/sequence_<campaign_name>_<timestamp>.json` neutro:

```json
{
  "campaign_name": "...",
  "sequence_name": "...",
  "channels": ["email", "linkedin"],
  "steps": [
    {
      "step_n": 1,
      "channel": "email",
      "delay_days": 0,
      "subject_variants": ["..."],
      "body_variants": ["..."],
      "signal_used": "job_change",
      "send_window": "tue_thu_9_13"
    },
    ...
  ],
  "leads": [...],
  "ab_test": true,
  "gdpr_footer_html": "...",
  "_meta": {...}
}
```

Da questo, `smartlead_upload.py` e `heyreach_upload.py` traducono in payload tool-specific. Re-processable, dry-run friendly.

**Alternative considerate**:
- Direct payload SmartLead → vendor lock-in, no portability
- YAML al posto di JSON → meno standard per API call
- DSL custom → over-engineering

**Trade-off**: 1 livello indirezione = leggera duplicazione code. Beneficio: dry-run + multi-vendor + audit trail.

**Reversibilità**: facile (schema editabile).
