# {{PROJECT_NAME_TITLE}}

{{DESCRIPTION}}

Generato con [/web-builder](https://github.com/filippogreco/claude-skills-learnn) — Pack v2 Learnn.

## Setup rapido

```bash
# 1. Install
npm install

# 2. Init Convex (browser OAuth)
npx convex dev
# Genera convex/_generated/ + .env.local con NEXT_PUBLIC_CONVEX_URL

# 3. Setup Clerk
# Vai su https://dashboard.clerk.com → Create app → API Keys
# Copy in .env.local: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY
# Setup JWT template "convex" in Clerk dashboard (vedi convex/auth.config.ts)

# 4. Test locale
npm run dev
# http://localhost:3000
```

## Deploy

```bash
# Preview
vercel deploy

# Production
vercel deploy --prod
```

Set env vars su Vercel:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `NEXT_PUBLIC_CONVEX_URL` (production deployment)
- `CLERK_JWT_ISSUER_DOMAIN`

## Structure

```
app/
├── (auth)/sign-in, sign-up    # Clerk auth pages
├── (dashboard)/dashboard      # Protected dashboard
├── ConvexClientProvider.tsx   # Provider chain
├── layout.tsx
└── page.tsx                   # Landing
convex/
├── schema.ts                  # DB schema
├── auth.config.ts             # Clerk JWT config
└── items.ts                   # Example queries
middleware.ts                  # Clerk route protection
lib/utils.ts                   # cn() helper
```

## License

{{AUTHOR}} © {{YEAR}}
