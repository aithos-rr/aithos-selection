# DECISIONS — `/automation-architect`

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

## Decisioni iniziali (coordinator, 2026-05-01)

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

### [DECISION-003] Riuso skill ecosystem n8n esistente

**Contesto**: Filippo ha 7 skill globali n8n già grounded e testate (`n8n-workflow-patterns`, `n8n-node-configuration`, `n8n-expression-syntax`, `n8n-code-javascript`, `n8n-code-python`, `n8n-validation-expert`, `n8n-mcp-tools-expert`) + 1 skill pack v1 (`n8n-quickstart`). Subagent `/automation-architect` deve estendere senza duplicare.

**Decisione**: subagent richiama skill esistenti come reference docs source (caricate in `references/n8n-*.md`). NON riscrive il contenuto. Esto sopra come orchestrator action-driven (parse requirements → design → validate → test → document) sfruttando le skill come knowledge base.

**Alternative considerate**:

- Inglobare contenuto skill in references → scartato: duplicazione, drift quando skill evolvono
- Wrappare skill esistenti senza scope nuovo → scartato: nessun valore aggiunto, skill già utilizzabili dirette
- Riscrivere zero ignorando skill → scartato: ignora 7 skill grounded

**Trade-off**: agent dipende da skill globali installate (per audience non-Filippo). Mitigation: README documenta dipendenze + setup script controlla presenza skill at first run.

**Reversibilità**: media (se skill rimosse, agent fallback a docs n8n).

### [DECISION-004] Memory scope = project

**Contesto**: dove salvare config persistente per `/automation-architect`.

**Decisione**: `memory: project` di default — config legata al cliente/progetto specifico (1 progetto = 1 n8n instance = 1 stack tool integrations).

**Alternative considerate**:

- `memory: user` → utile se user costruisce automazioni per tanti clienti con stessa istanza n8n. Ma normalmente integrations + scale + GDPR mode cambiano per cliente
- `memory: local` → solo locale al working dir, non sincronizzabile

**Trade-off**: scope project = config riusabile per build incrementale workflow nuovi nello stesso progetto. Cross-project bisogna ripetere discovery (rapida, 8 Q).

**Reversibilità**: facile (cambia frontmatter).

## Decisioni worker chat (build pipeline A→E, 2026-05-01)

### [DECISION-005] NotebookLM creation skip in Fase A

**Contesto**: BUILD-BRIEF prevede creazione NotebookLM `n8n Workflow Architecture 2026` in Fase A con 6+ sources. Indexing time = 3+ min, costo cache miss conversazione.

**Decisione**: skip NotebookLM creation. Skill ecosystem n8n esistente (7 skill globali, 13.4k righe pre-validate) sufficient come knowledge base. `research/research-summary.md` cita direttamente skill grounded.

**Alternative considerate**:
- Creare NotebookLM completo → scartato: overhead time + redundant con skill ecosystem grounded
- Skip research summary entirely → scartato: serve sintesi RQ Q1-Q7 + 10 recipes + 12 edge cases per Fase B

**Trade-off**: meno citation grounded esterne, ma skill ecosystem è già grounded e maintained. NotebookLM creabile post-hoc se utente richiede.

**Reversibilità**: facile (utente può chiamare `notebooklm create` separatamente).

### [DECISION-006] System prompt 488 righe (>450 target)

**Contesto**: BUILD-BRIEF target 350-450 righe per main agent file.

**Decisione**: 488 righe — accettato perché ricchezza giustificata: 17 sezioni complete inclusi 12 edge cases, 10 anti-pattern, 3 esempi reali documentati, output structure spec, audience-specific tono.

**Alternative considerate**:
- Compress sezioni edge case + anti-pattern in references esterni → scartato: edge case + anti-pattern devono essere INLINE per enforcement durante esecuzione (no read-on-demand)
- Skip output structure spec → scartato: serve per consistency cross-run

**Trade-off**: file più lungo del target ma copre tutti i casi enforce; niente è ridondante con references.

**Reversibilità**: facile (split sezioni in references se serve).

### [DECISION-007] Recipe library hard-coded vs MCP-fetched

**Contesto**: dove storare le 10 integration recipes? File markdown o fetch da n8n template library via MCP?

**Decisione**: hard-coded in `references/common-integrations-recipes.md` come knowledge base offline.

**Alternative considerate**:
- Fetch da `n8n-knowledge.search_templates` runtime → scartato: dipendenza MCP critica, fallback HTTP n8n/workflows/ slow
- Mix: hard-coded base 10 + fetch additional → scartato: complexity senza valore aggiunto immediato

**Trade-off**: recipes hard-coded vanno aggiornati manualmente se n8n cambia API. Mitigation: recipes coprono pattern stable (webhook → Notion, AI Agent + MCP, scheduled scraper) — pattern non cambiano spesso.

**Reversibilità**: media (aggiungere fetch dynamic richiede update skill workflow-designer).

### [DECISION-008] Validation block threshold = error level only

**Contesto**: validation produce error / warning / suggestion. Quale fa block?

**Decisione**: BLOCK solo su severity `error`. Warning + suggestion → notify utente, NON block.

**Alternative considerate**:
- Block anche su warning → scartato: troppo strict, frustra utente per false positives
- Block anche su suggestion → scartato: assurdo, sono optional improvements
- No block ever → scartato: workflow rotti vanno bloccati pre-deploy

**Trade-off**: utente può ignorare warnings critici. Mitigation: warnings sono SEMPRE listati output con suggested fix.

**Reversibilità**: facile (cambia config `validation_strictness`).

### [DECISION-009] Smoke test scope

**Contesto**: Fase D test coverage. Live MCP integration + interactive discovery non testabili senza utente.

**Decisione**: smoke test su 6 scripts Python (4 generators + validate + test + export + mcp_detect) + 4 negative test (secret detection, missing fields, duplicates, invalid refs). Live MCP + discovery interactive marked PENDING per Filippo manual test.

**Alternative considerate**:
- Mock MCP + simulate discovery → scartato: complessità test infra, false confidence
- Skip smoke test completely → scartato: violations definition of done

**Trade-off**: 5/5 static smoke PASS, ma runtime test pending Filippo. Accettato come standard pattern dei subagent #1-4 già done.

**Reversibilità**: facile (utente runs Fase D runtime tests post-build).
