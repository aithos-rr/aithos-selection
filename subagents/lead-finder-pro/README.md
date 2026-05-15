# `/lead-finder-pro` — Subagent Claude Code per Lead Generation B2B

**Cosa fa**: trasforma una lista grezza di lead (CSV, Sheet, LinkedIn Sales Nav, export CRM) in lead arricchiti, scorati per priorità, segmentati e — se vuoi — sincronizzati nel tuo CRM. Tutto via Claude Code, in un singolo prompt.

**Per chi**: SDR, BDR, Marketing Manager, Founder, Freelancer GTM. Non serve essere developer — l'agente si auto-configura al primo run con 8 domande in italiano. Audience target: community Learnn e chi fa GTM con strumenti moderni (Hunter, Apollo, Attio, SmartLead, HeyReach).

**Cosa lo rende speciale (vs skill v1 `lead-enrichment`)**:

- **Discovery interattiva**: 8 domande al primo run, poi memoria persistente. L'agente impara il tuo stack (CRM, enrichment tool, ICP, volume) e adatta il workflow.
- **Multi-vendor waterfall enrichment**: Hunter MCP (primary, ha MCP nativo) → Apollo API → Clay/parallel-cli → manual SMTP. Coverage target 85%+.
- **GDPR-aware EU detection**: se il tuo ICP contiene paesi EU, attiva auto-mode GDPR (LIA template, Article 9 filtering, opt-out workflow).
- **ICP scoring 60/40 fit/behavior**: 3 template per industry (SaaS, Agency, eCommerce) con signal decay 50%/mese. Grade A/B/C/D fissi.
- **Conflict-flag policy**: se due provider restituiscono dati diversi per lo stesso lead, flag per review manuale. Mai auto-overwrite silente.
- **Manual-field protection**: se hai già verificato manualmente email/role/phone, l'agente NON sovrascrive.

## Installazione (3 step)

### Step 1 — Clone o copia la cartella subagent

```bash
# Se project-level (consigliato):
cp -r .claude/agents/lead-finder-pro /path/to/your/project/.claude/agents/

# Se user-level globale:
cp -r .claude/agents/lead-finder-pro ~/.claude/agents/
```

### Step 2 — Setup MCP server (Hunter raccomandato)

Aggiungi a `~/.claude.json` (user) o `.claude/mcp_settings.json` (project):

```json
{
  "mcpServers": {
    "hunter": {
      "transport": "http",
      "url": "https://mcp.hunter.io",
      "auth": {"type": "api_key", "value": "YOUR_HUNTER_API_KEY"}
    }
  }
}
```

Free tier Hunter: 25 search/mese + 50 verify/mese (sufficiente per testing). Premium da $49/mese.

Optional: Apollo (`APOLLO_API_KEY` in env), Attio MCP, Google-personal MCP.

### Step 3 — Install Python deps

```bash
cd .claude/agents/lead-finder-pro
pip install -r scripts/requirements.txt
```

Done. Lancia Claude Code, digita `/lead-finder-pro`, rispondi alle 8 domande discovery, sei pronto.

## Esempi reali (3 use case)

### Esempio 1 — Lead post-conferenza SaaStr

**Situazione**: hai partecipato a SaaStr 2026 e hai esportato una lista di 200 partecipanti con `Name + Company`. Vuoi capire chi sono davvero, quale email scrivere, e prioritizzarli per outreach.

**Prompt**:

```text
/lead-finder-pro

Arricchisci il file output/saastr_attendees.csv (200 lead). Voglio Sheet output
+ sync Hot in Attio.
```

**Cosa succede**:

1. L'agente carica config (già esiste dal first run)
2. Ingest CSV → dedup (198 unique)
3. Waterfall enrichment Hunter→Apollo→parallel-cli (94% coverage)
4. Email verification waterfall (188 verified ≥0.80, esclude catch-all+disposable)
5. Score template SaaS B2B 60/40 → 28 Hot, 65 Warm, 75 Cold, 20 Disqualified
6. Output Google Sheet "SaaStr Lead Run 2026-04-30" + sync 28 Hot in Attio
7. Report finale + cost stimato (~$9.20)

**Tempo totale**: ~5-8 min per 200 lead.

### Esempio 2 — Audit qualità CRM Attio

**Situazione**: hai 500 contatti in Attio CRM con il campo email vuoto. Vuoi arricchire e poi tornare a un CRM pulito.

**Prompt**:

```text
/lead-finder-pro

Audit Attio: prendi i contatti dove email è vuoto, arricchisci, e fai update_record
con email + role + score.
```

**Cosa succede**:

1. L'agente lista i contatti via `mcp__attio__list_records --filter "email is empty"`
2. Per ognuno: Hunter email-finder via name+company, Apollo fallback
3. Email verify waterfall
4. Score con template selezionato
5. `mcp__attio__update_record` su ognuno (NO create — già esistono)
6. Report: 425 contatti aggiornati, 75 falliti (suggerimenti manuale), ~$13 cost

### Esempio 3 — Sourcing prospect nuovi via LinkedIn Sales Nav

**Situazione**: vuoi 100 nuovi VP Marketing FinTech USA che hanno **cambiato lavoro negli ultimi 30 giorni** (signal di buying window).

**Prompt**:

```text
/lead-finder-pro

Cerca 100 VP Marketing FinTech USA via Sales Navigator, filtra job-change <30
giorni, arricchisci ed esporta CSV.
```

**Cosa succede**:

1. Skill `linkedin-safe-scraping` → Sales Nav search via Playwright (filters: VP+Marketing+FinTech+USA+years_at_company<2)
2. Extract 100 LinkedIn URL + headline (NO bulk profile visit, ToS-safe)
3. Waterfall enrichment via domain extraction → 93% coverage
4. Job-change signal → score boost +10 timing
5. Output CSV `output/leads_new_jobchange_<ts>.csv` (35 Hot, 50 Warm)
6. Disclaimer reminder LinkedIn limit: "Today extracted 100/100 Sales Nav, riprendi domani"

## FAQ

### Devo essere developer per usarlo?

**No**. Le 8 domande discovery sono in italiano, le rispondi cliccando opzioni o scrivendo testo libero. L'agente fa tutto il lavoro tecnico (API call, parsing, MCP wrap).

### Quanto costa girarlo?

Dipende dal volume e dai tool. Stima per audience freelance/founder:

- <50 lead/mese: $0-20 (Hunter free tier)
- 50-200 lead/mese: $50-150 (Hunter Premium + parallel-cli)
- 200-500 lead/mese: $150-400 (Hunter Premium + Apollo Basic)
- 500+ lead/mese: $400+ (full stack consolidato)

L'agente stampa il cost stimato dopo ogni run.

### Posso usarlo solo con Hunter senza Apollo?

**Sì**. Hunter da solo copre ~70% dei lead mid-market. L'agente farà fallback su `parallel-cli` (gratuito) e manual SMTP per i miss. Coverage target 85% può non essere raggiunto in nicchie specifiche — l'agente lo segnala con warning.

### GDPR è sicuro?

L'agente attiva auto-mode GDPR se rileva EU nel tuo ICP. Genera LIA template, applica filter Article 9, gestisce opt-out via Hunter Error 451 + suppression list. **Disclaimer**: è guida operativa, non parere legale. Per production, consulta DPO.

### Cosa succede se cambio config dopo?

Digita "reconfigure" o "voglio cambiare config". L'agente fa backup del config corrente, ripete le 8 domande con valori precedenti come default, salva il nuovo config.

### Il subagent funziona offline?

**No**. Richiede internet per Hunter/Apollo API + LinkedIn Sales Nav. Funziona in modalità degradata (manuale SMTP + parallel-cli) se Hunter+Apollo down.

### Posso integrarlo con SmartLead/HeyReach per outreach?

**Sì** — output CSV format compatibile import SmartLead/HeyReach. In futuro pack v2 conterrà `/outbound-orchestrator` che chain naturale dopo `/lead-finder-pro`.

### Come faccio il re-enrichment dopo 90 giorni?

Lancia di nuovo `/lead-finder-pro` sullo stesso CSV/JSON output del run precedente. L'agente detect `_enriched_at > 90 giorni` → applica signal decay 50%/mese, re-verifica email, controlla job-change → output con score aggiornato.

## Troubleshooting (5 problemi comuni)

### 1. "Hunter MCP not available"

**Causa**: Hunter MCP non configurato in `~/.claude.json` o `.claude/mcp_settings.json`.

**Fix**:

```bash
# Verifica:
python scripts/mcp_detect.py --check hunter

# Se False:
# Aggiungi la entry mcpServers come da Step 2 installazione
# Riavvia Claude Code
```

L'agente continua in fallback con Apollo API + parallel-cli.

### 2. "Coverage 65% — sotto 85% threshold"

**Causa**: nicchia ICP con coverage limitata (es. founder small company, geographies under-covered).

**Fix opzioni**:

- Accept come expected (la nicchia ha coverage limitata, è normale)
- Aggiungi Cognism per EMEA o ZoomInfo per enterprise
- Allarga ICP (più industries, più geo) e rifa il run

### 3. "Email verification fail rate alto"

**Causa**: probabilmente catch-all domain (server accept-all) o disposable inclusi nella lista input.

**Fix**:

- L'agente flagga catch-all con `confidence < 0.80` e suggerisce LinkedIn DM invece di email
- Per disposable: aggiungere domain a `<memory>/email_blocklist.md` e rifare run
- Verificare manuale i top 10 fallimenti per pattern

### 4. "GDPR mode false positive USA-only"

**Causa**: ICP description contiene parola che match keyword EU (es. "European market" ma in realtà USA-focused).

**Fix**:

- Discovery Q5 più specifica: "USA only, not EU"
- Oppure manualmente in `<memory>/config.md` set `gdpr.mode_active: false`

### 5. "Conflict tra Hunter e Apollo per email"

**Causa**: provider diversi, email diversa per stesso prospect (raro ma succede).

**Fix**:

- L'agente flagga `_conflicts: [...]` e marca lead `needs_review: true`
- Tu fai verifica manuale (LinkedIn DM, prova email, altro)
- Conferma quale è giusta + update CRM
- Per skip auto policy in futuro: `config.waterfall.conflict_policy: auto_first` (NON consigliato)

## Skills companion (5 skill incluse)

Quando lanci `/lead-finder-pro`, queste skills vengono auto-invocate:

- **`icp-scoring`**: scoring 0-100 con 3 template industry + decay 50%/mese
- **`email-verification`**: waterfall Hunter→Apollo→SMTP, threshold 0.80
- **`gdpr-compliance`**: LIA template, 8-point checklist, Article 9 filter
- **`waterfall-enrichment`**: orchestrazione multi-vendor con conflict-flag
- **`linkedin-safe-scraping`**: Sales Nav signal-based extraction

Ogni skill ha SKILL.md proprio in `skills/<name>/SKILL.md`.

## References docs (6 file)

In `references/`:

- `lead-enrichment-best-practices-2026.md` — 7 best practice + 14 edge case + 4 case study
- `tool-integrations.md` — Hunter MCP, Apollo, Clay, Cognism, ZoomInfo, Lusha details
- `gdpr-compliance.md` — LIA template, Article 9, opt-out workflow, retention
- `icp-scoring-framework.md` — 3 template + signal decay formula
- `prompt-patterns.md` — template per outreach Hot/Warm + LinkedIn DM
- `apollo-api-recipes.md` — recipe API people-search, organization-search, bulk_match

## Cosa NON fa (anti-pattern)

- ❌ Mai bulk send senza email verification
- ❌ Mai overwrite manual-verified fields
- ❌ Mai scrape Article 9 sensitive data
- ❌ Mai skip LIA su EU lead
- ❌ Mai auto-pick first vendor in conflict
- ❌ Mai bulk profile visit LinkedIn (ban risk)
- ❌ Mai mass connection request automated

## Crediti

Built da Filippo Greco (GTM Engineer @ Yellow Tech) per Claude Week Learnn — maggio 2026.

Skill v1 baseline: `skills/webinar-2/lead-enrichment/SKILL.md`. Estesa in v2 con discovery, scoring 3-template, GDPR auto, waterfall multi-tier, conflict-flag, manual-field protection.

Research grounding: NotebookLM `3b40733b-3fc1-4c63-8dfd-e2566a06fe37` — 8 fonti verificate 2026 (SyncGTM, Amplemarket, IntentDepth, Breadcrumbs, Apollo docs, Hunter API V2, GDPR Recital 47).

License: MIT. Contributi welcome via fork + PR.
