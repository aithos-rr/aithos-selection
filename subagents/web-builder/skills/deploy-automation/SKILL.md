---
name: deploy-automation
description: Orchestrazione deploy Vercel via MCP (preferred Tier 1 OAuth-based), CLI fallback (Tier 2 vercel login), token last resort (Tier 3 VERCEL_TOKEN env). Init vercel link, push GitHub, configura env vars production, primo deploy preview, smoke test post-deploy (HTTP 200 + screenshot via Playwright se MCP available), comando promote a prod. Riusa pattern deploy-check skill v1 come gating pre-deploy. Da usare in Phase 6 della methodology /web-builder.
when_to_use: Phase 6 di /web-builder, deploy iniziale Vercel, env vars management production, smoke test post-deploy, promote preview → production
---

# Deploy Automation

Skill di Phase 6 della methodology `/web-builder`. Implementa pattern 3-tier (DECISION-007): MCP-first, CLI-fallback, token-last-resort. Riusa pattern `deploy-check` skill v1 come gating pre-deploy.

## When to use

Attiva quando:
- Phase 5 (componenti) completata
- `config.build.deploy_done == false`
- `config.deploy.auto_deploy_main == true`

**Non attivare se**:
- `config.deploy.auto_deploy_main == false` (utente preferisce manual deploy) → genera solo `vercel.json` + istruzioni README, skip skill
- `config.deploy.vercel_project_id` già set (skip vercel link, riusa esistente)

## Input contract

```yaml
project_path: /path/to/project
deploy_method: mcp | cli | token  # auto-detected, vedi sez "Tier detection"
env_vars: {KEY: VALUE, ...}        # da .env.local
prod: false                         # primo deploy = preview, non prod
github_repo: "user/repo" or null   # se null, propose creation
```

## Output contract

```yaml
status: success | partial | failed
deploy_url: https://my-saas-abc123.vercel.app
deploy_type: preview | production
smoke_test_results:
  http_status: 200
  response_time_ms: 245
  screenshot_path: /tmp/screenshot-home.png  # se Playwright MCP available
  errors: []
rollback_command: "vercel rollback <previous_deployment_id>"
deploy_logs_url: "https://vercel.com/<org>/<project>/deployments/xxx"
```

## Tier detection (DECISION-007)

### Tier 1 — Vercel MCP (preferred)

**Detection**: `verify_mcp("vercel")` returns `True`

**Flow**:
1. MCP `vercel:create_project(name, github_repo)` o `vercel:link_project(path)`
2. MCP `vercel:set_env_vars(project_id, env_vars, target="preview")`
3. MCP `vercel:deploy(project_id, target="preview")` → returns deploy_url
4. Smoke test (vedi step finale)

**Pro**: zero token entry utente, OAuth handled by Claude Code, confused-deputy protection automatica.

### Tier 2 — Vercel CLI

**Detection**: MCP missing, `shutil.which("vercel") is not None`

**Flow**:
1. Check `~/.local/share/com.vercel.cli/auth.json` esistenza (utente già loggato)
2. Se non loggato: `vercel login` (browser OAuth, attendi completion)
3. `cd <project_path> && vercel link --yes` (associa folder a progetto, ask team se più team)
4. Per ogni env var: `vercel env add <KEY> preview` (interactive prompt utente per value, MAI passare value via Bash)
5. `vercel deploy` (preview deploy auto)
6. Smoke test

**Pro**: funziona senza MCP installato. **Con**: utente deve fare 1 OAuth browser flow.

### Tier 3 — VERCEL_TOKEN env var (last resort)

**Detection**: MCP missing, CLI missing, `os.getenv("VERCEL_TOKEN")` exists

**Flow**:
1. Use `VERCEL_TOKEN` direct via API REST (skip CLI)
2. POST `https://api.vercel.com/v9/projects` per create project
3. POST `https://api.vercel.com/v10/projects/<id>/env` per set env vars (1 per request)
4. POST `https://api.vercel.com/v13/deployments` per deploy
5. Smoke test

**Pro**: funziona in CI senza interaction. **Con**: token in env var = anti-pattern security per non-dev. Solo last resort.

### Fallback final — Document manual

Se nessun tier disponibile: genera `vercel.json` + README sezione "Deploy manuale" con instructions step-by-step, skip skill execution.

## Workflow comune (post tier detection)

### Step 1 — GitHub repo setup

Se `config.deploy.github_repo` è null:

```bash
# Tier 1: GitHub MCP available
github:create_repo(name, private=false)

# Tier 2: gh CLI fallback
gh repo create <name> --public --source=<project_path> --push
```

Save `config.deploy.github_repo`.

### Step 2 — Vercel project link

(Vedi tier-specific flow sopra.)

### Step 3 — Env vars production setup

Per ogni env var necessaria (lista da Phase 4 output):

- **Public** (`NEXT_PUBLIC_*`): set in Vercel project env, target `preview` + `production`
- **Secret**: set in Vercel project env, target `preview` + `production`
- **Auto-generated** (es. `NEXT_PUBLIC_CONVEX_URL` da `npx convex deploy`): genera prima Convex prod deployment, poi set su Vercel

### Step 4 — Build verification (pre-deploy gate)

Riusa pattern `deploy-check` skill v1 (`references/deploy-check-rules.md`):

**🔴 Blocker (se fail → STOP deploy)**:
- Secrets in git: `git log --all -p | grep -E '(sk_live|pk_live|password=)' | head -5`
- `.env*.local` committed: `git ls-files | grep -E '\.env\.(local|production)$'` deve essere empty
- Build success local: `npm run build` exit 0
- Test pass (se test scritti): `npm test` exit 0

**🟡 Warning (review prima)**:
- Env vars Vercel matcha local
- HTTPS only (Vercel default ✅)
- Error monitoring (placeholder, suggest Sentry future)

Se Blocker fail: STOP deploy, report errore + fix command. Non procedere.

### Step 5 — Deploy preview

```bash
# Tier 2 esempio
vercel deploy --token $VERCEL_TOKEN  # o senza token se logged in
```

Output URL preview (es. `https://my-saas-abc123.vercel.app`).

### Step 6 — Smoke test post-deploy

#### Tier A — Playwright MCP available

```python
playwright:goto(deploy_url)
playwright:screenshot(path="/tmp/screenshot-home.png", fullPage=True)
playwright:get_response_status()  # check HTTP 200
```

#### Tier B — curl fallback

```bash
curl -I -L -m 10 <deploy_url>  # follow redirect, max 10s timeout
# Parse: HTTP/2 200 → ok
```

Se status != 200: report errore, **NON promote a prod**. Mostra log Vercel.

### Step 7 — Output user

```
🚀 Deploy preview live!

📍 URL: <deploy_url>
🐙 GitHub: https://github.com/<repo>
📊 Smoke test: ✅ HTTP 200 (245ms)
📸 Screenshot: <path>

🎯 Prossimi passi:
1. Apri <deploy_url> nel browser, verifica funzionamento
2. Test feature critiche (login, dashboard, ecc.)
3. Quando pronto, promote a production:
     `/web-builder promote-prod`
   (questo attiverà custom domain se configurato in Q4)

🔄 Rollback (se serve): `vercel rollback <deploy_id>`
```

## Edge cases

| Edge case | Handling |
|---|---|
| Vercel deploy fail (build error) | Parse log Vercel, identify: missing env / TS error / dependency. Report fix specifico. |
| Vercel quota exceeded (free tier) | "Hai esaurito il piano free. Upgrade a Pro $20/mo o usa altro Vercel account?" |
| GitHub repo name conflict | Suggest variant `<name>-app` o `<name>-2`. Ask user override. |
| Env vars missing pre-deploy | Lista mancanti from `grep -r 'process.env.' src/ app/`. Prompt utente con hint per ognuna. |
| MCP OAuth fail | Switch automatico a Tier 2 CLI con messaggio "MCP OAuth failed, fallback CLI". |
| Convex prod deploy required | Run `npx convex deploy` prima di Vercel deploy. Save `NEXT_PUBLIC_CONVEX_URL` prod. |
| Custom domain (Q4=Sì custom) | Post-deploy: `vercel domain add <domain>`. Show DNS instructions (CNAME a `cname.vercel-dns.com`). |

## Promote to production (separate command)

`/web-builder promote-prod` è un sub-command che:

1. Verifica deploy preview ok
2. Run `deploy-check` rules (blocker/warning)
3. Confirm utente esplicito "Sto deployando in PRODUCTION, sicuro?"
4. Tier-specific:
   - Tier 1: MCP `vercel:promote_to_production(project_id, deploy_id)`
   - Tier 2: `vercel deploy --prod`
5. Smoke test prod URL
6. Update `config.deploy.production_url` + `config.build.deploy_done = true`

## References

- `references/deploy-vercel-2026.md` — Vercel MCP usage + CLI commands ref + custom domain
- `references/deploy-check-rules.md` — 14 regole pre-deploy (riusa skill v1)
- [vercel.com/docs/agent-resources/vercel-mcp](https://vercel.com/docs/agent-resources/vercel-mcp)

## Gotchas

- 🔴 **Mai promote a prod senza smoke test preview**: gating obbligatorio.
- 🔴 **Mai passare valori secret via Bash arg**: shell history li registra. Use Vercel UI o `vercel env add` interactive prompt.
- 🟡 **Build cache**: prima deploy può richiedere 3-5 min. Subseguenti < 1 min con cache.
- 🟡 **Env var rename**: cambiare nome env var richiede manual delete + add (Vercel non rinomina).
- 🟢 **Branch deploys auto**: Vercel default deploya ogni branch in preview. Configurabile in `vercel.json`.

## Crediti

Skill creata per `/web-builder` (Pack v2 Learnn). Pattern 3-tier deploy automation derivato da DECISION-007 + research RQ8 (vedi `research/research-summary.md`). Riusa logic `deploy-check` skill v1.
