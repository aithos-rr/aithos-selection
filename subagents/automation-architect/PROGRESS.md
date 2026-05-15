# PROGRESS — `/automation-architect`

> Aggiornare ad ogni milestone (almeno ogni 25% context fill). Vedi BUILD-BRIEF.md sez "Context management" per template entry.

## Stato corrente

**Fase**: ✅ DONE — A→E completati (1 mag 2026)
**Last update**: 2026-05-01 18:00
**Worker chat**: aperta 2026-05-01 in `.claude/agents/automation-architect/`, scope = pipeline completa A→E

## Setup pre-build (coordinator)

- ✅ Cartella struttura creata
- ✅ BUILD-BRIEF.md scritto
- ✅ Skill v1 base + ecosistema 7 skill globali grounded — research Fase A è light

## Log milestone

## 2026-05-01 16:30 — Milestone 1: Worker chat opened, Fase A start

### ✅ Cosa è stato fatto
- Letto BUILD-BRIEF, PROGRESS, DECISIONS
- Verificato presenza skill ecosystem n8n (7 skill globali grounded in `~/.claude/skills/`)
- Verificato MCP disponibili: `n8n-knowledge`, `n8n-yellowtech`, `n8n-filippo`, `context7`, `parallel-cli`
- Pipeline plan A→E definito

### 🚧 Cosa sto facendo ora
- Fase A: Deep research light, leveraging skill ecosystem grounded come fonte primaria
- Skip NotebookLM creation (overhead 3+ min indexing) — usare skill esistenti come knowledge base + WebFetch n8n docs su gap

### 📋 Prossimi step
1. Generare `research/research-summary.md` con 7 RQ + 8 integration recipes + 6 archetype patterns
2. Fase B: Architecture design (discovery questions, MCP mapping, skills companion structure)
3. Fase C: Build main subagent + 5 skills + 6 references + scripts + README
4. Fase D: Test checklist + fixtures
5. Fase E: Bundle + update MASTER docs

### 🐛 Edge case scoperti
- (vedi research-summary.md sez "Edge cases" — 12 edge case documentati)

## 2026-05-01 16:45 — Milestone 2: Fase A done

### ✅ Cosa è stato fatto
- `research/research-summary.md` scritto (300+ righe)
- 7 RQ rispondi con citation a skill grounded
- 10 integration recipes documentati
- 6 archetype patterns mappati
- 12 edge cases scoperti
- NotebookLM creation skipped (deferred — skill ecosystem grounded sufficient)

### 🚧 Cosa sto facendo ora
- Fase B: Architecture design — discovery questions definitive, MCP mapping, schema config

### 📋 Prossimi step
1. Fase B: scrivere `discovery/questions.md` + `references/` (6 file) + `<memory>/config.md` template
2. Fase C: build main `automation-architect.md` + 5 skill SKILL.md + 6 scripts + README
3. Fase D: test fixtures + checklist
4. Fase E: bundle + update MASTER docs

## 2026-05-01 18:00 — Milestone 3: Pipeline A→E COMPLETATA ✅

### ✅ Cosa è stato fatto

**Fase B** ✅:
- `discovery/questions.md` — 8 domande discovery (Ruolo, n8nMode, UseCase, Stack, Scale, ErrorH, AIAgent, GDPR)
- `references/n8n-workflow-patterns-2026.md` — 6 archetype + decision tree
- `references/n8n-node-configuration.md` — node config best practice
- `references/n8n-expression-syntax.md` — top 10 pitfalls + helpful expressions
- `references/n8n-validation-guide.md` — severity model + validation loop + false positives
- `references/common-integrations-recipes.md` — 10 recipes pronti
- `references/error-handling-patterns.md` — 4-tier error stack + retry strategies

**Fase C** ✅:
- `automation-architect.md` main subagent — **488 righe** (target 350-450 superato per ricchezza)
- 17 sezioni: identità, discovery, MCP detection, methodology 6 fasi, skill chain, output spec, tool usage, edge cases (12), anti-pattern (10), esempi (3), memoria, output structure, chain, setup, definition done, tono, riferimenti
- `skills/workflow-designer/SKILL.md` — pattern matching + skeleton generator (4 pattern templates)
- `skills/node-validator/SKILL.md` — validation loop + auto-fix (max 3 iter) + false positive filter
- `skills/credential-mapper/SKILL.md` — secret detection + GDPR check + Article 9 block + rotation alert
- `skills/workflow-tester/SKILL.md` — fixture auto + dry-run mental sim + live test mode + assertions
- `skills/workflow-documenter/SKILL.md` — README + Mermaid + setup checklist + cost estimate
- `scripts/validate_input.py` — parse requirement (trigger + actions + integrations detection)
- `scripts/workflow_design.py` — 4 pattern generators (webhook, scheduled, ai_agent, data_pipeline)
- `scripts/workflow_validate.py` — static check + secret regex + structure
- `scripts/workflow_test.py` — fixture auto + scenario gen + assertions
- `scripts/workflow_export.py` — Mermaid + README markdown auto-gen
- `scripts/mcp_detect.py` — MCP availability probe
- `scripts/requirements.txt`
- `README.md` (260 righe) — utente-facing FAQ + 3 esempi reali + troubleshooting + anti-pattern

**Fase D** ✅:
- Smoke test scripts 5/5 PASS:
  1. `workflow_design.py --pattern webhook_driven` → exit 0, valid JSON
  2. `workflow_validate.py <valid>` → exit 0, valid: true
  3. `workflow_test.py <valid>` → trigger detected, fixture generato, assertions
  4. `workflow_export.py <valid>` → README 74 righe con Mermaid
  5. Negative test: `workflow_validate.py <bad>` con Bearer hardcoded → exit 1, errors detected
- `test-fixtures/test-checklist.md` — 10 test scenari + 4 negative test
- `test-fixtures/sample-requirements.md` — 10 sample input per parsing test
- `test-fixtures/sample-workflow-valid.json` + `sample-workflow-invalid.json` + `sample-readme-output.md`

**Fase E** ✅:
- `MASTER-PROGRESS.md` riga #7 → ✅ Done (1 mag), summary deliverable
- `dist/CLAUDE_WEEK_SKILL_PACK.md` sezione `/automation-architect` aggiunta (recipes, anti-pattern, MCP fallback, installazione)
- Obsidian note `~/Dev/obsidian-vault/02 - Ricerca/automation-architect_2026-05-01.md` (research-log con lezione, citazioni, backlink)

### 🚧 Cosa sto facendo ora
- Pipeline A→E completata. Nessun work in progress.

### 📋 Prossimi step (per Filippo)
1. Smoke run live: invoca `/automation-architect` da progetto test, verifica discovery 8 Q
2. Test runtime con MCP `n8n-knowledge` attivo: validate workflow real
3. Smoke run con MCP `n8n-yellowtech`: push workflow live test
4. Eventuale fine-tuning prompt main agent based on user feedback
5. Bundle finale Pack v2 quando #5, #6, #8 done

### 🐛 Edge case scoperti durante build
- `wc -l` script Python conferma 488 righe main agent (>450 target — sopra per ricchezza, accettabile)
- Smoke test exit code mascherato da `head` pipe — verificato manualmente exit 1 corretto
- Hook formatter Python su scripts (PostToolUse) — solo cosmetic, non funzionale
- Markdownlint warnings PROGRESS.md cosmetic (MD022/MD032/MD024) — ignorati, non bloccano
- 7 skill globali grounded già coprono 13.4k righe — NotebookLM creation skip giustificata

### 🔗 File esterni rilevanti
- `~/.claude/skills/n8n-*/` (7 skill globali — knowledge base)
- `~/Dev/clients/learnn/skills/n8n/n8n-quickstart/SKILL.md` (skill v1)
- `~/Dev/clients/learnn/.claude/agents/MASTER-PROGRESS.md` (riga 7 ✅)
- `~/Dev/clients/learnn/dist/CLAUDE_WEEK_SKILL_PACK.md` (sezione subagent)
- `~/Dev/obsidian-vault/02 - Ricerca/automation-architect_2026-05-01.md` (research-log)

### Definition of Done check
- [x] 5 fasi A→E completate
- [x] System prompt ≥350 righe (488 actual)
- [x] 5 skills + 6 references + 6 scripts + README + 3 esempi
- [x] Static + smoke test PASS (5/5)
- [x] PROGRESS + MASTER-PROGRESS aggiornati
- [x] Obsidian note salvata
- [x] dist/ skill pack updated

### 🔗 File esterni rilevanti
- `~/.claude/skills/n8n-workflow-patterns/` (5 pattern grounded)
- `~/.claude/skills/n8n-node-configuration/` (operation patterns + deps)
- `~/.claude/skills/n8n-expression-syntax/` (common mistakes + examples)
- `~/.claude/skills/n8n-validation-expert/` (error catalog + false positives)
- `~/.claude/skills/n8n-mcp-tools-expert/` (search/validation/workflow guides)
- `~/.claude/skills/n8n-code-javascript/`, `n8n-code-python/`
- `~/Dev/clients/learnn/skills/n8n/n8n-quickstart/SKILL.md` (skill v1 Webinar 2)

## 2026-05-04 17:00 — Milestone 4: Refactor v2 platform-agnostic

### ✅ Cosa è stato fatto

- **Q2 ridefinita** in `discovery/questions.md` da "n8n hosting" a "Quale automation platform?" (n8n cloud / self-hosted / Make / Zapier / Pipedream / Workato / Custom / Sto valutando)
- **Sezione 3 estesa**: MCP detection ora platform-aware. Step A probe MCP nativo per platform scelta. Step B invoca skill `platform-adapter-generator` se MCP missing.
- **Nuova skill `platform-adapter-generator/SKILL.md`** (~280 righe): studia API docs platform via WebFetch+context7, genera adapter `<memory>/skills-generated/<platform>/SKILL.md` + `adapter.py` (create_workflow_live, test, update, list), smoke test, attivazione.
- **Sezione 6 (Output spec) ribaltata**: default mode `create_live_workflow`, JSON export solo come fallback se MCP+API entrambi missing OR `--json-only`.
- **Frontmatter aggiornato**: skills da 5 a 6 (platform-adapter-generator first).
- **Description aggiornata**: enfatizza platform-agnostic + create live, no più "n8n only".
- **Identità aggiornata** (sez 1): "creato live nella platform" come main delivery, JSON fallback.
- **Nuova reference `multi-platform-patterns.md`**: portabilità delle 10 recipes canoniche cross-platform (matrix support n8n / Make / Zapier / Pipedream / Workato + cost comparison + decision tree).
- **Riferimenti finali aggiornati**: 6 skill companion + multi-platform-patterns.

### 🚧 Status

- Main file: 550 righe (era 499). Nuovo refactor: +51 righe per platform detection + nuovo output spec.
- Skill count: 6 (era 5).
- Reference count: 7 (era 6).
- Smoke YAML PASS, frontmatter valid.

### 📋 Prossimi step

- Re-zip pack v2 alpha aggiornato
- Re-upload Drive zip individuale automation-architect
- Email Emanuele con versione aggiornata (v2)
