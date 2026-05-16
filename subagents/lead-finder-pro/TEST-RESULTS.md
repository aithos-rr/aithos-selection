# TEST-RESULTS — `/lead-finder-pro`

> Output Fase D. Verification statica eseguita dalla worker chat (sessione 1, 2026-04-30). I 7 test runtime del BUILD-BRIEF richiedono Claude Code session vera con MCP attivi → documentati come "manual run checklist" per Filippo.

## Sezione 1 — Verification statica (PASS/FAIL eseguita ora)

### 1.1 Struttura cartelle

✅ PASS — `find . -type f` ha mostrato:

- 1 main agent `lead-finder-pro.md`
- 5 SKILL.md in `skills/`
- 6 references in `references/`
- 6 scripts + `requirements.txt` in `scripts/`
- 1 README.md
- 1 ARCHITECTURE.md
- 1 `discovery/questions.md`
- 1 `research/research-summary.md` + 7 raw notebooklm output
- 3 fixture in `test-fixtures/` (leads-20.csv, leads-edge.csv, leads-eu-3.csv)

Total: 33 file rilevanti.

### 1.2 Frontmatter validation

✅ PASS — Script Python ha validato:

- 5/5 SKILL.md con frontmatter valido (`name`, `description`, `when_to_use`, `allowed-tools`)
- Description range 383-481 char (sotto 1024 limit)
- desc+when_to_use range 539-685 char (sotto 1536 limit)
- Tutti `name` lowercase-kebab-case, no underscores

Main agent `lead-finder-pro.md`:

- `name: lead-finder-pro` ✅
- `description: 445 char` (sotto 1024) ✅
- `when_to_use: 292 char` (combined 737, sotto 1536) ✅
- `tools: Read, Write, Edit, Bash, WebFetch, WebSearch, AskUserQuestion` ✅
- `mcpServers: 7 server` ✅
- `skills: 5 skill` ✅
- `memory: project` (DECISION-004) ✅
- `model: sonnet` (DECISION-012) ✅
- `color: orange` ✅

### 1.3 Cross-reference integrity

✅ PASS — Tutti i link interni validati:

- 8 skills → references link OK (no broken)
- 5 skills folders esistono
- 6 references files esistono
- 6 scripts files esistono

### 1.4 Scripts smoke test

✅ PASS — Tutti i 6 scripts rispondono a `--help`:

- `discovery_check.py --help` → usage stampato OK
- `mcp_detect.py --help` → usage stampato OK
- `apollo_search.py --help` → usage stampato OK (richiede `requests` deps)
- `email_verify_waterfall.py --help` → usage stampato OK
- `csv_to_sheet.py --help` → usage stampato OK
- `attio_sync.py --help` → usage stampato OK

Eseguiti con fixture reali:

- `discovery_check.py --memory-path memory/config.md` → `{"exists": false}` correct (no config yet)
- `mcp_detect.py` → output JSON con stato 7 server (Hunter unavailable in test env, altri 6 disponibili user-scope)
- `csv_to_sheet.py --input-csv test-fixtures/leads-20.csv --create-with-name "Test Run"` → payload JSON corretto generato

### 1.5 Quantitative metrics (vs BUILD-BRIEF target)

| Target | Actual | Status |
|--------|--------|--------|
| System prompt 300-500 righe | **408** | ✅ in range |
| 5 skills companion | **5** | ✅ |
| 6 references docs | **6** | ✅ |
| 3+ esempi reali | **3** in main + 3 in README | ✅ |
| research-summary >2000 parole | **2976** | ✅ |
| Discovery 6-8 domande | **8** | ✅ |
| MCP detection + fallback | **7 server + fallback documentati** | ✅ |
| Memory persistente | `memory: project` | ✅ |
| Italiano UX, inglese tech | confermato | ✅ |
| ARCHITECTURE.md | **420 righe** | ✅ |
| README.md user-friendly | **269 righe**, 5 FAQ + 5 troubleshooting | ✅ |

### 1.6 Decisioni tracciate

✅ PASS — `DECISIONS.md` contiene 12 decisioni (4 originali coordinator + 8 emergent dalla research):

- DECISION-001/002/003/004 (coordinator originali)
- DECISION-005 Hunter MCP primary
- DECISION-006 Skills weighting 60/40 default + 3 template
- DECISION-007 Signal decay 50%/mese
- DECISION-008 Coverage threshold 85%
- DECISION-009 Conflict-resolution = flag
- DECISION-010 Manual-field protection
- DECISION-011 EU auto-load GDPR
- DECISION-012 Sonnet model

## Sezione 2 — 7 test runtime (manual checklist per Filippo)

Questi test richiedono Claude Code session reale con `/lead-finder-pro` invocabile + MCP setup. Non eseguibili da worker chat in plan/build mode.

### Test 1 — Discovery flow end-to-end

**Setup**: progetto pulito SENZA `<memory>/config.md`.

**Esecuzione**:

```bash
cd /path/to/test-project
claude
> /lead-finder-pro
```

**Pass criteria**:

- [ ] L'agente mostra benvenuto e dice "Config non trovata, eseguo discovery"
- [ ] Mostra 8 AskUserQuestion sequenziali (Q1-Q8)
- [ ] Salvataggio `<memory>/config.md` con tutti i field popolati
- [ ] Conferma summary in italiano con riepilogo stack + ICP + GDPR mode

### Test 2 — Re-run skip discovery

**Setup**: stessa dir di Test 1, config.md ora presente.

**Esecuzione**:

```bash
> /lead-finder-pro
```

**Pass criteria**:

- [ ] NESSUNA AskUserQuestion mostrata
- [ ] Conferma "Config trovata, sono pronto. Riepilogo: ..."
- [ ] Aspetta input lead

### Test 3 — Real task small (20 lead)

**Setup**: config presente, fixture `test-fixtures/leads-20.csv` copiato in dir progetto.

**Esecuzione**:

```bash
> /lead-finder-pro
> Arricchisci il file leads-20.csv (20 lead).
```

**Pass criteria**:

- [ ] Output Sheet o CSV con 17-18 colonne (16 lead unique dopo dedup approssimativo)
- [ ] Score+grade per ognuno
- [ ] Email verified ≥0.80 sui non-disposable/non-role
- [ ] Report finale con distribution Hot/Warm/Cold/Disqualified
- [ ] Cost stimato stampato

### Test 4 — MCP fallback

**Setup**: rinomina temporaneamente `attio-mcp` config (oppure rimuovi entry da `~/.claude.json`).

**Esecuzione**:

```bash
> /lead-finder-pro
> Audit qualità Attio CRM
```

**Pass criteria**:

- [ ] Warning visibile: "Attio non disponibile, output solo CSV"
- [ ] Continua flow senza crash
- [ ] Output CSV locale `output/leads_<ts>.csv`
- [ ] Dopo: ripristina config Attio

### Test 5 — Reconfigure trigger

**Setup**: config presente.

**Esecuzione**:

```bash
> /lead-finder-pro
> reconfigure
```

**Pass criteria**:

- [ ] Backup config: `<memory>/config_backup_<ts>.md` creato
- [ ] Ripete 8 domande con valori precedenti come hint default
- [ ] Salva nuovo config

### Test 6 — Edge case duplicati + parziali

**Setup**: fixture `test-fixtures/leads-edge.csv` (10 row con 3 dup di Sara Bianchi, 1 senza nome, 1 senza company, 1 con email manuale, 1 role-based info@, 1 con email gibberish).

**Esecuzione**:

```bash
> /lead-finder-pro
> Arricchisci leads-edge.csv
```

**Pass criteria**:

- [ ] Dedup: Sara Bianchi count 1 (3 row → 1)
- [ ] Skip + warn lead senza nome (riga "")
- [ ] Skip + warn lead senza company
- [ ] Manual-field protection attivo: Marco Rossi NON sovrascrive `marco.manual@shopfast.it` + role "VP Sales"
- [ ] Role-based `info@datapipe.io` flagged + excluded da personalized
- [ ] Gibberish `xyz123@@@` → invalid syntax, skip
- [ ] Output finale: ~5-6 lead processati, log dettagliato

### Test 7 — GDPR EU auto-mode

**Setup**: ICP description in config contiene "EU" o "Europa". Fixture `test-fixtures/leads-eu-3.csv` (Pierre/Klaus/Maria, FR/DE/ES).

**Esecuzione**:

```bash
> /lead-finder-pro
> Arricchisci leads-eu-3.csv
```

**Pass criteria**:

- [ ] Warning all'avvio: "🇪🇺 GDPR mode attivo"
- [ ] Auto-load `references/gdpr-compliance.md`
- [ ] LIA template suggested se segment LIA mancante
- [ ] Output CSV ha campo `gdpr_status` per ogni lead (`compliant` se ok)
- [ ] 8-point checklist eseguita, report `<memory>/gdpr_check_<ts>.md` creato

## Sezione 3 — Fixtures disponibili

| File | Use case | Note |
|------|----------|------|
| `test-fixtures/leads-20.csv` | Test 3 small task | 20 lead `name + company` only |
| `test-fixtures/leads-edge.csv` | Test 6 edge case | 10 row con 3 dup, 1 manual-field protected, 1 role-based, 1 gibberish |
| `test-fixtures/leads-eu-3.csv` | Test 7 GDPR EU | 3 lead EU (FR/DE/ES) |

## Sezione 4 — Esito complessivo

| Categoria | Risultato |
|-----------|-----------|
| Verification statica (Sezione 1) | ✅ 6/6 PASS |
| 7 runtime test (Sezione 2) | ⏳ Pending Filippo manual run |
| Definition of Done BUILD-BRIEF | ✅ tutti i criteri statici raggiunti |

**Conclusione worker chat**: il subagent è build-complete e statically validated. Pronto per smoke test runtime di Filippo. Attiva la sessione Claude Code in un progetto pulito con MCP setup (Hunter raccomandato), poi esegui i 7 test della Sezione 2 in ordine. Se test failure → log issue in PROGRESS.md per fix loop.

## Sezione 5 — Known limitations / future v2 improvements

- **ML scoring layer**: v1 ha solo rules, ML behavior scoring è v2
- **Apify/PhantomBuster integration**: v1 LinkedIn solo via Playwright/Sales Nav, no third-party wrapper
- **Cognism MCP**: nessun MCP nativo per Cognism, solo via Apollo fallback
- **Auto re-enrichment scheduler**: v1 manuale, v2 con cron/agent recurring
- **Parallel batch**: v1 sequenziale, v2 con Agent Teams parallelizzazione per >500 lead
- **`output/` directory creation**: subagent crea on-demand, no `.gitignore` aggiunto (TODO Fase E)
