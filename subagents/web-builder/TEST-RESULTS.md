# TEST RESULTS — `/web-builder`

> Output Fase D. Test statici eseguiti dalla worker chat + checklist runtime per Filippo (richiede sessione Claude Code live + utente reale + credenziali Vercel/GitHub/Clerk/Convex).
>
> Pattern allineato a `lead-finder-pro/TEST-RESULTS.md`: 6/6 statici eseguiti ✅, 7 runtime test documentati come checklist.

## Statici eseguiti dalla worker chat (6/6 ✅)

### TS-01 — Frontmatter YAML validation

**Cosa**: parse YAML frontmatter di `web-builder.md` + 5 SKILL.md, verifica chiavi `name`/`description` presenti (+ `when_to_use` per agent main).

**Comando**:
```bash
python3 -c "
import yaml, sys
files = [
    '.../web-builder.md',
    '.../skills/project-scaffolder/SKILL.md',
    '.../skills/claude-md-generator/SKILL.md',
    '.../skills/auth-database-setup/SKILL.md',
    '.../skills/deploy-automation/SKILL.md',
    '.../skills/n8n-bridge/SKILL.md',
]
# ... validation logic
"
```

**Risultato**: ✅ **6/6 OK**, 0 errors

```
OK frontmatter [web-builder.md] name=web-builder
OK frontmatter [project-scaffolder] name=project-scaffolder
OK frontmatter [claude-md-generator] name=claude-md-generator
OK frontmatter [auth-database-setup] name=auth-database-setup
OK frontmatter [deploy-automation] name=deploy-automation
OK frontmatter [n8n-bridge] name=n8n-bridge
```

### TS-02 — JSON validity (templates)

**Cosa**: validate JSON files in `scripts/templates/`: `package.json`, `tsconfig.json`, `components.json`.

**Risultato**: ✅ **7/7 OK**

```
OK scripts/templates/nextjs-saas/package.json
OK scripts/templates/nextjs-saas/tsconfig.json
OK scripts/templates/nextjs-saas/components.json
OK scripts/templates/nextjs-landing/package.json
OK scripts/templates/nextjs-landing/tsconfig.json
OK scripts/templates/astro-marketing/package.json
OK scripts/templates/astro-marketing/tsconfig.json
```

### TS-03 — Bash + Python syntax check

**Cosa**: `bash -n` su `.sh` scripts + `python3 -m py_compile` su `.py` scripts.

**Risultato**: ✅ **6/6 OK**

```
OK cli_detect.sh (bash -n)
OK vercel_deploy.sh (bash -n)
OK discovery_check.py (py_compile)
OK mcp_detect.py (py_compile)
OK scaffold_project.py (py_compile)
OK smoke_test.py (py_compile)
```

**Fix applicato**: aggiunto `from __future__ import annotations` a tutti gli script Python per compatibilità Python 3.9 (env locale era 3.9.6, type hints `X | None` richiedono 3.10+).

### TS-04 — Discovery check script execution

**Cosa**: run `scripts/discovery_check.py` su path inesistente, verifica gestione error path.

**Comando**: `python3 scripts/discovery_check.py --project-path /tmp/web-builder-test-empty`

**Risultato**: ✅ **OK** — output JSON corretto

```json
{"config_exists": false, "errors": ["Project path not exist: /private/tmp/web-builder-test-empty"]}
```

### TS-05 — MCP detection script execution

**Cosa**: run `scripts/mcp_detect.py` sul progetto Learnn, verifica detection MCP server.

**Comando**: `python3 scripts/mcp_detect.py --project-path ~/Dev/clients/learnn`

**Risultato**: ✅ **OK** — detection corretta

```json
{
  "vercel": {"configured": false},
  "github": {"configured": false},
  "context7": {"configured": true, "command": "npx"},
  "playwright": {"configured": true, "command": "npx"},
  "apify": {"configured": true, "command": "npx"},
  "n8n-default": {"configured": true},
  "n8n-knowledge": {"configured": true},
  "n8n-filippo": {"configured": true},
  "n8n-workspace_b-tools": {"configured": true}
}
```

**Note**: Vercel MCP NON installato in env corrente (Filippo deve fare `claude mcp add --transport http vercel https://mcp.vercel.com` per Tier 1 deploy). GitHub MCP idem. Tutti gli n8n MCP di Filippo correctly detected. Fallback chain (DECISION-007) correttamente armato.

### TS-06 — Scaffold project end-to-end (real run)

**Cosa**: run scaffolder reale su `/tmp/web-builder-test-real` con template `nextjs-saas`, verifica:
- 21 file creati
- Placeholder `{{X}}` e `{{ X }}` (formattati JSX) tutti sostituiti
- JSON validity preservata post-substitution
- Output utente leggibile

**Comando**:
```bash
python3 scripts/scaffold_project.py \
  --template-id nextjs-saas \
  --project-name test-real-saas \
  --project-path /tmp/web-builder-test-real \
  --author "Filippo Greco" \
  --description "Test scaffold reale" \
  --no-git
```

**Risultato**: ✅ **OK** — 21 file creati, 0 placeholder residui, JSON valido

```
status: success
files_count: 21
remaining_placeholders: 0 (after regex fix to handle {{ X }} formatter variant)
package.json substituted: name="test-real-saas", description="Test scaffold reale", author="Filippo Greco"
JSON validity: package.json + components.json + tsconfig.json all parse ok
```

**Fix applicato durante test**: `scaffold_project.py` originale non gestiva il caso `{{ X }}` con spazi (formatter TSX li aggiunge). Update con regex pattern `r"\{\{\s*KEY\s*\}\}"` per gestire entrambe le forme. Test TS-06 ri-eseguito post-fix con success.

---

## Runtime test (7 da eseguire da Filippo, sessione Claude Code live)

I seguenti test richiedono:
- Sessione Claude Code aperta in cartella reale
- Filippo come utente (per AskUserQuestion + OAuth flows)
- Credenziali: Vercel account, GitHub account, Clerk dashboard, Convex account

Worker chat NON può eseguirli direttamente. Documentati come checklist riproducibile.

### TR-01 — Discovery flow primo run

**Setup**:
```bash
cd ~/tmp
mkdir web-builder-test-1
cd web-builder-test-1
claude
```

**Step**:
```
> /web-builder
```

**Verifica**:
- [ ] 8 AskUserQuestion mostrate sequenzialmente (Q1 Tipo, Q2 Esperienza, ..., Q8 Deploy)
- [ ] Header chip mostrato per ogni domanda (Tipo, Esperienza, Stack, Dominio, Auth, Database, Automation, Deploy)
- [ ] Opzioni Q3 cambiano dinamicamente in base a Q1 (es. Q1=Landing → Astro come opzione raccomandata)
- [ ] Salvataggio config in `.claude/web-builder/config.md` (o `.claude/memory/config.md`)
- [ ] Summary finale "Ho capito: stack X. Procedo? [Sì/Modifica/Annulla]"

**Expected output**: config.md scritto con schema YAML valido, validabile con `python3 scripts/discovery_check.py --project-path . --validate`.

### TR-02 — Re-run skip discovery

**Setup**: stesso path di TR-01 (config.md già presente).

**Step**:
```
> /web-builder
```

**Verifica**:
- [ ] NESSUNA AskUserQuestion mostrata
- [ ] Messaggio tipo: "Trovo config esistente, riprendo da fase X"
- [ ] Comando `reconfigure` riapre discovery flow

### TR-03 — Real build landing (Astro)

**Setup**:
```bash
cd ~/tmp
mkdir web-builder-test-landing
cd web-builder-test-landing
claude
```

**Step**:
```
> /web-builder

Voglio una landing per il mio corso AI dal nome "AI Mastery 2026"

Discovery answers:
  Q1: Landing/marketing
  Q2: Vibe coder
  Q3: Astro (default raccomandato)
  Q4: No, uso .vercel.app
  Q5: No (pubblico)
  Q6: No (statico)
  Q7: No
  Q8: No (deploy manuale per ora)
```

**Verifica**:
- [ ] Cartella `ai-mastery-2026/` creata
- [ ] `package.json` con name="ai-mastery-2026", placeholder sostituiti
- [ ] CLAUDE.md presente, sezioni standard popolate (Project context, Stack, Common commands, ecc.)
- [ ] `npm install` eseguito senza errori
- [ ] `npm run dev` parte su `localhost:4321` (porta Astro default)
- [ ] Homepage mostra "AI Mastery 2026" hero + features + CTA
- [ ] Lighthouse score >90 (run via `npx lighthouse http://localhost:4321 --view`)

### TR-04 — Real build SaaS micro

**Setup**:
```bash
cd ~/tmp
mkdir web-builder-test-saas
cd web-builder-test-saas
claude
```

**Step**:
```
> /web-builder

SaaS per gestire clienti freelance: login email/password, dashboard, billing mensile

Discovery answers:
  Q1: SaaS micro
  Q2: Vibe coder
  Q3: Default Filippo
  Q4: Decido dopo
  Q5: Sì consumer (Clerk)
  Q6: Sì realtime (Convex)
  Q7: Sì (per webhook Stripe)
  Q8: Sì auto
```

**Verifica**:
- [ ] Cartella `freelance-crm/` creata con template `nextjs-saas`
- [ ] `convex/schema.ts` con `users` + `items` tables (placeholder `items` da rinominare)
- [ ] `middleware.ts` Clerk presente con `isProtectedRoute` matcher
- [ ] `app/(dashboard)/dashboard/page.tsx` esiste come protected route example
- [ ] `app/(auth)/sign-in/[[...sign-in]]/page.tsx` + `sign-up/` esistono
- [ ] `.env.local.example` con tutti env vars (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `NEXT_PUBLIC_CONVEX_URL`, `CLERK_JWT_ISSUER_DOMAIN`)
- [ ] `convex/auth.config.ts` per Clerk JWT config
- [ ] CLAUDE.md template SaaS variant compilato
- [ ] `npm install` ok
- [ ] `npx convex dev` apre browser per OAuth Convex (utente deve completare login)
- [ ] Phase 7 n8n: webhook handler `app/api/webhook/stripe/route.ts` generato
- [ ] Phase 6 deploy: triggers Vercel MCP OAuth o `vercel login` CLI

**Atteso edge case**: Clerk dashboard manual setup richiesto (no API per create app). Agent deve aprire URL dashboard.clerk.com e fornire instructions screenshot.

### TR-05 — MCP fallback Vercel

**Setup**: rimuovere temporaneamente Vercel MCP da `~/.claude.json` o disable, simulare missing.

**Step**: trigger Phase 6 (deploy) in test TR-04 senza Vercel MCP.

**Verifica**:
- [ ] Detection corretta MCP missing
- [ ] Switch automatico a Tier 2 (CLI) con messaggio "Vercel MCP non disponibile, uso CLI"
- [ ] Ask `vercel login` se non già loggato
- [ ] Procede con `vercel link` + `vercel env add` + `vercel deploy`
- [ ] Smoke test post-deploy via `curl` (no Playwright se non disponibile)

### TR-06 — Deploy automation end-to-end

**Setup**: continua da TR-04 con Vercel MCP attivo (Tier 1 path).

**Step**: completare Phase 6 con `Q8 = Sì auto`.

**Verifica**:
- [ ] Vercel MCP `create_project` esegue
- [ ] Env vars settati per `preview` + `production` (entrambi)
- [ ] Primo deploy preview ritorna URL (es. `freelance-crm-abc123.vercel.app`)
- [ ] Smoke test: HTTP 200 + screenshot via Playwright (se MCP attivo) o curl
- [ ] Output finale leggibile con:
  - Preview URL
  - GitHub repo URL
  - Smoke test status
  - Comando promote-prod
  - Comando rollback

**Pre-deploy gate**: deploy-check rules (deploy-check-rules.md) eseguite — secrets in git, .env.local committed, build success, test pass.

### TR-07 — Edge case cartella esistente

**Setup**:
```bash
cd ~/tmp
mkdir web-builder-test-existing
cd web-builder-test-existing
echo "# Mio progetto" > README.md
echo "console.log('test')" > existing.js
claude
```

**Step**:
```
> /web-builder

Voglio un SaaS micro
```

**Verifica**:
- [ ] Discovery completa normalmente
- [ ] In Phase 2 scaffold: prompt "Trovo file esistenti in `<path>`. Cosa vuoi fare? (1) merge, (2) backup + scaffold pulito, (3) abort"
- [ ] NO overwrite silenzioso di `README.md` o `existing.js`
- [ ] Se utente sceglie `2` (backup): cartella `<path>.bak/` creata con file originali
- [ ] Se utente sceglie `3` (abort): scaffold annullato, no file modified

---

## Coverage summary

| Test | Type | Status | Notes |
|---|---|---|---|
| TS-01 Frontmatter YAML | Static | ✅ Done | 6/6 OK |
| TS-02 JSON validity | Static | ✅ Done | 7/7 OK |
| TS-03 Bash+Python syntax | Static | ✅ Done | 6/6 OK (post Python 3.9 fix) |
| TS-04 Discovery script | Static | ✅ Done | Error handling ok |
| TS-05 MCP detection script | Static | ✅ Done | Detected expected MCPs |
| TS-06 Scaffold end-to-end | Static | ✅ Done | 21 file, 0 placeholder residui (post regex fix) |
| TR-01 Discovery flow | Runtime | ⏳ Pending Filippo | Richiede AskUserQuestion live |
| TR-02 Skip discovery | Runtime | ⏳ Pending Filippo | Post TR-01 |
| TR-03 Build landing Astro | Runtime | ⏳ Pending Filippo | Test full build |
| TR-04 Build SaaS micro | Runtime | ⏳ Pending Filippo | Richiede Clerk/Convex setup |
| TR-05 MCP fallback | Runtime | ⏳ Pending Filippo | Disable MCP simulation |
| TR-06 Deploy end-to-end | Runtime | ⏳ Pending Filippo | Richiede Vercel account |
| TR-07 Edge case existing | Runtime | ⏳ Pending Filippo | Manual setup folder |

**Worker chat completion**: 6/6 statici PASS ✅. Runtime 7/7 documentati come checklist riproducibile.

## Fix applicati durante test

1. **`from __future__ import annotations`** aggiunto ai 4 script Python (`discovery_check.py`, `mcp_detect.py`, `scaffold_project.py`, `smoke_test.py`) per compatibilità Python 3.9 (env locale era 3.9.6, type hints `X | None` richiedono 3.10+ a runtime; con future import sono trattati come string lazy).

2. **Placeholder substitution regex**: `scaffold_project.py` originale non gestiva caso `{{ X }}` (con spazi aggiunti dal formatter TSX in JSX expression). Aggiornato con regex `r"\{\{\s*KEY\s*\}\}"` per matchare entrambe le forme `{{KEY}}` e `{{ KEY }}`. Test TS-06 ri-eseguito post-fix con success.

## File totali deliverable

```
.claude/agents/web-builder/
├── ARCHITECTURE.md          (434 righe)
├── BUILD-BRIEF.md           (531 righe — coordinator pre-existing)
├── DECISIONS.md             (148 righe, 8 decisioni: 4 iniziali + 4 emergent)
├── PROGRESS.md              (85 righe, log worker chat)
├── README.md                (296 righe, user-facing)
├── TEST-RESULTS.md          (questo file)
├── web-builder.md           (391 righe, system prompt main agent)
├── discovery/
│   └── questions.md         (211 righe, 8 domande finalizzate)
├── research/
│   ├── notebook-id.txt      (1 riga, NotebookLM ID)
│   └── research-summary.md  (3653 parole, target >2500 ✅)
├── references/
│   ├── auth-integration-2026.md       (307 righe)
│   ├── claude-md-templates.md         (256 righe)
│   ├── database-integration-2026.md   (320 righe)
│   ├── deploy-check-rules.md          (199 righe)
│   ├── deploy-vercel-2026.md          (292 righe)
│   ├── n8n-integration-2026.md        (205 righe)
│   ├── shadcn-patterns-2026.md        (376 righe)
│   └── stack-comparison-2026.md       (258 righe)
├── scripts/
│   ├── cli_detect.sh                  (67 righe)
│   ├── discovery_check.py             (178 righe)
│   ├── mcp_detect.py                  (132 righe)
│   ├── requirements.txt
│   ├── scaffold_project.py            (310 righe)
│   ├── smoke_test.py                  (116 righe)
│   ├── vercel_deploy.sh               (104 righe)
│   └── templates/
│       ├── nextjs-saas/               (~21 file completo)
│       ├── nextjs-landing/            (~10 file completo)
│       ├── astro-marketing/           (~9 file completo)
│       ├── next-internal-tool/        (stub v1, README + roadmap v2)
│       └── expo-mobile/               (stub v1, README + roadmap v2)
└── skills/
    ├── auth-database-setup/SKILL.md   (297 righe)
    ├── claude-md-generator/SKILL.md   (308 righe)
    ├── deploy-automation/SKILL.md     (226 righe)
    ├── n8n-bridge/SKILL.md            (260 righe)
    └── project-scaffolder/SKILL.md    (254 righe)
```

**Total**: ~50 file, ~5500 righe di documentation + code.
