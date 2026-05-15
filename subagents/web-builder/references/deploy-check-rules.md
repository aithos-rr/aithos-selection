# Deploy Check Rules — Reference

> Riusa pattern `deploy-check` skill v1 (Webinar 3 Vibe Coding), espande per stack `tech-stack-2026`. Skill `deploy-automation` invoca queste regole come gating pre-deploy. 14 regole totali con severity blocker/warning/best-practice.

## 🔴 BLOCKER (se fail → STOP deploy)

### 1. Secrets in git history

**Check**:
```bash
git log --all -p | grep -E '(sk_live_|pk_live_|password=|api_key=|SECRET_KEY=)' | head -20
```

**Fail criteria**: any match found
**Fix**: `git filter-branch` o `git filter-repo` per rimuovere secret + force push (raro caso autorizzato). Rotate compromised secret IMMEDIATELY.

### 2. `.env*.local` committed

**Check**:
```bash
git ls-files | grep -E '\.env\.(local|production|development)$'
```

**Fail criteria**: any match
**Fix**:
```bash
git rm --cached .env.local
echo ".env*.local" >> .gitignore
git add .gitignore
git commit -m "Remove .env.local from tracking"
# Then rotate any secret that was in .env.local
```

### 3. Build success local

**Check**:
```bash
cd <project_path>
npm run build
echo $?  # exit 0 = ok
```

**Fail criteria**: exit !=0
**Fix**: parse error log, common cases:
- TS error → fix typing
- Missing dep → `npm install <missing>`
- Env var missing build-time → add to `.env.local` o Vercel
- Memory exceeded → `NODE_OPTIONS="--max-old-space-size=4096" npm run build`

### 4. Test pass (se test scritti)

**Check**:
```bash
[ -f package.json ] && grep -q "\"test\"" package.json && npm test
```

**Fail criteria**: exit !=0
**Fix**: fix failing test prima di deploy

### 5. No `console.log` con dati sensibili

**Check**:
```bash
grep -rE 'console\.(log|warn)\(.*\b(password|email|token|secret)\b' app/ src/ lib/ 2>/dev/null
```

**Fail criteria**: any match (false positive review needed)
**Fix**: replace con structured logging (winston, pino) o remove

## 🟡 WARNING (review prima di deploy)

### 6. Env vars Vercel matcha local

**Check**:
```bash
vercel env ls production | tail -n +2 | awk '{print $1}' | sort > /tmp/vercel-env.txt
grep -oE '^[A-Z_]+=' .env.local | sed 's/=$//' | sort > /tmp/local-env.txt
diff /tmp/vercel-env.txt /tmp/local-env.txt
```

**Warning criteria**: env vars in `.env.local` non in Vercel
**Fix**: `vercel env add <KEY> production` per ogni mancante

### 7. CORS config

**Check**: `app/api/*/route.ts` o `next.config.js` CORS headers
**Fail**: open CORS `*` su API protetti
**Fix**: restrict origins specifici

### 8. Rate limiting endpoint costosi

**Check**: API routes che hit DB / external service senza rate limit
**Warning**: endpoint senza protection
**Fix**: middleware rate limit (es. `@upstash/ratelimit`) o Convex Action throttling

### 9. Error monitoring (Sentry/Logtail)

**Check**: `package.json` dependencies for `@sentry/nextjs` o `pino`
**Warning**: no monitoring setup
**Fix**: install Sentry per tracking error production. Per MVP, skip ok ma documenta.

### 10. HTTPS only

**Check**: Vercel default = HTTPS automatic. No action needed.
**Warning**: solo se custom domain con DNS misconfigurato

## 🟢 BEST PRACTICE (nice to have)

### 11. Lighthouse score > 85

**Check**:
```bash
npx --yes lighthouse <preview_url> --quiet --chrome-flags="--headless" --output=json | jq '.categories'
```

**Best practice**: performance > 85, a11y > 90, seo > 90, best-practices > 90
**Fix**: ottimizza images (next/image), reduce JS bundle, lazy load

### 12. Performance — FCP < 2.5s

**Check**: WebPageTest o Vercel Speed Insights
**Best practice**: First Contentful Paint < 2.5s
**Fix**: code splitting, lazy load, CDN images

### 13. SEO base

**Check**: meta description, og:image, sitemap.xml, robots.txt
**Best practice**: tutti presenti
**Fix**: add `<head>` meta in `app/layout.tsx`, install `next-sitemap` o `@astrojs/sitemap`

### 14. Privacy policy + Terms

**Check**: `app/privacy/page.tsx` + `app/terms/page.tsx` esistono
**Best practice**: presenti per GDPR compliance EU
**Fix**: genera template via skill `legal-pages-generator` (v2 scope) o manual

## Stack-specific checks

### Next.js + Convex + Clerk

- ✅ Convex deployment URL (`NEXT_PUBLIC_CONVEX_URL`) production set su Vercel
- ✅ Clerk keys production (`pk_live_*`, `sk_live_*`) NOT test (`pk_test_*`)
- ✅ Clerk webhook URL configurato in dashboard Clerk
- ✅ Stripe webhook endpoint con HMAC verify (se billing)

### Astro

- ✅ `output: 'static'` o `'hybrid'` configurato in `astro.config.mjs`
- ✅ Adapter Vercel installato (`@astrojs/vercel`)
- ✅ Content Collections schema valido (`src/content/config.ts`)

### Expo (stub v1)

- (no checks v1, scope espanso v2)

## Output format report

```markdown
# Deploy Check — <project_name>
Data: 2026-MM-DD HH:MM
Env target: preview / production
URL pre-deploy: <preview_url>

## 🔴 Blocker (N)
- [Rule 2] `.env.local` committed in commit abc123 → STOP

## 🟡 Warning (N)
- [Rule 6] 2 env vars in .env.local non su Vercel: STRIPE_KEY, RESEND_API_KEY
  → Fix: `vercel env add STRIPE_KEY production`

## 🟢 OK (N)
- [Rule 1] No secrets in git history
- [Rule 3] Build success
- [Rule 4] Test pass
- [Rule 5] No sensitive console.log

## Verdict

- ✅ READY per deploy (0 blocker, 0 warning)
- ⚠️ BLOCKED — fix blocker prima di proseguire
- 🔶 PROCEED WITH CARE — 0 blocker ma 2 warning, valuta

## Next

- Fix blocker: `<comando specifico>`
- Deploy command: `vercel deploy --prod` (Tier 2)
- Rollback: `vercel rollback <previous_deployment_id>`
```

## Anti-pattern

- 🔴 **Mai skip blocker**: se Rule 1-5 fail, NO deploy. Audience non-dev rischia compromettere security/quality.
- 🔴 **Mai disabilitare check**: se rule sembra "false positive", review manuale. Non commit per silenziare warning.
- 🟡 **Don't break the build**: prima di "fix" warning, verifica non rompe altri test.
- 🟢 **Iterativo**: regole 11-14 sono BP, ok per MVP non superare. Documentare in CLAUDE.md.

## Crediti

Pattern derivato da `skills/webinar-3/deploy-check/SKILL.md` (Filippo's skill v1) + research Fase A best practices 2026.
