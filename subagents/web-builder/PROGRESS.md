# PROGRESS — `/web-builder`

> Aggiornare ad ogni milestone (almeno ogni 25% context fill). Vedi BUILD-BRIEF.md sez "Context management" per template entry.

## Stato corrente

**Fase**: ✅ DONE — A→E completate end-to-end (30 apr 2026 pomeriggio)
**Last update**: 2026-04-30 pomeriggio (worker chat session #1, finale)
**Worker chat**: aperta in `.claude/agents/web-builder/`, scope = pipeline completa A→E ✅

## Riepilogo deliverable

| Categoria | Conteggio | Note |
|---|---|---|
| Main agent (`web-builder.md`) | 391 righe | target 350-500 ✅ |
| ARCHITECTURE.md | 434 righe | target ~420 ✅ |
| README.md | 296 righe | target ~260 ✅ |
| DECISIONS.md | 148 righe (8 decisioni) | 4 iniziali + 4 emergent (DECISION-005-008) |
| TEST-RESULTS.md | 6 statici PASS + 7 runtime checklist | pattern lead-finder-pro |
| discovery/questions.md | 211 righe (8 Q finalizzate) | post-research affinate |
| research/research-summary.md | 3653 parole | target >2500 ✅, NotebookLM `e68d4b25` |
| Skills companion | 5 (226-308 righe ognuna) | project-scaffolder, claude-md-generator, auth-database-setup, deploy-automation, n8n-bridge |
| References docs | 8 (199-376 righe ognuno) | stack-comparison, db, auth, deploy, claude-md-templates, n8n, deploy-check, shadcn |
| Scripts | 6 (.py + .sh) | discovery_check, mcp_detect, cli_detect, scaffold_project, vercel_deploy, smoke_test |
| Templates starter | 5 (3 completi + 2 stub) | nextjs-saas (~21 file), nextjs-landing (~8 file), astro-marketing (~9 file), next-internal-tool (stub), expo-mobile (stub) |

**Total**: ~50 file, ~5500 righe deliverable.

## Setup pre-build (coordinator)

- ✅ Cartella struttura creata: `.claude/agents/web-builder/{discovery,skills,references,scripts,research}/`
- ✅ BUILD-BRIEF.md scritto (richiede solo lettura per worker chat)
- ✅ NotebookLM creato in Fase A — id: `e68d4b25-04fc-4ca3-8a6f-1a252d0dabb4` (8 sources aggiunte)
- ✅ Skill v1 base lette (`vibe-start` 236 righe, `deploy-check` 165 righe) + `tech-stack-2026` baseline (207 righe)

## Log milestone

### 2026-04-30 pomeriggio — Milestone Fase E (Documentation + Bundle) ✅ DONE

#### ✅ Cosa è stato fatto

- Update `MASTER-PROGRESS.md`: stato `/web-builder` da 🟡 → ✅ Done con riepilogo completo deliverable + log entry pomeriggio
- Update `dist/CLAUDE_WEEK_SKILL_PACK.md`: aggiunta sezione `/web-builder` user-facing (descrizione ARTIFACT-driven, MCP utilizzati, 5 skills, 5 templates, 3 esempi reali, source grounding NotebookLM, status build-complete)
- Sintesi Obsidian salvata: `~/Dev/obsidian-vault/02 - Ricerca/web-builder_2026-04-30.md` (frontmatter standard, top 5 finding, decision matrix, anti-pattern, lezione per il futuro, connessioni vault)
- Final update PROGRESS.md (questo file)

#### 🔗 File esterni rilevanti

- `<pack-root>/.claude/agents/MASTER-PROGRESS.md` (stato `/web-builder` ✅ Done)
- `<pack-root>/dist/CLAUDE_WEEK_SKILL_PACK.md` (sezione `/web-builder` user-facing)
- `~/Dev/obsidian-vault/02 - Ricerca/web-builder_2026-04-30.md` (sintesi)

### 2026-04-30 pomeriggio — Milestone Fase D (Test) ✅ DONE

#### ✅ Cosa è stato fatto

**Statici eseguiti dalla worker chat (6/6 PASS)**:

- TS-01 Frontmatter YAML validation: 6/6 OK (`web-builder.md` + 5 SKILL.md, chiavi `name`/`description`/`when_to_use` presenti)
- TS-02 JSON validity templates: 7/7 OK (package.json, tsconfig, components.json di tutti i 3 template completi)
- TS-03 Bash + Python syntax: 6/6 OK (post fix Python 3.9 compat con `from __future__ import annotations`)
- TS-04 Discovery script execution: error handling OK (path inesistente gestito)
- TS-05 MCP detection script: detect corretti (context7, playwright, apify, n8n-* configurati; Vercel/GitHub MCP NON configurati — fallback chain DECISION-007 armato)
- TS-06 Scaffold end-to-end real run: 21 file creati per `nextjs-saas`, 0 placeholder residui (post regex fix), JSON validity preservata

**Runtime documentati come checklist (7 pending Filippo)**:

- TR-01 Discovery flow primo run (verifica 8 AskUserQuestion + salvataggio config.md)
- TR-02 Re-run skip discovery (config esistente)
- TR-03 Real build landing (Astro)
- TR-04 Real build SaaS micro (Next + Convex + Clerk)
- TR-05 MCP fallback Vercel (simula MCP missing)
- TR-06 Deploy automation end-to-end (richiede Vercel account)
- TR-07 Edge case cartella esistente (NO overwrite silenzioso)

**Fix applicati durante test**:

1. `from __future__ import annotations` su 4 script Python (Python 3.9 compat — env locale 3.9.6, type hints `X | None` richiedono 3.10+ a runtime; con future import sono trattati come string lazy)
2. Placeholder substitution regex `r"\{\{\s*KEY\s*\}\}"` per gestire entrambe forme `{{KEY}}` e `{{ KEY }}` (formatter TSX aggiunge spazi nelle JSX expression)

#### 🔗 File esterni rilevanti

- `<pack-root>/.claude/agents/web-builder/TEST-RESULTS.md` (output completo)

### 2026-04-30 pomeriggio — Milestone Fase C (Build) ✅ DONE

#### ✅ Cosa è stato fatto

- `web-builder.md` system prompt 391 righe con 10 sezioni (identità, discovery flow, MCP+CLI detection, decision matrix stack, methodology 6+1 fasi, tool usage rules, output format, edge cases, examples, anti-patterns)
- 5 SKILL.md companion in `skills/`:
  - `project-scaffolder/SKILL.md` (254 righe)
  - `claude-md-generator/SKILL.md` (308 righe)
  - `auth-database-setup/SKILL.md` (297 righe)
  - `deploy-automation/SKILL.md` (226 righe)
  - `n8n-bridge/SKILL.md` (260 righe)
- 8 references docs in `references/`:
  - stack-comparison-2026.md (258 righe)
  - database-integration-2026.md (320 righe)
  - auth-integration-2026.md (307 righe)
  - deploy-vercel-2026.md (292 righe)
  - claude-md-templates.md (256 righe — 3 template variant)
  - n8n-integration-2026.md (205 righe)
  - deploy-check-rules.md (199 righe — 14 regole)
  - shadcn-patterns-2026.md (376 righe — top 10 pattern)
- 6 scripts in `scripts/`:
  - `discovery_check.py` (178 righe — config validation YAML)
  - `mcp_detect.py` (132 righe — MCP server detection)
  - `cli_detect.sh` (67 righe — CLI tool detection)
  - `scaffold_project.py` (310 righe — copy template + placeholder substitution + git init)
  - `vercel_deploy.sh` (104 righe — wrapper Vercel CLI 3-tier)
  - `smoke_test.py` (116 righe — HTTP 200 check + paths)
- 5 templates starter in `scripts/templates/`:
  - `nextjs-saas/` (~21 file completo: package.json, tsconfig, next.config, middleware Clerk, app/ con (auth) e (dashboard), convex/schema+items+auth.config, components.json, lib/utils, postcss, gitignore, env.example, CLAUDE.md, README.md, app pages)
  - `nextjs-landing/` (~8 file: package, tsconfig, next.config, app/layout+page+globals.css, postcss, CLAUDE.md, README.md, gitignore)
  - `astro-marketing/` (~9 file: package, astro.config con Vercel adapter + sitemap, tsconfig strict, src/{layouts/Layout.astro, pages/index.astro, content/config.ts, styles/global.css}, CLAUDE.md, README.md, gitignore)
  - `next-internal-tool/README.md` (stub v1, fallback `nextjs-saas`)
  - `expo-mobile/README.md` (stub v1, roadmap v2)
- README.md user-facing 296 righe (FAQ, troubleshooting, 3 esempi reali end-to-end)

### 2026-04-30 pomeriggio — Milestone Fase B (Architecture) ✅ DONE

#### ✅ Cosa è stato fatto

- `discovery/questions.md` 211 righe (8 domande finalizzate post-research, opzioni dinamiche per Q3 in base a Q1, conseguenze logiche per ogni Q, schema validation rules)
- `ARCHITECTURE.md` 434 righe (identità, architecture overview ASCII art, discovery flow dettagliato, MCP+CLI detection logic con pseudocode, tech stack decision matrix, methodology 6+1 fasi, skill contracts I/O completi, config schema YAML completo, edge cases handling, output conventions, anti-patterns)
- 5 skill contracts dettagliati (input/output/references/activation per ognuna)

### 2026-04-30 — Milestone Fase A (Deep Research) ✅ DONE

#### ✅ Cosa è stato fatto

- Letto BUILD-BRIEF.md (531 righe) + DECISIONS.md (4 decisioni iniziali) + PROGRESS.md template
- Letto skill v1 base: `tech-stack-2026/SKILL.md`, `vibe-start/SKILL.md`, `deploy-check/SKILL.md`
- Letto pattern lead-finder-pro deliverable list (target qualità)
- Creato NotebookLM "Web Builder - Tech Stack 2026" (id `e68d4b25-04fc-4ca3-8a6f-1a252d0dabb4`)
- Aggiunte 8 sources NotebookLM (Next.js docs, Convex docs, Supabase, Clerk Next.js, Vercel CLI, shadcn, Astro, Vercel MCP)
- Eseguite 7 WebSearch (RQ1-7 + audience non-dev SaaS MVP)
- Eseguite 2 WebFetch (Vercel MCP docs, Convex Quickstart Next.js)
- Eseguite 2 parallel-cli search (boilerplate Convex+Clerk+shadcn, Astro starter Tailwind v4)
- Scritto `research/research-summary.md` (~3653 parole, 8 RQ con citazioni, decision matrix, edge case, tool/CLI capabilities, 4 decisioni emergent, 8 anti-pattern)
- Scritto 4 decisioni emergent in `DECISIONS.md`: DECISION-005 (Astro override Landing), DECISION-006 (Convex confirmed default), DECISION-007 (Vercel MCP-first deploy), DECISION-008 (Expo stub v1)

#### 🐛 Edge case scoperti (Fase A)

- **Convex non ha MCP nativo** — fallback CLI `npx convex dev`. Documentato in skill `auth-database-setup` activation.
- **Vercel MCP only-Claude-Code (e altri client approved)** — flow OAuth via `claude mcp add --transport http vercel`. Documentato in skill `deploy-automation`.
- **`get-convex/template-nextjs-clerk-shadcn`** = template ufficiale Convex per default stack — usabile come base per `nextjs-saas/` template starter (riduce reinvent).
- **Existing `CLAUDE_starter_template.md` di Filippo** — verificato esistente in `<pack-root>/skills/CLAUDE_starter_template.md`. Da riusare in skill `claude-md-generator`.

## Definition of Done — checklist finale

- [x] Tutte le 5 fasi completate (A research → B architecture → C build → D test → E docs)
- [x] PROGRESS.md aggiornato a "Done" (questo file)
- [x] MASTER-PROGRESS.md aggiornato (✅ Done + log entry)
- [x] 7 test documentati (6 statici eseguiti PASS + 7 runtime checklist per Filippo)
- [x] README utente comprensibile da non-tech (test mentale: lo darei a un freelancer marketer? ✅)
- [x] System prompt `web-builder.md` ≥ 350 righe e sostanzioso (391 righe ✅)
- [x] 5 skills companion + 8 references docs (target era 4-5 + 6+ ✅)
- [x] 3 template starter funzionanti (smoke statico OK con scaffold real run, no `npm install` eseguito) + 2 stub
- [x] 3 esempi reali documentati end-to-end nel README
- [x] research-summary.md > 2500 parole con citazioni (3653 parole ✅)
- [x] Sintesi Obsidian salvata
- [x] Verifica statica: frontmatter YAML valido su main agent + tutte le SKILL.md (6/6 PASS)
- [ ] **Almeno 1 progetto demo deployato**: marcato come "pending Filippo" in TEST-RESULTS.md TR-06 (consistent con lead-finder-pro pattern — richiede credenziali Vercel)

## Notifica al coordinator

**`/web-builder` DONE end-to-end**, ready per:

1. **Test runtime** da Filippo (7 test documentati in TEST-RESULTS.md sez TR-01 a TR-07)
2. **Bundle alpha Pack v2** — 2/8 subagent completi (`/lead-finder-pro` + `/web-builder`)
3. **Avvio worker chat** per `/competitor-deep-dive` (Fase B-E, già Fase A done) e `/outbound-orchestrator` (BUILD-BRIEF ready)

Filippo: per validare runtime, apri Claude Code in cartella vuota, lancia `/web-builder`, segui discovery flow + checkpoint approval per ogni fase. Tempo stimato per test completo TR-01-04: ~60 min. TR-05-07 incrementali ~30 min.
