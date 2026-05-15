# Deploy Vercel 2026 — Reference

> Output Fase A research RQ4 + RQ8 → reference per skill `deploy-automation`. Pattern 3-tier MCP/CLI/token (DECISION-007).

## Tier 1 — Vercel MCP (preferred)

### Install

```bash
# In Claude Code project
claude mcp add --transport http vercel https://mcp.vercel.com
# Authenticate via /mcp
```

### Setup OAuth flow

1. `/mcp` in Claude Code → list MCPs
2. Selezionare `vercel` → autorizza nel browser
3. Token gestito automaticamente da Claude Code (no manual entry)

### Tools disponibili

**Public** (no auth required):
- `vercel:search_docs(query)` — search Vercel documentation

**Authenticated** (post-OAuth):
- `vercel:list_projects()` — list user/team projects
- `vercel:create_project(name, framework, gitRepository)` — create new project
- `vercel:link_project(projectId)` — link local folder to project
- `vercel:set_env_vars(projectId, vars[], target)` — set env per environment
- `vercel:deploy(projectId, target='preview'|'production')` — trigger deploy
- `vercel:list_deployments(projectId)` — history
- `vercel:get_deployment_logs(deploymentId)` — fetch logs
- `vercel:promote_to_production(projectId, deploymentId)` — preview → prod
- `vercel:list_env_vars(projectId)` — list (no values)
- `vercel:add_domain(projectId, domain)` — custom domain

### Security best practices

- **Verify endpoint**: sempre `https://mcp.vercel.com` (no third-party MCP marketplace impersonation)
- **Confused deputy protection**: explicit user consent per ogni client
- **Human confirmation**: always enable in workflow (Claude Code default)
- **Data scope**: MCP opera SOLO in account Vercel utente

## Tier 2 — Vercel CLI

### Install

```bash
npm install -g vercel
# o via Homebrew
brew install vercel-cli
```

### OAuth login (one-time)

```bash
vercel login
# Choose: GitHub | Email | SAML SSO | etc.
# Browser opens for OAuth → token stored in ~/.local/share/com.vercel.cli/auth.json
```

### Common commands

```bash
# Link folder a progetto Vercel
cd <project_path>
vercel link
# Ask: scope (personal o team), project name (existing or new)

# Set env var (interactive prompt per value)
vercel env add NEXT_PUBLIC_CONVEX_URL production
vercel env add CLERK_SECRET_KEY production
# Pulls from .env.local automatically
vercel env pull .env.local

# Deploy preview
vercel deploy
# Output: deploy URL preview

# Deploy production
vercel deploy --prod

# List deployments
vercel ls

# View logs
vercel logs <deployment_url>

# Rollback
vercel rollback <previous_deployment_url>

# Add custom domain
vercel domains add my-domain.com
# DNS instructions: CNAME my-domain.com → cname.vercel-dns.com
```

### Non-interactive mode (CI)

```bash
vercel deploy --token $VERCEL_TOKEN --yes  # skip confirms
```

## Tier 3 — VERCEL_TOKEN env var (last resort)

### Get token

1. https://vercel.com/account/tokens → Create
2. Scope: project-specific raccomandato (NOT account-wide)
3. Save in `.env.local` o `~/.zshrc` come `VERCEL_TOKEN`

### REST API direct usage

```bash
# Deploy via API
curl -X POST https://api.vercel.com/v13/deployments \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d @deployment.json
```

### Quando usarlo

- CI/CD environments (no browser)
- Automated scripts senza interaction
- Emergency fallback se MCP+CLI both broken

**Anti-pattern non-dev**: NON chiedere VERCEL_TOKEN in chat se MCP/CLI funzionano. Token è ultimo recourse.

## Custom domain setup

### Via MCP (Tier 1)

```
vercel:add_domain(projectId, "my-app.com")
# Returns DNS records to set
```

### Via CLI (Tier 2)

```bash
vercel domains add my-app.com
# Output:
# Set the following DNS records on your domain:
# Type:  CNAME
# Name:  my-app.com
# Value: cname.vercel-dns.com
```

### DNS providers comuni

| Provider | Where to set DNS |
|---|---|
| Cloudflare | Dashboard → DNS → CNAME record |
| Namecheap | Domain List → Advanced DNS → CNAME |
| Google Domains | DNS → Custom records → CNAME |
| GoDaddy | DNS Management → CNAME |

DNS propagation: 5 min - 48h (di solito < 1h).

## Env vars management

### Naming convention

- `NEXT_PUBLIC_*` — client-exposed (mai secrets)
- `*` (no prefix) — server-only (secrets, API keys)

### Env per ambiente

| Ambiente | Use |
|---|---|
| `development` | Local dev (`vercel dev`) |
| `preview` | PR/branch preview deploys |
| `production` | Production deploys (main branch) |

Best practice: setta env vars per `preview + production` simultaneamente (non solo prod).

### Pull env to local

```bash
vercel env pull .env.local
# Replicates Vercel env vars locally (exclude .gitignore'd)
```

## Build configuration

### `vercel.json` template

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "git": {
    "deploymentEnabled": {
      "main": true
    }
  },
  "regions": ["iad1"]
}
```

### Build cache

- Prima deploy: 3-5 min
- Subsequent deploy: < 1 min con cache (build cache invalidation se package.json change)

## CI/CD pattern raccomandato (audience non-dev)

**Default**: Vercel auto-deploy (NO GitHub Actions necessari).

1. `git push origin main` → Vercel auto-deploy production
2. `git push origin feat/x` → Vercel auto-deploy preview
3. PR comments mostrano preview URL automatico

**Optional GitHub Actions** (advanced):

```yaml
# .github/workflows/check.yml
name: Check
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm test
```

Per audience non-dev: skip GitHub Actions, trust Vercel build to fail if breaks.

## Pricing 2026

| Plan | Price | Bandwidth | Build minutes | Team |
|---|---|---|---|---|
| Hobby | $0 | 100 GB | 6000 min | Solo personal |
| Pro | $20/mo + usage | 1 TB | unlimited | Team collaboration |
| Enterprise | Custom | Custom | Custom | SLAs, SSO |

Free tier copre primo 100 user MVP. Upgrade Pro quando: serve team, SSL custom, analytics avanzati.

## Smoke test post-deploy

### Tier A — Playwright MCP

```python
playwright:goto(deploy_url)
playwright:screenshot(path="/tmp/screenshot.png", fullPage=True)
status = playwright:get_response_status()  # check 200
```

### Tier B — curl fallback

```bash
curl -I -L -m 10 <deploy_url>
# HTTP/2 200 → ok
# Otherwise: parse error, identify cause
```

### Tier C — Manual

```
Apri <deploy_url> nel browser. Verifica:
- [ ] Homepage carica
- [ ] No console errors (F12 → Console)
- [ ] Login funziona (se auth presente)
- [ ] Una pagina protetta accessibile
```

## Edge cases

| Issue | Fix |
|---|---|
| Build fail (TS error) | Fix locale, `npm run build` deve passare prima |
| Env var mancante | `vercel env add` o set via dashboard |
| Quota exceeded | Upgrade Pro o usa altro account |
| Domain not propagating | Wait 1-24h, check `dig <domain>` |
| MCP OAuth expired | Re-run `/mcp` reconnect |
| Multiple Vercel team scopes | `vercel switch <team>` |

## Sources

- [vercel.com/docs/agent-resources/vercel-mcp](https://vercel.com/docs/agent-resources/vercel-mcp)
- [vercel.com/docs/cli](https://vercel.com/docs/cli)
- [vercel.com/docs/deployments](https://vercel.com/docs/deployments)
