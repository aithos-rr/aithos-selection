# /web-builder — Subagent Claude Code

> **Pack v2 Learnn — Claude Skills/Subagents** | 3° subagent (Tier 1) | ARTIFACT-driven
>
> Da brief in linguaggio naturale a progetto web deploy-pronto in 30-60 minuti. Per founder, freelancer, marketer, entrepreneur **non-developer**.

## Cosa fa

Tu dici "voglio una landing per il mio corso AI" o "SaaS per gestire clienti freelance" — `/web-builder` ti scaffolda un progetto vero (Next.js 15 + Convex + Clerk + shadcn + Vercel oppure Astro per landing), genera CLAUDE.md preconfigurato, integra auth + database, e deploya un preview live su Vercel. Tu lo apri nel browser e funziona.

8 domande discovery → 6 fasi automatiche → repo Git su GitHub → URL Vercel pubblico. Audience non-tech: zero terminale richiesto se hai i tool MCP installati.

## Per chi è

- **Founder / Entrepreneur**: MVP rapido per validare idea pre-developer hire
- **Freelancer Marketing/Growth**: tool interno o landing per cliente
- **Content creator / Course builder**: landing corso, sales page
- **Vibe coder**: capisce la logica, non vuole imparare React/SQL
- **Developer junior**: scaffold rapido per non perdere tempo su boilerplate

## Stack supportato (default)

- **Frontend**: Next.js 15 (App Router) + Tailwind CSS v4 + shadcn/ui
- **Database**: Convex (TypeScript-first, realtime)
- **Auth**: Clerk (free 10k MAU, integrazione nativa con Convex)
- **Deploy**: Vercel (MCP-first OAuth, CLI fallback, token last resort)
- **Mobile** (stub v1): Expo + Convex (espansione v2)
- **Override permessi**: Astro (landing/content), Supabase (SQL), una piattaforma no-code (no-code), WorkOS (enterprise SSO)

## Installazione

### Prerequisiti

```bash
# Node 20+
node --version  # v20.x.x ✅

# Vercel CLI (opzionale ma raccomandato)
npm install -g vercel

# GitHub CLI (opzionale)
brew install gh  # o equivalente

# Claude Code (richiesto)
npm install -g @anthropic-ai/claude-code
```

### MCP servers (raccomandati per esperienza ottimale)

```bash
# Vercel MCP (deploy senza token)
claude mcp add --transport http vercel https://mcp.vercel.com

# Context7 MCP (docs runtime aggiornati)
claude mcp add context7 npx -- context7 mcp

# Playwright MCP (smoke test post-deploy)
claude mcp add playwright npx -- playwright-mcp
```

### Subagent setup

```bash
# Clone questo repo o copy sub-folder
git clone https://github.com/filippogreco/claude-skills-learnn.git
cp -r claude-skills-learnn/.claude/agents/web-builder/ ~/.claude/agents/

# Verifica
ls ~/.claude/agents/web-builder/
# Deve contenere: web-builder.md, skills/, references/, scripts/, ARCHITECTURE.md, ...
```

### Test

```bash
cd ~/Dev/projects
mkdir my-test-project && cd my-test-project
claude
```

Poi nel prompt:
```
/web-builder
```

## Esempi reali

### Esempio 1 — Landing corso AI

**Tu scrivi**:
> "voglio una landing per il mio corso AI dal nome 'AI Mastery 2026'"

**Discovery (8 Q in 2 minuti)**:
- Q1: Landing/marketing
- Q2: Vibe coder
- Q3: **Astro** (default proposto, +40% performance vs Next per static)
- Q4: No, uso .vercel.app
- Q5: No (pubblico)
- Q6: No (statico)
- Q7: No
- Q8: Sì auto

**Output (~25 min)**:
- Cartella `ai-mastery-2026/` con Astro + Tailwind v4 + Content Collections
- Hero + Features + CTA + Footer scaffolded
- CLAUDE.md preconfigurato (lingua italiana)
- `ai-mastery-2026.vercel.app` live, Lighthouse 95+
- Repo GitHub `username/ai-mastery-2026` pushed

### Esempio 2 — SaaS micro per freelance

**Tu scrivi**:
> "SaaS per gestire clienti freelance, login email/password, dashboard, billing mensile"

**Discovery**:
- Q1: SaaS micro
- Q2: Vibe coder
- Q3: Default Filippo (Next.js + Convex + Clerk)
- Q4: Decido dopo
- Q5: Sì consumer (Clerk)
- Q6: Sì realtime (Convex)
- Q7: Sì (per webhook Stripe)
- Q8: Sì auto

**Output (~45-60 min, include OAuth flow)**:
- Cartella `freelance-crm/` con Next.js 15 + Convex + Clerk
- Stripe billing scaffold (`app/api/webhook/stripe/route.ts`)
- Dashboard + Settings + Billing pages
- Convex schema (clients, invoices, subscriptions)
- Webhook n8n bridge generato
- Deploy preview su `freelance-crm-xxx.vercel.app`

### Esempio 3 — Internal tool tracciamento campagne

**Tu scrivi**:
> "tool interno per tracciare campagne marketing del nostro team"

**Discovery**:
- Q1: Internal tool
- Q2: Junior
- Q3: Default Filippo
- Q4: Custom (campaigns.yourdomain.it)
- Q5: Sì consumer (Clerk Organizations)
- Q6: Sì realtime (Convex)
- Q7: Sì (sync Attio CRM via n8n)
- Q8: Sì auto

**Output (~45 min)**:
- Cartella `campaigns-tracker/` con Next.js + Convex + Clerk Org mode
- Data table con filter + sort + pagination
- n8n webhook handler per sync Attio CRM
- Custom domain `campaigns.yourdomain.it` configurato
- Audit log per ogni mutation

## FAQ

### Posso cambiare stack dopo lo scaffold?

Sì, ma con limitazioni. Durante discovery puoi sempre modificare le risposte. Post-scaffold: stack core (Next.js → Astro) richiede re-scaffold da zero. Add-on (Stripe billing, n8n) si possono aggiungere via skill specifiche.

### Come gestisco i secrets?

Mai committati. Tutte le env vars in `.env.local` (in `.gitignore`). Per produzione: imposta via Vercel UI o `vercel env add`. Mai chiedere VERCEL_TOKEN in chat se MCP/CLI funzionano.

### Quanto costa un deploy?

**$0/month per il primo MVP**: Vercel free + Convex free + Clerk 10k MAU free. Total $0 fino a ~100 user attivi.

Custom domain: $0 con `.vercel.app` o ~$10-15/anno per `.com`.

### Posso usare il mio dominio?

Sì. In Q4 della discovery selezioni "Sì custom" → fornisci dominio → l'agent configura `vercel domain add` automaticamente. Tu setti DNS (CNAME a `cname.vercel-dns.com`).

### Cosa fa se MCP Vercel non è installato?

Fallback Tier 2 → Vercel CLI con `vercel login` (browser OAuth). Se anche CLI manca → Tier 3 con `VERCEL_TOKEN` env var (utenti advanced/CI). Last resort: documenta deploy manuale e skip skill.

### Funziona se non ho GitHub?

Sì. Scaffold + deploy Vercel funzionano senza GitHub (Vercel link diretto folder). Ma è raccomandato GitHub per: backup repo, preview branch deploys, collaboration.

### Posso aggiungere componenti dopo lo scaffold?

Sì. shadcn components vengono aggiunti via `npx shadcn@latest add <component>`. Per logica custom: chiedi a Claude Code "aggiungi pagina X" o "aggiungi feature Y" e itera.

### Quanto è opinionato lo stack?

Molto. Default è `tech-stack-2026` di Filippo (Next + Convex + Clerk + Vercel). Override permessi solo via discovery Q3 con flag esplicito. Filosofia: opinione forte = riduce paralysis-by-choice per audience non-dev.

## Troubleshooting

### "Node version mismatch"

```bash
nvm install 20
nvm use 20
```

### "Convex deployment fail"

```bash
# Re-init Convex
cd <project_path>
rm -rf convex/_generated/
npx convex dev
# Browser OAuth: login Convex
```

### "Vercel deploy build error"

Parse log Vercel:
- TS error → fix locale, `npm run build` deve passare prima
- Env var missing → `vercel env add <KEY> production`
- Quota exceeded → upgrade Pro o usa altro account

### "Clerk middleware non protegge route"

Check `middleware.ts`:
- `createRouteMatcher` include la route?
- Matcher config esclude file statici?

### "shadcn add fail"

```bash
# Re-init shadcn
npx shadcn@latest init
# Poi add
npx shadcn@latest add <component>
```

### "n8n webhook signature mismatch"

- Raw body usato? (`req.text()`, NOT `req.json()` poi serialize)
- Same secret in app + n8n env vars?
- HMAC algorithm SHA-256 (default) match?

### "Discovery flow loop"

Se discovery rimane bloccata: rinomina `<memory>/config.md.bak`, riprova `/web-builder`. Se persiste: report issue.

## Architettura

Vedi:
- `BUILD-BRIEF.md` — design specs originali (coordinator chat)
- `ARCHITECTURE.md` — design completo (worker chat output Fase B)
- `DECISIONS.md` — 8 decisioni immutabili (4 iniziali + 4 emergent post-research)
- `PROGRESS.md` — log build worker chat
- `research/research-summary.md` — output Fase A (~3200 parole con citazioni)

## Skills companion

- `project-scaffolder` — copia template + placeholder substitution + git init
- `claude-md-generator` — compila CLAUDE.md + .claude/settings.json
- `auth-database-setup` — Clerk + Convex (default) o Supabase override
- `deploy-automation` — Vercel MCP/CLI/token 3-tier
- `n8n-bridge` (opzionale) — webhook handler + n8n workflow template

## References docs

- `references/stack-comparison-2026.md` — decision matrix
- `references/database-integration-2026.md` — Convex + Supabase
- `references/auth-integration-2026.md` — Clerk + WorkOS
- `references/deploy-vercel-2026.md` — Vercel MCP + CLI
- `references/claude-md-templates.md` — 3 template variant
- `references/n8n-integration-2026.md` — webhook HMAC
- `references/deploy-check-rules.md` — 14 regole pre-deploy
- `references/shadcn-patterns-2026.md` — top 10 component patterns

## Templates starter

In `scripts/templates/`:
- `nextjs-saas/` — completo (~25 file): Next + Convex + Clerk + middleware
- `nextjs-landing/` — completo (~10 file): Next + Tailwind + hero/features/cta
- `astro-marketing/` — completo (~8 file): Astro + Tailwind v4 + Content Collections
- `next-internal-tool/` — stub v1 (variant `nextjs-saas`)
- `expo-mobile/` — stub v1 (placeholder + roadmap v2)

## Crediti

- **Pack v2 Learnn** — Claude Week (5-12 maggio 2026)
- **Coordinator**: Filippo Greco + Claude (chat principale)
- **Worker chat**: dedicata in `.claude/agents/web-builder/` (questa)
- **Pattern validation**: derivato da `/lead-finder-pro` (Done 30 apr 2026)
- **Skill v1 base**: `vibe-start` + `deploy-check` (Webinar 3 Vibe Coding)
- **Tech stack baseline**: `tech-stack-2026` (skill globale Filippo)

## License

MIT — vedi `LICENSE` (se presente).

## Feedback

Issue / PR: GitHub repo `filippogreco/claude-skills-learnn` (TBD post-pack release).

Per audience Learnn: feedback canale Discord pack v2 (TBD).
