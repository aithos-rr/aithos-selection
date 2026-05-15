# next-internal-tool — Stub v1

Questo template è una variant del `nextjs-saas` template specifica per **internal tool** (no billing, Clerk Organizations mode).

## Stato v1: STUB

Per ora, lo scaffolder usa il template `nextjs-saas` come fallback automatico quando `template_id == "next-internal-tool"`.

Differenze pianificate per v2:
- Clerk Organizations attivato di default
- Sidebar con multi-team selector
- No Stripe/billing scaffold
- Audit log table in Convex schema (`auditLogs`)
- Permission model role-based (admin / member / viewer)

## Workaround attuale

Lo scaffolder copia `nextjs-saas` poi:
1. Rimuove `app/(billing)/` (se presente)
2. Edita `convex/schema.ts` aggiungendo `organizations` table
3. Aggiorna CLAUDE.md per "Internal tool" template variant

In skill `auth-database-setup` Phase 4, attiva Clerk Organizations:
```bash
# In Clerk dashboard: enable Organizations feature
# In .env.local: NEXT_PUBLIC_CLERK_ORGANIZATIONS_MODE=true
```

## Roadmap v2

Vedi `DECISIONS.md` per scope expansion.
